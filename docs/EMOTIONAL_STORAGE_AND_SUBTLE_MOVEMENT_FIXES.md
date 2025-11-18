# Emotional Storage and Subtle Movement Fixes

## Overview
This document summarizes the fixes implemented to address three key issues:
1. Missing emotional values in event JSON files
2. Subtle movement interference with skill execution
3. Implementation of "yawn" script and "Waiting Fidget" action

## Issues Identified

### 1. Missing Emotional Values in Event JSON Files
**Problem**: Event JSON files were showing all emotion values as 0.0, despite CARL having active NEUCOGAR emotional states.

**Root Cause**: 
- The event export system was using the legacy emotional state (`self.emotional_state["current_emotions"]`) which was being reset to zeros
- The NEUCOGAR emotional state was not being properly mapped to the legacy format
- The export method was not prioritizing the NEUCOGAR emotional state

**Solution Implemented**:
- Updated `event.py` export_to_json method to include NEUCOGAR emotional state as primary data
- Enhanced `_update_legacy_emotional_state` method with proper emotion mapping
- Added emotion mapping from NEUCOGAR emotions to legacy emotions:
  - `joy` → `joy`
  - `happiness` → `joy`
  - `sadness` → `sadness`
  - `anger` → `anger`
  - `fear` → `fear`
  - `surprise` → `surprise`
  - `disgust` → `disgust`
  - `curiosity` → `surprise`
  - `neutral` → `joy` (low intensity for positive baseline)

### 2. Subtle Movement Interference with Skill Execution
**Problem**: Subtle movements (like head_bob) could interrupt longer skill executions like somersault.

**Root Cause**: 
- Subtle movement system ran independently without checking if skills were being executed
- No coordination between skill execution and subtle movements

**Solution Implemented**:
- Added `is_executing_skill()` method to ActionSystem class
- Updated subtle movement system to check if skills are being executed
- Added logic to skip subtle movements when skills are active
- Method checks both `is_executing` flag and `pending_actions` set

### 3. Missing "yawn" Script and "Waiting Fidget" Action
**Problem**: The subtle movement system was using `head_yes` as fallback for all movements instead of specific scripts.

**Solution Implemented**:
- Updated subtle movement system to use specific scripts:
  - `yawn` movement now uses `send_auto_position("yawn")` (case-sensitive)
  - `fidget` movement now uses `send_auto_position("Waiting Fidget")` (case-sensitive)
- Maintained fallback to `head_yes` for other movements

## Technical Implementation Details

### Event Export Changes (`event.py`)
```python
# Updated export_to_json method to include NEUCOGAR emotional state
event_data = {
    "WHO": self.WHO,
    "WHAT": self.WHAT,
    # ... other fields ...
    "neucogar_emotional_state": self.neucogar_emotional_state,
    "emotions": self.emotional_state["current_emotions"],  # Legacy compatibility
    "neurotransmitters": self.emotional_state["neurotransmitters"]
}
```

### Subtle Movement System Changes (`main.py`)
```python
def _execute_subtle_body_movement(self):
    # Check if CARL is currently executing a skill
    if hasattr(self, 'action_system') and self.action_system.is_executing_skill():
        # Skip subtle movements if a skill is being executed
        return
    
    # ... movement execution logic ...
    elif selected_movement == "yawn":
        # Use the "yawn" script (case-sensitive)
        self.action_system.ez_robot.send_auto_position("yawn")
    elif selected_movement == "fidget":
        # Use "Waiting Fidget" action (case-sensitive)
        self.action_system.ez_robot.send_auto_position("Waiting Fidget")
```

### Action System Enhancement (`action_system.py`)
```python
def is_executing_skill(self) -> bool:
    """
    Check if CARL is currently executing a skill.
    This prevents subtle movements from interfering with skill execution.
    """
    return self.is_executing or len(self.pending_actions) > 0
```

## Expected Results

### 1. Emotional Values in Event JSON Files
- Event JSON files will now contain proper emotional values from NEUCOGAR system
- Legacy emotion fields will be populated with mapped values
- Both NEUCOGAR and legacy emotional data will be preserved

### 2. Skill Execution Interference Prevention
- Subtle movements will be skipped when skills are being executed
- Longer skills like somersault will complete without interruption
- Better coordination between different movement systems

### 3. Enhanced Subtle Movements
- `yawn` movement will use the actual "yawn" script
- `fidget` movement will use the "Waiting Fidget" action
- More realistic and varied subtle movements

## Testing Recommendations

1. **Test Emotional Storage**: Run CARL and check that event JSON files contain proper emotional values
2. **Test Skill Interference**: Execute a somersault and verify no subtle movements interrupt it
3. **Test Subtle Movements**: Observe that yawn and fidget movements use the correct scripts

## Files Modified
- `event.py`: Updated export and emotional state mapping
- `main.py`: Enhanced subtle movement system
- `action_system.py`: Added skill execution checking method
- `EMOTIONAL_STORAGE_AND_SUBTLE_MOVEMENT_FIXES.md`: This summary document 