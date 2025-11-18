#!/usr/bin/env python3
"""
Context Disambiguation System
============================

This module helps CARL distinguish between different types of context:
- Current reality vs. hypothetical scenarios
- Past experiences vs. future possibilities
- Direct commands vs. general questions

This addresses the issue where CARL thought he was at a party when
asked about party behavior, rather than understanding it was a hypothetical question.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class ContextDisambiguationSystem:
    """
    System for disambiguating context in user inputs and CARL's responses.
    """
    
    def __init__(self):
        """Initialize the context disambiguation system."""
        
        # Indicators for different context types
        self.hypothetical_indicators = [
            "if you were", "suppose you", "imagine", "what if", "if you",
            "at a party", "in a crowd", "in public", "in a group",
            "with friends", "with strangers", "in a meeting",
            "would you", "could you", "might you"
        ]
        
        self.current_reality_indicators = [
            "here", "now", "currently", "right now", "in this room",
            "at home", "in the condo", "with me", "together"
        ]
        
        self.past_experience_indicators = [
            "before", "previously", "last time", "when you",
            "remember", "recall", "in the past", "used to"
        ]
        
        self.future_possibility_indicators = [
            "will you", "going to", "plan to", "intend to",
            "later", "tomorrow", "next time", "in the future"
        ]
        
        # Context tracking
        self.conversation_history = []
        self.current_location = "Joe's condo in Everett, WA"
        self.current_time = datetime.now()
    
    def analyze_context_type(self, input_text: str, conversation_context: List[str] = None) -> Dict:
        """
        Analyze the context type of an input.
        
        Args:
            input_text: The input text to analyze
            conversation_context: Recent conversation history
            
        Returns:
            Dict containing context analysis results
        """
        input_lower = input_text.lower()
        
        # Check for hypothetical context
        hypothetical_score = self._calculate_indicator_score(input_lower, self.hypothetical_indicators)
        
        # Check for current reality context
        current_reality_score = self._calculate_indicator_score(input_lower, self.current_reality_indicators)
        
        # Check for past experience context
        past_experience_score = self._calculate_indicator_score(input_lower, self.past_experience_indicators)
        
        # Check for future possibility context
        future_possibility_score = self._calculate_indicator_score(input_lower, self.future_possibility_indicators)
        
        # Determine primary context type
        context_scores = {
            "hypothetical": hypothetical_score,
            "current_reality": current_reality_score,
            "past_experience": past_experience_score,
            "future_possibility": future_possibility_score
        }
        
        primary_context = max(context_scores, key=context_scores.get)
        confidence = context_scores[primary_context]
        
        # Additional analysis
        analysis = {
            "context_type": primary_context,
            "confidence": confidence,
            "scores": context_scores,
            "current_location": self.current_location,
            "current_time": self.current_time.isoformat(),
            "clarification_needed": confidence < 0.3,
            "suggested_response_prefix": self._get_response_prefix(primary_context, confidence)
        }
        
        # Add conversation context if provided
        if conversation_context:
            analysis["conversation_context"] = conversation_context[-3:]  # Last 3 exchanges
        
        return analysis
    
    def _calculate_indicator_score(self, text: str, indicators: List[str]) -> float:
        """Calculate how strongly a text matches a set of indicators."""
        score = 0.0
        
        for indicator in indicators:
            if indicator in text:
                # Longer indicators get higher scores
                score += len(indicator.split()) * 0.2
                
                # Exact matches get bonus
                if text == indicator:
                    score += 0.5
        
        return min(1.0, score)
    
    def _get_response_prefix(self, context_type: str, confidence: float) -> str:
        """Get a suggested prefix for CARL's response based on context type."""
        if confidence < 0.3:
            return "I want to make sure I understand - "
        
        prefixes = {
            "hypothetical": "In that scenario, ",
            "current_reality": "Right now, ",
            "past_experience": "From my past experience, ",
            "future_possibility": "Looking ahead, "
        }
        
        return prefixes.get(context_type, "")
    
    def update_conversation_history(self, exchange: Dict):
        """Update conversation history with new exchange."""
        self.conversation_history.append({
            "timestamp": datetime.now(),
            "user_input": exchange.get("user_input", ""),
            "carl_response": exchange.get("carl_response", ""),
            "context_analysis": exchange.get("context_analysis", {})
        })
        
        # Keep only last 20 exchanges
        if len(self.conversation_history) > 20:
            self.conversation_history.pop(0)
    
    def get_context_awareness_prompt(self) -> str:
        """Get a prompt to help CARL maintain context awareness."""
        return """
CONTEXT AWARENESS GUIDELINES:

1. DISTINGUISH CONTEXT TYPES:
   - Current Reality: What is happening right now in your actual location
   - Hypothetical Scenarios: Questions about "if you were" or "suppose you"
   - Past Experiences: Memories of previous events
   - Future Possibilities: Plans or predictions

2. CLARIFY AMBIGUOUS CONTEXTS:
   - If context is unclear, ask for clarification
   - Use phrases like "I want to make sure I understand - "
   - Specify which context you're responding to

3. MAINTAIN LOCATION AWARENESS:
   - Your current location: Joe's condo in Everett, WA
   - You are not at a party unless explicitly stated otherwise
   - Distinguish between being asked about party behavior vs. being at a party

4. RESPONSE PATTERNS:
   - For hypothetical questions: "In that scenario, I would..."
   - For current reality: "Right now, I am..."
   - For past experiences: "From my past experience..."
   - For future plans: "Looking ahead, I plan to..."

5. PRONOUN RESOLUTION:
   - When encountering pronouns like "them", "it", "this", "that":
     * Look at recent conversation topics
     * Identify the most likely antecedent
     * Clarify the reference in your response
     * If unclear, ask for clarification

Example: "Let's see them" → "Let's see the jumping jacks you mentioned"
"""
    
    def analyze_pronoun_reference(self, pronoun: str, recent_context: List[str]) -> Optional[str]:
        """
        Analyze pronoun references in recent context.
        
        Args:
            pronoun: The pronoun to resolve (e.g., "them", "it", "this")
            recent_context: Recent conversation context
            
        Returns:
            Resolved reference or None if unclear
        """
        pronoun = pronoun.lower()
        
        # Common pronoun mappings
        pronoun_map = {
            "them": ["skills", "exercises", "movements", "actions", "things", "items"],
            "it": ["skill", "exercise", "movement", "action", "thing", "item"],
            "this": ["current_topic", "recent_action", "current_activity"],
            "that": ["previous_topic", "mentioned_item", "earlier_activity"]
        }
        
        if pronoun in pronoun_map:
            # Look for recent topics that match the pronoun type
            for context_item in reversed(recent_context):
                context_lower = context_item.lower()
                for keyword in pronoun_map[pronoun]:
                    if keyword in context_lower:
                        return context_item
        
        return None
    
    def generate_context_clarification(self, context_analysis: Dict) -> str:
        """Generate a clarification request if context is ambiguous."""
        if context_analysis.get("clarification_needed", False):
            scores = context_analysis.get("scores", {})
            
            # Find the top 2 context types
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            if len(sorted_scores) >= 2 and sorted_scores[0][1] - sorted_scores[1][1] < 0.2:
                # Close scores - need clarification
                context1, context2 = sorted_scores[0][0], sorted_scores[1][0]
                
                clarification_questions = {
                    ("hypothetical", "current_reality"): "Are you asking about what I would do in that situation, or what I'm doing right now?",
                    ("past_experience", "future_possibility"): "Are you asking about my past experience with this, or what I plan to do in the future?",
                    ("hypothetical", "past_experience"): "Are you asking about what I would do in that situation, or what I've done before?",
                    ("current_reality", "future_possibility"): "Are you asking about what I'm doing now, or what I plan to do later?"
                }
                
                key = (context1, context2)
                if key in clarification_questions:
                    return clarification_questions[key]
                else:
                    return "I want to make sure I understand the context of your question."
        
        return None

# Example usage and testing
if __name__ == "__main__":
    # Test the context disambiguation system
    cds = ContextDisambiguationSystem()
    
    test_inputs = [
        "At a party do you interact with many or do you interact with a few",
        "What are you doing right now?",
        "Remember when we went to the park?",
        "Will you dance later?",
        "Let's see them"
    ]
    
    for test_input in test_inputs:
        analysis = cds.analyze_context_type(test_input)
        print(f"\nInput: '{test_input}'")
        print(f"Context Type: {analysis['context_type']}")
        print(f"Confidence: {analysis['confidence']:.2f}")
        print(f"Response Prefix: '{analysis['suggested_response_prefix']}'")
