# Prompt Tune MVP

A cost-effective web application that generates optimized prompts with real-time chain-of-thought reasoning using Amazon Bedrock.

## Architecture Overview

### Phase 1: MVP with Bedrock (Target: $50/month)
- **Frontend**: React app with streaming display
- **Backend**: FastAPI with Bedrock integration
- **Database**: DynamoDB for prompt library
- **AI**: Amazon Bedrock (Claude/Llama models)
- **Hosting**: AWS Lambda + CloudFront
- **Storage**: S3 for static assets

### Phase 2: Custom Model (Future scaling)
- **Model**: Fine-tuned Llama 3.1 on SageMaker
- **Training**: Custom prompt engineering dataset
- **Inference**: SageMaker endpoints with auto-scaling

## Cost Breakdown (Phase 1)

| Service | Estimated Monthly Cost |
|---------|----------------------|
| Bedrock API calls | $20-30 |
| DynamoDB | $5 |
| Lambda | $5 |
| CloudFront | $5 |
| S3 | $2 |
| **Total** | **~$37-47/month** |

## Features

### Core Features
- ✅ Prompt optimization from user descriptions
- ✅ Real-time chain-of-thought reasoning display
- ✅ Basic prompt library (save/load)
- ✅ Clean, minimal web interface

### Technical Features
- ✅ Streaming responses for real-time feedback
- ✅ Cost-optimized serverless architecture
- ✅ Auto-scaling based on demand
- ✅ Monitoring and alerting

## Development Timeline

### Week 1
- [x] MCP servers setup
- [ ] Backend API development
- [ ] Bedrock integration
- [ ] DynamoDB setup
- [ ] Basic prompt engineering logic

### Week 2
- [ ] Frontend development
- [ ] Streaming implementation
- [ ] Deployment automation
- [ ] Testing and optimization
- [ ] Documentation

## Getting Started

1. **Prerequisites**
   - AWS CLI configured
   - Python 3.13+
   - Node.js 18+
   - MCP servers installed

2. **Setup**
   ```bash
   cd prompt-tune-mvp
   # Backend setup
   cd backend && pip install -r requirements.txt
   # Frontend setup
   cd ../frontend && npm install
   ```

3. **Development**
   ```bash
   # Start backend
   cd backend && uvicorn main:app --reload
   # Start frontend
   cd frontend && npm start
   ```

## MCP Servers Available

- `cost-analysis-mcp-server` - AWS cost monitoring
- `aws-bedrock-data-automation-mcp-server` - Bedrock integration
- `dynamodb-mcp-server` - DynamoDB operations
- `lambda-tool-mcp-server` - Lambda functions

## Next Steps

1. Set up Bedrock access and test models
2. Create the FastAPI backend structure
3. Implement prompt engineering logic
4. Build React frontend with streaming
5. Deploy to AWS with infrastructure as code
