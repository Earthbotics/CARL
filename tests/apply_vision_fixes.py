#!/usr/bin/env python3
"""
Apply Vision System Fixes
=========================

This script automatically applies the vision system fixes to main.py.
"""

import os
import re
import shutil
from datetime import datetime

def backup_main_py():
    """Create a backup of main.py before making changes."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"main_backup_{timestamp}.py"
    
    if os.path.exists("main.py"):
        shutil.copy2("main.py", backup_file)
        print(f"✅ Created backup: {backup_file}")
        return backup_file
    else:
        print("❌ main.py not found")
        return None

def apply_fix_1_vision_initialization(content):
    """Fix vision system initialization."""
    print("🔧 Applying Fix 1: Vision System Initialization...")
    
    # Find and replace the incorrect initialization
    pattern = r"""        try:
            from vision_system import VisionSystem
            self\.vision_system = VisionSystem\(\)
            
            # Initialize vision detection controls on startup
            self\._initialize_vision_detection_controls\(\)
            self\.vision_system = VisionSystem\(memory_system=self\.memory_system\)
            print\("✅ Vision system initialized"\)"""
    
    replacement = """        try:
            from vision_system import VisionSystem
            self.vision_system = VisionSystem(
                memory_system=self.memory_system,
                openai_client=self.openai_client,
                settings=self.settings
            )
            
            # Initialize vision detection controls on startup
            self._initialize_vision_detection_controls()
            print("✅ Vision system initialized")"""
    
    if re.search(pattern, content, re.MULTILINE | re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        print("✅ Fix 1 applied successfully")
    else:
        print("⚠️  Fix 1 pattern not found - may already be fixed")
    
    return content

def apply_fix_2_owner_concept(content):
    """Fix owner concept error."""
    print("🔧 Applying Fix 2: Owner Concept Error...")
    
    pattern = r"""owner_name = self\.settings\.get\('people-owner', 'name', fallback='Joe'\)"""
    replacement = """owner_name = self.settings.get('people-owner', {}).get('name', 'Joe')"""
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print("✅ Fix 2 applied successfully")
    else:
        print("⚠️  Fix 2 pattern not found - may already be fixed")
    
    return content

def apply_fix_3_vision_analysis_trigger(content):
    """Add vision analysis trigger before thought processing."""
    print("🔧 Applying Fix 3: Vision Analysis Trigger...")
    
    pattern = r"""                # Add perceived_message to event_data for summary generation
                if hasattr\(event, 'perceived_message'\):
                    event_data\["perceived_message"\] = event\.perceived_message
                
                # Get Carl's thought process
                event_data = await self\.get_carl_thought\(event_data\)"""
    
    replacement = """                # Add perceived_message to event_data for summary generation
                if hasattr(event, 'perceived_message'):
                    event_data["perceived_message"] = event.perceived_message
                
                # CRITICAL: Trigger vision analysis just before get_carl_thought
                # This ensures vision data is available for the thought process
                self.log("👁️ Triggering vision analysis before thought processing...")
                vision_result = await self._trigger_vision_analysis_before_thought()
                
                # Add vision result to event_data for memory storage
                if vision_result:
                    event_data["vision_analysis"] = vision_result
                    self.log(f"👁️ Vision analysis completed: {len(vision_result.get('objects_detected', []))} objects detected")
                else:
                    self.log("👁️ No vision analysis result available")
                
                # Get Carl's thought process
                event_data = await self.get_carl_thought(event_data)"""
    
    if re.search(pattern, content, re.MULTILINE | re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        print("✅ Fix 3 applied successfully")
    else:
        print("⚠️  Fix 3 pattern not found - may already be fixed")
    
    return content

def apply_fix_4_vision_context(content):
    """Add vision context to thought process."""
    print("🔧 Applying Fix 4: Vision Context Integration...")
    
    pattern = r"""            # Get sensory status information
            sensory_info = self\._get_sensory_status_information\(\)
            
            # Get memory context for introspection and communication"""
    
    replacement = """            # Get sensory status information
            sensory_info = self._get_sensory_status_information()
            
            # Get vision context for thought process
            vision_context = ""
            if hasattr(self, 'vision_system') and self.vision_system is not None:
                try:
                    vision_data = self.vision_system.get_vision_context_for_thought()
                    if vision_data and vision_data.get("vision_active"):
                        objects_detected = vision_data.get("recent_objects", [])
                        danger_detected = vision_data.get("danger_detected", False)
                        pleasure_detected = vision_data.get("pleasure_detected", False)
                        neucogar_response = vision_data.get("neucogar_response", {})
                        
                        vision_context = f'''
VISION PERCEPTION CONTEXT: You have recently analyzed your visual environment and detected:
- Objects visible: {', '.join(objects_detected) if objects_detected else 'None detected'}
- Danger detected: {'Yes' if danger_detected else 'No'}
- Pleasure detected: {'Yes' if pleasure_detected else 'No'}
- Visual NEUCOGAR response: {neucogar_response}

This visual information should influence your perception and judgment of the current situation.
'''
                    else:
                        vision_context = '''
VISION PERCEPTION CONTEXT: No recent visual analysis available. You are relying on other sensory inputs and memory.
'''
                except Exception as e:
                    self.log(f"Error getting vision context: {e}")
                    vision_context = '''
VISION PERCEPTION CONTEXT: Vision system temporarily unavailable. Using other sensory inputs.
'''
            else:
                vision_context = '''
VISION PERCEPTION CONTEXT: Vision system not available. Using other sensory inputs and memory.
'''
            
            # Get memory context for introspection and communication"""
    
    if re.search(pattern, content, re.MULTILINE | re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        print("✅ Fix 4 applied successfully")
    else:
        print("⚠️  Fix 4 pattern not found - may already be fixed")
    
    return content

def apply_fix_5_vision_context_prompt(content):
    """Add vision context to prompt."""
    print("🔧 Applying Fix 5: Vision Context in Prompt...")
    
    pattern = r"""SENSORY AWARENESS: You have self-awareness of your sensory capabilities and limitations\. You understand what senses you have available and which ones are currently unavailable\. This should influence your responses to sensory-related requests:
\{sensory_info\}

PHYSICAL WORLD OBSERVATION LIMITATIONS: You have important limitations in how you can observe the physical world:"""
    
    replacement = """SENSORY AWARENESS: You have self-awareness of your sensory capabilities and limitations. You understand what senses you have available and which ones are currently unavailable. This should influence your responses to sensory-related requests:
{sensory_info}

{vision_context}

PHYSICAL WORLD OBSERVATION LIMITATIONS: You have important limitations in how you can observe the physical world:"""
    
    if re.search(pattern, content, re.MULTILINE | re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        print("✅ Fix 5 applied successfully")
    else:
        print("⚠️  Fix 5 pattern not found - may already be fixed")
    
    return content

def apply_fix_6_vision_processing_pause(content):
    """Add vision processing pause in cognitive loop."""
    print("🔧 Applying Fix 6: Vision Processing Pause...")
    
    pattern = r"""                # CRITICAL: Pause cognitive processing during API calls
                if self\.cognitive_state\["is_api_call_in_progress"\]:
                    self\.log\("⏸️  API call in progress - pausing cognitive processing\.\.\."\)
                    time\.sleep\(1\.0\)  # Sleep longer during API calls to prevent interference
                    continue"""
    
    replacement = """                # CRITICAL: Pause cognitive processing during API calls
                if self.cognitive_state["is_api_call_in_progress"]:
                    self.log("⏸️  API call in progress - pausing cognitive processing...")
                    time.sleep(1.0)  # Sleep longer during API calls to prevent interference
                    continue
                    
                # CRITICAL: Pause cognitive processing during vision analysis
                if (hasattr(self, 'vision_system') and 
                    self.vision_system is not None and 
                    hasattr(self.vision_system, 'is_vision_processing_active') and
                    self.vision_system.is_vision_processing_active()):
                    self.log("⏸️  Vision analysis in progress - pausing cognitive processing...")
                    time.sleep(0.1)  # Short pause during vision processing
                    continue"""
    
    if re.search(pattern, content, re.MULTILINE | re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        print("✅ Fix 6 applied successfully")
    else:
        print("⚠️  Fix 6 pattern not found - may already be fixed")
    
    return content

def apply_fix_7_vision_analysis_method(content):
    """Add vision analysis trigger method."""
    print("🔧 Applying Fix 7: Vision Analysis Method...")
    
    # Check if method already exists
    if "async def _trigger_vision_analysis_before_thought(self):" in content:
        print("⚠️  Vision analysis method already exists")
        return content
    
    # Find a good place to add the method (before the last method)
    method_pattern = r"""    async def _trigger_vision_analysis_before_thought\(self\):
        \"\"\"
        Trigger vision analysis just before get_carl_thought execution\.
        This ensures vision data is available for the thought process\.
        
        Returns:
            Vision analysis result dict or None if analysis failed/not available
        \"\"\"
        try:
            # Check if vision system is available and enabled
            if \(hasattr\(self, 'vision_system'\) and 
                self\.vision_system is not None and 
                hasattr\(self\.vision_system, 'capture_and_analyze_vision'\) and
                hasattr\(self\.vision_system, 'vision_enabled'\) and
                self\.vision_system\.vision_enabled\):
                
                # Check if vision analysis should be triggered \(respects rate limiting\)
                if hasattr\(self\.vision_system, 'should_trigger_vision_analysis'\):
                    if not self\.vision_system\.should_trigger_vision_analysis\(\):
                        self\.log\("👁️ Vision analysis rate limited - skipping"\)
                        return None
                
                # Execute vision analysis asynchronously to ensure it completes before thought
                self\.log\("👁️ Executing vision analysis before thought process\.\.\."\)
                
                result = await self\.vision_system\.capture_and_analyze_vision\(\)
                
                if result\.get\("success"\):
                    objects_detected = result\["data"\]\.get\("objects", \[\]\)
                    danger_detected = result\["data"\]\.get\("danger_detected", False\)
                    pleasure_detected = result\["data"\]\.get\("pleasure_detected", False\)
                    neucogar = result\["data"\]\.get\("neucogar", \{\}\)
                    analysis = result\["data"\]\.get\("analysis", \{\}\)
                    image_path = result\["data"\]\.get\("image_path", ""\)
                    
                    self\.log\(f"👁️ Vision analysis completed before thought: \{len\(objects_detected\)\} objects detected"\)
                    self\.log\(f"👁️ Danger detected: \{danger_detected\}, Pleasure detected: \{pleasure_detected\}"\)
                    self\.log\(f"👁️ NEUCOGAR response: \{neucogar\}"\)
                    
                    # Update vision context for immediate use in thought process
                    if hasattr\(self\.vision_system, 'get_vision_context_for_thought'\):
                        vision_context = self\.vision_system\.get_vision_context_for_thought\(\)
                        if vision_context and vision_context\.get\("vision_active"\):
                            self\.log\(f"👁️ Vision context updated: \{len\(vision_context\.get\('recent_objects', \[\]\)\)\} recent objects"\)
                    
                    # Return vision result for memory storage
                    return \{
                        "objects_detected": objects_detected,
                        "danger_detected": danger_detected,
                        "danger_reason": result\["data"\]\.get\("danger_reason", ""\),
                        "pleasure_detected": pleasure_detected,
                        "pleasure_reason": result\["data"\]\.get\("pleasure_reason", ""\),
                        "neucogar_response": neucogar,
                        "analysis": analysis,
                        "image_path": image_path,
                        "timestamp": result\["data"\]\.get\("timestamp", ""\),
                        "vision_active": True
                    \}
                else:
                    self\.log\(f"⚠️ Vision analysis failed before thought: \{result\.get\('error', 'Unknown error'\)\}"\)
                    return \{
                        "vision_active": False,
                        "error": result\.get\('error', 'Unknown error'\),
                        "objects_detected": \[\],
                        "danger_detected": False,
                        "pleasure_detected": False,
                        "neucogar_response": \{"dopamine": 0\.5, "serotonin": 0\.5, "norepinephrine": 0\.5, "acetylcholine": 0\.5\}
                    \}
            else:
                self\.log\("👁️ Vision system not available or disabled - skipping vision analysis"\)
                return \{
                    "vision_active": False,
                    "error": "Vision system not available",
                    "objects_detected": \[\],
                    "danger_detected": False,
                    "pleasure_detected": False,
                    "neucogar_response": \{"dopamine": 0\.5, "serotonin": 0\.5, "norepinephrine": 0\.5, "acetylcholine": 0\.5\}
                \}
                    
        except Exception as e:
            self\.log\(f"Error in vision analysis before thought: \{e\}"\)
            # Don't let vision errors prevent thought processing
            return \{
                "vision_active": False,
                "error": str\(e\),
                "objects_detected": \[\],
                "danger_detected": False,
                "pleasure_detected": False,
                "neucogar_response": \{"dopamine": 0\.5, "serotonin": 0\.5, "norepinephrine": 0\.5, "acetylcholine": 0\.5\}
            \}"""
    
    # Add the method before the last method in the class
    # Find the last method and add before it
    lines = content.split('\n')
    last_method_index = -1
    
    for i, line in enumerate(lines):
        if line.strip().startswith('def ') or line.strip().startswith('async def '):
            last_method_index = i
    
    if last_method_index > 0:
        method_to_add = """    async def _trigger_vision_analysis_before_thought(self):
        \"\"\"
        Trigger vision analysis just before get_carl_thought execution.
        This ensures vision data is available for the thought process.
        
        Returns:
            Vision analysis result dict or None if analysis failed/not available
        \"\"\"
        try:
            # Check if vision system is available and enabled
            if (hasattr(self, 'vision_system') and 
                self.vision_system is not None and 
                hasattr(self.vision_system, 'capture_and_analyze_vision') and
                hasattr(self.vision_system, 'vision_enabled') and
                self.vision_system.vision_enabled):
                
                # Check if vision analysis should be triggered (respects rate limiting)
                if hasattr(self.vision_system, 'should_trigger_vision_analysis'):
                    if not self.vision_system.should_trigger_vision_analysis():
                        self.log("👁️ Vision analysis rate limited - skipping")
                        return None
                
                # Execute vision analysis asynchronously to ensure it completes before thought
                self.log("👁️ Executing vision analysis before thought process...")
                
                result = await self.vision_system.capture_and_analyze_vision()
                
                if result.get("success"):
                    objects_detected = result["data"].get("objects", [])
                    danger_detected = result["data"].get("danger_detected", False)
                    pleasure_detected = result["data"].get("pleasure_detected", False)
                    neucogar = result["data"].get("neucogar", {})
                    analysis = result["data"].get("analysis", {})
                    image_path = result["data"].get("image_path", "")
                    
                    self.log(f"👁️ Vision analysis completed before thought: {len(objects_detected)} objects detected")
                    self.log(f"👁️ Danger detected: {danger_detected}, Pleasure detected: {pleasure_detected}")
                    self.log(f"👁️ NEUCOGAR response: {neucogar}")
                    
                    # Update vision context for immediate use in thought process
                    if hasattr(self.vision_system, 'get_vision_context_for_thought'):
                        vision_context = self.vision_system.get_vision_context_for_thought()
                        if vision_context and vision_context.get("vision_active"):
                            self.log(f"👁️ Vision context updated: {len(vision_context.get('recent_objects', []))} recent objects")
                    
                    # Return vision result for memory storage
                    return {
                        "objects_detected": objects_detected,
                        "danger_detected": danger_detected,
                        "danger_reason": result["data"].get("danger_reason", ""),
                        "pleasure_detected": pleasure_detected,
                        "pleasure_reason": result["data"].get("pleasure_reason", ""),
                        "neucogar_response": neucogar,
                        "analysis": analysis,
                        "image_path": image_path,
                        "timestamp": result["data"].get("timestamp", ""),
                        "vision_active": True
                    }
                else:
                    self.log(f"⚠️ Vision analysis failed before thought: {result.get('error', 'Unknown error')}")
                    return {
                        "vision_active": False,
                        "error": result.get('error', 'Unknown error'),
                        "objects_detected": [],
                        "danger_detected": False,
                        "pleasure_detected": False,
                        "neucogar_response": {"dopamine": 0.5, "serotonin": 0.5, "norepinephrine": 0.5, "acetylcholine": 0.5}
                    }
            else:
                self.log("👁️ Vision system not available or disabled - skipping vision analysis")
                return {
                    "vision_active": False,
                    "error": "Vision system not available",
                    "objects_detected": [],
                    "danger_detected": False,
                    "pleasure_detected": False,
                    "neucogar_response": {"dopamine": 0.5, "serotonin": 0.5, "norepinephrine": 0.5, "acetylcholine": 0.5}
                }
                    
        except Exception as e:
            self.log(f"Error in vision analysis before thought: {e}")
            # Don't let vision errors prevent thought processing
            return {
                "vision_active": False,
                "error": str(e),
                "objects_detected": [],
                "danger_detected": False,
                "pleasure_detected": False,
                "neucogar_response": {"dopamine": 0.5, "serotonin": 0.5, "norepinephrine": 0.5, "acetylcholine": 0.5}
            }"""
        
        lines.insert(last_method_index, method_to_add)
        content = '\n'.join(lines)
        print("✅ Fix 7 applied successfully")
    else:
        print("⚠️  Could not find place to add vision analysis method")
    
    return content

def main():
    """Apply all vision system fixes to main.py."""
    print("🔧 VISION SYSTEM FIXES APPLICATION")
    print("=" * 50)
    
    # Create backup
    backup_file = backup_main_py()
    if not backup_file:
        return False
    
    # Read main.py
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading main.py: {e}")
        return False
    
    # Apply fixes
    content = apply_fix_1_vision_initialization(content)
    content = apply_fix_2_owner_concept(content)
    content = apply_fix_3_vision_analysis_trigger(content)
    content = apply_fix_4_vision_context(content)
    content = apply_fix_5_vision_context_prompt(content)
    content = apply_fix_6_vision_processing_pause(content)
    content = apply_fix_7_vision_analysis_method(content)
    
    # Write updated content
    try:
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("\n✅ All fixes applied successfully!")
        print(f"📁 Backup created: {backup_file}")
        
        print("\n📋 NEXT STEPS:")
        print("1. Restart CARL")
        print("2. Test vision analysis during events")
        print("3. Check for vision files in memories/vision")
        print("4. Verify vision data in CARL Memory Explorer")
        
        return True
        
    except Exception as e:
        print(f"❌ Error writing main.py: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
