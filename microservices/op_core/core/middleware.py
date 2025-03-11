import time
from fastapi import Request
import logging
from typing import Callable
import json
from sqlalchemy.orm import Session
from .database import engine
from .models.log import Log
from starlette.concurrency import iterate_in_threadpool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def log_request_middleware(request: Request, call_next: Callable):
    start_time = time.time()
    
    # Get request body
    request_body = None
    try:
        body = await request.body()
        if body:
            request_body = body.decode()
    except:
        pass

    # Process request
    response = await call_next(request)
    
    # Calculate process time
    process_time = time.time() - start_time

    # Get response body
    response_body = None
    try:
        response_body = [section async for section in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(response_body)
        response_body = response_body[0].decode()
    except:
        pass

    # Create log entry
    log_entry = Log(
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        request_body=request_body,
        response_body=response_body,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        process_time=process_time
    )

    # Save to database
    try:
        db = Session(engine)
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save log to database: {str(e)}")
    finally:
        db.close()
    
    # Log to console
    logger.info(f"Request completed: {request.method} {request.url}")
    logger.info(f"Process time: {process_time:.2f}s")
    logger.info(f"Status code: {response.status_code}")
    
    return response

class SQLQueryLoggingMiddleware:
    def __init__(self, engine):
        self.engine = engine
    
    def before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
        logger.info(f"Executing SQL: {statement}")
        if parameters:
            logger.info(f"Parameters: {parameters}")
    
    def after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop()
        logger.info(f"SQL execution time: {total:.2f}s") 