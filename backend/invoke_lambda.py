#!/usr/bin/env python3
"""
Simple Lambda Handler Invoker

Quick script to test Lambda handlers with custom events.
Usage: python invoke_lambda.py <endpoint> [method] [body]
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_simple_event(method="GET", path="/", body=None, headers=None):
    """Create a simple API Gateway event"""
    event = {
        "version": "2.0",
        "routeKey": f"{method} {path}",
        "rawPath": path,
        "rawQueryString": "",
        "headers": headers or {},
        "requestContext": {
            "http": {
                "method": method,
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "test-user-agent"
            },
            "requestId": "test-request-id",
            "routeKey": f"{method} {path}",
            "stage": "test"
        },
        "body": body,
        "isBase64Encoded": False
    }
    return event

def create_context():
    """Create a simple Lambda context"""
    class Context:
        def __init__(self):
            self.function_name = "ai-assistant-backend"
            self.aws_request_id = "test-request-id"
            self.remaining_time_in_millis = lambda: 30000
    
    return Context()

def main():
    if len(sys.argv) < 2:
        print("Usage: python invoke_lambda.py <endpoint> [method] [body]")
        print("Examples:")
        print("  python invoke_lambda.py /")
        print("  python invoke_lambda.py /health")
        print("  python invoke_lambda.py /chat POST '{\"message\": \"Hello\"}'")
        return
    
    endpoint = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else "GET"
    body = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Set headers for POST requests
    headers = {}
    if method == "POST" and body:
        headers["Content-Type"] = "application/json"
    
    # Create event and context
    event = create_simple_event(method, endpoint, body, headers)
    context = create_context()
    
    try:
        # Import and test the handler
        from lambda_handler import handler
        
        print(f"🚀 Testing {method} {endpoint}")
        print(f"📋 Event: {json.dumps(event, indent=2)}")
        print("-" * 50)
        
        response = handler(event, context)
        
        print(f"✅ Response:")
        print(f"Status Code: {response.get('statusCode', 'N/A')}")
        print(f"Headers: {response.get('headers', {})}")
        
        if 'body' in response:
            try:
                body_json = json.loads(response['body'])
                print(f"Body: {json.dumps(body_json, indent=2)}")
            except:
                print(f"Body: {response['body']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 