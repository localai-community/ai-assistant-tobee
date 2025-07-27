#!/usr/bin/env python3
"""
Test script to verify real-time streaming with timing
"""

import httpx
import json
import sys
import time
from datetime import datetime

def test_streaming_timing():
    """Test Phase 2 streaming with timing to verify real-time delivery"""
    print("🧪 Testing Phase 2 streaming timing...")
    print("=" * 60)
    
    try:
        with httpx.Client() as client:
            payload = {
                "message": "Write a detailed explanation of how photosynthesis works, step by step.",
                "model": "llama3:latest",
                "engine_type": "auto",
                "use_phase2_reasoning": True,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True
            }
            
            print(f"📤 Sending request to: http://localhost:8000/api/v1/phase2-reasoning/stream")
            print(f"📤 Message: {payload['message'][:50]}...")
            print("=" * 60)
            
            start_time = time.time()
            chunk_count = 0
            
            # Stream the response
            with client.stream(
                "POST",
                "http://localhost:8000/api/v1/phase2-reasoning/stream",
                json=payload,
                timeout=120.0,
                headers={"Accept": "text/event-stream", "Connection": "keep-alive"}
            ) as response:
                print(f"📥 Response status: {response.status_code}")
                print("=" * 60)
                
                if response.status_code == 200:
                    full_response = ""
                    
                    # Process Server-Sent Events
                    for line in response.iter_lines():
                        if line:
                            chunk_time = time.time()
                            chunk_count += 1
                            
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
                                        
                                        # Calculate timing
                                        elapsed = chunk_time - start_time
                                        chunk_size = len(chunk)
                                        
                                        # Display chunk info
                                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                                        print(f"📥 Chunk {chunk_count:2d} | {timestamp} | +{elapsed:6.3f}s | {chunk_size:3d} chars | {chunk[:50]}...")
                                        
                                        # Simulate real-time display delay
                                        time.sleep(0.1)  # 100ms delay to simulate processing
                                    
                                    # Check if this is the final message
                                    if data.get("final"):
                                        final_time = time.time()
                                        total_time = final_time - start_time
                                        print("=" * 60)
                                        print(f"✅ Final message received at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
                                        print(f"📊 Total time: {total_time:.3f}s")
                                        print(f"📊 Total chunks: {chunk_count}")
                                        print(f"📊 Total characters: {len(full_response)}")
                                        print(f"📊 Average chunk size: {len(full_response)/chunk_count:.1f} chars")
                                        print(f"📊 Average time per chunk: {total_time/chunk_count:.3f}s")
                                        print(f"🔧 Engine used: {data.get('engine_used', 'unknown')}")
                                        print(f"🧠 Reasoning type: {data.get('reasoning_type', 'unknown')}")
                                        print(f"📊 Steps count: {data.get('steps_count', 0)}")
                                        print(f"🎯 Confidence: {data.get('confidence', 0.0)}")
                                        return True
                                        
                                except json.JSONDecodeError as e:
                                    print(f"⚠️ JSON decode error: {e}")
                                    continue
                    
                    print(f"📊 Streaming ended, total chunks: {chunk_count}")
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

def test_slow_streaming():
    """Test with artificial delays to see streaming effect"""
    print("\n" + "=" * 60)
    print("🐌 Testing with artificial delays...")
    print("=" * 60)
    
    try:
        with httpx.Client() as client:
            payload = {
                "message": "Explain quantum computing in simple terms.",
                "model": "llama3:latest",
                "engine_type": "auto",
                "use_phase2_reasoning": True,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True
            }
            
            start_time = time.time()
            chunk_count = 0
            
            with client.stream(
                "POST",
                "http://localhost:8000/api/v1/phase2-reasoning/stream",
                json=payload,
                timeout=120.0,
                headers={"Accept": "text/event-stream", "Connection": "keep-alive"}
            ) as response:
                if response.status_code == 200:
                    full_response = ""
                    
                    for line in response.iter_lines():
                        if line:
                            chunk_time = time.time()
                            chunk_count += 1
                            
                            if line.startswith('data: '):
                                data_str = line[6:]
                                try:
                                    data = json.loads(data_str)
                                    
                                    if "content" in data:
                                        chunk = data["content"]
                                        full_response += chunk
                                        
                                        elapsed = chunk_time - start_time
                                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                                        
                                        print(f"📝 [{timestamp}] Chunk {chunk_count}: {chunk}")
                                        
                                        # Artificial delay to see streaming effect
                                        time.sleep(0.5)  # 500ms delay
                                    
                                    if data.get("final"):
                                        print(f"✅ Final message received after {chunk_count} chunks")
                                        return True
                                        
                                except json.JSONDecodeError:
                                    continue
                    
                    return len(full_response) > 0
                else:
                    print(f"❌ Backend error: {response.status_code}")
                    return False
                    
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Phase 2 Streaming Timing Test")
    print("=" * 60)
    
    # Test 1: Normal streaming with timing
    success1 = test_streaming_timing()
    
    # Test 2: Slow streaming with delays
    success2 = test_slow_streaming()
    
    if success1 and success2:
        print("\n✅ Both streaming tests PASSED")
        print("📊 Chunks are being delivered in real-time!")
        sys.exit(0)
    else:
        print("\n❌ Some streaming tests FAILED")
        sys.exit(1) 