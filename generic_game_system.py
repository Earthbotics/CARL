#!/usr/bin/env python3
"""
Generic Game System for CARL

This module implements a generic game system that can work with any game JSON file,
providing a flexible framework for different types of games.

Features:
- Dynamic game loading from JSON files
- Generic move processing
- Turn management
- Game state persistence
- Integration with LogicSystem for AI reasoning
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple, Any, List
from logic_system import LogicSystem

class GenericGameSystem:
    """
    Generic game system that can work with any game JSON file.
    """
    
    def __init__(self, logic_system: LogicSystem, main_app=None):
        """
        Initialize the Generic Game system.
        
        Args:
            logic_system: LogicSystem instance for reasoning
            main_app: Reference to main application for event logging
        """
        self.logic_system = logic_system
        self.main_app = main_app
        self.logger = logging.getLogger(__name__)
        
        # Game state
        self.games_dir = "games"
        self.current_game = None
        self.current_game_data = None
        # Cached strategy/priorities loaded from JSON with sensible defaults
        self.move_priority: List[str] = []  # e.g., ["win", "block", "center", "corner", "side"]
        self.rules_config: Dict[str, Any] = {}
        
    def load_game(self, game_type: str) -> Dict[str, Any]:
        """
        Load a game from JSON file.
        
        Args:
            game_type: Type of game to load (e.g., "tic_tac_toe", "chess")
            
        Returns:
            Dictionary with game loading result
        """
        try:
            game_file = os.path.join(self.games_dir, f"{game_type}.json")
            
            if not os.path.exists(game_file):
                return {"success": False, "error": f"Game file not found: {game_file}"}
            
            with open(game_file, 'r') as f:
                game_data = json.load(f)
            
            # Validate game data structure
            required_fields = ["name", "description", "board", "current_turn", "status"]
            for field in required_fields:
                if field not in game_data:
                    return {"success": False, "error": f"Missing required field: {field}"}
            
            # Inject defaults for strategy/config to support fresh startups
            if "move_priority" not in game_data:
                game_data["move_priority"] = ["win", "block", "center", "corner", "side"]
            if "rules_config" not in game_data:
                game_data["rules_config"] = {
                    "winning_lines": "standard_3x3",
                    "board_size": [3, 3],
                    "symbols": {"CARL": "X", "Human": "O"}
                }
            if "gameplay_prompts" not in game_data:
                game_data["gameplay_prompts"] = {}

            self.current_game = game_type
            self.current_game_data = game_data
            self.move_priority = game_data.get("move_priority", [])
            self.rules_config = game_data.get("rules_config", {})
            
            self.logger.info(f"🎮 Loaded game: {game_type}")
            
            return {
                "success": True,
                "game_type": game_type,
                "game_data": game_data
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error loading game {game_type}: {e}")
            return {"success": False, "error": str(e)}
    
    def start_game(self, game_type: str) -> Dict[str, Any]:
        """
        Start a new game.
        
        Args:
            game_type: Type of game to start
            
        Returns:
            Dictionary with game start result
        """
        try:
            # Load the game
            load_result = self.load_game(game_type)
            if not load_result.get("success"):
                return load_result
            
            # Reset game state
            self.current_game_data["status"] = "ongoing"
            self.current_game_data["moves"] = []
            
            # Reset board if it exists
            if "board" in self.current_game_data:
                if game_type == "tic_tac_toe":
                    self.current_game_data["board"] = [["", "", ""], ["", "", ""], ["", "", ""]]
                # Future: Add other game board resets here
            
            # Save game state
            self._save_game_data()
            
            # Log game start event
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log(f"🎮 Started {game_type} game")
            
            return {
                "success": True,
                "message": f"New {game_type} game started",
                "game_type": game_type,
                "game_data": self.current_game_data
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error starting game {game_type}: {e}")
            return {"success": False, "error": str(e)}
    
    def make_move(self, move, player: str = "Human") -> Dict[str, Any]:
        """
        Make a move in the current game.
        
        Args:
            move: Move coordinates/parameters
            player: Player making the move ("Human" or "CARL")
            
        Returns:
            Dictionary with move result
        """
        try:
            if not self.current_game_data:
                return {"success": False, "error": "No game loaded"}
            
            if self.current_game_data["current_turn"] != player:
                return {"success": False, "error": f"Not {player}'s turn"}
            
            if self.current_game_data["status"] not in ["ongoing", "new"]:
                return {"success": False, "error": "Game not in progress"}
            
            # Validate move based on game type
            if not self._is_valid_move(move):
                return {"success": False, "error": f"Invalid move: {move}"}
            
            # Make the move based on game type
            move_result = self._execute_move(move, player)
            if not move_result.get("success"):
                return move_result
            
            # Record the move
            move_record = {
                "turn": player,
                "move": move,
                "thought": move_result.get("thought", f"{player} player move"),
                "timestamp": datetime.now().isoformat()
            }
            self.current_game_data["moves"].append(move_record)
            
            # Check for win/draw
            game_status = self._evaluate_game_state()
            self.current_game_data["status"] = game_status["status"]
            
            # Switch turns
            self.current_game_data["current_turn"] = "CARL" if player == "Human" else "Human"
            
            # Save game state
            self._save_game_data()
            
            # Log move event
            if self.main_app and hasattr(self.main_app, 'log'):
                self.main_app.log(f"🎮 {player} made move {move}")
            
            return {
                "success": True,
                "move": move,
                "board": self.current_game_data.get("board"),
                "status": self.current_game_data["status"],
                "current_turn": self.current_game_data["current_turn"],
                "thought": move_result.get("thought")
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error making move: {e}")
            return {"success": False, "error": str(e)}
    
    def _is_valid_move(self, move) -> bool:
        """Check if a move is valid for the current game."""
        if not self.current_game or not self.current_game_data:
            return False
        
        if self.current_game == "tic_tac_toe":
            if not isinstance(move, list) or len(move) != 2:
                return False
            
            row, col = move
            if not (0 <= row <= 2 and 0 <= col <= 2):
                return False
            
            board = self.current_game_data.get("board", [])
            if not board or row >= len(board) or col >= len(board[0]):
                return False
            
            return board[row][col] == ""
        
        # Future: Add validation for other game types
        return False
    
    def choose_carl_move(self) -> Dict[str, Any]:
        """Choose CARL's move using AI prompt from JSON with fallback to JSON-configured priorities."""
        try:
            if not self.current_game_data:
                return {"success": False, "error": "No game loaded"}
            if self.current_game_data.get("current_turn") != "CARL":
                return {"success": False, "error": "Not CARL's turn"}

            board = self.current_game_data.get("board", [])
            prompts = self.current_game_data.get("gameplay_prompts", {})
            choose_move_prompt = prompts.get("choose_move")

            # Attempt AI-based move selection if prompt provided
            if choose_move_prompt:
                try:
                    context = {"board": board}
                    # Allow system personality context if main_app available
                    if self.main_app and hasattr(self.main_app, 'personality_system'):
                        context["personality_context"] = self.main_app.personality_system.get_current_personality_state()
                    result = self.logic_system.request_with_template(choose_move_prompt, context, crucial_process=True)
                    if result and result.get("success"):
                        if "move" in result and isinstance(result["move"], list):
                            move = result["move"]
                            thought = result.get("reasoning", "AI-selected strategic move")
                            # Validate
                            if self._is_valid_move(move):
                                return {"success": True, "move": move, "thought": thought}
                        # Try parsing JSON response field
                        if isinstance(result.get("response"), str):
                            try:
                                parsed = json.loads(result["response"])
                                move = parsed.get("move")
                                thought = parsed.get("reasoning", "AI-selected strategic move")
                                if move and self._is_valid_move(move):
                                    return {"success": True, "move": move, "thought": thought}
                            except Exception:
                                pass
                except Exception:
                    # Fall back below
                    pass

            # Fallback: JSON-configured priority policy
            fallback_move, policy_reason = self._fallback_move_by_priority(board)
            if fallback_move is not None:
                return {"success": True, "move": fallback_move, "thought": policy_reason}

            return {"success": False, "error": "No valid moves available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _fallback_move_by_priority(self, board: List[List[str]]) -> Tuple[Optional[List[int]], str]:
        """Choose a move using JSON-defined move_priority order."""
        try:
            priorities = self.move_priority or ["win", "block", "center", "corner", "side"]
            symbols = self.rules_config.get("symbols", {"CARL": "X", "Human": "O"})
            my_symbol = symbols.get("CARL", "X")
            opp_symbol = symbols.get("Human", "O")

            # Helper to iterate empties
            empties = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]

            for rule in priorities:
                if rule == "win":
                    for r, c in empties:
                        if self._would_win_on(board, r, c, my_symbol):
                            return [r, c], "Following JSON move_priority: WIN"
                elif rule == "block":
                    for r, c in empties:
                        if self._would_win_on(board, r, c, opp_symbol):
                            return [r, c], "Following JSON move_priority: BLOCK"
                elif rule == "center":
                    if [1, 1] in [[r, c] for r, c in empties]:
                        return [1, 1], "Following JSON move_priority: CENTER"
                elif rule == "corner":
                    for pos in [(0, 0), (0, 2), (2, 0), (2, 2)]:
                        if list(pos) in [[r, c] for r, c in empties]:
                            return [pos[0], pos[1]], "Following JSON move_priority: CORNER"
                elif rule == "side":
                    for pos in [(0, 1), (1, 0), (1, 2), (2, 1)]:
                        if list(pos) in [[r, c] for r, c in empties]:
                            return [pos[0], pos[1]], "Following JSON move_priority: SIDE"

            return None, ""
        except Exception:
            return None, ""

    def _would_win_on(self, board: List[List[str]], row: int, col: int, symbol: str) -> bool:
        try:
            temp = [r[:] for r in board]
            temp[row][col] = symbol
            return self._check_win_symbol(temp, symbol)
        except Exception:
            return False

    def _check_win_symbol(self, board: List[List[str]], symbol: str) -> bool:
        # rows
        for r in range(3):
            if all(board[r][c] == symbol for c in range(3)):
                return True
        # cols
        for c in range(3):
            if all(board[r][c] == symbol for r in range(3)):
                return True
        # diags
        if all(board[i][i] == symbol for i in range(3)):
            return True
        if all(board[i][2 - i] == symbol for i in range(3)):
            return True
        return False

    def simple_board_evaluation(self, board: Optional[List[List[str]]] = None) -> Dict[str, Any]:
        """JSON-driven simple board evaluation. Returns status, winner, and score breakdown."""
        try:
            if board is None:
                board = self.current_game_data.get("board", []) if self.current_game_data else []
            symbols = self.rules_config.get("symbols", {"CARL": "X", "Human": "O"})
            my_symbol = symbols.get("CARL", "X")
            opp_symbol = symbols.get("Human", "O")

            status = self._evaluate_game_state()
            score = 0
            lines = self._collect_lines(board)
            for line in lines:
                if line.count(my_symbol) == 2 and line.count("") == 1:
                    score += 3
                if line.count(opp_symbol) == 2 and line.count("") == 1:
                    score += 2
                if line.count(my_symbol) == 1 and line.count("") == 2:
                    score += 1
            return {"status": status.get("status"), "winner": status.get("winner"), "score": score}
        except Exception as e:
            return {"status": "ongoing", "winner": None, "error": str(e)}

    def _collect_lines(self, board: List[List[str]]) -> List[List[str]]:
        lines: List[List[str]] = []
        for r in range(3):
            lines.append([board[r][c] for c in range(3)])
        for c in range(3):
            lines.append([board[r][c] for r in range(3)])
        lines.append([board[i][i] for i in range(3)])
        lines.append([board[i][2 - i] for i in range(3)])
        return lines

    def _execute_move(self, move, player: str) -> Dict[str, Any]:
        """Execute a move for the current game."""
        if self.current_game == "tic_tac_toe":
            return self._execute_tic_tac_toe_move(move, player)
        
        # Future: Add execution for other game types
        return {"success": False, "error": f"Move execution not implemented for {self.current_game}"}
    
    def _execute_tic_tac_toe_move(self, move, player: str) -> Dict[str, Any]:
        """Execute a tic-tac-toe move."""
        try:
            row, col = move
            symbol = "X" if player == "CARL" else "O"
            
            # Make the move
            self.current_game_data["board"][row][col] = symbol
            
            # Use first-person phrasing for CARL
            if player == "CARL":
                thought = f"I placed {symbol} at {move}"
            else:
                thought = f"{player} placed {symbol} at {move}"
            
            return {
                "success": True,
                "thought": thought
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _evaluate_game_state(self) -> Dict[str, Any]:
        """Evaluate the current game state."""
        if self.current_game == "tic_tac_toe":
            return self._evaluate_tic_tac_toe_board()
        
        # Future: Add evaluation for other game types
        return {"status": "ongoing", "winner": None}
    
    def _evaluate_tic_tac_toe_board(self) -> Dict[str, Any]:
        """Evaluate tic-tac-toe board for wins or draws."""
        board = self.current_game_data.get("board", [])
        
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
    
    def _save_game_data(self):
        """Save current game data to file."""
        try:
            if not self.current_game or not self.current_game_data:
                return
            
            game_file = os.path.join(self.games_dir, f"{self.current_game}.json")
            os.makedirs(os.path.dirname(game_file), exist_ok=True)
            
            with open(game_file, 'w') as f:
                json.dump(self.current_game_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving game data: {e}")
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state."""
        if not self.current_game_data:
            return {"error": "No game loaded"}
        
        return {
            "game_type": self.current_game,
            "board": self.current_game_data.get("board"),
            "current_turn": self.current_game_data.get("current_turn"),
            "status": self.current_game_data.get("status"),
            "moves": self.current_game_data.get("moves", [])
        }
