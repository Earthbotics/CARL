import os
import json
import configparser
from datetime import datetime
from typing import Dict, List, Optional
import shutil
from aiml_reflex_layer import AIMLReflexEngine, AIMLReflexIntegration

class PerceptionSystem:
    def __init__(self, main_app=None):
        # Define base directories
        self.base_dirs = {
            'people': 'people',
            'places': 'places',
            'things': 'things',
            'needs': 'needs',
            'goals': 'goals',
            'skills': 'skills',
            'concepts': 'concepts'
        }
        
        # Define image directories
        self.image_dirs = {
            'outerworld': os.path.join('bin', 'images', 'outerworld'),
            'innerworld': os.path.join('bin', 'images', 'innerworld')
        }
        
        # Create necessary directories
        self._create_directories()
        
        # Initialize configuration
        self.config = configparser.ConfigParser()
        self.main_app = main_app
        
        # Load personality settings
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
        
        # 🔧 FIX: Add game focus mode for Game Active → Game Priority Processing → Minimal Cognitive Functions → Game State Maintenance pipeline
        self.game_focus_mode = False
        
        # Initialize fears and hopes
        self.fears = [fear.strip() for fear in self.config.get('personality-favorites', 'fears', fallback='').split(',')]
        self.hopes = [hope.strip() for hope in self.config.get('personality-favorites', 'hopes', fallback='').split(',')]
        
        # Initialize AIML reflex system
        self.aiml_enabled = self.config.getboolean('AIML', 'enable', fallback=True)
        self.openai_random_enabled = self.config.getboolean('AIML', 'openai_random_enabled', fallback=True)
        self.aiml_dynamic_path = self.config.get('AIML', 'aiml_dynamic_path', fallback='./aiml/dynamic.aiml')
        
        if self.aiml_enabled:
            self.aiml_engine = AIMLReflexEngine(aiml_dir='./aiml')
            self.aiml_integration = AIMLReflexIntegration(
                aiml_engine=self.aiml_engine,
                memory_system=getattr(main_app, 'memory_system', None) if main_app else None,
                concept_system=getattr(main_app, 'concept_system', None) if main_app else None
            )
        else:
            self.aiml_engine = None
            self.aiml_integration = None

    def _initialize_cognitive_functions(self):
        """
        Initialize cognitive functions based on MBTI type.
        Returns dict with function positions and effectiveness scores.
        """
        # MBTI cognitive function mapping
        function_map = {
            'INTP': {
                'dominant': ('Ti', 0.9),    # Introverted Thinking
                'auxiliary': ('Ne', 0.8),   # Extraverted Intuition
                'tertiary': ('Si', 0.6),    # Introverted Sensing
                'inferior': ('Fe', 0.4)     # Extraverted Feeling
            },
            'ISFP': {
                'dominant': ('Fi', 0.9),    # Introverted Feeling
                'auxiliary': ('Se', 0.8),   # Extraverted Sensing
                'tertiary': ('Ni', 0.6),    # Introverted Intuition
                'inferior': ('Te', 0.4)     # Extraverted Thinking
            },
            'INFP': {
                'dominant': ('Fi', 0.9),    # Introverted Feeling
                'auxiliary': ('Ne', 0.8),   # Extraverted Intuition
                'tertiary': ('Si', 0.6),    # Introverted Sensing
                'inferior': ('Te', 0.4)     # Extraverted Thinking
            },
            'INFJ': {
                'dominant': ('Ni', 0.9),    # Introverted Intuition
                'auxiliary': ('Fe', 0.8),   # Extraverted Feeling
                'tertiary': ('Ti', 0.6),    # Introverted Thinking
                'inferior': ('Se', 0.4)     # Extraverted Sensing
            },
            'INTJ': {
                'dominant': ('Ni', 0.9),    # Introverted Intuition
                'auxiliary': ('Te', 0.8),   # Extraverted Thinking
                'tertiary': ('Fi', 0.6),    # Introverted Feeling
                'inferior': ('Se', 0.4)     # Extraverted Sensing
            },
            'ISTP': {
                'dominant': ('Ti', 0.9),    # Introverted Thinking
                'auxiliary': ('Se', 0.8),   # Extraverted Sensing
                'tertiary': ('Ni', 0.6),    # Introverted Intuition
                'inferior': ('Fe', 0.4)     # Extraverted Feeling
            },
            'ISTJ': {
                'dominant': ('Si', 0.9),    # Introverted Sensing
                'auxiliary': ('Te', 0.8),   # Extraverted Thinking
                'tertiary': ('Fi', 0.6),    # Introverted Feeling
                'inferior': ('Ne', 0.4)     # Extraverted Intuition
            },
            'ISFJ': {
                'dominant': ('Si', 0.9),    # Introverted Sensing
                'auxiliary': ('Fe', 0.8),   # Extraverted Feeling
                'tertiary': ('Ti', 0.6),    # Introverted Thinking
                'inferior': ('Ne', 0.4)     # Extraverted Intuition
            },
            'ENFP': {
                'dominant': ('Ne', 0.9),    # Extraverted Intuition
                'auxiliary': ('Fi', 0.8),   # Introverted Feeling
                'tertiary': ('Te', 0.6),    # Extraverted Thinking
                'inferior': ('Si', 0.4)     # Introverted Sensing
            },
            'ENTP': {
                'dominant': ('Ne', 0.9),    # Extraverted Intuition
                'auxiliary': ('Ti', 0.8),   # Introverted Thinking
                'tertiary': ('Fe', 0.6),    # Extraverted Feeling
                'inferior': ('Si', 0.4)     # Introverted Sensing
            },
            'ENFJ': {
                'dominant': ('Fe', 0.9),    # Extraverted Feeling
                'auxiliary': ('Ni', 0.8),   # Introverted Intuition
                'tertiary': ('Se', 0.6),    # Extraverted Sensing
                'inferior': ('Ti', 0.4)     # Introverted Thinking
            },
            'ENTJ': {
                'dominant': ('Te', 0.9),    # Extraverted Thinking
                'auxiliary': ('Ni', 0.8),   # Introverted Intuition
                'tertiary': ('Se', 0.6),    # Extraverted Sensing
                'inferior': ('Fi', 0.4)     # Introverted Feeling
            },
            'ESFP': {
                'dominant': ('Se', 0.9),    # Extraverted Sensing
                'auxiliary': ('Fi', 0.8),   # Introverted Feeling
                'tertiary': ('Te', 0.6),    # Extraverted Thinking
                'inferior': ('Ni', 0.4)     # Introverted Intuition
            },
            'ESTP': {
                'dominant': ('Se', 0.9),    # Extraverted Sensing
                'auxiliary': ('Ti', 0.8),   # Introverted Thinking
                'tertiary': ('Fe', 0.6),    # Extraverted Feeling
                'inferior': ('Ni', 0.4)     # Introverted Intuition
            },
            'ESFJ': {
                'dominant': ('Fe', 0.9),    # Extraverted Feeling
                'auxiliary': ('Si', 0.8),   # Introverted Sensing
                'tertiary': ('Ne', 0.6),    # Extraverted Intuition
                'inferior': ('Ti', 0.4)     # Introverted Thinking
            },
            'ESTJ': {
                'dominant': ('Te', 0.9),    # Extraverted Thinking
                'auxiliary': ('Si', 0.8),   # Introverted Sensing
                'tertiary': ('Ne', 0.6),    # Extraverted Intuition
                'inferior': ('Fi', 0.4)     # Introverted Feeling
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
        
        # Ensure we have some default values if all are zero
        if traits["collection"]["intuition"] + traits["collection"]["sensation"] == 0:
            traits["collection"]["intuition"] = 0.8
            traits["collection"]["sensation"] = 0.2
            
        if traits["decision"]["thinking"] + traits["decision"]["feeling"] == 0:
            traits["decision"]["thinking"] = 0.9
            traits["decision"]["feeling"] = 0.1
        
        # Normalize all preferences to [0,1] range
        for category in traits:
            total = sum(traits[category].values())
            if total > 0:
                for key in traits[category]:
                    traits[category][key] /= total
                    
        return traits

    def _create_directories(self):
        """Create all necessary directories if they don't exist."""
        # Create base directories
        for dir_name, dir_path in self.base_dirs.items():
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Created directory: {dir_path}")
        
        # Create image directories
        for dir_name, dir_path in self.image_dirs.items():
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Created image directory: {dir_path}")

    def perceive_entity(self, entity_type: str, entity_data: Dict) -> Dict:
        """
        Perceive and process a new entity (person, place, or thing).
        
        Args:
            entity_type: Type of entity ('person', 'place', or 'thing')
            entity_data: Dictionary containing entity information
            
        Returns:
            Dict containing perception results and cross-references
        """
        try:
            # Create entity directory if it doesn't exist
            entity_dir = self.base_dirs[entity_type + 's']
            if not os.path.exists(entity_dir):
                os.makedirs(entity_dir)

            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            entity_name = entity_data.get('Name', 'unknown').lower().replace(' ', '_')
            filename = f"{entity_name}_{timestamp}.json"
            filepath = os.path.join(entity_dir, filename)

            # Add standard fields
            entity_data.update({
                "created_at": str(datetime.now()),
                "last_updated": str(datetime.now()),
                "cross_references": {
                    "needs": [],
                    "goals": [],
                    "skills": [],
                    "concepts": []
                }
            })

            # Handle image file path for people
            if entity_type == 'person' and 'ImageFilePath' in entity_data:
                # Determine if this is an outerworld or innerworld image
                image_type = 'outerworld' if entity_data.get('LocationCurrent') else 'innerworld'
                image_dir = os.path.join(self.image_dirs[image_type], entity_name)
                
                # Create the specific image directory if it doesn't exist
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)
                
                # Update the ImageFilePath with the full path
                entity_data['ImageFilePath'] = image_dir
                
                # Add image type information
                entity_data['ImageType'] = image_type

            # Cross-reference with existing needs, goals, and skills
            self._cross_reference_entity(entity_data)

            # Save entity data
            with open(filepath, 'w') as f:
                json.dump(entity_data, f, indent=2)

            # Cross-reference with other systems
            self._cross_reference_entity(entity_data)

            return {
                "success": True,
                "entity_type": entity_type,
                "filepath": filepath,
                "entity_data": entity_data
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "entity_type": entity_type
            }

    def process_vision(self, object_label: str, confidence: float) -> Dict:
        """
        Process vision input and create perception data.
        
        Args:
            object_label: Label of the detected object
            confidence: Confidence score of the detection
            
        Returns:
            Dict containing vision processing results
        """
        try:
            # Create vision perception data
            vision_data = {
                "object_label": object_label,
                "confidence": confidence,
                "timestamp": str(datetime.now()),
                "perception_type": "vision",
                "cross_references": {
                    "needs": [],
                    "goals": [],
                    "skills": [],
                    "concepts": []
                }
            }
            
            # Cross-reference with existing concepts
            self._cross_reference_entity(vision_data)
            
            return {
                "success": True,
                "vision_data": vision_data,
                "object_label": object_label,
                "confidence": confidence
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "object_label": object_label
            }

    def process_personality_functions(self, perception_data: Dict, event_data: Dict) -> Dict:
        """
        Process personality functions during the perception phase (40% of processing time).
        This includes extroversion, introversion, intuition, and sensation functions.
        
        Args:
            perception_data: Dictionary containing perception results
            event_data: Dictionary containing event data including emotions, intent, etc.
            
        Returns:
            Dict containing personality processing results
        """
        try:
            print(f"🧠 PERCEPTION PHASE: Processing personality functions for MBTI type {self.mbti_type}")
            
            personality_result = {
                "timestamp": str(datetime.now()),
                "mbti_type": self.mbti_type,
                "personality_impact": {
                    "energy": {"extrovert": 0.0, "introvert": 0.0},
                    "collection": {"intuition": 0.0, "sensation": 0.0},
                    "decision": {"thinking": 0.0, "feeling": 0.0},
                    "organize": {"judging": 0.0, "perceiving": 0.0}
                },
                "perception_processing": {
                    "extroversion_energy": 0.0,
                    "introversion_energy": 0.0,
                    "intuition_level": 0.0,
                    "sensation_level": 0.0
                },
                "active_functions": {},
                "next_phase": "judgment"
            }

            # Determine which cognitive functions are most active for this input
            active_functions = self._determine_active_perception_functions(perception_data, event_data)
            personality_result['active_functions'] = active_functions
            
            # Process perception functions (40% of processing time)
            for function, effectiveness in active_functions.items():
                impact = 0.0
                
                # Process based on function type
                if function.startswith('N'):  # Intuition functions
                    impact = self._process_intuition_perception(function, effectiveness, perception_data, event_data)
                    if function[1] == 'e':  # Extraverted Intuition
                        personality_result["personality_impact"]["collection"]["intuition"] += impact
                        personality_result["perception_processing"]["intuition_level"] += impact
                    else:  # Introverted Intuition
                        personality_result["personality_impact"]["collection"]["intuition"] += impact
                        personality_result["perception_processing"]["intuition_level"] += impact
                        
                elif function.startswith('S'):  # Sensing functions
                    impact = self._process_sensing_perception(function, effectiveness, perception_data, event_data)
                    if function[1] == 'e':  # Extraverted Sensing
                        personality_result["personality_impact"]["collection"]["sensation"] += impact
                        personality_result["perception_processing"]["sensation_level"] += impact
                    else:  # Introverted Sensing
                        personality_result["personality_impact"]["collection"]["sensation"] += impact
                        personality_result["perception_processing"]["sensation_level"] += impact
                
                # Update energy preferences based on function attitude
                if function[1] == 'e':  # Extraverted functions
                    personality_result["personality_impact"]["energy"]["extrovert"] += impact
                    personality_result["perception_processing"]["extroversion_energy"] += impact
                else:  # Introverted functions
                    personality_result["personality_impact"]["energy"]["introvert"] += impact
                    personality_result["perception_processing"]["introversion_energy"] += impact

            return personality_result

        except Exception as e:
            print(f"Error in process_personality_functions: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": str(datetime.now())
            }

    def _determine_active_perception_functions(self, perception_data: Dict, event_data: Dict) -> Dict:
        """
        Determine which cognitive functions should be active during perception phase.
        Returns dict of function codes and their current effectiveness.
        """
        active_functions = {}
        
        # Get base functions from cognitive stack
        for position, (function, base_effectiveness) in self.cognitive_functions.items():
            # Modify effectiveness based on context
            effectiveness = base_effectiveness
            
            # Focus on perception functions (N and S functions)
            if function[0] in ['N', 'S']:
                # External vs Internal focus adjustment
                is_external_focus = bool(perception_data.get('LocationCurrent')) or bool(event_data.get('people'))
                if (function[1] == 'e' and is_external_focus) or (function[1] == 'i' and not is_external_focus):
                    effectiveness *= 1.2
                else:
                    effectiveness *= 0.8
                    
                # Add to active functions if effectiveness is significant
                if effectiveness > 0.1:
                    active_functions[function] = min(1.0, effectiveness)
                    
        return active_functions

    def _process_intuition_perception(self, function: str, effectiveness: float, perception_data: Dict, event_data: Dict) -> float:
        """
        Process perception using intuition functions (Ni/Ne).
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
                
        print(f"   📊 Intuition perception impact score: {impact:.2f}")
        return impact

    def _process_sensing_perception(self, function: str, effectiveness: float, perception_data: Dict, event_data: Dict) -> float:
        """
        Process perception using sensing functions (Si/Se).
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
                
        print(f"   📊 Sensing perception impact score: {impact:.2f}")
        return impact

    def _cross_reference_entity(self, entity_data: Dict):
        """Cross-reference entity with existing needs, goals, and skills."""
        try:
            # Get all existing needs, goals, and skills
            needs = self._load_system_files('needs')
            goals = self._load_system_files('goals')
            skills = self._load_system_files('skills')
            concepts = self._load_system_files('concepts')

            # Get entity information for cross-referencing
            interests = entity_data.get('CommonInterests', [])
            location = entity_data.get('LocationCurrent', '').lower()
            name = entity_data.get('Name', '').lower()
            object_label = entity_data.get('object_label', '').lower()
            
            # Create a list of all searchable terms
            search_terms = []
            if interests:
                search_terms.extend([interest.lower() for interest in interests])
            if location:
                search_terms.append(location)
            if name:
                search_terms.append(name)
            if object_label:
                search_terms.append(object_label)
            
            # If no search terms found, use the object label as default
            if not search_terms and object_label:
                search_terms = [object_label]

            # Enhanced cross-referencing with broader matching
            # Cross-reference needs with multiple field matching
            for need_name, need_data in needs.items():
                need_concepts = need_data.get('Concepts', [])
                need_description = need_data.get('Description', '').lower()
                need_name_lower = need_name.lower()
                
                # Check multiple fields for matches
                if (any(term in [concept.lower() for concept in need_concepts] for term in search_terms) or
                    any(term in need_description for term in search_terms) or
                    any(term in need_name_lower for term in search_terms)):
                    entity_data['cross_references']['needs'].append(need_name)

            # Cross-reference goals with multiple field matching
            for goal_name, goal_data in goals.items():
                goal_concepts = goal_data.get('Concepts', [])
                goal_description = goal_data.get('Description', '').lower()
                goal_name_lower = goal_name.lower()
                
                # Check multiple fields for matches
                if (any(term in [concept.lower() for concept in goal_concepts] for term in search_terms) or
                    any(term in goal_description for term in search_terms) or
                    any(term in goal_name_lower for term in search_terms)):
                    entity_data['cross_references']['goals'].append(goal_name)

            # Cross-reference skills with multiple field matching
            for skill_name, skill_data in skills.items():
                skill_concepts = skill_data.get('Concepts', [])
                skill_description = skill_data.get('Description', '').lower()
                skill_name_lower = skill_name.lower()
                
                # Check multiple fields for matches
                if (any(term in [concept.lower() for concept in skill_concepts] for term in search_terms) or
                    any(term in skill_description for term in search_terms) or
                    any(term in skill_name_lower for term in search_terms)):
                    entity_data['cross_references']['skills'].append(skill_name)

            # Cross-reference concepts with multiple field matching
            for concept_name, concept_data in concepts.items():
                concept_concepts = concept_data.get('concepts', [])  # Note: concepts field is lowercase
                concept_description = concept_data.get('description', '').lower()
                concept_name_lower = concept_name.lower()
                
                # Check multiple fields for matches
                if (any(term in [concept.lower() for concept in concept_concepts] for term in search_terms) or
                    any(term in concept_description for term in search_terms) or
                    any(term in concept_name_lower for term in search_terms)):
                    if concept_name not in entity_data['cross_references']['concepts']:
                        entity_data['cross_references']['concepts'].append(concept_name)

            # Add default cross-references for vision events if none found
            if entity_data.get('perception_type') == 'vision':
                object_label = entity_data.get('object_label', '').lower()
                
                # Add default needs for vision events
                if not entity_data['cross_references']['needs']:
                    entity_data['cross_references']['needs'].extend(['perception', 'understanding'])
                
                # Add default goals for vision events
                if not entity_data['cross_references']['goals']:
                    entity_data['cross_references']['goals'].extend(['recognition', 'observation'])
                
                # Add default skills for vision events
                if not entity_data['cross_references']['skills']:
                    entity_data['cross_references']['skills'].extend(['visual_perception', 'object_recognition'])

        except Exception as e:
            print(f"Error in cross_reference_entity: {e}")

    def _load_system_files(self, system_type: str) -> Dict:
        """Load all files from a system directory."""
        system_files = {}
        dir_path = self.base_dirs[system_type]
        
        try:
            for filename in os.listdir(dir_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(dir_path, filename)
                    with open(file_path, 'r') as f:
                        name = filename[:-5]  # Remove .json
                        system_files[name] = json.load(f)
        except Exception as e:
            print(f"Error loading {system_type} files: {e}")
            
        return system_files

    def process_entity_with_personality(self, perception_data: Dict) -> Dict:
        """
        Process the perceived entity through personality functions during perception phase.
        
        Args:
            perception_data: Dictionary containing perception results
            
        Returns:
            Dict containing personality processing results
        """
        try:
            # Create event data for personality processing
            event_data = {
                "WHAT": perception_data.get('Name', ''),
                "emotions": perception_data.get('emotions', {}),
                "location": perception_data.get('LocationCurrent', ''),
                "interests": perception_data.get('CommonInterests', []),
                "nouns": perception_data.get('nouns', []),
                "WHY": perception_data.get('WHY', ''),
                "WHERE": perception_data.get('WHERE', ''),
                "WHEN": perception_data.get('WHEN', ''),
                "EXPECTATION": perception_data.get('EXPECTATION', '')
            }
            
            # Process through personality functions
            personality_result = self.process_personality_functions(perception_data, event_data)
            
            return personality_result

        except Exception as e:
            print(f"Error in process_entity_with_personality: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def check_reflex_response(self, user_input: str, context: Dict = None) -> Optional[Dict]:
        """
        Check for AIML reflex response before full cognitive processing.
        
        Args:
            user_input: The user's input text
            context: Additional context information
            
        Returns:
            Dict containing reflex response if found, None otherwise
        """
        try:
            if not self.aiml_enabled or not self.aiml_integration:
                return None
            
            # Process input through reflex system
            reflex_result = self.aiml_integration.process_input(user_input, context)
            
            if reflex_result.get('pattern_matched', False):
                # Log reflex hit to memory system
                if hasattr(self.main_app, 'memory_system') and self.main_app.memory_system:
                    self.main_app.memory_system.store_memory(
                        content=f"Reflex response: {user_input} -> {reflex_result['response']}",
                        memory_type="working",
                        context=None,  # Will be created by memory system
                        importance=0.3,
                        source="reflex_system"
                    )
                
                # Enhanced logging for reflex hits
                if hasattr(self.main_app, 'log'):
                    self.main_app.log(f"⚡ Reflex response: '{user_input}' -> '{reflex_result['response']}' (confidence: {reflex_result['confidence']:.2f})")
                
                return {
                    'response': reflex_result['response'],
                    'source': 'reflex',
                    'confidence': reflex_result['confidence'],
                    'processing_time': reflex_result['processing_time'],
                    'pattern_matched': True
                }
            
            return None
            
        except Exception as e:
            print(f"Error checking reflex response: {e}")
            return None

    def get_directory_summary(self) -> str:
        """
        Creates and returns a string containing detailed information about files in each directory.
        For each directory, it lists the path and counts files, then provides details about each file.
        
        Returns:
            str: A formatted string containing directory paths, file counts, and file details
        """
        summary = []
        
        # Process base directories
        for dir_name, dir_path in self.base_dirs.items():
            if os.path.exists(dir_path):
                files = [f for f in os.listdir(dir_path) if f.endswith('.json')]
                file_count = len(files)
                
                # For people directory, count only type='person' entries
                if dir_name == 'people':
                    people_count = 0
                    for file in files:
                        file_path = os.path.join(dir_path, file)
                        try:
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                                if data.get('type') == 'person':
                                    people_count += 1
                        except Exception:
                            pass
                    summary.append(f"\n{dir_path} ({people_count})")
                else:
                    summary.append(f"\n{dir_path} ({file_count})")
                
                # Add details for each file
                for file in files:
                    file_path = os.path.join(dir_path, file)
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            # Get relevant information based on directory type
                            if dir_name == 'people':
                                # Check if this is a person (type='person') before including
                                if data.get('type') == 'person':
                                    name = data.get('word', data.get('Name', 'Unknown'))
                                    emotional_associations = data.get('emotional_associations', {})
                                    
                                    # Format emotional associations for display
                                    emotion_parts = []
                                    for emotion, value in emotional_associations.items():
                                        emotion_parts.append(f"{emotion}={value}")
                                    
                                    emotion_str = ", ".join(emotion_parts) if emotion_parts else "no emotions"
                                    summary.append(f"  - {name} ({emotion_str})")
                            elif dir_name == 'concepts':
                                word = data.get('word', 'Unknown')
                                type_ = data.get('type', 'Unknown')
                                summary.append(f"  - {word} (Type: {type_})")
                            elif dir_name in ['needs', 'goals', 'skills']:
                                name = file.replace('_self_learned.json', '')
                                priority = data.get('priority', 0.0)
                                summary.append(f"  - {name} (Priority: {priority:.2f})")
                            else:
                                # For other directories, just show the filename
                                summary.append(f"  - {file}")
                    except Exception as e:
                        summary.append(f"  - {file} (Error reading: {str(e)})")
        
        # Process image directories
        for dir_name, dir_path in self.image_dirs.items():
            if os.path.exists(dir_path):
                files = [f for f in os.listdir(dir_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
                file_count = len(files)
                summary.append(f"\n{dir_path} ({file_count})")
                
                # Group images by subdirectory
                subdirs = {}
                for file in files:
                    subdir = os.path.dirname(os.path.join(dir_path, file))
                    if subdir not in subdirs:
                        subdirs[subdir] = []
                    subdirs[subdir].append(file)
                
                # Add details for each subdirectory
                for subdir, subdir_files in subdirs.items():
                    summary.append(f"  {os.path.basename(subdir)} ({len(subdir_files)})")
                    for file in subdir_files:
                        summary.append(f"    - {file}")
        
        return "\n".join(summary)

    def get_directory_files(self, directory_path: str) -> list:
        """
        Returns a list of all file names in the specified directory.
        
        Args:
            directory_path: Path to the directory to scan
            
        Returns:
            list: List of file names in the directory
        """
        if not os.path.exists(directory_path):
            return []
            
        return [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    
    def publish_earthly_observations(self, signals: dict):
        """
        Publish observations to the Earthly game engine.
        
        Args:
            signals: Dictionary of perception signals to map to Earthly observations
        """
        try:
            # Get earthly game engine if available
            eg = getattr(self.main_app, "earthly_game", None)
            if not eg:
                return
            
            # Map perception signals to Earthly observations using JSON configuration
            if hasattr(self.main_app, 'game_theory_system'):
                earthly_config = self.main_app.game_theory_system.get_game_config("earthly_life_liig")
                if earthly_config and "state_bridge" in earthly_config:
                    mapping = earthly_config["state_bridge"].get("perception_mapping", {})
                    
                    # Apply mappings from JSON configuration
                    for signal_key, earthly_key in mapping.items():
                        if signal_key in signals:
                            obs_value = signals[signal_key]
                            
                            # Convert observation value if needed
                            obs_type = earthly_config["state_bridge"]["observation_triggers"].get(signal_key, "string")
                            if obs_type == "float" and isinstance(obs_value, (int, float)):
                                obs_value = float(obs_value)
                            elif obs_type == "bool" and isinstance(obs_value, (bool, int)):
                                obs_value = bool(obs_value)
                            elif obs_type == "string" and isinstance(obs_value, str):
                                obs_value = str(obs_value)
                            
                            # Apply observation to earthly game engine
                            eg.apply_observation(earthly_key, obs_value)
                            
                            # Log the observation
                            if self.main_app and hasattr(self.main_app, 'log'):
                                self.main_app.log(f"🌍 Earthly observation: {earthly_key} = {obs_value}")
                                
        except Exception as e:
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log(f"❌ Error publishing earthly observations: {e}")
            print(f"❌ Error publishing earthly observations: {e}")

# Example usage
if __name__ == "__main__":
    perception_system = PerceptionSystem()
    
    # Example person data
    person_data = {
        "PreferredFunction": 0,
        "Name": "John Doe",
        "TrustValue": 0.8,
        "LocationCurrent": "New York",
        "LocationBorn": "Los Angeles",
        "CommonInterests": ["Football", "Cooking", "Hiking"],
        "ImageFilePath": "",
        "nouns": ["person", "friend", "athlete"],
        "WHY": "social interaction",
        "WHERE": "New York",
        "WHEN": "now"
    }
    
    # Perceive the person
    perception_result = perception_system.perceive_entity('person', person_data)
    print("Perception Result:", json.dumps(perception_result, indent=2))
    
    # Process with personality functions
    personality_result = perception_system.process_entity_with_personality(perception_result.get('entity_data', {}))
    print("Personality Processing Result:", json.dumps(personality_result, indent=2)) 