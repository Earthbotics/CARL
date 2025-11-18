#!/usr/bin/env python3
"""
Cognitive AI Integration System
==============================

Implements "Multi-Phase Cognitive Architecture with Conditional AI Integration"
- Hierarchical cognitive processing with selective AI augmentation
- Template-based OpenAI calls during personality functions
- Maintains realistic human cognition timing and order
- Intelligent caching and response integration
"""

import json
import time
import hashlib
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

@dataclass
class AICallContext:
    """Context for AI calls during cognitive processing."""
    cognitive_function: str
    message: str
    personality_traits: Dict[str, Any]
    neurotransmitter_levels: Dict[str, float]
    current_goals: List[str]
    current_values: List[str]
    context_history: List[str]
    social_context: Dict[str, Any]
    logical_framework: Dict[str, Any]
    system_context: Dict[str, Any]

@dataclass
class AICallResult:
    """Result of an AI call during cognitive processing."""
    cognitive_function: str
    response: Dict[str, Any]
    confidence_score: float
    processing_time: float
    cache_hit: bool
    timestamp: datetime

class CognitiveFunctionAICallManager:
    """Manages AI calls during cognitive function processing."""
    
    def __init__(self, openai_client=None):
        self.openai_client = openai_client
        self.ai_call_templates = self._load_ai_call_templates()
        self.response_cache = {}
        self.call_history = []
        self.logger = logging.getLogger(__name__)
        
        # Personality-driven thresholds for AI calls
        self.ai_call_thresholds = {
            "extroversion": 0.3,  # Low social energy triggers AI call
            "introversion": 0.7,  # High internal energy triggers AI call
            "sensation": 0.6,     # High detail focus triggers AI call
            "intuition": 0.7,     # High intuition triggers AI call
            "feeling": 0.4,       # Moderate feeling triggers AI call
            "thinking": 0.8,      # High thinking triggers AI call
            "perceiving": 0.6,    # High perceiving triggers AI call
            "judging": 0.5        # Moderate judging triggers AI call
        }
        
    def _load_ai_call_templates(self) -> Dict[str, str]:
        """Load AI call templates for each cognitive function."""
        return {
            "extroversion": """
As an AI cognitive assistant, analyze the social interaction context:
User Message: {message}
Current Social Energy: {social_energy_level}
Personality Type: {mbti_type}
Social Context: {social_context}

Provide 2-3 insights about:
1. Social dynamics at play
2. Optimal interaction approach
3. Potential social risks/opportunities

Response format: JSON with "insights", "recommended_approach", "social_energy_impact"
""",
            "introversion": """
As an AI cognitive assistant, analyze internal goal alignment:
Current Goals: {current_goals}
Internal Energy: {internal_energy_level}
Personality Type: {mbti_type}
Current Values: {current_values}

Provide 2-3 insights about:
1. Goal alignment with current situation
2. Internal energy optimization
3. Personal value conflicts/resolutions

Response format: JSON with "goal_insights", "energy_optimization", "value_alignment"
""",
            "sensation": """
As an AI cognitive assistant, analyze sensory details:
Message: {message}
Detail Focus Level: {sensation_level}
Available Context: {context}

Provide 2-3 insights about:
1. Key details that need attention
2. Missing contextual information
3. Detail prioritization strategy

Response format: JSON with "key_details", "missing_context", "priority_order"
""",
            "intuition": """
As an AI cognitive assistant, generate intuitive hypotheses:
Message: {message}
Intuition Level: {intuition_level}
Previous Context: {context_history}

Generate 3-5 possible interpretations:
1. Literal meaning
2. Metaphorical/symbolic meaning
3. Pattern connections
4. Underlying motivations
5. Future implications

Response format: JSON with "interpretations", "confidence_scores", "pattern_connections"
""",
            "feeling": """
As an AI cognitive assistant, analyze emotional and value implications:
Message: {message}
Feeling Function: {feeling_type}
Current Values: {current_values}
Social Context: {social_context}

Provide 2-3 insights about:
1. Emotional impact on self/others
2. Value alignment/conflicts
3. Social harmony implications

Response format: JSON with "emotional_impact", "value_assessment", "social_implications"
""",
            "thinking": """
As an AI cognitive assistant, perform logical analysis:
Message: {message}
Thinking Function: {thinking_type}
Logical Framework: {logical_framework}
System Context: {system_context}

Provide 2-3 insights about:
1. Logical consistency assessment
2. Systematic analysis results
3. Efficiency optimization opportunities

Response format: JSON with "logical_assessment", "systematic_insights", "efficiency_recommendations"
""",
            "perceiving": """
As an AI cognitive assistant, assess perceptual openness:
Message: {message}
Perceiving Level: {perceiving_level}
Information Gaps: {information_gaps}
Adaptation Needs: {adaptation_needs}

Provide 2-3 insights about:
1. Maintaining openness to new information
2. Exploration strategies for gaps
3. Flexibility requirements

Response format: JSON with "openness_strategies", "exploration_plans", "flexibility_assessment"
""",
            "judging": """
As an AI cognitive assistant, assess judgment and decision-making:
Message: {message}
Judging Level: {judging_level}
Decision Context: {decision_context}
Commitment Requirements: {commitment_needs}

Provide 2-3 insights about:
1. Decision framework appropriateness
2. Commitment readiness assessment
3. Structure optimization needs

Response format: JSON with "decision_assessment", "commitment_readiness", "structure_recommendations"
"""
        }
    
    def should_make_ai_call(self, cognitive_function: str, context: AICallContext, personality_traits: Dict[str, Any]) -> bool:
        """Determine if AI call is needed for this cognitive function."""
        try:
            # Check personality-driven thresholds
            threshold = self.ai_call_thresholds.get(cognitive_function, 0.5)
            
            # Get relevant personality trait level
            if cognitive_function == "extroversion":
                trait_level = personality_traits.get("energy", {}).get("extrovert", 0.5)
            elif cognitive_function == "introversion":
                trait_level = personality_traits.get("energy", {}).get("introvert", 0.5)
            elif cognitive_function == "sensation":
                trait_level = personality_traits.get("collection", {}).get("sensation", 0.5)
            elif cognitive_function == "intuition":
                trait_level = personality_traits.get("collection", {}).get("intuition", 0.5)
            elif cognitive_function == "feeling":
                trait_level = personality_traits.get("decision", {}).get("feeling", 0.5)
            elif cognitive_function == "thinking":
                trait_level = personality_traits.get("decision", {}).get("thinking", 0.5)
            elif cognitive_function == "perceiving":
                trait_level = personality_traits.get("organize", {}).get("perceiving", 0.5)
            elif cognitive_function == "judging":
                trait_level = personality_traits.get("organize", {}).get("judging", 0.5)
            else:
                trait_level = 0.5
            
            # Check if trait level exceeds threshold
            if trait_level < threshold:
                return False
            
            # Check cache for similar contexts
            cache_key = self._generate_cache_key(cognitive_function, context)
            if cache_key in self.response_cache:
                cached_result = self.response_cache[cache_key]
                # Check if cache is still valid (within 5 minutes)
                if (datetime.now() - cached_result.timestamp).total_seconds() < 300:
                    return False
            
            # Additional context-specific checks
            if cognitive_function == "intuition" and "?" in context.message:
                return True  # Questions often need intuitive analysis
            
            if cognitive_function == "thinking" and len(context.message.split()) > 10:
                return True  # Complex messages need logical analysis
            
            if cognitive_function == "feeling" and any(word in context.message.lower() for word in ["feel", "emotion", "value", "care"]):
                return True  # Emotional content needs feeling analysis
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error determining AI call need: {e}")
            return False
    
    def _generate_cache_key(self, cognitive_function: str, context: AICallContext) -> str:
        """Generate cache key for AI call context."""
        try:
            # Create a hash of the relevant context
            context_str = f"{cognitive_function}:{context.message}:{context.personality_traits.get('mbti_type', 'INTP')}"
            return hashlib.md5(context_str.encode()).hexdigest()
        except Exception as e:
            self.logger.error(f"Error generating cache key: {e}")
            return f"{cognitive_function}_{int(time.time())}"
    
    async def make_ai_call(self, cognitive_function: str, context: AICallContext, personality_traits: Dict[str, Any]) -> AICallResult:
        """Execute AI call for specific cognitive function."""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(cognitive_function, context)
            if cache_key in self.response_cache:
                cached_result = self.response_cache[cache_key]
                if (datetime.now() - cached_result.timestamp).total_seconds() < 300:
                    self.logger.info(f"Cache hit for {cognitive_function} AI call")
                    return AICallResult(
                        cognitive_function=cognitive_function,
                        response=cached_result.response,
                        confidence_score=cached_result.confidence_score,
                        processing_time=time.time() - start_time,
                        cache_hit=True,
                        timestamp=datetime.now()
                    )
            
            # Generate prompt from template
            prompt = self._generate_prompt(cognitive_function, context, personality_traits)
            
            # Make OpenAI call
            if self.openai_client:
                response = await self._call_openai(prompt)
            else:
                # Fallback to mock response for testing
                response = self._generate_mock_response(cognitive_function, context)
            
            # Create result
            result = AICallResult(
                cognitive_function=cognitive_function,
                response=response,
                confidence_score=self._calculate_confidence(response),
                processing_time=time.time() - start_time,
                cache_hit=False,
                timestamp=datetime.now()
            )
            
            # Cache result
            self.response_cache[cache_key] = result
            self.call_history.append(result)
            
            # Limit cache size
            if len(self.response_cache) > 1000:
                self._cleanup_cache()
            
            self.logger.info(f"AI call completed for {cognitive_function} in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Error making AI call for {cognitive_function}: {e}")
            return AICallResult(
                cognitive_function=cognitive_function,
                response={"error": str(e)},
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                cache_hit=False,
                timestamp=datetime.now()
            )
    
    def _generate_prompt(self, cognitive_function: str, context: AICallContext, personality_traits: Dict[str, Any]) -> str:
        """Generate prompt from template for cognitive function."""
        try:
            template = self.ai_call_templates.get(cognitive_function, "")
            
            # Prepare context variables
            context_vars = {
                "message": context.message,
                "mbti_type": personality_traits.get("mbti_type", "INTP"),
                "social_energy_level": personality_traits.get("energy", {}).get("extrovert", 0.5),
                "internal_energy_level": personality_traits.get("energy", {}).get("introvert", 0.5),
                "sensation_level": personality_traits.get("collection", {}).get("sensation", 0.5),
                "intuition_level": personality_traits.get("collection", {}).get("intuition", 0.5),
                "feeling_type": "Fi" if personality_traits.get("energy", {}).get("introvert", 0.5) > 0.5 else "Fe",
                "thinking_type": "Ti" if personality_traits.get("energy", {}).get("introvert", 0.5) > 0.5 else "Te",
                "perceiving_level": personality_traits.get("organize", {}).get("perceiving", 0.5),
                "judging_level": personality_traits.get("organize", {}).get("judging", 0.5),
                "current_goals": context.current_goals,
                "current_values": context.current_values,
                "context_history": context.context_history,
                "social_context": context.social_context,
                "logical_framework": context.logical_framework,
                "system_context": context.system_context,
                "context": context.context_history[-3:] if context.context_history else [],
                "information_gaps": [],
                "adaptation_needs": [],
                "decision_context": {},
                "commitment_needs": []
            }
            
            return template.format(**context_vars)
            
        except Exception as e:
            self.logger.error(f"Error generating prompt: {e}")
            return f"Analyze this message: {context.message}"
    
    async def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Make actual OpenAI API call."""
        try:
            if not self.openai_client:
                return self._generate_mock_response("general", AICallContext("general", prompt, {}, {}, [], [], [], {}, {}, {}))
            
            # This would be the actual OpenAI call
            # response = await self.openai_client.chat.completions.create(
            #     model="gpt-4",
            #     messages=[{"role": "user", "content": prompt}],
            #     temperature=0.7,
            #     max_tokens=500
            # )
            
            # For now, return mock response
            return self._generate_mock_response("general", AICallContext("general", prompt, {}, {}, [], [], [], {}, {}, {}))
            
        except Exception as e:
            self.logger.error(f"Error calling OpenAI: {e}")
            return {"error": str(e)}
    
    def _generate_mock_response(self, cognitive_function: str, context: AICallContext) -> Dict[str, Any]:
        """Generate mock response for testing."""
        mock_responses = {
            "extroversion": {
                "insights": ["User appears to be seeking social interaction", "Message suggests openness to conversation"],
                "recommended_approach": "Engage warmly but respect social energy levels",
                "social_energy_impact": 0.3
            },
            "introversion": {
                "goal_insights": ["Current situation aligns with personal learning goals", "Internal energy is well-suited for this interaction"],
                "energy_optimization": "Maintain current energy level for optimal processing",
                "value_alignment": 0.8
            },
            "sensation": {
                "key_details": ["Message contains specific technical terms", "User provided concrete examples"],
                "missing_context": ["Previous conversation context", "Technical background"],
                "priority_order": ["Technical accuracy", "Concrete examples", "Context clarity"]
            },
            "intuition": {
                "interpretations": [
                    "Literal: User is asking for technical information",
                    "Metaphorical: User is exploring new possibilities",
                    "Pattern: This connects to previous learning patterns"
                ],
                "confidence_scores": [0.9, 0.7, 0.6],
                "pattern_connections": ["Previous technical discussions", "Learning progression"]
            },
            "feeling": {
                "emotional_impact": "Positive engagement with learning",
                "value_assessment": "Aligns with personal growth values",
                "social_implications": "Maintains harmonious learning environment"
            },
            "thinking": {
                "logical_assessment": "Message follows logical structure",
                "systematic_insights": "Information is well-organized",
                "efficiency_recommendations": "Current approach is optimal"
            },
            "perceiving": {
                "openness_strategies": ["Maintain flexibility in response", "Keep options open"],
                "exploration_plans": ["Explore related topics", "Consider alternative approaches"],
                "flexibility_assessment": "High flexibility needed"
            },
            "judging": {
                "decision_assessment": "Ready to make structured response",
                "commitment_readiness": "High commitment to helpful response",
                "structure_recommendations": "Use clear, organized response format"
            }
        }
        
        return mock_responses.get(cognitive_function, {"analysis": "General cognitive analysis completed"})
    
    def _calculate_confidence(self, response: Dict[str, Any]) -> float:
        """Calculate confidence score for AI response."""
        try:
            # Simple confidence calculation based on response structure
            if "error" in response:
                return 0.0
            
            # Higher confidence for responses with more structured data
            confidence = 0.5  # Base confidence
            
            if len(response) > 2:
                confidence += 0.2
            
            if any(key in response for key in ["insights", "analysis", "assessment"]):
                confidence += 0.3
            
            return min(1.0, confidence)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _cleanup_cache(self):
        """Clean up old cache entries."""
        try:
            # Remove entries older than 10 minutes
            current_time = datetime.now()
            keys_to_remove = []
            
            for key, result in self.response_cache.items():
                if (current_time - result.timestamp).total_seconds() > 600:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.response_cache[key]
            
            self.logger.info(f"Cleaned up {len(keys_to_remove)} cache entries")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up cache: {e}")

class AIResponseIntegrationSystem:
    """Integrates AI responses back into cognitive flow."""
    
    def __init__(self):
        self.integration_strategies = self._load_integration_strategies()
        self.logger = logging.getLogger(__name__)
    
    def _load_integration_strategies(self) -> Dict[str, callable]:
        """Load integration strategies for each cognitive function."""
        return {
            "extroversion": self._integrate_extroversion_response,
            "introversion": self._integrate_introversion_response,
            "sensation": self._integrate_sensation_response,
            "intuition": self._integrate_intuition_response,
            "feeling": self._integrate_feeling_response,
            "thinking": self._integrate_thinking_response,
            "perceiving": self._integrate_perceiving_response,
            "judging": self._integrate_judging_response
        }
    
    def integrate_response(self, ai_result: AICallResult, cognitive_function: str, context: AICallContext) -> Dict[str, Any]:
        """Integrate AI response back into cognitive flow."""
        try:
            strategy = self.integration_strategies.get(cognitive_function, self._integrate_general_response)
            return strategy(ai_result, context)
            
        except Exception as e:
            self.logger.error(f"Error integrating AI response: {e}")
            return {"integration_status": "error", "error": str(e)}
    
    def _integrate_extroversion_response(self, ai_result: AICallResult, context: AICallContext) -> Dict[str, Any]:
        """Integrate extroversion AI response."""
        response = ai_result.response
        
        # Update neurotransmitter levels based on social energy impact
        neuro_updates = {}
        if "social_energy_impact" in response:
            impact = response["social_energy_impact"]
            neuro_updates["oxytocin"] = impact * 0.1
            neuro_updates["serotonin"] = impact * 0.05
        
        return {
            "cognitive_function": "extroversion",
            "neurotransmitter_updates": neuro_updates,
            "social_insights": response.get("insights", []),
            "recommended_approach": response.get("recommended_approach", ""),
            "confidence": ai_result.confidence_score
        }
    
    def _integrate_introversion_response(self, ai_result: AICallResult, context: AICallContext) -> Dict[str, Any]:
        """Integrate introversion AI response."""
        response = ai_result.response
        
        # Update neurotransmitter levels based on goal alignment
        neuro_updates = {}
        if "value_alignment" in response:
            alignment = response["value_alignment"]
            neuro_updates["dopamine"] = alignment * 0.1
            neuro_updates["acetylcholine"] = alignment * 0.05
        
        return {
            "cognitive_function": "introversion",
            "neurotransmitter_updates": neuro_updates,
            "goal_insights": response.get("goal_insights", []),
            "energy_optimization": response.get("energy_optimization", ""),
            "confidence": ai_result.confidence_score
        }
    
    def _integrate_sensation_response(self, ai_result: AICallResult, context: AICallContext) -> Dict[str, Any]:
        """Integrate sensation AI response."""
        response = ai_result.response
        
        # Update neurotransmitter levels for detail processing
        neuro_updates = {
            "norepinephrine": 0.05,  # Increased attention
            "glutamate": 0.03        # Enhanced learning
        }
        
        return {
            "cognitive_function": "sensation",
            "neurotransmitter_updates": neuro_updates,
            "key_details": response.get("key_details", []),
            "missing_context": response.get("missing_context", []),
            "priority_order": response.get("priority_order", []),
            "confidence": ai_result.confidence_score
        }
    
    def _integrate_intuition_response(self, ai_result: AICallResult, context: AICallContext) -> Dict[str, Any]:
        """Integrate intuition AI response."""
        response = ai_result.response
        
        # Update neurotransmitter levels for pattern recognition
        neuro_updates = {
            "dopamine": 0.08,        # Pattern recognition reward
            "acetylcholine": 0.05    # Enhanced memory
        }
        
        return {
            "cognitive_function": "intuition",
            "neurotransmitter_updates": neuro_updates,
            "interpretations": response.get("interpretations", []),
            "confidence_scores": response.get("confidence_scores", []),
            "pattern_connections": response.get("pattern_connections", []),
            "confidence": ai_result.confidence_score
        }
    
    def _integrate_feeling_response(self, ai_result: AICallResult, context: AICallContext) -> Dict[str, Any]:
        """Integrate feeling AI response."""
        response = ai_result.response
        
        # Update neurotransmitter levels for emotional processing
        neuro_updates = {
            "serotonin": 0.05,       # Emotional stability
            "oxytocin": 0.03         # Social bonding
        }
        
        return {
            "cognitive_function": "feeling",
            "neurotransmitter_updates": neuro_updates,
            "emotional_impact": response.get("emotional_impact", ""),
            "value_assessment": response.get("value_assessment", ""),
            "social_implications": response.get("social_implications", ""),
            "confidence": ai_result.confidence_score
        }
    
    def _integrate_thinking_response(self, ai_result: AICallResult, context: AICallContext) -> Dict[str, Any]:
        """Integrate thinking AI response."""
        response = ai_result.response
        
        # Update neurotransmitter levels for logical processing
        neuro_updates = {
            "acetylcholine": 0.05,   # Enhanced learning
            "glutamate": 0.03        # Cognitive enhancement
        }
        
        return {
            "cognitive_function": "thinking",
            "neurotransmitter_updates": neuro_updates,
            "logical_assessment": response.get("logical_assessment", ""),
            "systematic_insights": response.get("systematic_insights", []),
            "efficiency_recommendations": response.get("efficiency_recommendations", []),
            "confidence": ai_result.confidence_score
        }
    
    def _integrate_perceiving_response(self, ai_result: AICallResult, context: AICallContext) -> Dict[str, Any]:
        """Integrate perceiving AI response."""
        response = ai_result.response
        
        # Update neurotransmitter levels for openness
        neuro_updates = {
            "dopamine": 0.05,        # Exploration reward
            "glutamate": 0.03        # Enhanced flexibility
        }
        
        return {
            "cognitive_function": "perceiving",
            "neurotransmitter_updates": neuro_updates,
            "openness_strategies": response.get("openness_strategies", []),
            "exploration_plans": response.get("exploration_plans", []),
            "flexibility_assessment": response.get("flexibility_assessment", ""),
            "confidence": ai_result.confidence_score
        }
    
    def _integrate_judging_response(self, ai_result: AICallResult, context: AICallContext) -> Dict[str, Any]:
        """Integrate judging AI response."""
        response = ai_result.response
        
        # Update neurotransmitter levels for decision-making
        neuro_updates = {
            "serotonin": 0.05,       # Decision confidence
            "endorphins": 0.03       # Completion satisfaction
        }
        
        return {
            "cognitive_function": "judging",
            "neurotransmitter_updates": neuro_updates,
            "decision_assessment": response.get("decision_assessment", ""),
            "commitment_readiness": response.get("commitment_readiness", ""),
            "structure_recommendations": response.get("structure_recommendations", []),
            "confidence": ai_result.confidence_score
        }
    
    def _integrate_general_response(self, ai_result: AICallResult, context: AICallContext) -> Dict[str, Any]:
        """Integrate general AI response."""
        return {
            "cognitive_function": ai_result.cognitive_function,
            "neurotransmitter_updates": {},
            "analysis": ai_result.response,
            "confidence": ai_result.confidence_score
        }
