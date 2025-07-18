"""
Performance monitoring and circuit breaker utilities.
"""
import time
import psutil
import logging
from functools import wraps
from typing import Callable, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """Simple circuit breaker to prevent cascading failures."""
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Reset failure count on successful call."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Increment failure count and potentially open circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

def monitor_performance(func: Callable) -> Callable:
    """Decorator to monitor function performance and resource usage."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu_percent = process.cpu_percent()
        
        try:
            result = func(*args, **kwargs)
            
            # Log performance metrics
            end_time = time.time()
            duration = end_time - start_time
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = final_memory - initial_memory
            final_cpu_percent = process.cpu_percent()
            
            logger.info(f"{func.__name__} performance:")
            logger.info(f"  Duration: {duration:.2f}s")
            logger.info(f"  Memory change: {memory_used:+.1f} MB")
            logger.info(f"  CPU usage: {final_cpu_percent:.1f}%")
            
            # Warn on high resource usage
            if duration > 30:  # 30 second threshold
                logger.warning(f"{func.__name__} took {duration:.2f}s - consider optimization")
            if memory_used > 100:  # 100MB threshold
                logger.warning(f"{func.__name__} used {memory_used:.1f}MB - high memory usage")
            
            return result
            
        except Exception as e:
            logger.error(f"{func.__name__} failed after {time.time() - start_time:.2f}s: {e}")
            raise
    
    return wrapper

def check_system_resources() -> dict:
    """Check current system resource usage."""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "memory_available_mb": memory.available / 1024 / 1024,
        "disk_percent": disk.percent,
        "timestamp": datetime.now().isoformat()
    }

def is_system_under_load() -> bool:
    """Check if system is under high load."""
    resources = check_system_resources()
    
    # Define thresholds
    HIGH_CPU_THRESHOLD = 80  # 80% CPU
    HIGH_MEMORY_THRESHOLD = 85  # 85% Memory
    
    return (
        resources["cpu_percent"] > HIGH_CPU_THRESHOLD or 
        resources["memory_percent"] > HIGH_MEMORY_THRESHOLD
    )

# Global circuit breakers for critical operations
sync_circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=300)  # 5 min
api_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)   # 1 min