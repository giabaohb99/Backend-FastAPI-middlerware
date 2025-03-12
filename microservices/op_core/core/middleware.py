import time
from fastapi import Request, HTTPException
import logging
from typing import Callable
import json
import hashlib
from sqlalchemy.orm import Session
from .database import engine
from .models.log import Log
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.concurrency import iterate_in_threadpool
from sqlalchemy import event, text
from contextvars import ContextVar
from collections import defaultdict
import redis
from .config import settings
from starlette.responses import JSONResponse
from datetime import datetime, timedelta

# Initialize Redis connection
redis_client = redis.Redis(
    host=settings.RATE_LIMIT['REDIS_HOST'],
    port=settings.RATE_LIMIT['REDIS_PORT'],
    db=settings.RATE_LIMIT['REDIS_DB'],
    password=settings.RATE_LIMIT['REDIS_PASSWORD'],
    decode_responses=True
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create context variables to store request and SQL queries
request_var = ContextVar("request", default=None)
sql_queries_var = ContextVar("sql_queries", default=None)

def clean_old_logs(db: Session, minutes: int = 30):
    """
    Delete logs older than specified minutes
    """
    try:
        # Calculate the cutoff time
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        # Delete old logs
        delete_query = text("""
            DELETE FROM logs 
            WHERE created_at < :cutoff_time
        """)
        
        result = db.execute(delete_query, {"cutoff_time": cutoff_time})
        deleted_count = result.rowcount
        db.commit()
        
        if deleted_count > 0:
            logger.info(f"Cleaned {deleted_count} old logs (older than {minutes} minutes)")
            
    except Exception as e:
        logger.error(f"Error cleaning old logs: {str(e)}")
        db.rollback()

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Get client IP
            client_ip = request.client.host
            
            # Get request path
            path = request.url.path
            
            # Get request body if exists
            body = await request.body()
            body_hash = ""
            if body:
                # Create hash of the request body
                body_hash = hashlib.md5(body).hexdigest()
            
            # Create unique key for this request
            request_key = f"rate_limit:{client_ip}:{path}:{body_hash}"
            
            # Check if this exact request was made recently
            last_request = redis_client.get(request_key)
            if last_request:
                # If request was made within cooldown period, block it
                time_passed = time.time() - float(last_request)
                if time_passed < settings.RATE_LIMIT['REQUEST_COOLDOWN']:
                    wait_time = settings.RATE_LIMIT['REQUEST_COOLDOWN'] - time_passed
                    error_detail = {
                        "message": "Too many requests",
                        "wait_seconds": round(wait_time, 1),
                        "ip": client_ip,
                        "path": path,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    logger.warning(f"Rate limit exceeded for IP {client_ip} on path {path}. Wait time: {wait_time}s")
                    return JSONResponse(
                        status_code=429,
                        content=error_detail
                    )
            
            # Update last request time
            redis_client.setex(
                request_key,
                settings.RATE_LIMIT['REQUEST_COOLDOWN'],
                str(time.time())
            )
            
            # Check overall rate limit for IP
            ip_key = f"ip_requests:{client_ip}"
            request_count = redis_client.incr(ip_key)
            
            # Set expiry if first request
            if request_count == 1:
                redis_client.expire(ip_key, settings.RATE_LIMIT['RATE_LIMIT_WINDOW'])
            
            # If too many requests, block IP
            if request_count > settings.RATE_LIMIT['MAX_REQUESTS']:
                error_detail = {
                    "message": "Rate limit exceeded",
                    "retry_after": settings.RATE_LIMIT['RATE_LIMIT_WINDOW'],
                    "ip": client_ip,
                    "path": path,
                    "request_count": request_count,
                    "timestamp": datetime.utcnow().isoformat()
                }
                logger.warning(f"IP {client_ip} exceeded maximum requests ({request_count} requests)")
                return JSONResponse(
                    status_code=429,
                    content=error_detail
                )
            
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error in RateLimitMiddleware: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "message": "Internal server error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Initialize SQL queries tracking
            sql_queries = []
            sql_queries_token = sql_queries_var.set(sql_queries)
            
            # Set the request in context
            request_token = request_var.set(request)
            start_time = time.time()

            # Get request body
            request_body = None
            try:
                body = await request.body()
                if body:
                    request_body = body.decode()
            except Exception as e:
                logger.error(f"Error reading request body: {str(e)}")

            # Process request
            try:
                response = await call_next(request)
            except Exception as e:
                logger.error(f"Request processing error: {str(e)}", exc_info=True)
                response = JSONResponse(
                    status_code=500,
                    content={
                        "message": "Internal server error",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )

            process_time = time.time() - start_time

            # Get response body
            response_body = None
            try:
                response_body = [section async for section in response.body_iterator]
                response.body_iterator = iterate_in_threadpool(response_body)
                response_body = response_body[0].decode()
            except Exception as e:
                logger.error(f"Error reading response body: {str(e)}")

            # Get collected SQL queries
            collected_queries = sql_queries_var.get()
            
            # Store in database
            db = Session(engine)
            try:
                # Clean old logs before adding new one
                clean_old_logs(db)
                
                # Create log entry
                log_entry = Log(
                    method=request.method,
                    url=str(request.url),
                    status_code=response.status_code,
                    request_body=request_body,
                    response_body=response_body,
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent"),
                    process_time=process_time,
                    sql_queries=json.dumps(collected_queries)
                )
                db.add(log_entry)
                db.commit()
                
                # Log request details
                log_data = {
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "ip_address": request.client.host,
                    "user_agent": request.headers.get("user-agent"),
                    "process_time": process_time,
                    "sql_queries_count": len(collected_queries),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Log based on status code
                if response.status_code >= 400:
                    logger.error(f"Error request: {log_data}")
                elif response.status_code >= 300:
                    logger.warning(f"Redirect request: {log_data}")
                else:
                    logger.info(f"Successful request: {log_data}")
                    
            except Exception as e:
                logger.error(f"Error saving log: {str(e)}")
                db.rollback()
            finally:
                db.close()

            # Reset context variables
            request_var.reset(request_token)
            sql_queries_var.reset(sql_queries_token)

            return response
            
        except Exception as e:
            logger.error(f"Error in LoggingMiddleware: {str(e)}", exc_info=True)
            raise

class SQLQueryLoggingMiddleware:
    def __init__(self, engine):
        self.engine = engine

    def before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())

    def after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        try:
            total_time = time.time() - conn.info['query_start_time'].pop()
            
            # Try to get current SQL queries list
            current_queries = sql_queries_var.get()
            if current_queries is not None:
                # Add query information
                query_info = {
                    "query": statement,
                    "parameters": str(parameters),
                    "execution_time": round(total_time, 4),
                    "timestamp": datetime.utcnow().isoformat()
                }
                current_queries.append(query_info)
                
                # Log SQL query details
                logger.info(f"SQL Query: {statement}")
                logger.info(f"Parameters: {parameters}")
                logger.info(f"Execution Time: {total_time:.4f}s")
                
                # If query failed, add error details
                if hasattr(cursor, 'error'):
                    error_info = {
                        "error": str(cursor.error),
                        "error_code": cursor.error.code if hasattr(cursor.error, 'code') else None,
                        "error_message": cursor.error.message if hasattr(cursor.error, 'message') else None
                    }
                    query_info["error"] = error_info
                    logger.error(f"SQL Query Error: {error_info}")
        except Exception as e:
            logger.error(f"Error logging SQL query: {str(e)}")
            # Add error to current queries
            current_queries = sql_queries_var.get()
            if current_queries is not None:
                current_queries.append({
                    "error": str(e),
                    "query": statement,
                    "parameters": str(parameters),
                    "timestamp": datetime.utcnow().isoformat()
                })

# Connect middleware with SQLAlchemy engine
event.listen(engine, "before_cursor_execute", SQLQueryLoggingMiddleware(engine).before_cursor_execute)
event.listen(engine, "after_cursor_execute", SQLQueryLoggingMiddleware(engine).after_cursor_execute)