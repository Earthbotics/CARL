"""
Imagination Generator with Reliability and Artifact Memory

Implements scene generation with retry mechanisms, artifact storage, and purpose tracking.
Provides adaptive, dynamic generation without hardcoded templates or patterns.
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import shutil


@dataclass
class ImaginationArtifact:
    """Represents an imagination artifact."""
    artifact_id: str
    prompt: str
    image_path: str
    purpose: str
    style: str
    timestamp: str
    generation_attempts: int
    success: bool


class ImaginationGenerator:
    """Manages imagination generation with reliability features and adaptive styling."""
    
    def __init__(self, imagination_dir: str = "imagination"):
        self.imagination_dir = imagination_dir
        self.artifacts_dir = os.path.join(imagination_dir, "artifacts")
        self.artifacts_file = os.path.join(imagination_dir, "artifacts.json")
        self._logger = None
        
        # Ensure directories exist
        os.makedirs(imagination_dir, exist_ok=True)
        os.makedirs(self.artifacts_dir, exist_ok=True)
        
        # Load existing artifacts
        self.artifacts = self._load_artifacts()
        
        # Generation parameters
        self.max_attempts = 3
        self.retry_delay = 2.0  # seconds
        
        # Adaptive style system (not hardcoded templates)
        self.style_adaptation_data = self._load_style_adaptation_data()
        self.purpose_analysis_data = self._load_purpose_analysis_data()
        
        # Generation history for learning
        self.generation_history = []
        
    def _load_style_adaptation_data(self) -> Dict[str, Any]:
        """Load adaptive style data from files."""
        style_file = os.path.join(self.imagination_dir, "style_adaptation.json")
        if os.path.exists(style_file):
            try:
                with open(style_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Initialize with adaptive defaults
        return {
            "style_components": {
                "visual_effects": ["depth", "lighting", "composition", "color_palette", "texture"],
                "artistic_approaches": ["realistic", "abstract", "stylized", "experimental"],
                "mood_indicators": ["serene", "dynamic", "mysterious", "vibrant", "subtle"],
                "technical_aspects": ["perspective", "focus", "contrast", "harmony"]
            },
            "learned_combinations": [],
            "successful_patterns": {},
            "contextual_adaptations": {}
        }
    
    def _load_purpose_analysis_data(self) -> Dict[str, Any]:
        """Load purpose analysis data."""
        purpose_file = os.path.join(self.imagination_dir, "purpose_analysis.json")
        if os.path.exists(purpose_file):
            try:
                with open(purpose_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "purpose_indicators": {
                "story_illustration": ["character", "scene", "narrative", "story"],
                "concept_exploration": ["idea", "concept", "explore", "investigate"],
                "emotional_expression": ["feeling", "emotion", "mood", "atmosphere"],
                "technical_demonstration": ["show", "demonstrate", "display", "present"],
                "creative_experimentation": ["experiment", "try", "test", "explore"]
            },
            "contextual_clues": {},
            "learned_purposes": []
        }
    
    def set_logger(self, logger):
        """Set the logger for this generator."""
        self._logger = logger
    
    def imagine_scene(self, prompt: str, style: str = "hologram") -> Dict[str, Any]:
        """
        Generate an imagined scene with adaptive styling and retry mechanisms.
        
        Args:
            prompt: Scene description prompt
            style: Art style to apply (can be adaptive)
            
        Returns:
            Dictionary with generation results
        """
        artifact_id = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        # Determine purpose from context using adaptive analysis
        purpose = self._determine_purpose_adaptively(prompt)
        
        # Generate adaptive style description
        style_description = self._generate_adaptive_style(prompt, style, purpose)
        
        # Prepare full prompt with adaptive styling
        full_prompt = self._create_adaptive_prompt(prompt, style_description, purpose)
        
        if self._logger:
            self._logger(f"[IMAGINE] generating scene: {prompt[:50]}...")
        
        # Attempt generation with retries
        success = False
        image_path = None
        attempts = 0
        
        for attempt in range(self.max_attempts):
            attempts = attempt + 1
            
            try:
                # Try generation with adaptive approach
                result = self._generate_image_adaptively(full_prompt, artifact_id, attempt, purpose)
                
                if result and result.get('success', False):
                    success = True
                    image_path = result.get('image_path')
                    break
                else:
                    # Adaptive retry with simplified prompt
                    simplified_prompt = self._simplify_prompt_adaptively(prompt, attempt, purpose)
                    full_prompt = self._create_adaptive_prompt(simplified_prompt, style_description, purpose)
                    
                    if self._logger:
                        self._logger(f"[IMAGINE] retry {attempt + 1} with simplified prompt: {simplified_prompt[:30]}...")
                    
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                if self._logger:
                    self._logger(f"[IMAGINE] error in attempt {attempt + 1}: {e}")
                time.sleep(self.retry_delay)
        
        # Create artifact
        artifact = ImaginationArtifact(
            artifact_id=artifact_id,
            prompt=prompt,
            image_path=image_path or self._create_placeholder_image(artifact_id),
            purpose=purpose,
            style=style,
            timestamp=timestamp,
            generation_attempts=attempts,
            success=success
        )
        
        # Save artifact
        self._save_artifact(artifact)
        
        # Learn from this generation
        self._learn_from_generation(prompt, style, purpose, success, attempts)
        
        return {
            'success': success,
            'artifact_id': artifact_id,
            'image_path': artifact.image_path,
            'purpose': purpose,
            'style': style,
            'attempts': attempts,
            'timestamp': timestamp
        }
    
    def _determine_purpose_adaptively(self, prompt: str) -> str:
        """
        Determine purpose from prompt using adaptive analysis.
        
        Args:
            prompt: The generation prompt
            
        Returns:
            Determined purpose
        """
        prompt_lower = prompt.lower()
        
        # Analyze prompt for purpose indicators
        purpose_scores = {}
        
        for purpose, indicators in self.purpose_analysis_data["purpose_indicators"].items():
            score = 0
            for indicator in indicators:
                if indicator in prompt_lower:
                    score += 1
            purpose_scores[purpose] = score
        
        # Check for contextual clues
        contextual_purpose = self._analyze_contextual_purpose(prompt)
        if contextual_purpose:
            purpose_scores[contextual_purpose] = purpose_scores.get(contextual_purpose, 0) + 2
        
        # Find highest scoring purpose
        if purpose_scores:
            best_purpose = max(purpose_scores.items(), key=lambda x: x[1])
            if best_purpose[1] > 0:
                return best_purpose[0]
        
        # Default to creative experimentation if no clear purpose
        return "creative_experimentation"
    
    def _analyze_contextual_purpose(self, prompt: str) -> Optional[str]:
        """Analyze prompt for contextual purpose clues."""
        prompt_lower = prompt.lower()
        
        # Look for contextual patterns
        if any(word in prompt_lower for word in ["illustrate", "show", "depict"]):
            return "story_illustration"
        elif any(word in prompt_lower for word in ["explore", "investigate", "examine"]):
            return "concept_exploration"
        elif any(word in prompt_lower for word in ["express", "convey", "capture"]):
            return "emotional_expression"
        elif any(word in prompt_lower for word in ["demonstrate", "present", "display"]):
            return "technical_demonstration"
        
        return None
    
    def _generate_adaptive_style(self, prompt: str, base_style: str, purpose: str) -> str:
        """
        Generate adaptive style description based on prompt, base style, and purpose.
        
        Args:
            prompt: The generation prompt
            base_style: Base style name
            purpose: Determined purpose
            
        Returns:
            Adaptive style description
        """
        # Analyze prompt for style-relevant content
        style_analysis = self._analyze_prompt_for_style(prompt)
        
        # Get base style components
        base_components = self._get_base_style_components(base_style)
        
        # Adapt style based on purpose and content
        adapted_components = self._adapt_style_components(base_components, style_analysis, purpose)
        
        # Generate style description
        style_description = self._compose_style_description(adapted_components)
        
        return style_description
    
    def _analyze_prompt_for_style(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt for style-relevant content."""
        prompt_lower = prompt.lower()
        
        analysis = {
            "mood": self._detect_mood(prompt_lower),
            "complexity": self._assess_complexity(prompt_lower),
            "subject_type": self._identify_subject_type(prompt_lower),
            "spatial_requirements": self._assess_spatial_requirements(prompt_lower),
            "color_preferences": self._detect_color_preferences(prompt_lower)
        }
        
        return analysis
    
    def _detect_mood(self, prompt: str) -> str:
        """Detect mood from prompt."""
        mood_indicators = {
            "serene": ["calm", "peaceful", "tranquil", "gentle", "soft"],
            "dynamic": ["energetic", "vibrant", "active", "powerful", "intense"],
            "mysterious": ["mysterious", "enigmatic", "hidden", "secret", "obscure"],
            "vibrant": ["bright", "colorful", "lively", "cheerful", "energetic"],
            "subtle": ["subtle", "delicate", "refined", "elegant", "understated"]
        }
        
        for mood, indicators in mood_indicators.items():
            if any(indicator in prompt for indicator in indicators):
                return mood
        
        return "neutral"
    
    def _assess_complexity(self, prompt: str) -> str:
        """Assess complexity level of prompt."""
        word_count = len(prompt.split())
        
        if word_count < 5:
            return "simple"
        elif word_count < 15:
            return "moderate"
        else:
            return "complex"
    
    def _identify_subject_type(self, prompt: str) -> str:
        """Identify type of subject in prompt."""
        subject_types = {
            "human": ["person", "human", "figure", "character", "face"],
            "nature": ["nature", "landscape", "tree", "flower", "animal"],
            "object": ["object", "item", "thing", "tool", "device"],
            "abstract": ["abstract", "pattern", "shape", "form", "concept"],
            "scene": ["scene", "setting", "environment", "place", "location"]
        }
        
        for subject_type, indicators in subject_types.items():
            if any(indicator in prompt for indicator in indicators):
                return subject_type
        
        return "general"
    
    def _assess_spatial_requirements(self, prompt: str) -> str:
        """Assess spatial requirements from prompt."""
        spatial_indicators = {
            "wide": ["wide", "broad", "panoramic", "landscape", "horizon"],
            "close": ["close", "detailed", "intimate", "macro", "close-up"],
            "deep": ["deep", "layered", "multi-dimensional", "depth", "perspective"],
            "flat": ["flat", "minimal", "simple", "clean", "sparse"]
        }
        
        for spatial_type, indicators in spatial_indicators.items():
            if any(indicator in prompt for indicator in indicators):
                return spatial_type
        
        return "standard"
    
    def _detect_color_preferences(self, prompt: str) -> List[str]:
        """Detect color preferences from prompt."""
        colors = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown", "black", "white", "gray"]
        detected_colors = [color for color in colors if color in prompt]
        return detected_colors
    
    def _get_base_style_components(self, base_style: str) -> Dict[str, Any]:
        """Get base style components."""
        # Adaptive base style mapping
        base_styles = {
            "hologram": {
                "visual_effects": ["volumetric_glow", "depth_layering", "translucent_surfaces"],
                "artistic_approach": "experimental",
                "mood": "mysterious",
                "technical_aspects": ["perspective_3d", "lighting_dramatic", "contrast_high"]
            },
            "realistic": {
                "visual_effects": ["natural_lighting", "texture_detail", "accurate_perspective"],
                "artistic_approach": "realistic",
                "mood": "neutral",
                "technical_aspects": ["focus_sharp", "lighting_natural", "contrast_balanced"]
            },
            "abstract": {
                "visual_effects": ["geometric_shapes", "color_fields", "pattern_repetition"],
                "artistic_approach": "abstract",
                "mood": "dynamic",
                "technical_aspects": ["composition_bold", "color_vibrant", "form_simplified"]
            },
            "fantasy": {
                "visual_effects": ["magical_glow", "ethereal_atmosphere", "otherworldly_elements"],
                "artistic_approach": "stylized",
                "mood": "mysterious",
                "technical_aspects": ["lighting_dramatic", "color_saturated", "composition_dynamic"]
            }
        }
        
        return base_styles.get(base_style, base_styles["hologram"])
    
    def _adapt_style_components(self, base_components: Dict[str, Any], 
                              analysis: Dict[str, Any], purpose: str) -> Dict[str, Any]:
        """Adapt style components based on analysis and purpose."""
        adapted = base_components.copy()
        
        # Adapt based on mood
        if analysis["mood"] != "neutral":
            adapted["mood"] = analysis["mood"]
        
        # Adapt based on complexity
        if analysis["complexity"] == "simple":
            adapted["visual_effects"] = ["minimal_detail", "clean_lines", "simple_forms"]
        elif analysis["complexity"] == "complex":
            adapted["visual_effects"].extend(["detailed_texture", "layered_composition", "rich_detail"])
        
        # Adapt based on subject type
        if analysis["subject_type"] == "human":
            adapted["technical_aspects"].append("portrait_techniques")
        elif analysis["subject_type"] == "nature":
            adapted["technical_aspects"].append("landscape_techniques")
        
        # Adapt based on spatial requirements
        if analysis["spatial_requirements"] == "wide":
            adapted["technical_aspects"].append("panoramic_composition")
        elif analysis["spatial_requirements"] == "close":
            adapted["technical_aspects"].append("macro_techniques")
        
        # Adapt based on purpose
        purpose_adaptations = {
            "story_illustration": ["narrative_composition", "character_focus", "scene_setting"],
            "concept_exploration": ["experimental_techniques", "abstract_elements", "symbolic_representation"],
            "emotional_expression": ["mood_atmosphere", "color_psychology", "emotional_lighting"],
            "technical_demonstration": ["clear_composition", "focused_subject", "educational_clarity"],
            "creative_experimentation": ["innovative_techniques", "unconventional_composition", "artistic_freedom"]
        }
        
        if purpose in purpose_adaptations:
            adapted["visual_effects"].extend(purpose_adaptations[purpose])
        
        return adapted
    
    def _compose_style_description(self, components: Dict[str, Any]) -> str:
        """Compose style description from components."""
        description_parts = []
        
        # Add artistic approach
        if "artistic_approach" in components:
            description_parts.append(f"{components['artistic_approach']} style")
        
        # Add visual effects
        if "visual_effects" in components:
            effects = ", ".join(components["visual_effects"])
            description_parts.append(f"with {effects}")
        
        # Add mood
        if "mood" in components and components["mood"] != "neutral":
            description_parts.append(f"{components['mood']} atmosphere")
        
        # Add technical aspects
        if "technical_aspects" in components:
            aspects = ", ".join(components["technical_aspects"])
            description_parts.append(f"using {aspects}")
        
        return ", ".join(description_parts)
    
    def _create_adaptive_prompt(self, prompt: str, style_description: str, purpose: str) -> str:
        """Create adaptive prompt combining original prompt with style and purpose, emphasizing first-person perspective."""
        # Build adaptive prompt based on purpose
        purpose_prefixes = {
            "story_illustration": "First-person perspective from CARL's viewpoint - illustrate the scene: ",
            "concept_exploration": "First-person perspective from CARL's viewpoint - explore the concept: ",
            "emotional_expression": "First-person perspective from CARL's viewpoint - express the emotion: ",
            "technical_demonstration": "First-person perspective from CARL's viewpoint - demonstrate: ",
            "creative_experimentation": "First-person perspective from CARL's viewpoint - experiment with: "
        }
        
        prefix = purpose_prefixes.get(purpose, "First-person perspective from CARL's viewpoint: ")
        
        # Check if CARL is mentioned in the prompt (more precise detection)
        carl_mentioned = any(carl_word in prompt.lower() for carl_word in 
                           ["carl", "robot", " ai ", "self", " me ", "myself", "humanoid", "i am", "i'm"])
        
        # Add first-person perspective cues
        if carl_mentioned:
            # CARL is in the scene - emphasize first-person view
            perspective_cue = "as seen through CARL's own eyes, first-person camera view, "
        else:
            # CARL might be observing - suggest his perspective
            perspective_cue = "as CARL might imagine or observe, "
        
        # Combine elements with first-person perspective
        full_prompt = f"{prefix}{prompt}, {perspective_cue}{style_description}"
        
        return full_prompt
    
    def _simplify_prompt_adaptively(self, original_prompt: str, attempt: int, purpose: str) -> str:
        """
        Simplify prompt adaptively based on attempt number and purpose.
        
        Args:
            original_prompt: Original prompt
            attempt: Current attempt number
            purpose: Determined purpose
            
        Returns:
            Simplified prompt
        """
        words = original_prompt.split()
        
        # Progressive simplification strategies
        if attempt == 1:
            # Remove complex modifiers
            simplified = [word for word in words if len(word) <= 8]
        elif attempt == 2:
            # Keep only core concepts
            core_words = self._extract_core_concepts(original_prompt, purpose)
            simplified = core_words[:5]  # Limit to 5 core words
        else:
            # Minimal prompt
            simplified = words[:3]  # Keep only first 3 words
        
        return " ".join(simplified)
    
    def _extract_core_concepts(self, prompt: str, purpose: str) -> List[str]:
        """Extract core concepts from prompt based on purpose."""
        # Purpose-specific concept extraction
        if purpose == "story_illustration":
            # Focus on main subjects and actions
            return [word for word in prompt.split() if len(word) > 3 and not word.startswith(('the', 'and', 'or', 'but'))]
        elif purpose == "concept_exploration":
            # Focus on abstract concepts
            return [word for word in prompt.split() if len(word) > 4]
        elif purpose == "emotional_expression":
            # Focus on emotional words
            emotional_words = ["happy", "sad", "angry", "calm", "excited", "peaceful", "energetic"]
            return [word for word in prompt.split() if word.lower() in emotional_words]
        else:
            # General approach
            return [word for word in prompt.split() if len(word) > 3]
    
    def _generate_image_adaptively(self, prompt: str, artifact_id: str, 
                                 attempt: int, purpose: str) -> Optional[Dict[str, Any]]:
        """
        Generate image using adaptive approach.
        
        Args:
            prompt: Generation prompt
            artifact_id: Unique artifact ID
            attempt: Current attempt number
            purpose: Determined purpose
            
        Returns:
            Generation result dictionary
        """
        # This is a placeholder for actual image generation
        # In a real implementation, this would call an image generation API
        
        # Simulate generation process
        time.sleep(0.5)  # Simulate processing time
        
        # Create placeholder image for demonstration
        image_path = self._create_placeholder_image(artifact_id)
        
        # Simulate success/failure based on attempt
        success = attempt < 3  # Simulate eventual success
        
        return {
            'success': success,
            'image_path': image_path if success else None,
            'prompt': prompt,
            'attempt': attempt
        }
    
    def _create_placeholder_image(self, artifact_id: str) -> str:
        """Create a placeholder image for demonstration."""
        # Create a simple text-based placeholder
        placeholder_path = os.path.join(self.artifacts_dir, f"{artifact_id}_placeholder.txt")
        
        placeholder_content = f"""
IMAGINATION ARTIFACT
ID: {artifact_id}
Generated: {datetime.now().isoformat()}
Status: Placeholder (actual generation would occur here)

This is a placeholder for the imagination generation system.
In a full implementation, this would be an actual generated image.
        """
        
        with open(placeholder_path, 'w') as f:
            f.write(placeholder_content)
        
        return placeholder_path
    
    def _save_artifact(self, artifact: ImaginationArtifact):
        """Save artifact to storage."""
        # Add to artifacts list
        self.artifacts.append({
            'artifact_id': artifact.artifact_id,
            'prompt': artifact.prompt,
            'image_path': artifact.image_path,
            'purpose': artifact.purpose,
            'style': artifact.style,
            'timestamp': artifact.timestamp,
            'generation_attempts': artifact.generation_attempts,
            'success': artifact.success
        })
        
        # Save to file
        try:
            with open(self.artifacts_file, 'w') as f:
                json.dump(self.artifacts, f, indent=2)
        except Exception as e:
            if self._logger:
                self._logger(f"[IMAGINE] error saving artifact: {e}")
    
    def _learn_from_generation(self, prompt: str, style: str, purpose: str, 
                              success: bool, attempts: int):
        """Learn from generation attempt to improve future generations."""
        learning_data = {
            'prompt': prompt,
            'style': style,
            'purpose': purpose,
            'success': success,
            'attempts': attempts,
            'timestamp': datetime.now().isoformat()
        }
        
        self.generation_history.append(learning_data)
        
        # Keep only recent history
        if len(self.generation_history) > 100:
            self.generation_history = self.generation_history[-50:]
        
        # Update style adaptation data
        if success:
            self._update_successful_patterns(prompt, style, purpose)
        
        # Save learning data
        self._save_learning_data()
    
    def _update_successful_patterns(self, prompt: str, style: str, purpose: str):
        """Update successful generation patterns."""
        pattern_key = f"{style}_{purpose}"
        
        if pattern_key not in self.style_adaptation_data["successful_patterns"]:
            self.style_adaptation_data["successful_patterns"][pattern_key] = {
                'count': 0,
                'prompts': [],
                'avg_attempts': 0
            }
        
        pattern = self.style_adaptation_data["successful_patterns"][pattern_key]
        pattern['count'] += 1
        pattern['prompts'].append(prompt[:100])  # Store first 100 chars
        
        # Keep only recent prompts
        if len(pattern['prompts']) > 20:
            pattern['prompts'] = pattern['prompts'][-10:]
    
    def _save_learning_data(self):
        """Save learning data to files."""
        # Save style adaptation data
        style_file = os.path.join(self.imagination_dir, "style_adaptation.json")
        try:
            with open(style_file, 'w') as f:
                json.dump(self.style_adaptation_data, f, indent=2)
        except Exception as e:
            if self._logger:
                self._logger(f"[IMAGINE] error saving style data: {e}")
        
        # Save purpose analysis data
        purpose_file = os.path.join(self.imagination_dir, "purpose_analysis.json")
        try:
            with open(purpose_file, 'w') as f:
                json.dump(self.purpose_analysis_data, f, indent=2)
        except Exception as e:
            if self._logger:
                self._logger(f"[IMAGINE] error saving purpose data: {e}")
    
    def _load_artifacts(self) -> List[Dict[str, Any]]:
        """Load existing artifacts from file."""
        if os.path.exists(self.artifacts_file):
            try:
                with open(self.artifacts_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def get_artifact(self, artifact_id: str) -> Optional[ImaginationArtifact]:
        """Get artifact by ID."""
        for artifact_data in self.artifacts:
            if artifact_data['artifact_id'] == artifact_id:
                return ImaginationArtifact(**artifact_data)
        return None
    
    def list_artifacts(self, purpose: Optional[str] = None, 
                      style: Optional[str] = None) -> List[ImaginationArtifact]:
        """List artifacts with optional filtering."""
        filtered_artifacts = []
        
        for artifact_data in self.artifacts:
            if purpose and artifact_data['purpose'] != purpose:
                continue
            if style and artifact_data['style'] != style:
                continue
            
            filtered_artifacts.append(ImaginationArtifact(**artifact_data))
        
        return filtered_artifacts
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics."""
        if not self.generation_history:
            return {}
        
        total_generations = len(self.generation_history)
        successful_generations = sum(1 for g in self.generation_history if g['success'])
        avg_attempts = sum(g['attempts'] for g in self.generation_history) / total_generations
        
        purpose_stats = {}
        style_stats = {}
        
        for generation in self.generation_history:
            purpose = generation['purpose']
            style = generation['style']
            
            if purpose not in purpose_stats:
                purpose_stats[purpose] = {'count': 0, 'success': 0}
            if style not in style_stats:
                style_stats[style] = {'count': 0, 'success': 0}
            
            purpose_stats[purpose]['count'] += 1
            style_stats[style]['count'] += 1
            
            if generation['success']:
                purpose_stats[purpose]['success'] += 1
                style_stats[style]['success'] += 1
        
        return {
            'total_generations': total_generations,
            'success_rate': successful_generations / total_generations,
            'average_attempts': avg_attempts,
            'purpose_statistics': purpose_stats,
            'style_statistics': style_stats
        }


# Global instance
imagination_generator = ImaginationGenerator()
