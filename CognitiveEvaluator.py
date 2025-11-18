import json
from typing import Dict, List, Optional
from datetime import datetime

class CognitiveEvaluator:
    """Evaluates the 5Ws and HOW in a sentence and prioritizes which aspects need more attention"""
    def __init__(self, five_ws_results: Dict, conceptnet_edges: List[Dict], emotions_detected: List[str]):
        self.five_ws = five_ws_results  # WHO, WHAT, WHEN, WHERE, WHY, HOW
        self.conceptnet_edges = conceptnet_edges  # Top ConceptNet results
        self.emotions = emotions_detected  # List of detected emotions
        self.weights = {
            "WHO": 1.0, "WHAT": 1.0, "WHEN": 1.5, "WHERE": 1.5, "WHY": 2.5, "HOW": 1.2
        }
        self.lambda_emotion = 1.5
        self.lambda_reflection = 2.0
        self.lambda_length_bias = 1.5  # Weight for longer Ws
        self.why_boost_if_what_empty = 3.0  # Strong priority shift if WHAT is missing
        self.last_evaluation = None

    def evaluate_missing_ws(self) -> Dict[str, float]:
        """Score missing Ws to prioritize what should be answered next."""
        missing_ws = {w: self.weights[w] for w in self.five_ws if not self.five_ws[w] or self.five_ws[w] == ""}
        return missing_ws

    def evaluate_emotional_factor(self) -> float:
        """Increase weight if emotions are detected, emphasizing WHY."""
        if not self.emotions:
            return 0
        # Scale emotional factor based on emotion types
        emotion_weights = {
            "fear": 2.0, "anger": 1.8, "sadness": 1.5,
            "happiness": 1.2, "surprise": 1.3, "disgust": 1.4
        }
        total_weight = sum(emotion_weights.get(e, 1.0) for e in self.emotions)
        return self.lambda_emotion * total_weight

    def evaluate_self_reflection(self) -> float:
        """Determine if ConceptNet edges indicate self-referential concepts."""
        reflection_score = 0
        if not self.conceptnet_edges:
            return 0
            
        for edge in self.conceptnet_edges:
            if not edge.get("surfaceText"):
                continue
            text = edge["surfaceText"].lower()
            # Check for self-referential terms
            if any(term in text for term in ["me", "self", "i am", "myself"]):
                reflection_score += self.lambda_reflection * edge.get("weight", 1.0)
            # Check for emotional terms
            if any(term in text for term in ["feel", "emotion", "mood"]):
                reflection_score += (self.lambda_reflection * 0.5) * edge.get("weight", 1.0)
        return reflection_score

    def evaluate_length_bias(self) -> Dict[str, float]:
        """Check which W has the longest response to boost its priority."""
        max_length = 1  # Avoid division by zero
        for w in self.five_ws:
            if self.five_ws[w]:
                max_length = max(max_length, len(str(self.five_ws[w])))
        
        length_scores = {}
        for w in self.five_ws:
            if self.five_ws[w]:
                length_scores[w] = (len(str(self.five_ws[w])) / max_length) * self.lambda_length_bias
            else:
                length_scores[w] = 0
        return length_scores

    def determine_focus(self) -> Dict:
        """Compute the final focus score and determine the next W to prioritize."""
        missing_ws = self.evaluate_missing_ws()
        emotion_score = self.evaluate_emotional_factor()
        reflection_score = self.evaluate_self_reflection()
        length_bias = self.evaluate_length_bias()

        # Calculate base scores for each W
        focus_scores = {w: self.weights[w] for w in self.five_ws}

        # Add missing penalty
        for w in missing_ws:
            focus_scores[w] += missing_ws[w]

        # Add length bias
        for w, score in length_bias.items():
            focus_scores[w] += score

        # Add emotional emphasis to WHY
        if emotion_score > 0:
            focus_scores["WHY"] += emotion_score
            # Also slightly boost WHO for emotional contexts
            focus_scores["WHO"] += emotion_score * 0.3

        # Add reflection emphasis to WHO and WHY
        if reflection_score > 0:
            focus_scores["WHO"] += reflection_score
            focus_scores["WHY"] += reflection_score * 0.5

        # Special case: If WHAT is empty, boost WHY
        if not self.five_ws["WHAT"]:
            focus_scores["WHY"] += self.why_boost_if_what_empty

        # Get the highest scoring W
        next_focus = max(focus_scores.items(), key=lambda x: x[1])[0]

        # Store evaluation results
        evaluation_result = {
            "Next Focus": next_focus,
            "Scores": {
                "Focus Scores": focus_scores,
                "Missing Ws": missing_ws,
                "Emotion Score": emotion_score,
                "Reflection Score": reflection_score,
                "Length Bias": length_bias,
                "Final Score": sum(focus_scores.values())
            },
            "Timestamp": str(datetime.now())
        }
        
        self.last_evaluation = evaluation_result
        return evaluation_result

    def get_focus_explanation(self) -> str:
        """Returns a human-readable explanation of why the current focus was chosen."""
        if not self.last_evaluation:
            return "No evaluation has been performed yet."
            
        next_focus = self.last_evaluation["Next Focus"]
        scores = self.last_evaluation["Scores"]
        
        reasons = []
        
        # Check if it was chosen due to being missing
        if next_focus in scores["Missing Ws"]:
            reasons.append(f"{next_focus} is missing or empty")
            
        # Check if emotions played a role
        if next_focus in ["WHY", "WHO"] and scores["Emotion Score"] > 0:
            reasons.append(f"Emotional context detected ({len(self.emotions)} emotions)")
            
        # Check if reflection played a role
        if next_focus in ["WHO", "WHY"] and scores["Reflection Score"] > 0:
            reasons.append("Self-referential concepts detected")
            
        # Check length bias
        if scores["Length Bias"].get(next_focus, 0) > 0:
            reasons.append("Has significant existing content")
            
        return f"Focus on {next_focus} because: {'; '.join(reasons)}"

# TEST CASE
if __name__ == "__main__":
    five_ws_results = {
        "WHO": "you",
        "WHAT": "",
        "WHEN": None,
        "WHERE": None,
        "WHY": "to inquire about your emotional state and check if you are okay",
        "HOW": "how"
    }

    conceptnet_edges = [
        {"surfaceText": "[[me]] is not [[you]]", "weight": 2.39},
        {"surfaceText": "[[body]] is related to [[you]]", "weight": 2.39},
        {"surfaceText": None, "weight": 2.0},
        {"surfaceText": None, "weight": 2.0},
        {"surfaceText": None, "weight": 2.0}
    ]

    emotions_detected = ["fear"]

    cognitive_evaluator = CognitiveEvaluator(five_ws_results, conceptnet_edges, emotions_detected)
    result = cognitive_evaluator.determine_focus()
    print(json.dumps(result, indent=4))
    print("\nExplanation:", cognitive_evaluator.get_focus_explanation())
