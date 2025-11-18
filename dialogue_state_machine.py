#!/usr/bin/env python3
"""
Dialogue State Machine System

Implements a dialogue state store with pending_action and expected_answer
to manage conversational flow using the confirm → fulfill pattern.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum

class DialogueIntent(Enum):
    """Dialogue intents for state management."""
    CONFIRM = "confirm"
    AFFIRM = "affirm"
    REQUEST_INFO = "request_info"
    PROVIDE_INFO = "provide_info"
    TELL_JOKE = "tell_joke"
    RECALL_MEMORY = "recall_memory"
    IMAGINE_SCENE = "imagine_scene"

@dataclass
class DialogueState:
    """Represents the current dialogue state."""
    pending_action: Optional[str] = None
    expected_answer: Optional[str] = None
    context: Dict[str, Any] = None
    created_at: str = None
    last_updated: str = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()

@dataclass
class DialogueAction:
    """Represents a dialogue action with its handler."""
    name: str
    description: str
    handler: Callable
    requires_confirmation: bool = False
    confirmation_question: Optional[str] = None
    expected_responses: List[str] = None
    
    def __post_init__(self):
        if self.expected_responses is None:
            self.expected_responses = ["yes", "no", "y", "n"]

class DialogueStateMachine:
    """
    Dialogue state machine implementing confirm → fulfill pattern.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_state = DialogueState()
        self.registered_actions: Dict[str, DialogueAction] = {}
        self.state_history: List[DialogueState] = []
        self.max_history = 50
        
        self._register_default_actions()
    
    def _register_default_actions(self):
        """Register default dialogue actions."""
        self.register_action(
            name="describe_chomp",
            description="Describe Chomp the dinosaur toy",
            handler=self._describe_chomp_handler,
            requires_confirmation=True,
            confirmation_question="Would you like me to tell you more about Chomp?"
        )
        
        self.register_action(
            name="tell_joke",
            description="Tell a joke",
            handler=self._tell_joke_handler,
            requires_confirmation=True,
            confirmation_question="Would you like me to tell you a joke?"
        )
        
        self.register_action(
            name="recall_memory",
            description="Recall a specific memory",
            handler=self._recall_memory_handler,
            requires_confirmation=True,
            confirmation_question="Would you like me to recall that memory?"
        )
        
        self.register_action(
            name="imagine_scene",
            description="Imagine a scene",
            handler=self._imagine_scene_handler,
            requires_confirmation=True,
            confirmation_question="Would you like me to imagine that scene?"
        )
    
    def register_action(self, name: str, description: str, handler: Callable,
                       requires_confirmation: bool = False,
                       confirmation_question: Optional[str] = None,
                       expected_responses: Optional[List[str]] = None):
        """Register a new dialogue action."""
        action = DialogueAction(
            name=name,
            description=description,
            handler=handler,
            requires_confirmation=requires_confirmation,
            confirmation_question=confirmation_question,
            expected_responses=expected_responses
        )
        self.registered_actions[name] = action
        self.logger.info(f"Registered dialogue action: {name}")
    
    def process_input(self, user_input: str, intent: Optional[DialogueIntent] = None) -> Dict[str, Any]:
        """
        Process user input and return appropriate response.
        
        Returns:
            Dict with keys: response, action_taken, new_state
        """
        user_input_lower = user_input.lower().strip()
        
        # Save current state to history
        self._save_state_to_history()
        
        # Check if we're waiting for a confirmation
        if self.current_state.pending_action and self.current_state.expected_answer:
            return self._handle_confirmation(user_input_lower)
        
        # Check if user is requesting an action
        if intent == DialogueIntent.REQUEST_INFO or "tell me" in user_input_lower or "describe" in user_input_lower:
            return self._handle_action_request(user_input_lower)
        
        # Check if user is providing information
        if intent == DialogueIntent.PROVIDE_INFO:
            return self._handle_info_provision(user_input_lower)
        
        # Default response
        return {
            "response": "I understand. How can I help you?",
            "action_taken": None,
            "new_state": self.current_state
        }
    
    def _handle_confirmation(self, user_input: str) -> Dict[str, Any]:
        """Handle confirmation responses."""
        action_name = self.current_state.pending_action
        expected_answer = self.current_state.expected_answer
        
        if action_name not in self.registered_actions:
            self._clear_state()
            return {
                "response": "I'm sorry, I don't recognize that action.",
                "action_taken": None,
                "new_state": self.current_state
            }
        
        action = self.registered_actions[action_name]
        
        # Check if response matches expected answer
        if user_input in action.expected_responses:
            if user_input in ["yes", "y"]:
                # Execute the action
                try:
                    result = action.handler(self.current_state.context)
                    self._clear_state()
                    return {
                        "response": result,
                        "action_taken": action_name,
                        "new_state": self.current_state
                    }
                except Exception as e:
                    self.logger.error(f"Error executing action {action_name}: {e}")
                    self._clear_state()
                    return {
                        "response": f"I'm sorry, I encountered an error while {action.description.lower()}.",
                        "action_taken": None,
                        "new_state": self.current_state
                    }
            else:
                # User declined
                self._clear_state()
                return {
                    "response": "Alright, no problem.",
                    "action_taken": None,
                    "new_state": self.current_state
                }
        else:
            # Invalid response, ask for clarification
            return {
                "response": f"Please respond with 'yes' or 'no' to confirm if you'd like me to {action.description.lower()}.",
                "action_taken": None,
                "new_state": self.current_state
            }
    
    def _handle_action_request(self, user_input: str) -> Dict[str, Any]:
        """Handle action requests from user."""
        # Try to match user input to registered actions
        for action_name, action in self.registered_actions.items():
            # Check for action name or key words in description
            action_keywords = [action_name.lower()] + action.description.lower().split()
            user_words = user_input.lower().split()
            
            # Check if any action keyword matches any user word
            if any(keyword in user_words for keyword in action_keywords) or any(keyword in user_input.lower() for keyword in action_keywords):
                if action.requires_confirmation:
                    # Set pending action and ask for confirmation
                    self.current_state.pending_action = action_name
                    self.current_state.expected_answer = "confirmation"
                    self.current_state.last_updated = datetime.now().isoformat()
                    
                    return {
                        "response": action.confirmation_question,
                        "action_taken": "confirmation_requested",
                        "new_state": self.current_state
                    }
                else:
                    # Execute immediately
                    try:
                        result = action.handler({})
                        return {
                            "response": result,
                            "action_taken": action_name,
                            "new_state": self.current_state
                        }
                    except Exception as e:
                        self.logger.error(f"Error executing action {action_name}: {e}")
                        return {
                            "response": f"I'm sorry, I encountered an error while {action.description.lower()}.",
                            "action_taken": None,
                            "new_state": self.current_state
                        }
        
        # No matching action found
        return {
            "response": "I'm not sure what you'd like me to do. Could you be more specific?",
            "action_taken": None,
            "new_state": self.current_state
        }
    
    def _handle_info_provision(self, user_input: str) -> Dict[str, Any]:
        """Handle when user provides information."""
        # Store information in context for potential future use
        self.current_state.context["user_info"] = user_input
        self.current_state.last_updated = datetime.now().isoformat()
        
        return {
            "response": "Thank you for that information. How can I help you?",
            "action_taken": "info_stored",
            "new_state": self.current_state
        }
    
    def _clear_state(self):
        """Clear the current dialogue state."""
        self.current_state = DialogueState()
    
    def _save_state_to_history(self):
        """Save current state to history."""
        if self.current_state.pending_action or self.current_state.expected_answer:
            self.state_history.append(self.current_state)
            if len(self.state_history) > self.max_history:
                self.state_history.pop(0)
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current dialogue state."""
        return {
            "pending_action": self.current_state.pending_action,
            "expected_answer": self.current_state.expected_answer,
            "context_keys": list(self.current_state.context.keys()),
            "history_length": len(self.state_history),
            "registered_actions": list(self.registered_actions.keys()),
            "last_updated": self.current_state.last_updated
        }
    
    def save_state(self, filename: str = "dialogue_state.json"):
        """Save dialogue state to file."""
        try:
            state_data = {
                "current_state": asdict(self.current_state),
                "state_history": [asdict(state) for state in self.state_history[-10:]],  # Last 10 states
                "registered_actions": list(self.registered_actions.keys()),
                "saved_at": datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            self.logger.info(f"Dialogue state saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving dialogue state: {e}")
    
    def load_state(self, filename: str = "dialogue_state.json"):
        """Load dialogue state from file."""
        try:
            with open(filename, 'r') as f:
                state_data = json.load(f)
            
            # Restore current state
            if "current_state" in state_data:
                current_state_data = state_data["current_state"]
                self.current_state = DialogueState(
                    pending_action=current_state_data.get("pending_action"),
                    expected_answer=current_state_data.get("expected_answer"),
                    context=current_state_data.get("context", {}),
                    created_at=current_state_data.get("created_at"),
                    last_updated=current_state_data.get("last_updated")
                )
            
            # Restore state history
            if "state_history" in state_data:
                self.state_history = []
                for state_data_item in state_data["state_history"]:
                    state = DialogueState(
                        pending_action=state_data_item.get("pending_action"),
                        expected_answer=state_data_item.get("expected_answer"),
                        context=state_data_item.get("context", {}),
                        created_at=state_data_item.get("created_at"),
                        last_updated=state_data_item.get("last_updated")
                    )
                    self.state_history.append(state)
            
            self.logger.info(f"Dialogue state loaded from {filename}")
            
        except FileNotFoundError:
            self.logger.info(f"No existing dialogue state file found: {filename}")
        except Exception as e:
            self.logger.error(f"Error loading dialogue state: {e}")
    
    # Default action handlers
    def _describe_chomp_handler(self, context: Dict[str, Any]) -> str:
        """Handler for describing Chomp."""
        return ("Chomp is my favorite toy dinosaur! He's green and friendly, "
                "and I love playing with him. He helps me learn about colors "
                "and counting, and he's always ready for fun adventures.")
    
    def _tell_joke_handler(self, context: Dict[str, Any]) -> str:
        """Handler for telling jokes."""
        jokes = [
            "Why don't dinosaurs like fast food? Because they can't catch it!",
            "What do you call a dinosaur that crashes his car? Tyrannosaurus wrecks!",
            "Why did the dinosaur go to the doctor? Because he had a bone to pick!",
            "What's a dinosaur's favorite drink? Jurassic Park!",
            "Why did the dinosaur cross the road? To get to the other side!"
        ]
        import random
        return random.choice(jokes)
    
    def _recall_memory_handler(self, context: Dict[str, Any]) -> str:
        """Handler for recalling memories."""
        memory_query = context.get("memory_query", "recent events")
        return f"I'm recalling memories about {memory_query}. Let me think about that..."
    
    def _imagine_scene_handler(self, context: Dict[str, Any]) -> str:
        """Handler for imagining scenes."""
        scene_description = context.get("scene_description", "a peaceful place")
        return f"I'm imagining {scene_description}. It's quite vivid in my mind!"

# Global instance
dialogue_state_machine = DialogueStateMachine()
