import json
import os
from datetime import datetime
import configparser
import re
from collections import defaultdict
import math

class Event:
    def __init__(self, message=None, event_type=None):
        # Basic event fields
        self.timestamp = datetime.now()
        self.event_type = event_type  # Type of event (speak, game_event, etc.)
        self.meaning_cloud_topics = None
        self.meaning_cloud_sentiment = None
        self.concept_net = None
        self.personality = None
        
        # Vision/Image association fields
        self.vision_data = {
            "image_filepath": "",  # Path to associated image file
            "image_filename": "",  # Just the filename
            "image_hash": "",      # Hash of the image for change detection
            "vision_enabled": True,  # Whether vision was enabled during event
            "camera_active": False,  # Whether camera was active during event
            "image_captured": False,  # Whether an image was successfully captured
            "image_context": {}    # Additional context about the image capture
        }
        
        # HEARER process fields
        self.perceived_message = message  # W1 - what was actually perceived
        self.possible_meanings = []    # P1...Pn - possible interpretations
        self.intended_meaning = None   # P1 - inferred intended meaning
        self.expectation = None        # Expected response or outcome
        self.belief_state = {          # Current belief state
            "accepted": False,         # Whether the message was accepted
            "rejection_reason": None,  # Why it was rejected if applicable
            "confidence": 0.0,        # Confidence in interpretation
            "conflicts": []           # Any conflicts with existing beliefs
        }
        
        # NEUCOGAR Emotional Engine state tracking
        self.neucogar_emotional_state = {
            "primary": "neutral",
            "sub_emotion": "calm",
            "detail": "balanced",
            "neuro_coordinates": {
                "dopamine": 0.0,      # DA: reward/motivation (-1.0 to +1.0)
                "serotonin": 0.0,     # 5-HT: mood/stability/confidence (-1.0 to +1.0)
                "noradrenaline": 0.0  # NE: arousal/alertness (-1.0 to +1.0)
            },
            "intensity": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Legacy emotional state (for backward compatibility during transition)
        self.emotional_state = {
            "current_emotions": {
                "joy": 0.0,
                "surprise": 0.0,
                "sadness": 0.0,
                "fear": 0.0,
                "anger": 0.0,
                "disgust": 0.0
            },
            "neurotransmitters": {
                "dopamine": 0.5,    # Controls cognitive ticking rate
                "serotonin": 0.5,   # Mood stability
                "norepinephrine": 0.5,  # Alertness
                "gaba": 0.5,        # Inhibition
                "glutamate": 0.5,   # Excitation
                "acetylcholine": 0.5,  # Memory formation
                "oxytocin": 0.5,    # Social bonding
                "endorphins": 0.5   # Reward
            }
        }
        
        # Cognitive state for personality processing
        self.cognitive_state = {
            "perception": {
                "intuition": 0.9,  # Default INTP values
                "sensation": 0.3
            },
            "judgment": {
                "thinking": 0.7,
                "feeling": 0.4
            },
            "ticking_rate": 1.0,  # Base rate multiplier
            "tick_count": 0,
            "last_tick": datetime.now()
        }
        
        # Analysis fields
        self.WHO = None
        self.WHAT = None
        self.WHEN = None
        self.WHERE = None
        self.WHY = None
        self.HOW = None
        self.EXPECTATION = None
        self.intent = None
        self.verbs = []
        self.nouns = []  # Now contains dictionaries with word and type
        self.people = []  # List of people mentioned in the event
        self.subjects = []
        
        # Concept tracking
        self.processed_concepts = {}
        
        # Load core emotions mapping
        self.core_emotions = {
            "fear": {
                "humiliated": ["ridiculed", "disrespected"],
                "rejected": ["alienated", "inadequate"],
                "submissive": ["insignificant", "worthless"],
                "insecure": ["inferior", "inadequate"],
                "anxious": ["worried", "overwhelmed"],
                "scared": ["frightened", "terrified"]
            },
            "anger": {
                "frustrated": ["irritated", "infuriated"],
                "aggressive": ["hostile", "provoked"],
                "resentful": ["offended", "jealous"],
                "distant": ["withdrawn", "critical"],
                "infuriated": ["enraged", "annoyed"],
                "bitter": ["violated", "indignant"]
            },
            "disgust": {
                "disapproving": ["judgmental", "dismissive"],
                "disdainful": ["scornful", "contemptuous"],
                "aversion": ["repelled", "nauseated"],
                "apathetic": ["indifferent", "uninterested"]
            },
            "sadness": {
                "hurt": ["betrayed", "abandoned"],
                "grief": ["sorrowful", "mourning"],
                "depressed": ["lonely", "isolated"],
                "guilty": ["remorseful", "ashamed"],
                "despair": ["powerless", "vulnerable"]
            },
            "happiness": {
                "joyful": ["ecstatic", "delighted"],
                "content": ["satisfied", "fulfilled"],
                "amused": ["playful", "cheerful"],
                "proud": ["confident", "successful"],
                "optimistic": ["hopeful", "encouraged"],
                "liberated": ["free", "peaceful"]
            },
            "surprise": {
                "startled": ["shocked", "astonished"],
                "amazed": ["awe-struck", "dumbfounded"],
                "confused": ["perplexed", "disoriented"],
                "curious": ["intrigued", "fascinated"]
            }
        }

        # Add spatial context tracking
        self.spatial_context = {
            "speaker_visible": False,
            "speaker_position": None,  # relative to bot
            "gesture_detected": False,
            "gesture_type": None,
            "object_visibility": {
                "behind_speaker": False,
                "in_hands": False,
                "hidden": True
            }
        }
        
        # Add concept relationship scoring
        self.concept_relationships = {
            "spatial": [],  # spatial relationships
            "temporal": [],  # temporal relationships
            "causal": [],   # causal relationships
            "functional": [] # functional relationships
        }
        
        # Add belief confidence scoring
        self.belief_confidence = {
            "visual_evidence": 0.0,
            "concept_alignment": 0.0,
            "context_relevance": 0.0,
            "relationship_strength": 0.0
        }
        
        # Add emotions field for direct access
        self.emotions = self.emotional_state["current_emotions"]

        # Initialize short-term memory if it doesn't exist
        self._initialize_short_term_memory()

    def _initialize_short_term_memory(self):
        """Initialize or load the short-term memory file."""
        self.short_term_memory_file = 'short_term_memory.json'
        if not os.path.exists(self.short_term_memory_file):
            initial_memory = {
                "last_updated": str(datetime.now()),
                "recent_events": [],
                "max_events": 7
            }
            with open(self.short_term_memory_file, 'w') as f:
                json.dump(initial_memory, f, indent=4)

    def _update_short_term_memory(self, event_file_path):
        """Update the short-term memory with a new event reference."""
        try:
            with open(self.short_term_memory_file, 'r') as f:
                memory = json.load(f)
            
            # Add new event to the beginning of the list
            memory["recent_events"].insert(0, {
                "file_path": event_file_path,
                "timestamp": str(self.timestamp),
                "event_type": self.event_type,
                "summary": self._generate_event_summary()
            })
            
            # Keep only the most recent events (max_events)
            memory["recent_events"] = memory["recent_events"][:memory["max_events"]]
            memory["last_updated"] = str(datetime.now())
            
            with open(self.short_term_memory_file, 'w') as f:
                json.dump(memory, f, indent=4)
                
        except Exception as e:
            print(f"Error updating short-term memory: {e}")

    def _generate_event_summary(self):
        """Generate a human-readable summary of the event."""
        summary_parts = []
        
        if self.event_type:
            summary_parts.append(f"Type: {self.event_type}")
        
        if self.WHAT:
            summary_parts.append(f"What: {self.WHAT}")
        
        if self.WHO:
            summary_parts.append(f"Who: {self.WHO}")
        
        if self.emotions:
            dominant_emotion = max(self.emotions.items(), key=lambda x: x[1])[0]
            summary_parts.append(f"Felt: {dominant_emotion}")
        
        return " | ".join(summary_parts) if summary_parts else "Event occurred"

    def process_hearer_perception(self, message):
        """
        Process the initial perception of a message (W1).
        Returns True if perception was successful.
        """
        try:
            self.perceived_message = message
            # Basic validation of perception
            if not message or not isinstance(message, str):
                return False
            return True
        except Exception as e:
            print(f"Error in perception: {e}")
            return False

    def analyze_possible_meanings(self, openai_result):
        """
        Analyze possible meanings (P1...Pn) from the OpenAI result.
        Updates the event with analyzed data.
        """
        try:
            if not openai_result:
                return False
                
            # Extract the main fields
            self.WHO = openai_result.get("WHO")
            self.WHAT = openai_result.get("WHAT")
            self.WHEN = openai_result.get("WHEN")
            self.WHERE = openai_result.get("WHERE")
            self.WHY = openai_result.get("WHY")
            self.HOW = openai_result.get("HOW")
            self.EXPECTATION = openai_result.get("EXPECTATION")
            self.intent = openai_result.get("intent")
            self.verbs = openai_result.get("verbs", [])
            self.nouns = openai_result.get("nouns", [])
            self.people = openai_result.get("people", [])
            self.subjects = openai_result.get("subjects", [])
            
            # Store primary meaning
            primary_meaning = {
                "what": self.WHAT,
                "intent": self.intent,
                "confidence": 1.0
            }
            self.possible_meanings = [primary_meaning]
            
            return True
        except Exception as e:
            print(f"Error in meaning analysis: {e}")
            return False

    def disambiguate_meaning(self):
        """
        Infer the intended meaning (P1) from possible meanings.
        """
        if not self.possible_meanings:
            return False
            
        try:
            # Sort by confidence and pick the highest
            sorted_meanings = sorted(
                self.possible_meanings,
                key=lambda x: x.get("confidence", 0),
                reverse=True
            )
            
            self.intended_meaning = sorted_meanings[0]
            self.belief_state["confidence"] = self.intended_meaning.get("confidence", 0)
            
            return True
        except Exception as e:
            print(f"Error in disambiguation: {e}")
            return False

    def incorporate_belief(self, existing_beliefs=None):
        """
        Enhanced belief incorporation with context-aware evaluation.
        """
        if not self.intended_meaning:
            return False
            
        try:
            # Calculate overall belief confidence
            overall_confidence = sum(self.belief_confidence.values()) / len(self.belief_confidence)
            
            # Check for conflicts with existing beliefs
            conflicts = []
            if existing_beliefs:
                for belief in existing_beliefs:
                    if self._check_belief_conflict(belief):
                        conflicts.append(belief)
            
            self.belief_state["conflicts"] = conflicts
            
            # Decide whether to accept based on confidence and conflicts
            if not conflicts and overall_confidence > 0.6:  # Higher threshold for acceptance
                self.belief_state["accepted"] = True
                self.belief_state["confidence"] = overall_confidence
            else:
                self.belief_state["accepted"] = False
                self.belief_state["rejection_reason"] = (
                    "Conflicts with existing beliefs" if conflicts
                    else "Insufficient confidence in interpretation"
                )
            
            return True
        except Exception as e:
            print(f"Error in belief incorporation: {e}")
            return False

    def _check_belief_conflict(self, belief):
        """Check if a belief conflicts with the current interpretation."""
        # Implement belief conflict checking logic
        return False  # Placeholder implementation

    def export_to_json(self, folder_path):
        """Export event data to a JSON file and update short-term memory."""
        try:
            # Create folder if it doesn't exist
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            # Generate filename with timestamp
            timestamp_str = self.timestamp.strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp_str}_event.json"
            filepath = os.path.join(folder_path, filename)
            
            # Prepare event data with NEUCOGAR emotional state
            event_data = {
                "WHO": self.WHO,
                "WHAT": self.WHAT,
                "WHEN": self.WHEN,
                "WHERE": self.WHERE,
                "WHY": self.WHY,
                "HOW": self.HOW,
                "EXPECTATION": self.EXPECTATION,
                "intent": self.intent,
                "nouns": self.nouns,
                "verbs": self.verbs,
                "people": self.people,
                "subjects": self.subjects,
                # Include NEUCOGAR emotional state as primary emotional data
                "neucogar_emotional_state": self.neucogar_emotional_state,
                # Legacy emotional state for backward compatibility
                "emotions": self.emotional_state["current_emotions"],
                "neurotransmitters": self.emotional_state["neurotransmitters"],
                "carl_thought": {
                    "automatic_thought": getattr(self, 'automatic_thought', ''),
                    "proposed_action": getattr(self, 'proposed_action', {}),
                    "emotional_context": getattr(self, 'emotional_context', {}),
                    "needs_considered": getattr(self, 'needs_considered', []),
                    "goal_alignment": getattr(self, 'goal_alignment', []),
                    "relevant_experience": getattr(self, 'relevant_experience', {}),
                    "next_mbti_function_phase": getattr(self, 'next_mbti_function_phase', {})
                }
            }
            
            # Save event data
            with open(filepath, 'w') as f:
                json.dump(event_data, f, indent=4)
            
            # Update short-term memory
            self._update_short_term_memory(filepath)
            
            # Create long-term memory for speak events or events with observations
            if (self.event_type == "speak" or 
                self.WHAT or 
                self.WHO or 
                self.emotions):
                self.add_memory_long_term(folder_path)
            
            return filepath
            
        except Exception as e:
            print(f"Error exporting event: {e}")
            return None

    def add_memory_long_term(self, root_folder):
        """Implement logic to save long-term memory."""
        try:
            # Create memory directory if it doesn't exist
            memory_dir = os.path.join(root_folder, 'memories')
            if not os.path.exists(memory_dir):
                os.makedirs(memory_dir)

            # Generate memory filename
            memory_file = os.path.join(memory_dir, f"{self.timestamp.strftime('%Y-%m-%d_%H%M%S')}_memory.json")

            # Prepare memory data
            memory_data = {
                "timestamp": str(self.timestamp),
                "event_data": {
                    "WHAT": self.WHAT,
                    "WHEN": self.WHEN,
                    "WHERE": self.WHERE,
                    "WHY": self.WHY,
                    "HOW": self.HOW,
                    "EXPECTATION": self.EXPECTATION,
                    "intent": self.intent,
                    "nouns": self.nouns,
                    "verbs": self.verbs,
                    "people": self.people,
                    "subjects": self.subjects
                },
                "neucogar_emotional_state": self.neucogar_emotional_state,
                "emotional_state": {
                    "current_emotions": self.emotional_state["current_emotions"],
                    "neurotransmitters": self.emotional_state["neurotransmitters"],
                    "emotional_history": self.emotional_state["emotional_history"],
                    "aggregated_emotions": self.emotional_state["emotional_history"]["aggregated_emotions"],
                    "aggregated_neurotransmitters": self.emotional_state["emotional_history"]["aggregated_neurotransmitters"]
                },
                "cognitive_state": {
                    "tick_count": self.cognitive_state["tick_count"],
                    "ticking_rate": self.cognitive_state["ticking_rate"],
                    "perception": self.cognitive_state.get("perception", {}),
                    "judgment": self.cognitive_state.get("judgment", {})
                },
                "belief_state": {
                    "accepted": self.belief_state["accepted"],
                    "confidence": self.belief_state["confidence"],
                    "conflicts": self.belief_state["conflicts"]
                },
                "perception_result": self.perception_result if hasattr(self, 'perception_result') else {},
                "judgment_result": self.judgment_result if hasattr(self, 'judgment_result') else {},
                "associated_concepts": {
                    "nouns": self.nouns,
                    "verbs": self.verbs,
                    "subjects": self.subjects,
                    "people": self.people
                },
                "needs_impact": self.judgment_result.get("needs_impact", {}) if hasattr(self, 'judgment_result') else {},
                "goals_impact": self.judgment_result.get("goals_impact", {}) if hasattr(self, 'judgment_result') else {},
                "recommended_actions": self.judgment_result.get("recommended_actions", []) if hasattr(self, 'judgment_result') else []
            }

            # Save memory file
            with open(memory_file, 'w') as f:
                json.dump(memory_data, f, indent=4)

            # Update associated concepts with this memory
            self.associate_with_concepts(self.nouns + self.verbs + self.subjects + self.people)

            return memory_file

        except Exception as e:
            print(f"Error saving long-term memory: {e}")
            return None

    def associate_with_concepts(self, concepts):
        """
        Associate this event with the given concepts, updating their data.
        
        Args:
            concepts (list): List of concept names to associate with this event
        """
        for concept in concepts:
            concept_file_path = os.path.join('concepts', f"{concept}.json")
            
            # Initialize or load concept data
            if os.path.exists(concept_file_path):
                with open(concept_file_path, 'r') as f:
                    concept_data = json.load(f)
            else:
                concept_data = {
                    "concept": concept,
                    "conceptnet_data": {
                        "has_data": False,
                        "last_lookup": None,
                        "edges": [],
                        "relationships": []
                    },
                    "emotional_history": [],
                    "event_references": [],
                    "aggregated_emotions": {},
                    "last_updated": str(datetime.now()),
                    "linked_concepts": [],
                    "linked_needs": [],
                    "linked_goals": [],
                    "linked_skills": [],
                    "emotional_links": {},
                    "rankings": {}
                }

            # Update event references
            event_file_name = f"{self.timestamp.strftime('%Y-%m-%d_%H%M%S')}_event"
            if event_file_name not in concept_data["event_references"]:
                concept_data["event_references"].append(event_file_name)

            # Update emotional history
            if self.emotions:
                emotional_entry = {
                    "timestamp": str(self.timestamp),
                    "event_file": event_file_name,
                    "emotions": self.emotions
                }
                concept_data["emotional_history"].append(emotional_entry)

                # Update aggregated emotions
                for emotion, score in self.emotions.items():
                    if emotion in concept_data["aggregated_emotions"]:
                        old_score = concept_data["aggregated_emotions"][emotion]["score"]
                        old_count = concept_data["aggregated_emotions"][emotion]["count"]
                        new_score = ((old_score * old_count) + score) / (old_count + 1)
                        concept_data["aggregated_emotions"][emotion] = {
                            "score": new_score,
                            "count": old_count + 1
                        }
                    else:
                        concept_data["aggregated_emotions"][emotion] = {
                            "score": score,
                            "count": 1
                        }

            # Update emotional links
            if self.emotions:
                for emotion, score in self.emotions.items():
                    if score > 0:  # Only store significant emotional associations
                        if emotion not in concept_data["emotional_links"]:
                            concept_data["emotional_links"][emotion] = []
                        
                        emotional_link = {
                            "event_file": event_file_name,
                            "score": score,
                            "timestamp": str(self.timestamp)
                        }
                        concept_data["emotional_links"][emotion].append(emotional_link)

            # Update linked concepts
            if hasattr(self, 'nouns'):
                for noun in self.nouns:
                    if noun != concept and noun not in concept_data["linked_concepts"]:
                        concept_data["linked_concepts"].append(noun)

            # Update rankings
            base_score = concept_data["rankings"].get(event_file_name, 0)
            emotion_multiplier = self._calculate_emotion_multiplier()
            concept_data["rankings"][event_file_name] = base_score + (1 * emotion_multiplier)

            concept_data["last_updated"] = str(datetime.now())

            # Save the updated concept data
            with open(concept_file_path, 'w') as f:
                json.dump(concept_data, f, indent=4)

    def _calculate_emotion_multiplier(self):
        """
        Calculates a multiplier based on emotional intensity.
        Returns a value between 0.0 and 1.0 based on emotional response.
        """
        if not self.emotions:
            return 0.0
            
        # Calculate average emotional intensity
        total_intensity = sum(score for score in self.emotions.values())
        num_emotions = len(self.emotions)
        
        if num_emotions == 0:
            return 0.0
            
        avg_intensity = total_intensity / num_emotions
        
        # Return a multiplier between 0.0 and 1.0
        return min(avg_intensity, 1.0)

    def update_neucogar_emotional_state(self, neucogar_state):
        """
        Update NEUCOGAR emotional state with new state from the engine.
        This is the primary method for updating emotional state.
        """
        self.neucogar_emotional_state = neucogar_state.copy()
        self.neucogar_emotional_state["timestamp"] = datetime.now().isoformat()
        
        # Update cognitive ticking rate based on dopamine level
        dopamine_level = neucogar_state["neuro_coordinates"]["dopamine"]
        self.cognitive_state["ticking_rate"] = self._calculate_ticking_rate_from_neucogar(dopamine_level)
        
        # Update legacy emotional state for backward compatibility
        self._update_legacy_emotional_state(neucogar_state)
        
    def _calculate_ticking_rate_from_neucogar(self, dopamine_level):
        """
        Calculate cognitive ticking rate based on NEUCOGAR dopamine level.
        Maps from NEUCOGAR range (-1.0 to +1.0) to legacy range (0.0 to 1.0).
        """
        # Convert NEUCOGAR dopamine range (-1.0 to +1.0) to legacy range (0.0 to 1.0)
        legacy_dopamine = (dopamine_level + 1.0) / 2.0
        
        # Base rate is 0.25 (quarter speed)
        base_rate = 0.25
        
        # More gradual dopamine effect
        if legacy_dopamine < 0.3:
            # Slower when dopamine is low, but not too slow
            return max(0.1, base_rate * (0.5 + legacy_dopamine))
        elif legacy_dopamine > 0.7:
            # Faster when dopamine is high, but not too fast
            return min(1.0, base_rate * (1.0 + (legacy_dopamine - 0.7) * 1.5))
        else:
            # Normal range - gradual increase
            return base_rate * (0.8 + (legacy_dopamine - 0.3) * 0.4)
    
    def _update_legacy_emotional_state(self, neucogar_state):
        """
        Update legacy emotional state for backward compatibility.
        Maps NEUCOGAR emotional state to legacy format.
        """
        # Map NEUCOGAR primary emotion to legacy emotions
        primary_emotion = neucogar_state["primary"]
        intensity = neucogar_state["intensity"]
        
        # Reset all legacy emotions
        for emotion in self.emotional_state["current_emotions"]:
            self.emotional_state["current_emotions"][emotion] = 0.0
        
        # Map NEUCOGAR emotions to legacy emotions with proper intensity
        emotion_mapping = {
            "joy": "joy",
            "happiness": "joy",
            "sadness": "sadness",
            "anger": "anger",
            "fear": "fear",
            "surprise": "surprise",
            "disgust": "disgust",
            "curiosity": "surprise",  # Map curiosity to surprise
            "neutral": "joy"  # Map neutral to low joy for positive baseline
        }
        
        # Set the mapped emotion intensity
        mapped_emotion = emotion_mapping.get(primary_emotion, "joy")
        if mapped_emotion in self.emotional_state["current_emotions"]:
            self.emotional_state["current_emotions"][mapped_emotion] = intensity
        
        # Update legacy neurotransmitters (map from NEUCOGAR to legacy format)
        neucogar_coords = neucogar_state["neuro_coordinates"]
        
        # Map NEUCOGAR coordinates to legacy neurotransmitter ranges
        self.emotional_state["neurotransmitters"]["dopamine"] = (neucogar_coords["dopamine"] + 1.0) / 2.0
        self.emotional_state["neurotransmitters"]["serotonin"] = (neucogar_coords["serotonin"] + 1.0) / 2.0
        self.emotional_state["neurotransmitters"]["norepinephrine"] = (neucogar_coords["noradrenaline"] + 1.0) / 2.0
        
        # Set other neurotransmitters to baseline
        self.emotional_state["neurotransmitters"]["gaba"] = 0.5
        self.emotional_state["neurotransmitters"]["glutamate"] = 0.5
        self.emotional_state["neurotransmitters"]["acetylcholine"] = 0.5
        self.emotional_state["neurotransmitters"]["oxytocin"] = 0.5
        self.emotional_state["neurotransmitters"]["endorphins"] = 0.5

    def update_emotional_state(self, new_emotions, new_neurotransmitters=None):
        """
        Legacy method for updating emotional state.
        Now delegates to NEUCOGAR engine through main application.
        """
        # This method is kept for backward compatibility but should not be used directly
        # The main application should use update_neucogar_emotional_state instead
        pass
            
    def _calculate_ticking_rate(self, dopamine_level):
        """
        Calculate cognitive ticking rate based on dopamine level.
        Base rate is now 0.25 (quarter speed), with dopamine affecting speed more gradually.
        """
        # Base rate is now 0.25 (quarter speed)
        base_rate = 0.25
        
        # More gradual dopamine effect
        if dopamine_level < 0.3:
            # Slower when dopamine is low, but not too slow
            return max(0.1, base_rate * (0.5 + dopamine_level))
        elif dopamine_level > 0.7:
            # Faster when dopamine is high, but not too fast
            return min(1.0, base_rate * (1.0 + (dopamine_level - 0.7) * 1.5))
        else:
            # Normal range - gradual increase
            return base_rate * (0.8 + (dopamine_level - 0.3) * 0.4)

    def _should_update_emotions(self):
        """
        Determine if enough cognitive ticks have passed to update emotions.
        Base tick interval is now 400ms (slower than before), modified by ticking rate.
        """
        current_time = datetime.now()
        time_passed = (current_time - self.cognitive_state["last_tick"]).total_seconds()
        
        # Base tick interval is 400ms (slower than before), modified by ticking rate
        tick_interval = 0.4 / self.cognitive_state["ticking_rate"]
        
        if time_passed >= tick_interval:
            self.cognitive_state["tick_count"] += 1
            self.cognitive_state["last_tick"] = current_time
            return True
            
        return False
        
    def _update_neurotransmitters(self, new_values):
        """
        Update neurotransmitter levels with smoother transitions.
        """
        for nt, value in new_values.items():
            if nt in self.emotional_state["neurotransmitters"]:
                current = self.emotional_state["neurotransmitters"][nt]
                # Smoother transition with smaller adjustment
                self.emotional_state["neurotransmitters"][nt] = (current + value) / 2.5
                
        # Apply homeostasis
        self._apply_neurotransmitter_homeostasis()
        
    def _apply_neurotransmitter_homeostasis(self):
        """
        Apply homeostasis to neurotransmitter levels.
        More gradual return to baseline.
        """
        for nt in self.emotional_state["neurotransmitters"]:
            current = self.emotional_state["neurotransmitters"][nt]
            # Move towards baseline (0.5) at a slower rate based on distance
            if current > 0.5:
                # Slower return when higher above baseline
                adjustment = 0.02 * (current - 0.5)
                self.emotional_state["neurotransmitters"][nt] = max(0.5, current - adjustment)
            elif current < 0.5:
                # Slower return when lower below baseline
                adjustment = 0.02 * (0.5 - current)
                self.emotional_state["neurotransmitters"][nt] = min(0.5, current + adjustment)

    def _update_aggregated_values(self):
        """
        Update aggregated emotions and neurotransmitters based on historical events.
        """
        events = self.emotional_state["emotional_history"]["events"]
        if not events:
            return

        # Initialize aggregated dictionaries
        agg_emotions = {}
        agg_neurotransmitters = {}

        # Calculate averages for emotions
        for event in events:
            for emotion, value in event["emotions"].items():
                if emotion not in agg_emotions:
                    agg_emotions[emotion] = {"sum": 0, "count": 0}
                agg_emotions[emotion]["sum"] += value
                agg_emotions[emotion]["count"] += 1

        # Calculate averages for neurotransmitters
        for event in events:
            for nt, value in event["neurotransmitters"].items():
                if nt not in agg_neurotransmitters:
                    agg_neurotransmitters[nt] = {"sum": 0, "count": 0}
                agg_neurotransmitters[nt]["sum"] += value
                agg_neurotransmitters[nt]["count"] += 1

        # Convert sums to averages
        self.emotional_state["emotional_history"]["aggregated_emotions"] = {
            emotion: data["sum"] / data["count"]
            for emotion, data in agg_emotions.items()
        }

        self.emotional_state["emotional_history"]["aggregated_neurotransmitters"] = {
            nt: data["sum"] / data["count"]
            for nt, data in agg_neurotransmitters.items()
        }

    def get_emotional_summary(self, concept=None):
        """
        Get emotional summary for a specific concept or overall.
        Returns aggregated emotions and neurotransmitters.
        """
        if concept:
            # Filter events related to the concept
            concept_events = [
                event for event in self.emotional_state["emotional_history"]["events"]
                if concept in self.concepts
            ]
            
            if not concept_events:
                return None
                
            # Calculate concept-specific aggregates
            agg_emotions = {}
            agg_neurotransmitters = {}
            
            for event in concept_events:
                for emotion, value in event["emotions"].items():
                    if emotion not in agg_emotions:
                        agg_emotions[emotion] = {"sum": 0, "count": 0}
                    agg_emotions[emotion]["sum"] += value
                    agg_emotions[emotion]["count"] += 1
                    
                for nt, value in event["neurotransmitters"].items():
                    if nt not in agg_neurotransmitters:
                        agg_neurotransmitters[nt] = {"sum": 0, "count": 0}
                    agg_neurotransmitters[nt]["sum"] += value
                    agg_neurotransmitters[nt]["count"] += 1
            
            return {
                "emotions": {
                    emotion: data["sum"] / data["count"]
                    for emotion, data in agg_emotions.items()
                },
                "neurotransmitters": {
                    nt: data["sum"] / data["count"]
                    for nt, data in agg_neurotransmitters.items()
                }
            }
        
        return {
            "emotions": self.emotional_state["emotional_history"]["aggregated_emotions"],
            "neurotransmitters": self.emotional_state["emotional_history"]["aggregated_neurotransmitters"]
        }

    def get_dominant_emotion(self):
        """Returns the currently dominant emotion and its intensity."""
        if not self.emotional_state["current_emotions"]:
            return None, 0.0
        
        dominant_emotion = max(self.emotional_state["current_emotions"].items(), key=lambda x: x[1])
        return dominant_emotion[0], dominant_emotion[1]

    def get_emotional_complexity(self):
        """
        Calculates the complexity of the current emotional state.
        Returns a score based on how many different emotions are active and their relative intensities.
        """
        emotions = self.emotional_state["current_emotions"]
        if not emotions:
            return 0.0
        
        # Calculate Shannon's entropy for emotional complexity
        total = sum(emotions.values())
        if total == 0:
            return 0.0
        
        probabilities = [v/total for v in emotions.values() if v > 0]
        entropy = -sum(p * math.log2(p) for p in probabilities)
        
        return entropy

    def evaluate_concept_relationships(self, conceptnet_edges, context):
        """
        Evaluate concept relationships based on context and visual evidence.
        
        Args:
            conceptnet_edges: List of ConceptNet edges
            context: Current context including visual information
        """
        relevant_edges = []
        
        # Update spatial context based on visual information
        if context.get("speaker_visible"):
            self.spatial_context["speaker_visible"] = True
            self.spatial_context["speaker_position"] = context.get("speaker_position")
            
            # Check for gestures or hidden objects
            if context.get("gesture_detected"):
                self.spatial_context["gesture_detected"] = True
                self.spatial_context["gesture_type"] = context.get("gesture_type")
                
                # If gesture indicates something behind back
                if context.get("gesture_type") == "behind_back":
                    self.spatial_context["object_visibility"]["behind_speaker"] = True
                    self.spatial_context["object_visibility"]["hidden"] = True
        
        # Score each edge based on context and relationships
        for edge in conceptnet_edges:
            score = self._score_concept_edge(edge, context)
            if score > 0.5:  # Only include highly relevant edges
                relevant_edges.append((edge, score))
        
        # Sort edges by relevance score
        relevant_edges.sort(key=lambda x: x[1], reverse=True)
        
        # Update belief confidence based on edge evaluation
        self._update_belief_confidence(relevant_edges)
        
        return relevant_edges

    def _score_concept_edge(self, edge, context):
        """
        Score a concept edge based on context and relationship type.
        """
        score = 0.0
        surface_text = edge.get("surfaceText", "").lower()
        
        # Check for spatial relationships
        spatial_terms = ["behind", "back", "front", "rear", "spine"]
        if any(term in surface_text for term in spatial_terms):
            # Boost score for spatial relationships if we have visual context
            if self.spatial_context["speaker_visible"]:
                score += 0.4
                
                # Further boost if the relationship matches our visual context
                if self.spatial_context["object_visibility"]["behind_speaker"]:
                    if "behind" in surface_text or "back" in surface_text:
                        score += 0.3
                        
                # Penalize if relationship contradicts visual context
                if "front" in surface_text and self.spatial_context["object_visibility"]["behind_speaker"]:
                    score -= 0.2
        
        # Check relationship type
        rel_type = edge.get("rel", {}).get("label", "").lower()
        if rel_type in ["relatedto", "isa", "partof"]:
            score += 0.2
            
        # Check weight/confidence from ConceptNet
        weight = edge.get("weight", 1.0)
        score *= weight
        
        return min(1.0, max(0.0, score))

    def _update_belief_confidence(self, relevant_edges):
        """
        Update belief confidence based on evaluated edges.
        """
        if not relevant_edges:
            return
            
        # Calculate visual evidence score
        self.belief_confidence["visual_evidence"] = (
            0.8 if self.spatial_context["speaker_visible"] else 0.2
        )
        
        # Calculate concept alignment score
        spatial_edges = [edge for edge, score in relevant_edges 
                        if any(term in edge.get("surfaceText", "").lower() 
                              for term in ["behind", "back", "front"])]
        self.belief_confidence["concept_alignment"] = len(spatial_edges) / len(relevant_edges)
        
        # Calculate context relevance score
        context_relevance = 0.0
        if self.spatial_context["object_visibility"]["behind_speaker"]:
            context_relevance += 0.4
        if self.spatial_context["gesture_detected"]:
            context_relevance += 0.3
        if self.spatial_context["speaker_visible"]:
            context_relevance += 0.3
        self.belief_confidence["context_relevance"] = context_relevance
        
        # Calculate relationship strength score
        avg_score = sum(score for _, score in relevant_edges) / len(relevant_edges)
        self.belief_confidence["relationship_strength"] = avg_score

    def update_from_analysis(self, analysis):
        """Update event attributes from analysis results."""
        self.WHO = analysis.get("WHO", "")
        self.WHAT = analysis.get("WHAT", "")
        self.WHEN = analysis.get("WHEN", "")
        self.WHERE = analysis.get("WHERE", "")
        self.WHY = analysis.get("WHY", "")
        self.HOW = analysis.get("HOW", "")
        self.EXPECTATION = analysis.get("EXPECTATION", "")
        self.intent = analysis.get("intent", "unknown")
        self.nouns = analysis.get("nouns", [])
        self.verbs = analysis.get("verbs", [])
        self.people = analysis.get("people", [])
        self.subjects = analysis.get("subjects", [])

    def get_recent_events_summary(self):
        """Get a human-readable summary of recent events."""
        try:
            with open(self.short_term_memory_file, 'r') as f:
                memory = json.load(f)
            
            if not memory["recent_events"]:
                return "I haven't done anything recently."
            
            # Group events by date
            events_by_date = {}
            for event in memory["recent_events"]:
                event_date = datetime.fromisoformat(event["timestamp"]).date()
                if event_date not in events_by_date:
                    events_by_date[event_date] = []
                events_by_date[event_date].append(event)
            
            # Generate summary
            summary_parts = []
            for date, events in events_by_date.items():
                date_str = date.strftime("%B %d")
                event_summaries = [event["summary"] for event in events]
                summary_parts.append(f"On {date_str}, I {', '.join(event_summaries)}")
            
            return " ".join(summary_parts)
            
        except Exception as e:
            print(f"Error getting recent events summary: {e}")
            return "I'm having trouble remembering my recent activities."
    
    def associate_image(self, image_filepath: str, image_hash: str = "", vision_enabled: bool = True, 
                       camera_active: bool = False, context: dict = None):
        """
        Associate an image with this event.
        
        Args:
            image_filepath: Path to the image file
            image_hash: Hash of the image for change detection
            vision_enabled: Whether vision was enabled during capture
            camera_active: Whether camera was active during capture
            context: Additional context about the image capture
        """
        try:
            # Extract filename from filepath
            image_filename = os.path.basename(image_filepath) if image_filepath else ""
            
            # Update vision data
            self.vision_data.update({
                "image_filepath": image_filepath,
                "image_filename": image_filename,
                "image_hash": image_hash,
                "vision_enabled": vision_enabled,
                "camera_active": camera_active,
                "image_captured": bool(image_filepath),
                "image_context": context or {}
            })
            
            print(f"✅ Image associated with event: {image_filename}")
            
        except Exception as e:
            print(f"Error associating image with event: {e}")
            # Set default values if association fails
            self.vision_data.update({
                "image_filepath": "",
                "image_filename": "",
                "image_hash": "",
                "vision_enabled": vision_enabled,
                "camera_active": camera_active,
                "image_captured": False,
                "image_context": {}
            })
    
    def get_image_info(self) -> dict:
        """Get information about the associated image."""
        return self.vision_data.copy()
    
    def has_image(self) -> bool:
        """Check if this event has an associated image."""
        return self.vision_data["image_captured"] and bool(self.vision_data["image_filepath"])