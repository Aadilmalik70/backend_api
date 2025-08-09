"""
Middleware package for SERP Strategist

Contains middleware components for request processing, authentication,
usage tracking, and other cross-cutting concerns.
"""

from .usage_tracker import (
    UsageTracker, UsageMiddleware, track_blueprint_generation, track_api_call,
    get_user_usage_info, set_resource_id, set_generated_blueprint_id,
    check_can_generate_blueprint, record_blueprint_generation, get_user_subscription_info
)

__all__ = [
    'UsageTracker', 'UsageMiddleware', 'track_blueprint_generation', 'track_api_call',
    'get_user_usage_info', 'set_resource_id', 'set_generated_blueprint_id',
    'check_can_generate_blueprint', 'record_blueprint_generation', 'get_user_subscription_info'
]