#!/usr/bin/env python3
"""
AWS Deployment Script for Prompt Tune MVP
Deploys backend to Lambda and frontend to S3/CloudFront
"""

import boto3
import json
import zipfile
import os
import subprocess
from datetime import datetime

class PromptTuneDeployer:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.lambda_client = boto3.client('lambda')
        self.cloudfront = boto3.client('cloudfront')
        self.apigateway = boto3.client('apigateway')
        
        self.project_name = "prompt-tune-mvp"
        self.bucket_name = f"{self.project_name}-frontend-{datetime.now().strftime('%Y%m%d')}"
        self.lambda_function_name = f"{self.project_name}-backend"
        
    def create_s3_bucket(self):
        """Create S3 bucket for frontend hosting"""
        print("🪣 Creating S3 bucket for frontend...")
        
        try:
            self.s3.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration={'LocationConstraint': 'us-east-1'}
            )
            
            # Configure bucket for static website hosting
            self.s3.put_bucket_website(
                Bucket=self.bucket_name,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'index.html'},
                    'ErrorDocument': {'Key': 'error.html'}
                }
            )
            
            # Make bucket public for website hosting
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                    }
                ]
            }
            
            self.s3.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            
            print(f"✅ S3 bucket created: {self.bucket_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create S3 bucket: {str(e)}")
            return False
    
    def build_frontend(self):
        """Build React frontend for production"""
        print("🏗️  Building React frontend...")
        
        try:
            # Change to frontend directory and build
            os.chdir('frontend')
            result = subprocess.run(['npm', 'run', 'build'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Frontend build failed: {result.stderr}")
                return False
            
            print("✅ Frontend built successfully")
            os.chdir('..')
            return True
            
        except Exception as e:
            print(f"❌ Frontend build error: {str(e)}")
            return False
    
    def deploy_frontend(self):
        """Deploy frontend to S3"""
        print("🚀 Deploying frontend to S3...")
        
        try:
            build_dir = 'frontend/build'
            
            for root, dirs, files in os.walk(build_dir):
                for file in files:
                    local_path = os.path.join(root, file)
                    s3_path = os.path.relpath(local_path, build_dir)
                    
                    # Determine content type
                    content_type = 'text/html'
                    if file.endswith('.js'):
                        content_type = 'application/javascript'
                    elif file.endswith('.css'):
                        content_type = 'text/css'
                    elif file.endswith('.json'):
                        content_type = 'application/json'
                    elif file.endswith('.png'):
                        content_type = 'image/png'
                    elif file.endswith('.jpg') or file.endswith('.jpeg'):
                        content_type = 'image/jpeg'
                    
                    self.s3.upload_file(
                        local_path,
                        self.bucket_name,
                        s3_path,
                        ExtraArgs={'ContentType': content_type}
                    )
            
            website_url = f"http://{self.bucket_name}.s3-website-us-east-1.amazonaws.com"
            print(f"✅ Frontend deployed to: {website_url}")
            return website_url
            
        except Exception as e:
            print(f"❌ Frontend deployment failed: {str(e)}")
            return None
    
    def package_backend(self):
        """Package backend for Lambda deployment"""
        print("📦 Packaging backend for Lambda...")
        
        try:
            # Create deployment package
            with zipfile.ZipFile('lambda-deployment.zip', 'w') as zip_file:
                # Add backend files
                for root, dirs, files in os.walk('backend'):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            zip_file.write(file_path, file)
                
                # Add dependencies (would need to install in Lambda-compatible way)
                # This is simplified - in production, use Lambda layers or container images
            
            print("✅ Backend packaged for Lambda")
            return True
            
        except Exception as e:
            print(f"❌ Backend packaging failed: {str(e)}")
            return False
    
    def create_lambda_function(self):
        """Create Lambda function for backend"""
        print("⚡ Creating Lambda function...")
        
        try:
            with open('lambda-deployment.zip', 'rb') as zip_file:
                zip_content = zip_file.read()
            
            response = self.lambda_client.create_function(
                FunctionName=self.lambda_function_name,
                Runtime='python3.9',
                Role='arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role',  # Need to create this
                Handler='main.handler',
                Code={'ZipFile': zip_content},
                Description='Prompt Tune MVP Backend',
                Timeout=30,
                MemorySize=512,
                Environment={
                    'Variables': {
                        'ENVIRONMENT': 'production'
                    }
                }
            )
            
            function_arn = response['FunctionArn']
            print(f"✅ Lambda function created: {function_arn}")
            return function_arn
            
        except Exception as e:
            print(f"❌ Lambda function creation failed: {str(e)}")
            return None
    
    def create_api_gateway(self, lambda_arn):
        """Create API Gateway for Lambda function"""
        print("🌐 Creating API Gateway...")
        
        try:
            # This is a simplified version - full implementation would be more complex
            api_response = self.apigateway.create_rest_api(
                name=f"{self.project_name}-api",
                description="API for Prompt Tune MVP"
            )
            
            api_id = api_response['id']
            api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
            
            print(f"✅ API Gateway created: {api_url}")
            return api_url
            
        except Exception as e:
            print(f"❌ API Gateway creation failed: {str(e)}")
            return None
    
    def deploy(self):
        """Deploy the entire application"""
        print("🚀 Starting AWS Deployment for Prompt Tune MVP")
        print("=" * 60)
        
        # Frontend deployment
        if not self.create_s3_bucket():
            return False
        
        if not self.build_frontend():
            return False
        
        frontend_url = self.deploy_frontend()
        if not frontend_url:
            return False
        
        # Backend deployment (simplified)
        print("\n⚠️  Backend deployment requires additional setup:")
        print("  1. Create IAM role for Lambda execution")
        print("  2. Install dependencies in Lambda-compatible format")
        print("  3. Configure API Gateway properly")
        print("  4. Set up CloudFront distribution")
        
        print(f"\n🎉 Frontend deployed successfully!")
        print(f"📍 Frontend URL: {frontend_url}")
        print(f"\n📋 Next steps for full deployment:")
        print("  1. Complete backend Lambda setup")
        print("  2. Configure custom domain")
        print("  3. Set up SSL certificate")
        print("  4. Configure monitoring and logging")
        
        return True

def main():
    """Main deployment function"""
    deployer = PromptTuneDeployer()
    
    print("⚠️  This is a simplified deployment script.")
    print("For production deployment, consider using:")
    print("  - AWS CDK or CloudFormation")
    print("  - Serverless Framework")
    print("  - AWS Amplify")
    print("\nProceed with basic deployment? (y/n): ", end="")
    
    if input().lower() != 'y':
        print("Deployment cancelled.")
        return
    
    success = deployer.deploy()
    
    if success:
        print("\n✅ Deployment completed successfully!")
    else:
        print("\n❌ Deployment failed. Check the logs above.")

if __name__ == "__main__":
    main()
