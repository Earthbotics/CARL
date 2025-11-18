#!/usr/bin/env python3
"""
Exercise Monitoring System

Implements watchdog rules for exercise skills to stop based on:
- Duration limits
- Repetition limits  
- NEUCOGAR fatigue thresholds
"""

import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

class ExerciseType(Enum):
    """Types of exercises."""
    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    ENDURANCE = "endurance"

class StopReason(Enum):
    """Reasons for stopping exercise."""
    DURATION_EXCEEDED = "duration_exceeded"
    REPS_EXCEEDED = "reps_exceeded"
    FATIGUE_THRESHOLD = "fatigue_threshold"
    MANUAL_STOP = "manual_stop"
    SAFETY_LIMIT = "safety_limit"

@dataclass
class ExerciseConfig:
    """Configuration for an exercise."""
    name: str
    exercise_type: ExerciseType
    max_duration_seconds: int = 300  # 5 minutes default
    max_reps: Optional[int] = None
    fatigue_thresholds: Dict[str, float] = None
    safety_limits: Dict[str, float] = None
    cooldown_seconds: int = 60
    description: str = ""
    
    def __post_init__(self):
        if self.fatigue_thresholds is None:
            self.fatigue_thresholds = {
                "norepinephrine": 0.3,  # Stop if norepinephrine drops below 0.3
                "serotonin": 0.4,       # Stop if serotonin drops below 0.4
                "dopamine": 0.2         # Stop if dopamine drops below 0.2
            }
        if self.safety_limits is None:
            self.safety_limits = {
                "heart_rate": 0.8,      # Stop if heart rate exceeds 80% of max
                "energy": 0.1,          # Stop if energy drops below 10%
                "stress": 0.9           # Stop if stress exceeds 90%
            }

@dataclass
class ExerciseSession:
    """Represents an active exercise session."""
    config: ExerciseConfig
    start_time: str
    current_duration: float = 0.0
    current_reps: int = 0
    is_active: bool = True
    stop_reason: Optional[StopReason] = None
    fatigue_levels: Dict[str, float] = None
    safety_metrics: Dict[str, float] = None
    
    def __post_init__(self):
        if self.fatigue_levels is None:
            self.fatigue_levels = {}
        if self.safety_metrics is None:
            self.safety_metrics = {}

@dataclass
class ExerciseStats:
    """Statistics for exercise performance."""
    total_sessions: int = 0
    total_duration: float = 0.0
    total_reps: int = 0
    sessions_completed: int = 0
    sessions_stopped_early: int = 0
    average_duration: float = 0.0
    average_reps: float = 0.0
    last_exercise_time: Optional[str] = None

class ExerciseMonitoringSystem:
    """
    Exercise monitoring system with watchdog rules.
    """
    
    def __init__(self, 
                 neucogar_engine=None,
                 ezrobot=None,
                 stop_callback: Optional[Callable] = None):
        self.logger = logging.getLogger(__name__)
        self.neucogar_engine = neucogar_engine
        self.ezrobot = ezrobot
        self.stop_callback = stop_callback
        
        self.exercise_configs: Dict[str, ExerciseConfig] = {}
        self.active_sessions: Dict[str, ExerciseSession] = {}
        self.exercise_stats: Dict[str, ExerciseStats] = {}
        
        self.monitoring_thread = None
        self.monitoring_active = False
        self.monitoring_interval = 1.0  # Check every second
        
        self._load_exercise_configs()
        self._load_exercise_stats()
        self._register_default_exercises()
    
    def _load_exercise_configs(self):
        """Load exercise configurations from file."""
        try:
            with open("exercise/exercise_configs.json", 'r') as f:
                configs_data = json.load(f)
                for config_data in configs_data:
                    config = ExerciseConfig(
                        name=config_data["name"],
                        exercise_type=ExerciseType(config_data["exercise_type"]),
                        max_duration_seconds=config_data.get("max_duration_seconds", 300),
                        max_reps=config_data.get("max_reps"),
                        fatigue_thresholds=config_data.get("fatigue_thresholds"),
                        safety_limits=config_data.get("safety_limits"),
                        cooldown_seconds=config_data.get("cooldown_seconds", 60),
                        description=config_data.get("description", "")
                    )
                    self.exercise_configs[config.name] = config
            self.logger.info(f"Loaded {len(self.exercise_configs)} exercise configurations")
        except FileNotFoundError:
            self.logger.info("No exercise configs file found, will create defaults")
        except Exception as e:
            self.logger.error(f"Error loading exercise configs: {e}")
    
    def _save_exercise_configs(self):
        """Save exercise configurations to file."""
        try:
            import os
            os.makedirs("exercise", exist_ok=True)
            configs_data = []
            for config in self.exercise_configs.values():
                config_dict = asdict(config)
                config_dict["exercise_type"] = config.exercise_type.value
                configs_data.append(config_dict)
            with open("exercise/exercise_configs.json", 'w') as f:
                json.dump(configs_data, f, indent=2)
            self.logger.info(f"Saved {len(self.exercise_configs)} exercise configurations")
        except Exception as e:
            self.logger.error(f"Error saving exercise configs: {e}")
    
    def _load_exercise_stats(self):
        """Load exercise statistics from file."""
        try:
            with open("exercise/exercise_stats.json", 'r') as f:
                stats_data = json.load(f)
                for exercise_name, stats_dict in stats_data.items():
                    stats = ExerciseStats(
                        total_sessions=stats_dict.get("total_sessions", 0),
                        total_duration=stats_dict.get("total_duration", 0.0),
                        total_reps=stats_dict.get("total_reps", 0),
                        sessions_completed=stats_dict.get("sessions_completed", 0),
                        sessions_stopped_early=stats_dict.get("sessions_stopped_early", 0),
                        average_duration=stats_dict.get("average_duration", 0.0),
                        average_reps=stats_dict.get("average_reps", 0.0),
                        last_exercise_time=stats_dict.get("last_exercise_time")
                    )
                    self.exercise_stats[exercise_name] = stats
        except FileNotFoundError:
            self.logger.info("No exercise stats file found, will create defaults")
        except Exception as e:
            self.logger.error(f"Error loading exercise stats: {e}")
    
    def _save_exercise_stats(self):
        """Save exercise statistics to file."""
        try:
            import os
            os.makedirs("exercise", exist_ok=True)
            stats_data = {}
            for exercise_name, stats in self.exercise_stats.items():
                stats_data[exercise_name] = asdict(stats)
            with open("exercise/exercise_stats.json", 'w') as f:
                json.dump(stats_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving exercise stats: {e}")
    
    def _register_default_exercises(self):
        """Register default exercise configurations."""
        default_exercises = [
            ExerciseConfig(
                name="jump_jack",
                exercise_type=ExerciseType.CARDIO,
                max_duration_seconds=180,  # 3 minutes
                max_reps=50,
                description="Jumping jacks for cardio exercise"
            ),
            ExerciseConfig(
                name="push_up",
                exercise_type=ExerciseType.STRENGTH,
                max_duration_seconds=120,  # 2 minutes
                max_reps=20,
                description="Push-ups for upper body strength"
            ),
            ExerciseConfig(
                name="squat",
                exercise_type=ExerciseType.STRENGTH,
                max_duration_seconds=90,   # 1.5 minutes
                max_reps=30,
                description="Squats for lower body strength"
            ),
            ExerciseConfig(
                name="stretch",
                exercise_type=ExerciseType.FLEXIBILITY,
                max_duration_seconds=300,  # 5 minutes
                description="Stretching exercises for flexibility"
            ),
            ExerciseConfig(
                name="balance_pose",
                exercise_type=ExerciseType.BALANCE,
                max_duration_seconds=60,   # 1 minute
                description="Balance poses for stability"
            )
        ]
        
        for exercise in default_exercises:
            if exercise.name not in self.exercise_configs:
                self.exercise_configs[exercise.name] = exercise
        
        self._save_exercise_configs()
    
    def start_exercise(self, exercise_name: str) -> bool:
        """Start monitoring an exercise session with neurotransmitter tracking."""
        if exercise_name not in self.exercise_configs:
            self.logger.error(f"Unknown exercise: {exercise_name}")
            return False
        
        if exercise_name in self.active_sessions:
            self.logger.warning(f"Exercise {exercise_name} already active")
            return False
        
        config = self.exercise_configs[exercise_name]
        session = ExerciseSession(
            config=config,
            start_time=datetime.now().isoformat()
        )
        
        # Record initial neurotransmitter levels
        if self.neucogar_engine:
            try:
                initial_nt_levels = self._get_fatigue_levels()
                session.fatigue_levels = initial_nt_levels.copy()
                
                # Apply exercise start neurotransmitter changes
                self._apply_exercise_start_effects()
                
                self.logger.info(f"Exercise {exercise_name} started with initial NT levels: {initial_nt_levels}")
            except Exception as e:
                self.logger.error(f"Error recording initial neurotransmitter levels: {e}")
        
        self.active_sessions[exercise_name] = session
        
        # Initialize stats if needed
        if exercise_name not in self.exercise_stats:
            self.exercise_stats[exercise_name] = ExerciseStats()
        
        self.logger.info(f"Started monitoring exercise: {exercise_name}")
        
        # Start monitoring thread if not already running
        if not self.monitoring_active:
            self._start_monitoring()
        
        return True
    
    def stop_exercise(self, exercise_name: str, reason: StopReason = StopReason.MANUAL_STOP) -> bool:
        """Stop monitoring an exercise session."""
        if exercise_name not in self.active_sessions:
            self.logger.warning(f"Exercise {exercise_name} not active")
            return False
        
        session = self.active_sessions[exercise_name]
        session.is_active = False
        session.stop_reason = reason
        
        # Update statistics
        stats = self.exercise_stats[exercise_name]
        stats.total_sessions += 1
        stats.total_duration += session.current_duration
        stats.total_reps += session.current_reps
        stats.last_exercise_time = datetime.now().isoformat()
        
        if reason == StopReason.MANUAL_STOP:
            stats.sessions_completed += 1
        else:
            stats.sessions_stopped_early += 1
        
        # Calculate averages
        if stats.total_sessions > 0:
            stats.average_duration = stats.total_duration / stats.total_sessions
            stats.average_reps = stats.total_reps / stats.total_sessions
        
        # Save stats
        self._save_exercise_stats()
        
        # Remove from active sessions
        del self.active_sessions[exercise_name]
        
        self.logger.info(f"Stopped exercise {exercise_name}: {reason.value}")
        
        # Stop monitoring if no active sessions
        if not self.active_sessions and self.monitoring_active:
            self._stop_monitoring()
        
        return True
    
    def increment_reps(self, exercise_name: str, count: int = 1) -> bool:
        """Increment repetition count for an exercise."""
        if exercise_name not in self.active_sessions:
            return False
        
        session = self.active_sessions[exercise_name]
        session.current_reps += count
        
        self.logger.info(f"Incremented reps for {exercise_name}: {session.current_reps}")
        return True
    
    def _start_monitoring(self):
        """Start the monitoring thread."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Exercise monitoring started")
    
    def _stop_monitoring(self):
        """Stop the monitoring thread."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
        self.logger.info("Exercise monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                current_time = time.time()
                
                # Check each active session
                for exercise_name, session in list(self.active_sessions.items()):
                    if not session.is_active:
                        continue
                    
                    # Update duration
                    start_time = datetime.fromisoformat(session.start_time)
                    session.current_duration = (datetime.now() - start_time).total_seconds()
                    
                    # Apply exercise duration effects (serotonin decrease over time)
                    self._apply_exercise_duration_effects(session.current_duration)
                    
                    # Check stop conditions including neurotransmitter-based auto-stop
                    stop_reason = self._check_stop_conditions(session)
                    if stop_reason:
                        self._handle_exercise_stop(exercise_name, stop_reason)
                
                # Sleep for monitoring interval
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _check_stop_conditions(self, session: ExerciseSession) -> Optional[StopReason]:
        """Check if exercise should be stopped."""
        config = session.config
        
        # Check duration limit
        if session.current_duration >= config.max_duration_seconds:
            return StopReason.DURATION_EXCEEDED
        
        # Check repetition limit
        if config.max_reps and session.current_reps >= config.max_reps:
            return StopReason.REPS_EXCEEDED
        
        # Check neurotransmitter-based auto-stop conditions
        if self.neucogar_engine:
            try:
                fatigue_levels = self._get_fatigue_levels()
                session.fatigue_levels = fatigue_levels
                
                # Check serotonin threshold (auto-stop if serotonin < 0.3)
                serotonin_level = fatigue_levels.get("serotonin", 0.5)
                if serotonin_level < 0.3:
                    self.logger.info(f"Serotonin threshold reached: {serotonin_level:.3f} < 0.3")
                    return StopReason.FATIGUE_THRESHOLD
                
                # Check dopamine maximum (auto-stop if dopamine > 0.8)
                dopamine_level = fatigue_levels.get("dopamine", 0.5)
                if dopamine_level > 0.8:
                    self.logger.info(f"Dopamine maximum reached: {dopamine_level:.3f} > 0.8")
                    return StopReason.FATIGUE_THRESHOLD
                
                # Check norepinephrine maximum (auto-stop if norepinephrine > 0.8)
                norepinephrine_level = fatigue_levels.get("norepinephrine", 0.5)
                if norepinephrine_level > 0.8:
                    self.logger.info(f"Norepinephrine maximum reached: {norepinephrine_level:.3f} > 0.8")
                    return StopReason.FATIGUE_THRESHOLD
                
                # Check legacy fatigue thresholds
                for nt, threshold in config.fatigue_thresholds.items():
                    current_level = fatigue_levels.get(nt, 0.5)
                    if current_level <= threshold:
                        self.logger.info(f"Legacy fatigue threshold reached: {nt} = {current_level:.3f} <= {threshold}")
                        return StopReason.FATIGUE_THRESHOLD
                
                # Check safety limits
                safety_metrics = self._get_safety_metrics()
                session.safety_metrics = safety_metrics
                
                for metric, limit in config.safety_limits.items():
                    current_value = safety_metrics.get(metric, 0.5)
                    if current_value >= limit:
                        self.logger.info(f"Safety limit reached: {metric} = {current_value:.3f} >= {limit}")
                        return StopReason.SAFETY_LIMIT
                        
            except Exception as e:
                self.logger.error(f"Error checking fatigue/safety levels: {e}")
        
        return None
    
    def _apply_exercise_start_effects(self):
        """Apply neurotransmitter changes when exercise starts."""
        if not self.neucogar_engine:
            return
        
        try:
            # Get current neurotransmitter levels
            current_nt = self._get_fatigue_levels()
            
            # Apply exercise start effects:
            # - Dopamine +0.2 (reward/motivation boost)
            # - Norepinephrine +0.1 (arousal/alertness boost)
            # - Serotonin starts decreasing over time
            
            new_dopamine = min(1.0, current_nt["dopamine"] + 0.2)
            new_norepinephrine = min(1.0, current_nt["norepinephrine"] + 0.1)
            
            # Update NEUCOGAR engine with new levels
            self.neucogar_engine.update_neurotransmitter_levels({
                "dopamine": new_dopamine,
                "norepinephrine": new_norepinephrine
            })
            
            self.logger.info(f"Applied exercise start effects: DA={new_dopamine:.3f}, NE={new_norepinephrine:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error applying exercise start effects: {e}")
    
    def _apply_exercise_duration_effects(self, duration_seconds: float):
        """Apply neurotransmitter changes based on exercise duration."""
        if not self.neucogar_engine:
            return
        
        try:
            # Get current neurotransmitter levels
            current_nt = self._get_fatigue_levels()
            
            # Serotonin decreases over time during exercise
            # Decrease rate: 0.1 per minute (0.00167 per second)
            serotonin_decrease = (duration_seconds / 60.0) * 0.1
            new_serotonin = max(0.0, current_nt["serotonin"] - serotonin_decrease)
            
            # Update NEUCOGAR engine with new serotonin level
            self.neucogar_engine.update_neurotransmitter_levels({
                "serotonin": new_serotonin
            })
            
            self.logger.info(f"Applied exercise duration effects: 5-HT={new_serotonin:.3f} (duration: {duration_seconds:.1f}s)")
            
        except Exception as e:
            self.logger.error(f"Error applying exercise duration effects: {e}")
    
    def _get_fatigue_levels(self) -> Dict[str, float]:
        """Get current fatigue levels from NEUCOGAR engine."""
        if not self.neucogar_engine:
            return {"dopamine": 0.5, "serotonin": 0.5, "norepinephrine": 0.5}
        
        try:
            # Get neurotransmitter levels from NEUCOGAR
            nt_state = self.neucogar_engine.get_neurotransmitter_state()
            return {
                "dopamine": nt_state.get("dopamine", 0.5),
                "serotonin": nt_state.get("serotonin", 0.5),
                "norepinephrine": nt_state.get("norepinephrine", 0.5)
            }
        except Exception as e:
            self.logger.error(f"Error getting fatigue levels: {e}")
            return {"dopamine": 0.5, "serotonin": 0.5, "norepinephrine": 0.5}
    
    def _get_safety_metrics(self) -> Dict[str, float]:
        """Get current safety metrics."""
        # This would integrate with actual sensors in a real implementation
        # For now, return simulated values
        return {
            "heart_rate": 0.6,  # 60% of max heart rate
            "energy": 0.7,      # 70% energy level
            "stress": 0.3       # 30% stress level
        }
    
    def _handle_exercise_stop(self, exercise_name: str, reason: StopReason):
        """Handle automatic exercise stop."""
        self.logger.info(f"Auto-stopping exercise {exercise_name}: {reason.value}")
        
        # Execute stop action
        if self.stop_callback:
            try:
                self.stop_callback(exercise_name, reason)
            except Exception as e:
                self.logger.error(f"Error in stop callback: {e}")
        
        # Stop the exercise
        self.stop_exercise(exercise_name, reason)

    def check_voice_stop_command(self, user_input: str) -> Optional[str]:
        """
        Check if user input contains a stop command for any active exercise.
        
        Args:
            user_input: User's voice input
            
        Returns:
            Exercise name if stop command detected, None otherwise
        """
        if not self.active_sessions:
            return None
        
        user_input_lower = user_input.lower().strip()
        
        # Stop command patterns
        stop_commands = [
            "stop", "that's enough", "sit down", "enough", "quit", "end",
            "finish", "done", "halt", "cease", "terminate", "no more"
        ]
        
        # Check if any stop command is in the user input
        for command in stop_commands:
            if command in user_input_lower:
                # Return the first active exercise name
                active_exercises = list(self.active_sessions.keys())
                if active_exercises:
                    exercise_name = active_exercises[0]
                    self.logger.info(f"Voice stop command detected: '{user_input}' -> stopping {exercise_name}")
                    return exercise_name
        
        return None

    def stop_exercise_by_voice(self, user_input: str) -> bool:
        """
        Stop exercise based on voice command.
        
        Args:
            user_input: User's voice input
            
        Returns:
            True if exercise was stopped, False otherwise
        """
        exercise_name = self.check_voice_stop_command(user_input)
        if exercise_name:
            return self.stop_exercise(exercise_name, StopReason.MANUAL_STOP)
        return False

    def get_active_exercises(self) -> List[str]:
        """Get list of currently active exercises."""
        return list(self.active_sessions.keys())

    def is_exercise_active(self, exercise_name: str) -> bool:
        """Check if a specific exercise is currently active."""
        return exercise_name in self.active_sessions and self.active_sessions[exercise_name].is_active
    
    def get_exercise_status(self, exercise_name: str) -> Optional[Dict[str, Any]]:
        """Get status of an exercise session."""
        if exercise_name not in self.active_sessions:
            return None
        
        session = self.active_sessions[exercise_name]
        return {
            "name": exercise_name,
            "start_time": session.start_time,
            "current_duration": session.current_duration,
            "current_reps": session.current_reps,
            "max_duration": session.config.max_duration_seconds,
            "max_reps": session.config.max_reps,
            "fatigue_levels": session.fatigue_levels,
            "safety_metrics": session.safety_metrics,
            "is_active": session.is_active
        }
    
    def get_exercise_stats(self, exercise_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for an exercise."""
        if exercise_name not in self.exercise_stats:
            return None
        
        stats = self.exercise_stats[exercise_name]
        return asdict(stats)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all exercises."""
        return {
            name: asdict(stats) for name, stats in self.exercise_stats.items()
        }

# Global instance
exercise_monitoring_system = ExerciseMonitoringSystem()
