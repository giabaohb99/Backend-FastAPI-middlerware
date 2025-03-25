from typing import Any
import sys
from pprint import pprint
import json
from datetime import datetime

def debug_print(data: Any, exit: bool = False, title: str = "DEBUG INFO"):
    """
    Print data in a formatted way and optionally exit
    
    Args:
        data: Data to print
        exit: Whether to exit after printing
        title: Title of the debug section
    """
    print(f"\n=== {title} ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if isinstance(data, (dict, list)):
        pprint(data, indent=2)
    elif isinstance(data, str):
        try:
            # Try to parse and pretty print JSON string
            json_data = json.loads(data)
            pprint(json_data, indent=2)
        except json.JSONDecodeError:
            print(data)
    else:
        print(data)
    print("================\n")
    
    if exit:
        sys.exit(1)

def debug_request(method: str, url: str, headers: dict, data: Any = None, exit: bool = False):
    """
    Debug HTTP request
    
    Args:
        method: HTTP method
        url: Request URL
        headers: Request headers
        data: Request data
        exit: Whether to exit after printing
    """
    debug_data = {
        "method": method,
        "url": url,
        "headers": headers,
        "data": data
    }
    debug_print(debug_data, exit=exit, title="REQUEST DEBUG")

def debug_response(status_code: int, headers: dict, body: Any = None, exit: bool = False):
    """
    Debug HTTP response
    
    Args:
        status_code: Response status code
        headers: Response headers
        body: Response body
        exit: Whether to exit after printing
    """
    debug_data = {
        "status_code": status_code,
        "headers": headers,
        "body": body
    }
    debug_print(debug_data, exit=exit, title="RESPONSE DEBUG")

def debug_error(error: Exception, exit: bool = True):
    """
    Debug error with full traceback
    
    Args:
        error: Exception object
        exit: Whether to exit after printing
    """
    import traceback
    debug_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc()
    }
    debug_print(debug_data, exit=exit, title="ERROR DEBUG") 