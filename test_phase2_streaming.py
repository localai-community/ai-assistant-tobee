#!/usr/bin/env python3
"""
Test script for Phase 2 streaming functionality
"""

import httpx
import json
import sys

def test_phase2_streaming():
    """Test Phase 2 streaming endpoint"""
    print("🧪 Testing Phase 2 streaming...")
    
    try:
        with httpx.Client() as client:
            payload = {
                "message": "What is 5 + 3?",
                "model": "llama3:latest",
                "engine_type": "auto",
                "use_phase2_reasoning": True,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True
            }
            
            print(f"📤 Sending request to: http://localhost:8000/api/v1/phase2-reasoning/stream")
            print(f"📤 Payload: {json.dumps(payload, indent=2)}")
            
            # Stream the response
            with client.stream(
                "POST",
                "http://localhost:8000/api/v1/phase2-reasoning/stream",
                json=payload,
                timeout=60.0,
                headers={"Accept": "text/event-stream", "Connection": "keep-alive"}
            ) as response:
                print(f"📥 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    full_response = ""
                    chunk_count = 0
                    
                    # Process Server-Sent Events
                    for line in response.iter_lines():
                        if line:
                            chunk_count += 1
                            print(f"📥 Chunk {chunk_count}: {line[:100]}...")
                            
                            # httpx.iter_lines() returns strings, not bytes
                            if line.startswith('data: '):
                                data_str = line[6:]  # Remove 'data: ' prefix
                                try:
                                    data = json.loads(data_str)
                                    
                                    if data.get("error"):
                                        print(f"❌ Error in data: {data.get('error')}")
                                        return False
                                    
                                    # Handle different response types
                                    if "content" in data:
                                        chunk = data["content"]
                                        full_response += chunk
                                        print(f"📝 Content chunk: {chunk[:50]}...")
                                    
                                    # Check if this is the final message
                                    if data.get("final"):
                                        print(f"✅ Final message received")
                                        print(f"📊 Engine used: {data.get('engine_used', 'unknown')}")
                                        print(f"📊 Reasoning type: {data.get('reasoning_type', 'unknown')}")
                                        print(f"📊 Steps count: {data.get('steps_count', 0)}")
                                        print(f"📊 Confidence: {data.get('confidence', 0.0)}")
                                        print(f"📝 Full response length: {len(full_response)}")
                                        return True
                                        
                                except json.JSONDecodeError as e:
                                    print(f"⚠️ JSON decode error: {e}")
                                    continue
                    
                    print(f"📊 Streaming ended, total chunks: {chunk_count}")
                    print(f"📝 Full response length: {len(full_response)}")
                    return len(full_response) > 0
                else:
                    print(f"❌ Backend error: {response.status_code}")
                    return False
                    
    except httpx.TimeoutException:
        print("⏰ Request timed out")
        return False
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_phase2_streaming()
    if success:
        print("✅ Phase 2 streaming test PASSED")
        sys.exit(0)
    else:
        print("❌ Phase 2 streaming test FAILED")
        sys.exit(1) 