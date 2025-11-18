import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import configparser

# Import OpenAI with error handling
try:
    import openai
    openai_available = True
except ImportError:
    openai = None
    openai_available = False
    print("ℹ️ Info: OpenAI library not available - AIML fallback responses disabled")

class JudgmentSystem:
    def __init__(self, main_app=None):
        # Load personality settings
        self.config = configparser.ConfigParser()
        self.main_app = main_app
        if os.path.exists('settings_current.ini'):
            self.config.read('settings_current.ini')
        else:
            self.config.read('settings_default.ini')
            
        # Initialize MBTI type and cognitive functions
        self.mbti_type = self.config.get('personality', 'type', fallback='INTP')
        self.cognitive_functions = self._initialize_cognitive_functions()
        
        # Initialize personality traits from cognitive functions
        self.personality_traits = self._derive_personality_traits()
        
        # Initialize needs and goals from settings
        self.needs = [need.strip() for need in self.config.get('personality-favorites', 'needs', fallback='').split(',')]
        self.goals = [goal.strip() for goal in self.config.get('personality-favorites', 'goals', fallback='').split(',')]
        
        # Initialize fears and hopes
        self.fears = [fear.strip() for fear in self.config.get('personality-favorites', 'fears', fallback='').split(',')]
        self.hopes = [hope.strip() for hope in self.config.get('personality-favorites', 'hopes', fallback='').split(',')]
        
        # Initialize OpenAI settings
        self.openai_api_key = self.config.get('settings', 'openaiapikey', fallback='')
        self.openai_random_enabled = self.config.getboolean('AIML', 'openai_random_enabled', fallback=True)
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Only set up OpenAI if library is available
        if openai_available and self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        elif not openai_available:
            self.openai_random_enabled = False
            self.openai_client = None
            print("ℹ️ Info: OpenAI library not available - disabling OpenAI fallback responses")
        else:
            self.openai_client = None

    def _initialize_cognitive_functions(self):
        """
        Initialize cognitive function stack based on MBTI type.
        Returns a dictionary with function positions and their corresponding effectiveness levels.
        """
        # MBTI type to cognitive function mapping
        function_map = {
            'ISFP': {
                'dominant': ('Fi', 0.9),     # Introverted Feeling
                'auxiliary': ('Se', 0.7),    # Extraverted Sensing
                'tertiary': ('Ni', 0.5),     # Introverted Intuition
                'inferior': ('Te', 0.3),     # Extraverted Thinking
                'demon': ('Fe', 0.2),        # Extraverted Feeling
                'critic': ('Si', 0.4),       # Introverted Sensing
                'trickster': ('Ne', 0.3),    # Extraverted Intuition
                'nemesis': ('Ti', 0.4)       # Introverted Thinking
            },
            'INTP': {
                'dominant': ('Ti', 0.9),     # Introverted Thinking
                'auxiliary': ('Ne', 0.7),    # Extraverted Intuition
                'tertiary': ('Si', 0.5),     # Introverted Sensing
                'inferior': ('Fe', 0.3),     # Extraverted Feeling
                'demon': ('Te', 0.2),        # Extraverted Thinking
                'critic': ('Ni', 0.4),       # Introverted Intuition
                'trickster': ('Se', 0.3),    # Extraverted Sensing
                'nemesis': ('Fi', 0.4)       # Introverted Feeling
            },
            'INFP': {
                'dominant': ('Fi', 0.9),     # Introverted Feeling
                'auxiliary': ('Ne', 0.7),    # Extraverted Intuition
                'tertiary': ('Si', 0.5),     # Introverted Sensing
                'inferior': ('Te', 0.3),     # Extraverted Thinking
                'demon': ('Fe', 0.2),        # Extraverted Feeling
                'critic': ('Ni', 0.4),       # Introverted Intuition
                'trickster': ('Se', 0.3),    # Extraverted Sensing
                'nemesis': ('Ti', 0.4)       # Introverted Thinking
            },
            'ISTP': {
                'dominant': ('Ti', 0.9),     # Introverted Thinking
                'auxiliary': ('Se', 0.7),    # Extraverted Sensing
                'tertiary': ('Ni', 0.5),     # Introverted Intuition
                'inferior': ('Fe', 0.3),     # Extraverted Feeling
                'demon': ('Te', 0.2),        # Extraverted Thinking
                'critic': ('Si', 0.4),       # Introverted Sensing
                'trickster': ('Ne', 0.3),    # Extraverted Intuition
                'nemesis': ('Fi', 0.4)       # Introverted Feeling
            },
            'INFJ': {
                'dominant': ('Ni', 0.9),     # Introverted Intuition
                'auxiliary': ('Fe', 0.7),    # Extraverted Feeling
                'tertiary': ('Ti', 0.5),     # Introverted Thinking
                'inferior': ('Se', 0.3),     # Extraverted Sensing
                'demon': ('Ne', 0.2),        # Extraverted Intuition
                'critic': ('Fi', 0.4),       # Introverted Feeling
                'trickster': ('Te', 0.3),    # Extraverted Thinking
                'nemesis': ('Si', 0.4)       # Introverted Sensing
            },
            'INTJ': {
                'dominant': ('Ni', 0.9),     # Introverted Intuition
                'auxiliary': ('Te', 0.7),    # Extraverted Thinking
                'tertiary': ('Fi', 0.5),     # Introverted Feeling
                'inferior': ('Se', 0.3),     # Extraverted Sensing
                'demon': ('Ne', 0.2),        # Extraverted Intuition
                'critic': ('Ti', 0.4),       # Introverted Thinking
                'trickster': ('Fe', 0.3),    # Extraverted Feeling
                'nemesis': ('Si', 0.4)       # Introverted Sensing
            },
            'ISTJ': {
                'dominant': ('Si', 0.9),     # Introverted Sensing
                'auxiliary': ('Te', 0.7),    # Extraverted Thinking
                'tertiary': ('Fi', 0.5),     # Introverted Feeling
                'inferior': ('Ne', 0.3),     # Extraverted Intuition
                'demon': ('Se', 0.2),        # Extraverted Sensing
                'critic': ('Ti', 0.4),       # Introverted Thinking
                'trickster': ('Fe', 0.3),    # Extraverted Feeling
                'nemesis': ('Ni', 0.4)       # Introverted Intuition
            },
            'ISFJ': {
                'dominant': ('Si', 0.9),     # Introverted Sensing
                'auxiliary': ('Fe', 0.7),    # Extraverted Feeling
                'tertiary': ('Ti', 0.5),     # Introverted Thinking
                'inferior': ('Ne', 0.3),     # Extraverted Intuition
                'demon': ('Se', 0.2),        # Extraverted Sensing
                'critic': ('Fi', 0.4),       # Introverted Feeling
                'trickster': ('Te', 0.3),    # Extraverted Thinking
                'nemesis': ('Ni', 0.4)       # Introverted Intuition
            },
            'ENFP': {
                'dominant': ('Ne', 0.9),     # Extraverted Intuition
                'auxiliary': ('Fi', 0.7),    # Introverted Feeling
                'tertiary': ('Te', 0.5),     # Extraverted Thinking
                'inferior': ('Si', 0.3),     # Introverted Sensing
                'demon': ('Ni', 0.2),        # Introverted Intuition
                'critic': ('Fe', 0.4),       # Extraverted Feeling
                'trickster': ('Ti', 0.3),    # Introverted Thinking
                'nemesis': ('Se', 0.4)       # Extraverted Sensing
            },
            'ENTP': {
                'dominant': ('Ne', 0.9),     # Extraverted Intuition
                'auxiliary': ('Ti', 0.7),    # Introverted Thinking
                'tertiary': ('Fe', 0.5),     # Extraverted Feeling
                'inferior': ('Si', 0.3),     # Introverted Sensing
                'demon': ('Ni', 0.2),        # Introverted Intuition
                'critic': ('Te', 0.4),       # Extraverted Thinking
                'trickster': ('Fi', 0.3),    # Introverted Feeling
                'nemesis': ('Se', 0.4)       # Extraverted Sensing
            },
            'ENFJ': {
                'dominant': ('Fe', 0.9),     # Extraverted Feeling
                'auxiliary': ('Ni', 0.7),    # Introverted Intuition
                'tertiary': ('Se', 0.5),     # Extraverted Sensing
                'inferior': ('Ti', 0.3),     # Introverted Thinking
                'demon': ('Fi', 0.2),        # Introverted Feeling
                'critic': ('Ne', 0.4),       # Extraverted Intuition
                'trickster': ('Si', 0.3),    # Introverted Sensing
                'nemesis': ('Te', 0.4)       # Extraverted Thinking
            },
            'ENTJ': {
                'dominant': ('Te', 0.9),     # Extraverted Thinking
                'auxiliary': ('Ni', 0.7),    # Introverted Intuition
                'tertiary': ('Se', 0.5),     # Extraverted Sensing
                'inferior': ('Fi', 0.3),     # Introverted Feeling
                'demon': ('Ti', 0.2),        # Introverted Thinking
                'critic': ('Ne', 0.4),       # Extraverted Intuition
                'trickster': ('Si', 0.3),    # Introverted Sensing
                'nemesis': ('Fe', 0.4)       # Extraverted Feeling
            },
            'ESFP': {
                'dominant': ('Se', 0.9),     # Extraverted Sensing
                'auxiliary': ('Fi', 0.7),    # Introverted Feeling
                'tertiary': ('Te', 0.5),     # Extraverted Thinking
                'inferior': ('Ni', 0.3),     # Introverted Intuition
                'demon': ('Si', 0.2),        # Introverted Sensing
                'critic': ('Fe', 0.4),       # Extraverted Feeling
                'trickster': ('Ti', 0.3),    # Introverted Thinking
                'nemesis': ('Ne', 0.4)       # Extraverted Intuition
            },
            'ESTP': {
                'dominant': ('Se', 0.9),     # Extraverted Sensing
                'auxiliary': ('Ti', 0.7),    # Introverted Thinking
                'tertiary': ('Fe', 0.5),     # Extraverted Feeling
                'inferior': ('Ni', 0.3),     # Introverted Intuition
                'demon': ('Si', 0.2),        # Introverted Sensing
                'critic': ('Te', 0.4),       # Extraverted Thinking
                'trickster': ('Fi', 0.3),    # Introverted Feeling
                'nemesis': ('Ne', 0.4)       # Extraverted Intuition
            },
            'ESFJ': {
                'dominant': ('Fe', 0.9),     # Extraverted Feeling
                'auxiliary': ('Si', 0.7),    # Introverted Sensing
                'tertiary': ('Ne', 0.5),     # Extraverted Intuition
                'inferior': ('Ti', 0.3),     # Introverted Thinking
                'demon': ('Fi', 0.2),        # Introverted Feeling
                'critic': ('Se', 0.4),       # Extraverted Sensing
                'trickster': ('Ni', 0.3),    # Introverted Intuition
                'nemesis': ('Te', 0.4)       # Extraverted Thinking
            },
            'ESTJ': {
                'dominant': ('Te', 0.9),     # Extraverted Thinking
                'auxiliary': ('Si', 0.7),    # Introverted Sensing
                'tertiary': ('Ne', 0.5),     # Extraverted Intuition
                'inferior': ('Fi', 0.3),     # Introverted Feeling
                'demon': ('Ti', 0.2),        # Introverted Thinking
                'critic': ('Se', 0.4),       # Extraverted Sensing
                'trickster': ('Ni', 0.3),    # Introverted Intuition
                'nemesis': ('Fe', 0.4)       # Extraverted Feeling
            }
        }
        
        # Get function stack for current type
        type_functions = function_map.get(self.mbti_type.upper())
        if not type_functions:
            # Default to INTP if type not found
            type_functions = function_map['INTP']
            print(f"Warning: MBTI type {self.mbti_type} not found, defaulting to INTP")
            
        return type_functions

    def _derive_personality_traits(self):
        """
        Derive personality trait preferences from cognitive functions.
        """
        traits = {
            "energy": {"extrovert": 0.0, "introvert": 0.0},
            "collection": {"intuition": 0.0, "sensation": 0.0},
            "decision": {"thinking": 0.0, "feeling": 0.0},
            "organize": {"judging": 0.0, "perceiving": 0.0}
        }
        
        # Calculate trait preferences based on function positions and effectiveness
        for position, (function, effectiveness) in self.cognitive_functions.items():
            # Get function attitude (e/i) and process (N/S/T/F)
            attitude = function[0]  # 'e' or 'i'
            process = function[1]   # 'N', 'S', 'T', or 'F'
            
            # Update energy preference
            if attitude == 'e':
                traits["energy"]["extrovert"] += effectiveness
            else:
                traits["energy"]["introvert"] += effectiveness
                
            # Update collection preference
            if process in ['N']:
                traits["collection"]["intuition"] += effectiveness
            elif process in ['S']:
                traits["collection"]["sensation"] += effectiveness
                
            # Update decision preference
            if process in ['T']:
                traits["decision"]["thinking"] += effectiveness
            elif process in ['F']:
                traits["decision"]["feeling"] += effectiveness
                
            # Update organization preference (J types lead with a judging function in their dominant/auxiliary)
            if position in ['dominant', 'auxiliary']:
                if process in ['T', 'F']:
                    traits["organize"]["judging"] += effectiveness
                else:
                    traits["organize"]["perceiving"] += effectiveness
        
        # Normalize all preferences to [0,1] range
        for category in traits:
            total = sum(traits[category].values())
            if total > 0:
                for key in traits[category]:
                    traits[category][key] /= total
                    
        return traits

    def judge_input(self, perception_data: Dict, event_data: Dict) -> Dict:
        """
        Main judgment function that processes all perceived data through MBTI cognitive functions.
        Implements Jungian theory with dominant judgment function and inferior function processing.
        
        Args:
            perception_data: Dictionary containing perception results
            event_data: Dictionary containing event data including emotions, intent, etc.
            
        Returns:
            Dict containing judgment results and decisions
        """
        try:
            print(f"🧠 JUDGMENT PHASE: Processing with MBTI type {self.mbti_type}")
            
            # 🎯 ATTENTION SYSTEM: Get current focus and apply attention bias
            focus = None
            outer_bias = 0.0
            if hasattr(self.main_app, 'attention') and self.main_app.attention:
                focus = self.main_app.attention.view()
                if focus:
                    outer_bias = 0.25 if focus.owner in ("outer", "game") else 0.0
            
            judgment = {
                "timestamp": str(datetime.now()),
                "mbti_type": self.mbti_type,
                "personality_impact": {
                    "energy": {"extrovert": 0.0, "introvert": 0.0},
                    "collection": {"intuition": 0.0, "sensation": 0.0},
                    "decision": {"thinking": 0.0, "feeling": 0.0},
                    "organize": {"judging": 0.0, "perceiving": 0.0}
                },
                "trust_assessment": perception_data.get('TrustValue', 0.5),
                "interaction_priority": 0.0,
                "recommended_actions": [],
                "emotional_response": {},
                "needs_impact": {},
                "goals_impact": {},
                "mbti_function_logs": {},
                "next_mbti_function_phase": "",
                "cognitive_processing_summary": {},
                "attention_context": {
                    "focus_owner": focus.owner if focus else "none",
                    "focus_topic": focus.topic if focus else "none",
                    "outer_bias": outer_bias
                }
            }

            # Determine which cognitive functions are most active for this input
            active_functions = self._determine_active_judgment_functions(perception_data, event_data)
            judgment['active_functions'] = active_functions
            
            # Process through dominant judgment function (Feeling or Thinking)
            dominant_judgment = self._process_dominant_judgment(perception_data, event_data, active_functions)
            judgment['judgment_scores'] = dominant_judgment
            
            # Process through inferior functions at reduced effectiveness
            inferior_judgment = self._process_inferior_judgment(perception_data, event_data, active_functions)
            judgment['judgment_scores'].update(inferior_judgment)
            
            # Process personality-based judgment
            self._process_personality_judgment(judgment, perception_data, event_data)
            
            # Process needs-based judgment
            self._process_needs_judgment(judgment, perception_data, event_data)
            
            # Process goals-based judgment
            self._process_goals_judgment(judgment, perception_data, event_data)
            
            # Process ConceptNet-based common sense judgment
            self._process_conceptnet_judgment(judgment, perception_data, event_data)
            
            # Process earthly game suggestions
            self._process_earthly_game_suggestions(judgment, perception_data, event_data)
            
            # Calculate final interaction priority
            judgment["interaction_priority"] = self._calculate_interaction_priority(judgment)
            
            # Generate recommended actions based on personality and context
            self._generate_recommended_actions(judgment, perception_data, event_data)
            
            # Generate cognitive processing summary
            judgment['cognitive_processing_summary'] = self._generate_cognitive_summary(judgment, active_functions)
            
            # Add timeline tracking if available
            if hasattr(self, 'main_app') and self.main_app and hasattr(self.main_app, '_add_timeline_event'):
                # Determine dominant function used
                dominant_function = judgment['cognitive_processing_summary'].get('dominant_function_used', 'unknown')
                
                # Determine success based on interaction priority
                success = judgment.get('interaction_priority', 0.0) > 0.3
                
                self.main_app._add_timeline_event(
                    event_type="judgment_processing",
                    function_used=dominant_function,
                    action="cognitive_analysis",
                    success=success,
                    details=f"priority:{judgment.get('interaction_priority', 0.0):.2f}"
                )
            
            return judgment

        except Exception as e:
            print(f"Error in judgment process: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _generate_emotional_response(self, judgment: Dict, perception_data: Dict, event_data: Dict) -> Dict:
        """
        Generate emotional response based on judgment process and context.
        """
        emotional_response = {}
        
        try:
            # Get interaction priority as base emotional intensity
            interaction_priority = judgment.get("interaction_priority", 0.0)
            
            # Determine primary emotion based on context and judgment
            primary_emotion = "joy"  # Default to positive emotion
            intensity = 0.3  # Base intensity
            
            # Check for command/request context
            if event_data.get("intent") == "command":
                if "somersault" in str(event_data.get("WHAT", "")).lower():
                    primary_emotion = "joy"
                    intensity = 0.6  # Excited to perform acrobatics
                elif "dance" in str(event_data.get("WHAT", "")).lower():
                    primary_emotion = "joy"
                    intensity = 0.7  # Very excited to dance
                elif "head" in str(event_data.get("WHAT", "")).lower():
                    primary_emotion = "surprise"
                    intensity = 0.4  # Slightly surprised by head movement request
                else:
                    primary_emotion = "surprise"
                    intensity = 0.5  # Surprised by command
            
            # Check for greeting context
            elif event_data.get("intent") == "greet":
                primary_emotion = "joy"
                intensity = 0.5  # Happy to greet
            
            # Check for question context
            elif event_data.get("intent") == "inquiry":
                primary_emotion = "surprise"
                intensity = 0.4  # Curious about question
            
            # Check for needs satisfaction
            needs_impact = judgment.get("needs_impact", {})
            if needs_impact:
                max_need_impact = max(needs_impact.values()) if needs_impact.values() else 0.0
                if max_need_impact > 0.3:
                    primary_emotion = "joy"
                    intensity = min(0.8, intensity + 0.3)
                elif max_need_impact < -0.3:
                    primary_emotion = "sadness"
                    intensity = 0.5
            
            # Check for goal progress
            goals_impact = judgment.get("goals_impact", {})
            if goals_impact:
                max_goal_impact = max(goals_impact.values()) if goals_impact.values() else 0.0
                if max_goal_impact > 0.3:
                    primary_emotion = "joy"
                    intensity = min(0.8, intensity + 0.2)
                elif max_goal_impact < -0.3:
                    primary_emotion = "sadness"
                    intensity = 0.4
            
            # Adjust intensity based on interaction priority
            intensity = min(1.0, intensity + (interaction_priority * 0.3))
            
            # Create emotional response
            emotional_response = {
                primary_emotion: intensity
            }
            
            # Add secondary emotions if significant
            if primary_emotion == "joy" and intensity > 0.6:
                emotional_response["surprise"] = 0.3  # Excited surprise
            
            elif primary_emotion == "surprise" and intensity > 0.5:
                emotional_response["joy"] = 0.2  # Pleasant surprise
            
            elif primary_emotion == "sadness" and intensity > 0.5:
                emotional_response["fear"] = 0.2  # Worried about failure
            
        except Exception as e:
            print(f"Error generating emotional response: {e}")
            emotional_response = {"joy": 0.3}  # Default to positive emotion
        
        return emotional_response

    def _process_conceptnet_judgment(self, judgment: Dict, perception_data: Dict, event_data: Dict):
        """
        Process judgment based on ConceptNet common sense relationships.
        This enhances CARL's reasoning with external knowledge validation.
        """
        try:
            # Extract concepts from event data
            concepts = []
            if 'nouns' in event_data:
                for noun in event_data['nouns']:
                    if isinstance(noun, dict):
                        concepts.append(noun.get('word', ''))
                    else:
                        concepts.append(str(noun))
            
            if 'WHAT' in event_data and event_data['WHAT']:
                concepts.append(event_data['WHAT'])
            
            if 'WHERE' in event_data and event_data['WHERE']:
                concepts.append(event_data['WHERE'])
            
            # Initialize ConceptNet judgment data
            judgment['conceptnet_validation'] = {
                'concepts_analyzed': concepts,
                'common_sense_score': 0.0,
                'relationship_confidence': 0.0,
                'knowledge_gaps': [],
                'validated_relationships': []
            }
            
            # Process each concept for common sense validation
            total_confidence = 0.0
            valid_relationships = 0
            
            for concept in concepts:
                if not concept:
                    continue
                
                # Check if we have ConceptNet data for this concept
                concept_file = f"concepts/{concept.lower().replace(' ', '_')}_self_learned.json"
                if os.path.exists(concept_file):
                    with open(concept_file, 'r') as f:
                        concept_data = json.load(f)
                        
                    if 'conceptnet_data' in concept_data and concept_data['conceptnet_data'].get('has_data', False):
                        conceptnet_data = concept_data['conceptnet_data']
                        
                        # Calculate confidence based on relationship weights
                        edges = conceptnet_data.get('edges', [])
                        if edges:
                            avg_weight = sum(edge.get('weight', 0) for edge in edges) / len(edges)
                            total_confidence += avg_weight
                            valid_relationships += len(edges)
                            
                            # Add validated relationships
                            for edge in edges[:3]:  # Top 3 relationships
                                judgment['conceptnet_validation']['validated_relationships'].append({
                                    'concept': concept,
                                    'target': edge.get('target', ''),
                                    'relationship': edge.get('relationship', ''),
                                    'weight': edge.get('weight', 0)
                                })
                        else:
                            judgment['conceptnet_validation']['knowledge_gaps'].append(concept)
                    else:
                        judgment['conceptnet_validation']['knowledge_gaps'].append(concept)
                else:
                    judgment['conceptnet_validation']['knowledge_gaps'].append(concept)
            
            # Calculate overall common sense score
            if concepts:
                judgment['conceptnet_validation']['common_sense_score'] = total_confidence / len(concepts)
                judgment['conceptnet_validation']['relationship_confidence'] = valid_relationships / len(concepts) if concepts else 0.0
            
            # Adjust personality impact based on common sense validation
            if judgment['conceptnet_validation']['common_sense_score'] > 0.7:
                # High common sense confidence - boost thinking and intuition
                judgment['personality_impact']['decision']['thinking'] *= 1.1
                judgment['personality_impact']['collection']['intuition'] *= 1.1
            elif judgment['conceptnet_validation']['common_sense_score'] < 0.3:
                # Low common sense confidence - boost sensing and feeling
                judgment['personality_impact']['collection']['sensation'] *= 1.1
                judgment['personality_impact']['decision']['feeling'] *= 1.1
            
        except Exception as e:
            print(f"Error in ConceptNet judgment processing: {e}")
            judgment['conceptnet_validation'] = {
                'error': str(e),
                'common_sense_score': 0.0
            }

    def _process_personality_judgment(self, judgment: Dict, perception_data: Dict, event_data: Dict):
        """Process judgment based on cognitive functions and personality traits."""
        # Get active judgment functions based on context (only T and F functions)
        active_functions = self._determine_active_judgment_functions(perception_data, event_data)
        
        # Initialize impact values for each personality trait based on current preferences
        if "personality_preferences" in perception_data:
            preferences = perception_data["personality_preferences"]
            for trait, values in preferences.items():
                if trait not in judgment["personality_impact"]:
                    judgment["personality_impact"][trait] = {}
                for subtrait, value in values.items():
                    judgment["personality_impact"][trait][subtrait] = value
        
        # Adjust impacts based on neurotransmitter levels
        if "neurotransmitters" in perception_data:
            neurotransmitters = perception_data["neurotransmitters"]
            
            # Dopamine affects energy and motivation
            dopamine_level = neurotransmitters.get("dopamine", 0.5)
            if dopamine_level > 0.7:  # High dopamine
                judgment["personality_impact"]["energy"]["extrovert"] *= 1.2
                judgment["personality_impact"]["organize"]["perceiving"] *= 1.2
            elif dopamine_level < 0.3:  # Low dopamine
                judgment["personality_impact"]["energy"]["introvert"] *= 1.2
                judgment["personality_impact"]["organize"]["judging"] *= 1.2
            
            # Serotonin affects mood and social behavior
            serotonin_level = neurotransmitters.get("serotonin", 0.5)
            if serotonin_level > 0.7:  # High serotonin
                judgment["personality_impact"]["decision"]["feeling"] *= 1.2
            elif serotonin_level < 0.3:  # Low serotonin
                judgment["personality_impact"]["decision"]["thinking"] *= 1.2
            
            # Norepinephrine affects attention and focus
            norepinephrine_level = neurotransmitters.get("norepinephrine", 0.5)
            if norepinephrine_level > 0.7:  # High norepinephrine
                judgment["personality_impact"]["collection"]["sensation"] *= 1.2
            elif norepinephrine_level < 0.3:  # Low norepinephrine
                judgment["personality_impact"]["collection"]["intuition"] *= 1.2
            
            # Acetylcholine affects learning and memory
            acetylcholine_level = neurotransmitters.get("acetylcholine", 0.5)
            if acetylcholine_level > 0.7:  # High acetylcholine
                judgment["personality_impact"]["collection"]["intuition"] *= 1.1
                judgment["personality_impact"]["decision"]["thinking"] *= 1.1
            elif acetylcholine_level < 0.3:  # Low acetylcholine
                judgment["personality_impact"]["collection"]["sensation"] *= 1.1
                judgment["personality_impact"]["decision"]["feeling"] *= 1.1
        
        # Process MBTI function phases if available
        if "next_mbti_function_phase" in perception_data:
            mbti_phases = perception_data["next_mbti_function_phase"]
            
            # Update personality impacts based on MBTI phases
            if "introversion" in mbti_phases:
                judgment["personality_impact"]["energy"]["introvert"] *= 1.2
            if "extroversion" in mbti_phases:
                judgment["personality_impact"]["energy"]["extrovert"] *= 1.2
            if "intuition" in mbti_phases:
                judgment["personality_impact"]["collection"]["intuition"] *= 1.2
            if "sensation" in mbti_phases:
                judgment["personality_impact"]["collection"]["sensation"] *= 1.2
        
        # Normalize all personality impacts to ensure they sum to 1.0 for each trait
        for trait in judgment["personality_impact"]:
            total = sum(judgment["personality_impact"][trait].values())
            if total > 0:
                for subtrait in judgment["personality_impact"][trait]:
                    judgment["personality_impact"][trait][subtrait] /= total
        
        # Generate emotional response based on judgment process
        judgment["emotional_response"] = self._generate_emotional_response(judgment, perception_data, event_data)
        
        # Process needs and goals from perception data
        if "needs_considered" in perception_data:
            for need in perception_data["needs_considered"]:
                if need not in judgment["needs_impact"]:
                    judgment["needs_impact"][need] = 0.0
                judgment["needs_impact"][need] += 0.3
                
        if "goal_alignment" in perception_data:
            for goal in perception_data["goal_alignment"]:
                if goal not in judgment["goals_impact"]:
                    judgment["goals_impact"][goal] = 0.0
                judgment["goals_impact"][goal] += 0.3
        
        # Process proposed action if available
        if "proposed_action" in perception_data:
            action = perception_data["proposed_action"]
            if action.get("type") == "command":
                judgment["recommended_actions"].append(action.get("content", ""))
        
        # Process regular function-based judgment
        for function, effectiveness in active_functions.items():
            impact = 0.0
            
            # Process based on function type
            if function.startswith('F'):  # Feeling functions
                impact = self._process_feeling_judgment(function, effectiveness, perception_data, event_data)
                if function[0] == 'e':  # Extraverted Feeling
                    judgment["personality_impact"]["decision"]["feeling"] += impact
                else:  # Introverted Feeling
                    judgment["personality_impact"]["decision"]["feeling"] += impact
                
            elif function.startswith('T'):  # Thinking functions
                impact = self._process_thinking_judgment(function, effectiveness, perception_data, event_data)
                if function[0] == 'e':  # Extraverted Thinking
                    judgment["personality_impact"]["decision"]["thinking"] += impact
                else:  # Introverted Thinking
                    judgment["personality_impact"]["decision"]["thinking"] += impact
                
            # Note: N (Intuition) and S (Sensing) functions are now processed in perception phase

    def _determine_active_judgment_functions(self, perception_data: Dict, event_data: Dict) -> Dict:
        """
        Determine which judgment functions (T and F) should be active based on context.
        Returns dict of function codes and their current effectiveness.
        """
        active_functions = {}
        
        # Get base functions from cognitive stack
        for position, (function, base_effectiveness) in self.cognitive_functions.items():
            # Only process judgment functions (T and F)
            if function[1] in ['T', 'F']:
                # Modify effectiveness based on context
                effectiveness = base_effectiveness
                
                # External vs Internal focus adjustment
                is_external_focus = bool(perception_data.get('LocationCurrent')) or bool(event_data.get('people'))
                if (function[0] == 'e' and is_external_focus) or (function[0] == 'i' and not is_external_focus):
                    effectiveness *= 1.2
                else:
                    effectiveness *= 0.8
                    
                # Emotional vs Logical context adjustment
                has_emotional_context = bool(event_data.get('emotions'))
                if (function[1] in ['F'] and has_emotional_context) or (function[1] in ['T'] and not has_emotional_context):
                    effectiveness *= 1.2
                
                # Add to active functions if effectiveness is significant
                if effectiveness > 0.1:
                    active_functions[function] = min(1.0, effectiveness)
                    
        return active_functions

    def _process_dominant_judgment(self, perception_data: Dict, event_data: Dict, active_functions: Dict) -> Dict:
        """
        Process judgment through the dominant judgment function (Feeling or Thinking).
        This is the primary decision-making function according to Jungian theory.
        """
        judgment_scores = {}
        dominant_function = None
        dominant_effectiveness = 0.0
        
        # Determine dominant judgment function based on MBTI type
        if 'dominant' in self.cognitive_functions:
            dominant_function, dominant_effectiveness = self.cognitive_functions['dominant']
        
        if not dominant_function:
            print(f"⚠️ No dominant function found for MBTI type {self.mbti_type}")
            return judgment_scores
        
        print(f"🎯 DOMINANT JUDGMENT: Using {dominant_function} (effectiveness: {dominant_effectiveness})")
        
        # Process through dominant function
        if dominant_function in ['Fi', 'Fe']:
            # Feeling function - values over logic
            feeling_score = self._process_feeling_judgment(dominant_function, dominant_effectiveness, perception_data, event_data)
            judgment_scores['feeling_dominant'] = feeling_score
            judgment_scores['next_mbti_function_phase'] = f"Feeling ({dominant_function}) processed with score {feeling_score:.2f}"
            
        elif dominant_function in ['Ti', 'Te']:
            # Thinking function - logic over values
            thinking_score = self._process_thinking_judgment(dominant_function, dominant_effectiveness, perception_data, event_data)
            judgment_scores['thinking_dominant'] = thinking_score
            judgment_scores['next_mbti_function_phase'] = f"Thinking ({dominant_function}) processed with score {thinking_score:.2f}"
        
        return judgment_scores

    def _process_inferior_judgment(self, perception_data: Dict, event_data: Dict, active_functions: Dict) -> Dict:
        """
        Process judgment through inferior functions at reduced effectiveness.
        This represents the unconscious processing that still occurs but with less accuracy.
        """
        judgment_scores = {}
        inferior_functions = []
        
        # Get inferior functions for this MBTI type
        if 'inferior' in self.cognitive_functions:
            inferior_functions.append(self.cognitive_functions['inferior'])
        if 'tertiary' in self.cognitive_functions:
            inferior_functions.append(self.cognitive_functions['tertiary'])
        
        print(f"🔄 INFERIOR JUDGMENT: Processing {len(inferior_functions)} inferior functions")
        
        for function, effectiveness in inferior_functions:
            # Reduce effectiveness for inferior functions
            reduced_effectiveness = effectiveness * 0.5
            
            if function in ['Fi', 'Fe']:
                feeling_score = self._process_feeling_judgment(function, reduced_effectiveness, perception_data, event_data)
                judgment_scores[f'feeling_inferior_{function}'] = feeling_score
                
            elif function in ['Ti', 'Te']:
                thinking_score = self._process_thinking_judgment(function, reduced_effectiveness, perception_data, event_data)
                judgment_scores[f'thinking_inferior_{function}'] = thinking_score
                
            elif function in ['Ni', 'Ne']:
                intuition_score = self._process_intuition_judgment(function, reduced_effectiveness, perception_data, event_data)
                judgment_scores[f'intuition_inferior_{function}'] = intuition_score
                
            elif function in ['Si', 'Se']:
                sensing_score = self._process_sensing_judgment(function, reduced_effectiveness, perception_data, event_data)
                judgment_scores[f'sensing_inferior_{function}'] = sensing_score
        
        return judgment_scores

    def _generate_cognitive_summary(self, judgment: Dict, active_functions: Dict) -> Dict:
        """
        Generate a summary of cognitive processing for this judgment cycle.
        """
        summary = {
            'mbti_type': self.mbti_type,
            'dominant_function_used': None,
            'inferior_functions_processed': [],
            'judgment_approach': '',
            'personality_influence': '',
            'recommended_next_phase': ''
        }
        
        # Determine dominant function used
        if 'feeling_dominant' in judgment.get('judgment_scores', {}):
            summary['dominant_function_used'] = 'Feeling'
            summary['judgment_approach'] = 'Values-based decision making'
        elif 'thinking_dominant' in judgment.get('judgment_scores', {}):
            summary['dominant_function_used'] = 'Thinking'
            summary['judgment_approach'] = 'Logic-based decision making'
        
        # Identify inferior functions processed
        judgment_scores = judgment.get('judgment_scores', {})
        for key in judgment_scores:
            if 'inferior' in key:
                summary['inferior_functions_processed'].append(key)
        
        # Determine personality influence
        if self.mbti_type.startswith('I'):
            summary['personality_influence'] = 'Introverted processing - internal reflection'
        else:
            summary['personality_influence'] = 'Extraverted processing - external engagement'
        
        # Recommend next phase
        if summary['dominant_function_used'] == 'Feeling':
            summary['recommended_next_phase'] = 'Focus on emotional connection and values alignment'
        else:
            summary['recommended_next_phase'] = 'Focus on logical analysis and systematic approach'
        
        return summary

    def _process_feeling_judgment(self, function: str, effectiveness: float, perception_data: Dict, event_data: Dict) -> float:
        """
        Process judgment using feeling functions (Fi/Fe).
        Feeling prefers values over logic - focuses on personal values, harmony, and emotional impact.
        """
        impact = 0.0
        
        if function == 'Fi':  # Introverted Feeling
            # Internal value system - personal values and authenticity
            print(f"💙 Fi (Introverted Feeling): Evaluating against personal values")
            
            # Check alignment with personal needs and goals
            for need in self.needs:
                if need.lower() in str(event_data.get('WHAT', '')).lower():
                    impact += 0.3 * effectiveness
                    print(f"   ✓ Aligns with need: {need}")
            
            for goal in self.goals:
                if goal.lower() in str(event_data.get('WHAT', '')).lower():
                    impact += 0.2 * effectiveness
                    print(f"   ✓ Supports goal: {goal}")
            
            # Check emotional resonance
            if event_data.get('emotions'):
                impact += 0.2 * effectiveness
                print(f"   ✓ Emotional context detected")
                
        else:  # Fe - Extraverted Feeling
            # External harmony - others' emotions and social values
            print(f"💙 Fe (Extraverted Feeling): Evaluating social harmony and others' emotions")
            
            # Focus on external emotional impact
            if event_data.get('emotions'):
                impact += 0.4 * effectiveness
                print(f"   ✓ External emotions detected")
            
            # Check for social harmony indicators
            if 'people' in str(event_data).lower() or 'friend' in str(event_data).lower():
                impact += 0.3 * effectiveness
                print(f"   ✓ Social context detected")
                
        print(f"   📊 Feeling impact score: {impact:.2f}")
        return impact

    def _process_thinking_judgment(self, function: str, effectiveness: float, perception_data: Dict, event_data: Dict) -> float:
        """
        Process judgment using thinking functions (Ti/Te).
        Thinking prefers logic over values - focuses on logical consistency and systematic analysis.
        """
        impact = 0.0
        
        if function == 'Ti':  # Introverted Thinking
            # Internal logical consistency - personal logical framework
            print(f"🧠 Ti (Introverted Thinking): Analyzing internal logical consistency")
            
            # Check for logical reasoning opportunities
            if event_data.get('WHY') or event_data.get('HOW'):
                impact += 0.3 * effectiveness
                print(f"   ✓ Logical reasoning context detected")
            
            # Check for systematic analysis needs
            if event_data.get('nouns') and len(event_data.get('nouns', [])) > 1:
                impact += 0.2 * effectiveness
                print(f"   ✓ Multiple concepts for analysis")
            
            # Check for internal consistency
            if perception_data.get('TrustValue', 0.5) > 0.7:
                impact += 0.2 * effectiveness
                print(f"   ✓ High trust context - logical consistency important")
                
        else:  # Te - Extraverted Thinking
            # External systems and efficiency - objective analysis
            print(f"🧠 Te (Extraverted Thinking): Evaluating external systems and efficiency")
            
            # Focus on external logical frameworks
            if perception_data.get('CommonInterests'):
                impact += 0.3 * effectiveness
                print(f"   ✓ Common interests - systematic approach beneficial")
            
            # Check for efficiency opportunities
            if 'test' in str(event_data).lower() or 'evaluate' in str(event_data).lower():
                impact += 0.3 * effectiveness
                print(f"   ✓ Testing/evaluation context - efficiency focus")
            
            # Check for objective analysis needs
            if event_data.get('WHERE') or event_data.get('WHEN'):
                impact += 0.2 * effectiveness
                print(f"   ✓ Objective context (where/when) detected")
                
        print(f"   📊 Thinking impact score: {impact:.2f}")
        return impact

    def _process_intuition_judgment(self, function: str, effectiveness: float, perception_data: Dict, event_data: Dict) -> float:
        """
        Process judgment using intuition functions (Ni/Ne).
        Intuition prefers possibilities and patterns over concrete details.
        """
        impact = 0.0
        
        if function == 'Ni':  # Introverted Intuition
            # Look for patterns and future implications
            print(f"🔮 Ni (Introverted Intuition): Analyzing patterns and future implications")
            
            if event_data.get('WHY') or event_data.get('EXPECTATION'):
                impact += 0.3 * effectiveness
                print(f"   ✓ Future-oriented context detected")
            
            # Check for pattern recognition opportunities
            if event_data.get('nouns') and len(event_data.get('nouns', [])) > 2:
                impact += 0.2 * effectiveness
                print(f"   ✓ Multiple concepts for pattern analysis")
                
        else:  # Ne - Extraverted Intuition
            # Generate possibilities and connections
            print(f"🔮 Ne (Extraverted Intuition): Generating possibilities and connections")
            
            if perception_data.get('CommonInterests'):
                impact += 0.3 * effectiveness
                print(f"   ✓ Common interests - connection opportunities")
            
            # Check for exploration opportunities
            if 'explore' in str(event_data).lower() or 'discover' in str(event_data).lower():
                impact += 0.3 * effectiveness
                print(f"   ✓ Exploration context detected")
                
        print(f"   📊 Intuition impact score: {impact:.2f}")
        return impact

    def _process_sensing_judgment(self, function: str, effectiveness: float, perception_data: Dict, event_data: Dict) -> float:
        """
        Process judgment using sensing functions (Si/Se).
        Sensing prefers concrete details and immediate experience over abstract possibilities.
        """
        impact = 0.0
        
        if function == 'Si':  # Introverted Sensing
            # Compare with past experiences and details
            print(f"👁️ Si (Introverted Sensing): Comparing with past experiences and details")
            
            if event_data.get('WHERE') or event_data.get('WHEN'):
                impact += 0.3 * effectiveness
                print(f"   ✓ Specific context (where/when) detected")
            
            # Check for detail-oriented processing
            if event_data.get('nouns') and len(event_data.get('nouns', [])) > 0:
                impact += 0.2 * effectiveness
                print(f"   ✓ Concrete details available for processing")
                
        else:  # Se - Extraverted Sensing
            # Focus on immediate sensory input and action
            print(f"👁️ Se (Extraverted Sensing): Focusing on immediate sensory input and action")
            
            if event_data.get('nouns') and any('action' in str(noun).lower() for noun in event_data['nouns']):
                impact += 0.3 * effectiveness
                print(f"   ✓ Action-oriented context detected")
            
            # Check for immediate experience opportunities
            if 'test' in str(event_data).lower() or 'try' in str(event_data).lower():
                impact += 0.3 * effectiveness
                print(f"   ✓ Immediate experience context detected")
                
        print(f"   📊 Sensing impact score: {impact:.2f}")
        return impact

    def _process_needs_judgment(self, judgment: Dict, perception_data: Dict, event_data: Dict):
        """Process judgment based on needs and their satisfaction."""
        # Get attention bias from judgment context
        attention_context = judgment.get("attention_context", {})
        outer_bias = attention_context.get("outer_bias", 0.0)
        
        for need in self.needs:
            need_impact = 0.0
            
            # Check if need is satisfied in perception data
            if need in perception_data.get('CommonInterests', []):
                need_impact += 0.3
                
            # Check if need is threatened
            if need in self.fears and any(fear in str(event_data.get('WHAT', '')).lower() 
                                        for fear in self.fears):
                need_impact -= 0.4
                
            # Check if need aligns with hopes
            if need in self.hopes and any(hope in str(event_data.get('WHAT', '')).lower() 
                                        for hope in self.hopes):
                need_impact += 0.3
            
            # 🎯 ATTENTION SYSTEM: Apply outer bias to reduce inner exploration when outer focus dominates
            if need == "play_explore_inner" and outer_bias > 0.0:
                need_impact = max(0.0, need_impact - outer_bias)
                print(f"   🎯 Reduced inner exploration need due to outer focus: {outer_bias:.2f}")
                
            judgment["needs_impact"][need] = need_impact

    def _process_goals_judgment(self, judgment: Dict, perception_data: Dict, event_data: Dict):
        """Process judgment based on goals and their progress."""
        for goal in self.goals:
            goal_impact = 0.0
            
            # Check if goal is supported by perception
            if goal in perception_data.get('CommonInterests', []):
                goal_impact += 0.3
                
            # Check if goal is threatened
            if goal in self.fears and any(fear in str(event_data.get('WHAT', '')).lower() 
                                        for fear in self.fears):
                goal_impact -= 0.4
                
            # Check if goal aligns with hopes
            if goal in self.hopes and any(hope in str(event_data.get('WHAT', '')).lower() 
                                        for hope in self.hopes):
                goal_impact += 0.3
                
            judgment["goals_impact"][goal] = goal_impact

    def _calculate_interaction_priority(self, judgment: Dict) -> float:
        """Calculate final interaction priority based on all factors."""
        # Base priority from trust
        base_priority = judgment["trust_assessment"] * 0.3
        
        # Add personality impact
        personality_impact = 0.0
        for trait_category in judgment["personality_impact"].values():
            for trait_value in trait_category.values():
                personality_impact += trait_value * 0.2
        
        # Add needs impact
        needs_impact = sum(impact * 0.2 for impact in judgment["needs_impact"].values())
        
        # Add goals impact
        goals_impact = sum(impact * 0.2 for impact in judgment["goals_impact"].values())
        
        return max(0.0, min(1.0, base_priority + personality_impact + needs_impact + goals_impact))

    def _generate_recommended_actions(self, judgment: Dict, perception_data: Dict, event_data: Dict):
        """Generate recommended actions based on judgment results."""
        # Initialize recommended actions list
        judgment["recommended_actions"] = []
        
        # Add proposed action from perception if available
        if "proposed_action" in perception_data:
            action = perception_data["proposed_action"]
            if action.get("type") == "command":
                judgment["recommended_actions"].append(action.get("content", ""))
        
        # Add actions based on relevant experience
        if "relevant_experience" in perception_data:
            experience = perception_data["relevant_experience"]
            if "skills_activated" in experience:
                for skill in experience["skills_activated"]:
                    judgment["recommended_actions"].append(f"practice_{skill}")
            if "concepts_used" in experience:
                for concept in experience["concepts_used"]:
                    judgment["recommended_actions"].append(f"explore_{concept}")
        
        # Add personality-based actions
        if judgment["personality_impact"]["energy"]["introvert"] > 0.7:
            judgment["recommended_actions"].append("maintain_social_distance")
        elif judgment["personality_impact"]["energy"]["extrovert"] > 0.7:
            judgment["recommended_actions"].append("engage_socially")
            
        # Add needs-based actions
        for need, impact in judgment["needs_impact"].items():
            if impact < -0.3:
                judgment["recommended_actions"].append(f"address_need_{need}")
            elif impact > 0.3:
                judgment["recommended_actions"].append(f"pursue_need_{need}")
                
        # Add goals-based actions
        for goal, impact in judgment["goals_impact"].items():
            if impact > 0.3:
                judgment["recommended_actions"].append(f"pursue_goal_{goal}")
                
        # Add context-specific actions
        if judgment["interaction_priority"] > 0.7:
            judgment["recommended_actions"].append("engage_in_deep_conversation")
        if len(perception_data.get('CommonInterests', [])) > 0:
            judgment["recommended_actions"].append("share_interests")
        if perception_data.get('LocationCurrent'):
            judgment["recommended_actions"].append("discuss_location")
            
        # Add emotional response actions
        if "emotional_response" in judgment and judgment["emotional_response"]:
            emotion = judgment["emotional_response"].get("primary_emotion", "")
            if emotion:
                judgment["recommended_actions"].append(f"express_{emotion}")

    def update_personality(self, new_values: Dict):
        """Update personality traits based on learning and experience."""
        for trait, values in new_values.items():
            if trait in self.personality_traits:
                for subtrait, value in values.items():
                    if subtrait in self.personality_traits[trait]:
                        self.personality_traits[trait][subtrait] = max(0.0, min(1.0, value))
        
        # Save updated personality to settings
        self._save_personality_settings()

    def evaluate_vision(self, object_label: str, confidence: float) -> Dict:
        """
        Evaluate vision input and generate judgment.
        
        Args:
            object_label: The label/name of the detected object
            confidence: Confidence score of the detection
            
        Returns:
            Dict containing judgment results
        """
        try:
            # Create perception data structure
            perception_data = {
                'object_label': object_label,
                'confidence': confidence,
                'perception_type': 'vision',
                'timestamp': datetime.now().isoformat()
            }
            
            # Create event data structure
            event_data = {
                'type': 'vision_detection',
                'object': object_label,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
            
            # Use the existing judgment system
            judgment_result = self.judge_input(perception_data, event_data)
            
            # Add vision-specific processing
            judgment_result['vision_specific'] = {
                'object_recognized': object_label,
                'recognition_confidence': confidence,
                'requires_attention': confidence > 0.7,
                'emotional_impact': self._assess_vision_emotional_impact(object_label, confidence)
            }
            
            return judgment_result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'vision_specific': {
                    'object_recognized': object_label,
                    'recognition_confidence': confidence,
                    'requires_attention': False,
                    'emotional_impact': 'neutral'
                }
            }
    
    def _assess_vision_emotional_impact(self, object_label: str, confidence: float) -> str:
        """Assess the emotional impact of a vision detection."""
        try:
            # Check if object is related to needs/goals/fears/hopes
            object_lower = object_label.lower()
            
            # Check needs
            for need in self.needs:
                if need.lower() in object_lower or object_lower in need.lower():
                    return 'positive' if confidence > 0.7 else 'neutral'
            
            # Check goals
            for goal in self.goals:
                if goal.lower() in object_lower or object_lower in goal.lower():
                    return 'positive' if confidence > 0.7 else 'neutral'
            
            # Check fears
            for fear in self.fears:
                if fear.lower() in object_lower or object_lower in fear.lower():
                    return 'negative' if confidence > 0.7 else 'neutral'
            
            # Check hopes
            for hope in self.hopes:
                if hope.lower() in object_lower or object_lower in hope.lower():
                    return 'positive' if confidence > 0.7 else 'neutral'
            
            # Default to neutral for unknown objects
            return 'neutral'
            
        except Exception as e:
            return 'neutral'
    
    def _save_personality_settings(self):
        """Save current personality settings to the config file."""
        for trait, values in self.personality_traits.items():
            for subtrait, value in values.items():
                self.config.set('personality', subtrait, str(value))
        
        with open('settings_current.ini', 'w') as configfile:
            self.config.write(configfile)
    
    def _process_earthly_game_suggestions(self, judgment: Dict, perception_data: Dict, event_data: Dict):
        """
        Process earthly game suggestions and integrate them into judgment.
        
        Args:
            judgment: Current judgment dictionary
            perception_data: Perception data
            event_data: Event data
        """
        try:
            # Get earthly game engine if available
            eg = getattr(self.main_app, "earthly_game", None)
            if not eg:
                return
            
            # Get current need levels from judgment
            current_need_levels = {
                "safety": judgment.get("needs_impact", {}).get("safety", 0.5),
                "achievement": judgment.get("needs_impact", {}).get("achievement", 0.5),
                "affiliation": judgment.get("needs_impact", {}).get("affiliation", 0.5),
                "health": judgment.get("needs_impact", {}).get("health", 0.5),
                "learning": judgment.get("needs_impact", {}).get("learning", 0.5)
            }
            
            # Get suggestion from earthly game engine
            suggestion = eg.suggest_action(need_levels=current_need_levels)
            
            # 🔧 FIX: Log game reasoning event for suggestion processing
            if hasattr(self.main_app, 'consciousness_evaluation'):
                consciousness_eval = self.main_app.consciousness_evaluation
                if hasattr(consciousness_eval, 'increment_pdb_counter'):
                    consciousness_eval.increment_pdb_counter('game_reasoning', strength=1.0)
                    self.logger.info(f"🎮 Game Reasoning: Suggestion processing logged")
            
            # Add earthly suggestion to judgment
            judgment["earthly_suggestion"] = suggestion
            
            # Log the suggestion
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log(f"🧭 Earthly suggestion: {suggestion}")
            
            # Add earthly suggestion to event data for action system
            if hasattr(event_data, 'earthly_suggestion'):
                event_data.earthly_suggestion = suggestion
            elif isinstance(event_data, dict):
                event_data['earthly_suggestion'] = suggestion
                
        except Exception as e:
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log(f"❌ Error processing earthly game suggestions: {e}")
            print(f"❌ Error processing earthly game suggestions: {e}")
    
    def generate_openai_response(self, user_input: str, context: Dict = None) -> Optional[str]:
        """
        Generate a random/creative response using OpenAI as fallback.
        
        Args:
            user_input: The user's input text
            context: Additional context information
            
        Returns:
            OpenAI-generated response with [[random_action]] tag, or None if failed
        """
        try:
            if not openai_available or not self.openai_random_enabled or not self.openai_api_key:
                return None
            
            # Create a creative prompt for random responses
            prompt = f"""You are CARL, an AI with personality. The user said: "{user_input}"

Generate a creative, random, or unexpected response. Be playful, curious, or philosophical. 
The response should be tagged with [[random_action]] at the start.

Examples:
- "[[random_action]] Maybe in their own tiny alien minds!"
- "[[random_action]] That reminds me of a dream I had about dancing robots..."
- "[[random_action]] I wonder if trees have conversations when we're not looking..."

Keep it under 100 characters and make it feel spontaneous and creative."""

            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are CARL, a creative AI with a playful personality."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.9,  # High creativity
                top_p=0.9
            )
            
            # Extract response
            openai_response = response.choices[0].message.content.strip()
            
            # Ensure it has the random action tag
            if not openai_response.startswith("[[random_action]]"):
                openai_response = f"[[random_action]] {openai_response}"
            
            # Log the OpenAI fallback with detailed information
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log(f"🤖 OpenAI fallback response: {openai_response}")
            
            # Enhanced logging for learning integration
            self.logger.info(f"🎲 OpenAI fallback generated: '{user_input}' -> '{openai_response}' (confidence: 0.6, type: random)")
            
            return openai_response
            
        except Exception as e:
            print(f"Error generating OpenAI response: {e}")
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log(f"❌ Error generating OpenAI response: {e}")
            return None
    
    def process_openai_fallback(self, user_input: str, context: Dict = None) -> Dict:
        """
        Process OpenAI fallback and prepare for learning integration.
        
        Args:
            user_input: The user's input text
            context: Additional context information
            
        Returns:
            Dict containing OpenAI response and metadata
        """
        try:
            # Generate OpenAI response
            openai_response = self.generate_openai_response(user_input, context)
            
            if openai_response:
                # Log to memory system if available
                if hasattr(self.main_app, 'memory_system') and self.main_app.memory_system:
                    self.main_app.memory_system.store_memory(
                        content=f"OpenAI fallback: {user_input} -> {openai_response}",
                        memory_type="working",
                        context=None,  # Will be created by memory system
                        importance=0.4,
                        source="openai_fallback"
                    )
                
                return {
                    'response': openai_response,
                    'source': 'openai',
                    'confidence': 0.6,  # Lower confidence for random responses
                    'processing_time': 2.0,  # Slower than reflexes
                    'response_type': 'random',
                    'origin': 'openai',
                    'learnable': True
                }
            
            return None
            
        except Exception as e:
            print(f"Error processing OpenAI fallback: {e}")
            return None

# Example usage
if __name__ == "__main__":
    judgment_system = JudgmentSystem()
    
    # Example perception and event data
    perception_data = {
        "PreferredFunction": 0,
        "Name": "John Doe",
        "TrustValue": 0.8,
        "LocationCurrent": "New York",
        "CommonInterests": ["Learning", "Technology"],
        "interaction_count": 5
    }
    
    event_data = {
        "WHAT": "Learning about new technology",
        "emotions": {
            "joy": 0.7,
            "surprise": 0.3
        }
    }
    
    # Process judgment
    judgment_result = judgment_system.judge_input(perception_data, event_data)
    print("Judgment Result:", json.dumps(judgment_result, indent=2)) 