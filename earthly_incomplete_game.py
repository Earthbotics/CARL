#!/usr/bin/env python3
"""
Earthly Incomplete Game Engine for CARL

This module implements a minimal, JSON-driven incomplete-game engine for CARL's "Earthly" that:
- maintains a belief state
- plans actions vs. probes (VoI - Value of Information)
- computes need/goal reward (homeostasis)
- updates PDB + STM/LTM + concept associations
- plugs into the existing Perception → Judgment → Needs → Goals → Actions pipeline without hardcoding

The engine is designed to be completely JSON-driven, with no hardcoded strings or game logic.
"""

from typing import Dict, Any, Tuple, List
import math
import random
import logging

class BeliefState:
    """
    Maintains belief state for latent variables using Bayesian updates.
    """
    
    def __init__(self, priors: Dict[str, Any]):
        """
        Initialize belief state with prior distributions.
        
        Args:
            priors: Dictionary of prior distributions for latent variables
        """
        self.latent = priors.copy()  # store params (e.g., categorical probs / beta params)
        self.logger = logging.getLogger(__name__)
    
    def entropy(self, key: str) -> float:
        """
        Calculate entropy for a given latent variable.
        
        Args:
            key: Name of the latent variable
            
        Returns:
            Entropy value
        """
        p = self.latent.get(key, {})
        
        if "probs" in p:
            # Categorical distribution entropy
            probs = p["probs"]
            return -sum(max(1e-9, x) * math.log(max(1e-9, x)) for x in probs.values())
        
        if {"alpha", "beta"} <= p.keys():
            # Beta distribution - use variance as entropy proxy
            a, b = p["alpha"], p["beta"]
            mean = a / (a + b)
            var = (a * b) / (((a + b) ** 2) * (a + b + 1))
            return float(var + (0.5 - abs(0.5 - mean)) * 0.1)
        
        if "p" in p:  # Bernoulli distribution
            q = max(1e-9, min(1 - 1e-9, p["p"]))
            return -(q * math.log(q) + (1 - q) * math.log(1 - q))
        
        return 0.0
    
    def expected_entropy(self, key: str) -> float:
        """
        Calculate expected entropy after observation (myopic assumption).
        
        Args:
            key: Name of the latent variable
            
        Returns:
            Expected entropy value
        """
        # Simple myopic assumption: observation will collapse uncertainty
        return 0.2 * self.entropy(key)
    
    def update(self, obs_key: str, obs_value: Any):
        """
        Update belief state with new observation using Bayesian update.
        
        Args:
            obs_key: Key of the observed variable
            obs_value: Observed value
        """
        p = self.latent.get(obs_key)
        if not p:
            return
        
        if "probs" in p and isinstance(obs_value, str):
            # Categorical update - strongly trust observation
            for k in p["probs"]:
                p["probs"][k] = 0.99 if k == obs_value else 0.01 / (len(p["probs"]) - 1)
        
        elif "p" in p and isinstance(obs_value, bool):
            # Bernoulli update
            p["p"] = 0.9 if obs_value else 0.1
        
        elif {"alpha", "beta"} <= p.keys() and isinstance(obs_value, (int, float)):
            # Beta update with pseudo counts
            self.latent[obs_key]["alpha"] += obs_value * 2
            self.latent[obs_key]["beta"] += (1 - obs_value) * 2


class EarthlyIncompleteGame:
    """
    Main engine for the Earthly incomplete game system.
    Implements POMDP-lite core that stays JSON-driven.
    """
    
    def __init__(self, main_app, game_json: Dict[str, Any]):
        """
        Initialize the Earthly game engine.
        
        Args:
            main_app: Reference to main application
            game_json: Game configuration from JSON file
        """
        self.app = main_app
        self.cfg = game_json
        self.belief = BeliefState(game_json["beliefs"]["priors"])
        self.voi_threshold = game_json["beliefs"].get("voi_threshold", 0.05)
        self.weights = game_json["reward_model"]["needs"]
        self.setpoints = game_json["reward_model"]["homeostasis"]["setpoints"]
        self.curiosity = float(game_json["reward_model"].get("curiosity_bonus", 0.0))
        self.logger = logging.getLogger(__name__)
        
        # Initialize agent tracking for consciousness gaps
        self.inactive_agents = {}
        self.world_state = {"missed_rounds": {}}
        
        self.logger.info("🌍 Earthly Incomplete Game Engine initialized")
    
    def homeostatic_reward(self, need_levels: Dict[str, float]) -> float:
        """
        Calculate homeostatic reward based on need levels vs setpoints.
        
        Args:
            need_levels: Current need levels
            
        Returns:
            Reward value (positive when moving toward setpoint)
        """
        r = 0.0
        for k, w in self.weights.items():
            tgt = self.setpoints.get(k, 0.6)
            cur = need_levels.get(k, 0.5)
            r += w * (cur - tgt)
        
        # 🔧 FIX: Log game reasoning event for homeostatic reward calculation
        if abs(r) > 0.01:  # Only log if there's a meaningful reward
            self.log_game_reasoning_event('homeostatic_reward', {
                'description': f'Calculated homeostatic reward: {r:.3f}',
                'reward_value': r,
                'need_levels': need_levels
            })
        
        return r
    
    def value_of_information(self) -> List[Tuple[str, float]]:
        """
        Calculate value of information for each latent variable.
        
        Returns:
            List of (variable_name, voi_score) tuples sorted by VOI
        """
        out = []
        for key in self.cfg["beliefs"]["latent_vars"]:
            curH = self.belief.entropy(key)
            expH = self.belief.expected_entropy(key)
            out.append((key, max(0.0, curH - expH)))
        
        # 🔧 FIX: Log game reasoning event for value of information calculation
        if out and max(out, key=lambda x: x[1])[1] > 0.01:  # Only log if there's meaningful VOI
            top_voi = max(out, key=lambda x: x[1])
            self.log_game_reasoning_event('value_of_information', {
                'description': f'Calculated VOI for {top_voi[0]}: {top_voi[1]:.3f}',
                'top_variable': top_voi[0],
                'top_voi_score': top_voi[1],
                'all_voi_scores': out
            })
        
        return sorted(out, key=lambda x: x[1], reverse=True)
    
    def suggest_action(self, need_levels: Dict[str, float]) -> Dict[str, Any]:
        """
        Suggest next action based on current state and needs.
        
        Args:
            need_levels: Current need levels
            
        Returns:
            Dictionary with suggested action
        """
        # 1) Consider probes if VoI is significant
        voi = self.value_of_information()
        if voi and voi[0][1] >= self.voi_threshold:
            probe = self.cfg["actions"]["probe"][0]  # simplest: pick first defined probe
            
            # 🔧 FIX: Log game reasoning event for probe analysis
            self.log_game_reasoning_event('probe_analysis', {
                'description': f'Analyzing probe {probe["id"]} with VoI {voi[0][1]:.3f}',
                'voi_score': voi[0][1],
                'probe_id': probe["id"]
            })
            
            return {
                "type": "probe", 
                "action_id": probe["id"], 
                "obs": probe["obs"], 
                "info_gain": voi[0][1]
            }
        
        # 2) Otherwise pick a task that best improves deficit needs (greedy)
        deficits = {
            k: max(0.0, self.setpoints.get(k, 0.6) - need_levels.get(k, 0.5)) 
            for k in self.weights
        }
        target_need = max(deficits, key=deficits.get)
        tasks = [t for t in self.cfg["actions"]["task"] if t.get("need") == target_need]
        
        if tasks:
            t = max(tasks, key=lambda x: x.get("delta", 0))
            
            # 🔧 FIX: Log game reasoning event for task selection
            self.log_game_reasoning_event('task_execution', {
                'description': f'Selected task {t["id"]} for need {target_need}',
                'target_need': target_need,
                'task_id': t["id"],
                'delta': t.get("delta", 0)
            })
            
            return {
                "type": "task",
                "action_id": t["id"], 
                "need": target_need, 
                "delta": t.get("delta", 0)
            }
        
        # Fallback
        return {"type": "idle"}
    
    def apply_observation(self, obs_key: str, obs_value: Any):
        """
        Apply observation to update belief state.
        
        Args:
            obs_key: Key of the observed variable
            obs_value: Observed value
        """
        self.belief.update(obs_key, obs_value)
        self.logger.debug(f"🌍 Applied observation: {obs_key} = {obs_value}")
        
        # 🔧 FIX: Log game reasoning event for belief update
        self.log_game_reasoning_event('belief_update', {
            'description': f'Updated belief for {obs_key} with value {obs_value}',
            'obs_key': obs_key,
            'obs_value': obs_value
        })
    
    def get_belief_state(self) -> Dict[str, Any]:
        """
        Get current belief state for debugging/monitoring.
        
        Returns:
            Current belief state
        """
        return self.belief.latent.copy()
    
    def get_voi_scores(self) -> List[Tuple[str, float]]:
        """
        Get current value of information scores.
        
        Returns:
            List of (variable_name, voi_score) tuples
        """
        return self.value_of_information()
    
    def get_homeostatic_reward(self, need_levels: Dict[str, float]) -> float:
        """
        Get current homeostatic reward.
        
        Args:
            need_levels: Current need levels
            
        Returns:
            Homeostatic reward value
        """
        return self.homeostatic_reward(need_levels)
    
    def notify_agent_inactive(self, agent_name: str, reason: str):
        """Notify that an agent has become inactive (lost consciousness)."""
        try:
            import time
            self.inactive_agents[agent_name] = {
                "reason": reason, 
                "timestamp": time.time(),
                "missed_rounds": 0
            }
            self.logger.info(f"🌍 Agent {agent_name} marked as inactive: {reason}")
        except Exception as e:
            self.logger.error(f"❌ Error notifying agent inactivity: {e}")
    
    def register_agent_recovery(self, agent_name: str, elapsed_time: float):
        """Register that an agent has recovered from inactivity."""
        try:
            import time
            if agent_name in self.inactive_agents:
                # Calculate missed rounds based on elapsed time
                missed_rounds = int(elapsed_time / 10)  # Assume 10 seconds per round
                self.world_state["missed_rounds"][agent_name] = missed_rounds
                
                # Remove from inactive agents
                del self.inactive_agents[agent_name]
                
                self.logger.info(f"🌍 Agent {agent_name} recovered after {elapsed_time:.1f}s, missed {missed_rounds} rounds")
            else:
                self.logger.warning(f"🌍 Agent {agent_name} was not marked as inactive")
        except Exception as e:
            self.logger.error(f"❌ Error registering agent recovery: {e}")
    
    def get_unobserved_rounds(self, agent_name: str) -> int:
        """Get the number of unobserved rounds for an agent."""
        try:
            return self.world_state.get("missed_rounds", {}).get(agent_name, 0)
        except Exception as e:
            self.logger.error(f"❌ Error getting unobserved rounds: {e}")
            return 0
    
    def clear_unobserved_rounds(self, agent_name: str):
        """Clear the unobserved rounds for an agent."""
        try:
            if agent_name in self.world_state.get("missed_rounds", {}):
                self.world_state["missed_rounds"][agent_name] = 0
                self.logger.info(f"🌍 Cleared unobserved rounds for agent {agent_name}")
        except Exception as e:
            self.logger.error(f"❌ Error clearing unobserved rounds: {e}")
    
    def advance_time(self, elapsed_time: float):
        """Advance the game time and update world state."""
        try:
            # Update belief state based on elapsed time
            # This simulates the world continuing to evolve while the agent was unconscious
            for key in self.belief.latent:
                # Add some entropy to simulate uncertainty from missed time
                if "probs" in self.belief.latent[key]:
                    # Slightly randomize probabilities to simulate uncertainty
                    import random
                    for prob_key in self.belief.latent[key]["probs"]:
                        current_prob = self.belief.latent[key]["probs"][prob_key]
                        noise = (random.random() - 0.5) * 0.1  # ±5% noise
                        self.belief.latent[key]["probs"][prob_key] = max(0.01, min(0.99, current_prob + noise))
            
            self.logger.info(f"🌍 Advanced game time by {elapsed_time:.1f}s")
        except Exception as e:
            self.logger.error(f"❌ Error advancing time: {e}")
    
    def log_event(self, message: str):
        """Log an event to the game system."""
        try:
            self.logger.info(f"🌍 Game Event: {message}")
            
            # 🔧 FIX: Update consciousness evaluation Game Reasoning metrics
            if hasattr(self.app, 'consciousness_evaluation'):
                consciousness_eval = self.app.consciousness_evaluation
                if hasattr(consciousness_eval, 'increment_pdb_counter'):
                    consciousness_eval.increment_pdb_counter('game_reasoning', strength=1.0)
                    self.logger.info(f"🎮 Game Reasoning PDB counter updated")
        except Exception as e:
            self.logger.error(f"❌ Error logging event: {e}")
    
    def log_game_reasoning_event(self, event_type: str, context: Dict = None):
        """
        Log a specific game reasoning event to consciousness evaluation.
        
        Args:
            event_type: Type of game reasoning event (e.g., 'strategic_move', 'probe_analysis', 'task_execution')
            context: Additional context for the event
        """
        try:
            if not context:
                context = {}
            
            # Log to consciousness evaluation system
            if hasattr(self.app, 'consciousness_evaluation'):
                consciousness_eval = self.app.consciousness_evaluation
                if hasattr(consciousness_eval, 'increment_pdb_counter'):
                    # Calculate strength based on event type
                    strength_map = {
                        'strategic_move': 2.0,
                        'probe_analysis': 1.5,
                        'task_execution': 1.0,
                        'homeostatic_reward': 1.5,
                        'value_of_information': 2.0,
                        'belief_update': 1.0
                    }
                    strength = strength_map.get(event_type, 1.0)
                    
                    consciousness_eval.increment_pdb_counter('game_reasoning', strength=strength)
                    self.logger.info(f"🎮 Game Reasoning event logged: {event_type} (strength: {strength})")
            
            # Also log to episodic memory if available
            if hasattr(self.app, 'inner_self'):
                self.app.inner_self.add_thought(
                    f"Game reasoning: {event_type} - {context.get('description', 'Strategic analysis')}"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error logging game reasoning event: {e}")
