#!/usr/bin/env python3
"""
Simple UI streaming test with visible delays
"""

import httpx
import json
import time
import sys

def test_ui_streaming():
    """Test streaming with UI-like display and delays"""
    print("🚀 Phase 2 Streaming UI Test")
    print("=" * 60)
    print("This simulates what you should see in the UI with streaming enabled")
    print("=" * 60)
    
    try:
        with httpx.Client() as client:
            payload = {
                "message": "Explain how a computer works in simple terms.",
                "model": "llama3:latest",
                "engine_type": "auto",
                "use_phase2_reasoning": True,
                "show_steps": True,
                "output_format": "markdown",
                "include_validation": True
            }
            
            print("📤 Sending request...")
            print("📤 Message:", payload['message'])
            print("=" * 60)
            
            # Simulate UI display
            print("🤖 Assistant:")
            print("_" * 40)
            
            full_response = ""
            chunk_count = 0
            
            with client.stream(
                "POST",
                "http://localhost:8000/api/v1/phase2-reasoning/stream",
                json=payload,
                timeout=120.0,
                headers={"Accept": "text/event-stream", "Connection": "keep-alive"}
            ) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            if line.startswith('data: '):
                                data_str = line[6:]
                                try:
                                    data = json.loads(data_str)
                                    
                                    if "content" in data:
                                        chunk = data["content"]
                                        full_response += chunk
                                        chunk_count += 1
                                        
                                        # Display chunk with cursor (like UI)
                                        print(chunk, end="", flush=True)
                                        
                                        # Add delay to see streaming effect
                                        time.sleep(0.1)  # 100ms delay
                                    
                                    if data.get("final"):
                                        print("\n" + "=" * 60)
                                        print("✅ Final message received!")
                                        print(f"📊 Total chunks: {chunk_count}")
                                        print(f"🔧 Engine used: {data.get('engine_used', 'unknown')}")
                                        print(f"🧠 Reasoning type: {data.get('reasoning_type', 'unknown')}")
                                        print(f"📊 Steps count: {data.get('steps_count', 0)}")
                                        print(f"🎯 Confidence: {data.get('confidence', 0.0)}")
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
    print("💡 Tip: This test adds 100ms delays between chunks to show streaming effect")
    print("💡 In the real UI, chunks arrive much faster (every ~0.7 seconds)")
    print("=" * 60)
    
    success = test_ui_streaming()
    if success:
        print("\n✅ Streaming test PASSED")
        print("📊 You can see chunks appearing one by one!")
        sys.exit(0)
    else:
        print("\n❌ Streaming test FAILED")
        sys.exit(1) 