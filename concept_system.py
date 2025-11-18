#!/usr/bin/env python3
"""
Enhanced Concept System with Schema Validation and Template Management

Handles concept creation, updates, and schema validation with proper defaults
for Learning_Integration and Learning_System keys.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

@dataclass
class ConceptDefaults:
    """Default values for concept schema."""
    LEARNING_INTEGRATION_DEFAULTS = {
        "enabled": False,
        "strategy": "none",
        "concept_learning_system": {
            "neurological_basis": {
                "reward_prediction_error": {
                    "expected_utility": 0.5,
                    "prediction_error": 0.0,
                    "learning_rate": 0.1
                },
                "attention_mechanism": {
                    "salience": 0.5,
                    "focus_level": 0.5
                },
                "memory_consolidation": {
                    "strength": 0.5,
                    "retrieval_ease": 0.5
                }
            },
            "concept_learning_system": {
                "pattern_recognition": {
                    "feature_extraction": [],
                    "similarity_threshold": 0.5
                },
                "categorization": {
                    "prototype_formation": {
                        "primary_features": [],
                        "secondary_features": []
                    },
                    "boundary_adjustment": 0.5
                },
                "generalization": {
                    "transfer_learning": {
                        "related_activities": []
                    },
                    "abstraction_level": 0.5
                }
            },
            "learning_principles": {
                "information_processing": {
                    "encoding_depth": 0.5,
                    "retrieval_practice": {
                        "spaced_repetition": {
                            "next_review": "",
                            "review_interval": 0.5
                        }
                    }
                },
                "motivational_factors": {
                    "intrinsic_interest": 0.5,
                    "extrinsic_rewards": 0.5
                },
                "metacognitive_awareness": {
                    "self_monitoring": 0.5,
                    "strategy_selection": 0.5
                }
            }
        },
        "concept_progression": {
            "current_level": "basic_recognition",
            "level_progress": 0.0,
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
                "current_challenge": 0.5,
                "success_rate": 0.5
            },
            "personalization": {
                "learning_style": "general",
                "preference_adaptation": 0.5
            }
        }
    }
    
    LEARNING_SYSTEM_DEFAULTS = {
        "strategy": "none",
        "enabled": False,
        "learning_rate": 0.1,
        "retention_factor": 0.8
    }

class ConceptSchemaManager:
    """Manages concept schema validation and template merging."""
    
    def __init__(self, concepts_dir: str = "concepts"):
        self.concepts_dir = concepts_dir
        self.logger = logging.getLogger(__name__)
        self.template_path = os.path.join(concepts_dir, "concept_template.json")
        self.defaults = ConceptDefaults()
        
    def load_template(self) -> Dict[str, Any]:
        """Load the concept template with defaults."""
        try:
            if os.path.exists(self.template_path):
                with open(self.template_path, 'r') as f:
                    template = json.load(f)
            else:
                template = self._create_default_template()
                
            # Ensure required keys exist
            template = self._ensure_required_keys(template)
            return template
            
        except Exception as e:
            self.logger.error(f"Error loading template: {e}")
            return self._create_default_template()
    
    def _create_default_template(self) -> Dict[str, Any]:
        """Create a default template if none exists."""
        template = {
            "word": "",
            "type": "thing",
            "first_seen": "",
            "last_updated": "",
            "occurrences": 0,
            "contexts": [],
            "emotional_history": [],
            "conceptnet_data": {
                "has_data": False,
                "last_lookup": None,
                "edges": [],
                "relationships": []
            },
            "related_concepts": [],
            "linked_needs": [],
            "linked_goals": [],
            "linked_skills": [],
            "linked_senses": [],
            "neucogar_emotional_associations": {
                "primary": "neutral",
                "sub_emotion": "calm",
                "neuro_coordinates": {
                    "dopamine": 0.0,
                    "serotonin": 0.0,
                    "noradrenaline": 0.0
                },
                "intensity": 0.0,
                "triggers": []
            },
            "emotional_associations": {},
            "contextual_usage": [],
            "semantic_relationships": [],
            "keywords": [],
            "values_alignment": {
                "value_alignments": {},
                "belief_alignments": {},
                "conflicts": [],
                "overall_alignment": 0.0,
                "acc_activation": 0.0,
                "recommendation": "Neutral - minimal alignment or conflict"
            },
            "beliefs": []
        }
        
        # Add required learning keys
        template = self._ensure_required_keys(template)
        
        # Save the template
        os.makedirs(self.concepts_dir, exist_ok=True)
        with open(self.template_path, 'w') as f:
            json.dump(template, f, indent=4)
            
        self.logger.info(f"Created default template at {self.template_path}")
        return template
    
    def _ensure_required_keys(self, concept_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all required keys exist with proper defaults."""
        # Add Learning_Integration if missing
        if "Learning_Integration" not in concept_data:
            concept_data["Learning_Integration"] = self.defaults.LEARNING_INTEGRATION_DEFAULTS.copy()
            self.logger.info("Added Learning_Integration defaults")
        
        # Add Learning_System if missing
        if "Learning_System" not in concept_data:
            concept_data["Learning_System"] = self.defaults.LEARNING_SYSTEM_DEFAULTS.copy()
            self.logger.info("Added Learning_System defaults")
        
        # Ensure other required keys exist
        required_keys = {
            "word": "",
            "type": "thing",
            "first_seen": str(datetime.now()),
            "last_updated": str(datetime.now()),
            "occurrences": 0,
            "contexts": [],
            "emotional_history": [],
            "conceptnet_data": {
                "has_data": False,
                "last_lookup": None,
                "edges": [],
                "relationships": []
            },
            "related_concepts": [],
            "linked_needs": [],
            "linked_goals": [],
            "linked_skills": [],
            "linked_senses": [],
            "neucogar_emotional_associations": {
                "primary": "neutral",
                "sub_emotion": "calm",
                "neuro_coordinates": {
                    "dopamine": 0.0,
                    "serotonin": 0.0,
                    "noradrenaline": 0.0
                },
                "intensity": 0.0,
                "triggers": []
            },
            "emotional_associations": {},
            "contextual_usage": [],
            "semantic_relationships": [],
            "keywords": [],
            "values_alignment": {
                "value_alignments": {},
                "belief_alignments": {},
                "conflicts": [],
                "overall_alignment": 0.0,
                "acc_activation": 0.0,
                "recommendation": "Neutral - minimal alignment or conflict"
            },
            "beliefs": []
        }
        
        for key, default_value in required_keys.items():
            if key not in concept_data:
                concept_data[key] = default_value
                self.logger.info(f"Added missing key '{key}' to concept")
        
        return concept_data
    
    def merge_with_template(self, concept_data: Dict[str, Any], word: str, word_type: str = "thing") -> Dict[str, Any]:
        """Merge concept data with template, ensuring all required keys exist."""
        # Load template
        template = self.load_template()
        
        # Update with provided data
        concept_data.update({
            "word": word,
            "type": word_type,
            "first_seen": concept_data.get("first_seen", str(datetime.now())),
            "last_updated": str(datetime.now())
        })
        
        # Ensure all required keys exist
        concept_data = self._ensure_required_keys(concept_data)
        
        return concept_data
    
    def validate_concept_schema(self, concept_data: Dict[str, Any]) -> bool:
        """Validate that a concept has all required keys."""
        required_keys = [
            "word", "type", "first_seen", "last_updated", "occurrences",
            "contexts", "emotional_history", "conceptnet_data", "related_concepts",
            "linked_needs", "linked_goals", "linked_skills", "linked_senses",
            "neucogar_emotional_associations", "emotional_associations",
            "contextual_usage", "semantic_relationships", "keywords",
            "values_alignment", "beliefs", "Learning_Integration", "Learning_System"
        ]
        
        missing_keys = [key for key in required_keys if key not in concept_data]
        
        if missing_keys:
            self.logger.warning(f"Missing required keys: {missing_keys}")
            return False
        
        return True
            
    def upgrade_legacy_concept(self, concept_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upgrade legacy concept format to current schema as in version 5.13.2."""
        # Handle old self-learned format with legacy keys
        if "Type" in concept_data and "word" in concept_data:
            # Convert old format to new with comprehensive structure
            upgraded = {
                "word": concept_data["word"],
                "type": concept_data.get("Type", "thing"),
                "first_seen": concept_data.get("first_seen", str(datetime.now())),
                "last_updated": str(datetime.now()),
                "occurrences": concept_data.get("occurrences", 0),
                "contexts": concept_data.get("contexts", []),
                "emotional_history": concept_data.get("emotional_history", []),
                "conceptnet_data": concept_data.get("conceptnet_data", {
                    "has_data": False,
                    "last_lookup": None,
                    "edges": [],
                    "relationships": []
                }),
                "related_concepts": concept_data.get("related_concepts", []),
                "linked_needs": concept_data.get("AssociatedNeeds", []),
                "linked_goals": concept_data.get("AssociatedGoals", []),
                "linked_skills": concept_data.get("linked_skills", []),
                "linked_senses": concept_data.get("linked_senses", []),
                "neucogar_emotional_associations": concept_data.get("neucogar_emotional_associations", {
                    "primary": "neutral",
                    "sub_emotion": "calm",
                    "neuro_coordinates": {
                        "dopamine": 0.0,
                        "serotonin": 0.0,
                        "noradrenaline": 0.0
                    },
                    "intensity": 0.0,
                    "triggers": []
                }),
                "emotional_associations": concept_data.get("emotional_associations", {}),
                "contextual_usage": concept_data.get("contextual_usage", []),
                "semantic_relationships": concept_data.get("semantic_relationships", []),
                "keywords": concept_data.get("keywords", []),
                "values_alignment": concept_data.get("values_alignment", {
                    "value_alignments": {},
                    "belief_alignments": {},
                    "conflicts": [],
                    "overall_alignment": 0.0,
                    "acc_activation": 0.0,
                    "recommendation": "Neutral - minimal alignment or conflict"
                }),
                "beliefs": concept_data.get("beliefs", []),
                "Learning_Integration": concept_data.get("Learning_Integration", {
                    "enabled": False,
                    "strategy": "none",
                    "concept_learning_system": {
                        "neurological_basis": {
                            "reward_prediction_error": {
                                "expected_utility": 0.5,
                                "prediction_error": 0.0,
                                "learning_rate": 0.1
                            },
                            "attention_mechanism": {
                                "salience": 0.5,
                                "focus_level": 0.5
                            },
                            "memory_consolidation": {
                                "strength": 0.5,
                                "retrieval_ease": 0.5
                            }
                        },
                        "concept_learning_system": {
                            "pattern_recognition": {
                                "feature_extraction": [],
                                "similarity_threshold": 0.5
                            },
                            "categorization": {
                                "prototype_formation": {
                                    "primary_features": [],
                                    "secondary_features": []
                                },
                                "boundary_adjustment": 0.5
                            },
                            "generalization": {
                                "transfer_learning": {
                                    "related_activities": []
                                },
                                "abstraction_level": 0.5
                            }
                        },
                        "learning_principles": {
                            "information_processing": {
                                "encoding_depth": 0.5,
                                "retrieval_practice": {
                                    "spaced_repetition": {
                                        "next_review": "",
                                        "review_interval": 0.5
                                    }
                                }
                            },
                            "motivational_factors": {
                                "intrinsic_interest": 0.5,
                                "extrinsic_rewards": 0.5
                            },
                            "metacognitive_awareness": {
                                "self_monitoring": 0.5,
                                "strategy_selection": 0.5
                            }
                        }
                    },
                    "concept_progression": {
                        "current_level": "basic_recognition",
                        "level_progress": 0.0,
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
                            "current_challenge": 0.5,
                            "success_rate": 0.5
                        },
                        "personalization": {
                            "learning_style": "general",
                            "preference_adaptation": 0.5
                        }
                    }
                }),
                "Learning_System": concept_data.get("Learning_System", {
                    "strategy": "none",
                    "enabled": False,
                    "learning_rate": 0.1,
                    "retention_factor": 0.8
                })
            }
            
            # Preserve legacy keys for backward compatibility
            if "IsUsedInNeeds" in concept_data:
                upgraded["IsUsedInNeeds"] = concept_data["IsUsedInNeeds"]
            if "AssociatedGoals" in concept_data:
                upgraded["AssociatedGoals"] = concept_data["AssociatedGoals"]
            if "AssociatedNeeds" in concept_data:
                upgraded["AssociatedNeeds"] = concept_data["AssociatedNeeds"]
            
            self.logger.info(f"Upgraded legacy concept: {concept_data['word']}")
            return upgraded
        
        # For other formats, ensure required keys exist
        return self._ensure_required_keys(concept_data)

class ConceptManager:
    """Main concept management system with idempotent operations."""
    
    def __init__(self, concepts_dir: str = "concepts"):
        self.concepts_dir = concepts_dir
        self.schema_manager = ConceptSchemaManager(concepts_dir)
        self.logger = logging.getLogger(__name__)
        self.registered_concepts = set()
        self._load_registered_concepts()
    
    def _load_registered_concepts(self):
        """Load list of registered concepts from directory with _self_learned.json suffix support."""
        try:
            if os.path.exists(self.concepts_dir):
                for filename in os.listdir(self.concepts_dir):
                    if filename.endswith('_self_learned.json'):
                        concept_name = filename.replace('_self_learned.json', '')
                        self.registered_concepts.add(concept_name)
        except Exception as e:
            self.logger.error(f"Error loading registered concepts: {e}")
    
    def create_or_update_concept(self, word: str, word_type: str = "thing", 
                                conceptnet_data: Optional[Dict] = None, 
                                event: Optional[Any] = None) -> bool:
        """
        Create or update a concept idempotently with _self_learned.json suffix as in version 5.13.2.
        
        Args:
            word: The concept word
            word_type: Type of concept (thing, action, person, etc.)
            conceptnet_data: Optional ConceptNet data
            event: Optional event context
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Normalize word for filename and add _self_learned suffix
            safe_word = word.replace(' ', '_').replace('/', '_')
            concept_file = os.path.join(self.concepts_dir, f"{safe_word}_self_learned.json")
            
            # Check if concept already exists
            if os.path.exists(concept_file):
                # Load existing concept
                with open(concept_file, 'r') as f:
                    concept_data = json.load(f)
                
                # Upgrade if needed
                if not self.schema_manager.validate_concept_schema(concept_data):
                    concept_data = self.schema_manager.upgrade_legacy_concept(concept_data)
                
                # Update existing concept
                concept_data = self._update_existing_concept(concept_data, conceptnet_data, event)
                
            else:
                # Create new concept
                concept_data = self._create_new_concept(word, word_type, conceptnet_data, event)
            
            # Save concept
            os.makedirs(self.concepts_dir, exist_ok=True)
            with open(concept_file, 'w') as f:
                json.dump(concept_data, f, indent=4)
            
            # Register concept (without _self_learned suffix for internal tracking)
            self.registered_concepts.add(safe_word)
            
            self.logger.info(f"✅ Concept '{word}' {'updated' if os.path.exists(concept_file) else 'created'} successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error creating/updating concept '{word}': {e}")
            return False
    
    def _create_new_concept(self, word: str, word_type: str, 
                           conceptnet_data: Optional[Dict], event: Optional[Any]) -> Dict[str, Any]:
        """Create a new concept with comprehensive schema as in version 5.13.2."""
        # Create comprehensive concept structure based on the provided examples
        concept_data = {
            "word": word,
            "type": word_type,
            "first_seen": str(datetime.now()),
            "last_updated": str(datetime.now()),
            "occurrences": 0,
            "contexts": [],
            "emotional_history": [],
            "conceptnet_data": conceptnet_data or {
                "has_data": False,
                "last_lookup": None,
                "edges": [],
                "relationships": []
            },
            "related_concepts": [],
            "linked_needs": [],
            "linked_goals": [],
            "linked_skills": [],
            "linked_senses": [],
            "neucogar_emotional_associations": {
                "primary": "neutral",
                "sub_emotion": "calm",
                "neuro_coordinates": {
                    "dopamine": 0.0,
                    "serotonin": 0.0,
                    "noradrenaline": 0.0
                },
                "intensity": 0.0,
                "triggers": []
            },
            "emotional_associations": {},
            "contextual_usage": [],
            "semantic_relationships": [],
            "keywords": [],
            "values_alignment": {
                "value_alignments": {},
                "belief_alignments": {},
                "conflicts": [],
                "overall_alignment": 0.0,
                "acc_activation": 0.0,
                "recommendation": "Neutral - minimal alignment or conflict"
            },
            "beliefs": [],
            "Learning_Integration": {
                "enabled": False,
                "strategy": "none",
                "concept_learning_system": {
                    "neurological_basis": {
                        "reward_prediction_error": {
                            "expected_utility": 0.5,
                            "prediction_error": 0.0,
                            "learning_rate": 0.1
                        },
                        "attention_mechanism": {
                            "salience": 0.5,
                            "focus_level": 0.5
                        },
                        "memory_consolidation": {
                            "strength": 0.5,
                            "retrieval_ease": 0.5
                        }
                    },
                    "concept_learning_system": {
                        "pattern_recognition": {
                            "feature_extraction": [],
                            "similarity_threshold": 0.5
                        },
                        "categorization": {
                            "prototype_formation": {
                                "primary_features": [],
                                "secondary_features": []
                            },
                            "boundary_adjustment": 0.5
                        },
                        "generalization": {
                            "transfer_learning": {
                                "related_activities": []
                            },
                            "abstraction_level": 0.5
                        }
                    },
                    "learning_principles": {
                        "information_processing": {
                            "encoding_depth": 0.5,
                            "retrieval_practice": {
                                "spaced_repetition": {
                                    "next_review": "",
                                    "review_interval": 0.5
                                }
                            }
                        },
                        "motivational_factors": {
                            "intrinsic_interest": 0.5,
                            "extrinsic_rewards": 0.5
                        },
                        "metacognitive_awareness": {
                            "self_monitoring": 0.5,
                            "strategy_selection": 0.5
                        }
                    }
                },
                "concept_progression": {
                    "current_level": "basic_recognition",
                    "level_progress": 0.0,
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
                        "current_challenge": 0.5,
                        "success_rate": 0.5
                    },
                    "personalization": {
                        "learning_style": "general",
                        "preference_adaptation": 0.5
                    }
                }
            },
            "Learning_System": {
                "strategy": "none",
                "enabled": False,
                "learning_rate": 0.1,
                "retention_factor": 0.8
            }
        }
        
        # Update ConceptNet data if provided
        if conceptnet_data and conceptnet_data.get('has_data', False):
            concept_data['conceptnet_data'] = conceptnet_data
            self.logger.info(f"📚 Added ConceptNet data for '{word}' with {len(conceptnet_data.get('edges', []))} relationships")
            
            # Extract related concepts from ConceptNet edges
            if 'edges' in conceptnet_data:
                for edge in conceptnet_data['edges']:
                    target = edge.get('target', '')
                    if target and target not in concept_data.get('related_concepts', []):
                        concept_data['related_concepts'].append(target)
        
        # Add event context if available
        if event:
            context = self._create_event_context(event)
            concept_data["contexts"].append(context)
            
            # Update emotional history with NEUCOGAR data
            if hasattr(event, 'neucogar_emotional_state'):
                emotional_entry = {
                    "timestamp": str(event.timestamp),
                    "neucogar_emotional_state": event.neucogar_emotional_state,
                    "emotions": event.emotional_state["current_emotions"] if hasattr(event, 'emotional_state') else {},
                    "neurotransmitters": event.emotional_state["neurotransmitters"] if hasattr(event, 'emotional_state') else {}
                }
                concept_data["emotional_history"].append(emotional_entry)
                
                # Update NEUCOGAR emotional associations
                if hasattr(event, 'neucogar_emotional_state'):
                    neucogar_state = event.neucogar_emotional_state
                    if neucogar_state.get('primary') != 'neutral':
                        concept_data['neucogar_emotional_associations'] = {
                            "primary": neucogar_state.get('primary', 'neutral'),
                            "sub_emotion": neucogar_state.get('sub_emotion', 'calm'),
                            "neuro_coordinates": neucogar_state.get('neuro_coordinates', {
                                "dopamine": 0.0,
                                "serotonin": 0.0,
                                "noradrenaline": 0.0
                            }),
                            "intensity": neucogar_state.get('intensity', 0.0),
                            "triggers": neucogar_state.get('triggers', [])
                        }
        
        # Build contextual associations
        self._build_contextual_associations(concept_data, event)
        
        return concept_data
    
    def _update_existing_concept(self, concept_data: Dict[str, Any], 
                                conceptnet_data: Optional[Dict], event: Optional[Any]) -> Dict[str, Any]:
        """Update an existing concept with enhanced association building."""
        # Update occurrences
        concept_data["occurrences"] += 1
        concept_data["last_updated"] = str(datetime.now())
        
        # Update ConceptNet data if provided
        if conceptnet_data and conceptnet_data.get('has_data', False):
            concept_data['conceptnet_data'] = conceptnet_data
            self.logger.info(f"📚 Updated ConceptNet data for '{concept_data['word']}' with {len(conceptnet_data.get('edges', []))} relationships")
            
            # Extract related concepts from ConceptNet edges with enhanced processing
            if 'edges' in conceptnet_data:
                for edge in conceptnet_data['edges']:
                    target = edge.get('target', '')
                    relationship = edge.get('relationship', 'RelatedTo')
                    weight = edge.get('weight', 0.0)
                    
                    # Only add high-quality relationships
                    if target and weight > 3.0 and target not in concept_data.get('related_concepts', []):
                        concept_data['related_concepts'].append(target)
                        
                        # Add semantic relationships
                        if relationship not in concept_data.get('semantic_relationships', []):
                            concept_data['semantic_relationships'].append(relationship)
        
        # Add event context if available
        if event:
            context = self._create_event_context(event)
            concept_data["contexts"].append(context)
            
            # Update emotional history with NEUCOGAR data
            if hasattr(event, 'neucogar_emotional_state'):
                emotional_entry = {
                    "timestamp": str(event.timestamp),
                    "neucogar_emotional_state": event.neucogar_emotional_state,
                    "emotions": event.emotional_state["current_emotions"] if hasattr(event, 'emotional_state') else {},
                    "neurotransmitters": event.emotional_state["neurotransmitters"] if hasattr(event, 'emotional_state') else {}
                }
                concept_data["emotional_history"].append(emotional_entry)
                
                # Update NEUCOGAR emotional associations
                if hasattr(event, 'neucogar_emotional_state'):
                    neucogar_state = event.neucogar_emotional_state
                    if neucogar_state.get('primary') != 'neutral':
                        concept_data['neucogar_emotional_associations'] = {
                            "primary": neucogar_state.get('primary', 'neutral'),
                            "sub_emotion": neucogar_state.get('sub_emotion', 'calm'),
                            "neuro_coordinates": neucogar_state.get('neuro_coordinates', {
                                "dopamine": 0.0,
                                "serotonin": 0.0,
                                "noradrenaline": 0.0
                            }),
                            "intensity": neucogar_state.get('intensity', 0.0),
                            "triggers": neucogar_state.get('triggers', [])
                        }
        
        # Build contextual associations
        self._build_contextual_associations(concept_data, event)
        
        return concept_data
    
    def _create_event_context(self, event: Any) -> Dict[str, Any]:
        """Create context entry from event."""
        return {
            "timestamp": str(event.timestamp),
            "WHAT": event.WHAT,
            "WHERE": event.WHERE,
            "WHY": event.WHY,
            "HOW": event.HOW,
            "neucogar_emotional_state": event.neucogar_emotional_state if hasattr(event, 'neucogar_emotional_state') else {},
            "emotions": event.emotional_state["current_emotions"] if hasattr(event, 'emotional_state') else {},
            "neurotransmitters": event.emotional_state["neurotransmitters"] if hasattr(event, 'emotional_state') else {}
        }
    
    def _build_contextual_associations(self, concept_data: Dict[str, Any], event: Optional[Any]):
        """Build contextual associations for enhanced concept relationships."""
        if not event:
            return
            
        try:
            # Extract keywords from event context
            keywords = set()
            if hasattr(event, 'WHAT') and event.WHAT:
                words = event.WHAT.lower().split()
                keywords.update([word for word in words if len(word) > 2])
            
            if hasattr(event, 'WHERE') and event.WHERE:
                words = event.WHERE.lower().split()
                keywords.update([word for word in words if len(word) > 2])
            
            # Add keywords to concept
            for keyword in keywords:
                if keyword not in concept_data.get('keywords', []):
                    concept_data['keywords'].append(keyword)
            
            # Build contextual usage patterns
            if hasattr(event, 'WHAT') and event.WHAT:
                usage_pattern = f"Used in context: {event.WHAT}"
                if usage_pattern not in concept_data.get('contextual_usage', []):
                    concept_data['contextual_usage'].append(usage_pattern)
            
            # Link to needs and goals based on context
            if hasattr(event, 'WHY') and event.WHY:
                why_text = event.WHERE.lower()
                
                # Check for need-related keywords
                need_keywords = ['need', 'want', 'desire', 'require', 'must', 'should']
                for keyword in need_keywords:
                    if keyword in why_text:
                        # This could be linked to a need
                        self.logger.info(f"Potential need association for {concept_data['word']}: {keyword}")
            
            # Link to skills based on HOW
            if hasattr(event, 'HOW') and event.HOW:
                how_text = event.HOW.lower()
                
                # Check for skill-related keywords
                skill_keywords = ['skill', 'ability', 'capability', 'technique', 'method']
                for keyword in skill_keywords:
                    if keyword in how_text:
                        # This could be linked to a skill
                        self.logger.info(f"Potential skill association for {concept_data['word']}: {keyword}")
            
        except Exception as e:
            self.logger.error(f"Error building contextual associations: {e}")
    
    def get_concept(self, word: str) -> Optional[Dict[str, Any]]:
        """Get a concept by word with _self_learned.json suffix support."""
        try:
            safe_word = word.replace(' ', '_').replace('/', '_')
            concept_file = os.path.join(self.concepts_dir, f"{safe_word}_self_learned.json")
            
            if os.path.exists(concept_file):
                with open(concept_file, 'r') as f:
                    concept_data = json.load(f)
                
                # Ensure schema is valid
                if not self.schema_manager.validate_concept_schema(concept_data):
                    concept_data = self.schema_manager.upgrade_legacy_concept(concept_data)
                
                return concept_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting concept '{word}': {e}")
            return None
    
    def list_concepts(self) -> List[str]:
        """List all registered concepts."""
        return list(self.registered_concepts)
    
    def upgrade_all_concepts(self) -> int:
        """Upgrade all concepts to current schema with _self_learned.json suffix support."""
        upgraded_count = 0
        
        try:
            for filename in os.listdir(self.concepts_dir):
                if filename.endswith('_self_learned.json'):
                    concept_file = os.path.join(self.concepts_dir, filename)
                    
                    with open(concept_file, 'r') as f:
                        concept_data = json.load(f)
                    
                    # Check if upgrade is needed
                    if not self.schema_manager.validate_concept_schema(concept_data):
                        # Upgrade the concept
                        concept_data = self.schema_manager.upgrade_legacy_concept(concept_data)
                        
                        # Save upgraded concept
                        with open(concept_file, 'w') as f:
                            json.dump(concept_data, f, indent=4)
                        
                        upgraded_count += 1
                        self.logger.info(f"Upgraded concept: {filename}")
            
            self.logger.info(f"Upgraded {upgraded_count} concepts to current schema")
            return upgraded_count
            
        except Exception as e:
            self.logger.error(f"Error upgrading concepts: {e}")
            return upgraded_count

class ConceptSystem:
    """Main concept system interface that wraps ConceptManager with personality integration."""
    
    def __init__(self, personality_type: str = 'INTP'):
        self.personality_type = personality_type
        self.concept_manager = ConceptManager()
        self.logger = logging.getLogger(__name__)
        # Initialize registered_concepts to prevent AttributeError
        self.registered_concepts = set()
        self._load_registered_concepts()
        
    def _load_registered_concepts(self):
        """Load list of registered concepts from directory with _self_learned.json suffix support."""
        try:
            concepts_dir = "concepts"
            if os.path.exists(concepts_dir):
                for filename in os.listdir(concepts_dir):
                    if filename.endswith('_self_learned.json'):
                        concept_name = filename.replace('_self_learned.json', '')
                        self.registered_concepts.add(concept_name)
        except Exception as e:
            self.logger.error(f"Error loading registered concepts: {e}")
        
    def create_or_update_concept(self, word: str, word_type: str = "thing", 
                                conceptnet_data: Optional[Dict] = None, 
                                event: Optional[Any] = None) -> bool:
        """Create or update a concept."""
        return self.concept_manager.create_or_update_concept(word, word_type, conceptnet_data, event)
    
    def get_concept(self, word: str) -> Optional[Dict[str, Any]]:
        """Get a concept by word."""
        return self.concept_manager.get_concept(word)
    
    def list_concepts(self) -> List[str]:
        """List all registered concepts."""
        return self.concept_manager.list_concepts()
    
    def upgrade_all_concepts(self) -> int:
        """Upgrade all concepts to current schema."""
        return self.concept_manager.upgrade_all_concepts()
    
    def get_related_concepts(self, concept_name: str, limit: int = 10) -> List[str]:
        """
        Get related concepts for imagination system fragment retrieval.
        
        Args:
            concept_name: The concept to find related concepts for
            limit: Maximum number of related concepts to return
            
        Returns:
            List of related concept names
        """
        try:
            related = []
            
            # Get concept data
            concept_data = self.get_concept(concept_name)
            if concept_data:
                # Add direct relations from concept data
                relations = concept_data.get("relations", [])
                if isinstance(relations, list):
                    related.extend(relations)
                elif isinstance(relations, dict):
                    # Handle dict format relations
                    for rel_type, rel_list in relations.items():
                        if isinstance(rel_list, list):
                            related.extend(rel_list)
                
                # Add co-occurrence concepts
                co_occurrence = concept_data.get("co_occurrence", [])
                if isinstance(co_occurrence, list):
                    related.extend(co_occurrence)
            
            # Add semantic neighbors from ConceptNet if available
            try:
                if hasattr(self.concept_manager, 'conceptnet') and self.concept_manager.conceptnet:
                    conceptnet_relations = self.concept_manager.conceptnet.get_relations(concept_name)
                    if conceptnet_relations:
                        related.extend(conceptnet_relations)
            except Exception as e:
                self.logger.debug(f"ConceptNet relations not available: {e}")
            
            # Add fallback related concepts based on concept type
            if not related:
                related = self._get_fallback_related_concepts(concept_name)
            
            # Remove duplicates and limit results
            unique_related = list(set(related))
            return unique_related[:limit]
            
        except Exception as e:
            self.logger.warning(f"Error getting related concepts for '{concept_name}': {e}")
            return self._get_fallback_related_concepts(concept_name)[:limit]
    
    def _get_fallback_related_concepts(self, concept_name: str) -> List[str]:
        """Get fallback related concepts when no direct relations exist."""
        fallback_concepts = []
        
        # Add common related concepts based on concept type
        if any(word in concept_name.lower() for word in ["person", "human", "man", "woman", "boy", "girl"]):
            fallback_concepts.extend(["interaction", "conversation", "emotion", "relationship"])
        elif any(word in concept_name.lower() for word in ["object", "thing", "item"]):
            fallback_concepts.extend(["use", "function", "location", "purpose"])
        elif any(word in concept_name.lower() for word in ["place", "location", "room"]):
            fallback_concepts.extend(["activity", "purpose", "atmosphere", "objects"])
        elif any(word in concept_name.lower() for word in ["action", "activity", "event"]):
            fallback_concepts.extend(["participants", "location", "time", "purpose"])
        else:
            # Generic fallback
            fallback_concepts.extend(["context", "purpose", "function", "relation"])
        
        return fallback_concepts
    
    def learn_new_reflex(self, input_text: str, response_text: str) -> bool:
        """
        Learn a new reflex pattern from input/response pair.
        
        Args:
            input_text: The input pattern to learn
            response_text: The response to associate with the input
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract concepts from input and response
            concepts = self._extract_concepts_from_text(input_text + " " + response_text)
            
            # Create or update concepts related to this reflex
            for concept in concepts:
                self.create_or_update_concept(
                    word=concept,
                    word_type="reflex_pattern",
                    conceptnet_data=None,
                    event=None
                )
            
            # Store the reflex pattern as a concept
            reflex_concept_name = f"reflex_{hash(input_text) % 10000}"
            reflex_data = {
                "input_pattern": input_text,
                "response_template": response_text,
                "learned_at": datetime.now().isoformat(),
                "usage_count": 0,
                "confidence": 0.5  # Initial confidence
            }
            
            # Create reflex concept
            success = self.create_or_update_concept(
                word=reflex_concept_name,
                word_type="reflex_pattern",
                conceptnet_data=None,
                event=None
            )
            
            if success:
                # Store reflex data in the concept
                concept_data = self.get_concept(reflex_concept_name)
                if concept_data:
                    concept_data["reflex_data"] = reflex_data
                    concept_data["keywords"].extend(concepts)
                    
                    # Save updated concept
                    safe_word = reflex_concept_name.replace(' ', '_').replace('/', '_')
                    concept_file = os.path.join(self.concept_manager.concepts_dir, f"{safe_word}_self_learned.json")
                    with open(concept_file, 'w') as f:
                        json.dump(concept_data, f, indent=4)
                
                self.logger.info(f"🧠 Learned new reflex: '{input_text}' -> '{response_text}' (concept: {reflex_concept_name}, keywords: {concepts})")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error learning new reflex: {e}")
            return False
    
    def _extract_concepts_from_text(self, text: str) -> List[str]:
        """Extract concepts from text for reflex learning."""
        try:
            # Simple concept extraction - could be enhanced with NLP
            words = text.lower().split()
            concepts = []
            
            # Look for meaningful words (longer than 3 characters, not common words)
            common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall'}
            
            for word in words:
                # Clean word
                clean_word = ''.join(c for c in word if c.isalnum())
                if len(clean_word) > 3 and clean_word not in common_words:
                    concepts.append(clean_word)
            
            return concepts[:5]  # Limit to 5 concepts
            
        except Exception as e:
            self.logger.error(f"Error extracting concepts from text: {e}")
            return []

# Global instance
concept_manager = ConceptManager()
