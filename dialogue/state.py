"""
Dialogue State Management System

Handles pending actions and user confirmations to prevent dialogue loops.
Implements a state machine for confirm → fulfill pattern.
"""

import time
from typing import Optional, Set, Literal
from dataclasses import dataclass


@dataclass
class DialogueState:
    """Represents the current state of dialogue interactions."""
    pending_action: Optional[str]
    expected: Set[Literal["yes", "no"]]
    expires_at: float
    context: Optional[dict] = None
    
    def __post_init__(self):
        if self.pending_action is None:
            self.expected = set()
            self.expires_at = 0.0
        if self.context is None:
            self.context = {}


class DialogueStateManager:
    """Manages dialogue state transitions and pending actions."""
    
    def __init__(self):
        self.state = DialogueState(None, set(), 0.0)
        self._logger = None  # Will be set by main application
    
    def set_logger(self, logger):
        """Set the logger for this manager."""
        self._logger = logger
    
    def set_pending(self, action: str, expected: Set[Literal["yes", "no"]] = {"yes", "no"}, ttl_s: float = 20.0, context: Optional[dict] = None) -> None:
        """
        Set a pending action that expects user confirmation.
        
        Args:
            action: The action identifier (e.g., "describe_chomp")
            expected: Set of expected responses ("yes", "no")
            ttl_s: Time to live in seconds
            context: Additional context for the action
        """
        self.state = DialogueState(
            pending_action=action,
            expected=expected,
            expires_at=time.time() + ttl_s,
            context=context or {}
        )
        
        if self._logger:
            self._logger(f"[DIALOG] pending={action} expected={expected} ttl={ttl_s}s context={context}")
    
    def consume_affirmation(self, user_text: str) -> Optional[str]:
        """
        Check if user text affirms the pending action.
        
        Args:
            user_text: User's input text
            
        Returns:
            The pending action if affirmed, None otherwise
        """
        # Check if we have a pending action and it hasn't expired
        if not self.state.pending_action or time.time() > self.state.expires_at:
            if self.state.pending_action and self._logger:
                self._logger(f"[DIALOG] pending={self.state.pending_action} expired")
            self._clear_state()
            return None
        
        # Normalize user input
        user_text_lower = user_text.lower().strip()
        
        # Check for affirmative responses
        affirmative_words = {"yes", "yeah", "sure", "okay", "ok", "yep", "yup", "absolutely", "definitely", "y", "yea", "uh-huh", "mm-hmm"}
        negative_words = {"no", "nope", "nah", "not", "don't", "dont", "never", "n", "nay"}
        
        is_affirmative = any(word in user_text_lower for word in affirmative_words)
        is_negative = any(word in user_text_lower for word in negative_words)
        
        # Determine response type
        if is_affirmative and "yes" in self.state.expected:
            pending_action = self.state.pending_action
            self._clear_state()
            if self._logger:
                self._logger(f"[DIALOG] pending={pending_action} → fulfilled")
            
            # Trigger head nodding behavior for affirmative responses
            self._trigger_head_nod()
            
            return pending_action
        elif is_negative and "no" in self.state.expected:
            if self._logger:
                self._logger(f"[DIALOG] pending={self.state.pending_action} → declined")
            self._clear_state()
            return None
        
        # No clear affirmation/negation
        return None
    
    def _trigger_head_nod(self):
        """Trigger head nodding behavior for affirmative responses."""
        try:
            # This will be called by the main system to trigger head nodding
            if self._logger:
                self._logger("[DIALOG] Triggering head nod for affirmative response")
        except Exception as e:
            if self._logger:
                self._logger(f"[DIALOG] Error triggering head nod: {e}")
    
    def get_pending_action(self) -> Optional[str]:
        """Get the current pending action if not expired."""
        if self.state.pending_action and time.time() <= self.state.expires_at:
            return self.state.pending_action
        return None
    
    def clear_pending(self) -> None:
        """Clear any pending action."""
        self._clear_state()
    
    def handle_device_context(self, user_text: str) -> Optional[str]:
        """
        Handle device-related context and indirect prompts.
        
        Args:
            user_text: User's input text
            
        Returns:
            The action to take if device context is detected, None otherwise
        """
        user_text_lower = user_text.lower().strip()
        
        # Check for device-related indirect prompts
        device_patterns = {
            "turn it on": "device_toggle_on",
            "turn it off": "device_toggle_off", 
            "turn on": "device_toggle_on",
            "turn off": "device_toggle_off",
            "switch it on": "device_toggle_on",
            "switch it off": "device_toggle_off",
            "power on": "device_toggle_on",
            "power off": "device_toggle_off",
            "turn on the": "device_toggle_on",
            "turn off the": "device_toggle_off"
        }
        
        # Check for device-related patterns
        for pattern, action in device_patterns.items():
            if pattern in user_text_lower:
                if self._logger:
                    self._logger(f"[DIALOG] Device context detected: {pattern} -> {action}")
                return action
        
        # Check for promise/acknowledgment patterns
        promise_patterns = [
            "sure, let me",
            "okay, let me", 
            "alright, let me",
            "i'll",
            "i will",
            "let me"
        ]
        
        for pattern in promise_patterns:
            if pattern in user_text_lower:
                # Check if there's a pending action with device context
                if self.state.pending_action and self.state.context:
                    device_action = self.state.context.get("device_action")
                    if device_action:
                        if self._logger:
                            self._logger(f"[DIALOG] Promise detected with device context: {device_action}")
                        return device_action
        
        return None
    
    def _clear_state(self) -> None:
        """Clear the current state."""
        self.state = DialogueState(None, set(), 0.0, {})


# Global instance for easy access
dialogue_state_manager = DialogueStateManager()


def set_pending(action: str, expected: Set[Literal["yes", "no"]] = {"yes", "no"}, ttl_s: float = 20.0) -> None:
    """Convenience function to set a pending action."""
    dialogue_state_manager.set_pending(action, expected, ttl_s)


def consume_affirmation(user_text: str) -> Optional[str]:
    """Convenience function to consume user affirmation."""
    return dialogue_state_manager.consume_affirmation(user_text)


def get_pending_action() -> Optional[str]:
    """Convenience function to get current pending action."""
    return dialogue_state_manager.get_pending_action()


def clear_pending() -> None:
    """Convenience function to clear pending action."""
    dialogue_state_manager.clear_pending()


def handle_device_context(user_text: str) -> Optional[str]:
    """Convenience function to handle device context."""
    return dialogue_state_manager.handle_device_context(user_text)
