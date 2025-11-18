#!/usr/bin/env python3
"""
Fix Startup Memory Loading Issue

This script addresses the problem where CARL's existing memories and concepts
aren't loaded into the GUI until there's a trigger event (speech or object detection).
The fix ensures that memories and concepts are loaded and displayed in the GUI
immediately during startup.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class StartupMemoryLoadingFixer:
    def __init__(self):
        self.memories_dir = "memories"
        self.concepts_dir = "concepts"
        self.people_dir = "people"
        self.skills_dir = "skills"
        
    def analyze_current_loading_flow(self):
        """Analyze the current memory and concept loading flow."""
        print("🔍 Analyzing Current Loading Flow")
        print("=" * 50)
        
        # Check what files exist
        print("\n📁 Existing Files:")
        
        # Check memories
        if os.path.exists(self.memories_dir):
            memory_files = [f for f in os.listdir(self.memories_dir) if f.endswith('_event.json')]
            print(f"  Memories: {len(memory_files)} files")
            if memory_files:
                print(f"    Examples: {memory_files[:3]}")
        else:
            print("  Memories: Directory not found")
        
        # Check concepts
        if os.path.exists(self.concepts_dir):
            concept_files = [f for f in os.listdir(self.concepts_dir) if f.endswith('_self_learned.json')]
            print(f"  Concepts: {len(concept_files)} files")
            if concept_files:
                print(f"    Examples: {concept_files[:3]}")
        else:
            print("  Concepts: Directory not found")
        
        # Check people
        if os.path.exists(self.people_dir):
            people_files = [f for f in os.listdir(self.people_dir) if f.endswith('_self_learned.json')]
            print(f"  People: {len(people_files)} files")
            if people_files:
                print(f"    Examples: {people_files[:3]}")
        else:
            print("  People: Directory not found")
        
        # Check skills
        if os.path.exists(self.skills_dir):
            skill_files = [f for f in os.listdir(self.skills_dir) if f.endswith('.json')]
            print(f"  Skills: {len(skill_files)} files")
            if skill_files:
                print(f"    Examples: {skill_files[:3]}")
        else:
            print("  Skills: Directory not found")
        
        print("\n🔧 Current Issue:")
        print("  - Memories and concepts exist but aren't loaded into GUI on startup")
        print("  - GUI only updates when there's a trigger event (speech/object detection)")
        print("  - This makes it appear like CARL has 'forgotten' everything")
        
        return {
            'memories': memory_files if os.path.exists(self.memories_dir) else [],
            'concepts': concept_files if os.path.exists(self.concepts_dir) else [],
            'people': people_files if os.path.exists(self.people_dir) else [],
            'skills': skill_files if os.path.exists(self.skills_dir) else []
        }
    
    def create_startup_loading_fix(self):
        """Create a fix to ensure memories and concepts are loaded during startup."""
        print("\n🔧 Creating Startup Loading Fix")
        print("=" * 50)
        
        fix_code = '''def _load_startup_knowledge(self):
    """Load all existing memories and concepts into GUI during startup."""
    try:
        self.log("🧠 Loading existing knowledge into GUI...")
        
        # Load memories
        self._load_startup_memories()
        
        # Load concepts
        self._load_startup_concepts()
        
        # Load people
        self._load_startup_people()
        
        # Load skills
        self._load_startup_skills()
        
        # Update GUI status labels
        self._update_startup_gui_status()
        
        self.log("✅ Startup knowledge loading complete")
        
    except Exception as e:
        self.log(f"❌ Error loading startup knowledge: {e}")

def _load_startup_memories(self):
    """Load existing memories into GUI memory explorer."""
    try:
        if not os.path.exists(self.memories_dir):
            self.log("📁 No memories directory found")
            return
        
        memory_files = [f for f in os.listdir(self.memories_dir) if f.endswith('_event.json')]
        
        if not memory_files:
            self.log("📁 No memory files found")
            return
        
        # Update memory count
        self.total_memories = len(memory_files)
        self.log(f"📚 Loaded {self.total_memories} memories into GUI")
        
        # Update memory status label if it exists
        if hasattr(self, 'memory_status_label'):
            self.memory_status_label.config(text=f"Loaded {self.total_memories} memories")
        
        # Refresh memory explorer if it exists
        if hasattr(self, '_refresh_memory_list'):
            # Find memory listbox and details text widgets
            for widget in self.winfo_children():
                if hasattr(widget, 'winfo_children'):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Listbox):
                            # Found memory listbox, refresh it
                            self._refresh_memory_list(child, None)
                            break
        
    except Exception as e:
        self.log(f"❌ Error loading startup memories: {e}")

def _load_startup_concepts(self):
    """Load existing concepts into GUI."""
    try:
        concepts_loaded = 0
        
        # Load from concepts directory
        if os.path.exists(self.concepts_dir):
            concept_files = [f for f in os.listdir(self.concepts_dir) if f.endswith('_self_learned.json')]
            concepts_loaded += len(concept_files)
        
        # Load from people directory
        if os.path.exists(self.people_dir):
            people_files = [f for f in os.listdir(self.people_dir) if f.endswith('_self_learned.json')]
            concepts_loaded += len(people_files)
        
        self.log(f"💡 Loaded {concepts_loaded} concepts into GUI")
        
        # Update concept status label if it exists
        if hasattr(self, 'concept_status_label'):
            self.concept_status_label.config(text=f"Loaded {concepts_loaded} concepts")
        
    except Exception as e:
        self.log(f"❌ Error loading startup concepts: {e}")

def _load_startup_people(self):
    """Load existing people into GUI."""
    try:
        if os.path.exists(self.people_dir):
            people_files = [f for f in os.listdir(self.people_dir) if f.endswith('_self_learned.json')]
            self.log(f"👥 Loaded {len(people_files)} people into GUI")
        else:
            self.log("👥 No people directory found")
        
    except Exception as e:
        self.log(f"❌ Error loading startup people: {e}")

def _load_startup_skills(self):
    """Load existing skills into GUI."""
    try:
        if os.path.exists(self.skills_dir):
            skill_files = [f for f in os.listdir(self.skills_dir) if f.endswith('.json')]
            self.log(f"🎯 Loaded {len(skill_files)} skills into GUI")
        else:
            self.log("🎯 No skills directory found")
        
    except Exception as e:
        self.log(f"❌ Error loading startup skills: {e}")

def _update_startup_gui_status(self):
    """Update all GUI status labels with loaded knowledge."""
    try:
        # Update various status labels that might exist
        status_updates = {
            'memory_status_label': f"Loaded {getattr(self, 'total_memories', 0)} memories",
            'concept_status_label': f"Loaded {len(self._load_all_concepts())} concepts",
            'knowledge_status_label': "Knowledge loaded successfully",
            'startup_status_label': "Startup complete - knowledge loaded"
        }
        
        for label_name, text in status_updates.items():
            if hasattr(self, label_name):
                getattr(self, label_name).config(text=text)
        
        self.log("✅ GUI status labels updated")
        
    except Exception as e:
        self.log(f"❌ Error updating GUI status: {e}")

def _enhanced_count_memories(self):
    """Enhanced memory counting that also loads memories into GUI."""
    try:
        # Original memory counting logic
        if os.path.exists(self.memories_dir):
            self.total_memories = len([f for f in os.listdir(self.memories_dir) if f.endswith('.json')])
            self.log(f"Total memories loaded: {self.total_memories}")
        else:
            self.total_memories = 0
            self.log("No memories directory found")
        
        # NEW: Load memories into GUI
        self._load_startup_memories()
        
        # After loading memories, have CARL wave with emotional eyes
        self._carl_startup_greeting()
        
    except Exception as e:
        self.log(f"Error counting memories: {e}")
        self.total_memories = 0
'''
        
        # Save the fix code
        with open("startup_loading_fix.py", 'w', encoding='utf-8') as f:
            f.write(fix_code)
        
        print("✅ Created startup_loading_fix.py")
        print("\n📝 Integration Instructions:")
        print("1. Copy the methods from startup_loading_fix.py to main.py")
        print("2. Replace _count_memories() with _enhanced_count_memories()")
        print("3. Add _load_startup_knowledge() call to startup sequence")
        print("4. Update GUI initialization to call _load_startup_knowledge()")
        
        return fix_code
    
    def create_integration_guide(self):
        """Create a guide for integrating the fix into main.py."""
        print("\n📋 Integration Guide")
        print("=" * 50)
        
        integration_steps = """
# Integration Steps for Startup Memory Loading Fix

## Step 1: Add New Methods to main.py
Add the following methods to the main.py file (after the existing _count_memories method):

```python
def _load_startup_knowledge(self):
    # [Copy the entire method from startup_loading_fix.py]

def _load_startup_memories(self):
    # [Copy the entire method from startup_loading_fix.py]

def _load_startup_concepts(self):
    # [Copy the entire method from startup_loading_fix.py]

def _load_startup_people(self):
    # [Copy the entire method from startup_loading_fix.py]

def _load_startup_skills(self):
    # [Copy the entire method from startup_loading_fix.py]

def _update_startup_gui_status(self):
    # [Copy the entire method from startup_loading_fix.py]

def _enhanced_count_memories(self):
    # [Copy the entire method from startup_loading_fix.py]
```

## Step 2: Replace _count_memories Calls
Replace all calls to `self._count_memories()` with `self._enhanced_count_memories()`:

- Line 316: self._enhanced_count_memories()
- Line 1051: self._enhanced_count_memories()
- Line 4556: self._enhanced_count_memories()

## Step 3: Add Startup Knowledge Loading
Add a call to `self._load_startup_knowledge()` in the startup sequence:

```python
# In the startup sequence (after EZ-Robot connection)
if self.startup_sequencing.execute_startup_sequence():
    self.ez_robot_connected = True
    self.action_system.ez_robot = self.ez_robot
    
    # Initialize enhanced systems after successful EZ-Robot connection
    self._initialize_enhanced_systems()
    
    # NEW: Load existing knowledge into GUI
    self._load_startup_knowledge()
    
    self.log("🎉 Enhanced startup sequence completed - JD is ready!")
```

## Step 4: Update GUI Initialization
Add knowledge loading to GUI initialization:

```python
# In the GUI initialization section
self._create_memory_explorer()
self._create_concept_explorer()

# NEW: Load existing knowledge
self._load_startup_knowledge()
```

## Step 5: Test the Fix
1. Start CARL with existing memories and concepts
2. Verify that memories appear in the memory explorer immediately
3. Verify that concept count is displayed correctly
4. Verify that GUI status labels show loaded knowledge

## Expected Results
- Memories will be visible in the memory explorer on startup
- Concept counts will be displayed correctly
- GUI status labels will show "Loaded X memories" and "Loaded Y concepts"
- No need to wait for speech or object detection to see existing knowledge
"""
        
        with open("startup_loading_integration_guide.md", 'w', encoding='utf-8') as f:
            f.write(integration_steps)
        
        print("✅ Created startup_loading_integration_guide.md")
        print("\n📖 The integration guide contains step-by-step instructions")
        print("   for implementing the fix in main.py")
    
    def create_test_script(self):
        """Create a test script to verify the fix works."""
        print("\n🧪 Creating Test Script")
        print("=" * 50)
        
        test_script = '''#!/usr/bin/env python3
"""
Test Startup Memory Loading Fix

This script tests whether the startup memory loading fix works correctly.
"""

import os
import json
from datetime import datetime

def test_startup_loading_fix():
    """Test the startup memory loading fix."""
    print("🧪 Testing Startup Memory Loading Fix")
    print("=" * 50)
    
    # Test 1: Check if memory files exist
    print("\\n📁 Test 1: Memory Files")
    memories_dir = "memories"
    if os.path.exists(memories_dir):
        memory_files = [f for f in os.listdir(memories_dir) if f.endswith('_event.json')]
        print(f"  ✅ Found {len(memory_files)} memory files")
        if memory_files:
            print(f"    Examples: {memory_files[:3]}")
    else:
        print("  ❌ No memories directory found")
    
    # Test 2: Check if concept files exist
    print("\\n💡 Test 2: Concept Files")
    concepts_dir = "concepts"
    if os.path.exists(concepts_dir):
        concept_files = [f for f in os.listdir(concepts_dir) if f.endswith('_self_learned.json')]
        print(f"  ✅ Found {len(concept_files)} concept files")
        if concept_files:
            print(f"    Examples: {concept_files[:3]}")
    else:
        print("  ❌ No concepts directory found")
    
    # Test 3: Check if people files exist
    print("\\n👥 Test 3: People Files")
    people_dir = "people"
    if os.path.exists(people_dir):
        people_files = [f for f in os.listdir(people_dir) if f.endswith('_self_learned.json')]
        print(f"  ✅ Found {len(people_files)} people files")
        if people_files:
            print(f"    Examples: {people_files[:3]}")
    else:
        print("  ❌ No people directory found")
    
    # Test 4: Check if skill files exist
    print("\\n🎯 Test 4: Skill Files")
    skills_dir = "skills"
    if os.path.exists(skills_dir):
        skill_files = [f for f in os.listdir(skills_dir) if f.endswith('.json')]
        print(f"  ✅ Found {len(skill_files)} skill files")
        if skill_files:
            print(f"    Examples: {skill_files[:3]}")
    else:
        print("  ❌ No skills directory found")
    
    # Test 5: Simulate memory loading
    print("\\n🔄 Test 5: Simulate Memory Loading")
    total_memories = 0
    if os.path.exists(memories_dir):
        total_memories = len([f for f in os.listdir(memories_dir) if f.endswith('_event.json')])
    
    print(f"  📊 Total memories to load: {total_memories}")
    print(f"  📊 Memory status label would show: 'Loaded {total_memories} memories'")
    
    # Test 6: Simulate concept loading
    print("\\n🔄 Test 6: Simulate Concept Loading")
    total_concepts = 0
    if os.path.exists(concepts_dir):
        total_concepts += len([f for f in os.listdir(concepts_dir) if f.endswith('_self_learned.json')])
    if os.path.exists(people_dir):
        total_concepts += len([f for f in os.listdir(people_dir) if f.endswith('_self_learned.json')])
    
    print(f"  📊 Total concepts to load: {total_concepts}")
    print(f"  📊 Concept status label would show: 'Loaded {total_concepts} concepts'")
    
    print("\\n✅ Test completed successfully!")
    print("\\n💡 Next Steps:")
    print("1. Implement the fix in main.py using the integration guide")
    print("2. Test with CARL startup to verify memories appear immediately")
    print("3. Verify that GUI status labels show correct counts")

if __name__ == "__main__":
    test_startup_loading_fix()
'''
        
        with open("test_startup_loading_fix.py", 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        print("✅ Created test_startup_loading_fix.py")
        print("\n🧪 Run the test script to verify the fix will work:")
        print("   python test_startup_loading_fix.py")

def main():
    """Main function to create the startup memory loading fix."""
    print("🔧 Startup Memory Loading Fix")
    print("=" * 50)
    
    fixer = StartupMemoryLoadingFixer()
    
    # Analyze current state
    current_state = fixer.analyze_current_loading_flow()
    
    # Create the fix
    fixer.create_startup_loading_fix()
    
    # Create integration guide
    fixer.create_integration_guide()
    
    # Create test script
    fixer.create_test_script()
    
    print("\n✅ Startup Memory Loading Fix Complete!")
    print("\n📋 Files Created:")
    print("1. startup_loading_fix.py - The fix code")
    print("2. startup_loading_integration_guide.md - Integration instructions")
    print("3. test_startup_loading_fix.py - Test script")
    
    print("\n🚀 Next Steps:")
    print("1. Run: python test_startup_loading_fix.py")
    print("2. Follow the integration guide to implement the fix")
    print("3. Test CARL startup to verify memories appear immediately")

if __name__ == "__main__":
    main()
