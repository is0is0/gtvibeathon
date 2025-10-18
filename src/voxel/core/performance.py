"""Performance optimization system with caching and parallel processing."""

import asyncio
import hashlib
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """A cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if the cache entry is still valid."""
        return not self.is_expired()


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring."""
    cache_hits: int = 0
    cache_misses: int = 0
    parallel_tasks: int = 0
    total_execution_time: float = 0.0
    average_response_time: float = 0.0
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


class PerformanceCache:
    """High-performance caching system for the Voxel system."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.metrics = PerformanceMetrics()
        self._lock = asyncio.Lock()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        # Create a deterministic string representation
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                
                if entry.is_valid():
                    # Update access statistics
                    entry.access_count += 1
                    entry.last_accessed = datetime.now()
                    self.metrics.cache_hits += 1
                    logger.debug(f"Cache hit for key: {key}")
                    return entry.value
                else:
                    # Remove expired entry
                    del self.cache[key]
                    logger.debug(f"Cache entry expired for key: {key}")
            
            self.metrics.cache_misses += 1
            logger.debug(f"Cache miss for key: {key}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache."""
        async with self._lock:
            # Remove oldest entries if cache is full
            if len(self.cache) >= self.max_size:
                await self._evict_oldest()
            
            ttl = ttl or self.default_ttl
            expires_at = datetime.now() + timedelta(seconds=ttl)
            
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                expires_at=expires_at
            )
            
            self.cache[key] = entry
            logger.debug(f"Cached value for key: {key}")
    
    async def _evict_oldest(self) -> None:
        """Evict the oldest cache entry."""
        if not self.cache:
            return
        
        # Find the least recently accessed entry
        oldest_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed or self.cache[k].created_at
        )
        
        del self.cache[oldest_key]
        logger.debug(f"Evicted cache entry: {oldest_key}")
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get performance metrics."""
        return self.metrics
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": self.metrics.hit_rate(),
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses
        }


class ParallelProcessor:
    """Parallel processing system for agent operations."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize the parallel processor.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.metrics = PerformanceMetrics()
    
    def execute_parallel(self, tasks: List[Tuple[Callable, tuple, dict]]) -> List[Any]:
        """
        Execute multiple tasks in parallel.
        
        Args:
            tasks: List of (function, args, kwargs) tuples
            
        Returns:
            List of results in the same order as tasks
        """
        start_time = time.time()
        
        # Submit all tasks
        future_to_index = {}
        for i, (func, args, kwargs) in enumerate(tasks):
            future = self.executor.submit(func, *args, **kwargs)
            future_to_index[future] = i
        
        # Collect results in order
        results = [None] * len(tasks)
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                results[index] = future.result()
            except Exception as e:
                logger.error(f"Task {index} failed: {e}")
                results[index] = None
        
        # Update metrics
        execution_time = time.time() - start_time
        self.metrics.parallel_tasks += len(tasks)
        self.metrics.total_execution_time += execution_time
        self.metrics.average_response_time = (
            self.metrics.total_execution_time / self.metrics.parallel_tasks
        )
        
        logger.info(f"Executed {len(tasks)} tasks in parallel in {execution_time:.2f}s")
        return results
    
    async def execute_async(self, tasks: List[Tuple[Callable, tuple, dict]]) -> List[Any]:
        """
        Execute multiple tasks asynchronously.
        
        Args:
            tasks: List of (function, args, kwargs) tuples
            
        Returns:
            List of results in the same order as tasks
        """
        start_time = time.time()
        
        # Create async tasks
        async_tasks = []
        for func, args, kwargs in tasks:
            # Run sync function in thread pool
            task = asyncio.get_event_loop().run_in_executor(
                self.executor, func, *args, **kwargs
            )
            async_tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # Update metrics
        execution_time = time.time() - start_time
        self.metrics.parallel_tasks += len(tasks)
        self.metrics.total_execution_time += execution_time
        self.metrics.average_response_time = (
            self.metrics.total_execution_time / self.metrics.parallel_tasks
        )
        
        logger.info(f"Executed {len(tasks)} tasks asynchronously in {execution_time:.2f}s")
        return results
    
    def shutdown(self) -> None:
        """Shutdown the thread pool executor."""
        self.executor.shutdown(wait=True)
        logger.info("Parallel processor shutdown")


class PerformanceOptimizer:
    """Main performance optimization system."""
    
    def __init__(self, cache_size: int = 1000, max_workers: int = 4):
        """
        Initialize the performance optimizer.
        
        Args:
            cache_size: Maximum cache size
            max_workers: Maximum number of parallel workers
        """
        self.cache = PerformanceCache(max_size=cache_size)
        self.parallel_processor = ParallelProcessor(max_workers=max_workers)
        self.script_cache: Dict[str, str] = {}
        self.pattern_cache: Dict[str, List[Any]] = {}
    
    async def cached_agent_call(self, agent, method: str, *args, **kwargs) -> Any:
        """Execute an agent method with caching."""
        # Generate cache key
        cache_key = self.cache._generate_key(
            agent.__class__.__name__,
            method,
            *args,
            **kwargs
        )
        
        # Try to get from cache
        result = await self.cache.get(cache_key)
        if result is not None:
            logger.debug(f"Cache hit for {agent.__class__.__name__}.{method}")
            return result
        
        # Execute method
        if hasattr(agent, method):
            func = getattr(agent, method)
            result = func(*args, **kwargs)
            
            # Cache the result
            await self.cache.set(cache_key, result)
            logger.debug(f"Cached result for {agent.__class__.__name__}.{method}")
            
            return result
        else:
            raise AttributeError(f"Agent {agent.__class__.__name__} has no method {method}")
    
    def cache_script(self, prompt: str, script: str) -> None:
        """Cache a generated script."""
        script_hash = hashlib.md5(prompt.encode()).hexdigest()
        self.script_cache[script_hash] = script
        logger.debug(f"Cached script for prompt: {prompt[:50]}...")
    
    def get_cached_script(self, prompt: str) -> Optional[str]:
        """Get a cached script."""
        script_hash = hashlib.md5(prompt.encode()).hexdigest()
        return self.script_cache.get(script_hash)
    
    def cache_patterns(self, context_type: str, patterns: List[Any]) -> None:
        """Cache patterns for a context type."""
        self.pattern_cache[context_type] = patterns
        logger.debug(f"Cached {len(patterns)} patterns for {context_type}")
    
    def get_cached_patterns(self, context_type: str) -> Optional[List[Any]]:
        """Get cached patterns for a context type."""
        return self.pattern_cache.get(context_type)
    
    def execute_agents_parallel(self, agents: List[Any], method: str, *args, **kwargs) -> List[Any]:
        """Execute the same method on multiple agents in parallel."""
        tasks = [(getattr(agent, method), args, kwargs) for agent in agents]
        return self.parallel_processor.execute_parallel(tasks)
    
    async def execute_agents_async(self, agents: List[Any], method: str, *args, **kwargs) -> List[Any]:
        """Execute the same method on multiple agents asynchronously."""
        tasks = [(getattr(agent, method), args, kwargs) for agent in agents]
        return await self.parallel_processor.execute_async(tasks)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        cache_stats = self.cache.get_cache_stats()
        metrics = self.cache.get_metrics()
        
        return {
            "cache": cache_stats,
            "parallel_processing": {
                "total_tasks": self.parallel_processor.metrics.parallel_tasks,
                "total_execution_time": self.parallel_processor.metrics.total_execution_time,
                "average_response_time": self.parallel_processor.metrics.average_response_time
            },
            "script_cache": {
                "size": len(self.script_cache),
                "keys": list(self.script_cache.keys())[:5]  # Show first 5 keys
            },
            "pattern_cache": {
                "size": len(self.pattern_cache),
                "context_types": list(self.pattern_cache.keys())
            }
        }
    
    def clear_all_caches(self) -> None:
        """Clear all caches."""
        asyncio.create_task(self.cache.clear())
        self.script_cache.clear()
        self.pattern_cache.clear()
        logger.info("All caches cleared")
    
    def shutdown(self) -> None:
        """Shutdown the performance optimizer."""
        self.parallel_processor.shutdown()
        logger.info("Performance optimizer shutdown")
