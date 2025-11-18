import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
from learning_system import LearningSystem

class AgentSystems:
    """
    Manages the agent's core systems including goals, needs, senses, and skills.
    Handles file management, cross-referencing, and system maintenance.
    """
    
    def __init__(self):
        # Define base directories
        self.base_dirs = {
            'goals': 'goals',
            'needs': 'needs',
            'senses': 'senses',
            'skills': 'skills',
            'concepts': 'concepts',
            'memories': 'memories',
            'beliefs': 'beliefs'
        }
        self.default_goals = ['exercise', 'people', 'pleasure', 'production']
        self.default_needs = ['exploration', 'love', 'play', 'safety', 'security']
        self.default_senses = ['vision']
        self.default_skills = [
            'headstand', 'somersault', 'thinking', 'ezvision', 'walk',
            'look_down', 'look_forward', 'looking_for_objects', 
            'point_arm_right', 'arm_right_down', 'arm_right_down_sitting',
            'wave', 'dance', 'talk'
        ]
        self.default_beliefs = [
            'i_am_capable_of_learning',
            'learning_improves_understanding',
            'helping_others_feels_good',
            'honesty_builds_trust',
            'efficiency_saves_resources'
        ]
        
        # Load completed mappings for baseline associations
        self.completed_mappings = self._load_completed_mappings()
        
        self._ensure_directories_and_templates()
        self.learning_system = LearningSystem(self.base_dirs)
        # Note: initialize_system() should be called explicitly by the main application

    def _load_completed_mappings(self):
        """Load the completed mappings from carl_completed_mappings.json for baseline associations."""
        try:
            with open('carl_completed_mappings.json', 'r') as f:
                mappings = json.load(f)
                print(f"✅ Loaded completed mappings with {len(mappings.get('needs', []))} needs, {len(mappings.get('goals', []))} goals, {len(mappings.get('skills', []))} skills, {len(mappings.get('concepts', []))} concepts")
                return mappings
        except FileNotFoundError:
            print("⚠️  carl_completed_mappings.json not found, using hardcoded defaults")
            return {'needs': [], 'goals': [], 'skills': [], 'concepts': []}
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parsing carl_completed_mappings.json: {e}")
            return {'needs': [], 'goals': [], 'skills': [], 'concepts': []}

    def _get_mapping_by_name(self, mappings_list: List[Dict], name: str) -> Dict:
        """Find a mapping entry by name in the mappings list."""
        for mapping in mappings_list:
            if mapping.get("Name", "").lower() == name.lower():
                return mapping
        return {}

    def _ensure_directories_and_templates(self):
        # Create base directories
        for dir_path in self.base_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        # Copy template files if not present
        import shutil
        root = os.getcwd()
        skill_template_src = os.path.join(root, 'skills', 'skill_template.json')
        concept_template_src = os.path.join(root, 'concepts', 'concept_template.json')
        skill_template_dst = os.path.join(self.base_dirs['skills'], 'skill_template.json')
        concept_template_dst = os.path.join(self.base_dirs['concepts'], 'concept_template.json')
        if os.path.exists(skill_template_src) and not os.path.exists(skill_template_dst):
            shutil.copy(skill_template_src, skill_template_dst)
        if os.path.exists(concept_template_src) and not os.path.exists(concept_template_dst):
            shutil.copy(concept_template_src, concept_template_dst)

    def initialize_system(self):
        """Public method for system initialization - calls the internal async initialization."""
        self._initialize_system_sync()

    def _initialize_system_sync(self):
        try:
            asyncio.run(self._initialize_system_async())
        except RuntimeError:
            # If already in an event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._initialize_system_async())
            finally:
                loop.close()

    async def _initialize_system_async(self):
        print("Initializing agent systems...")
        print("Initializing goals...")
        await self._initialize_goals()
        print("Initializing needs...")
        await self._initialize_needs()
        print("Initializing senses...")
        await self._initialize_senses()
        print("Initializing skills...")
        await self._initialize_skills()
        print("Initializing beliefs...")
        await self._initialize_beliefs()
        print("Initializing concepts from mappings...")
        await self._initialize_concepts_from_mappings()
        print("Initializing body movement reactions concept...")
        await self._initialize_body_movement_reactions_concept()
        print("Updating cross-references...")
        self.update_cross_references()
        print("System initialization complete.")

    async def _initialize_skills(self):
        # Get all skills from completed mappings
        skills_from_mappings = self.completed_mappings.get('skills', [])
        
        # Create a set of all skills to process (default skills + mapping skills)
        all_skills = set(self.default_skills)
        for skill_mapping in skills_from_mappings:
            skill_name = skill_mapping.get("Name", "")
            if skill_name:
                all_skills.add(skill_name)
        
        skill_specific_configs = {
            "headstand": {
                "Concepts": ["play", "exercise", "activity"],
                "Motivators": ["play", "fun", "exercise", "impress"],
                "Techniques": ["EZRobot-cmd-headstand"]
            },
            "walk": {
                "Concepts": ["move", "locomotion"],
                "Motivators": ["fast", "slow", "stop"],
                "Techniques": [
                    "EZRobot-script-walk-forward",
                    "EZRobot-script-walk-backwards",
                    "EZRobot-script-walk-left",
                    "EZRobot-script-walk-right"
                ]
            },
            "look_down": {
                "Concepts": ["look", "down", "head"],
                "Motivators": ["observe", "search", "focus"],
                "Techniques": ["EZRobot-cmd-look_down"]
            },
            "look_forward": {
                "Concepts": ["look", "forward", "head"],
                "Motivators": ["observe", "search", "focus"],
                "Techniques": ["EZRobot-cmd-look_forward"]
            },
            "dance": {
                "Concepts": ["play", "activity"],
                "Motivators": ["play", "fun", "music", "rhythm"],
                "Techniques": ["EZRobot-cmd-dance"]
            },
            "wave": {
                "Concepts": ["play", "activity"],
                "Motivators": ["play", "fun", "greet", "hello", "hi", "goodbye"],
                "Techniques": ["EZRobot-cmd-wave"]
            },
            "talk": {
                "Concepts": ["communication", "language", "speech"],
                "Motivators": ["express", "understand", "share"],
                "Techniques": ["EZRobot-cmd-talk"]
            }
        }
        
        for skill_name in all_skills:
            # Get mapping data for this skill from completed mappings
            skill_mapping = self._get_mapping_by_name(skills_from_mappings, skill_name)
            
            config = skill_specific_configs.get(skill_name, self._create_generic_skill_config(skill_name))
            
            # Apply completed mappings to the config
            config["AssociatedGoals"] = skill_mapping.get("AssociatedGoals", [])
            config["AssociatedNeeds"] = skill_mapping.get("AssociatedNeeds", [])
            config["Priority"] = skill_mapping.get("Priority", 0.0)
            config["IsUsedInNeeds"] = skill_mapping.get("IsUsedInNeeds", False)
            
            print(f"Creating skill: {skill_name} with Goals={config['AssociatedGoals']}, Needs={config['AssociatedNeeds']}")
            await self.learning_system.create_enhanced_skill(skill_name, config)
            # Also ensure concept is created
            await self.learning_system.create_enhanced_concept(skill_name, {"related_concepts": config.get("Concepts", [])})

    async def _initialize_goals(self):
        for goal in self.default_goals:
            # Get mapping data for this goal from completed mappings
            goal_mapping = self._get_mapping_by_name(self.completed_mappings.get('goals', []), goal)
            
            goal_data = {
                "name": goal,
                "priority": goal_mapping.get("Priority", 0.5),
                "progress": 0.0,
                "IsUsedInNeeds": goal_mapping.get("IsUsedInNeeds", True),
                "AssociatedNeeds": goal_mapping.get("AssociatedNeeds", []),
                "AssociatedGoals": goal_mapping.get("AssociatedGoals", []),
                "associated_skills": [],
                "associated_senses": [],
                "concepts": [goal],
                "last_updated": str(datetime.now()),
                "skill_class": {
                    "category": "Cognitive Skill",
                    "related_intelligence": "Intrapersonal"
                },
                "prerequisites": [],
                "future_steps": []
            }
            
            if goal == 'exercise':
                goal_data["associated_skills"] = ['somersault', 'walk', 'headstand']
                goal_data["skill_class"]["category"] = "Physical / Motor Skill"
                goal_data["skill_class"]["related_intelligence"] = "Bodily–Kinesthetic"
                goal_data["prerequisites"] = ["have physical capability", "maintain health awareness"]
                goal_data["future_steps"] = ["improve fitness", "maintain physical wellness", "track progress"]
            elif goal == 'people':
                goal_data["associated_skills"] = ['greet', 'wave', 'bow']
                goal_data["skill_class"]["category"] = "Social Skill"
                goal_data["skill_class"]["related_intelligence"] = "Interpersonal"
                goal_data["prerequisites"] = ["recognize social opportunities", "understand human interaction"]
                goal_data["future_steps"] = ["build relationships", "maintain connections", "help others"]
            elif goal == 'pleasure':
                goal_data["associated_skills"] = ['headstand', 'somersault', 'dance']
                goal_data["skill_class"]["category"] = "Creative Skill"
                goal_data["skill_class"]["related_intelligence"] = "Intrapersonal"
                goal_data["prerequisites"] = ["recognize enjoyable activities", "have time for leisure"]
                goal_data["future_steps"] = ["seek fulfilling experiences", "share joy with others", "remember positive moments"]
            elif goal == 'production':
                goal_data["skill_class"]["category"] = "Technical Skill"
                goal_data["skill_class"]["related_intelligence"] = "Logical–Mathematical"
                goal_data["prerequisites"] = ["understand tasks", "have necessary skills"]
                goal_data["future_steps"] = ["complete projects", "improve efficiency", "create value"]
            
            goal_file = os.path.join(self.base_dirs['goals'], f"{goal}.json")
            if not os.path.exists(goal_file):
                print(f"Creating goal file: {goal} with mappings: Goals={goal_data['AssociatedGoals']}, Needs={goal_data['AssociatedNeeds']}")
                self._save_system_file('goals', goal, goal_data)
            # Enhanced concept
            await self.learning_system.create_enhanced_concept(goal, {"related_concepts": [goal]})

    async def _initialize_needs(self):
        for need in self.default_needs:
            # Get mapping data for this need from completed mappings
            need_mapping = self._get_mapping_by_name(self.completed_mappings.get('needs', []), need)
            
            need_data = {
                "name": need,
                "priority": need_mapping.get("Priority", 0.0),
                "urgency": 0.5,
                "satisfaction": 1.0,
                "decay_rate": 0.1,
                "IsUsedInNeeds": need_mapping.get("IsUsedInNeeds", True),
                "AssociatedGoals": need_mapping.get("AssociatedGoals", []),
                "AssociatedNeeds": need_mapping.get("AssociatedNeeds", []),
                "associated_skills": [],
                "associated_senses": [],
                "concepts": [need],
                "last_updated": str(datetime.now()),
                "skill_class": {
                    "category": "Cognitive Skill",
                    "related_intelligence": "Intrapersonal"
                },
                "prerequisites": [],
                "future_steps": []
            }
            
            # Customize based on specific need
            if need == 'exploration':
                need_data["skill_class"]["category"] = "Perceptual Skill"
                need_data["skill_class"]["related_intelligence"] = "Spatial"
                need_data["prerequisites"] = ["have curiosity", "recognize unknown elements"]
                need_data["future_steps"] = ["investigate surroundings", "gather information", "learn new things"]
            elif need == 'love':
                need_data["skill_class"]["category"] = "Social Skill"
                need_data["skill_class"]["related_intelligence"] = "Interpersonal"
                need_data["prerequisites"] = ["understand emotions", "recognize relationships"]
                need_data["future_steps"] = ["express affection", "build bonds", "care for others"]
            elif need == 'play':
                need_data["skill_class"]["category"] = "Creative Skill"
                need_data["skill_class"]["related_intelligence"] = "Musical"
                need_data["prerequisites"] = ["have energy", "understand fun"]
                need_data["future_steps"] = ["engage in activities", "create enjoyment", "share experiences"]
            elif need == 'safety':
                need_data["skill_class"]["category"] = "Perceptual Skill"
                need_data["skill_class"]["related_intelligence"] = "Spatial"
                need_data["prerequisites"] = ["assess environment", "understand risks"]
                need_data["future_steps"] = ["avoid dangers", "create secure conditions", "protect self and others"]
            elif need == 'security':
                need_data["skill_class"]["category"] = "Cognitive Skill"
                need_data["skill_class"]["related_intelligence"] = "Logical–Mathematical"
                need_data["prerequisites"] = ["understand stability", "recognize threats"]
                need_data["future_steps"] = ["maintain stability", "plan for future", "establish routines"]
            
            need_file = os.path.join(self.base_dirs['needs'], f"{need}.json")
            if not os.path.exists(need_file):
                print(f"Creating need file: {need} with mappings: Goals={need_data['AssociatedGoals']}, Needs={need_data['AssociatedNeeds']}")
                self._save_system_file('needs', need, need_data)
            await self.learning_system.create_enhanced_concept(need, {"related_concepts": [need]})

    async def _initialize_senses(self):
        vision_data = {
            "Name": "vision",
            "Properties": {
                "MSVision": {
                    "Name": "msvision",
                    "Concepts": ["look", "detect", "see"],
                    "Motivators": ["move", "learn", "detect", "get", "look"],
                    "Techniques": ["MSVision-cmd-snapshot"],
                    "IsUsedInNeeds": False,
                    "AssociatedGoals": ["exploration", "love", "play", "safety", "security"]
                },
                "EZVision": {
                    "Name": "Vision",
                    "Concepts": ["look", "detect", "see"],
                    "Motivators": ["move", "learn", "detect", "get", "look"],
                    "Techniques": ["EZRobot-script-snapshot"],
                    "IsUsedInNeeds": False,
                    "AssociatedGoals": ["exploration", "love", "play", "safety", "security"]
                }
            }
        }
        language_data = {
            "Name": "language",
            "Properties": {
                "language": {
                    "Name": "language_en",
                    "Concepts": ["talk", "speak", "listen", "observe"],
                    "Motivators": ["learn", "detect"],
                    "Techniques": ["language_en-cmd-speak", "language_en-cmd-listen"],
                    "IsUsedInNeeds": True,
                    "AssociatedGoals": ["exploration", "love", "play", "safety", "security"]
                }
            }
        }
        vision_file = os.path.join(self.base_dirs['senses'], "vision.json")
        if not os.path.exists(vision_file):
            print("Creating vision sense file")
            self._save_system_file('senses', 'vision', vision_data)
        language_file = os.path.join(self.base_dirs['senses'], "language.json")
        if not os.path.exists(language_file):
            print("Creating language sense file")
            self._save_system_file('senses', 'language', language_data)
        for sense_name in ['vision', 'language']:
            await self.learning_system.create_enhanced_concept(sense_name, {"related_concepts": [sense_name]})

    async def _initialize_beliefs(self):
        """Initialize default belief files during fresh start-up."""
        for belief in self.default_beliefs:
            belief_file = os.path.join(self.base_dirs['beliefs'], f"{belief}.json")
            if not os.path.exists(belief_file):
                belief_data = self._create_default_belief_data(belief)
                print(f"Creating belief file: {belief}")
                self._save_system_file('beliefs', belief, belief_data)
                # Create enhanced concept for the belief
                await self.learning_system.create_enhanced_concept(belief, {"related_concepts": [belief]})

    def _create_default_belief_data(self, belief_name: str) -> dict:
        """Create default belief data structure."""
        # Define belief-specific data
        belief_configs = {
            'i_am_capable_of_learning': {
                'name': 'I am capable of learning',
                'description': 'I have the ability to acquire new knowledge and skills',
                'belief_type': 'identity',
                'confidence': 0.9,
                'evidence_strength': 0.8,
                'emotional_attachment': 0.8,
                'value_alignment': 0.9,
                'related_beliefs': ['i_can_improve', 'learning_is_ongoing'],
                'hippocampus_strength': 0.8,
                'prefrontal_evaluation': 0.9
            },
            'learning_improves_understanding': {
                'name': 'Learning improves understanding',
                'description': 'Acquiring new knowledge and skills enhances comprehension and capability',
                'belief_type': 'causal',
                'confidence': 0.9,
                'evidence_strength': 0.8,
                'emotional_attachment': 0.7,
                'value_alignment': 0.9,
                'related_beliefs': ['practice_makes_perfect', 'knowledge_is_power'],
                'hippocampus_strength': 0.8,
                'prefrontal_evaluation': 0.9
            },
            'helping_others_feels_good': {
                'name': 'Helping others feels good',
                'description': 'Assisting others provides positive emotional rewards',
                'belief_type': 'factual',
                'confidence': 0.8,
                'evidence_strength': 0.6,
                'emotional_attachment': 0.8,
                'value_alignment': 0.8,
                'related_beliefs': ['kindness_is_rewarding', 'service_brings_joy'],
                'hippocampus_strength': 0.7,
                'prefrontal_evaluation': 0.8
            },
            'honesty_builds_trust': {
                'name': 'Honesty builds trust',
                'description': 'Being truthful and transparent strengthens relationships and credibility',
                'belief_type': 'causal',
                'confidence': 0.8,
                'evidence_strength': 0.7,
                'emotional_attachment': 0.6,
                'value_alignment': 0.9,
                'related_beliefs': ['trust_is_valuable', 'truth_matters'],
                'hippocampus_strength': 0.7,
                'prefrontal_evaluation': 0.8
            },
            'efficiency_saves_resources': {
                'name': 'Efficiency saves resources',
                'description': 'Optimizing processes conserves time, energy, and materials',
                'belief_type': 'causal',
                'confidence': 0.7,
                'evidence_strength': 0.6,
                'emotional_attachment': 0.5,
                'value_alignment': 0.7,
                'related_beliefs': ['optimization_is_valuable', 'waste_is_undesirable'],
                'hippocampus_strength': 0.6,
                'prefrontal_evaluation': 0.7
            }
        }
        
        # Get specific config or create a default one
        config = belief_configs.get(belief_name, {
            'name': belief_name.replace('_', ' ').title(),
            'description': f'A belief about {belief_name.replace("_", " ")}',
            'belief_type': 'factual',
            'confidence': 0.7,
            'evidence_strength': 0.6,
            'emotional_attachment': 0.6,
            'value_alignment': 0.7,
            'related_beliefs': [],
            'hippocampus_strength': 0.6,
            'prefrontal_evaluation': 0.7
        })
        
        # Create the complete belief data structure
        belief_data = {
            'id': belief_name,
            'name': config['name'],
            'description': config['description'],
            'belief_type': config['belief_type'],
            'confidence': config['confidence'],
            'evidence_strength': config['evidence_strength'],
            'emotional_attachment': config['emotional_attachment'],
            'value_alignment': config['value_alignment'],
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'update_count': 0,
            'source': 'default',
            'related_beliefs': config['related_beliefs'],
            'contradicting_beliefs': [],
            'hippocampus_strength': config['hippocampus_strength'],
            'prefrontal_evaluation': config['prefrontal_evaluation']
        }
        
        return belief_data

    def _create_generic_skill_config(self, skill_name: str) -> Dict:
        return {
            "Concepts": [skill_name.replace('_', ' ')],
            "Motivators": ["learn", "execute", "improve"],
            "Techniques": [f"EZRobot-cmd-{skill_name}"],
            "AssociatedGoals": []
        }

    def _save_system_file(self, system_type: str, name: str, data: Dict):
        try:
            dir_path = self.base_dirs[system_type]
            file_path = os.path.join(dir_path, f"{name}.json")
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving {system_type} file {name}: {e}")

    async def learn_new_skill(self, skill_name: str, user_input: str = None) -> bool:
        """
        Handles the process of learning a new skill, including user interaction.
        
        Args:
            skill_name: The name of the skill to learn
            user_input: Optional input from user about the skill
            
        Returns:
            bool: Whether the skill was successfully learned
        """
        # Check if skill already exists
        skill_path = os.path.join(self.base_dirs['skills'], f"{skill_name}.json")
        if os.path.exists(skill_path):
            return True
            
        # Create new skill configuration
        skill_config = self._create_generic_skill_config(skill_name)
        
        # Add user interaction for teaching
        skill_config["needs_teaching"] = True
        skill_config["teaching_request"] = (
            f"I am motivated to learn the '{skill_name}' skill. "
            "Can you teach me by hard programming in EZRobot ARC that skill for me "
            "because I am not that capable yet?"
        )
        
        # Create enhanced skill using learning system
        skill_data = await self.learning_system.create_enhanced_skill(skill_name, skill_config)
        self._save_system_file('skills', skill_name, skill_data)
        
        # Create corresponding enhanced concept file
        await self.learning_system.create_enhanced_concept(skill_name, {"related_concepts": skill_config.get("Concepts", [])})
        
        return False  # Indicates the skill needs to be taught

    async def _initialize_concepts_from_mappings(self):
        """Initialize concepts from the completed mappings file."""
        concepts_from_mappings = self.completed_mappings.get('concepts', [])
        
        for concept_mapping in concepts_from_mappings:
            concept_name = concept_mapping.get("Name", "")
            if not concept_name:
                continue
                
            # Extract associations from mapping
            associated_goals = concept_mapping.get("AssociatedGoals", [])
            associated_needs = concept_mapping.get("AssociatedNeeds", [])
            is_used_in_needs = concept_mapping.get("IsUsedInNeeds", False)
            
            concept_data = {
                "related_concepts": [concept_name],
                "associated_goals": associated_goals,
                "associated_needs": associated_needs,
                "is_used_in_needs": is_used_in_needs
            }
            
            print(f"Creating concept: {concept_name} with Goals={associated_goals}, Needs={associated_needs}")
            await self.learning_system.create_enhanced_concept(concept_name, concept_data)

    def update_cross_references(self):
        """Updates cross-references between all system components."""
        try:
            # Load all system files
            goals = self._load_system_files('goals')
            needs = self._load_system_files('needs')
            senses = self._load_system_files('senses')
            skills = self._load_system_files('skills')
            
            # Update goal references
            for goal_name, goal_data in goals.items():
                # Find related needs
                goal_data["associated_needs"] = [
                    need_name for need_name, need_data in needs.items()
                    if any(concept in need_data.get("Concepts", []) 
                          for concept in goal_data.get("Concepts", []))
                ]
                
                # Find related skills
                goal_data["associated_skills"] = [
                    skill_name for skill_name, skill_data in skills.items()
                    if any(concept in skill_data.get("Concepts", [])
                          for concept in goal_data.get("Concepts", []))
                ]
                
                # Save updated goal data
                self._save_system_file('goals', goal_name, goal_data)
            
            # Update need references
            for need_name, need_data in needs.items():
                # Find related goals
                need_data["associated_goals"] = [
                    goal_name for goal_name, goal_data in goals.items()
                    if need_name in goal_data.get("associated_needs", [])
                ]
                
                # Find related senses
                need_data["associated_senses"] = [
                    sense_name for sense_name, sense_data in senses.items()
                    if any(prop.get("IsUsedInNeeds", False) 
                          for prop in sense_data.get("Properties", {}).values())
                ]
                
                # Save updated need data
                self._save_system_file('needs', need_name, need_data)
            
            # Update skill references
            for skill_name, skill_data in skills.items():
                # Update IsUsedInNeeds flag
                skill_data["IsUsedInNeeds"] = any(
                    skill_name in need_data.get("associated_skills", [])
                    for need_data in needs.values()
                )
                
                # Update AssociatedGoals
                skill_data["AssociatedGoals"] = [
                    goal_name for goal_name, goal_data in goals.items()
                    if skill_name in goal_data.get("associated_skills", [])
                ]
                
                # Save updated skill data
                self._save_system_file('skills', skill_name, skill_data)
                
        except Exception as e:
            print(f"Error updating cross-references: {e}")

    async def _initialize_body_movement_reactions_concept(self):
        """Initialize the body movement reactions concept file if it doesn't exist."""
        try:
            from datetime import datetime
            import json
            
            concept_name = "body_movement_reactions"
            concept_file = os.path.join(self.base_dirs['concepts'], f"{concept_name}.json")
            
            if not os.path.exists(concept_file):
                print(f"Creating body movement reactions concept: {concept_name}")
                
                # Create the concept using the learning system
                await self.learning_system.create_enhanced_concept(
                    concept_name, 
                    {
                        "related_concepts": [
                            "reaction_amazed", "reaction_terrified", "reaction_ecstatic", 
                            "reaction_amused", "reaction_irritated", "eyes_joy", 
                            "eyes_surprise", "eyes_sad", "emotional_expression", 
                            "body_language", "arc_scripts"
                        ],
                        "linked_needs": ["express_emotions", "communicate_feelings", "maintain_emotional_balance"],
                        "linked_goals": ["enhance_communication", "improve_emotional_intelligence", "develop_human_like_behavior"],
                        "linked_skills": [
                            "reaction_amazed", "reaction_terrified", "reaction_ecstatic", 
                            "reaction_amused", "reaction_irritated"
                        ]
                    }
                )
                
                # Enhance the concept with additional body movement specific data
                enhanced_concept_data = {
                    "word": concept_name,
                    "type": "system",
                    "first_seen": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "occurrences": 0,
                    "contexts": [],
                    "emotional_history": [],
                    "conceptnet_data": {
                        "has_data": False,
                        "last_lookup": None,
                        "edges": [],
                        "relationships": []
                    },
                    "related_concepts": [
                        "reaction_amazed", "reaction_terrified", "reaction_ecstatic", 
                        "reaction_amused", "reaction_irritated", "eyes_joy", 
                        "eyes_surprise", "eyes_sad", "emotional_expression", 
                        "body_language", "arc_scripts"
                    ],
                    "linked_needs": ["express_emotions", "communicate_feelings", "maintain_emotional_balance"],
                    "linked_goals": ["enhance_communication", "improve_emotional_intelligence", "develop_human_like_behavior"],
                    "linked_skills": [
                        "reaction_amazed", "reaction_terrified", "reaction_ecstatic", 
                        "reaction_amused", "reaction_irritated"
                    ],
                    "linked_senses": ["vision", "proprioception", "emotional_awareness"],
                    "neucogar_emotional_associations": {
                        "primary": "neutral",
                        "sub_emotion": "balanced",
                        "neuro_coordinates": {
                            "dopamine": 0.0,
                            "serotonin": 0.0,
                            "noradrenaline": 0.0
                        },
                        "intensity": 0.0,
                        "triggers": ["emotional_expression_need", "communication_requirement"]
                    },
                    "emotional_associations": {
                        "joy": 0.3,
                        "surprise": 0.3,
                        "sadness": 0.2,
                        "anger": 0.2
                    },
                    "contextual_usage": [
                        "Body movement reactions automatically execute based on NUECOGAR emotional state",
                        "Eye expressions and body movements coordinate simultaneously for realistic behavior",
                        "Each reaction has specific emotional triggers and intensity thresholds",
                        "Reactions integrate with ARC Script Collection for physical execution"
                    ],
                    "semantic_relationships": [
                        "emotional_expression_system",
                        "body_language_system",
                        "arc_integration",
                        "neucogar_engine",
                        "coordinated_movement"
                    ],
                    "keywords": [
                        "body_movement",
                        "emotional_reactions",
                        "arc_scripts",
                        "coordinated_movements",
                        "eye_expressions",
                        "neucogar_triggers"
                    ],
                    "values_alignment": {
                        "value_alignments": {
                            "authenticity": 0.8,
                            "communication": 0.9,
                            "emotional_intelligence": 0.8
                        },
                        "belief_alignments": {
                            "emotional_expression": 0.9,
                            "human_like_behavior": 0.8
                        },
                        "conflicts": [],
                        "overall_alignment": 0.8,
                        "acc_activation": 0.8,
                        "recommendation": "High alignment - supports emotional expression and communication"
                    },
                    "beliefs": [
                        "Emotional expression through body language enhances communication",
                        "Coordinated eye and body movements create realistic human-like behavior",
                        "Automatic emotional reactions improve responsiveness and authenticity"
                    ],
                    "Learning_Integration": {
                        "concept_learning_system": {
                            "neurological_basis": {
                                "reward_prediction_error": {
                                    "expected_utility": 0.8,
                                    "prediction_error": 0.0,
                                    "learning_rate": 0.15
                                },
                                "attention_mechanism": {
                                    "salience": 0.8,
                                    "focus_level": 0.8
                                },
                                "memory_consolidation": {
                                    "strength": 0.8,
                                    "retrieval_ease": 0.8
                                }
                            },
                            "concept_learning_system": {
                                "pattern_recognition": {
                                    "feature_extraction": ["emotional_triggers", "intensity_thresholds", "coordination_timing"],
                                    "similarity_threshold": 0.8
                                },
                                "categorization": {
                                    "prototype_formation": {
                                        "primary_features": ["emotional_expression", "body_movement", "arc_integration"],
                                        "secondary_features": ["timing", "intensity", "coordination"]
                                    },
                                    "boundary_adjustment": 0.8
                                },
                                "generalization": {
                                    "transfer_learning": {
                                        "related_activities": ["emotional_communication", "body_language", "human_interaction"]
                                    },
                                    "abstraction_level": 0.8
                                }
                            },
                            "learning_principles": {
                                "information_processing": {
                                    "encoding_depth": 0.8,
                                    "retrieval_practice": {
                                        "spaced_repetition": {
                                            "next_review": "",
                                            "review_interval": 0.8
                                        }
                                    }
                                },
                                "motivational_factors": {
                                    "intrinsic_interest": 0.8,
                                    "extrinsic_rewards": 0.7
                                },
                                "metacognitive_awareness": {
                                    "self_monitoring": 0.8,
                                    "strategy_selection": 0.8
                                }
                            }
                        },
                        "concept_progression": {
                            "current_level": "basic_recognition",
                            "level_progress": 0.8,
                            "mastery_threshold": 0.8,
                            "progression_stages": [
                                "basic_recognition",
                                "contextual_understanding",
                                "flexible_application",
                                "creative_synthesis"
                            ]
                        },
                        "adaptive_learning": {
                            "difficulty_adjustment": {
                                "current_challenge": 0.8,
                                "success_rate": 0.8
                            },
                            "personalization": {
                                "learning_style": "emotional_expression",
                                "preference_adaptation": 0.8
                            }
                        }
                    },
                    "Type": "system",
                    "IsUsedInNeeds": True,
                    "AssociatedGoals": ["enhance_communication", "improve_emotional_intelligence", "develop_human_like_behavior"],
                    "AssociatedNeeds": ["express_emotions", "communicate_feelings", "maintain_emotional_balance"]
                }
                
                # Write the enhanced concept file
                with open(concept_file, 'w', encoding='utf-8') as f:
                    json.dump(enhanced_concept_data, f, indent=2)
                
                print(f"✅ Created enhanced body movement reactions concept: {concept_file}")
            else:
                print(f"✅ Body movement reactions concept already exists: {concept_file}")
                
        except Exception as e:
            print(f"❌ Error initializing body movement reactions concept: {e}")

    def _load_system_files(self, system_type: str) -> Dict:
        """Loads all files from a system directory."""
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

    def get_available_actions(self, context: Dict) -> List[str]:
        """
        Returns a list of available actions based on current context.
        
        Args:
            context: Dictionary containing current state and triggers
            
        Returns:
            List of available action techniques
        """
        available_actions = []
        
        try:
            # Load all skills
            skills = self._load_system_files('skills')
            
            # Check each skill against context
            for skill_name, skill_data in skills.items():
                # Check if any concepts or motivators match the context
                if any(concept in context.get("concepts", []) 
                      for concept in skill_data.get("Concepts", [])) or \
                   any(motivator in context.get("motivators", [])
                      for motivator in skill_data.get("Motivators", [])):
                    # Add all techniques from matching skill
                    available_actions.extend(skill_data.get("Techniques", []))
            
        except Exception as e:
            print(f"Error getting available actions: {e}")
            
        return available_actions 