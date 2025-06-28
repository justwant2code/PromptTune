#!/usr/bin/env python3
"""
Domain Setup Monitoring Script for prompttune.io
Monitors DNS propagation and SSL certificate validation
"""

import boto3
import time
import subprocess
import json
from datetime import datetime

def check_dns_propagation():
    """Check if DNS has propagated"""
    try:
        result = subprocess.run(['nslookup', '-type=NS', 'prompttune.io'], 
                              capture_output=True, text=True, timeout=10)
        
        if 'awsdns' in result.stdout:
            return True, "DNS propagated to AWS Route 53"
        else:
            return False, "DNS still propagating"
    except Exception as e:
        return False, f"DNS check failed: {str(e)}"

def check_certificate_status():
    """Check SSL certificate validation status"""
    try:
        acm = boto3.client('acm', region_name='us-east-1')
        response = acm.describe_certificate(
            CertificateArn='arn:aws:acm:us-east-1:161693365686:certificate/35fbac3a-9106-4c5a-8171-a0b7e5e1126f'
        )
        
        cert = response['Certificate']
        status = cert['Status']
        
        if status == 'ISSUED':
            return True, "SSL certificate validated and issued"
        elif status == 'PENDING_VALIDATION':
            return False, "SSL certificate still validating"
        else:
            return False, f"SSL certificate status: {status}"
            
    except Exception as e:
        return False, f"Certificate check failed: {str(e)}"

def create_cloudfront_distribution():
    """Create CloudFront distribution once certificate is ready"""
    try:
        cloudfront = boto3.client('cloudfront')
        
        distribution_config = {
            'CallerReference': f'prompttune-{int(time.time())}',
            'Aliases': {
                'Quantity': 2,
                'Items': ['prompttune.io', 'www.prompttune.io']
            },
            'DefaultRootObject': 'index.html',
            'Origins': {
                'Quantity': 2,
                'Items': [
                    {
                        'Id': 'S3Origin',
                        'DomainName': 'prompt-tune-frontend-161693365686.s3-website-us-east-1.amazonaws.com',
                        'CustomOriginConfig': {
                            'HTTPPort': 80,
                            'HTTPSPort': 443,
                            'OriginProtocolPolicy': 'http-only'
                        }
                    },
                    {
                        'Id': 'ApiOrigin',
                        'DomainName': 'v4hpbo4znc.execute-api.us-east-1.amazonaws.com',
                        'OriginPath': '/prod',
                        'CustomOriginConfig': {
                            'HTTPPort': 80,
                            'HTTPSPort': 443,
                            'OriginProtocolPolicy': 'https-only'
                        }
                    }
                ]
            },
            'DefaultCacheBehavior': {
                'TargetOriginId': 'S3Origin',
                'ViewerProtocolPolicy': 'redirect-to-https',
                'MinTTL': 0,
                'ForwardedValues': {
                    'QueryString': False,
                    'Cookies': {'Forward': 'none'}
                },
                'TrustedSigners': {
                    'Enabled': False,
                    'Quantity': 0
                }
            },
            'CacheBehaviors': {
                'Quantity': 1,
                'Items': [
                    {
                        'PathPattern': '/api/*',
                        'TargetOriginId': 'ApiOrigin',
                        'ViewerProtocolPolicy': 'https-only',
                        'MinTTL': 0,
                        'ForwardedValues': {
                            'QueryString': True,
                            'Headers': {
                                'Quantity': 3,
                                'Items': ['Authorization', 'Content-Type', 'Origin']
                            },
                            'Cookies': {'Forward': 'none'}
                        },
                        'TrustedSigners': {
                            'Enabled': False,
                            'Quantity': 0
                        }
                    }
                ]
            },
            'Comment': 'CloudFront distribution for prompttune.io',
            'Enabled': True,
            'ViewerCertificate': {
                'ACMCertificateArn': 'arn:aws:acm:us-east-1:161693365686:certificate/35fbac3a-9106-4c5a-8171-a0b7e5e1126f',
                'SSLSupportMethod': 'sni-only',
                'MinimumProtocolVersion': 'TLSv1.2_2021'
            },
            'CustomErrorResponses': {
                'Quantity': 1,
                'Items': [
                    {
                        'ErrorCode': 404,
                        'ResponsePagePath': '/index.html',
                        'ResponseCode': '200',
                        'ErrorCachingMinTTL': 300
                    }
                ]
            },
            'PriceClass': 'PriceClass_100'
        }
        
        response = cloudfront.create_distribution(DistributionConfig=distribution_config)
        return True, response['Distribution']['Id']
        
    except Exception as e:
        return False, f"CloudFront creation failed: {str(e)}"

def main():
    """Main monitoring function"""
    print("🌐 PROMPTTUNE.IO DOMAIN SETUP MONITOR")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    dns_ready = False
    cert_ready = False
    cloudfront_created = False
    
    while not (dns_ready and cert_ready and cloudfront_created):
        print(f"⏰ Checking status at {datetime.now().strftime('%H:%M:%S')}...")
        
        # Check DNS propagation
        if not dns_ready:
            dns_ready, dns_msg = check_dns_propagation()
            status = "✅" if dns_ready else "🔄"
            print(f"   {status} DNS: {dns_msg}")
        
        # Check certificate
        if not cert_ready:
            cert_ready, cert_msg = check_certificate_status()
            status = "✅" if cert_ready else "🔄"
            print(f"   {status} SSL: {cert_msg}")
        
        # Create CloudFront if both are ready
        if dns_ready and cert_ready and not cloudfront_created:
            print("   🚀 Creating CloudFront distribution...")
            cf_success, cf_msg = create_cloudfront_distribution()
            if cf_success:
                cloudfront_created = True
                print(f"   ✅ CloudFront: Distribution created - {cf_msg}")
                print()
                print("🎉 DOMAIN SETUP COMPLETE!")
                print("   Your app will be live at https://prompttune.io")
                print("   CloudFront deployment takes 15-20 minutes")
                break
            else:
                print(f"   ❌ CloudFront: {cf_msg}")
        
        if not (dns_ready and cert_ready and cloudfront_created):
            print("   ⏳ Waiting 60 seconds before next check...")
            print()
            time.sleep(60)
    
    print("🎊 Setup monitoring complete!")

if __name__ == "__main__":
    main()
