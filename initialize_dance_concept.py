#!/usr/bin/env python3
"""
Initialize dance concept with all dance skills and associations.
This ensures CARL knows about all dance variants by default.
"""

import json
import os
from typing import Dict, List

def initialize_dance_concept():
    """Initialize the dance concept with all dance skills and associations."""
    
    # Define all dance skills that should be associated with the dance concept
    dance_skills = [
        "dance",
        "ymca_dance", 
        "disco_dance",
        "hands_dance",
        "predance",
        "wiggle_it"
    ]
    
    # Define dance skill descriptions
    dance_variants = {
        "ymca_dance": {
            "description": "YMCA dance with arm movements spelling Y-M-C-A",
            "energy_level": "high",
            "mood": "energetic",
            "difficulty": "medium",
            "keywords": ["ymca", "dance", "arms", "spelling"]
        },
        "disco_dance": {
            "description": "Disco-style dance with groovy movements",
            "energy_level": "high", 
            "mood": "fun",
            "difficulty": "medium",
            "keywords": ["disco", "dance", "groovy", "fun"]
        },
        "hands_dance": {
            "description": "Dance focusing on hand and arm movements",
            "energy_level": "medium",
            "mood": "playful", 
            "difficulty": "easy",
            "keywords": ["hands", "dance", "arms", "playful"]
        },
        "predance": {
            "description": "Preparatory dance movements",
            "energy_level": "low",
            "mood": "calm",
            "difficulty": "easy", 
            "keywords": ["pre", "dance", "preparation", "calm"]
        },
        "wiggle_it": {
            "description": "Wiggling dance movement",
            "energy_level": "medium",
            "mood": "silly",
            "difficulty": "easy",
            "keywords": ["wiggle", "dance", "silly", "fun"]
        }
    }
    
    # Create the dance concept
    dance_concept = {
        "word": "dance",
        "first_seen": "2025-07-30T09:10:22.700322",
        "last_updated": "2025-07-30T09:10:22.700322",
        "type": "action",
        "emotional_associations": {
            "joy": 0.8,
            "excitement": 0.7,
            "pleasure": 0.6,
            "energy": 0.9
        },
        "contextual_usage": [
            "physical movement to music",
            "expression through body movement", 
            "entertainment and performance",
            "exercise and fitness",
            "social interaction"
        ],
        "semantic_relationships": [
            "music",
            "movement",
            "performance",
            "entertainment",
            "exercise",
            "expression"
        ],
        "linked_skills": dance_skills,
        "related_concepts": [
            "music",
            "movement", 
            "performance",
            "entertainment",
            "exercise",
            "expression",
            "rhythm",
            "coordination"
        ],
        "dance_variants": dance_variants,
        "keywords": ["dance", "movement", "music", "rhythm", "performance", "entertainment"],
        "Learning_Integration": {
            "concept_learning_system": {
                "neurological_basis": {
                    "reward_prediction_error": {
                        "expected_utility": 0.8,
                        "prediction_error": 0.0,
                        "learning_rate": 0.2
                    },
                    "attention_mechanism": {
                        "salience": 0.9,
                        "focus_level": 0.8
                    },
                    "memory_consolidation": {
                        "strength": 0.8,
                        "retrieval_ease": 0.9
                    }
                },
                "concept_learning_system": {
                    "pattern_recognition": {
                        "feature_extraction": ["rhythm", "movement", "music", "expression"],
                        "similarity_threshold": 0.8
                    },
                    "categorization": {
                        "prototype_formation": {
                            "primary_features": ["movement", "music", "expression"],
                            "secondary_features": ["rhythm", "coordination", "energy"]
                        },
                        "boundary_adjustment": 0.8
                    },
                    "generalization": {
                        "transfer_learning": {
                            "related_activities": ["exercise", "performance", "entertainment"]
                        },
                        "abstraction_level": 0.7
                    }
                },
                "learning_principles": {
                    "information_processing": {
                        "encoding_depth": 0.8,
                        "retrieval_practice": {
                            "spaced_repetition": {
                                "next_review": "",
                                "review_interval": 0.5
                            }
                        }
                    },
                    "motivational_factors": {
                        "intrinsic_interest": 0.9,
                        "extrinsic_rewards": 0.7
                    },
                    "metacognitive_awareness": {
                        "self_monitoring": 0.8,
                        "strategy_selection": 0.7
                    }
                }
            },
            "concept_progression": {
                "current_level": "contextual_understanding",
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
                    "current_challenge": 0.7,
                    "success_rate": 0.8
                },
                "personalization": {
                    "learning_style": "kinesthetic",
                    "preference_adaptation": 0.8
                }
            }
        }
    }
    
    # Save the dance concept
    concepts_dir = "concepts"
    if not os.path.exists(concepts_dir):
        os.makedirs(concepts_dir)
    
    dance_concept_path = os.path.join(concepts_dir, "dance.json")
    with open(dance_concept_path, 'w') as f:
        json.dump(dance_concept, f, indent=4)
    
    print(f"✅ Dance concept initialized at {dance_concept_path}")
    print(f"📋 Linked skills: {dance_skills}")
    print(f"🎭 Dance variants: {list(dance_variants.keys())}")
    
    return dance_concept

def ensure_dance_skill_associations():
    """Ensure all dance skills are properly associated with the dance concept."""
    
    # Check if dance skills exist and create associations
    skills_dir = "skills"
    dance_skills = ["dance", "ymca_dance", "disco dance", "hands_dance", "predance", "wiggle_it"]
    
    for skill in dance_skills:
        skill_file = skill.replace(" ", "%20") + ".json"
        skill_path = os.path.join(skills_dir, skill_file)
        
        if os.path.exists(skill_path):
            print(f"✅ Dance skill exists: {skill}")
        else:
            print(f"⚠️  Dance skill missing: {skill}")
    
    print("🎯 Dance concept associations verified")

if __name__ == "__main__":
    print("🎭 Initializing Dance Concept System")
    print("=" * 50)
    
    # Initialize the dance concept
    dance_concept = initialize_dance_concept()
    
    # Ensure skill associations
    ensure_dance_skill_associations()
    
    print("\n🎉 Dance concept system initialization complete!")
    print("CARL now knows about all dance variants and their associations.") 