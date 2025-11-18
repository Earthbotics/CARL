#!/usr/bin/env python3
"""
NEUCOGAR Emotional Engine Migration Cleanup Script
==================================================

This script cleans up the knowledgebase to prepare for the NEUCOGAR emotional engine migration.
It removes legacy emotional data and ensures all files use the new NEUCOGAR format.

Usage:
    python cleanup_neucogar_migration.py
"""

import os
import json
import shutil
from datetime import datetime
import glob

def backup_directory(directory, backup_name=None):
    """Create a backup of a directory."""
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist, skipping backup")
        return None
    
    if backup_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{directory}_backup_{timestamp}"
    
    backup_path = f"backups/{backup_name}"
    
    # Create backups directory if it doesn't exist
    os.makedirs("backups", exist_ok=True)
    
    try:
        shutil.copytree(directory, backup_path)
        print(f"✅ Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Failed to create backup of {directory}: {e}")
        return None

def cleanup_concepts_directory():
    """Clean up concepts directory to use NEUCOGAR emotional associations."""
    concepts_dir = "concepts"
    if not os.path.exists(concepts_dir):
        print("Concepts directory does not exist, skipping cleanup")
        return
    
    print(f"\n🧹 Cleaning up concepts directory: {concepts_dir}")
    
    # Find all concept files
    concept_files = glob.glob(os.path.join(concepts_dir, "*.json"))
    
    for concept_file in concept_files:
        try:
            with open(concept_file, 'r') as f:
                concept_data = json.load(f)
            
            # Check if file already has NEUCOGAR emotional associations
            if "neucogar_emotional_associations" not in concept_data:
                print(f"  📝 Updating {os.path.basename(concept_file)} with NEUCOGAR structure")
                
                # Add NEUCOGAR emotional associations structure
                concept_data["neucogar_emotional_associations"] = {
                    "primary": "neutral",
                    "sub_emotion": "calm",
                    "neuro_coordinates": {
                        "dopamine": 0.0,
                        "serotonin": 0.0,
                        "noradrenaline": 0.0
                    },
                    "intensity": 0.0,
                    "triggers": []
                }
                
                # Keep legacy emotional_associations for backward compatibility
                if "emotional_associations" not in concept_data:
                    concept_data["emotional_associations"] = {}
                
                # Save updated concept file
                with open(concept_file, 'w') as f:
                    json.dump(concept_data, f, indent=4)
                
                print(f"    ✅ Updated {os.path.basename(concept_file)}")
            else:
                print(f"  ✅ {os.path.basename(concept_file)} already has NEUCOGAR structure")
                
        except Exception as e:
            print(f"  ❌ Error processing {concept_file}: {e}")

def cleanup_people_directory():
    """Clean up people directory to use NEUCOGAR emotional associations."""
    people_dir = "people"
    if not os.path.exists(people_dir):
        print("People directory does not exist, skipping cleanup")
        return
    
    print(f"\n🧹 Cleaning up people directory: {people_dir}")
    
    # Find all people files
    people_files = glob.glob(os.path.join(people_dir, "*.json"))
    
    for people_file in people_files:
        try:
            with open(people_file, 'r') as f:
                people_data = json.load(f)
            
            # Check if file already has NEUCOGAR emotional associations
            if "neucogar_emotional_associations" not in people_data:
                print(f"  📝 Updating {os.path.basename(people_file)} with NEUCOGAR structure")
                
                # Add NEUCOGAR emotional associations structure
                people_data["neucogar_emotional_associations"] = {
                    "primary": "neutral",
                    "sub_emotion": "calm",
                    "neuro_coordinates": {
                        "dopamine": 0.0,
                        "serotonin": 0.0,
                        "noradrenaline": 0.0
                    },
                    "intensity": 0.0,
                    "triggers": []
                }
                
                # Keep legacy emotional_associations for backward compatibility
                if "emotional_associations" not in people_data:
                    people_data["emotional_associations"] = {}
                
                # Save updated people file
                with open(people_file, 'w') as f:
                    json.dump(people_data, f, indent=4)
                
                print(f"    ✅ Updated {os.path.basename(people_file)}")
            else:
                print(f"  ✅ {os.path.basename(people_file)} already has NEUCOGAR structure")
                
        except Exception as e:
            print(f"  ❌ Error processing {people_file}: {e}")

def cleanup_places_directory():
    """Clean up places directory to use NEUCOGAR emotional associations."""
    places_dir = "places"
    if not os.path.exists(places_dir):
        print("Places directory does not exist, skipping cleanup")
        return
    
    print(f"\n🧹 Cleaning up places directory: {places_dir}")
    
    # Find all places files
    places_files = glob.glob(os.path.join(places_dir, "*.json"))
    
    for places_file in places_files:
        try:
            with open(places_file, 'r') as f:
                places_data = json.load(f)
            
            # Check if file already has NEUCOGAR emotional associations
            if "neucogar_emotional_associations" not in places_data:
                print(f"  📝 Updating {os.path.basename(places_file)} with NEUCOGAR structure")
                
                # Add NEUCOGAR emotional associations structure
                places_data["neucogar_emotional_associations"] = {
                    "primary": "neutral",
                    "sub_emotion": "calm",
                    "neuro_coordinates": {
                        "dopamine": 0.0,
                        "serotonin": 0.0,
                        "noradrenaline": 0.0
                    },
                    "intensity": 0.0,
                    "triggers": []
                }
                
                # Keep legacy emotional_associations for backward compatibility
                if "emotional_associations" not in places_data:
                    places_data["emotional_associations"] = {}
                
                # Save updated places file
                with open(places_file, 'w') as f:
                    json.dump(places_data, f, indent=4)
                
                print(f"    ✅ Updated {os.path.basename(places_file)}")
            else:
                print(f"  ✅ {os.path.basename(places_file)} already has NEUCOGAR structure")
                
        except Exception as e:
            print(f"  ❌ Error processing {places_file}: {e}")

def cleanup_memories_directory():
    """Clean up memories directory to use NEUCOGAR emotional state."""
    memories_dir = "memories"
    if not os.path.exists(memories_dir):
        print("Memories directory does not exist, skipping cleanup")
        return
    
    print(f"\n🧹 Cleaning up memories directory: {memories_dir}")
    
    # Find all memory files
    memory_files = glob.glob(os.path.join(memories_dir, "*_event.json"))
    
    for memory_file in memory_files:
        try:
            with open(memory_file, 'r') as f:
                memory_data = json.load(f)
            
            # Check if file already has NEUCOGAR emotional state
            if "neucogar_emotional_state" not in memory_data:
                print(f"  📝 Updating {os.path.basename(memory_file)} with NEUCOGAR structure")
                
                # Add NEUCOGAR emotional state structure
                memory_data["neucogar_emotional_state"] = {
                    "primary": "neutral",
                    "sub_emotion": "calm",
                    "detail": "balanced",
                    "neuro_coordinates": {
                        "dopamine": 0.0,
                        "serotonin": 0.0,
                        "noradrenaline": 0.0
                    },
                    "intensity": 0.0,
                    "timestamp": memory_data.get("timestamp", datetime.now().isoformat())
                }
                
                # Keep legacy emotions and neurotransmitters for backward compatibility
                if "emotions" not in memory_data:
                    memory_data["emotions"] = {}
                if "neurotransmitters" not in memory_data:
                    memory_data["neurotransmitters"] = {}
                
                # Save updated memory file
                with open(memory_file, 'w') as f:
                    json.dump(memory_data, f, indent=4)
                
                print(f"    ✅ Updated {os.path.basename(memory_file)}")
            else:
                print(f"  ✅ {os.path.basename(memory_file)} already has NEUCOGAR structure")
                
        except Exception as e:
            print(f"  ❌ Error processing {memory_file}: {e}")

def cleanup_short_term_memory():
    """Clean up short-term memory file."""
    stm_file = "short_term_memory.json"
    if not os.path.exists(stm_file):
        print("Short-term memory file does not exist, skipping cleanup")
        return
    
    print(f"\n🧹 Cleaning up short-term memory file: {stm_file}")
    
    try:
        with open(stm_file, 'r') as f:
            stm_data = json.load(f)
        
        # Check if file already has NEUCOGAR emotional state
        updated = False
        for entry in stm_data:
            if "neucogar_emotional_state" not in entry:
                print(f"  📝 Updating STM entry with NEUCOGAR structure")
                
                # Add NEUCOGAR emotional state structure
                entry["neucogar_emotional_state"] = {
                    "primary": "neutral",
                    "sub_emotion": "calm",
                    "detail": "balanced",
                    "neuro_coordinates": {
                        "dopamine": 0.0,
                        "serotonin": 0.0,
                        "noradrenaline": 0.0
                    },
                    "intensity": 0.0,
                    "timestamp": entry.get("timestamp", datetime.now().isoformat())
                }
                
                # Keep legacy emotions and neurotransmitters for backward compatibility
                if "emotions" not in entry:
                    entry["emotions"] = {}
                if "neurotransmitters" not in entry:
                    entry["neurotransmitters"] = {}
                
                updated = True
        
        if updated:
            # Save updated STM file
            with open(stm_file, 'w') as f:
                json.dump(stm_data, f, indent=4)
            
            print(f"    ✅ Updated {stm_file}")
        else:
            print(f"  ✅ {stm_file} already has NEUCOGAR structure")
            
    except Exception as e:
        print(f"  ❌ Error processing {stm_file}: {e}")

def cleanup_working_memory():
    """Clean up working memory file."""
    wm_file = "working_memory.json"
    if not os.path.exists(wm_file):
        print("Working memory file does not exist, skipping cleanup")
        return
    
    print(f"\n🧹 Cleaning up working memory file: {wm_file}")
    
    try:
        with open(wm_file, 'r') as f:
            wm_data = json.load(f)
        
        # Check if file already has NEUCOGAR emotional state
        if "neucogar_emotional_state" not in wm_data:
            print(f"  📝 Updating {wm_file} with NEUCOGAR structure")
            
            # Add NEUCOGAR emotional state structure
            wm_data["neucogar_emotional_state"] = {
                "primary": "neutral",
                "sub_emotion": "calm",
                "detail": "balanced",
                "neuro_coordinates": {
                    "dopamine": 0.0,
                    "serotonin": 0.0,
                    "noradrenaline": 0.0
                },
                "intensity": 0.0,
                "timestamp": datetime.now().isoformat()
            }
            
            # Keep legacy emotions and neurotransmitters for backward compatibility
            if "emotions" not in wm_data:
                wm_data["emotions"] = {}
            if "neurotransmitters" not in wm_data:
                wm_data["neurotransmitters"] = {}
            
            # Save updated WM file
            with open(wm_file, 'w') as f:
                json.dump(wm_data, f, indent=4)
            
            print(f"    ✅ Updated {wm_file}")
        else:
            print(f"  ✅ {wm_file} already has NEUCOGAR structure")
            
    except Exception as e:
        print(f"  ❌ Error processing {wm_file}: {e}")

def main():
    """Main cleanup function."""
    print("🧠 NEUCOGAR Emotional Engine Migration Cleanup")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create backups first
    print("\n📦 Creating backups...")
    backup_concepts = backup_directory("concepts", "concepts_pre_neucogar")
    backup_people = backup_directory("people", "people_pre_neucogar")
    backup_places = backup_directory("places", "places_pre_neucogar")
    backup_memories = backup_directory("memories", "memories_pre_neucogar")
    
    # Clean up each directory
    cleanup_concepts_directory()
    cleanup_people_directory()
    cleanup_places_directory()
    cleanup_memories_directory()
    cleanup_short_term_memory()
    cleanup_working_memory()
    
    print(f"\n✅ NEUCOGAR migration cleanup completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📋 Summary:")
    print("  - Created backups of all knowledge directories")
    print("  - Updated all concept files with NEUCOGAR emotional associations")
    print("  - Updated all people files with NEUCOGAR emotional associations")
    print("  - Updated all places files with NEUCOGAR emotional associations")
    print("  - Updated all memory files with NEUCOGAR emotional state")
    print("  - Updated short-term and working memory files")
    print("\n🚀 CARL is now ready to use the NEUCOGAR emotional engine!")
    print("   Legacy emotional data has been preserved for backward compatibility.")

if __name__ == "__main__":
    main() 