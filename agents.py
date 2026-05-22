import time
import random
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock timeout exception
class AgentTimeoutError(Exception):
    pass

def with_retry_and_timeout(max_retries: int = 3, timeout: int = 2):
    """
    Decorator to implement retry and timeout logic for agent boundaries.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    start_time = time.time()
                    # Simulate intermittent failure and latency
                    if random.random() < 0.2:
                        time.sleep(timeout + 1) # Force timeout
                    
                    if time.time() - start_time > timeout:
                        raise AgentTimeoutError("Agent execution timed out")
                    
                    return func(*args, **kwargs)
                except AgentTimeoutError as e:
                    logger.warning(f"{func.__name__} timed out. Retry {retries + 1}/{max_retries}")
                    retries += 1
                except Exception as e:
                    logger.error(f"{func.__name__} failed with error: {e}")
                    retries += 1
            return {"response": f"System experiencing high load. {func.__name__} failed after {max_retries} retries.", "status": "error"}
        return wrapper
    return decorator

@with_retry_and_timeout()
def scheduling_agent(query: str, context: str) -> Dict[str, Any]:
    """Handles calendar and scheduling requests."""
    return {
        "response": f"Scheduling request processed. I have updated your calendar.",
        "status": "success",
        "agent": "Scheduling"
    }

@with_retry_and_timeout()
def leave_agent(query: str, context: str) -> Dict[str, Any]:
    """Handles time-off and leave policies."""
    return {
        "response": f"Leave request processed based on company policy.",
        "status": "success",
        "agent": "Leave"
    }

@with_retry_and_timeout()
def compliance_agent(query: str, context: str) -> Dict[str, Any]:
    """Handles HR compliance and policy queries."""
    return {
        "response": f"Compliance query answered according to HR guidelines.",
        "status": "success",
        "agent": "Compliance"
    }

@with_retry_and_timeout()
def clarification_agent(query: str, context: str) -> Dict[str, Any]:
    """Asks for more details when intent is ambiguous."""
    return {
        "response": f"Could you please provide more details? I am not sure exactly what you need.",
        "status": "success",
        "agent": "Clarification"
    }

def fallback_agent(query: str, context: str) -> Dict[str, Any]:
    """Fallback handling for uncertain requests to ensure graceful failure."""
    return {
        "response": "I'm sorry, I encountered an unexpected issue while processing your request. Please try again later or contact HR support.",
        "status": "fallback",
        "agent": "Fallback"
    }
