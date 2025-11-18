#!/usr/bin/env python3
"""
Logic System for CARL

This module provides a wrapper around OpenAI calls for structured reasoning.
It serves as the foundation for CARL's reasoning pipeline, allowing for
dynamic thought generation and decision-making based on prompts and context.

Features:
- OpenAI API integration for reasoning
- Template-based prompt processing
- Structured JSON response parsing
- Error handling and fallback logic
- Future expansion for general reasoning tasks
"""

import json
import logging
from typing import Dict, Any, Optional

try:
    from api_client import APIClient
except ImportError:
    APIClient = None

class LogicSystem:
    """
    Logic System that acts as a wrapper around OpenAI calls for structured reasoning.
    
    This system provides a clean interface for CARL to request reasoning from OpenAI,
    with proper error handling and response parsing.
    """
    
    def __init__(self, api_client: Optional[APIClient] = None):
        """
        Initialize the Logic System.
        
        Args:
            api_client: Optional APIClient instance. If None, creates a new one.
        """
        self.logger = logging.getLogger(__name__)
        if api_client is not None:
            self.api_client = api_client
        elif APIClient is not None:
            try:
                self.api_client = APIClient()
            except Exception as e:
                self.logger.warning(f"Failed to create APIClient: {e} - LogicSystem will work in offline mode")
                self.api_client = None
        else:
            self.logger.warning("APIClient not available - LogicSystem will work in offline mode")
            self.api_client = None
        
    def request(self, prompt: str, max_retries: int = 3, crucial_process: bool = False) -> Dict[str, Any]:
        """
        Make a reasoning request to OpenAI and return structured response.
        Implements memory bias by checking local JSON files first.
        
        Args:
            prompt: The prompt to send to OpenAI
            max_retries: Maximum number of retry attempts
            crucial_process: If True, uses enhanced processing for critical decisions
            
        Returns:
            Dictionary containing the reasoning result, or error information
        """
        try:
            self.logger.info(f"🧠 LogicSystem: Processing reasoning request")
            if crucial_process:
                self.logger.info("⚡ CRUCIAL PROCESS: Enhanced analysis mode activated")
            self.logger.debug(f"Prompt: {prompt[:100]}...")
            
            # Check for local JSON data first (memory bias)
            local_response = self._check_local_json_for_reasoning(prompt)
            if local_response:
                self.logger.info("🎯 LogicSystem: Using local JSON data (memory bias)")
                return local_response
            
            # Check if API client is available
            if self.api_client is None:
                return {
                    "error": "APIClient not available - LogicSystem in offline mode",
                    "success": False
                }
            
            # Enhanced prompt for crucial processes (like gameplay)
            enhanced_prompt = prompt
            if crucial_process:
                enhanced_prompt = self._enhance_prompt_for_crucial_process(prompt)
                self.logger.info("⚡ Enhanced prompt for crucial analysis")
            
            # Make the API call
            response = self.api_client.openai_call(enhanced_prompt)
            
            if not response:
                return {
                    "error": "No response from OpenAI",
                    "success": False
                }
            
            # Try to parse as JSON if it looks like JSON
            if response.strip().startswith('{') or response.strip().startswith('['):
                try:
                    parsed_response = json.loads(response)
                    parsed_response["success"] = True
                    if crucial_process:
                        parsed_response["crucial_analysis"] = True
                    return parsed_response
                except json.JSONDecodeError:
                    # If JSON parsing fails, return as text
                    return {
                        "response": response,
                        "success": True,
                        "raw": True,
                        "crucial_analysis": crucial_process
                    }
            else:
                # Return as text response
                return {
                    "response": response,
                    "success": True,
                    "raw": True
                }
                
        except Exception as e:
            self.logger.error(f"❌ LogicSystem error: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def process_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process a template string with context variables.
        
        Args:
            template: Template string with {{variable}} placeholders
            context: Dictionary of variables to substitute
            
        Returns:
            Processed template string
        """
        try:
            processed = template
            for key, value in context.items():
                placeholder = f"{{{{{key}}}}}"
                processed = processed.replace(placeholder, str(value))
            return processed
        except Exception as e:
            self.logger.error(f"❌ Template processing error: {e}")
            return template
    
    def request_with_template(self, template: str, context: Dict[str, Any], crucial_process: bool = False) -> Dict[str, Any]:
        """
        Process a template and make a reasoning request.
        
        Args:
            template: Template string with {{variable}} placeholders
            context: Dictionary of variables to substitute
            crucial_process: If True, uses enhanced processing for critical decisions
            
        Returns:
            Dictionary containing the reasoning result
        """
        try:
            processed_prompt = self.process_template(template, context)
            return self.request(processed_prompt, crucial_process=crucial_process)
        except Exception as e:
            self.logger.error(f"❌ Template request error: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def _enhance_prompt_for_crucial_process(self, prompt: str) -> str:
        """
        Enhance prompt for crucial processes like gameplay.
        
        Args:
            prompt: Original prompt
            
        Returns:
            Enhanced prompt with additional context and instructions
        """
        enhancement = """
        
CRUCIAL ANALYSIS MODE:
- This is a critical decision requiring deep strategic analysis
- Consider all possible outcomes and consequences
- Apply advanced reasoning and pattern recognition
- Provide detailed justification for your decision
- Think step-by-step through the problem
- Consider both immediate and long-term implications
"""
        return prompt + enhancement
    
    def _check_local_json_for_reasoning(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Check local JSON files for relevant reasoning before calling OpenAI.
        Implements memory bias by prioritizing personal/local data.
        
        SPECIAL CASE: Gameplay requests always go to OpenAI for strategic analysis.
        
        Args:
            prompt: The prompt to analyze
            
        Returns:
            Local response if found, None otherwise
        """
        try:
            import os
            import json
            
            prompt_lower = prompt.lower()
            
            # CRITICAL: Gameplay requests always go to OpenAI for strategic analysis
            if any(keyword in prompt_lower for keyword in [
                "tic-tac-toe", "tic tac toe", "choose_move", "gameplay", 
                "board", "move", "strategy", "win", "block"
            ]):
                self.logger.info("🎮 Gameplay detected - routing to OpenAI for strategic analysis")
                return None  # Force OpenAI call for gameplay
            
            # Check for goal-related reasoning
            if any(keyword in prompt_lower for keyword in ["goal", "goals", "objective", "target"]):
                return self._get_goal_reasoning_from_local(prompt)
            
            # Check for need-related reasoning
            if any(keyword in prompt_lower for keyword in ["need", "needs", "requirement", "desire"]):
                return self._get_need_reasoning_from_local(prompt)
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error checking local JSON for reasoning: {e}")
            return None
    
    def _get_tic_tac_toe_reasoning_from_local(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get tic-tac-toe reasoning from local JSON data."""
        try:
            import os
            import json
            
            game_file = "games/tic_tac_toe.json"
            if os.path.exists(game_file):
                with open(game_file, 'r') as f:
                    game_data = json.load(f)
                
                # Extract board state from prompt if available
                board = game_data.get("board", [["", "", ""], ["", "", ""], ["", "", ""]])
                
                # Simple strategy reasoning based on local game data
                if "choose_move" in prompt.lower():
                    # Find best move using simple strategy
                    move = self._find_best_move_simple(board)
                    reasoning = "I'm using my strategic thinking to find the best move based on the current board state."
                    
                    return {
                        "move": move,
                        "reasoning": reasoning,
                        "success": True,
                        "source": "local_json"
                    }
                
                elif "evaluate_board" in prompt.lower():
                    # Evaluate board state
                    status = self._evaluate_board_simple(board)
                    
                    return {
                        "status": status["status"],
                        "winner": status["winner"],
                        "success": True,
                        "source": "local_json"
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error getting tic-tac-toe reasoning from local data: {e}")
            return None
    
    def _find_best_move_simple(self, board):
        """Find best move using simple strategy."""
        try:
            # Strategy: center > corners > sides
            move_priority = [
                (1, 1),  # center
                (0, 0), (0, 2), (2, 0), (2, 2),  # corners
                (0, 1), (1, 0), (1, 2), (2, 1)   # sides
            ]
            
            for row, col in move_priority:
                if board[row][col] == "":
                    return [row, col]
            
            return [0, 0]  # fallback
            
        except Exception as e:
            self.logger.error(f"❌ Error finding best move: {e}")
            return [0, 0]
    
    def _evaluate_board_simple(self, board) -> Dict[str, Any]:
        """Evaluate board state using simple logic."""
        try:
            # Check for wins
            for player in ["X", "O"]:
                # Check rows
                for row in board:
                    if all(cell == player for cell in row):
                        return {"status": "win", "winner": "CARL" if player == "X" else "Human"}
                
                # Check columns
                for col in range(3):
                    if all(board[row][col] == player for row in range(3)):
                        return {"status": "win", "winner": "CARL" if player == "X" else "Human"}
                
                # Check diagonals
                if all(board[i][i] == player for i in range(3)):
                    return {"status": "win", "winner": "CARL" if player == "X" else "Human"}
                if all(board[i][2-i] == player for i in range(3)):
                    return {"status": "win", "winner": "CARL" if player == "X" else "Human"}
            
            # Check for draw
            if all(cell != "" for row in board for cell in row):
                return {"status": "draw", "winner": None}
            
            return {"status": "ongoing", "winner": None}
            
        except Exception as e:
            self.logger.error(f"❌ Error evaluating board: {e}")
            return {"status": "ongoing", "winner": None}
    
    def _get_goal_reasoning_from_local(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get goal reasoning from local JSON data."""
        try:
            import os
            import json
            
            goals_dir = "goals"
            if not os.path.exists(goals_dir):
                return None
            
            goals_list = []
            for filename in os.listdir(goals_dir):
                if filename.endswith('.json'):
                    goal_file = os.path.join(goals_dir, filename)
                    try:
                        with open(goal_file, 'r') as f:
                            goal_data = json.load(f)
                            goals_list.append(goal_data.get('name', filename.replace('.json', '')))
                    except Exception as e:
                        self.logger.error(f"❌ Error loading goal file {goal_file}: {e}")
            
            if goals_list:
                return {
                    "goals": goals_list,
                    "reasoning": f"Based on my local goal data, I have {len(goals_list)} active goals: {', '.join(goals_list)}",
                    "success": True,
                    "source": "local_json"
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error getting goal reasoning from local data: {e}")
            return None
    
    def _get_need_reasoning_from_local(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get need reasoning from local JSON data."""
        try:
            import os
            import json
            
            needs_dir = "needs"
            if not os.path.exists(needs_dir):
                return None
            
            needs_list = []
            for filename in os.listdir(needs_dir):
                if filename.endswith('.json'):
                    need_file = os.path.join(needs_dir, filename)
                    try:
                        with open(need_file, 'r') as f:
                            need_data = json.load(f)
                            needs_list.append(need_data.get('name', filename.replace('.json', '')))
                    except Exception as e:
                        self.logger.error(f"❌ Error loading need file {need_file}: {e}")
            
            if needs_list:
                return {
                    "needs": needs_list,
                    "reasoning": f"Based on my local need data, I have {len(needs_list)} active needs: {', '.join(needs_list)}",
                    "success": True,
                    "source": "local_json"
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error getting need reasoning from local data: {e}")
            return None
