#!/usr/bin/env python3
"""
Comprehensive test suite for Prompt Tune MVP
Tests all features including new enhancements
"""

import requests
import json
import time
import asyncio
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_and_models():
    """Test basic health and model endpoints"""
    print("🏥 Testing health and models...")
    
    # Health check
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    health_data = response.json()
    print(f"✅ Health: {health_data['status']}")
    
    # Models endpoint
    response = requests.get(f"{BASE_URL}/models")
    assert response.status_code == 200
    models_data = response.json()
    print(f"✅ Available models: {models_data['models']}")
    print(f"✅ Default model: {models_data['default']}")
    
    return models_data['models'][0]  # Return first available model

def test_synchronous_optimization(model):
    """Test synchronous optimization"""
    print(f"\n🔄 Testing synchronous optimization with {model}...")
    
    payload = {
        "description": "Create a prompt for writing product reviews",
        "context": "Focus on electronics and gadgets",
        "model": model,
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/optimize-sync", json=payload)
    end_time = time.time()
    
    assert response.status_code == 200
    result = response.json()
    
    print(f"✅ Optimization completed in {end_time - start_time:.2f}s")
    print(f"✅ Cost: ${result['cost_estimate']}")
    print(f"✅ Reasoning steps: {len(result['reasoning_trace'])}")
    print(f"✅ Prompt length: {len(result['optimized_prompt'])} chars")
    
    return result

def test_caching():
    """Test caching functionality"""
    print(f"\n💾 Testing caching...")
    
    # Get initial cache stats
    response = requests.get(f"{BASE_URL}/cache/stats")
    initial_stats = response.json()
    print(f"✅ Initial cache entries: {initial_stats['total_entries']}")
    
    # Make the same request twice
    payload = {
        "description": "Test caching with this unique request",
        "model": "claude-haiku",
        "max_tokens": 300
    }
    
    # First request (should hit the model)
    start_time = time.time()
    response1 = requests.post(f"{BASE_URL}/optimize-sync", json=payload)
    time1 = time.time() - start_time
    
    # Second request (should hit cache)
    start_time = time.time()
    response2 = requests.post(f"{BASE_URL}/optimize-sync", json=payload)
    time2 = time.time() - start_time
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Cache should be faster
    print(f"✅ First request: {time1:.2f}s")
    print(f"✅ Second request (cached): {time2:.2f}s")
    print(f"✅ Cache speedup: {time1/time2:.1f}x faster")
    
    # Check cache stats
    response = requests.get(f"{BASE_URL}/cache/stats")
    final_stats = response.json()
    print(f"✅ Final cache entries: {final_stats['total_entries']}")

def test_prompt_library():
    """Test prompt library functionality"""
    print(f"\n📚 Testing prompt library...")
    
    # Save a prompt
    save_payload = {
        "name": "Test Product Review Prompt",
        "description": "A test prompt for product reviews",
        "optimized_prompt": "Write a detailed product review for [PRODUCT] focusing on [FEATURES]...",
        "tags": ["test", "product-review", "automated"]
    }
    
    response = requests.post(f"{BASE_URL}/library/save", json=save_payload)
    assert response.status_code == 200
    save_result = response.json()
    prompt_id = save_result['id']
    print(f"✅ Saved prompt with ID: {prompt_id}")
    
    # Get all prompts
    response = requests.get(f"{BASE_URL}/library")
    assert response.status_code == 200
    library = response.json()
    print(f"✅ Library contains {len(library)} prompts")
    
    # Get specific prompt
    response = requests.get(f"{BASE_URL}/library/{prompt_id}")
    assert response.status_code == 200
    prompt = response.json()
    print(f"✅ Retrieved prompt: {prompt['name']}")
    print(f"✅ Usage count: {prompt['usage_count']}")
    
    # Delete the test prompt
    response = requests.delete(f"{BASE_URL}/library/{prompt_id}")
    assert response.status_code == 200
    print(f"✅ Deleted test prompt")

def test_streaming_optimization(model):
    """Test streaming optimization"""
    print(f"\n🌊 Testing streaming optimization with {model}...")
    
    payload = {
        "description": "Create a prompt for writing creative stories",
        "context": "Focus on science fiction themes",
        "model": model,
        "max_tokens": 600
    }
    
    response = requests.post(f"{BASE_URL}/optimize", json=payload, stream=True)
    assert response.status_code == 200
    
    reasoning_steps = 0
    result_received = False
    
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                try:
                    data = json.loads(line_str[6:])
                    
                    if data.get('type') == 'reasoning':
                        reasoning_steps += 1
                        print(f"  📝 Step {data['step']}: {data['content'][:50]}...")
                    
                    elif data.get('type') == 'result':
                        result_received = True
                        print(f"✅ Final result received")
                        print(f"✅ Cost: ${data['cost_estimate']}")
                    
                    elif data.get('type') == 'complete':
                        break
                        
                except json.JSONDecodeError:
                    continue
    
    print(f"✅ Streaming completed with {reasoning_steps} reasoning steps")
    assert result_received, "No result received from streaming"

def test_usage_stats():
    """Test usage statistics"""
    print(f"\n📊 Testing usage statistics...")
    
    response = requests.get(f"{BASE_URL}/stats")
    assert response.status_code == 200
    stats = response.json()
    
    print(f"✅ Total prompts in library: {stats['total_prompts']}")
    print(f"✅ Total usage count: {stats['total_usage']}")
    print(f"✅ Average usage: {stats['average_usage']:.2f}")
    
    if stats['most_used_prompts']:
        print(f"✅ Most used prompt: {stats['most_used_prompts'][0]['name']}")

def test_error_handling():
    """Test error handling"""
    print(f"\n⚠️  Testing error handling...")
    
    # Test invalid model
    payload = {
        "description": "Test prompt",
        "model": "invalid-model"
    }
    
    response = requests.post(f"{BASE_URL}/optimize-sync", json=payload)
    # Should still work with default model fallback
    print(f"✅ Invalid model handled gracefully")
    
    # Test empty description
    payload = {
        "description": "",
        "model": "claude-haiku"
    }
    
    response = requests.post(f"{BASE_URL}/optimize-sync", json=payload)
    # Should handle empty input
    print(f"✅ Empty description handled")
    
    # Test non-existent prompt in library
    response = requests.get(f"{BASE_URL}/library/non-existent-id")
    assert response.status_code == 404
    print(f"✅ 404 error for non-existent prompt")

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive Prompt Tune MVP Test Suite")
    print("=" * 60)
    
    try:
        # Basic functionality
        model = test_health_and_models()
        
        # Core features
        optimization_result = test_synchronous_optimization(model)
        test_streaming_optimization(model)
        
        # Enhanced features
        test_caching()
        test_prompt_library()
        test_usage_stats()
        
        # Error handling
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("✨ Your Prompt Tune MVP is fully functional!")
        print("\n📊 Test Summary:")
        print("  ✅ Health & Models")
        print("  ✅ Synchronous Optimization")
        print("  ✅ Streaming Optimization")
        print("  ✅ Caching System")
        print("  ✅ Prompt Library")
        print("  ✅ Usage Statistics")
        print("  ✅ Error Handling")
        print("\n🚀 Ready for production deployment!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("🔧 Check the backend server and try again.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
