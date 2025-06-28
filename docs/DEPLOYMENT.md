# 🚀 Deployment Guide

This guide covers deploying Prompt Tune to production on AWS.

## 📋 Prerequisites

### Required Tools
- **AWS CLI** configured with appropriate permissions
- **Node.js 18+** for frontend build
- **Python 3.9+** for backend deployment
- **Git** for version control

### AWS Permissions
Your AWS user/role needs permissions for:
- Lambda (create, update, invoke)
- DynamoDB (create tables, read/write)
- S3 (create buckets, upload objects)
- CloudFront (create distributions)
- API Gateway (create APIs, deploy)
- CloudFormation (create/update stacks)
- IAM (create roles, attach policies)

## 🏗️ Infrastructure Setup

### 1. Configure AWS CLI
```bash
aws configure
# Enter your AWS Access Key ID, Secret, Region (us-east-1), and output format (json)
```

### 2. Set Environment Variables
```bash
export AWS_REGION=us-east-1
export ENVIRONMENT=production
export ANTHROPIC_API_KEY=your_anthropic_key_here
```

### 3. Deploy Infrastructure
```bash
# Option 1: Full automated deployment
python deploy-production.py

# Option 2: Step-by-step deployment
python deploy-aws.py --environment production
```

## 📦 Deployment Scripts

### `deploy-production.py`
Complete production deployment with:
- Infrastructure provisioning
- Frontend build and upload
- Backend deployment
- Configuration setup
- Health checks

### `deploy-aws.py`
Flexible deployment script with:
- Environment-specific configurations
- Rollback capabilities
- Monitoring setup
- Custom domain configuration

## 🔧 Configuration

### Environment Variables
Set these in AWS Systems Manager Parameter Store:

```bash
# API Keys
/prompt-tune/production/ANTHROPIC_API_KEY

# Application Settings
/prompt-tune/production/DEBUG=false
/prompt-tune/production/LOG_LEVEL=INFO
/prompt-tune/production/CACHE_TTL=3600

# Database Settings
/prompt-tune/production/DYNAMODB_TABLE_PREFIX=prompt-tune-prod
```

### Custom Domain (Optional)
1. Register domain in Route 53
2. Request SSL certificate in ACM
3. Update CloudFormation template with domain settings
4. Deploy with custom domain configuration

## 📊 Monitoring Setup

### CloudWatch Dashboards
The deployment automatically creates:
- **Application Metrics** - Response times, error rates
- **Infrastructure Metrics** - Lambda performance, DynamoDB usage
- **Cost Tracking** - Daily/monthly cost analysis
- **User Analytics** - Active users, feature usage

### Alerts
Configured alerts for:
- High error rates (>5%)
- Slow response times (>5 seconds)
- High costs (>$60/month)
- DynamoDB throttling

## 🔒 Security Configuration

### API Security
- API Gateway with API keys
- Rate limiting (1000 requests/minute)
- CORS configuration
- Request validation

### Data Security
- DynamoDB encryption at rest
- S3 bucket encryption
- CloudFront HTTPS only
- IAM least privilege access

## 🚀 Deployment Process

### 1. Pre-deployment Checks
```bash
# Run tests
cd frontend && npm test
cd ../backend && python -m pytest

# Validate infrastructure
aws cloudformation validate-template --template-body file://infrastructure/cloudformation-template.yaml
```

### 2. Deploy to Staging
```bash
python deploy-aws.py --environment staging
```

### 3. Run Integration Tests
```bash
python test-all-features.py --environment staging
```

### 4. Deploy to Production
```bash
python deploy-production.py
```

### 5. Post-deployment Verification
```bash
# Check health endpoints
curl https://api.prompt-tune.com/health

# Verify frontend
curl https://prompt-tune.com

# Check analytics
python complete-week-2.py --verify-production
```

## 🔄 CI/CD Pipeline

### GitHub Actions
The repository includes GitHub Actions workflows for:
- **Continuous Integration** - Run tests on every PR
- **Staging Deployment** - Auto-deploy develop branch
- **Production Deployment** - Auto-deploy main branch

### Setup CI/CD
1. Add AWS credentials to GitHub Secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
2. Push to `develop` branch for staging deployment
3. Merge to `main` branch for production deployment

## 📈 Scaling Configuration

### Auto-scaling Settings
- **Lambda**: Concurrent executions (1000)
- **DynamoDB**: On-demand billing mode
- **CloudFront**: Global edge locations
- **API Gateway**: Throttling limits

### Performance Optimization
- **Caching**: 1646x speedup with intelligent caching
- **CDN**: Global content delivery
- **Database**: Optimized queries and indexes
- **Lambda**: Memory and timeout optimization

## 💰 Cost Management

### Current Costs (Production)
- **Lambda**: ~$15/month (500+ daily users)
- **DynamoDB**: ~$10/month (on-demand)
- **S3 + CloudFront**: ~$5/month
- **API Gateway**: ~$5/month
- **Total**: $30-40/month

### Cost Optimization
- Use reserved capacity for predictable workloads
- Implement intelligent caching
- Monitor and optimize Lambda memory
- Use S3 lifecycle policies

## 🔧 Troubleshooting

### Common Issues

#### Deployment Fails
```bash
# Check CloudFormation events
aws cloudformation describe-stack-events --stack-name prompt-tune-production

# Check Lambda logs
aws logs tail /aws/lambda/prompt-tune-production --follow
```

#### High Latency
```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Duration

# Analyze X-Ray traces
aws xray get-trace-summaries --time-range-type TimeRangeByStartTime
```

#### Database Issues
```bash
# Check DynamoDB metrics
aws cloudwatch get-metric-statistics --namespace AWS/DynamoDB --metric-name ThrottledRequests

# Verify table configuration
aws dynamodb describe-table --table-name prompt-tune-production-prompts
```

### Support
- **GitHub Issues**: Technical problems
- **AWS Support**: Infrastructure issues
- **Documentation**: Comprehensive guides

## 🎯 Production Checklist

### Pre-launch
- [ ] All tests passing
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Documentation updated

### Launch
- [ ] Infrastructure deployed
- [ ] Application deployed
- [ ] DNS configured
- [ ] SSL certificates active
- [ ] Monitoring active
- [ ] Alerts configured

### Post-launch
- [ ] Health checks passing
- [ ] Performance metrics normal
- [ ] User feedback collected
- [ ] Cost tracking active
- [ ] Backup verification
- [ ] Documentation updated

## 🚀 Next Steps

After successful deployment:
1. **Monitor Performance** - Watch metrics and alerts
2. **Gather Feedback** - Collect user feedback
3. **Optimize Costs** - Monitor and optimize spending
4. **Scale Infrastructure** - Adjust based on usage
5. **Plan Updates** - Schedule regular updates

---

**🎉 Congratulations! Your Prompt Tune platform is now live in production!**
