"""
Advanced Analytics Module for Prompt Tune MVP
Handles usage tracking, cost monitoring, and performance analytics
"""

import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class AnalyticsManager:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.dynamodb = boto3.resource('dynamodb')
        
        # Analytics table for detailed tracking
        self.analytics_table = self.dynamodb.Table('prompt-tune-analytics')
        
        # In-memory cache for real-time metrics
        self.metrics_cache = {
            'requests_today': 0,
            'users_today': set(),
            'total_cost_today': 0.0,
            'error_count': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'model_usage': defaultdict(int),
            'template_usage': defaultdict(int),
            'response_times': [],
            'hourly_usage': defaultdict(int)
        }
        
        # Cost per model (per 1K tokens)
        self.model_costs = {
            'claude-haiku': 0.00025,
            'claude-sonnet': 0.003,
            'claude-opus': 0.015
        }
    
    async def track_request(self, 
                          user_id: str,
                          model: str,
                          template: Optional[str] = None,
                          tokens_used: int = 0,
                          response_time: float = 0.0,
                          cache_hit: bool = False,
                          error: bool = False):
        """Track a single request with comprehensive metrics"""
        
        try:
            timestamp = datetime.utcnow()
            hour_key = timestamp.strftime('%H')
            
            # Update in-memory cache
            self.metrics_cache['requests_today'] += 1
            self.metrics_cache['users_today'].add(user_id)
            self.metrics_cache['model_usage'][model] += 1
            self.metrics_cache['hourly_usage'][hour_key] += 1
            self.metrics_cache['response_times'].append(response_time)
            
            if template:
                self.metrics_cache['template_usage'][template] += 1
            
            if cache_hit:
                self.metrics_cache['cache_hits'] += 1
            else:
                self.metrics_cache['cache_misses'] += 1
            
            if error:
                self.metrics_cache['error_count'] += 1
            
            # Calculate cost
            cost = (tokens_used / 1000) * self.model_costs.get(model, 0.001)
            self.metrics_cache['total_cost_today'] += cost
            
            # Store detailed record in DynamoDB
            await self._store_analytics_record({
                'id': f"{user_id}_{timestamp.isoformat()}",
                'user_id': user_id,
                'timestamp': timestamp.isoformat(),
                'model': model,
                'template': template,
                'tokens_used': tokens_used,
                'response_time': response_time,
                'cost': cost,
                'cache_hit': cache_hit,
                'error': error,
                'hour': int(hour_key),
                'date': timestamp.strftime('%Y-%m-%d')
            })
            
            # Send metrics to CloudWatch
            await self._send_cloudwatch_metrics(model, response_time, cost, error)
            
        except Exception as e:
            logger.error(f"Failed to track request: {str(e)}")
    
    async def _store_analytics_record(self, record: Dict):
        """Store analytics record in DynamoDB"""
        try:
            self.analytics_table.put_item(Item=record)
        except Exception as e:
            logger.error(f"Failed to store analytics record: {str(e)}")
    
    async def _send_cloudwatch_metrics(self, model: str, response_time: float, cost: float, error: bool):
        """Send custom metrics to CloudWatch"""
        try:
            metrics = [
                {
                    'MetricName': 'RequestCount',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'Model', 'Value': model}
                    ]
                },
                {
                    'MetricName': 'ResponseTime',
                    'Value': response_time,
                    'Unit': 'Seconds',
                    'Dimensions': [
                        {'Name': 'Model', 'Value': model}
                    ]
                },
                {
                    'MetricName': 'Cost',
                    'Value': cost,
                    'Unit': 'None',
                    'Dimensions': [
                        {'Name': 'Model', 'Value': model}
                    ]
                }
            ]
            
            if error:
                metrics.append({
                    'MetricName': 'ErrorCount',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'Model', 'Value': model}
                    ]
                })
            
            self.cloudwatch.put_metric_data(
                Namespace='PromptTune/Application',
                MetricData=metrics
            )
            
        except Exception as e:
            logger.error(f"Failed to send CloudWatch metrics: {str(e)}")
    
    async def get_analytics_data(self, time_range: str = '24h') -> Dict:
        """Get comprehensive analytics data"""
        
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            if time_range == '1h':
                start_time = end_time - timedelta(hours=1)
            elif time_range == '24h':
                start_time = end_time - timedelta(days=1)
            elif time_range == '7d':
                start_time = end_time - timedelta(days=7)
            elif time_range == '30d':
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=1)
            
            # Get data from DynamoDB
            historical_data = await self._get_historical_data(start_time, end_time)
            
            # Combine with real-time cache data
            analytics_data = {
                'totalRequests': len(historical_data) + self.metrics_cache['requests_today'],
                'totalUsers': len(set([r['user_id'] for r in historical_data] + list(self.metrics_cache['users_today']))),
                'averageResponseTime': self._calculate_average_response_time(historical_data),
                'cacheHitRate': self._calculate_cache_hit_rate(),
                'costToday': self.metrics_cache['total_cost_today'],
                'costThisMonth': await self._get_monthly_cost(),
                'topTemplates': self._get_top_templates(historical_data),
                'hourlyUsage': self._get_hourly_usage(historical_data),
                'modelUsage': self._get_model_usage(historical_data),
                'errorRate': self._calculate_error_rate(historical_data),
                'userSatisfaction': 4.7  # This would come from user feedback in a real system
            }
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Failed to get analytics data: {str(e)}")
            return self._get_default_analytics()
    
    async def _get_historical_data(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get historical data from DynamoDB"""
        try:
            # This is a simplified query - in production, you'd use GSI for efficient querying
            response = self.analytics_table.scan(
                FilterExpression='#ts BETWEEN :start AND :end',
                ExpressionAttributeNames={'#ts': 'timestamp'},
                ExpressionAttributeValues={
                    ':start': start_time.isoformat(),
                    ':end': end_time.isoformat()
                }
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Failed to get historical data: {str(e)}")
            return []
    
    def _calculate_average_response_time(self, historical_data: List[Dict]) -> float:
        """Calculate average response time"""
        all_times = [r.get('response_time', 0) for r in historical_data] + self.metrics_cache['response_times']
        return sum(all_times) / len(all_times) if all_times else 0.0
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_requests = self.metrics_cache['cache_hits'] + self.metrics_cache['cache_misses']
        if total_requests == 0:
            return 0.0
        return (self.metrics_cache['cache_hits'] / total_requests) * 100
    
    async def _get_monthly_cost(self) -> float:
        """Get total cost for current month"""
        try:
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_time = datetime.utcnow()
            
            monthly_data = await self._get_historical_data(start_of_month, end_time)
            monthly_cost = sum([r.get('cost', 0) for r in monthly_data])
            
            return monthly_cost + self.metrics_cache['total_cost_today']
        except Exception as e:
            logger.error(f"Failed to get monthly cost: {str(e)}")
            return 0.0
    
    def _get_top_templates(self, historical_data: List[Dict]) -> List[Dict]:
        """Get most popular templates"""
        template_counts = defaultdict(int)
        
        # Count from historical data
        for record in historical_data:
            template = record.get('template')
            if template:
                template_counts[template] += 1
        
        # Add current cache data
        for template, count in self.metrics_cache['template_usage'].items():
            template_counts[template] += count
        
        # Sort and return top 5
        sorted_templates = sorted(template_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return [{'name': name, 'usage': count} for name, count in sorted_templates]
    
    def _get_hourly_usage(self, historical_data: List[Dict]) -> List[Dict]:
        """Get hourly usage pattern"""
        hourly_counts = defaultdict(int)
        
        # Count from historical data
        for record in historical_data:
            hour = record.get('hour', 0)
            hourly_counts[hour] += 1
        
        # Add current cache data
        for hour_str, count in self.metrics_cache['hourly_usage'].items():
            hour = int(hour_str)
            hourly_counts[hour] += count
        
        # Create 24-hour array
        hourly_usage = []
        for hour in range(24):
            hourly_usage.append({
                'hour': f"{hour:02d}:00",
                'requests': hourly_counts[hour]
            })
        
        return hourly_usage
    
    def _get_model_usage(self, historical_data: List[Dict]) -> List[Dict]:
        """Get model usage and costs"""
        model_stats = defaultdict(lambda: {'requests': 0, 'cost': 0.0})
        
        # Count from historical data
        for record in historical_data:
            model = record.get('model', 'unknown')
            model_stats[model]['requests'] += 1
            model_stats[model]['cost'] += record.get('cost', 0)
        
        # Add current cache data
        for model, count in self.metrics_cache['model_usage'].items():
            model_stats[model]['requests'] += count
        
        # Convert to list format
        model_usage = []
        for model, stats in model_stats.items():
            model_usage.append({
                'model': model.title().replace('-', ' '),
                'requests': stats['requests'],
                'cost': stats['cost']
            })
        
        return sorted(model_usage, key=lambda x: x['requests'], reverse=True)
    
    def _calculate_error_rate(self, historical_data: List[Dict]) -> float:
        """Calculate error rate"""
        total_requests = len(historical_data) + self.metrics_cache['requests_today']
        total_errors = len([r for r in historical_data if r.get('error', False)]) + self.metrics_cache['error_count']
        
        if total_requests == 0:
            return 0.0
        
        return (total_errors / total_requests) * 100
    
    def _get_default_analytics(self) -> Dict:
        """Return default analytics data when real data is unavailable"""
        return {
            'totalRequests': 0,
            'totalUsers': 0,
            'averageResponseTime': 0.0,
            'cacheHitRate': 0.0,
            'costToday': 0.0,
            'costThisMonth': 0.0,
            'topTemplates': [],
            'hourlyUsage': [{'hour': f"{h:02d}:00", 'requests': 0} for h in range(24)],
            'modelUsage': [],
            'errorRate': 0.0,
            'userSatisfaction': 0.0
        }
    
    async def get_cost_breakdown(self) -> Dict:
        """Get detailed cost breakdown"""
        try:
            return {
                'lambda_cost': await self._get_lambda_cost(),
                'bedrock_cost': self.metrics_cache['total_cost_today'],
                'dynamodb_cost': await self._get_dynamodb_cost(),
                'cloudfront_cost': await self._get_cloudfront_cost(),
                's3_cost': await self._get_s3_cost(),
                'total_estimated': await self._get_total_estimated_cost()
            }
        except Exception as e:
            logger.error(f"Failed to get cost breakdown: {str(e)}")
            return {}
    
    async def _get_lambda_cost(self) -> float:
        """Estimate Lambda costs"""
        # Simplified calculation - in production, use AWS Cost Explorer API
        requests = self.metrics_cache['requests_today']
        avg_duration = sum(self.metrics_cache['response_times']) / len(self.metrics_cache['response_times']) if self.metrics_cache['response_times'] else 1.0
        
        # Lambda pricing: $0.0000166667 per GB-second
        memory_gb = 1.0  # 1GB memory allocation
        cost = requests * avg_duration * memory_gb * 0.0000166667
        
        return cost
    
    async def _get_dynamodb_cost(self) -> float:
        """Estimate DynamoDB costs"""
        # Simplified calculation
        requests = self.metrics_cache['requests_today']
        # $0.25 per million read/write requests
        return (requests * 2) * (0.25 / 1000000)  # 2 operations per request
    
    async def _get_cloudfront_cost(self) -> float:
        """Estimate CloudFront costs"""
        # Very simplified - would need actual data transfer metrics
        return 0.01  # Minimal cost for typical usage
    
    async def _get_s3_cost(self) -> float:
        """Estimate S3 costs"""
        # Very simplified - mostly storage cost
        return 0.02  # Minimal cost for static assets
    
    async def _get_total_estimated_cost(self) -> float:
        """Get total estimated daily cost"""
        lambda_cost = await self._get_lambda_cost()
        bedrock_cost = self.metrics_cache['total_cost_today']
        dynamodb_cost = await self._get_dynamodb_cost()
        cloudfront_cost = await self._get_cloudfront_cost()
        s3_cost = await self._get_s3_cost()
        
        return lambda_cost + bedrock_cost + dynamodb_cost + cloudfront_cost + s3_cost

# Global analytics manager instance
analytics_manager = AnalyticsManager()
