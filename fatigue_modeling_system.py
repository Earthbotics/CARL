#!/usr/bin/env python3
"""
Fatigue Modeling System
=======================

This module implements a fatigue modeling system that tracks energy depletion
during physical activities and affects neurotransmitter levels. This addresses
the issue where CARL didn't show fatigue effects during prolonged dancing.

The system models:
- Physical energy depletion over time
- Cognitive fatigue from sustained activities
- Recovery patterns during rest
- Effects on neurotransmitter levels
- Individual variation in fatigue response
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ActivityState:
    """Represents the current state of physical activity."""
    activity_type: str
    intensity: float  # 0.0 to 1.0
    start_time: datetime
    duration: float  # seconds
    energy_expended: float  # 0.0 to 1.0
    fatigue_level: float  # 0.0 to 1.0

@dataclass
class FatigueEffects:
    """Represents the effects of fatigue on neurotransmitters."""
    dopamine: float      # Reduced motivation
    serotonin: float     # Reduced mood
    noradrenaline: float # Reduced alertness
    acetylcholine: float # Reduced focus
    gaba: float         # Increased (for rest/sleep)
    glutamate: float    # Reduced (for cognitive function)

class FatigueModelingSystem:
    """
    System for modeling fatigue and its effects on CARL's cognitive and emotional state.
    """
    
    def __init__(self):
        """Initialize the fatigue modeling system."""
        
        # Energy and fatigue parameters
        self.max_energy = 1.0
        self.current_energy = 1.0
        self.fatigue_level = 0.0
        
        # Activity tracking
        self.current_activity = None
        self.activity_history = []
        
        # Fatigue rates (per second)
        self.fatigue_rates = {
            "dancing": 0.015,
            "jumping_jacks": 0.025,
            "walking": 0.005,
            "sitting": 0.001,
            "standing": 0.003,
            "exercise": 0.020,
            "conversation": 0.002,
            "thinking": 0.004
        }
        
        # Recovery rates (per second)
        self.recovery_rates = {
            "rest": 0.008,
            "sleep": 0.015,
            "sitting": 0.003,
            "light_activity": 0.001
        }
        
        # Neurotransmitter fatigue effects
        self.neurotransmitter_fatigue_effects = {
            "dopamine": {
                "fatigue_factor": -0.4,      # Reduced motivation
                "recovery_factor": 0.2       # Recovery rate
            },
            "serotonin": {
                "fatigue_factor": -0.3,      # Reduced mood
                "recovery_factor": 0.15      # Recovery rate
            },
            "noradrenaline": {
                "fatigue_factor": -0.5,      # Reduced alertness
                "recovery_factor": 0.25      # Recovery rate
            },
            "acetylcholine": {
                "fatigue_factor": -0.35,     # Reduced focus
                "recovery_factor": 0.18      # Recovery rate
            },
            "gaba": {
                "fatigue_factor": 0.2,       # Increased (rest/sleep)
                "recovery_factor": -0.1      # Recovery rate
            },
            "glutamate": {
                "fatigue_factor": -0.3,      # Reduced cognitive function
                "recovery_factor": 0.15      # Recovery rate
            }
        }
        
        # Session tracking
        self.session_start_time = datetime.now()
        self.fatigue_events = []
    
    def start_activity(self, activity_type: str, intensity: float = 1.0) -> Dict:
        """
        Start tracking a new physical activity.
        
        Args:
            activity_type: Type of activity (dancing, jumping_jacks, etc.)
            intensity: Activity intensity (0.0 to 1.0)
            
        Returns:
            Dict containing activity start information
        """
        # Stop current activity if any
        if self.current_activity:
            self.stop_activity()
        
        # Create new activity state
        self.current_activity = ActivityState(
            activity_type=activity_type,
            intensity=intensity,
            start_time=datetime.now(),
            duration=0.0,
            energy_expended=0.0,
            fatigue_level=0.0
        )
        
        # Log activity start
        event = {
            "timestamp": datetime.now(),
            "event_type": "activity_start",
            "activity_type": activity_type,
            "intensity": intensity,
            "current_energy": self.current_energy,
            "current_fatigue": self.fatigue_level
        }
        self.fatigue_events.append(event)
        
        return {
            "activity_started": activity_type,
            "intensity": intensity,
            "current_energy": self.current_energy,
            "current_fatigue": self.fatigue_level
        }
    
    def stop_activity(self) -> Dict:
        """
        Stop the current activity and calculate fatigue effects.
        
        Returns:
            Dict containing activity summary and fatigue effects
        """
        if not self.current_activity:
            return {"error": "No activity currently running"}
        
        # Calculate final activity metrics
        end_time = datetime.now()
        duration = (end_time - self.current_activity.start_time).total_seconds()
        
        # Update activity state
        self.current_activity.duration = duration
        self.current_activity.energy_expended = self._calculate_energy_expended(
            self.current_activity.activity_type,
            duration,
            self.current_activity.intensity
        )
        self.current_activity.fatigue_level = self._calculate_fatigue_level(
            self.current_activity.activity_type,
            duration,
            self.current_activity.intensity
        )
        
        # Add to activity history
        self.activity_history.append(self.current_activity)
        
        # Log activity end
        event = {
            "timestamp": datetime.now(),
            "event_type": "activity_end",
            "activity_type": self.current_activity.activity_type,
            "duration": duration,
            "energy_expended": self.current_activity.energy_expended,
            "fatigue_generated": self.current_activity.fatigue_level,
            "final_energy": self.current_energy,
            "final_fatigue": self.fatigue_level
        }
        self.fatigue_events.append(event)
        
        # Clear current activity
        activity_summary = {
            "activity_type": self.current_activity.activity_type,
            "duration": duration,
            "energy_expended": self.current_activity.energy_expended,
            "fatigue_generated": self.current_activity.fatigue_level
        }
        
        self.current_activity = None
        
        return activity_summary
    
    def update_fatigue(self) -> Dict:
        """
        Update fatigue levels based on current activity or recovery.
        
        Returns:
            Dict containing current fatigue state
        """
        current_time = datetime.now()
        
        if self.current_activity:
            # Update activity duration
            duration = (current_time - self.current_activity.start_time).total_seconds()
            self.current_activity.duration = duration
            
            # Calculate fatigue from current activity
            fatigue_rate = self.fatigue_rates.get(self.current_activity.activity_type, 0.01)
            fatigue_increase = fatigue_rate * duration * self.current_activity.intensity
            
            # Update fatigue level
            self.fatigue_level = min(1.0, self.fatigue_level + fatigue_increase)
            
            # Calculate energy loss
            energy_loss = fatigue_increase * 0.8  # Energy loss proportional to fatigue
            self.current_energy = max(0.1, self.current_energy - energy_loss)
            
        else:
            # Recovery mode - reduce fatigue and increase energy
            recovery_rate = self.recovery_rates.get("rest", 0.008)
            fatigue_decrease = recovery_rate * 0.1  # Slower recovery
            energy_gain = recovery_rate * 0.05
            
            self.fatigue_level = max(0.0, self.fatigue_level - fatigue_decrease)
            self.current_energy = min(self.max_energy, self.current_energy + energy_gain)
        
        return {
            "current_energy": self.current_energy,
            "current_fatigue": self.fatigue_level,
            "activity_type": self.current_activity.activity_type if self.current_activity else "rest",
            "activity_duration": self.current_activity.duration if self.current_activity else 0.0
        }
    
    def get_fatigue_effects_on_neurotransmitters(self) -> FatigueEffects:
        """
        Calculate the effects of current fatigue on neurotransmitter levels.
        
        Returns:
            FatigueEffects object with neurotransmitter adjustments
        """
        # Calculate fatigue effects on each neurotransmitter
        effects = {}
        
        for nt, params in self.neurotransmitter_fatigue_effects.items():
            fatigue_effect = params["fatigue_factor"] * self.fatigue_level
            recovery_effect = params["recovery_factor"] * (1.0 - self.fatigue_level)
            
            # Net effect is fatigue + recovery
            net_effect = fatigue_effect + recovery_effect
            
            # Apply energy level modifier
            energy_modifier = self.current_energy * 0.5
            final_effect = net_effect * (1.0 + energy_modifier)
            
            effects[nt] = final_effect
        
        return FatigueEffects(**effects)
    
    def get_fatigue_summary(self) -> Dict:
        """
        Get a comprehensive summary of current fatigue state.
        
        Returns:
            Dict containing fatigue summary information
        """
        current_activity = None
        if self.current_activity:
            current_activity = {
                "type": self.current_activity.activity_type,
                "intensity": self.current_activity.intensity,
                "duration": self.current_activity.duration,
                "energy_expended": self.current_activity.energy_expended
            }
        
        # Calculate session statistics
        session_duration = (datetime.now() - self.session_start_time).total_seconds()
        total_activities = len(self.activity_history)
        total_energy_expended = sum(activity.energy_expended for activity in self.activity_history)
        
        return {
            "current_energy": self.current_energy,
            "current_fatigue": self.fatigue_level,
            "current_activity": current_activity,
            "session_duration": session_duration,
            "total_activities": total_activities,
            "total_energy_expended": total_energy_expended,
            "fatigue_events": len(self.fatigue_events),
            "neurotransmitter_effects": self.get_fatigue_effects_on_neurotransmitters().__dict__
        }
    
    def _calculate_energy_expended(self, activity_type: str, duration: float, intensity: float) -> float:
        """Calculate energy expended for an activity."""
        base_rate = self.fatigue_rates.get(activity_type, 0.01)
        energy_expended = base_rate * duration * intensity
        return min(1.0, energy_expended)
    
    def _calculate_fatigue_level(self, activity_type: str, duration: float, intensity: float) -> float:
        """Calculate fatigue level generated by an activity."""
        base_rate = self.fatigue_rates.get(activity_type, 0.01)
        fatigue_generated = base_rate * duration * intensity * 1.2  # Fatigue accumulates faster than energy loss
        return min(1.0, fatigue_generated)
    
    def get_fatigue_warnings(self) -> List[str]:
        """
        Get warnings based on current fatigue state.
        
        Returns:
            List of warning messages
        """
        warnings = []
        
        if self.fatigue_level > 0.8:
            warnings.append("High fatigue level detected - consider rest")
        
        if self.current_energy < 0.2:
            warnings.append("Low energy level - performance may be affected")
        
        if self.current_activity and self.current_activity.duration > 300:  # 5 minutes
            warnings.append("Prolonged activity detected - fatigue building up")
        
        return warnings
    
    def reset_fatigue(self):
        """Reset fatigue levels (for testing or new session)."""
        self.current_energy = self.max_energy
        self.fatigue_level = 0.0
        self.current_activity = None
        self.activity_history = []
        self.fatigue_events = []

# Example usage and testing
if __name__ == "__main__":
    # Test the fatigue modeling system
    fms = FatigueModelingSystem()
    
    print("Starting fatigue modeling test...")
    
    # Start dancing activity
    print("\n1. Starting dance activity...")
    fms.start_activity("dancing", intensity=0.8)
    
    # Simulate 2 minutes of dancing
    import time
    for i in range(12):  # 12 * 10 seconds = 2 minutes
        time.sleep(0.1)  # Simulate time passing
        fms.update_fatigue()
        if i % 3 == 0:  # Every 30 seconds
            summary = fms.get_fatigue_summary()
            print(f"   Energy: {summary['current_energy']:.2f}, Fatigue: {summary['current_fatigue']:.2f}")
    
    # Stop dancing
    print("\n2. Stopping dance activity...")
    activity_summary = fms.stop_activity()
    print(f"   Activity summary: {activity_summary}")
    
    # Check fatigue effects
    print("\n3. Checking fatigue effects on neurotransmitters...")
    effects = fms.get_fatigue_effects_on_neurotransmitters()
    print(f"   Dopamine effect: {effects.dopamine:.3f}")
    print(f"   Serotonin effect: {effects.serotonin:.3f}")
    print(f"   Noradrenaline effect: {effects.noradrenaline:.3f}")
    
    # Simulate recovery
    print("\n4. Simulating recovery...")
    for i in range(10):  # 10 recovery cycles
        time.sleep(0.1)
        fms.update_fatigue()
        if i % 2 == 0:
            summary = fms.get_fatigue_summary()
            print(f"   Energy: {summary['current_energy']:.2f}, Fatigue: {summary['current_fatigue']:.2f}")
    
    print("\nFatigue modeling test completed!")
