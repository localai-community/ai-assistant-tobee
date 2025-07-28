import json

def handler(event, context):
    """Simple Lambda handler for frontend"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
        },
        "body": json.dumps({
            "message": "Frontend API is running",
            "service": "ai-assistant-frontend",
            "status": "operational"
        })
    } 