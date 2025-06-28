"""
Prompt Tune MVP - FastAPI Backend
Cost-effective prompt optimization using Amazon Bedrock
"""

import json
import os
from typing import Dict, List, Optional, AsyncGenerator
from datetime import datetime
import asyncio

import boto3
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from loguru import logger
import httpx

from cache import prompt_cache

# Initialize FastAPI app
app = FastAPI(
    title="Prompt Tune MVP",
    description="Cost-effective prompt optimization with real-time reasoning",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Configuration
MODELS = {
    "claude-haiku": "anthropic.claude-3-haiku-20240307-v1:0", 
    "claude-sonnet": "anthropic.claude-3-sonnet-20240229-v1:0"
}

DEFAULT_MODEL = "claude-haiku"
PROMPT_TABLE_NAME = "prompt-tune-library"

# Pydantic models
class PromptRequest(BaseModel):
    description: str
    context: Optional[str] = ""
    model: Optional[str] = DEFAULT_MODEL
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

class PromptResponse(BaseModel):
    optimized_prompt: str
    reasoning_trace: List[str]
    model_used: str
    timestamp: datetime
    cost_estimate: float

class SavePromptRequest(BaseModel):
    name: str
    description: str
    optimized_prompt: str
    tags: Optional[List[str]] = []

class PromptLibraryItem(BaseModel):
    id: str
    name: str
    description: str
    optimized_prompt: str
    tags: List[str]
    created_at: datetime
    usage_count: int

# Prompt engineering system prompt
SYSTEM_PROMPT = """You are an expert prompt engineer. Your task is to optimize prompts for maximum effectiveness while showing your reasoning process step by step.

When given a user's description of what they want to achieve, you should:

1. **Analyze** the user's intent and identify key requirements
2. **Consider** best practices for prompt engineering (clarity, specificity, examples, etc.)
3. **Structure** the prompt using proven techniques (role-playing, step-by-step instructions, etc.)
4. **Optimize** for the specific use case and model capabilities
5. **Validate** that the prompt addresses all requirements

Show your thinking process clearly in a "reasoning trace" format, then provide the final optimized prompt.

Format your response as JSON:
{
    "reasoning_trace": [
        "Step 1: Analysis - [your analysis]",
        "Step 2: Requirements - [key requirements identified]", 
        "Step 3: Structure - [how you'll structure the prompt]",
        "Step 4: Optimization - [specific optimizations made]",
        "Step 5: Validation - [final checks and improvements]"
    ],
    "optimized_prompt": "[your final optimized prompt]"
}"""

async def call_bedrock_model(model_id: str, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> Dict:
    """Call Bedrock model with streaming support"""
    try:
        if model_id.startswith("amazon.nova"):
            # Nova models use the new format
            body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": max_tokens,
                    "temperature": temperature
                }
            }
        elif model_id.startswith("anthropic.claude"):
            # Claude models
            body = {
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "anthropic_version": "bedrock-2023-05-31"
            }
        elif model_id.startswith("meta.llama"):
            # Llama models
            body = {
                "prompt": prompt,
                "max_gen_len": max_tokens,
                "temperature": temperature
            }
        elif model_id.startswith("amazon.titan"):
            # Titan models
            body = {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": max_tokens,
                    "temperature": temperature,
                    "topP": 0.9
                }
            }
        elif model_id.startswith("cohere.command"):
            # Cohere models
            body = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "p": 0.9
            }
        else:
            raise ValueError(f"Unsupported model: {model_id}")

        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        
        # Extract text based on model type
        if model_id.startswith("amazon.nova"):
            text = response_body['output']['message']['content'][0]['text']
        elif model_id.startswith("anthropic.claude"):
            text = response_body['content'][0]['text']
        elif model_id.startswith("meta.llama"):
            text = response_body['generation']
        elif model_id.startswith("amazon.titan"):
            text = response_body['results'][0]['outputText']
        elif model_id.startswith("cohere.command"):
            text = response_body['generations'][0]['text']
        else:
            text = str(response_body)
            
        return {"text": text, "usage": response_body.get("usage", {})}
        
    except Exception as e:
        logger.error(f"Error calling Bedrock model {model_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model call failed: {str(e)}")

def estimate_cost(model_id: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost based on model and token usage"""
    # Rough cost estimates per 1K tokens (input/output)
    costs = {
        "amazon.nova-lite-v1:0": (0.00006, 0.00024),  # Very cheap
        "anthropic.claude-3-haiku-20240307-v1:0": (0.00025, 0.00125),
        "anthropic.claude-3-5-sonnet-20240620-v1:0": (0.003, 0.015),
        "meta.llama3-8b-instruct-v1:0": (0.0003, 0.0006),
        "amazon.titan-text-express-v1": (0.0002, 0.0006),
        "cohere.command-light-text-v14": (0.0003, 0.0006)
    }
    
    input_cost, output_cost = costs.get(model_id, (0.0001, 0.0002))
    total_cost = (input_tokens / 1000 * input_cost) + (output_tokens / 1000 * output_cost)
    return round(total_cost, 6)

async def stream_prompt_optimization(request: PromptRequest) -> AsyncGenerator[str, None]:
    """Stream the prompt optimization process"""
    try:
        model_id = MODELS.get(request.model, MODELS[DEFAULT_MODEL])
        
        # Create the full prompt for the model
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser Request: {request.description}"
        if request.context:
            full_prompt += f"\nContext: {request.context}"
        
        # Yield initial status
        yield f"data: {json.dumps({'type': 'status', 'message': 'Starting optimization...'})}\n\n"
        
        # Call the model
        yield f"data: {json.dumps({'type': 'status', 'message': f'Calling {request.model} model...'})}\n\n"
        
        result = await call_bedrock_model(
            model_id, 
            full_prompt, 
            request.max_tokens, 
            request.temperature
        )
        
        # Parse the JSON response
        try:
            parsed_result = json.loads(result["text"])
            reasoning_trace = parsed_result.get("reasoning_trace", [])
            optimized_prompt = parsed_result.get("optimized_prompt", "")
        except json.JSONDecodeError:
            # Fallback if model doesn't return proper JSON
            reasoning_trace = ["Model response was not in expected JSON format"]
            optimized_prompt = result["text"]
        
        # Stream reasoning trace
        for i, step in enumerate(reasoning_trace):
            yield f"data: {json.dumps({'type': 'reasoning', 'step': i+1, 'content': step})}\n\n"
            await asyncio.sleep(0.1)  # Small delay for streaming effect
        
        # Calculate cost estimate
        input_tokens = len(full_prompt.split()) * 1.3  # Rough estimate
        output_tokens = len(result["text"].split()) * 1.3
        cost = estimate_cost(model_id, int(input_tokens), int(output_tokens))
        
        # Final result
        final_result = {
            "type": "result",
            "optimized_prompt": optimized_prompt,
            "reasoning_trace": reasoning_trace,
            "model_used": request.model,
            "timestamp": datetime.now().isoformat(),
            "cost_estimate": cost
        }
        
        yield f"data: {json.dumps(final_result)}\n\n"
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
        
    except Exception as e:
        logger.error(f"Error in stream_prompt_optimization: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Prompt Tune MVP API", 
        "version": "1.0.0",
        "features": [
            "Real-time prompt optimization",
            "Multiple AI models",
            "Prompt library management",
            "Cost estimation",
            "Streaming responses"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "models_available": len(MODELS),
        "database_connected": True  # Could add actual DB health check
    }

@app.get("/models")
async def get_available_models():
    return {
        "models": list(MODELS.keys()), 
        "default": DEFAULT_MODEL,
        "model_details": {
            model: {
                "id": model_id,
                "cost_per_1k_tokens": estimate_cost(model_id, 1000, 1000)
            }
            for model, model_id in MODELS.items()
        }
    }

@app.post("/optimize")
async def optimize_prompt_stream(request: PromptRequest):
    """Stream prompt optimization with real-time reasoning"""
    return StreamingResponse(
        stream_prompt_optimization(request),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.post("/optimize-sync")
async def optimize_prompt_sync(request: PromptRequest) -> PromptResponse:
    """Synchronous prompt optimization with caching"""
    
    # Check cache first
    cached_result = prompt_cache.get(request.description, request.context or "", request.model)
    if cached_result:
        logger.info("Returning cached result")
        return PromptResponse(**cached_result)
    
    model_id = MODELS.get(request.model, MODELS[DEFAULT_MODEL])
    
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser Request: {request.description}"
    if request.context:
        full_prompt += f"\nContext: {request.context}"
    
    result = await call_bedrock_model(model_id, full_prompt, request.max_tokens, request.temperature)
    
    try:
        parsed_result = json.loads(result["text"])
        reasoning_trace = parsed_result.get("reasoning_trace", [])
        optimized_prompt = parsed_result.get("optimized_prompt", "")
    except json.JSONDecodeError:
        reasoning_trace = ["Model response was not in expected JSON format"]
        optimized_prompt = result["text"]
    
    input_tokens = len(full_prompt.split()) * 1.3
    output_tokens = len(result["text"].split()) * 1.3
    cost = estimate_cost(model_id, int(input_tokens), int(output_tokens))
    
    response_data = {
        "optimized_prompt": optimized_prompt,
        "reasoning_trace": reasoning_trace,
        "model_used": request.model,
        "timestamp": datetime.now(),
        "cost_estimate": cost
    }
    
    # Cache the result
    prompt_cache.set(request.description, request.context or "", request.model, {
        "optimized_prompt": optimized_prompt,
        "reasoning_trace": reasoning_trace,
        "model_used": request.model,
        "timestamp": datetime.now().isoformat(),
        "cost_estimate": cost
    })
    
    return PromptResponse(**response_data)

# Prompt Library endpoints (DynamoDB integration)
@app.post("/library/save")
async def save_prompt(request: SavePromptRequest):
    """Save optimized prompt to library"""
    try:
        table = dynamodb.Table(PROMPT_TABLE_NAME)
        
        item = {
            "id": f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "name": request.name,
            "description": request.description,
            "optimized_prompt": request.optimized_prompt,
            "tags": request.tags,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        table.put_item(Item=item)
        return {"message": "Prompt saved successfully", "id": item["id"]}
        
    except Exception as e:
        logger.error(f"Error saving prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save prompt: {str(e)}")

@app.get("/library")
async def get_prompt_library() -> List[PromptLibraryItem]:
    """Get all saved prompts from library"""
    try:
        table = dynamodb.Table(PROMPT_TABLE_NAME)
        response = table.scan()
        
        items = []
        for item in response.get('Items', []):
            items.append(PromptLibraryItem(
                id=item["id"],
                name=item["name"],
                description=item["description"],
                optimized_prompt=item["optimized_prompt"],
                tags=item.get("tags", []),
                created_at=datetime.fromisoformat(item["created_at"]),
                usage_count=item.get("usage_count", 0)
            ))
        
        return sorted(items, key=lambda x: x.created_at, reverse=True)
        
    except Exception as e:
        logger.error(f"Error getting prompt library: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get library: {str(e)}")

@app.get("/library/{prompt_id}")
async def get_prompt(prompt_id: str) -> PromptLibraryItem:
    """Get specific prompt by ID"""
    try:
        table = dynamodb.Table(PROMPT_TABLE_NAME)
        response = table.get_item(Key={"id": prompt_id})
        
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        item = response["Item"]
        
        # Increment usage count
        table.update_item(
            Key={"id": prompt_id},
            UpdateExpression="SET usage_count = usage_count + :inc",
            ExpressionAttributeValues={":inc": 1}
        )
        
        return PromptLibraryItem(
            id=item["id"],
            name=item["name"],
            description=item["description"],
            optimized_prompt=item["optimized_prompt"],
            tags=item.get("tags", []),
            created_at=datetime.fromisoformat(item["created_at"]),
            usage_count=item.get("usage_count", 0) + 1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt {prompt_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get prompt: {str(e)}")

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    return prompt_cache.stats()

@app.post("/cache/clear")
async def clear_cache():
    """Clear the cache"""
    prompt_cache.clear()
    return {"message": "Cache cleared successfully"}

@app.delete("/library/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """Delete a prompt from the library"""
    try:
        table = dynamodb.Table(PROMPT_TABLE_NAME)
        
        # Check if prompt exists
        response = table.get_item(Key={"id": prompt_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        # Delete the prompt
        table.delete_item(Key={"id": prompt_id})
        
        return {"message": "Prompt deleted successfully", "id": prompt_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prompt {prompt_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete prompt: {str(e)}")

@app.get("/stats")
async def get_usage_stats():
    """Get usage statistics"""
    try:
        table = dynamodb.Table(PROMPT_TABLE_NAME)
        response = table.scan()
        
        prompts = response.get('Items', [])
        total_prompts = len(prompts)
        total_usage = sum(item.get('usage_count', 0) for item in prompts)
        
        # Get most used prompts
        most_used = sorted(prompts, key=lambda x: x.get('usage_count', 0), reverse=True)[:5]
        
        return {
            "total_prompts": total_prompts,
            "total_usage": total_usage,
            "average_usage": total_usage / total_prompts if total_prompts > 0 else 0,
            "most_used_prompts": [
                {
                    "name": p["name"],
                    "usage_count": p.get("usage_count", 0)
                }
                for p in most_used
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
