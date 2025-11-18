#!/usr/bin/env python3
"""
CARL Imagination GUI System

This module provides a GUI interface for CARL's imagination system,
displaying DALL-E generated images and real-time imagination states.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
from PIL import Image, ImageTk
import json
from datetime import datetime
from typing import Optional, Dict, Any
import logging

class ImaginationGUI(tk.Frame):
    """GUI component for CARL's imagination system."""
    
    def __init__(self, parent_frame, imagination_system, neucogar_engine, enhanced_imagination_system=None):
        # Initialize as tk.Frame
        super().__init__(parent_frame)
        
        # Store parent reference for after() calls
        self.root_parent = parent_frame
        """
        Initialize the imagination GUI.
        
        Args:
            parent_frame: Parent tkinter frame
            imagination_system: CARL's imagination system
            neucogar_engine: NEUCOGAR emotional engine
        """
        self.parent_frame = parent_frame
        self.imagination_system = imagination_system
        self.enhanced_imagination_system = enhanced_imagination_system
        self.neucogar_engine = neucogar_engine
        self.logger = logging.getLogger(__name__)
        
        # GUI state
        self.current_image = None
        self.image_label = None
        self.status_label = None
        self.imagination_text = None
        self.episode_list = None
        self.is_generating = False
        
        # Create GUI components
        self._create_widgets()
        
        # Don't start update thread immediately - wait for GUI to be ready
        self.update_thread = None
        self.update_active = False
    
    def _create_widgets(self):
        """Create and arrange GUI widgets."""
        # 🔧 FIX 6: GUI ADJUSTMENT - Make imagination panel more compact
        # Main imagination frame - COMPACT
        imagination_frame = ttk.LabelFrame(self.parent_frame, text="🧠 CARL's Imagination", padding="3")
        imagination_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Configure grid weights for larger panel
        self.parent_frame.grid_rowconfigure(0, weight=1)
        self.parent_frame.grid_columnconfigure(0, weight=1)
        imagination_frame.grid_rowconfigure(0, weight=1)
        imagination_frame.grid_rowconfigure(1, weight=1)  # Add second row for better height distribution
        imagination_frame.grid_columnconfigure(0, weight=1)
        imagination_frame.grid_columnconfigure(1, weight=1)
        
        # Left panel - Image display
        left_panel = ttk.Frame(imagination_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        # Image display area
        image_frame = ttk.LabelFrame(left_panel, text="Generated Imagination", padding="4")
        image_frame.pack(fill="both", expand=True)
        
        # Image label
        self.image_label = ttk.Label(image_frame, text="No image generated yet", 
                                    background="white", relief="sunken", borderwidth=2)
        self.image_label.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Image controls
        image_controls = ttk.Frame(image_frame)
        image_controls.pack(fill="x", pady=(4, 0))
        
        ttk.Button(image_controls, text="Generate", 
                  command=self._generate_new_image).pack(side="left", padx=(0, 3))
        ttk.Button(image_controls, text="Refresh", 
                  command=self._refresh_image).pack(side="left", padx=(0, 3))
        
        # Right panel - Imagination details
        right_panel = ttk.Frame(imagination_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        # Status and controls
        status_frame = ttk.LabelFrame(right_panel, text="Imagination Status", padding="2")
        status_frame.pack(fill="x", pady=(0, 2))
        
        self.status_label = ttk.Label(status_frame, text="Ready to imagine...", 
                                     font=("Arial", 10, "bold"))
        self.status_label.pack(fill="x")
        
        # Imagination controls
        controls_frame = ttk.Frame(status_frame)
        controls_frame.pack(fill="x", pady=(4, 0))
        
        ttk.Label(controls_frame, text="Seed Concept:").pack(anchor="w")
        self.seed_entry = ttk.Entry(controls_frame, width=30)
        self.seed_entry.pack(fill="x", pady=(2, 4))
        self.seed_entry.insert(0, "a friendly robot and human interaction")
        
        ttk.Label(controls_frame, text="Purpose:").pack(anchor="w")
        self.purpose_combo = ttk.Combobox(controls_frame, width=30, state="readonly")
        self.purpose_combo['values'] = [
            "plan-social-interaction",
            "explore-scenario", 
            "counterfactual",
            "creative-expression",
            "problem-solving",
            "memory-reconstruction"
        ]
        self.purpose_combo.set("explore-scenario")
        self.purpose_combo.pack(fill="x", pady=(2, 4))
        
        ttk.Button(controls_frame, text="Imagine!", 
                  command=self._trigger_imagination).pack(fill="x", pady=(2, 0))  # Compact spacing
        
        # Imagination details
        details_frame = ttk.LabelFrame(right_panel, text="Current Imagination", padding="2")  # Compact padding
        details_frame.pack(fill="both", expand=True)
        
        # Imagination text display
        self.imagination_text = tk.Text(details_frame, height=3, width=40, wrap="word")  # Compact height
        imagination_scroll = ttk.Scrollbar(details_frame, orient="vertical", command=self.imagination_text.yview)
        self.imagination_text.configure(yscrollcommand=imagination_scroll.set)
        
        self.imagination_text.pack(side="left", fill="both", expand=True, padx=2, pady=2)  # Compact padding
        imagination_scroll.pack(side="right", fill="y", pady=2)  # Compact padding
        
        # Recent episodes
        episodes_frame = ttk.LabelFrame(right_panel, text="Recent Episodes", padding="2")  # Compact padding
        episodes_frame.pack(fill="x", pady=(2, 0))  # Compact spacing
        
        # Episode listbox
        self.episode_list = tk.Listbox(episodes_frame, height=1)  # Compact height
        episode_scroll = ttk.Scrollbar(episodes_frame, orient="vertical", command=self.episode_list.yview)
        self.episode_list.configure(yscrollcommand=episode_scroll.set)
        
        # Add double-click handler for convenience
        self.episode_list.bind("<Double-Button-1>", lambda event: self._load_episode())
        
        self.episode_list.pack(side="left", fill="both", expand=True, padx=3, pady=3)  # Increased padding from 1 to 3
        episode_scroll.pack(side="right", fill="y", pady=3)  # Increased padding from 1 to 3
        
        # Episode controls - Vertical layout with Refresh under Load
        episode_controls = ttk.Frame(episodes_frame)
        episode_controls.pack(fill="x", pady=(3, 0))  # Increased pady from 1 to 3 for better spacing
        
        ttk.Button(episode_controls, text="Load", 
                  command=self._load_episode).pack(fill="x", pady=(0, 2))  # Load button on top
        ttk.Button(episode_controls, text="Refresh", 
                  command=self._refresh_episodes).pack(fill="x")  # Refresh button directly under Load
        
        
        # Initialize the imagination text with default content
        self._initialize_imagination_text()
        
        # Set up auto-update for purpose dropdown
        self._setup_purpose_auto_update()
        
        # Refresh episodes list on startup
        self._refresh_episodes()
    
    def _initialize_imagination_text(self):
        """Initialize the imagination textbox with default content."""
        try:
            # Clear any existing content
            self.imagination_text.delete(1.0, tk.END)
            
            # Try to load the most recent episode
            episodes = self.imagination_system.get_imagined_episodes(limit=1)
            
            if episodes:
                # Load the most recent episode
                latest_episode = episodes[0]
                self._update_with_episode_data(latest_episode)
                self.logger.info("Initialized imagination text with most recent episode")
            else:
                # Show default welcome message
                default_text = """Welcome to CARL's Imagination System!

This is where CARL's mental imagery and creative thoughts are displayed.

To get started:
1. Enter a seed concept in the text field above
2. Select a purpose for your imagination
3. Click "Imagine!" to generate new mental imagery

CARL can imagine:
• Social interactions and scenarios
• Problem-solving situations
• Creative expressions
• Memory reconstructions
• Counterfactual scenarios

The system will display both visual imagery and detailed descriptions of CARL's imagined scenarios.

Ready to explore CARL's inner world? 🧠✨"""
                
                self.imagination_text.insert(1.0, default_text)
                self.logger.info("Initialized imagination text with default welcome message")
                
        except Exception as e:
            self.logger.error(f"Error initializing imagination text: {e}")
            # Fallback to simple message
            self.imagination_text.insert(1.0, "Welcome to CARL's Imagination System!\n\nEnter a seed concept and click 'Imagine!' to get started.")
    
    def update_seed_concept_from_thought(self, automatic_thought: str):
        """
        Update the seed concept textbox based on CARL's automatic thought.
        
        Args:
            automatic_thought: The automatic thought content to use as seed concept
        """
        try:
            if not automatic_thought or len(automatic_thought.strip()) == 0:
                return
            
            # Extract key concepts from the automatic thought
            seed_concept = self._extract_seed_concept_from_thought(automatic_thought)
            
            # Update the seed entry in the main thread
            self.parent_frame.after(0, self._update_seed_entry, seed_concept)
            
            self.logger.info(f"Updated seed concept from automatic thought: {seed_concept[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Error updating seed concept from thought: {e}")
    
    def _extract_seed_concept_from_thought(self, automatic_thought: str) -> str:
        """
        Extract a meaningful seed concept from an automatic thought.
        
        Args:
            automatic_thought: The automatic thought content
            
        Returns:
            Extracted seed concept string
        """
        try:
            # Clean the thought text
            thought = automatic_thought.strip()
            
            # If thought is too long, truncate it
            if len(thought) > 100:
                thought = thought[:97] + "..."
            
            # Remove common prefixes that don't add value to imagination
            prefixes_to_remove = [
                "I think", "I feel", "I wonder", "I should", "I need to",
                "Joe is", "User is", "I understand", "I'm excited",
                "I'm intrigued", "I'm curious", "I want to"
            ]
            
            for prefix in prefixes_to_remove:
                if thought.lower().startswith(prefix.lower()):
                    thought = thought[len(prefix):].strip()
                    break
            
            # If the thought is still too long, take the first sentence
            if len(thought) > 80:
                sentences = thought.split('.')
                if sentences:
                    thought = sentences[0].strip()
            
            # Ensure we have a meaningful concept
            if len(thought) < 10:
                thought = "a friendly robot and human interaction"
            
            return thought
            
        except Exception as e:
            self.logger.error(f"Error extracting seed concept: {e}")
            return "a friendly robot and human interaction"
    
    def _update_seed_entry(self, seed_concept: str):
        """Update the seed entry widget with new concept."""
        try:
            # Clear current content
            self.seed_entry.delete(0, tk.END)
            # Insert new concept
            self.seed_entry.insert(0, seed_concept)
            
        except Exception as e:
            self.logger.error(f"Error updating seed entry: {e}")
    
    def _setup_purpose_auto_update(self):
        """Set up automatic updates for the purpose dropdown based on context."""
        try:
            # Auto-update purpose based on current context
            self._update_purpose_based_on_context()
            
            # Set up periodic updates (every 30 seconds)
            self.after(30000, self._setup_purpose_auto_update)
            
        except Exception as e:
            self.logger.error(f"Error setting up purpose auto-update: {e}")
    
    def _update_purpose_based_on_context(self):
        """Update the purpose dropdown based on current context and recent interactions."""
        try:
            # Get current context from main app if available
            if hasattr(self, 'main_app') and self.main_app:
                # Check recent interactions to determine appropriate purpose
                recent_context = self._get_recent_context()
                
                # Map context to appropriate purpose
                purpose_mapping = {
                    'social': 'plan-social-interaction',
                    'problem': 'problem-solving',
                    'creative': 'creative-expression',
                    'memory': 'memory-reconstruction',
                    'scenario': 'explore-scenario',
                    'what-if': 'counterfactual',
                    'explore': 'explore-scenario',
                    'plan': 'plan-social-interaction',
                    'rehearse': 'memory-reconstruction',
                    'create': 'creative-expression'
                }
                
                # Determine purpose based on context
                if recent_context:
                    for context_key, purpose in purpose_mapping.items():
                        if context_key in recent_context.lower():
                            self.purpose_combo.set(purpose)
                            self.logger.info(f"Auto-updated purpose to: {purpose} based on context: {recent_context}")
                            return
                
                # Default to explore-scenario if no specific context detected
                self.purpose_combo.set('explore-scenario')
                
        except Exception as e:
            self.logger.error(f"Error updating purpose based on context: {e}")
    
    def update_purpose_from_autonomous_lookup(self, lookup_context: str):
        """
        Update the purpose dropdown when an autonomous lookup occurs.
        
        Args:
            lookup_context: Context of the autonomous lookup
        """
        try:
            # Map lookup context to appropriate purpose
            purpose_mapping = {
                'explore': 'explore-scenario',
                'plan': 'plan-social-interaction',
                'rehearse': 'memory-reconstruction',
                'create': 'creative-expression',
                'problem': 'problem-solving',
                'social': 'plan-social-interaction',
                'memory': 'memory-reconstruction',
                'what-if': 'counterfactual'
            }
            
            # Determine purpose based on lookup context
            for context_key, purpose in purpose_mapping.items():
                if context_key in lookup_context.lower():
                    self.purpose_combo.set(purpose)
                    self.logger.info(f"Auto-updated purpose to: {purpose} from autonomous lookup: {lookup_context}")
                    return
            
            # Default to explore-scenario if no specific context detected
            self.purpose_combo.set('explore-scenario')
            
        except Exception as e:
            self.logger.error(f"Error updating purpose from autonomous lookup: {e}")
    
    def _get_recent_context(self):
        """Get recent context from main app to determine appropriate purpose."""
        try:
            if hasattr(self, 'main_app') and self.main_app:
                # Check recent short-term memory for context clues
                if hasattr(self.main_app, 'short_term_memory') and self.main_app.short_term_memory:
                    recent_memories = self.main_app.short_term_memory[-3:]  # Last 3 memories
                    context_text = " ".join([str(mem.get('summary', '')) for mem in recent_memories])
                    return context_text
                
                # Check current emotional state
                if hasattr(self.main_app, 'neucogar_engine') and self.main_app.neucogar_engine:
                    current_emotion = self.main_app.neucogar_engine.current_state.primary
                    return f"current emotion: {current_emotion}"
                    
        except Exception as e:
            self.logger.error(f"Error getting recent context: {e}")
        
        return "explore-scenario"
    
    def _generate_new_image(self):
        """Generate a new imagination image."""
        if self.is_generating:
            messagebox.showwarning("Generation in Progress", "Please wait for current generation to complete.")
            return
        
        seed = self.seed_entry.get().strip()
        if not seed:
            messagebox.showerror("Error", "Please enter a seed concept.")
            return
        
        purpose = self.purpose_combo.get()
        
        # Start generation in background thread
        self.is_generating = True
        self.status_label.config(text="Generating imagination...")
        
        # Set mouse pointer to waiting state
        self.parent_frame.config(cursor="wait")
        
        # Start status monitoring for EnhancedImaginationSystem
        self._start_dalle_status_monitoring()
        
        # Send status notification to Output
        self._send_output_notification("🎭 Starting imagination generation...", "info")
        
        thread = threading.Thread(target=self._generate_image_thread, args=(seed, purpose), daemon=True)
        thread.start()
    
    def _generate_image_thread(self, seed: str, purpose: str):
        """Generate image in background thread."""
        try:
            self.logger.info(f"Starting imagination generation: {seed} for {purpose}")
            
            # Create constraints based on current emotional state
            constraints = self._get_emotional_constraints()
            
            # Generate imagined episode
            episode = self.imagination_system.imagine(seed, purpose, constraints)
            
            # Update GUI in main thread
            self.root_parent.after(0, self._update_with_episode, episode)
            
        except Exception as e:
            self.logger.error(f"Imagination generation failed: {e}")
            self.root_parent.after(0, self._show_error, f"Generation failed: {e}")
        finally:
            self.root_parent.after(0, self._set_generating_false)
    
    def _get_emotional_constraints(self) -> Dict[str, Any]:
        """Get emotional constraints based on current NEUCOGAR state."""
        try:
            current_emotion = self.neucogar_engine.get_current_emotion()
            neuro_coords = current_emotion.get("neuro_coordinates", {})
            
            constraints = {
                "mood": current_emotion.get("primary", "neutral"),
                "intensity": current_emotion.get("intensity", 0.5),
                "dopamine_level": neuro_coords.get("dopamine", 0.0),
                "serotonin_level": neuro_coords.get("serotonin", 0.0),
                "noradrenaline_level": neuro_coords.get("noradrenaline", 0.0)
            }
            
            # Add time and weather based on mood
            if current_emotion.get("primary") == "joy":
                constraints["lighting"] = "warm, golden hour"
                constraints["weather"] = "clear, pleasant"
            elif current_emotion.get("primary") == "sadness":
                constraints["lighting"] = "soft, diffused"
                constraints["weather"] = "overcast, gentle"
            elif current_emotion.get("primary") == "fear":
                constraints["lighting"] = "dramatic, high contrast"
                constraints["weather"] = "stormy, intense"
            else:
                constraints["lighting"] = "natural, balanced"
                constraints["weather"] = "clear, moderate"
            
            return constraints
            
        except Exception as e:
            self.logger.warning(f"Could not get emotional constraints: {e}")
            return {"mood": "neutral", "lighting": "natural", "weather": "clear"}
    
    def _update_with_episode(self, episode):
        """Update GUI with generated episode."""
        try:
            # Update status
            self.status_label.config(text=f"Generated: {episode.episode_id}")
            
            # Update imagination text
            self.imagination_text.delete(1.0, tk.END)
            
            episode_info = f"""Episode ID: {episode.episode_id}
Generated: {episode.timestamp}
Seed: {episode.request.seed}
Purpose: {episode.request.purpose}

Scene Description:
- Primary Emotion: {episode.scene_graph.affect.get('dominant', 'neutral')}
- Valence: {episode.scene_graph.affect.get('valence', 0.5):.2f}
- Arousal: {episode.scene_graph.affect.get('arousal', 0.4):.2f}

Objects: {len(episode.scene_graph.objects)}
Relations: {len(episode.scene_graph.relations)}

Scores:
- Coherence: {episode.coherence_score:.2f}
- Plausibility: {episode.plausibility_score:.2f}
- Novelty: {episode.novelty_score:.2f}
- Utility: {episode.utility_score:.2f}
- Vividness: {episode.vividness_score:.2f}
- Affect Alignment: {episode.affect_alignment:.2f}

Details: {episode.scene_graph.details}
Context: {episode.scene_graph.context}
"""
            
            self.imagination_text.insert(1.0, episode_info)
            
            # Update image if available
            if episode.render_data and episode.render_data.get("path"):
                self._load_image(episode.render_data["path"])
            
            # Refresh episode list
            self._refresh_episodes()
            
            
        except Exception as e:
            self.logger.error(f"Could not update GUI with episode: {e}")
    
    def _load_image(self, image_path: str):
        """Load and display image."""
        try:
            if os.path.exists(image_path):
                # Load and resize image
                image = Image.open(image_path)
                
                # Calculate resize dimensions (max 400x400)
                max_size = (400, 400)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image)
                
                # Update image label
                self.image_label.config(image=photo, text="")
                self.current_image = photo  # Keep reference
                
                self.logger.info(f"Loaded imagination image: {image_path}")
            else:
                self.image_label.config(image="", text="Image file not found")
                
        except Exception as e:
            self.logger.error(f"Could not load image {image_path}: {e}")
            self.image_label.config(image="", text="Error loading image")
    
    def _display_image(self, image_path: str, episode_data: Optional[Dict[str, Any]] = None):
        """Display image and update GUI with episode data."""
        try:
            # Load and display the image
            self._load_image(image_path)
            
            # Update status
            if episode_data and isinstance(episode_data, dict):
                episode_id = episode_data.get("id", "unknown")
                self.status_label.config(text=f"Displaying: {episode_id}")
                
                # Update imagination text with episode details
                if hasattr(self, 'imagination_text') and self.imagination_text:
                    self.imagination_text.delete(1.0, tk.END)
                    
                    info_text = f"""Episode: {episode_id}
Generated: {episode_data.get('timestamp', 'unknown')}
What: {episode_data.get('WHAT', 'No description')}
Where: {episode_data.get('WHERE', 'Unknown location')}
Why: {episode_data.get('WHY', 'No purpose specified')}

Emotional State:
{json.dumps(episode_data.get('neucogar_emotional_state', {}), indent=2)}

Scores:
{json.dumps(episode_data.get('scores', {}), indent=2)}
"""
                    
                    self.imagination_text.insert(1.0, info_text)
            else:
                self.status_label.config(text="Image displayed")
            
            self.logger.info(f"Displayed imagination image: {image_path}")
            
        except Exception as e:
            self.logger.error(f"Could not display image {image_path}: {e}")
            self.status_label.config(text=f"Error displaying image: {e}")
    
    def _refresh_image(self):
        """Refresh the current image display."""
        try:
            # Get most recent episode with image
            episodes = self.imagination_system.get_imagined_episodes(limit=5)
            
            for episode in episodes:
                if episode.get("render_data") and episode["render_data"].get("path"):
                    self._load_image(episode["render_data"]["path"])
                    break
            else:
                self.image_label.config(image="", text="No recent images found")
                
        except Exception as e:
            self.logger.error(f"Could not refresh image: {e}")
    
    def _trigger_imagination(self):
        """Trigger imagination with current settings."""
        self._generate_new_image()
    
    def _load_episode(self):
        """Load selected episode."""
        try:
            selection = self.episode_list.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an episode to load.")
                return
            
            # Get episode ID from selection (first part before " - ")
            selected_text = self.episode_list.get(selection[0])
            episode_id = selected_text.split(" - ")[0]
            
            self.logger.info(f"Loading episode: {episode_id}")
            
            # Load episode details
            episodes = self.imagination_system.get_imagined_episodes(limit=50)
            for episode_data in episodes:
                # Check multiple possible ID fields
                episode_data_id = (episode_data.get("episode_id") or 
                                 episode_data.get("id") or 
                                 episode_data.get("WHAT", "").replace("Episode: ", "").strip())
                
                if episode_data_id == episode_id or episode_id in episode_data_id:
                    self._update_with_episode_data(episode_data)
                    self.logger.info(f"Successfully loaded episode: {episode_id}")
                    return
            
            # If no exact match found, try partial matching
            for episode_data in episodes:
                episode_data_id = (episode_data.get("episode_id") or 
                                 episode_data.get("id") or 
                                 episode_data.get("WHAT", ""))
                
                if episode_id.lower() in str(episode_data_id).lower():
                    self._update_with_episode_data(episode_data)
                    self.logger.info(f"Successfully loaded episode with partial match: {episode_id}")
                    return
            
            messagebox.showerror("Error", f"Could not find episode with ID: {episode_id}")
                
        except Exception as e:
            self.logger.error(f"Could not load episode: {e}")
            messagebox.showerror("Error", f"Could not load episode: {e}")
    
    def _refresh_episodes(self):
        """Refresh the episode list."""
        try:
            self.episode_list.delete(0, tk.END)
            
            episodes = self.imagination_system.get_imagined_episodes(limit=20)
            
            for episode in episodes:
                # Try different possible ID fields
                episode_id = (episode.get("episode_id") or 
                            episode.get("id") or 
                            episode.get("WHAT", "").replace("Episode: ", "").split("\n")[0].strip() or
                            "unknown")
                
                # Try different possible timestamp fields
                timestamp = (episode.get("timestamp") or 
                           episode.get("created_at") or 
                           episode.get("WHEN", "") or
                           "")
                
                # Try different possible seed fields
                seed = (episode.get("seed") or
                       episode.get("WHAT", "").replace("Imagined scenario: ", "") or
                       episode.get("request", {}).get("seed", "") if isinstance(episode.get("request"), dict) else "" or
                       "No description")
                
                # Format timestamp
                try:
                    if timestamp:
                        # Handle different timestamp formats
                        if 'T' in timestamp:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        else:
                            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                        time_str = dt.strftime("%m/%d %H:%M")
                    else:
                        time_str = "unknown"
                except Exception as ts_error:
                    self.logger.debug(f"Error parsing timestamp '{timestamp}': {ts_error}")
                    time_str = "unknown"
                
                # Truncate long seeds for display
                display_seed = seed[:30] + ("..." if len(seed) > 30 else "")
                
                display_text = f"{episode_id} - {time_str} - {display_seed}"
                self.episode_list.insert(tk.END, display_text)
                
            if not episodes:
                self.episode_list.insert(tk.END, "No episodes found")
                
        except Exception as e:
            self.logger.error(f"Could not refresh episodes: {e}")
            self.episode_list.insert(tk.END, "Error loading episodes")
    
    def _show_error(self, message: str):
        """Show error message."""
        self.status_label.config(text=f"Error: {message}")
        messagebox.showerror("Imagination Error", message)
    
    def _start_dalle_status_monitoring(self):
        """Start monitoring DALL-E status from EnhancedImaginationSystem."""
        def monitor_status():
            try:
                # Check if we have access to enhanced imagination system
                if hasattr(self, 'enhanced_imagination_system') and self.enhanced_imagination_system:
                    # Check for current session in enhanced system
                    if hasattr(self.enhanced_imagination_system, 'current_session'):
                        session = self.enhanced_imagination_system.current_session
                        if session and hasattr(session, 'dall_e_status'):
                            status = session.dall_e_status
                            if status and status != "Not started":
                                # Update status label with DALL-E status
                                self._safe_gui_update(self.status_label, text=f"DALL-E Status: {status}")
                                
                                # If generation is complete, stop monitoring
                                if status in ["Success", "Failed"]:
                                    return
                
                # Continue monitoring if still generating
                if self.is_generating:
                    self.root_parent.after(1000, monitor_status)  # Check every second
                    
            except Exception as e:
                self.logger.error(f"Error monitoring DALL-E status: {e}")
        
        # Start monitoring
        self.root_parent.after(1000, monitor_status)
    
    def _set_generating_false(self):
        """Set generating flag to false and restore UI state."""
        self.is_generating = False
        
        # Restore mouse pointer to default
        self.parent_frame.config(cursor="")
        
        # Send completion notification to Output
        self._send_output_notification("✅ Imagination generation completed!", "success")
    
    def start_update_thread(self):
        """Start the update thread when GUI is ready."""
        if not self.update_active:
            self.update_active = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            self.logger.info("Imagination GUI update thread started")
    
    def _send_output_notification(self, message: str, level: str = "info"):
        """
        Send notification to the Output section.
        
        Args:
            message: Message to display
            level: Message level (info, success, warning, error)
        """
        try:
            # Try to find the main output widget
            root = self.parent_frame.winfo_toplevel()
            
            # Look for output-related widgets in the main window
            for widget in root.winfo_children():
                if hasattr(widget, 'winfo_children'):
                    for child in widget.winfo_children():
                        if hasattr(child, 'winfo_children'):
                            for grandchild in child.winfo_children():
                                # Look for text widgets that might be the output
                                if isinstance(grandchild, tk.Text) and 'output' in str(grandchild).lower():
                                    # Add timestamp and message
                                    timestamp = datetime.now().strftime("%H:%M:%S")
                                    level_icon = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}.get(level, "ℹ️")
                                    formatted_message = f"[{timestamp}] {level_icon} {message}\n"
                                    
                                    # Insert at the end
                                    grandchild.insert(tk.END, formatted_message)
                                    grandchild.see(tk.END)
                                    return
                                
        except Exception as e:
            self.logger.warning(f"Could not send output notification: {e}")
            # Fallback: just log it
            self.logger.info(f"Output notification: {message}")
    
    def _safe_gui_update(self, widget, **kwargs):
        """Safely update GUI elements from any thread."""
        try:
            if widget and widget.winfo_exists():
                widget.after(0, lambda: widget.config(**kwargs))
        except Exception as e:
            self.logger.error(f"Error updating GUI: {e}")
    
    def _update_loop(self):
        """Background update loop."""
        while self.update_active:
            try:
                # Update status based on current state
                if hasattr(self.imagination_system, 'neucogar_engine'):
                    current_emotion = self.neucogar_engine.get_current_emotion()
                    emotion_text = f"Current mood: {current_emotion.get('primary', 'neutral')}"
                    
                    # Update in main thread safely
                    self._safe_gui_update(self.status_label, text=emotion_text)
                
                # Sleep for a bit
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                time.sleep(10)
    
    def update_imagination_state(self, episode_data: Dict[str, Any]):
        """Update GUI with new imagination state (called from main system)."""
        try:
            # Update in main thread safely
            if self.parent_frame and self.parent_frame.winfo_exists():
                self.parent_frame.after(0, lambda: self._update_with_episode_data(episode_data))
        except Exception as e:
            self.logger.error(f"Could not update imagination state: {e}")
    
    def _update_with_episode_data(self, episode_data: Dict[str, Any]):
        """Update GUI with episode data."""
        try:
            # Get episode ID from multiple possible fields
            episode_id = (episode_data.get("episode_id") or 
                         episode_data.get("id") or 
                         episode_data.get("WHAT", "").split("\n")[0].strip() or
                         "unknown")
            
            # Update status
            self.status_label.config(text=f"Loaded: {episode_id}")
            
            # Update imagination text
            self.imagination_text.delete(1.0, tk.END)
            
            # Get various fields with fallbacks
            timestamp = (episode_data.get('timestamp') or 
                        episode_data.get('created_at') or 
                        episode_data.get('WHEN', 'unknown'))
            
            what = episode_data.get('WHAT', 'No description available')
            where = episode_data.get('WHERE', 'Unknown location')
            why = episode_data.get('WHY', 'No purpose specified')
            
            # Format emotional state more readably
            emotional_state = episode_data.get('neucogar_emotional_state', {})
            if emotional_state:
                emotion_text = f"Primary: {emotional_state.get('primary', 'neutral')}"
                if 'intensity' in emotional_state:
                    emotion_text += f" (intensity: {emotional_state.get('intensity', 0):.2f})"
                if 'neuro_coordinates' in emotional_state:
                    neuro = emotional_state['neuro_coordinates']
                    emotion_text += f"\nNeurotransmitters: DA:{neuro.get('dopamine', 0):.2f}, 5HT:{neuro.get('serotonin', 0):.2f}, NE:{neuro.get('noradrenaline', 0):.2f}"
            else:
                emotion_text = "No emotional data"
            
            # Format scores more readably
            scores = episode_data.get('scores', {})
            if scores:
                score_text = ", ".join([f"{k}: {v:.2f}" if isinstance(v, (int, float)) else f"{k}: {v}" 
                                      for k, v in scores.items()])
            else:
                score_text = "No scores available"
            
            # Check for additional fields
            seed = (episode_data.get('seed') or 
                   episode_data.get('request', {}).get('seed', '') if isinstance(episode_data.get('request'), dict) else '')
            purpose = (episode_data.get('purpose') or 
                      episode_data.get('request', {}).get('purpose', '') if isinstance(episode_data.get('request'), dict) else '')
            
            info_text = f"""🎭 IMAGINATION EPISODE 🎭

Episode ID: {episode_id}
Generated: {timestamp}

🎯 CONTEXT:
What: {what}
Where: {where}
Why: {why}"""

            if seed:
                info_text += f"\nSeed Concept: {seed}"
            if purpose:
                info_text += f"\nPurpose: {purpose}"

            info_text += f"""

😊 EMOTIONAL STATE:
{emotion_text}

📊 QUALITY SCORES:
{score_text}

💡 STATUS: Episode loaded successfully"""
            
            self.imagination_text.insert(1.0, info_text)
            
            # Update image if available
            render_data = episode_data.get("render_data")
            image_path = None
            
            if render_data:
                if isinstance(render_data, dict):
                    image_path = render_data.get("path")
                elif isinstance(render_data, str):
                    image_path = render_data
            
            # Also check for direct image path
            if not image_path:
                image_path = episode_data.get("image_path")
            
            if image_path and os.path.exists(image_path):
                self._load_image(image_path)
            else:
                # Clear previous image
                self.image_label.config(text="Imagination is online! No image generated for this episode.", image="")
                self.current_image = None
            
            # Update seed entry with the episode's seed if available
            if seed and hasattr(self, 'seed_entry'):
                self.seed_entry.delete(0, tk.END)
                self.seed_entry.insert(0, seed)
            
            # Update purpose combo if available
            if purpose and hasattr(self, 'purpose_combo'):
                # Try to set the purpose in the combo box
                try:
                    self.purpose_combo.set(purpose)
                except:
                    pass  # Purpose might not be in the list
            
            
        except Exception as e:
            self.logger.error(f"Could not update with episode data: {e}")
            # Show error in the text area
            self.imagination_text.delete(1.0, tk.END)
            self.imagination_text.insert(1.0, f"Error loading episode data: {e}\n\nRaw data:\n{json.dumps(episode_data, indent=2)[:500]}...")

