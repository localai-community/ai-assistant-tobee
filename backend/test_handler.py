import json

def handler(event, context):
    """Simple test Lambda handler"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "message": "Backend API is running",
            "service": "ai-assistant-backend",
            "status": "operational",
            "event": event
        })
    } 