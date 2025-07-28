#!/usr/bin/env python3
"""
Local Lambda Handler Testing Script

This script allows you to test Lambda handlers locally by simulating
AWS Lambda events and contexts.
"""

import json
import sys
import os
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_lambda_context():
    """Create a mock Lambda context"""
    class LambdaContext:
        def __init__(self):
            self.function_name = "ai-assistant-backend"
            self.memory_limit_in_mb = 512
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:ai-assistant-backend"
            self.aws_request_id = "test-request-id-12345"
            self.remaining_time_in_millis = lambda: 30000
            self.log_group_name = "/aws/lambda/ai-assistant-backend"
            self.log_stream_name = "2023/01/01/[$LATEST]test-stream"
    
    return LambdaContext()

def create_api_gateway_event(
    method="GET",
    path="/",
    body=None,
    headers=None,
    query_params=None
):
    """Create a mock API Gateway event"""
    event = {
        "version": "2.0",
        "routeKey": f"{method} {path}",
        "rawPath": path,
        "rawQueryString": "",
        "headers": headers or {},
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "test-api-id",
            "domainName": "test-api.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "test-api",
            "http": {
                "method": method,
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "test-user-agent"
            },
            "requestId": "test-request-id",
            "routeKey": f"{method} {path}",
            "stage": "test",
            "time": "12/Mar/2020:19:03:58 +0000",
            "timeEpoch": 1583348638390
        },
        "body": body,
        "isBase64Encoded": False
    }
    
    if query_params:
        event["queryStringParameters"] = query_params
        event["rawQueryString"] = "&".join([f"{k}={v}" for k, v in query_params.items()])
    
    return event

def test_handler(handler_func, event, context):
    """Test a Lambda handler with given event and context"""
    try:
        print(f"🔍 Testing handler: {handler_func.__name__}")
        print(f"📋 Event type: {type(event).__name__}")
        print(f"📋 Event keys: {list(event.keys()) if isinstance(event, dict) else 'N/A'}")
        print("-" * 50)
        
        response = handler_func(event, context)
        
        print(f"✅ Handler executed successfully")
        print(f"📤 Response type: {type(response).__name__}")
        
        if isinstance(response, dict):
            print(f"📤 Status Code: {response.get('statusCode', 'N/A')}")
            print(f"📤 Headers: {response.get('headers', {})}")
            if 'body' in response:
                try:
                    body = json.loads(response['body']) if isinstance(response['body'], str) else response['body']
                    print(f"📤 Body: {json.dumps(body, indent=2)}")
                except:
                    print(f"📤 Body: {response['body']}")
        else:
            print(f"📤 Response: {response}")
        
        return response
        
    except Exception as e:
        print(f"❌ Handler failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main testing function"""
    print("🚀 Local Lambda Handler Testing")
    print("=" * 50)
    
    # Import handlers
    try:
        from lambda_handler import handler as main_handler
        from test_handler import handler as test_handler_func
        print("✅ Successfully imported handlers")
    except ImportError as e:
        print(f"❌ Failed to import handlers: {e}")
        return
    
    # Create context
    context = create_lambda_context()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Root endpoint (GET /)",
            "event": create_api_gateway_event("GET", "/"),
            "handler": main_handler
        },
        {
            "name": "Health check (GET /health)",
            "event": create_api_gateway_event("GET", "/health"),
            "handler": main_handler
        },
        {
            "name": "API status (GET /api/v1/status)",
            "event": create_api_gateway_event("GET", "/api/v1/status"),
            "handler": main_handler
        },
        {
            "name": "Chat endpoint (POST /chat)",
            "event": create_api_gateway_event(
                "POST", 
                "/chat",
                body=json.dumps({"message": "Hello, test message"}),
                headers={"Content-Type": "application/json"}
            ),
            "handler": main_handler
        },
        {
            "name": "Test handler",
            "event": create_api_gateway_event("GET", "/test"),
            "handler": test_handler_func
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🧪 Test {i}: {scenario['name']}")
        print("=" * 50)
        
        result = test_handler(scenario['handler'], scenario['event'], context)
        
        if result:
            print(f"✅ Test {i} PASSED")
        else:
            print(f"❌ Test {i} FAILED")
    
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    main() 