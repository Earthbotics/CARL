#!/usr/bin/env python3
"""
Game Theory System for CARL

This module implements a generic game theory system that integrates with CARL's
reasoning pipeline, using JSON-driven game configurations instead of hardcoded
game logic. This replaces the specific tic_tac_toe_system.py with a more
flexible, generic approach.

Features:
- JSON-driven game configurations
- Integration with LogicSystem for OpenAI-based reasoning
- Dynamic thought patterns from JSON configuration
- Event system integration for logging moves
- Memory system integration for storing game history
- Purpose-driven behavior through needs/goals system
- Support for both complete games (like tic-tac-toe) and incomplete games (like Earthly)
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from logic_system import LogicSystem

class GameTheorySystem:
    """
    Generic game theory system that uses CARL's reasoning pipeline.
    Supports both complete games (tic-tac-toe) and incomplete games (Earthly).
    """
    
    def __init__(self, logic_system: LogicSystem, main_app=None):
        """
        Initialize the Game Theory system.
        
        Args:
            logic_system: LogicSystem instance for reasoning
            main_app: Reference to main application for event logging
        """
        self.logic_system = logic_system
        self.main_app = main_app
        self.logger = logging.getLogger(__name__)
        
        # Game configurations loaded from JSON files
        self.game_configs = {}
        self.active_games = {}
        
        # Load all available game configurations
        self._load_game_configurations()
        
    def _load_game_configurations(self):
        """Load all available game configurations from JSON files."""
        try:
            games_dir = "games"
            if os.path.exists(games_dir):
                for filename in os.listdir(games_dir):
                    if filename.endswith('.json'):
                        game_name = filename[:-5]  # Remove .json extension
                        game_path = os.path.join(games_dir, filename)
                        
                        with open(game_path, 'r') as f:
                            config = json.load(f)
                            self.game_configs[game_name] = config
                            self.logger.info(f"🎮 Loaded game configuration: {game_name}")
        except Exception as e:
            self.logger.error(f"❌ Error loading game configurations: {e}")
    
    def get_game_config(self, game_name: str) -> Optional[Dict[str, Any]]:
        """
        Get game configuration by name.
        
        Args:
            game_name: Name of the game
            
        Returns:
            Game configuration dictionary or None if not found
        """
        return self.game_configs.get(game_name)
    
    def start_game(self, game_name: str, **kwargs) -> Dict[str, Any]:
        """
        Start a new game of the specified type.
        
        Args:
            game_name: Name of the game to start
            **kwargs: Additional game-specific parameters
            
        Returns:
            Dictionary with game start information
        """
        try:
            config = self.get_game_config(game_name)
            if not config:
                return {"success": False, "error": f"Game configuration not found: {game_name}"}
            
            # Initialize game state based on configuration
            game_state = self._initialize_game_state(config, **kwargs)
            
            # Store active game
            self.active_games[game_name] = {
                "config": config,
                "state": game_state,
                "started_at": datetime.now().isoformat()
            }
            
            # Log game start event
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log(f"🎮 Started {game_name} game")
            
            # Evaluate Purpose Driven Behavior for game start
            if self.main_app and hasattr(self.main_app, 'inner_self'):
                pdb_result = self.main_app.inner_self.evaluate_purpose_driven_behavior(
                    action_type=f"{game_name}_start",
                    context={"game_type": game_name, "action": "start_game"}
                )
                if pdb_result and pdb_result.get('pdb_score', 0) > 0:
                    self.logger.info(f"🎯 PDB Score: {pdb_result['pdb_score']:.2f} for starting {game_name}")
            
            return {
                "success": True,
                "message": f"New {game_name} game started",
                "game_state": game_state,
                "config": config
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error starting game {game_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def _initialize_game_state(self, config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Initialize game state based on configuration.
        
        Args:
            config: Game configuration
            **kwargs: Additional parameters
            
        Returns:
            Initialized game state
        """
        game_type = config.get("type", "complete")
        
        if game_type == "incomplete_game":
            # For incomplete games like Earthly, initialize belief state
            return {
                "type": "incomplete_game",
                "belief_state": config.get("beliefs", {}),
                "current_actions": [],
                "observations": [],
                "rewards": []
            }
        else:
            # For complete games like tic-tac-toe, initialize board state
            return {
                "type": "complete_game",
                "board": config.get("board", [["", "", ""], ["", "", ""], ["", "", ""]]),
                "current_turn": config.get("current_turn", "CARL"),
                "status": "new",
                "moves": [],
                "rules_summary": config.get("rules_summary", "")
            }
    
    def make_move(self, game_name: str, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a move in the specified game.
        
        Args:
            game_name: Name of the game
            move_data: Move data (coordinates, player, etc.)
            
        Returns:
            Dictionary with move result
        """
        try:
            if game_name not in self.active_games:
                return {"success": False, "error": f"Game {game_name} not active"}
            
            game = self.active_games[game_name]
            config = game["config"]
            state = game["state"]
            
            if config.get("type") == "incomplete_game":
                return self._handle_incomplete_game_move(game_name, move_data)
            else:
                return self._handle_complete_game_move(game_name, move_data)
                
        except Exception as e:
            self.logger.error(f"❌ Error making move in {game_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def _handle_complete_game_move(self, game_name: str, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle move for complete games (like tic-tac-toe).
        
        Args:
            game_name: Name of the game
            move_data: Move data
            
        Returns:
            Move result
        """
        game = self.active_games[game_name]
        state = game["state"]
        
        # Extract move information
        row = move_data.get("row", 0)
        col = move_data.get("col", 0)
        player = move_data.get("player", "Human")
        
        # Validate move
        if not self._is_valid_move(state, row, col):
            return {"success": False, "error": f"Invalid move: [{row}, {col}]"}
        
        # Make the move
        symbol = "X" if player == "CARL" else "O"
        state["board"][row][col] = symbol
        
        # Record the move
        move_record = {
            "turn": player,
            "move": [row, col],
            "thought": f"{player} placed {symbol} at [{row}, {col}]",
            "timestamp": datetime.now().isoformat()
        }
        state["moves"].append(move_record)
        
        # Check for win/draw
        game_status = self._evaluate_board(state)
        state["status"] = game_status["status"]
        
        # Switch turns
        state["current_turn"] = "Human" if player == "CARL" else "CARL"
        
        # 🎯 ATTENTION SYSTEM: Update attention on turn switch
        if hasattr(self.main_app, 'attention') and self.main_app.attention:
            from inner_attention import FocusSlot
            game_id = game_name
            
            if state["current_turn"] == "Human":
                # When it's Human's turn, focus shifts to outer (waiting for human input)
                self.main_app.attention.propose(FocusSlot(
                    owner="outer",
                    topic=f"game/{game_id}",
                    strength=0.9,
                    context={"game_id": game_id, "turn": "human"}
                ))
            else:
                # When it's CARL's turn, focus shifts to game (planning move)
                self.main_app.attention.propose(FocusSlot(
                    owner="game",
                    topic=f"game/{game_id}",
                    strength=0.85,
                    context={"game_id": game_id, "turn": "carl"}
                ))
            
            # Log focus change
            if hasattr(self.main_app, '_log_focus_change'):
                self.main_app._log_focus_change()
        
        # Log move event
        if self.main_app and hasattr(self.main_app, 'log'):
            self.main_app.log(f"🎮 {player} placed {symbol} at [{row}, {col}]")
        
        return {
            "success": True,
            "move": [row, col],
            "board": state["board"],
            "status": state["status"],
            "current_turn": state["current_turn"]
        }
    
    def _handle_incomplete_game_move(self, game_name: str, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle move for incomplete games (like Earthly).
        
        Args:
            game_name: Name of the game
            move_data: Move data
            
        Returns:
            Move result
        """
        # For incomplete games, moves are more like actions/observations
        game = self.active_games[game_name]
        state = game["state"]
        
        action_type = move_data.get("action_type", "observation")
        action_data = move_data.get("action_data", {})
        
        # Record the action
        action_record = {
            "action_type": action_type,
            "action_data": action_data,
            "timestamp": datetime.now().isoformat()
        }
        state["current_actions"].append(action_record)
        
        # Log action event
        if self.main_app and hasattr(self.main_app, 'log'):
            self.main_app.log(f"🌍 {game_name} action: {action_type}")
        
        return {
            "success": True,
            "action": action_record,
            "game_state": state
        }
    
    def _is_valid_move(self, state: Dict[str, Any], row: int, col: int) -> bool:
        """
        Check if a move is valid for complete games.
        
        Args:
            state: Game state
            row: Row index
            col: Column index
            
        Returns:
            True if move is valid
        """
        if "board" not in state:
            return False
        
        board = state["board"]
        if not (0 <= row < len(board) and 0 <= col < len(board[0])):
            return False
        
        return board[row][col] == ""
    
    def _evaluate_board(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate board for complete games.
        
        Args:
            state: Game state
            
        Returns:
            Game status
        """
        board = state["board"]
        
        # Check for wins
        for player in ["X", "O"]:
            # Check rows
            for row in board:
                if all(cell == player for cell in row):
                    return {"status": "win", "winner": "CARL" if player == "X" else "Human"}
            
            # Check columns
            for col in range(len(board[0])):
                if all(board[row][col] == player for row in range(len(board))):
                    return {"status": "win", "winner": "CARL" if player == "X" else "Human"}
            
            # Check diagonals
            if all(board[i][i] == player for i in range(min(len(board), len(board[0])))):
                return {"status": "win", "winner": "CARL" if player == "X" else "Human"}
            if all(board[i][len(board[0])-1-i] == player for i in range(min(len(board), len(board[0])))):
                return {"status": "win", "winner": "CARL" if player == "X" else "Human"}
        
        # Check for draw
        if all(cell != "" for row in board for cell in row):
            return {"status": "draw", "winner": None}
        
        return {"status": "ongoing", "winner": None}
    
    def get_game_state(self, game_name: str) -> Dict[str, Any]:
        """
        Get current game state.
        
        Args:
            game_name: Name of the game
            
        Returns:
            Current game state
        """
        if game_name not in self.active_games:
            return {"success": False, "error": f"Game {game_name} not active"}
        
        return {
            "success": True,
            "game_state": self.active_games[game_name]["state"],
            "config": self.active_games[game_name]["config"]
        }
    
    def end_game(self, game_name: str) -> Dict[str, Any]:
        """
        End the specified game.
        
        Args:
            game_name: Name of the game
            
        Returns:
            End game result
        """
        try:
            if game_name not in self.active_games:
                return {"success": False, "error": f"Game {game_name} not active"}
            
            # Get final state
            final_state = self.active_games[game_name]["state"]
            
            # Remove from active games
            del self.active_games[game_name]
            
            # Log game end event
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log(f"🎮 Ended {game_name} game")
            
            return {
                "success": True,
                "message": f"{game_name} game ended",
                "final_state": final_state
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error ending game {game_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def list_available_games(self) -> List[str]:
        """
        Get list of available game configurations.
        
        Returns:
            List of game names
        """
        return list(self.game_configs.keys())
    
    def list_active_games(self) -> List[str]:
        """
        Get list of currently active games.
        
        Returns:
            List of active game names
        """
        return list(self.active_games.keys())
