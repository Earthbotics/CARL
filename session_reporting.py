#!/usr/bin/env python3
"""
Session Reporting System
========================

Generates comprehensive end-of-test reports including:
- Intents and emotions with true averages
- Neurotransmitter trends
- Inner-dialogue turns
- Vision events received
- Humor detections
- Imagination artifacts
- Errors and warnings
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

@dataclass
class SessionReport:
    """Complete session report data."""
    session_id: str
    start_time: str
    end_time: str
    duration_seconds: float
    
    # Cognitive metrics
    intents: List[Dict[str, Any]]
    emotions: Dict[str, Dict[str, float]]  # emotion -> {current, avg, min, max}
    neurotransmitter_trends: Dict[str, List[float]]
    
    # Interaction metrics
    inner_dialogue_turns: int
    vision_events_received: int
    humor_detections: int
    laughter_triggers: int
    imagination_artifacts: int
    
    # System metrics
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    
    # Memory metrics
    memories_created: int
    memories_retrieved: int
    
    # Skill metrics
    skills_executed: List[str]
    skill_success_rate: float
    
    # Purpose-driven behavior metrics
    needs_selected: int
    goals_activated: int
    tasks_completed: int
    purpose_driven_events: List[Dict[str, Any]]

class SessionReporter:
    """
    Session reporting and analysis system.
    """
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize the session reporter."""
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Session tracking
        self.session_start_time = None
        self.session_data = {
            "intents": [],
            "emotions": [],
            "neurotransmitters": [],
            "vision_events": [],
            "humor_events": [],
            "imagination_artifacts": [],
            "errors": [],
            "warnings": [],
            "inner_dialogue_turns": 0,
            "laughter_triggers": 0,
            "memories_created": 0,
            "memories_retrieved": 0,
            "skills_executed": [],
            "skill_failures": 0,
            "needs_selected": 0,
            "goals_activated": 0,
            "tasks_completed": 0,
            "purpose_driven_events": []
        }
    
    def start_session(self, session_id: Optional[str] = None):
        """Start tracking a new session."""
        self.session_start_time = datetime.now()
        self.session_id = session_id or f"session_{int(self.session_start_time.timestamp())}"
        
        # Reset session data
        for key in self.session_data:
            if isinstance(self.session_data[key], list):
                self.session_data[key] = []
            elif isinstance(self.session_data[key], int):
                self.session_data[key] = 0
        
        self.logger.info(f"📊 Session started: {self.session_id}")
    
    def record_intent(self, intent: str, confidence: float, context: Optional[Dict[str, Any]] = None):
        """Record an intent detection."""
        self.session_data["intents"].append({
            "timestamp": datetime.now().isoformat(),
            "intent": intent,
            "confidence": confidence,
            "context": context or {}
        })
    
    def record_emotion(self, emotion: str, intensity: float):
        """Record an emotion with intensity."""
        self.session_data["emotions"].append({
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion,
            "intensity": intensity
        })
    
    def record_neurotransmitters(self, nt_levels: Dict[str, float]):
        """Record neurotransmitter levels."""
        self.session_data["neurotransmitters"].append({
            "timestamp": datetime.now().isoformat(),
            "levels": nt_levels.copy()
        })
    
    def record_vision_event(self, event: Dict[str, Any]):
        """Record a vision event."""
        self.session_data["vision_events"].append({
            "timestamp": datetime.now().isoformat(),
            "event": event
        })
    
    def record_humor_event(self, event: Dict[str, Any]):
        """Record a humor detection event."""
        self.session_data["humor_events"].append({
            "timestamp": datetime.now().isoformat(),
            "event": event
        })
        if event.get("trigger_laughter", False):
            self.session_data["laughter_triggers"] += 1
    
    def record_imagination_artifact(self, artifact: Dict[str, Any]):
        """Record an imagination artifact."""
        self.session_data["imagination_artifacts"].append({
            "timestamp": datetime.now().isoformat(),
            "artifact": artifact
        })
    
    def record_inner_dialogue_turn(self):
        """Record an inner dialogue turn."""
        self.session_data["inner_dialogue_turns"] += 1
    
    def record_memory_created(self):
        """Record memory creation."""
        self.session_data["memories_created"] += 1
    
    def record_memory_retrieved(self):
        """Record memory retrieval."""
        self.session_data["memories_retrieved"] += 1
    
    def record_skill_execution(self, skill_name: str, success: bool):
        """Record skill execution."""
        self.session_data["skills_executed"].append({
            "timestamp": datetime.now().isoformat(),
            "skill": skill_name,
            "success": success
        })
        if not success:
            self.session_data["skill_failures"] += 1
    
    def record_error(self, error: str, context: Optional[Dict[str, Any]] = None):
        """Record an error."""
        self.session_data["errors"].append({
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "context": context or {}
        })
        self.logger.error(f"Session error: {error}")
    
    def record_warning(self, warning: str, context: Optional[Dict[str, Any]] = None):
        """Record a warning."""
        self.session_data["warnings"].append({
            "timestamp": datetime.now().isoformat(),
            "warning": warning,
            "context": context or {}
        })
        self.logger.warning(f"Session warning: {warning}")
    
    def record_purpose_driven_event(self, event_type: str, details: Dict[str, Any]):
        """Record a purpose-driven behavior event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details
        }
        self.session_data["purpose_driven_events"].append(event)
        
        # Update counters based on event type
        if event_type == "need_selected":
            self.session_data["needs_selected"] += 1
        elif event_type == "goal_activated":
            self.session_data["goals_activated"] += 1
        elif event_type == "task_completed":
            self.session_data["tasks_completed"] += 1
        
        self.logger.info(f"Purpose-driven event recorded: {event_type}")
    
    def record_need_selection(self, need: str, priority: float, status: str):
        """Record a need selection event."""
        self.record_purpose_driven_event("need_selected", {
            "need": need,
            "priority": priority,
            "status": status
        })
    
    def record_goal_activation(self, goal: str, linked_need: str, tasks: List[str]):
        """Record a goal activation event."""
        self.record_purpose_driven_event("goal_activated", {
            "goal": goal,
            "linked_need": linked_need,
            "tasks": tasks
        })
    
    def record_task_completion(self, task: str, success: bool, details: str = ""):
        """Record a task completion event."""
        self.record_purpose_driven_event("task_completed", {
            "task": task,
            "success": success,
            "details": details
        })
    
    def generate_report(self, neucogar_engine=None, humor_system=None, 
                       imagination_system=None, memory_system=None) -> SessionReport:
        """
        Generate comprehensive session report.
        
        Args:
            neucogar_engine: NEUCOGAR engine for emotion analysis
            humor_system: Humor system for statistics
            imagination_system: Imagination system for artifacts
            memory_system: Memory system for statistics
            
        Returns:
            SessionReport: Complete session report
        """
        if not self.session_start_time:
            raise ValueError("No session started")
        
        end_time = datetime.now()
        duration = (end_time - self.session_start_time).total_seconds()
        
        # Calculate emotion statistics
        emotion_stats = self._calculate_emotion_statistics()
        
        # Calculate neurotransmitter trends
        nt_trends = self._calculate_neurotransmitter_trends()
        
        # Calculate skill success rate
        total_skills = len(self.session_data["skills_executed"])
        successful_skills = sum(1 for skill in self.session_data["skills_executed"] if skill["success"])
        skill_success_rate = successful_skills / total_skills if total_skills > 0 else 0.0
        
        # Get system-specific statistics
        humor_stats = humor_system.get_humor_stats() if humor_system else {}
        imagination_stats = self._get_imagination_statistics(imagination_system)
        memory_stats = self._get_memory_statistics(memory_system)
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(duration)
        
        report = SessionReport(
            session_id=self.session_id,
            start_time=self.session_start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration_seconds=duration,
            
            # Cognitive metrics
            intents=self.session_data["intents"],
            emotions=emotion_stats,
            neurotransmitter_trends=nt_trends,
            
            # Interaction metrics
            inner_dialogue_turns=self.session_data["inner_dialogue_turns"],
            vision_events_received=len(self.session_data["vision_events"]),
            humor_detections=len(self.session_data["humor_events"]),
            laughter_triggers=self.session_data["laughter_triggers"],
            imagination_artifacts=len(self.session_data["imagination_artifacts"]),
            
            # System metrics
            errors=self.session_data["errors"],
            warnings=self.session_data["warnings"],
            performance_metrics=performance_metrics,
            
            # Memory metrics
            memories_created=self.session_data["memories_created"],
            memories_retrieved=self.session_data["memories_retrieved"],
            
            # Skill metrics
            skills_executed=[skill["skill"] for skill in self.session_data["skills_executed"]],
            skill_success_rate=skill_success_rate,
            
            # Purpose-driven behavior metrics
            needs_selected=self.session_data["needs_selected"],
            goals_activated=self.session_data["goals_activated"],
            tasks_completed=self.session_data["tasks_completed"],
            purpose_driven_events=self.session_data["purpose_driven_events"]
        )
        
        return report
    
    def _calculate_emotion_statistics(self) -> Dict[str, Dict[str, float]]:
        """Calculate emotion statistics from session data."""
        emotion_stats = {}
        
        # Group emotions by type
        emotion_groups = {}
        for entry in self.session_data["emotions"]:
            emotion = entry["emotion"]
            intensity = entry["intensity"]
            
            if emotion not in emotion_groups:
                emotion_groups[emotion] = []
            emotion_groups[emotion].append(intensity)
        
        # Calculate statistics for each emotion
        for emotion, intensities in emotion_groups.items():
            if intensities:
                emotion_stats[emotion] = {
                    "current": intensities[-1] if intensities else 0.0,
                    "average": sum(intensities) / len(intensities),
                    "min": min(intensities),
                    "max": max(intensities),
                    "count": len(intensities)
                }
        
        return emotion_stats
    
    def _calculate_neurotransmitter_trends(self) -> Dict[str, List[float]]:
        """Calculate neurotransmitter trends from session data."""
        nt_trends = {}
        
        if not self.session_data["neurotransmitters"]:
            return nt_trends
        
        # Get all NT types
        nt_types = set()
        for entry in self.session_data["neurotransmitters"]:
            nt_types.update(entry["levels"].keys())
        
        # Create trend lists for each NT
        for nt_type in nt_types:
            nt_trends[nt_type] = [
                entry["levels"].get(nt_type, 0.0) 
                for entry in self.session_data["neurotransmitters"]
            ]
        
        return nt_trends
    
    def _get_imagination_statistics(self, imagination_system) -> Dict[str, Any]:
        """Get imagination system statistics."""
        if not imagination_system:
            return {}
        
        try:
            episodes = imagination_system.get_imagined_episodes(limit=100)
            return {
                "total_episodes": len(episodes),
                "average_coherence": sum(ep.get("coherence_score", 0) for ep in episodes) / max(len(episodes), 1),
                "average_plausibility": sum(ep.get("plausibility_score", 0) for ep in episodes) / max(len(episodes), 1),
                "average_novelty": sum(ep.get("novelty_score", 0) for ep in episodes) / max(len(episodes), 1),
                "purposes_used": list(set(ep.get("purpose", "unknown") for ep in episodes))
            }
        except Exception as e:
            self.logger.error(f"Error getting imagination statistics: {e}")
            return {}
    
    def _get_memory_statistics(self, memory_system) -> Dict[str, Any]:
        """Get memory system statistics."""
        if not memory_system:
            return {}
        
        try:
            # This would depend on the memory system's API
            return {
                "total_memories": self.session_data["memories_created"],
                "memories_retrieved": self.session_data["memories_retrieved"],
                "retrieval_ratio": self.session_data["memories_retrieved"] / max(self.session_data["memories_created"], 1)
            }
        except Exception as e:
            self.logger.error(f"Error getting memory statistics: {e}")
            return {}
    
    def _calculate_performance_metrics(self, duration: float) -> Dict[str, float]:
        """Calculate performance metrics."""
        return {
            "events_per_minute": (len(self.session_data["intents"]) + 
                                len(self.session_data["vision_events"]) + 
                                len(self.session_data["humor_events"])) / (duration / 60),
            "inner_dialogue_rate": self.session_data["inner_dialogue_turns"] / (duration / 60),
            "error_rate": len(self.session_data["errors"]) / (duration / 60),
            "warning_rate": len(self.session_data["warnings"]) / (duration / 60),
            "skill_execution_rate": len(self.session_data["skills_executed"]) / (duration / 60)
        }
    
    def save_report(self, report: SessionReport, format: str = "both") -> List[str]:
        """
        Save session report to files.
        
        Args:
            report: SessionReport to save
            format: "json", "markdown", or "both"
            
        Returns:
            List of saved file paths
        """
        saved_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format in ["json", "both"]:
            json_path = os.path.join(self.output_dir, f"report_v5.15.0_{timestamp}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(report), f, indent=2, ensure_ascii=False)
            saved_files.append(json_path)
        
        if format in ["markdown", "both"]:
            md_path = os.path.join(self.output_dir, f"report_v5.15.0_{timestamp}.md")
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_markdown_report(report))
            saved_files.append(md_path)
        
        self.logger.info(f"📊 Session report saved: {saved_files}")
        return saved_files
    
    def _generate_markdown_report(self, report: SessionReport) -> str:
        """Generate human-readable markdown report."""
        md_lines = []
        
        # Header
        md_lines.append(f"# CARL Session Report v5.15.0")
        md_lines.append(f"**Session ID:** {report.session_id}")
        md_lines.append(f"**Duration:** {report.duration_seconds:.1f} seconds")
        md_lines.append(f"**Start:** {report.start_time}")
        md_lines.append(f"**End:** {report.end_time}")
        md_lines.append("")
        
        # Cognitive Metrics
        md_lines.append("## Cognitive Metrics")
        md_lines.append("")
        
        # Emotions
        md_lines.append("### Emotions")
        for emotion, stats in report.emotions.items():
            md_lines.append(f"- **{emotion}:** Current: {stats['current']:.3f}, "
                          f"Avg: {stats['average']:.3f}, Min: {stats['min']:.3f}, "
                          f"Max: {stats['max']:.3f} ({stats['count']} samples)")
        md_lines.append("")
        
        # Intents
        md_lines.append("### Intents Detected")
        intent_counts = {}
        for intent in report.intents:
            intent_type = intent["intent"]
            intent_counts[intent_type] = intent_counts.get(intent_type, 0) + 1
        
        for intent_type, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True):
            md_lines.append(f"- **{intent_type}:** {count} times")
        md_lines.append("")
        
        # Interaction Metrics
        md_lines.append("## Interaction Metrics")
        md_lines.append(f"- **Inner Dialogue Turns:** {report.inner_dialogue_turns}")
        md_lines.append(f"- **Vision Events:** {report.vision_events_received}")
        md_lines.append(f"- **Humor Detections:** {report.humor_detections}")
        md_lines.append(f"- **Laughter Triggers:** {report.laughter_triggers}")
        md_lines.append(f"- **Imagination Artifacts:** {report.imagination_artifacts}")
        md_lines.append("")
        
        # Memory Metrics
        md_lines.append("## Memory Metrics")
        md_lines.append(f"- **Memories Created:** {report.memories_created}")
        md_lines.append(f"- **Memories Retrieved:** {report.memories_retrieved}")
        md_lines.append("")
        
        # Skill Metrics
        md_lines.append("## Skill Metrics")
        md_lines.append(f"- **Skills Executed:** {len(report.skills_executed)}")
        md_lines.append(f"- **Success Rate:** {report.skill_success_rate:.1%}")
        md_lines.append("")
        
        # System Metrics
        md_lines.append("## System Metrics")
        md_lines.append(f"- **Errors:** {len(report.errors)}")
        md_lines.append(f"- **Warnings:** {len(report.warnings)}")
        md_lines.append("")
        
        # Performance Metrics
        md_lines.append("### Performance")
        for metric, value in report.performance_metrics.items():
            md_lines.append(f"- **{metric}:** {value:.2f}")
        md_lines.append("")
        
        # Errors and Warnings
        if report.errors:
            md_lines.append("## Errors")
            for error in report.errors[-10:]:  # Last 10 errors
                md_lines.append(f"- **{error['timestamp']}:** {error['error']}")
            md_lines.append("")
        
        if report.warnings:
            md_lines.append("## Warnings")
            for warning in report.warnings[-10:]:  # Last 10 warnings
                md_lines.append(f"- **{warning['timestamp']}:** {warning['warning']}")
            md_lines.append("")
        
        return "\n".join(md_lines)
