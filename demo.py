#!/usr/bin/env python3
"""
Prompt Tune MVP - Interactive Demo
Showcases all features in a guided tour
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(title):
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def print_step(step, description):
    print(f"\n📍 Step {step}: {description}")
    print("-" * 40)

def demo_basic_optimization():
    print_header("BASIC PROMPT OPTIMIZATION")
    
    print_step(1, "Optimizing a simple prompt")
    
    payload = {
        "description": "Write a professional email to decline a meeting",
        "context": "The meeting conflicts with another important commitment",
        "model": "claude-haiku",
        "max_tokens": 600
    }
    
    print(f"📝 Input: {payload['description']}")
    print(f"🎯 Context: {payload['context']}")
    print(f"🤖 Model: {payload['model']}")
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/optimize-sync", json=payload)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Optimization completed in {end_time - start_time:.2f}s")
        print(f"💰 Cost: ${result['cost_estimate']}")
        print(f"\n🎯 Optimized Prompt:")
        print("-" * 40)
        print(result['optimized_prompt'][:300] + "...")
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        return None

def demo_caching():
    print_header("INTELLIGENT CACHING SYSTEM")
    
    print_step(1, "Making the same request twice to demonstrate caching")
    
    payload = {
        "description": "Create a social media post about AI technology",
        "model": "claude-haiku"
    }
    
    # First request
    print("🔄 First request (hits the AI model)...")
    start_time = time.time()
    response1 = requests.post(f"{BASE_URL}/optimize-sync", json=payload)
    time1 = time.time() - start_time
    
    # Second request
    print("🔄 Second request (should hit cache)...")
    start_time = time.time()
    response2 = requests.post(f"{BASE_URL}/optimize-sync", json=payload)
    time2 = time.time() - start_time
    
    if response1.status_code == 200 and response2.status_code == 200:
        speedup = time1 / time2 if time2 > 0 else float('inf')
        print(f"\n⚡ Performance Comparison:")
        print(f"   First request:  {time1:.3f}s")
        print(f"   Second request: {time2:.3f}s")
        print(f"   Speedup:        {speedup:.1f}x faster!")
        
        # Show cache stats
        cache_response = requests.get(f"{BASE_URL}/cache/stats")
        if cache_response.status_code == 200:
            stats = cache_response.json()
            print(f"\n📊 Cache Statistics:")
            print(f"   Total entries: {stats['total_entries']}")
            print(f"   Active entries: {stats['active_entries']}")
            print(f"   TTL: {stats['ttl_minutes']} minutes")

def demo_prompt_library():
    print_header("PROMPT LIBRARY MANAGEMENT")
    
    print_step(1, "Saving a prompt to the library")
    
    save_payload = {
        "name": "Demo: Professional Email Decline",
        "description": "A polite way to decline meeting invitations",
        "optimized_prompt": "Subject: Unable to Attend [Meeting Topic] - [Date]\n\nDear [Name],\n\nThank you for inviting me to [meeting topic] on [date]. Unfortunately, I have a prior commitment that conflicts with this time.\n\nI'm very interested in [topic/project] and would appreciate the opportunity to contribute. Could we explore alternative ways for me to stay involved, such as:\n\n- Reviewing meeting notes afterward\n- Scheduling a brief follow-up call\n- Contributing input via email before the meeting\n\nI apologize for any inconvenience and look forward to finding another way to participate.\n\nBest regards,\n[Your name]",
        "tags": ["email", "professional", "decline", "demo"]
    }
    
    response = requests.post(f"{BASE_URL}/library/save", json=save_payload)
    if response.status_code == 200:
        result = response.json()
        prompt_id = result['id']
        print(f"✅ Saved prompt with ID: {prompt_id}")
        
        print_step(2, "Retrieving the prompt from library")
        
        get_response = requests.get(f"{BASE_URL}/library/{prompt_id}")
        if get_response.status_code == 200:
            prompt = get_response.json()
            print(f"📚 Retrieved: {prompt['name']}")
            print(f"🏷️  Tags: {', '.join(prompt['tags'])}")
            print(f"📊 Usage count: {prompt['usage_count']}")
            
            print_step(3, "Viewing all prompts in library")
            
            library_response = requests.get(f"{BASE_URL}/library")
            if library_response.status_code == 200:
                library = library_response.json()
                print(f"📚 Library contains {len(library)} prompts")
                
                for i, p in enumerate(library[:3], 1):  # Show first 3
                    print(f"   {i}. {p['name']} (used {p['usage_count']} times)")
            
            print_step(4, "Cleaning up demo prompt")
            
            delete_response = requests.delete(f"{BASE_URL}/library/{prompt_id}")
            if delete_response.status_code == 200:
                print("🗑️  Demo prompt deleted successfully")

def demo_streaming():
    print_header("REAL-TIME STREAMING OPTIMIZATION")
    
    print_step(1, "Starting streaming optimization")
    
    payload = {
        "description": "Create a prompt for writing product descriptions that convert browsers into buyers",
        "context": "Focus on e-commerce and highlight emotional triggers",
        "model": "claude-haiku"
    }
    
    print(f"📝 Request: {payload['description']}")
    print(f"🎯 Context: {payload['context']}")
    print("\n🌊 Streaming response:")
    print("-" * 40)
    
    response = requests.post(f"{BASE_URL}/optimize", json=payload, stream=True)
    
    if response.status_code == 200:
        reasoning_steps = 0
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        
                        if data.get('type') == 'status':
                            print(f"📊 {data['message']}")
                        
                        elif data.get('type') == 'reasoning':
                            reasoning_steps += 1
                            print(f"🧠 Step {data['step']}: {data['content'][:80]}...")
                        
                        elif data.get('type') == 'result':
                            print(f"\n🎯 Final Result Received!")
                            print(f"💰 Cost: ${data['cost_estimate']}")
                            print(f"📏 Length: {len(data['optimized_prompt'])} characters")
                        
                        elif data.get('type') == 'complete':
                            print(f"✅ Streaming completed with {reasoning_steps} reasoning steps")
                            break
                            
                    except json.JSONDecodeError:
                        continue

def demo_statistics():
    print_header("USAGE STATISTICS & MONITORING")
    
    print_step(1, "Viewing system statistics")
    
    # Health check
    health_response = requests.get(f"{BASE_URL}/health")
    if health_response.status_code == 200:
        health = health_response.json()
        print(f"🏥 System Status: {health['status']}")
        print(f"📅 Timestamp: {health['timestamp']}")
        print(f"🤖 Models Available: {health['models_available']}")
    
    # Usage stats
    stats_response = requests.get(f"{BASE_URL}/stats")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"\n📊 Usage Statistics:")
        print(f"   Total prompts: {stats['total_prompts']}")
        print(f"   Total usage: {stats['total_usage']}")
        print(f"   Average usage: {stats['average_usage']:.2f}")
    
    # Cache stats
    cache_response = requests.get(f"{BASE_URL}/cache/stats")
    if cache_response.status_code == 200:
        cache_stats = cache_response.json()
        print(f"\n💾 Cache Performance:")
        print(f"   Total entries: {cache_stats['total_entries']}")
        print(f"   Active entries: {cache_stats['active_entries']}")
        print(f"   TTL: {cache_stats['ttl_minutes']} minutes")
    
    # Model information
    models_response = requests.get(f"{BASE_URL}/models")
    if models_response.status_code == 200:
        models = models_response.json()
        print(f"\n🤖 Available Models:")
        for model in models['models']:
            print(f"   • {model}")
        print(f"   Default: {models['default']}")

def main():
    print("🎯 PROMPT TUNE MVP - INTERACTIVE DEMO")
    print("🚀 Showcasing all features in a guided tour")
    print("=" * 60)
    
    try:
        # Check if server is running
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code != 200:
            print("❌ Backend server is not running!")
            print("Please start the server with: ./start-dev.sh")
            return
        
        print("✅ Backend server is running!")
        
        # Run all demos
        demo_basic_optimization()
        time.sleep(1)
        
        demo_caching()
        time.sleep(1)
        
        demo_prompt_library()
        time.sleep(1)
        
        demo_streaming()
        time.sleep(1)
        
        demo_statistics()
        
        print_header("DEMO COMPLETE!")
        print("🎉 All features demonstrated successfully!")
        print("\n📍 Next Steps:")
        print("   1. Open http://localhost:3000 to try the web interface")
        print("   2. Explore the API docs at http://localhost:8000/docs")
        print("   3. Run the full test suite: python3 test-all-features.py")
        print("   4. Deploy to production when ready!")
        
        print("\n✨ Your Prompt Tune MVP is ready for users!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server!")
        print("Please start the server with: ./start-dev.sh")
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")

if __name__ == "__main__":
    main()
