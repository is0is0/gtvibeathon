"""Error recovery and fallback mechanisms for the Voxel system."""

import logging
import time
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """Types of errors that can occur."""
    AGENT_FAILURE = "agent_failure"
    SCRIPT_EXECUTION = "script_execution"
    CONTEXT_UPDATE = "context_update"
    BLENDER_ERROR = "blender_error"
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    CONFIG_ERROR = "config_error"


class RecoveryStrategy(str, Enum):
    """Recovery strategies for different error types."""
    RETRY = "retry"
    FALLBACK = "fallback"
    SIMPLIFY = "simplify"
    SKIP = "skip"
    ABORT = "abort"


@dataclass
class ErrorContext:
    """Context information about an error."""
    error_type: ErrorType
    error_message: str
    agent_role: Optional[str] = None
    script_content: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class RecoveryAction:
    """A recovery action to take."""
    strategy: RecoveryStrategy
    description: str
    action: Callable
    success_criteria: Optional[Callable] = None


class ErrorRecoverySystem:
    """Comprehensive error recovery system for the Voxel system."""
    
    def __init__(self):
        self.error_history: List[ErrorContext] = []
        self.recovery_strategies: Dict[ErrorType, List[RecoveryAction]] = {}
        self.fallback_agents: Dict[str, str] = {}
        self.simplified_prompts: Dict[str, str] = {}
        self._setup_default_strategies()
    
    def _setup_default_strategies(self) -> None:
        """Set up default recovery strategies for each error type."""
        
        # Agent failure strategies
        self.recovery_strategies[ErrorType.AGENT_FAILURE] = [
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                description="Retry agent with exponential backoff",
                action=self._retry_agent_with_backoff
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK,
                description="Use fallback agent",
                action=self._use_fallback_agent
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.SIMPLIFY,
                description="Simplify prompt and retry",
                action=self._simplify_prompt_and_retry
            )
        ]
        
        # Script execution strategies
        self.recovery_strategies[ErrorType.SCRIPT_EXECUTION] = [
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                description="Retry script execution",
                action=self._retry_script_execution
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.SIMPLIFY,
                description="Use simplified script",
                action=self._use_simplified_script
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.SKIP,
                description="Skip problematic script",
                action=self._skip_problematic_script
            )
        ]
        
        # Context update strategies
        self.recovery_strategies[ErrorType.CONTEXT_UPDATE] = [
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                description="Retry context update",
                action=self._retry_context_update
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.SKIP,
                description="Skip context update",
                action=self._skip_context_update
            )
        ]
        
        # Blender error strategies
        self.recovery_strategies[ErrorType.BLENDER_ERROR] = [
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                description="Retry Blender operation",
                action=self._retry_blender_operation
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK,
                description="Use fallback Blender settings",
                action=self._use_fallback_blender_settings
            )
        ]
        
        # API error strategies
        self.recovery_strategies[ErrorType.API_ERROR] = [
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                description="Retry API call with backoff",
                action=self._retry_api_call_with_backoff
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK,
                description="Use cached response",
                action=self._use_cached_response
            )
        ]
    
    def handle_error(self, error_context: ErrorContext) -> Tuple[bool, Any]:
        """
        Handle an error using appropriate recovery strategies.
        
        Args:
            error_context: Context about the error
            
        Returns:
            Tuple of (success, result)
        """
        logger.error(f"Handling error: {error_context.error_type} - {error_context.error_message}")
        
        # Add to error history
        self.error_history.append(error_context)
        
        # Get recovery strategies for this error type
        strategies = self.recovery_strategies.get(error_context.error_type, [])
        
        if not strategies:
            logger.warning(f"No recovery strategies for error type: {error_context.error_type}")
            return False, None
        
        # Try each strategy in order
        for strategy in strategies:
            try:
                logger.info(f"Trying recovery strategy: {strategy.description}")
                result = strategy.action(error_context)
                
                # Check if the result meets success criteria
                if strategy.success_criteria and not strategy.success_criteria(result):
                    logger.warning(f"Recovery strategy failed success criteria: {strategy.description}")
                    continue
                
                logger.info(f"Recovery successful: {strategy.description}")
                return True, result
                
            except Exception as e:
                logger.error(f"Recovery strategy failed: {strategy.description} - {e}")
                continue
        
        logger.error(f"All recovery strategies failed for error: {error_context.error_type}")
        return False, None
    
    def _retry_agent_with_backoff(self, error_context: ErrorContext) -> Any:
        """Retry agent with exponential backoff."""
        if error_context.retry_count >= error_context.max_retries:
            raise Exception("Max retries exceeded")
        
        # Exponential backoff: 1s, 2s, 4s, 8s...
        delay = 2 ** error_context.retry_count
        logger.info(f"Retrying agent in {delay} seconds (attempt {error_context.retry_count + 1})")
        time.sleep(delay)
        
        # Update retry count
        error_context.retry_count += 1
        
        # Return a flag indicating retry should be attempted
        return {"retry": True, "delay": delay}
    
    def _use_fallback_agent(self, error_context: ErrorContext) -> Any:
        """Use a fallback agent when the primary agent fails."""
        fallback_agent = self.fallback_agents.get(error_context.agent_role)
        if not fallback_agent:
            raise Exception(f"No fallback agent for {error_context.agent_role}")
        
        logger.info(f"Using fallback agent: {fallback_agent}")
        return {"fallback_agent": fallback_agent}
    
    def _simplify_prompt_and_retry(self, error_context: ErrorContext) -> Any:
        """Simplify the prompt and retry."""
        original_prompt = error_context.script_content or "complex scene"
        simplified_prompt = self._simplify_prompt(original_prompt)
        
        logger.info(f"Simplified prompt: '{original_prompt}' -> '{simplified_prompt}'")
        return {"simplified_prompt": simplified_prompt}
    
    def _retry_script_execution(self, error_context: ErrorContext) -> Any:
        """Retry script execution with error handling."""
        if error_context.retry_count >= error_context.max_retries:
            raise Exception("Max retries exceeded")
        
        logger.info("Retrying script execution")
        error_context.retry_count += 1
        return {"retry_script": True}
    
    def _use_simplified_script(self, error_context: ErrorContext) -> Any:
        """Use a simplified version of the script."""
        if not error_context.script_content:
            raise Exception("No script content to simplify")
        
        simplified_script = self._simplify_script(error_context.script_content)
        logger.info("Using simplified script")
        return {"simplified_script": simplified_script}
    
    def _skip_problematic_script(self, error_context: ErrorContext) -> Any:
        """Skip the problematic script and continue."""
        logger.info("Skipping problematic script")
        return {"skip_script": True}
    
    def _retry_context_update(self, error_context: ErrorContext) -> Any:
        """Retry context update operation."""
        logger.info("Retrying context update")
        return {"retry_context": True}
    
    def _skip_context_update(self, error_context: ErrorContext) -> Any:
        """Skip context update and continue."""
        logger.info("Skipping context update")
        return {"skip_context": True}
    
    def _retry_blender_operation(self, error_context: ErrorContext) -> Any:
        """Retry Blender operation."""
        logger.info("Retrying Blender operation")
        return {"retry_blender": True}
    
    def _use_fallback_blender_settings(self, error_context: ErrorContext) -> Any:
        """Use fallback Blender settings."""
        fallback_settings = {
            "render_engine": "EEVEE",  # Faster than Cycles
            "samples": 32,  # Lower quality but faster
            "resolution": (1280, 720)  # Lower resolution
        }
        logger.info("Using fallback Blender settings")
        return {"fallback_settings": fallback_settings}
    
    def _retry_api_call_with_backoff(self, error_context: ErrorContext) -> Any:
        """Retry API call with exponential backoff."""
        if error_context.retry_count >= error_context.max_retries:
            raise Exception("Max retries exceeded")
        
        delay = 2 ** error_context.retry_count
        logger.info(f"Retrying API call in {delay} seconds")
        time.sleep(delay)
        error_context.retry_count += 1
        return {"retry_api": True, "delay": delay}
    
    def _use_cached_response(self, error_context: ErrorContext) -> Any:
        """Use cached response when API fails."""
        logger.info("Using cached response")
        return {"use_cache": True}
    
    def _simplify_prompt(self, prompt: str) -> str:
        """Simplify a complex prompt."""
        # Remove complex modifiers
        simplified = prompt.lower()
        
        # Remove complex descriptors
        complex_words = [
            "detailed", "complex", "intricate", "sophisticated", 
            "advanced", "professional", "cinematic", "dramatic"
        ]
        
        for word in complex_words:
            simplified = simplified.replace(word, "")
        
        # Keep only essential elements
        words = simplified.split()
        if len(words) > 5:
            # Keep first 5 words
            simplified = " ".join(words[:5])
        
        return simplified.strip()
    
    def _simplify_script(self, script: str) -> str:
        """Simplify a Blender script."""
        lines = script.split('\n')
        simplified_lines = []
        
        # Keep only essential operations
        essential_ops = [
            'bpy.ops.mesh.primitive_',
            'bpy.ops.object.',
            'bpy.ops.material.',
            'bpy.ops.light.',
            'bpy.ops.camera.'
        ]
        
        for line in lines:
            if any(op in line for op in essential_ops):
                simplified_lines.append(line)
            elif line.strip().startswith('#') or line.strip() == '':
                simplified_lines.append(line)
        
        return '\n'.join(simplified_lines)
    
    def set_fallback_agent(self, primary_agent: str, fallback_agent: str) -> None:
        """Set a fallback agent for a primary agent."""
        self.fallback_agents[primary_agent] = fallback_agent
        logger.info(f"Set fallback agent: {primary_agent} -> {fallback_agent}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get statistics about errors and recovery attempts."""
        if not self.error_history:
            return {"total_errors": 0}
        
        error_counts = {}
        recovery_success = 0
        
        for error in self.error_history:
            error_type = error.error_type.value
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            if error.retry_count > 0:
                recovery_success += 1
        
        return {
            "total_errors": len(self.error_history),
            "error_types": error_counts,
            "recovery_attempts": recovery_success,
            "recovery_rate": recovery_success / len(self.error_history) if self.error_history else 0
        }
    
    def clear_error_history(self) -> None:
        """Clear the error history."""
        self.error_history.clear()
        logger.info("Error history cleared")
    
    def get_recent_errors(self, limit: int = 10) -> List[ErrorContext]:
        """Get recent errors."""
        return self.error_history[-limit:] if self.error_history else []
