#!/usr/bin/env python3
"""
Enhanced Skill Execution System for CARL

This module provides improved skill execution with:
1. Better rate limiting to prevent ARC overload
2. Connection health monitoring
3. Automatic retry logic for failed commands
4. Command queuing and prioritization
5. Enhanced error handling and recovery
"""

import time
import threading
import asyncio
from typing import Optional, Dict, List, Tuple
from enum import Enum
import logging
from collections import deque

class SkillExecutionState(Enum):
    """Skill execution states."""
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    TIMEOUT = "timeout"

class EnhancedSkillExecutionSystem:
    """
    Enhanced skill execution system with improved rate limiting and error handling.
    """
    
    def __init__(self, ez_robot=None, action_system=None):
        self.ez_robot = ez_robot
        self.action_system = action_system
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting configuration
        self.min_command_interval = 1.0  # seconds between commands
        self.max_concurrent_commands = 1  # Only one command at a time
        self.command_timeout = 10.0  # seconds
        
        # Command tracking
        self.last_command_time = 0
        self.command_queue = deque()
        self.executing_commands = {}
        self.command_history = []
        
        # Connection health
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.connection_healthy = True
        
        # Retry configuration
        self.max_retries = 2
        self.retry_delay = 2.0  # seconds
        
        # Threading
        self.execution_lock = threading.Lock()
        self.queue_lock = threading.Lock()
        
        # Start command processor
        self.running = True
        self.command_processor_thread = threading.Thread(target=self._command_processor, daemon=True)
        self.command_processor_thread.start()
    
    def execute_skill(self, skill_name: str, priority: int = 1) -> bool:
        """
        Execute a skill with enhanced rate limiting and error handling.
        
        Args:
            skill_name: Name of the skill to execute
            priority: Priority level (1=low, 5=high)
            
        Returns:
            True if command was queued successfully, False otherwise
        """
        if not self.ez_robot:
            self.logger.warning("EZ-Robot not available for skill execution")
            return False
        
        # Check connection health
        if not self.connection_healthy:
            self.logger.warning("Connection unhealthy, cannot execute skill")
            return False
        
        # Create command entry
        command_entry = {
            'skill_name': skill_name,
            'priority': priority,
            'timestamp': time.time(),
            'state': SkillExecutionState.PENDING,
            'attempts': 0,
            'retry_count': 0
        }
        
        # Add to queue
        with self.queue_lock:
            self.command_queue.append(command_entry)
            self.logger.info(f"📋 Queued skill: {skill_name} (priority: {priority}, queue size: {len(self.command_queue)})")
        
        return True
    
    def _command_processor(self):
        """Background thread to process command queue."""
        while self.running:
            try:
                # Get next command from queue
                command = None
                with self.queue_lock:
                    if self.command_queue and len(self.executing_commands) < self.max_concurrent_commands:
                        command = self.command_queue.popleft()
                
                if command:
                    self._execute_command(command)
                else:
                    # No commands to process, sleep briefly
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Error in command processor: {e}")
                time.sleep(1.0)
    
    def _execute_command(self, command: Dict):
        """
        Execute a single command with retry logic.
        
        Args:
            command: Command dictionary
        """
        skill_name = command['skill_name']
        command['state'] = SkillExecutionState.EXECUTING
        command['attempts'] += 1
        
        # Add to executing commands
        with self.execution_lock:
            self.executing_commands[skill_name] = command
        
        self.logger.info(f"🎯 Executing skill: {skill_name} (attempt {command['attempts']})")
        
        try:
            # Rate limiting check
            current_time = time.time()
            time_since_last = current_time - self.last_command_time
            
            if time_since_last < self.min_command_interval:
                sleep_time = self.min_command_interval - time_since_last
                self.logger.info(f"⏳ Rate limiting: Waiting {sleep_time:.2f}s before executing {skill_name}")
                time.sleep(sleep_time)
            
            # Execute the command
            start_time = time.time()
            success = self._execute_single_command(skill_name)
            execution_time = time.time() - start_time
            
            if success:
                # Command succeeded
                command['state'] = SkillExecutionState.SUCCESS
                self.last_command_time = time.time()
                self.consecutive_failures = 0
                self.connection_healthy = True
                
                self.logger.info(f"✅ Skill executed successfully: {skill_name} (time: {execution_time:.2f}s)")
                
                # Update history
                self.command_history.append({
                    'skill_name': skill_name,
                    'timestamp': time.time(),
                    'execution_time': execution_time,
                    'state': SkillExecutionState.SUCCESS,
                    'attempts': command['attempts']
                })
                
            else:
                # Command failed
                command['state'] = SkillExecutionState.FAILED
                self.consecutive_failures += 1
                
                self.logger.warning(f"❌ Skill execution failed: {skill_name}")
                
                # Check if we should retry
                if command['retry_count'] < self.max_retries:
                    command['retry_count'] += 1
                    command['state'] = SkillExecutionState.RETRYING
                    
                    self.logger.info(f"🔄 Retrying skill: {skill_name} (retry {command['retry_count']}/{self.max_retries})")
                    
                    # Add back to queue with higher priority
                    with self.queue_lock:
                        command['priority'] = min(command['priority'] + 1, 5)  # Increase priority
                        self.command_queue.appendleft(command)  # Add to front of queue
                    
                    # Wait before retry
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"💥 Skill execution failed permanently: {skill_name} after {command['attempts']} attempts")
                    
                    # Check connection health
                    if self.consecutive_failures >= self.max_consecutive_failures:
                        self.connection_healthy = False
                        self.logger.warning(f"Connection marked as unhealthy after {self.consecutive_failures} consecutive failures")
                    
                    # Update history
                    self.command_history.append({
                        'skill_name': skill_name,
                        'timestamp': time.time(),
                        'execution_time': execution_time,
                        'state': SkillExecutionState.FAILED,
                        'attempts': command['attempts']
                    })
        
        except Exception as e:
            self.logger.error(f"Exception executing skill '{skill_name}': {e}")
            command['state'] = SkillExecutionState.FAILED
        
        finally:
            # Remove from executing commands
            with self.execution_lock:
                if skill_name in self.executing_commands:
                    del self.executing_commands[skill_name]
    
    def _execute_single_command(self, skill_name: str) -> bool:
        """
        Execute a single skill command using the action system.
        
        Args:
            skill_name: Name of the skill to execute
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.action_system:
                # Use the action system's command execution
                result = self.action_system._execute_ezrobot_command(skill_name, skill_name)
                return result is not None
            else:
                self.logger.error("Action system not available")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in single command execution: {e}")
            return False
    
    def get_execution_stats(self) -> Dict:
        """
        Get statistics about skill execution.
        
        Returns:
            Dictionary with execution statistics
        """
        return {
            'queue_size': len(self.command_queue),
            'executing_commands': len(self.executing_commands),
            'consecutive_failures': self.consecutive_failures,
            'connection_healthy': self.connection_healthy,
            'total_commands': len(self.command_history),
            'recent_commands': self.command_history[-10:] if self.command_history else [],
            'executing_skill_names': list(self.executing_commands.keys())
        }
    
    def clear_queue(self):
        """Clear the command queue."""
        with self.queue_lock:
            self.command_queue.clear()
        self.logger.info("Command queue cleared")
    
    def reset_connection_health(self):
        """Reset connection health status."""
        self.connection_healthy = True
        self.consecutive_failures = 0
        self.logger.info("Skill execution connection health reset")
    
    def stop(self):
        """Stop the command processor."""
        self.running = False
        if self.command_processor_thread.is_alive():
            self.command_processor_thread.join(timeout=5.0)
        self.logger.info("Skill execution system stopped") 