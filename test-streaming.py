#!/usr/bin/env python3
"""
Test the streaming optimization endpoint
"""

import requests
import json
import time

def test_streaming_optimization():
    url = "http://localhost:8000/optimize"
    
    payload = {
        "description": "Create a prompt for writing engaging social media posts",
        "context": "The posts should be for a tech startup",
        "model": "claude-haiku",
        "max_tokens": 800,
        "temperature": 0.7
    }
    
    print("🧪 Testing streaming optimization...")
    print(f"📝 Description: {payload['description']}")
    print(f"🤖 Model: {payload['model']}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()
        
        reasoning_steps = []
        result = None
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        
                        if data.get('type') == 'status':
                            print(f"📊 Status: {data['message']}")
                        
                        elif data.get('type') == 'reasoning':
                            step_content = data['content']
                            print(f"🧠 Step {data['step']}: {step_content}")
                            reasoning_steps.append(step_content)
                        
                        elif data.get('type') == 'result':
                            result = data
                            print("\n" + "="*60)
                            print("🎯 OPTIMIZED PROMPT:")
                            print("="*60)
                            print(result['optimized_prompt'])
                            print("\n" + "="*60)
                            print(f"💰 Cost: ${result['cost_estimate']}")
                            print(f"🤖 Model: {result['model_used']}")
                            print(f"⏰ Time: {result['timestamp']}")
                        
                        elif data.get('type') == 'complete':
                            print("\n✅ Optimization complete!")
                            break
                        
                        elif data.get('type') == 'error':
                            print(f"❌ Error: {data['message']}")
                            return False
                            
                    except json.JSONDecodeError as e:
                        print(f"⚠️  JSON decode error: {e}")
                        continue
        
        if result:
            print(f"\n📊 Summary:")
            print(f"   • Reasoning steps: {len(reasoning_steps)}")
            print(f"   • Total cost: ${result['cost_estimate']}")
            print(f"   • Model used: {result['model_used']}")
            return True
        else:
            print("❌ No result received")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Prompt Tune MVP - Streaming Test")
    print("=" * 60)
    
    success = test_streaming_optimization()
    
    if success:
        print("\n🎉 Streaming test PASSED!")
        print("✨ Your Prompt Tune MVP is working perfectly!")
    else:
        print("\n💥 Streaming test FAILED!")
        print("🔧 Check the backend server and try again.")
