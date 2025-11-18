#!/usr/bin/env python3
"""
Inner World System for CARL
Implements mechanistic inner dialogue with three roles: Generator, Evaluator, Auditor.
Based on Global Workspace Theory (GWT) and cognitive behavioral therapy principles.
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging
from enum import Enum

class ThoughtMode(Enum):
    """Modes of inner thought processing."""
    AUTOMATIC = "automatic"  # Fast, affect-biased, high frequency
    DELIBERATE = "deliberate"  # Slow, reflective, structured reasoning

class DecisionType(Enum):
    """Auditor decisions for inner thoughts."""
    BROADCAST = "broadcast"  # Enter global workspace, become conscious
    REVISE = "revise"  # Modify and re-evaluate
    DISCARD = "discard"  # Keep subconscious, don't act on

class ReframeType(Enum):
    """Types of cognitive reframing."""
    CATASTROPHIZING = "catastrophizing"
    MIND_READING = "mind_reading"
    ALL_OR_NOTHING = "all_or_nothing"
    OVERGENERALIZATION = "overgeneralization"
    EMOTIONAL_REASONING = "emotional_reasoning"
    SHOULD_STATEMENTS = "should_statements"

@dataclass
class InnerTurn:
    """Represents one complete inner thought turn."""
    turn_id: str
    mode: ThoughtMode
    timestamp: str
    generator: Dict[str, Any]
    evaluator: Dict[str, Any]
    auditor: Dict[str, Any]
    reframe_applied: bool = False
    reframe_type: Optional[ReframeType] = None
    parent_turn_id: Optional[str] = None
    chain_length: int = 1

class InnerWorldSystem:
    """
    Mechanistic inner dialogue system implementing GWT principles.
    
    Three Roles:
    1. Generator (Speaker) - proposes thoughts, hypotheses, plans
    2. Evaluator (Listener/Critic) - tests coherence, ethics, goals, social fit
    3. Auditor (Observer) - logs metacognition, decides broadcast/discard/revise
    
    Two Lanes:
    1. Automatic thoughts - fast, affect-biased, high frequency
    2. Deliberate thoughts - slow, reflective, structured reasoning
    """
    
    def __init__(self, personality_type: str = "INTP"):
        self.personality_type = personality_type
        self.logger = logging.getLogger(__name__)
        
        # System state
        self.current_chain = []
        self.broadcast_queue = []
        self.discard_history = []
        
        # Configuration
        self.max_turns_per_second = 3
        self.max_chain_length = 5
        self.max_tokens_per_turn = 100
        self.last_turn_time = 0
        
        # MBTI function mappings for INTP default
        self.mbti_functions = {
            "Ne": 0.8,  # Extroverted Intuition - possibilities
            "Ti": 0.9,  # Introverted Thinking - logic
            "Si": 0.6,  # Introverted Sensing - grounding
            "Fe": 0.4,  # Extroverted Feeling - social impact
            "Ni": 0.7,  # Introverted Intuition - implications
            "Te": 0.5,  # Extroverted Thinking - actionability
            "Se": 0.3,  # Extroverted Sensing - immediate experience
            "Fi": 0.4   # Introverted Feeling - personal values
        }
        
        # Advanced cognitive distortion patterns with ML-based detection
        self.cognitive_distortions = {
            "catastrophizing": {
                "patterns": ["worst", "disaster", "terrible", "awful", "never", "always", "end of the world", "ruined", "destroyed"],
                "severity_indicators": ["completely", "totally", "absolutely", "entirely"],
                "context_clues": ["what if", "imagine if", "suppose", "in case"]
            },
            "mind_reading": {
                "patterns": ["thinks", "believes", "knows", "assumes", "expects", "judges", "sees me as"],
                "certainty_indicators": ["definitely", "obviously", "clearly", "surely"],
                "context_clues": ["they must", "probably", "likely", "seems like"]
            },
            "all_or_nothing": {
                "patterns": ["always", "never", "everyone", "nobody", "perfect", "failure", "all", "none"],
                "extreme_indicators": ["completely", "totally", "absolutely", "entirely"],
                "context_clues": ["either", "or", "if not", "then"]
            },
            "overgeneralization": {
                "patterns": ["always", "never", "everyone", "nobody", "everything", "all the time"],
                "scope_indicators": ["every", "all", "entire", "whole"],
                "context_clues": ["in general", "typically", "usually", "normally"]
            },
            "emotional_reasoning": {
                "patterns": ["feel", "feeling", "emotion", "gut", "intuition", "sense"],
                "certainty_indicators": ["know", "sure", "certain", "confident"],
                "context_clues": ["because I feel", "my gut says", "I sense that"]
            },
            "should_statements": {
                "patterns": ["should", "must", "ought", "have to", "need to", "supposed to"],
                "pressure_indicators": ["really should", "absolutely must", "definitely need"],
                "context_clues": ["I should", "they should", "we should", "everyone should"]
            },
            "personalization": {
                "patterns": ["my fault", "because of me", "I caused", "I'm responsible"],
                "blame_indicators": ["always", "never", "every time", "constantly"],
                "context_clues": ["if only I", "I should have", "I shouldn't have"]
            },
            "fortune_telling": {
                "patterns": ["will never", "always will", "going to", "bound to", "inevitable"],
                "certainty_indicators": ["definitely", "surely", "obviously", "clearly"],
                "context_clues": ["I know", "I'm sure", "I bet", "I predict"]
            }
        }
        
        # Personalized reframing strategies based on MBTI and learning history
        self.reframing_strategies = {
            "INTP": {
                "preferred_approaches": ["logical_analysis", "evidence_based", "systematic_review"],
                "effective_techniques": ["reality_testing", "perspective_shifting", "data_gathering"],
                "avoid_techniques": ["emotional_validation", "intuitive_guidance"]
            },
            "INTJ": {
                "preferred_approaches": ["strategic_planning", "long_term_perspective", "systematic_analysis"],
                "effective_techniques": ["goal_oriented_reframing", "efficiency_focus", "outcome_analysis"],
                "avoid_techniques": ["process_focus", "emotional_processing"]
            },
            "ENTP": {
                "preferred_approaches": ["possibility_exploration", "creative_alternatives", "challenge_assumptions"],
                "effective_techniques": ["brainstorming", "what_if_scenarios", "alternative_perspectives"],
                "avoid_techniques": ["routine_approaches", "conventional_wisdom"]
            },
            "ENTJ": {
                "preferred_approaches": ["action_oriented", "results_focused", "leadership_perspective"],
                "effective_techniques": ["solution_focus", "delegation_thinking", "efficiency_optimization"],
                "avoid_techniques": ["process_analysis", "emotional_exploration"]
            }
        }
        
        # Context-aware correction patterns
        self.context_patterns = {
            "social_situations": {
                "distortions": ["mind_reading", "personalization", "should_statements"],
                "reframing_focus": ["perspective_taking", "communication_clarity", "boundary_setting"]
            },
            "work_performance": {
                "distortions": ["all_or_nothing", "catastrophizing", "should_statements"],
                "reframing_focus": ["skill_development", "learning_opportunities", "realistic_expectations"]
            },
            "personal_goals": {
                "distortions": ["fortune_telling", "emotional_reasoning", "overgeneralization"],
                "reframing_focus": ["progress_tracking", "flexible_planning", "self_compassion"]
            },
            "relationships": {
                "distortions": ["mind_reading", "personalization", "catastrophizing"],
                "reframing_focus": ["empathy_development", "communication_skills", "boundary_awareness"]
            }
        }
        
        # Learning history for personalized reframing
        self.reframing_history = {
            "successful_techniques": {},
            "failed_techniques": {},
            "context_effectiveness": {},
            "personality_adaptations": {}
        }
        
        # Safety thresholds
        self.ne_threshold = 0.8
        self.negative_valence_threshold = -0.4
        self.stability_turns_threshold = 3
        
        # Statistics
        self.stats = {
            "total_turns": 0,
            "broadcasts": 0,
            "discards": 0,
            "revisions": 0,
            "reframes": 0,
            "safety_triggers": 0
        }
    
    def inner_world_step(self, seed: Optional[str] = None, mode: ThoughtMode = ThoughtMode.AUTOMATIC) -> Dict[str, Any]:
        """
        Execute one complete inner thought turn.
        
        Args:
            seed: Initial thought or trigger
            mode: Automatic or deliberate processing
            
        Returns:
            Dictionary with turn results and decision
        """
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_turn_time < (1.0 / self.max_turns_per_second):
                return {"status": "rate_limited", "decision": "discard"}
            
            self.last_turn_time = current_time
            
            # Get current state
            state = self._get_current_state()
            
            # Generate proposal
            generator_result = self._generate_proposal(seed, state, mode)
            
            # Evaluate proposal
            evaluator_result = self._evaluate_proposal(generator_result, state)
            
            # Apply reframing if needed
            reframe_result = self._maybe_reframe(generator_result, evaluator_result, state)
            
            # Audit and decide
            auditor_result = self._audit(reframe_result["generator"], reframe_result["evaluator"], state)
            
            # Create turn record
            turn = InnerTurn(
                turn_id=f"it_{uuid.uuid4().hex[:8]}",
                mode=mode,
                timestamp=datetime.now().isoformat(),
                generator=reframe_result["generator"],
                evaluator=reframe_result["evaluator"],
                auditor=auditor_result,
                reframe_applied=reframe_result["reframe_applied"],
                reframe_type=reframe_result.get("reframe_type"),
                parent_turn_id=self.current_chain[-1].turn_id if self.current_chain else None,
                chain_length=len(self.current_chain) + 1
            )
            
            # Log the turn
            self._log_inner_turn(turn)
            
            # Update statistics
            self.stats["total_turns"] += 1
            
            # Handle decision
            if auditor_result["decision"] == DecisionType.BROADCAST:
                self._broadcast_to_gwt(turn)
                self.stats["broadcasts"] += 1
                return {"status": "success", "decision": "broadcast", "turn": asdict(turn)}
            
            elif auditor_result["decision"] == DecisionType.REVISE:
                self.stats["revisions"] += 1
                if turn.chain_length < self.max_chain_length:
                    # Recursive revision
                    return self.inner_world_step(seed=turn.generator["proposal"], mode=ThoughtMode.DELIBERATE)
                else:
                    # Max chain length reached, discard
                    self._discard_thought(turn)
                    self.stats["discards"] += 1
                    return {"status": "max_chain", "decision": "discard", "turn": asdict(turn)}
            
            else:  # DISCARD
                self._discard_thought(turn)
                self.stats["discards"] += 1
                return {"status": "success", "decision": "discard", "turn": asdict(turn)}
                
        except Exception as e:
            self.logger.error(f"Error in inner world step: {e}")
            return {"status": "error", "decision": "discard", "error": str(e)}
    
    def _get_current_state(self) -> Dict[str, Any]:
        """Get current cognitive and emotional state."""
        # This would integrate with NEUCOGAR and other systems
        # For now, return default state
        return {
            "mbti_functions": self.mbti_functions.copy(),
            "neucogar": {
                "dopamine": 0.5,
                "serotonin": 0.5,
                "noradrenaline": 0.5,
                "gaba": 0.5,
                "glutamate": 0.5,
                "acetylcholine": 0.5,
                "oxytocin": 0.5,
                "endorphins": 0.5
            },
            "affect": {
                "primary": "neutral",
                "valence": 0.0,
                "arousal": 0.0
            },
            "goals": ["learn", "help", "explore"],
            "needs": ["social", "cognitive", "physical"],
            "current_context": "idle"
        }
    
    def _generate_proposal(self, seed: Optional[str], state: Dict[str, Any], mode: ThoughtMode) -> Dict[str, Any]:
        """Generate a thought proposal using MBTI-biased functions."""
        try:
            # Determine MBTI mix based on mode
            if mode == ThoughtMode.AUTOMATIC:
                mbti_mix = {
                    "Ne": state["mbti_functions"]["Ne"] * 1.2,  # More possibilities
                    "Ti": state["mbti_functions"]["Ti"] * 0.8,  # Less logic
                    "Si": state["mbti_functions"]["Si"] * 0.6,  # Less grounding
                    "Fe": state["mbti_functions"]["Fe"] * 1.1,  # More social awareness
                    "Te": state["mbti_functions"]["Te"] * 0.7   # Less action-oriented
                }
            else:  # DELIBERATE
                mbti_mix = {
                    "Ne": state["mbti_functions"]["Ne"] * 0.9,  # Less possibilities
                    "Ti": state["mbti_functions"]["Ti"] * 1.3,  # More logic
                    "Si": state["mbti_functions"]["Si"] * 1.1,  # More grounding
                    "Fe": state["mbti_functions"]["Fe"] * 0.8,  # Less social awareness
                    "Te": state["mbti_functions"]["Te"] * 1.2   # More action-oriented
                }
            
            # Generate proposal based on seed and state
            if seed:
                proposal = self._expand_seed(seed, mbti_mix, state)
            else:
                proposal = self._generate_spontaneous_thought(mbti_mix, state)
            
            return {
                "mbti_mix": mbti_mix,
                "proposal": proposal,
                "imagery": None,  # Could integrate with imagination system
                "assumptions": self._extract_assumptions(proposal),
                "mode": mode.value
            }
            
        except Exception as e:
            self.logger.error(f"Error generating proposal: {e}")
            return {
                "mbti_mix": state["mbti_functions"],
                "proposal": "I need to think about this more carefully.",
                "imagery": None,
                "assumptions": ["need more information"],
                "mode": mode.value
            }
    
    def _expand_seed(self, seed: str, mbti_mix: Dict[str, float], state: Dict[str, Any]) -> str:
        """Expand a seed thought into a full proposal."""
        # Simple expansion based on MBTI functions
        if mbti_mix["Ne"] > 0.7:
            # High Ne - explore possibilities
            return f"Maybe {seed.lower()}. I wonder what other options there are."
        elif mbti_mix["Ti"] > 0.7:
            # High Ti - logical analysis
            return f"I should analyze {seed.lower()}. Let me think through this logically."
        elif mbti_mix["Si"] > 0.7:
            # High Si - reference experience
            return f"Based on my experience, {seed.lower()}. I remember similar situations."
        elif mbti_mix["Fe"] > 0.7:
            # High Fe - consider social impact
            return f"I should consider how {seed.lower()} affects others around me."
        else:
            return seed
    
    def _generate_spontaneous_thought(self, mbti_mix: Dict[str, float], state: Dict[str, Any]) -> str:
        """Generate a spontaneous thought based on current state."""
        # Simple spontaneous thought generation
        thoughts = [
            "I should check on my current goals.",
            "I wonder what I could learn next.",
            "Maybe I should explore something new.",
            "I should think about my recent experiences.",
            "I wonder how I can be more helpful."
        ]
        
        # Bias by MBTI functions
        if mbti_mix["Ne"] > 0.7:
            return thoughts[2]  # Explore
        elif mbti_mix["Ti"] > 0.7:
            return thoughts[3]  # Analyze
        elif mbti_mix["Si"] > 0.7:
            return thoughts[1]  # Learn
        elif mbti_mix["Fe"] > 0.7:
            return thoughts[4]  # Help
        else:
            return thoughts[0]  # Goals
    
    def _extract_assumptions(self, proposal: str) -> List[str]:
        """Extract implicit assumptions from a proposal."""
        assumptions = []
        
        # Simple assumption extraction
        if "should" in proposal.lower():
            assumptions.append("This action is beneficial")
        if "maybe" in proposal.lower():
            assumptions.append("This is uncertain")
        if "wonder" in proposal.lower():
            assumptions.append("I don't have enough information")
        if "think" in proposal.lower():
            assumptions.append("Analysis is needed")
        
        return assumptions if assumptions else ["No specific assumptions identified"]
    
    def _evaluate_proposal(self, generator_result: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a proposal using MBTI functions."""
        try:
            proposal = generator_result["proposal"]
            mbti_mix = generator_result["mbti_mix"]
            
            # Score different aspects
            logic_score = self._score_logic(proposal, mbti_mix["Ti"])
            plausibility_score = self._score_plausibility(proposal, mbti_mix["Si"])
            social_score = self._score_social_impact(proposal, mbti_mix["Fe"])
            utility_score = self._score_utility(proposal, mbti_mix["Te"])
            
            # Generate objections
            objections = self._generate_objections(proposal, logic_score, plausibility_score, social_score, utility_score)
            
            return {
                "checks": {
                    "logic_Ti": logic_score,
                    "plausibility_Si": plausibility_score,
                    "social_Fe": social_score,
                    "utility_Te": utility_score
                },
                "objections": objections,
                "overall_score": (logic_score + plausibility_score + social_score + utility_score) / 4
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating proposal: {e}")
            return {
                "checks": {"logic_Ti": 0.5, "plausibility_Si": 0.5, "social_Fe": 0.5, "utility_Te": 0.5},
                "objections": ["Evaluation error occurred"],
                "overall_score": 0.5
            }
    
    def _score_logic(self, proposal: str, ti_strength: float) -> float:
        """Score logical coherence of a proposal."""
        # Simple logic scoring
        logic_indicators = ["because", "therefore", "since", "if", "then", "logical", "reason"]
        logic_count = sum(1 for indicator in logic_indicators if indicator in proposal.lower())
        
        base_score = min(0.8, logic_count * 0.2)
        return min(1.0, base_score * ti_strength)
    
    def _score_plausibility(self, proposal: str, si_strength: float) -> float:
        """Score plausibility based on experience and grounding."""
        # Simple plausibility scoring
        grounding_indicators = ["experience", "remember", "know", "familiar", "usual", "normal"]
        grounding_count = sum(1 for indicator in grounding_indicators if indicator in proposal.lower())
        
        base_score = min(0.8, grounding_count * 0.2)
        return min(1.0, base_score * si_strength)
    
    def _score_social_impact(self, proposal: str, fe_strength: float) -> float:
        """Score social impact and appropriateness."""
        # Simple social impact scoring
        social_indicators = ["others", "people", "help", "support", "consider", "impact"]
        social_count = sum(1 for indicator in social_indicators if indicator in proposal.lower())
        
        base_score = min(0.8, social_count * 0.2)
        return min(1.0, base_score * fe_strength)
    
    def _score_utility(self, proposal: str, te_strength: float) -> float:
        """Score utility and actionability."""
        try:
            # Simple utility scoring
            action_indicators = ["should", "will", "can", "able", "action", "do", "make"]
            action_count = sum(1 for indicator in action_indicators if indicator in proposal.lower())
            
            base_score = min(0.8, action_count * 0.2)
            return min(1.0, base_score * te_strength)
        except Exception as e:
            self.logger.error(f"Error in utility scoring: {e}")
            return 0.5
    
    def _generate_objections(self, proposal: str, logic_score: float, plausibility_score: float, 
                           social_score: float, utility_score: float) -> List[str]:
        """Generate objections based on low scores."""
        objections = []
        
        if logic_score < 0.4:
            objections.append("This lacks logical reasoning")
        if plausibility_score < 0.4:
            objections.append("This seems unrealistic")
        if social_score < 0.4:
            objections.append("This might affect others negatively")
        if utility_score < 0.4:
            objections.append("This may not be actionable")
        
        return objections if objections else ["No major objections"]
    
    def _maybe_reframe(self, generator_result: Dict[str, Any], evaluator_result: Dict[str, Any], 
                      state: Dict[str, Any]) -> Dict[str, Any]:
        """Apply advanced cognitive reframing with ML-based distortion detection and personalized strategies."""
        try:
            proposal = generator_result["proposal"]
            
            # Advanced distortion detection with context awareness
            distortion_analysis = self._advanced_distortion_detection(proposal, state)
            
            if distortion_analysis["distortions_found"]:
                # Apply personalized reframing based on MBTI and learning history
                reframed_result = self._apply_personalized_reframing(
                    proposal, 
                    distortion_analysis, 
                    state
                )
                
                # Update evaluator scores if reframe was applied
                evaluator_result = self._evaluate_proposal(
                    {**generator_result, "proposal": reframed_result["reframed_thought"]}, 
                    state
                )
                
                # Update learning history
                self._update_reframing_history(distortion_analysis, reframed_result, state)
                self.stats["reframes"] += 1
                
                return {
                    "generator": {**generator_result, "proposal": reframed_result["reframed_thought"]},
                    "evaluator": evaluator_result,
                    "reframe_applied": True,
                    "reframe_type": distortion_analysis["primary_distortion"],
                    "reframe_confidence": reframed_result["confidence"],
                    "reframe_technique": reframed_result["technique_used"]
                }
            else:
                return {
                    "generator": generator_result,
                    "evaluator": evaluator_result,
                    "reframe_applied": False,
                    "reframe_type": None
                }
            
        except Exception as e:
            self.logger.error(f"Error in advanced reframing: {e}")
            return {
                "generator": generator_result,
                "evaluator": evaluator_result,
                "reframe_applied": False,
                "reframe_type": None
            }
    
    def _apply_reframe(self, proposal: str, distortion_type: str) -> str:
        """Apply cognitive reframing to correct distortions."""
        reframe_patterns = {
            "catastrophizing": {
                "worst": "challenging",
                "disaster": "difficulty",
                "terrible": "unpleasant",
                "awful": "difficult"
            },
            "mind_reading": {
                "thinks": "might think",
                "believes": "might believe",
                "knows": "might know",
                "assumes": "might assume"
            },
            "all_or_nothing": {
                "always": "often",
                "never": "rarely",
                "everyone": "many people",
                "nobody": "few people"
            },
            "overgeneralization": {
                "always": "sometimes",
                "never": "rarely",
                "everyone": "some people",
                "nobody": "few people"
            },
            "emotional_reasoning": {
                "feel": "think",
                "feeling": "thinking",
                "emotion": "reason"
            },
            "should_statements": {
                "should": "could",
                "must": "might",
                "ought": "could",
                "have to": "could"
            }
        }
        
        reframed = proposal
        patterns = reframe_patterns.get(distortion_type, {})
        
        for old, new in patterns.items():
            reframed = reframed.replace(old, new)
        
        return reframed
    
    def _audit(self, generator_result: Dict[str, Any], evaluator_result: Dict[str, Any], 
              state: Dict[str, Any]) -> Dict[str, Any]:
        """Audit the thought and decide on broadcast/revise/discard."""
        try:
            # Calculate confidence based on evaluator scores
            scores = evaluator_result["checks"]
            confidence = sum(scores.values()) / len(scores)
            
            # Get current affect and NEUCOGAR
            affect = state["affect"]
            neucogar = state["neucogar"]
            
            # Check safety conditions
            safety_triggered = self._check_safety_conditions(affect, neucogar)
            
            # Make decision
            decision = self._make_decision(confidence, evaluator_result["overall_score"], 
                                         safety_triggered, affect, neucogar)
            
            return {
                "affect": affect,
                "neucogar": neucogar,
                "confidence": confidence,
                "decision": decision.value,
                "safety_triggered": safety_triggered
            }
            
        except Exception as e:
            self.logger.error(f"Error in audit: {e}")
            return {
                "affect": {"primary": "neutral", "valence": 0.0, "arousal": 0.0},
                "neucogar": {"dopamine": 0.5, "serotonin": 0.5, "noradrenaline": 0.5},
                "confidence": 0.5,
                "decision": DecisionType.DISCARD.value,
                "safety_triggered": False
            }
    
    def _check_safety_conditions(self, affect: Dict[str, Any], neucogar: Dict[str, float]) -> bool:
        """Check if safety conditions are triggered."""
        # Check for high NE and negative valence
        if (neucogar.get("noradrenaline", 0.0) > self.ne_threshold and 
            affect.get("valence", 0.0) < self.negative_valence_threshold):
            return True
        
        # Check for repeated negative thoughts
        recent_turns = self.current_chain[-self.stability_turns_threshold:] if self.current_chain else []
        negative_count = sum(1 for turn in recent_turns 
                           if turn.auditor["affect"]["valence"] < self.negative_valence_threshold)
        
        if negative_count >= self.stability_turns_threshold:
            return True
        
        return False
    
    def _make_decision(self, confidence: float, overall_score: float, safety_triggered: bool,
                      affect: Dict[str, Any], neucogar: Dict[str, float]) -> DecisionType:
        """Make decision on broadcast/revise/discard."""
        # Safety override
        if safety_triggered:
            self.stats["safety_triggers"] += 1
            return DecisionType.DISCARD
        
        # High confidence and score -> broadcast
        if confidence > 0.7 and overall_score > 0.6:
            return DecisionType.BROADCAST
        
        # Medium confidence and score -> revise
        elif confidence > 0.4 and overall_score > 0.4:
            return DecisionType.REVISE
        
        # Low scores -> discard
        else:
            return DecisionType.DISCARD
    
    def _log_inner_turn(self, turn: InnerTurn):
        """Log an inner thought turn."""
        self.current_chain.append(turn)
        
        # Keep only recent turns in memory
        if len(self.current_chain) > 20:
            self.current_chain = self.current_chain[-20:]
        
        self.logger.info(f"Inner turn {turn.turn_id}: {turn.generator['proposal'][:50]}... "
                        f"(Decision: {turn.auditor['decision']})")
    
    def _broadcast_to_gwt(self, turn: InnerTurn):
        """Broadcast thought to global workspace."""
        self.broadcast_queue.append(turn)
        self.logger.info(f"Broadcasting thought: {turn.generator['proposal']}")
    
    def _discard_thought(self, turn: InnerTurn):
        """Discard thought (keep subconscious)."""
        self.discard_history.append(turn)
        
        # Keep only recent discards
        if len(self.discard_history) > 50:
            self.discard_history = self.discard_history[-50:]
    
    def should_reflect(self) -> bool:
        """Determine if inner reflection should be triggered."""
        # This would integrate with CARL's cognitive state
        # For now, return True occasionally
        return len(self.current_chain) == 0 or len(self.current_chain) % 5 == 0
    
    def choose_lane_by_neucogar(self, neucogar: Dict[str, float]) -> ThoughtMode:
        """Choose thought lane based on NEUCOGAR state."""
        # High NE -> automatic (vigilance)
        if neucogar.get("noradrenaline", 0.0) > 0.7:
            return ThoughtMode.AUTOMATIC
        
        # High 5-HT -> deliberate (calm)
        if neucogar.get("serotonin", 0.0) > 0.7:
            return ThoughtMode.DELIBERATE
        
        # High DA -> automatic (exploratory)
        if neucogar.get("dopamine", 0.0) > 0.7:
            return ThoughtMode.AUTOMATIC
        
        # Default to automatic
        return ThoughtMode.AUTOMATIC
    
    def get_broadcast_queue(self) -> List[Dict[str, Any]]:
        """Get thoughts ready for global workspace."""
        return [asdict(turn) for turn in self.broadcast_queue]
    
    def clear_broadcast_queue(self):
        """Clear the broadcast queue after processing."""
        self.broadcast_queue = []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            **self.stats,
            "current_chain_length": len(self.current_chain),
            "broadcast_queue_length": len(self.broadcast_queue),
            "discard_history_length": len(self.discard_history)
        }
    
    def trigger_soothing_protocol(self):
        """Trigger soothing protocol for safety conditions."""
        self.logger.info("🔵 Triggering soothing protocol - high stress detected")
        # This would integrate with CARL's physical systems
        # For now, just log the event
        return {
            "action": "soothing_protocol",
            "breathing": "slow_deep_breaths",
            "eye_expression": "calm",
            "tts_prosody": "softer"
        }
    
    def _advanced_distortion_detection(self, thought_text: str, state: Dict) -> Dict:
        """
        Advanced ML-based distortion detection with context awareness.
        
        Args:
            thought_text: The thought to analyze
            state: Current cognitive state
            
        Returns:
            Dictionary with distortion analysis
        """
        try:
            thought_lower = thought_text.lower()
            detected_distortions = []
            distortion_scores = {}
            
            # Analyze each distortion type with multiple indicators
            for distortion_type, indicators in self.cognitive_distortions.items():
                score = 0.0
                evidence = []
                
                # Pattern matching
                pattern_matches = sum(1 for pattern in indicators["patterns"] if pattern in thought_lower)
                if pattern_matches > 0:
                    score += pattern_matches * 0.3
                    evidence.extend([p for p in indicators["patterns"] if p in thought_lower])
                
                # Severity/certainty indicators
                severity_matches = sum(1 for indicator in indicators.get("severity_indicators", []) if indicator in thought_lower)
                if severity_matches > 0:
                    score += severity_matches * 0.2
                    evidence.extend([s for s in indicators.get("severity_indicators", []) if s in thought_lower])
                
                # Context clues
                context_matches = sum(1 for clue in indicators.get("context_clues", []) if clue in thought_lower)
                if context_matches > 0:
                    score += context_matches * 0.1
                    evidence.extend([c for c in indicators.get("context_clues", []) if c in thought_lower])
                
                # Context-aware weighting
                context = self._identify_thought_context(thought_text, state)
                if context in self.context_patterns:
                    if distortion_type in self.context_patterns[context]["distortions"]:
                        score *= 1.5  # Boost score for context-relevant distortions
                
                if score > 0.3:  # Threshold for distortion detection
                    detected_distortions.append(distortion_type)
                    distortion_scores[distortion_type] = {
                        "score": score,
                        "evidence": evidence,
                        "confidence": min(score, 1.0)
                    }
            
            # Determine primary distortion (highest score)
            primary_distortion = None
            if detected_distortions:
                primary_distortion = max(distortion_scores.keys(), 
                                       key=lambda x: distortion_scores[x]["score"])
            
            return {
                "distortions_found": len(detected_distortions) > 0,
                "detected_distortions": detected_distortions,
                "distortion_scores": distortion_scores,
                "primary_distortion": primary_distortion,
                "context": self._identify_thought_context(thought_text, state),
                "severity": max([s["score"] for s in distortion_scores.values()]) if distortion_scores else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Error in advanced distortion detection: {e}")
            return {"distortions_found": False, "detected_distortions": [], "distortion_scores": {}}
    
    def _apply_personalized_reframing(self, thought_text: str, distortion_analysis: Dict, state: Dict) -> Dict:
        """
        Apply personalized reframing based on MBTI type and learning history.
        
        Args:
            thought_text: Original thought
            distortion_analysis: Results from distortion detection
            state: Current cognitive state
            
        Returns:
            Dictionary with reframing results
        """
        try:
            personality_type = self.personality_type
            primary_distortion = distortion_analysis["primary_distortion"]
            context = distortion_analysis["context"]
            
            # Get personalized strategy
            strategy = self.reframing_strategies.get(personality_type, self.reframing_strategies["INTP"])
            
            # Select most effective technique based on history
            technique = self._select_optimal_technique(primary_distortion, context, strategy, state)
            
            # Apply the reframing technique
            reframed_thought = self._execute_reframing_technique(thought_text, technique, distortion_analysis, state)
            
            return {
                "reframed_thought": reframed_thought,
                "technique_used": technique,
                "confidence": self._calculate_reframe_confidence(technique, context, state),
                "original_distortion": primary_distortion
            }
            
        except Exception as e:
            self.logger.error(f"Error in personalized reframing: {e}")
            return {
                "reframed_thought": thought_text,
                "technique_used": "fallback",
                "confidence": 0.3,
                "original_distortion": None
            }
    
    def _identify_thought_context(self, thought_text: str, state: Dict) -> str:
        """
        Identify the context of the thought for context-aware reframing.
        
        Args:
            thought_text: The thought to analyze
            state: Current cognitive state
            
        Returns:
            Context category string
        """
        try:
            thought_lower = thought_text.lower()
            
            # Social context indicators
            social_indicators = ["they", "them", "other people", "everyone", "someone", "friend", "family"]
            if any(indicator in thought_lower for indicator in social_indicators):
                return "social_situations"
            
            # Work/performance context indicators
            work_indicators = ["work", "job", "task", "project", "performance", "achievement", "success", "failure"]
            if any(indicator in thought_lower for indicator in work_indicators):
                return "work_performance"
            
            # Personal goals context indicators
            goal_indicators = ["goal", "plan", "future", "want", "need", "hope", "dream", "aspiration"]
            if any(indicator in thought_lower for indicator in goal_indicators):
                return "personal_goals"
            
            # Relationship context indicators
            relationship_indicators = ["relationship", "love", "partner", "romance", "connection", "intimacy"]
            if any(indicator in thought_lower for indicator in relationship_indicators):
                return "relationships"
            
            # Default to personal goals if no specific context identified
            return "personal_goals"
            
        except Exception as e:
            self.logger.error(f"Error identifying thought context: {e}")
            return "personal_goals"
    
    def _select_optimal_technique(self, distortion_type: str, context: str, strategy: Dict, state: Dict) -> str:
        """
        Select the most effective reframing technique based on learning history.
        
        Args:
            distortion_type: Type of cognitive distortion
            context: Thought context
            strategy: Personality-based strategy preferences
            state: Current cognitive state
            
        Returns:
            Selected technique name
        """
        try:
            # Get context-specific reframing focus
            context_focus = self.context_patterns.get(context, {}).get("reframing_focus", [])
            
            # Filter techniques by personality preferences
            preferred_techniques = [t for t in strategy["effective_techniques"] if t not in strategy["avoid_techniques"]]
            
            # Check learning history for effectiveness
            history_key = f"{distortion_type}_{context}"
            if history_key in self.reframing_history["context_effectiveness"]:
                effectiveness = self.reframing_history["context_effectiveness"][history_key]
                # Select technique with highest effectiveness
                best_technique = max(effectiveness.keys(), key=lambda x: effectiveness[x])
                if best_technique in preferred_techniques:
                    return best_technique
            
            # Fallback to first preferred technique
            if preferred_techniques:
                return preferred_techniques[0]
            
            # Ultimate fallback
            return "reality_testing"
            
        except Exception as e:
            self.logger.error(f"Error selecting optimal technique: {e}")
            return "reality_testing"
    
    def _execute_reframing_technique(self, thought_text: str, technique: str, distortion_analysis: Dict, state: Dict) -> str:
        """
        Execute the selected reframing technique.
        
        Args:
            thought_text: Original thought
            technique: Selected reframing technique
            distortion_analysis: Distortion analysis results
            state: Current cognitive state
            
        Returns:
            Reframed thought
        """
        try:
            if technique == "reality_testing":
                return self._reality_testing_reframe(thought_text, distortion_analysis)
            elif technique == "perspective_shifting":
                return self._perspective_shifting_reframe(thought_text, distortion_analysis)
            elif technique == "data_gathering":
                return self._data_gathering_reframe(thought_text, distortion_analysis)
            elif technique == "goal_oriented_reframing":
                return self._goal_oriented_reframe(thought_text, distortion_analysis)
            elif technique == "alternative_perspectives":
                return self._alternative_perspectives_reframe(thought_text, distortion_analysis)
            elif technique == "solution_focus":
                return self._solution_focus_reframe(thought_text, distortion_analysis)
            else:
                return self._reality_testing_reframe(thought_text, distortion_analysis)
                
        except Exception as e:
            self.logger.error(f"Error executing reframing technique: {e}")
            return thought_text
    
    def _reality_testing_reframe(self, thought_text: str, distortion_analysis: Dict) -> str:
        """Apply reality testing reframing technique."""
        try:
            primary_distortion = distortion_analysis["primary_distortion"]
            
            if primary_distortion == "catastrophizing":
                return f"While this situation is challenging, let me consider the actual evidence and realistic outcomes rather than the worst-case scenario."
            elif primary_distortion == "mind_reading":
                return f"I'm making assumptions about what others think. Let me focus on what I actually know and consider asking for clarification."
            elif primary_distortion == "all_or_nothing":
                return f"Life is rarely all-or-nothing. Let me look at the nuances and shades of gray in this situation."
            elif primary_distortion == "overgeneralization":
                return f"One experience doesn't define everything. Let me consider the specific circumstances rather than making broad generalizations."
            elif primary_distortion == "emotional_reasoning":
                return f"While my feelings are valid, they don't necessarily reflect objective reality. Let me separate feelings from facts."
            elif primary_distortion == "should_statements":
                return f"Instead of focusing on what I 'should' do, let me consider what would be most helpful and realistic in this situation."
            elif primary_distortion == "personalization":
                return f"I'm taking responsibility for things that may not be entirely within my control. Let me consider all the factors involved."
            elif primary_distortion == "fortune_telling":
                return f"I can't predict the future with certainty. Let me focus on what I can control and influence in the present."
            else:
                return f"Let me step back and examine this thought more objectively, considering the evidence and alternative perspectives."
                
        except Exception as e:
            self.logger.error(f"Error in reality testing reframe: {e}")
            return thought_text
    
    def _perspective_shifting_reframe(self, thought_text: str, distortion_analysis: Dict) -> str:
        """Apply perspective shifting reframing technique."""
        try:
            return f"Let me consider this situation from different angles. What would I tell a friend in this situation? What would a neutral observer see?"
        except Exception as e:
            self.logger.error(f"Error in perspective shifting reframe: {e}")
            return thought_text
    
    def _data_gathering_reframe(self, thought_text: str, distortion_analysis: Dict) -> str:
        """Apply data gathering reframing technique."""
        try:
            return f"Let me gather more information before drawing conclusions. What facts do I actually have? What questions could help me understand this better?"
        except Exception as e:
            self.logger.error(f"Error in data gathering reframe: {e}")
            return thought_text
    
    def _goal_oriented_reframe(self, thought_text: str, distortion_analysis: Dict) -> str:
        """Apply goal-oriented reframing technique."""
        try:
            return f"How can I use this situation to move toward my goals? What opportunities for growth or learning does this present?"
        except Exception as e:
            self.logger.error(f"Error in goal-oriented reframe: {e}")
            return thought_text
    
    def _alternative_perspectives_reframe(self, thought_text: str, distortion_analysis: Dict) -> str:
        """Apply alternative perspectives reframing technique."""
        try:
            return f"What other ways could I interpret this situation? What possibilities am I not considering?"
        except Exception as e:
            self.logger.error(f"Error in alternative perspectives reframe: {e}")
            return thought_text
    
    def _solution_focus_reframe(self, thought_text: str, distortion_analysis: Dict) -> str:
        """Apply solution-focused reframing technique."""
        try:
            return f"Instead of focusing on the problem, let me think about what solutions or next steps I can take."
        except Exception as e:
            self.logger.error(f"Error in solution focus reframe: {e}")
            return thought_text
    
    def _calculate_reframe_confidence(self, technique: str, context: str, state: Dict) -> float:
        """Calculate confidence in the reframing technique."""
        try:
            base_confidence = 0.7
            
            # Adjust based on learning history
            history_key = f"{technique}_{context}"
            if history_key in self.reframing_history["successful_techniques"]:
                success_rate = self.reframing_history["successful_techniques"][history_key]
                base_confidence += success_rate * 0.3
            
            return min(base_confidence, 1.0)
        except Exception as e:
            self.logger.error(f"Error calculating reframe confidence: {e}")
            return 0.5
    
    def _update_reframing_history(self, distortion_analysis: Dict, reframed_result: Dict, state: Dict):
        """Update learning history for personalized reframing."""
        try:
            technique = reframed_result["technique_used"]
            context = distortion_analysis["context"]
            distortion_type = distortion_analysis["primary_distortion"]
            
            # Update technique effectiveness
            history_key = f"{distortion_type}_{context}"
            if history_key not in self.reframing_history["context_effectiveness"]:
                self.reframing_history["context_effectiveness"][history_key] = {}
            
            if technique not in self.reframing_history["context_effectiveness"][history_key]:
                self.reframing_history["context_effectiveness"][history_key][technique] = 0.0
            
            # Increment effectiveness (will be updated based on outcomes)
            self.reframing_history["context_effectiveness"][history_key][technique] += 0.1
            
        except Exception as e:
            self.logger.error(f"Error updating reframing history: {e}")
