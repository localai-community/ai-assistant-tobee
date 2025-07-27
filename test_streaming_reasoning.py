#!/usr/bin/env python3
"""
Test script to verify streaming reasoning chat functionality
"""

import httpx
import json
import time

def test_streaming_reasoning():
    """Test the streaming reasoning chat endpoint"""
    
    print("🧪 Testing Streaming Reasoning Chat...")
    print("=" * 50)
    
    # Test data
    test_message = "Solve 2x + 3 = 7"
    
    print(f"📝 Test message: {test_message}")
    print(f"🎯 Endpoint: http://localhost:8000/api/v1/reasoning-chat/stream")
    print()
    
    try:
        with httpx.Client(timeout=30.0) as client:
            payload = {
                "message": test_message,
                "model": "llama3:latest",
                "use_reasoning": True,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True
            }
            
            print("📤 Sending request...")
            print(f"📦 Payload: {json.dumps(payload, indent=2)}")
            print()
            
            # Use streaming endpoint
            with client.stream(
                "POST",
                "http://localhost:8000/api/v1/reasoning-chat/stream",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print("📥 Response received:")
                print(f"🔢 Status Code: {response.status_code}")
                print(f"📋 Content-Type: {response.headers.get('content-type', 'unknown')}")
                print()
                
                if response.status_code == 200:
                    print("✅ Streaming response:")
                    print("-" * 30)
                    
                    full_content = ""
                    chunk_count = 0
                    
                    for chunk in response.iter_text():
                        if chunk:
                            # Handle different response formats
                            if chunk.startswith('data: '):
                                try:
                                    data = json.loads(chunk[6:])  # Remove 'data: ' prefix
                                    content = data.get('content', '')
                                    full_content += content
                                    chunk_count += 1
                                    
                                    # Print first few chunks to show streaming
                                    if chunk_count <= 10:
                                        print(f"📦 Chunk {chunk_count}: {repr(content)}")
                                    
                                except json.JSONDecodeError:
                                    print(f"❌ Failed to parse JSON: {chunk}")
                            else:
                                # Direct text response
                                full_content += chunk
                                chunk_count += 1
                                if chunk_count <= 10:
                                    print(f"📦 Chunk {chunk_count}: {repr(chunk)}")
                    
                    print(f"📊 Total chunks received: {chunk_count}")
                    print()
                    print("📄 Full response:")
                    print("=" * 30)
                    print(full_content)
                    print("=" * 30)
                    
                    # Check if reasoning was applied
                    if "Step" in full_content and ("1" in full_content or "2" in full_content):
                        print("✅ Reasoning steps detected!")
                    else:
                        print("❌ No reasoning steps found")
                        
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"📄 Response: {response.text}")
                    
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

def test_non_streaming_reasoning():
    """Test the non-streaming reasoning chat endpoint for comparison"""
    
    print("\n🧪 Testing Non-Streaming Reasoning Chat...")
    print("=" * 50)
    
    test_message = "Solve 2x + 3 = 7"
    
    try:
        with httpx.Client(timeout=30.0) as client:
            payload = {
                "message": test_message,
                "model": "llama3:latest",
                "use_reasoning": True,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True
            }
            
            response = client.post(
                "http://localhost:8000/api/v1/reasoning-chat/",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📤 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Non-streaming response received")
                print(f"📄 Response length: {len(data.get('response', ''))} characters")
                
                # Check if reasoning was applied
                response_text = data.get('response', '')
                if "Step" in response_text and ("1" in response_text or "2" in response_text):
                    print("✅ Reasoning steps detected!")
                else:
                    print("❌ No reasoning steps found")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Streaming Reasoning Chat Tests")
    print("=" * 60)
    
    # Test streaming first
    test_streaming_reasoning()
    
    # Test non-streaming for comparison
    test_non_streaming_reasoning()
    
    print("\n�� Tests completed!") 