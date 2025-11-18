#!/usr/bin/env python3
"""
Humor System with Joke/Laughter Pipeline

Implements joke selection, delivery, incongruity evaluation, 
transient dopamine/endorphin spikes, and laugh() function.
"""

import json
import logging
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import os

class HumorType(Enum):
    """Types of humor for categorization."""
    PUN = "pun"
    WORDPLAY = "wordplay"
    INCONGUITY = "incongruity"
    OBSERVATIONAL = "observational"
    SITUATIONAL = "situational"
    DAD_JOKE = "dad_joke"

@dataclass
class Joke:
    """Represents a joke with metadata."""
    setup: str
    punchline: str
    humor_type: HumorType
    target_audience: str = "general"
    complexity: float = 0.5  # 0.0 to 1.0
    success_rate: float = 0.5  # Historical success rate
    tags: List[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class HumorResponse:
    """Represents a humor response with evaluation."""
    joke: Joke
    delivery_time: str
    audience_reaction: Optional[str] = None
    incongruity_score: float = 0.0
    dopamine_spike: float = 0.0
    endorphin_spike: float = 0.0
    laughter_triggered: bool = False
    success: bool = False

@dataclass
class NeurotransmitterState:
    """Represents neurotransmitter levels."""
    dopamine: float = 0.5  # 0.0 to 1.0
    endorphins: float = 0.5  # 0.0 to 1.0
    serotonin: float = 0.5  # 0.0 to 1.0
    norepinephrine: float = 0.5  # 0.0 to 1.0
    last_updated: str = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()

class HumorSystem:
    """
    Comprehensive humor system with joke/laughter pipeline.
    """
    
    def __init__(self, 
                 neucogar_engine=None,
                 api_client=None,
                 ezrobot=None):
        self.logger = logging.getLogger(__name__)
        self.neucogar_engine = neucogar_engine
        self.api_client = api_client
        self.ezrobot = ezrobot
        
        self.jokes: List[Joke] = []
        self.humor_responses: List[HumorResponse] = []
        self.neurotransmitter_state = NeurotransmitterState()
        
        self.dopamine_threshold = 0.1
        self.serotonin_baseline = 0.5
        self.laughter_cooldown = 30.0  # seconds
        self.last_laughter_time = 0.0
        
        self._load_jokes()
        self._load_neurotransmitter_state()
    
    def _load_jokes(self):
        """Load jokes from file or create defaults."""
        try:
            with open("humor/jokes.json", 'r') as f:
                jokes_data = json.load(f)
                for joke_data in jokes_data:
                    joke = Joke(
                        setup=joke_data["setup"],
                        punchline=joke_data["punchline"],
                        humor_type=HumorType(joke_data["humor_type"]),
                        target_audience=joke_data.get("target_audience", "general"),
                        complexity=joke_data.get("complexity", 0.5),
                        success_rate=joke_data.get("success_rate", 0.5),
                        tags=joke_data.get("tags", []),
                        created_at=joke_data.get("created_at")
                    )
                    self.jokes.append(joke)
            self.logger.info(f"Loaded {len(self.jokes)} jokes from file")
        except FileNotFoundError:
            self.logger.info("No jokes file found, creating default jokes")
            self._create_default_jokes()
        except Exception as e:
            self.logger.error(f"Error loading jokes: {e}")
            self._create_default_jokes()
    
    def _create_default_jokes(self):
        """Create default jokes if none exist."""
        default_jokes = [
            Joke(
                setup="Why don't dinosaurs like fast food?",
                punchline="Because they can't catch it!",
                humor_type=HumorType.INCONGUITY,
                tags=["dinosaurs", "food", "puns"]
            ),
            Joke(
                setup="What do you call a dinosaur that crashes his car?",
                punchline="Tyrannosaurus wrecks!",
                humor_type=HumorType.WORDPLAY,
                tags=["dinosaurs", "cars", "wordplay"]
            ),
            Joke(
                setup="Why did the dinosaur go to the doctor?",
                punchline="Because he had a bone to pick!",
                humor_type=HumorType.PUN,
                tags=["dinosaurs", "health", "puns"]
            ),
            Joke(
                setup="What's a dinosaur's favorite drink?",
                punchline="Jurassic Park!",
                humor_type=HumorType.WORDPLAY,
                tags=["dinosaurs", "drinks", "wordplay"]
            ),
            Joke(
                setup="Why did the dinosaur cross the road?",
                punchline="To get to the other side!",
                humor_type=HumorType.DAD_JOKE,
                tags=["dinosaurs", "roads", "classic"]
            ),
            Joke(
                setup="What do you call a robot that tells jokes?",
                punchline="A comedian-bot!",
                humor_type=HumorType.WORDPLAY,
                tags=["robots", "comedy", "wordplay"]
            ),
            Joke(
                setup="Why did the robot go to the library?",
                punchline="To check out some bytes!",
                humor_type=HumorType.PUN,
                tags=["robots", "libraries", "puns"]
            ),
            Joke(
                setup="What do robots do on their day off?",
                punchline="They recharge their batteries!",
                humor_type=HumorType.OBSERVATIONAL,
                tags=["robots", "leisure", "observational"]
            )
        ]
        
        self.jokes.extend(default_jokes)
        self._save_jokes()
    
    def _save_jokes(self):
        """Save jokes to file."""
        try:
            os.makedirs("humor", exist_ok=True)
            jokes_data = []
            for joke in self.jokes:
                joke_dict = asdict(joke)
                joke_dict["humor_type"] = joke.humor_type.value  # Convert enum to string
                jokes_data.append(joke_dict)
            with open("humor/jokes.json", 'w') as f:
                json.dump(jokes_data, f, indent=2)
            self.logger.info(f"Saved {len(self.jokes)} jokes to file")
        except Exception as e:
            self.logger.error(f"Error saving jokes: {e}")
    
    def _load_neurotransmitter_state(self):
        """Load neurotransmitter state from file."""
        try:
            with open("humor/neurotransmitter_state.json", 'r') as f:
                state_data = json.load(f)
                self.neurotransmitter_state = NeurotransmitterState(
                    dopamine=state_data.get("dopamine", 0.5),
                    endorphins=state_data.get("endorphins", 0.5),
                    serotonin=state_data.get("serotonin", 0.5),
                    norepinephrine=state_data.get("norepinephrine", 0.5),
                    last_updated=state_data.get("last_updated")
                )
        except FileNotFoundError:
            self.logger.info("No neurotransmitter state file found, using defaults")
        except Exception as e:
            self.logger.error(f"Error loading neurotransmitter state: {e}")
    
    def _save_neurotransmitter_state(self):
        """Save neurotransmitter state to file."""
        try:
            os.makedirs("humor", exist_ok=True)
            state_data = asdict(self.neurotransmitter_state)
            with open("humor/neurotransmitter_state.json", 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving neurotransmitter state: {e}")

    def detect_user_humor(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Optional[HumorResponse]:
        """
        Detect humor in user input and trigger appropriate responses.
        
        Args:
            user_input: User's text input
            context: Additional context information
            
        Returns:
            HumorResponse if humor detected, None otherwise
        """
        try:
            user_input_lower = user_input.lower().strip()
            
            # Check for known joke setups and punchlines
            joke_detected = self._detect_known_jokes(user_input_lower)
            if joke_detected:
                return self._handle_detected_joke(joke_detected, context)
            
            # Check for incongruity cues
            incongruity_score = self._detect_incongruity_cues(user_input_lower)
            if incongruity_score > 0.6:
                return self._handle_incongruity_humor(incongruity_score, user_input, context)
            
            # Check for humor keywords
            humor_keywords = self._detect_humor_keywords(user_input_lower)
            if humor_keywords:
                return self._handle_humor_keywords(humor_keywords, user_input, context)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting user humor: {e}")
            return None

    def _detect_known_jokes(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Detect known joke setups and punchlines."""
        # Known joke patterns (setup -> punchline)
        known_jokes = {
            "what's a cat's favorite jacket": "a purr coat",
            "what do you call a bear with no teeth": "a gummy bear",
            "why don't scientists trust atoms": "because they make up everything",
            "what do you call a fake noodle": "an impasta",
            "why did the scarecrow win an award": "because he was outstanding in his field",
            "what do you call a can opener that doesn't work": "a can't opener",
            "what do you call a bear with no ears": "b",
            "what do you call a fish wearing a bowtie": "so-fish-ticated",
            "what do you call a dinosaur that crashes his car": "tyrannosaurus wrecks",
            "what do you call a sleeping bull": "a bulldozer"
        }
        
        # Check if user input matches any known punchline
        for setup, punchline in known_jokes.items():
            if punchline.lower() in user_input or user_input in punchline.lower():
                return {
                    "type": "known_joke",
                    "setup": setup,
                    "punchline": punchline,
                    "confidence": 0.9
                }
        
        return None

    def _detect_incongruity_cues(self, user_input: str) -> float:
        """Detect incongruity-based humor cues."""
        score = 0.0
        
        # Incongruity cue words
        incongruity_cues = {
            "puns": ["pun", "wordplay", "play on words", "double meaning"],
            "surprise": ["unexpected", "surprise", "twist", "irony", "paradox"],
            "absurdity": ["ridiculous", "absurd", "nonsense", "silly", "crazy"],
            "word_substitution": ["instead of", "rather than", "substitute", "replace"]
        }
        
        for category, cues in incongruity_cues.items():
            for cue in cues:
                if cue in user_input:
                    score += 0.2
        
        # Check for question-answer patterns that might be jokes
        if "?" in user_input and len(user_input.split()) < 10:
            score += 0.1
        
        return min(score, 1.0)

    def _detect_humor_keywords(self, user_input: str) -> List[str]:
        """Detect humor-related keywords."""
        humor_keywords = [
            "joke", "funny", "laugh", "humor", "hilarious", "amusing", "comedy",
            "wit", "clever", "smart", "genius", "brilliant", "perfect"
        ]
        
        detected = []
        for keyword in humor_keywords:
            if keyword in user_input:
                detected.append(keyword)
        
        return detected

    def _handle_detected_joke(self, joke_info: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> HumorResponse:
        """Handle detected known joke."""
        # Create a joke object
        joke = Joke(
            setup=joke_info["setup"],
            punchline=joke_info["punchline"],
            humor_type=HumorType.DAD_JOKE,
            complexity=0.3,
            success_rate=0.8
        )
        
        # Trigger neurotransmitter spikes
        dopamine_spike, endorphin_spike = self.trigger_neurotransmitter_spikes(0.8)
        
        # Determine if laughter should be triggered
        should_laugh = self.should_laugh(dopamine_spike, endorphin_spike)
        
        # Execute laughter if appropriate
        laughter_triggered = False
        if should_laugh:
            laughter_triggered = self.laugh()
        
        # Create response
        response = HumorResponse(
            joke=joke,
            delivery_time=datetime.now().isoformat(),
            incongruity_score=0.8,
            dopamine_spike=dopamine_spike,
            endorphin_spike=endorphin_spike,
            laughter_triggered=laughter_triggered,
            success=True
        )
        
        self.logger.info(f"Detected known joke: {joke.setup} -> {joke.punchline}")
        return response

    def _handle_incongruity_humor(self, incongruity_score: float, user_input: str, context: Optional[Dict[str, Any]] = None) -> HumorResponse:
        """Handle detected incongruity humor."""
        # Create a joke object from user input
        joke = Joke(
            setup="User input",
            punchline=user_input,
            humor_type=HumorType.INCONGUITY,
            complexity=0.6,
            success_rate=0.7
        )
        
        # Trigger neurotransmitter spikes
        dopamine_spike, endorphin_spike = self.trigger_neurotransmitter_spikes(incongruity_score)
        
        # Determine if laughter should be triggered
        should_laugh = self.should_laugh(dopamine_spike, endorphin_spike)
        
        # Execute laughter if appropriate
        laughter_triggered = False
        if should_laugh:
            laughter_triggered = self.laugh()
        
        # Create response
        response = HumorResponse(
            joke=joke,
            delivery_time=datetime.now().isoformat(),
            incongruity_score=incongruity_score,
            dopamine_spike=dopamine_spike,
            endorphin_spike=endorphin_spike,
            laughter_triggered=laughter_triggered,
            success=incongruity_score > 0.5
        )
        
        self.logger.info(f"Detected incongruity humor: {user_input} (score: {incongruity_score:.2f})")
        return response

    def _handle_humor_keywords(self, keywords: List[str], user_input: str, context: Optional[Dict[str, Any]] = None) -> HumorResponse:
        """Handle detected humor keywords."""
        # Create a joke object from user input
        joke = Joke(
            setup="User input",
            punchline=user_input,
            humor_type=HumorType.OBSERVATIONAL,
            complexity=0.4,
            success_rate=0.6
        )
        
        # Trigger moderate neurotransmitter spikes
        dopamine_spike, endorphin_spike = self.trigger_neurotransmitter_spikes(0.5)
        
        # Determine if laughter should be triggered
        should_laugh = self.should_laugh(dopamine_spike, endorphin_spike)
        
        # Execute laughter if appropriate
        laughter_triggered = False
        if should_laugh:
            laughter_triggered = self.laugh()
        
        # Create response
        response = HumorResponse(
            joke=joke,
            delivery_time=datetime.now().isoformat(),
            incongruity_score=0.5,
            dopamine_spike=dopamine_spike,
            endorphin_spike=endorphin_spike,
            laughter_triggered=laughter_triggered,
            success=True
        )
        
        self.logger.info(f"Detected humor keywords: {keywords} in '{user_input}'")
        return response
    
    def select_joke(self, context: Optional[Dict[str, Any]] = None) -> Optional[Joke]:
        """Select an appropriate joke based on context."""
        if not self.jokes:
            return None
        
        # Filter jokes based on context
        available_jokes = self.jokes.copy()
        
        if context:
            # Filter by tags if context provides keywords
            keywords = context.get("keywords", [])
            if keywords:
                available_jokes = [
                    joke for joke in available_jokes
                    if any(keyword.lower() in tag.lower() for tag in joke.tags for keyword in keywords)
                ]
            
            # Filter by complexity if specified
            target_complexity = context.get("complexity")
            if target_complexity is not None:
                available_jokes = [
                    joke for joke in available_jokes
                    if abs(joke.complexity - target_complexity) < 0.3
                ]
        
        if not available_jokes:
            available_jokes = self.jokes
        
        # Weight by success rate (prefer successful jokes)
        weights = [joke.success_rate for joke in available_jokes]
        total_weight = sum(weights)
        
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
            selected_joke = random.choices(available_jokes, weights=weights)[0]
        else:
            selected_joke = random.choice(available_jokes)
        
        return selected_joke
    
    def deliver_joke(self, joke: Joke, context: Optional[Dict[str, Any]] = None) -> str:
        """Deliver a joke with proper timing and delivery."""
        delivery = f"{joke.setup}\n\n...\n\n{joke.punchline}"
        
        # Log the delivery
        self.logger.info(f"Delivering joke: {joke.setup} -> {joke.punchline}")
        
        return delivery
    
    def evaluate_incongruity(self, joke: Joke, context: Optional[Dict[str, Any]] = None) -> float:
        """Evaluate the incongruity level of a joke (0.0 to 1.0)."""
        base_score = 0.5
        
        # Adjust based on humor type
        type_scores = {
            HumorType.PUN: 0.7,
            HumorType.WORDPLAY: 0.8,
            HumorType.INCONGUITY: 0.9,
            HumorType.OBSERVATIONAL: 0.6,
            HumorType.SITUATIONAL: 0.7,
            HumorType.DAD_JOKE: 0.4
        }
        
        base_score = type_scores.get(joke.humor_type, 0.5)
        
        # Adjust based on complexity
        complexity_factor = joke.complexity * 0.3
        
        # Adjust based on context relevance
        context_factor = 0.0
        if context and context.get("keywords"):
            keyword_matches = sum(
                1 for keyword in context["keywords"]
                for tag in joke.tags
                if keyword.lower() in tag.lower()
            )
            context_factor = min(keyword_matches * 0.1, 0.2)
        
        final_score = min(base_score + complexity_factor + context_factor, 1.0)
        
        return final_score
    
    def trigger_neurotransmitter_spikes(self, incongruity_score: float) -> Tuple[float, float]:
        """Trigger transient dopamine and endorphin spikes based on incongruity."""
        # Calculate spikes based on incongruity
        dopamine_spike = incongruity_score * 0.3  # Max 0.3 spike
        endorphin_spike = incongruity_score * 0.2  # Max 0.2 spike
        
        # Apply spikes to current levels
        current_dopamine = self.neurotransmitter_state.dopamine
        current_endorphins = self.neurotransmitter_state.endorphins
        
        new_dopamine = min(current_dopamine + dopamine_spike, 1.0)
        new_endorphins = min(current_endorphins + endorphin_spike, 1.0)
        
        # Update state
        self.neurotransmitter_state.dopamine = new_dopamine
        self.neurotransmitter_state.endorphins = new_endorphins
        self.neurotransmitter_state.last_updated = datetime.now().isoformat()
        
        # Update NEUCOGAR if available to trigger "amused" emotion
        if self.neucogar_engine:
            try:
                # Trigger amusement emotion in NEUCOGAR
                self.neucogar_engine.trigger_neurotransmitter_effect("dopamine", dopamine_spike, "humor_amusement")
                self.neucogar_engine.trigger_neurotransmitter_effect("endorphins", endorphin_spike, "humor_amusement")
                
                # Update emotional state to "amused"
                amusement_event = {
                    'event_type': 'humor',
                    'content': 'joke or humorous content',
                    'concepts': ['humor', 'amusement', 'laughter'],
                    'goals': ['entertainment', 'social_bonding'],
                    'needs': ['social', 'entertainment'],
                    'emotion': {'primary': 'happiness', 'sub': 'amused'}
                }
                self.neucogar_engine.update_from_event(amusement_event)
                
                self.logger.info(f"Amused emotion triggered in NEUCOGAR - DA: +{dopamine_spike:.3f}, Endorphins: +{endorphin_spike:.3f}")
                
            except Exception as e:
                self.logger.error(f"Error updating NEUCOGAR for humor: {e}")
        
        # Log the spikes
        self.logger.info(f"Neurotransmitter spikes - Dopamine: +{dopamine_spike:.3f}, Endorphins: +{endorphin_spike:.3f}")
        
        return dopamine_spike, endorphin_spike
    
    def should_laugh(self, dopamine_spike: float, endorphin_spike: float) -> bool:
        """Determine if laughter should be triggered."""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_laughter_time < self.laughter_cooldown:
            return False
        
        # Check thresholds
        if dopamine_spike >= self.dopamine_threshold and self.neurotransmitter_state.serotonin >= self.serotonin_baseline:
                return True
        
        return False
    
    def laugh(self) -> bool:
        """Execute laughter reaction: TTS chuckle + motion + eyes."""
        try:
            current_time = time.time()
            
            # Check cooldown
            if current_time - self.last_laughter_time < self.laughter_cooldown:
                self.logger.info("Laughter on cooldown")
                return False
            
            self.logger.info("Executing laughter reaction...")
            
            # TTS chuckle
            if self.api_client:
                try:
                    self.api_client.speak("Hehehe! *chuckles*")
                    self.logger.info("TTS chuckle delivered")
                except Exception as e:
                    self.logger.error(f"Error with TTS chuckle: {e}")
            
            # Motion
            if self.ezrobot:
                try:
                    # Use AutoPositionAction for laugh motion
                    self.ezrobot.AutoPositionAction("laugh_motion")
                    self.logger.info("Laugh motion executed")
                except Exception as e:
                    self.logger.error(f"Error with laugh motion: {e}")
            
            # Eyes
            if self.ezrobot:
                try:
                    self.ezrobot.eyes("joy")
                    self.logger.info("Joy eyes expression set")
                except Exception as e:
                    self.logger.error(f"Error with joy eyes: {e}")
            
            # Update last laughter time
            self.last_laughter_time = current_time
            
            self.logger.info("Laughter reaction completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in laugh function: {e}")
            return False
    
    def tell_joke(self, context: Optional[Dict[str, Any]] = None) -> HumorResponse:
        """Complete joke/laughter pipeline."""
        # Step 1: Select joke
        joke = self.select_joke(context)
        if not joke:
            self.logger.warning("No jokes available")
            return None
    
        # Step 2: Deliver joke
        delivery = self.deliver_joke(joke, context)
        
        # Step 3: Evaluate incongruity
        incongruity_score = self.evaluate_incongruity(joke, context)
        
        # Step 4: Trigger neurotransmitter spikes
        dopamine_spike, endorphin_spike = self.trigger_neurotransmitter_spikes(incongruity_score)
        
        # Step 5: Determine if laughter should be triggered
        should_laugh = self.should_laugh(dopamine_spike, endorphin_spike)
        
        # Step 6: Execute laughter if appropriate
        laughter_triggered = False
        if should_laugh:
            laughter_triggered = self.laugh()
        
        # Step 7: Create response record
        response = HumorResponse(
            joke=joke,
            delivery_time=datetime.now().isoformat(),
            incongruity_score=incongruity_score,
            dopamine_spike=dopamine_spike,
            endorphin_spike=endorphin_spike,
            laughter_triggered=laughter_triggered,
            success=incongruity_score > 0.5  # Simple success metric
        )
        
        # Step 8: Update joke success rate
        joke.success_rate = (joke.success_rate * 0.9) + (response.success * 0.1)
        
        # Step 9: Store joke in memory for future reference
        memory_id = self.store_joke_in_memory(joke, context)
        if memory_id:
            self.logger.info(f"Joke stored in memory with ID: {memory_id}")
        
        # Step 10: Save response and update files
        self.humor_responses.append(response)
        self._save_jokes()
        self._save_neurotransmitter_state()
        
        self.logger.info(f"Joke pipeline completed - Incongruity: {incongruity_score:.3f}, Laughter: {laughter_triggered}")
        
        return response
    
    def store_joke_in_memory(self, joke: Joke, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a joke in STM/episodic memory for future reference.
        
        Args:
            joke: The joke to store
            context: Additional context for the joke
            
        Returns:
            str: Memory ID of the stored joke
        """
        try:
            import os
            import json
            from datetime import datetime
            
            # Create memory data for the joke
            memory_data = {
                "id": f"joke_{int(time.time())}",
                "type": "humor_joke",
                "timestamp": datetime.now().isoformat(),
                "WHAT": f"Told joke: {joke.setup} -> {joke.punchline}",
                "WHERE": "Humor interaction",
                "WHY": "User requested a joke",
                "HOW": "Humor system delivery",
                "WHO": "Carl (telling joke)",
                "emotions": ["amusement", "happiness"],
                
                # Joke-specific data
                "joke_data": {
                    "setup": joke.setup,
                    "punchline": joke.punchline,
                    "humor_type": joke.humor_type.value,
                    "complexity": joke.complexity,
                    "success_rate": joke.success_rate,
                    "tags": joke.tags,
                    "created_at": joke.created_at
                },
                
                # Context information
                "context": context or {},
                
                # NEUCOGAR emotional state
                "neucogar_emotional_state": {
                    "primary": "amusement",
                    "intensity": 0.7,
                    "neuro_coordinates": {
                        "dopamine": 0.7,
                        "serotonin": 0.6,
                        "noradrenaline": 0.3
                    }
                }
            }
            
            # Save to STM (short-term memory)
            stm_dir = "memories"
            if not os.path.exists(stm_dir):
                os.makedirs(stm_dir, exist_ok=True)
            
            # Create filename with timestamp
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"joke_{joke.humor_type.value}_{timestamp_str}.json"
            filepath = os.path.join(stm_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Stored joke in memory: {filepath}")
            return memory_data["id"]
            
        except Exception as e:
            self.logger.error(f"Error storing joke in memory: {e}")
            return ""
    
    def check_joke_repeat_query(self, query: str) -> Optional[str]:
        """
        Check if the user is asking for a repeat joke and generate reflective response.
        
        Args:
            query: The user's query
            
        Returns:
            str: Reflective response if this is a repeat query, None otherwise
        """
        try:
            query_lower = query.lower()
            
            # Check for repeat joke patterns
            repeat_patterns = [
                'tell me that joke again',
                'repeat that joke',
                'say that joke again',
                'tell the same joke',
                'that joke was funny',
                'i liked that joke',
                'tell me another joke',
                'more jokes',
                'another joke'
            ]
            
            if any(pattern in query_lower for pattern in repeat_patterns):
                # Check if we have recent jokes in memory
                recent_jokes = self._get_recent_jokes_from_memory()
                
                if recent_jokes:
                    if 'another' in query_lower or 'more' in query_lower:
                        # User wants a new joke
                        return "That's great! I'm glad you enjoyed it. Let me tell you another one!"
                    else:
                        # User wants the same joke repeated
                        latest_joke = recent_jokes[0]
                        return f"That's funny, you want to hear it again! Here it is: {latest_joke['setup']} ... {latest_joke['punchline']}"
                else:
                    # No recent jokes in memory
                    return "I'd love to tell you a joke! Let me think of a good one for you."
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking joke repeat query: {e}")
            return None
    
    def _get_recent_jokes_from_memory(self) -> List[Dict]:
        """Get recent jokes from memory for repeat query handling."""
        try:
            import os
            import json
            from datetime import datetime, timedelta
            
            memories_dir = "memories"
            if not os.path.exists(memories_dir):
                return []
            
            recent_jokes = []
            cutoff_time = datetime.now() - timedelta(hours=1)  # Last hour
            
            for filename in os.listdir(memories_dir):
                if filename.startswith('joke_') and filename.endswith('.json'):
                    try:
                        filepath = os.path.join(memories_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            memory_data = json.load(f)
                        
                        # Check if it's recent enough
                        memory_timestamp = memory_data.get('timestamp', '')
                        if memory_timestamp:
                            try:
                                memory_date = datetime.fromisoformat(memory_timestamp.replace('Z', '+00:00'))
                                if memory_date >= cutoff_time:
                                    joke_data = memory_data.get('joke_data', {})
                                    if joke_data:
                                        recent_jokes.append(joke_data)
                            except:
                                continue
                                
                    except Exception as e:
                        continue
            
            # Sort by timestamp (most recent first)
            recent_jokes.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return recent_jokes[:3]  # Return top 3 most recent
            
        except Exception as e:
            self.logger.error(f"Error getting recent jokes from memory: {e}")
            return []
    
    def get_humor_stats(self) -> Dict[str, Any]:
        """Get humor system statistics."""
        if not self.humor_responses:
            return {"total_jokes": 0, "success_rate": 0.0}
        
        total_jokes = len(self.humor_responses)
        successful_jokes = sum(1 for r in self.humor_responses if r.success)
        laughter_count = sum(1 for r in self.humor_responses if r.laughter_triggered)
        
        avg_incongruity = sum(r.incongruity_score for r in self.humor_responses) / total_jokes
        avg_dopamine_spike = sum(r.dopamine_spike for r in self.humor_responses) / total_jokes
        
        return {
            "total_jokes": total_jokes,
            "successful_jokes": successful_jokes,
            "success_rate": successful_jokes / total_jokes,
            "laughter_count": laughter_count,
            "laughter_rate": laughter_count / total_jokes,
            "avg_incongruity": avg_incongruity,
            "avg_dopamine_spike": avg_dopamine_spike,
            "neurotransmitter_state": asdict(self.neurotransmitter_state)
        }

# Global instance
humor_system = HumorSystem()
