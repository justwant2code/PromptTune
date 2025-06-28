"""
Test script for Prompt Tune MVP backend
"""

import asyncio
import json
import httpx
from main import app, optimize_prompt_sync, PromptRequest

async def test_bedrock_connection():
    """Test basic Bedrock connectivity"""
    print("🧪 Testing Bedrock connection...")
    
    try:
        request = PromptRequest(
            description="Create a prompt for writing a professional email",
            model="claude-haiku",
            max_tokens=500
        )
        
        result = await optimize_prompt_sync(request)
        print(f"✅ Bedrock test successful!")
        print(f"Model used: {result.model_used}")
        print(f"Cost estimate: ${result.cost_estimate}")
        print(f"Reasoning steps: {len(result.reasoning_trace)}")
        print(f"Optimized prompt preview: {result.optimized_prompt[:100]}...")
        
    except Exception as e:
        print(f"❌ Bedrock test failed: {str(e)}")

async def test_models():
    """Test different models"""
    print("\n🧪 Testing different models...")
    
    models = ["claude-haiku", "claude-sonnet", "claude-sonnet-legacy", "llama-8b", "llama-70b"]
    
    for model in models:
        try:
            print(f"\nTesting {model}...")
            request = PromptRequest(
                description="Write a prompt for creative writing",
                model=model,
                max_tokens=300
            )
            
            result = await optimize_prompt_sync(request)
            print(f"✅ {model}: Cost ${result.cost_estimate}, Steps: {len(result.reasoning_trace)}")
            
        except Exception as e:
            print(f"❌ {model} failed: {str(e)}")

async def main():
    print("🚀 Starting Prompt Tune MVP Backend Tests\n")
    
    await test_bedrock_connection()
    await test_models()
    
    print("\n✨ Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
