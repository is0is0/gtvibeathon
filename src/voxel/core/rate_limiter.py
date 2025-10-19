"""Rate limiter for managing API token usage and preventing rate limit errors."""

import time
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TokenRateLimiter:
    """Rate limiter that tracks token usage and enforces delays between API calls."""
    
    def __init__(self, tokens_per_minute_limit: int = 4000):
        """
        Initialize the rate limiter.
        
        Args:
            tokens_per_minute_limit: Maximum tokens allowed per minute
        """
        self.tokens_per_minute_limit = tokens_per_minute_limit
        self.token_usage: Dict[str, int] = {}  # minute_timestamp -> tokens_used
        self.last_call_times: Dict[str, datetime] = {}  # agent_name -> last_call_time
        self.min_delay_seconds = 60  # Minimum delay between agent calls
        
    def can_make_request(self, agent_name: str, estimated_tokens: int = 4000) -> bool:
        """
        Check if a request can be made without exceeding rate limits.
        
        Args:
            agent_name: Name of the agent making the request
            estimated_tokens: Estimated tokens this request will use
            
        Returns:
            True if request can be made, False if should wait
        """
        current_minute = self._get_current_minute()
        
        # Check if this minute's usage would exceed limit
        current_usage = self.token_usage.get(current_minute, 0)
        if current_usage + estimated_tokens > self.tokens_per_minute_limit:
            logger.info(f"Rate limit would be exceeded. Current: {current_usage}, Request: {estimated_tokens}, Limit: {self.tokens_per_minute_limit}")
            return False
            
        # Check minimum delay between agent calls
        last_call = self.last_call_times.get(agent_name)
        if last_call:
            time_since_last = datetime.now() - last_call
            if time_since_last.total_seconds() < self.min_delay_seconds:
                remaining_delay = self.min_delay_seconds - time_since_last.total_seconds()
                logger.info(f"Agent {agent_name} needs to wait {remaining_delay:.1f} more seconds")
                return False
                
        return True
    
    def record_request(self, agent_name: str, actual_tokens: int) -> None:
        """
        Record a completed request and its token usage.
        
        Args:
            agent_name: Name of the agent that made the request
            actual_tokens: Actual tokens used in the request
        """
        current_minute = self._get_current_minute()
        
        # Update token usage for this minute
        if current_minute not in self.token_usage:
            self.token_usage[current_minute] = 0
        self.token_usage[current_minute] += actual_tokens
        
        # Update last call time
        self.last_call_times[agent_name] = datetime.now()
        
        # Clean up old usage data (keep only last 2 minutes)
        self._cleanup_old_usage()
        
        logger.info(f"Recorded {actual_tokens} tokens for {agent_name}. Current minute usage: {self.token_usage[current_minute]}")
    
    def get_wait_time(self, agent_name: str, estimated_tokens: int = 4000) -> float:
        """
        Get the time to wait before making a request.
        
        Args:
            agent_name: Name of the agent making the request
            estimated_tokens: Estimated tokens this request will use
            
        Returns:
            Seconds to wait before making the request
        """
        wait_times = []
        
        # Check rate limit wait time
        current_minute = self._get_current_minute()
        current_usage = self.token_usage.get(current_minute, 0)
        
        if current_usage + estimated_tokens > self.tokens_per_minute_limit:
            # Wait until next minute
            now = datetime.now()
            next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
            rate_limit_wait = (next_minute - now).total_seconds()
            wait_times.append(rate_limit_wait)
            logger.info(f"Rate limit wait: {rate_limit_wait:.1f} seconds")
        
        # Check minimum delay wait time
        last_call = self.last_call_times.get(agent_name)
        if last_call:
            time_since_last = datetime.now() - last_call
            if time_since_last.total_seconds() < self.min_delay_seconds:
                delay_wait = self.min_delay_seconds - time_since_last.total_seconds()
                wait_times.append(delay_wait)
                logger.info(f"Agent delay wait: {delay_wait:.1f} seconds")
        
        return max(wait_times) if wait_times else 0.0
    
    def _get_current_minute(self) -> str:
        """Get current minute timestamp as string."""
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M")
    
    def _cleanup_old_usage(self) -> None:
        """Remove token usage data older than 2 minutes."""
        current_minute = self._get_current_minute()
        current_time = datetime.strptime(current_minute, "%Y-%m-%d %H:%M")
        
        # Remove entries older than 2 minutes
        to_remove = []
        for minute_str in self.token_usage.keys():
            minute_time = datetime.strptime(minute_str, "%Y-%m-%d %H:%M")
            if (current_time - minute_time).total_seconds() > 120:  # 2 minutes
                to_remove.append(minute_str)
        
        for minute_str in to_remove:
            del self.token_usage[minute_str]
    
    def get_status(self) -> Dict[str, any]:
        """Get current rate limiter status."""
        current_minute = self._get_current_minute()
        current_usage = self.token_usage.get(current_minute, 0)
        
        return {
            "current_minute": current_minute,
            "tokens_used_this_minute": current_usage,
            "tokens_remaining_this_minute": self.tokens_per_minute_limit - current_usage,
            "tokens_per_minute_limit": self.tokens_per_minute_limit,
            "active_agents": list(self.last_call_times.keys()),
            "usage_history": dict(self.token_usage)
        }


# Global rate limiter instance
_rate_limiter: Optional[TokenRateLimiter] = None


def get_rate_limiter() -> TokenRateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = TokenRateLimiter()
    return _rate_limiter


def initialize_rate_limiter(tokens_per_minute_limit: int = 4000) -> None:
    """Initialize the global rate limiter."""
    global _rate_limiter
    _rate_limiter = TokenRateLimiter(tokens_per_minute_limit)
    logger.info(f"Initialized rate limiter with {tokens_per_minute_limit} tokens per minute limit")
