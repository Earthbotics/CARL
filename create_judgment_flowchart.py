#!/usr/bin/env python3
"""
Create a flowchart diagram illustrating CARL's Judgment System mechanisms.
"""

try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

def create_judgment_flowchart_matplotlib(output_path="docs/CARL_Judgment_System_Flowchart.png"):
    """Create comprehensive judgment system flowchart using matplotlib."""
    fig, ax = plt.subplots(1, 1, figsize=(24, 20))
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 24)
    ax.axis('off')
    
    # Color scheme
    input_color = '#E3F2FD'  # Light blue - input
    personality_color = '#FFE0B2'  # Light amber - personality functions
    judgment_color = '#FFF3E0'  # Light orange - judgment processing
    values_color = '#E8F5E9'  # Light green - values system
    integration_color = '#F3E5F5'  # Light purple - integration
    output_color = '#FCE4EC'  # Light pink - output
    
    # Define positions (x, y, width, height)
    boxes = {
        # === INPUT LAYER (y=22) ===
        'perception_input': (12, 22, 6, 1.2),
        
        # === FUNCTION DETERMINATION (y=19.5) ===
        'active_functions': (12, 19.5, 5, 1),
        
        # === PERSONALITY FUNCTIONS (y=17) ===
        'personality_judgment': (12, 17, 5, 1),
        
        # === JUDGMENT FUNCTIONS DETAIL (y=14.5) ===
        'feeling': (6, 14.5, 3, 1),
        'thinking': (12, 14.5, 3, 1),
        'perceiving': (18, 14.5, 3, 1),
        'judging': (6, 13, 3, 1),
        'dominant_judgment': (12, 13, 3, 1),
        'inferior_judgment': (18, 13, 3, 1),
        
        # === JUDGMENT PROCESSING (y=10.5) ===
        'needs_judgment': (3, 10.5, 4, 1),
        'goals_judgment': (8, 10.5, 4, 1),
        'conceptnet_judgment': (13, 10.5, 4, 1),
        'earthly_game': (18, 10.5, 4, 1),
        
        # === VALUES SYSTEM (y=8) ===
        'values_evaluation': (6, 8, 4, 1.2),
        'conflict_monitor': (12, 8, 4, 1.2),
        'moral_reasoning': (18, 8, 4, 1.2),
        
        # === VALUES DETAILS (y=6) ===
        'reward_system': (4, 6, 3, 0.8),
        'prefrontal_cortex': (9, 6, 3, 0.8),
        'emotional_weighting': (15, 6, 3, 0.8),
        'dmn_reflection': (20, 6, 3, 0.8),
        
        # === INTEGRATION (y=4) ===
        'priority_calc': (6, 4, 4, 1),
        'action_generation': (14, 4, 4, 1),
        
        # === OUTPUT LAYER (y=1.5) ===
        'judgment_output': (10, 1.5, 6, 1),
        'action_system': (18, 1.5, 4, 1),
    }
    
    # Draw boxes with appropriate colors
    for name, (x, y, w, h) in boxes.items():
        # Determine color
        if name == 'perception_input':
            color = input_color
        elif name in ['personality_judgment', 'feeling', 'thinking', 'perceiving', 'judging', 
                      'dominant_judgment', 'inferior_judgment']:
            color = personality_color
        elif name in ['active_functions', 'needs_judgment', 'goals_judgment', 'conceptnet_judgment', 
                      'earthly_game', 'priority_calc', 'action_generation']:
            color = judgment_color
        elif name in ['values_evaluation', 'conflict_monitor', 'moral_reasoning', 'reward_system',
                      'prefrontal_cortex', 'emotional_weighting', 'dmn_reflection']:
            color = values_color
        elif name == 'judgment_output':
            color = integration_color
        else:
            color = output_color
        
        box = FancyBboxPatch((x-w/2, y-h/2), w, h,
                             boxstyle="round,pad=0.1", 
                             facecolor=color, 
                             edgecolor='black',
                             linewidth=2)
        ax.add_patch(box)
        
        # Add text with detailed labels
        labels = {
            'perception_input': 'Perception System Input\nCognitive Representation\nStructured Data',
            'active_functions': 'Active Function Determination\nMBTI Cognitive Stack\nContext-Based Selection',
            'personality_judgment': 'Personality Functions\n(60% Processing Time)\nMBTI Judgment Phase',
            'feeling': 'Feeling (Fi/Fe)\nHow do I/others feel?',
            'thinking': 'Thinking (Ti/Te)\nDoes this make sense?',
            'perceiving': 'Perceiving (P)\nStay open/adaptive?',
            'judging': 'Judging (J)\nStructured decision?',
            'dominant_judgment': 'Dominant Judgment\nPrimary Function\n(40% Processing)',
            'inferior_judgment': 'Inferior Judgment\nSupporting Functions\nReduced Effectiveness',
            'needs_judgment': 'Needs-Based Judgment\nPersonal Needs\nSatisfaction Assessment',
            'goals_judgment': 'Goals-Based Judgment\nActive Goals\nProgress Evaluation',
            'conceptnet_judgment': 'ConceptNet Judgment\nCommon Sense\nKnowledge Validation',
            'earthly_game': 'Earthly Game\nSuggestions\nGame State Integration',
            'values_evaluation': 'Values Evaluation\nCore Values\nBeliefs Assessment',
            'conflict_monitor': 'Conflict Monitor\n(ACC Analog)\nValue Conflicts',
            'moral_reasoning': 'Moral Reasoning\nEthical Principles\nDecision Alignment',
            'reward_system': 'Reward System\n(Nucleus Accumbens)\nImmediate Signals',
            'prefrontal_cortex': 'Prefrontal Cortex\n(vmPFC/OFC)\nAbstract Values',
            'emotional_weighting': 'Emotional Weighting\n(Amygdala)\nSalience',
            'dmn_reflection': 'DMN Reflection\nSelf-Reflection\nMoral Reasoning',
            'priority_calc': 'Interaction Priority\nCalculation\nWeighted Scoring',
            'action_generation': 'Recommended Actions\nPersonality-Based\nContext-Aware',
            'judgment_output': 'Judgment Output\nComplete Analysis\nDecision Ready',
            'action_system': 'Action System\nBehavior Execution\nPhysical Actions',
        }
        
        ax.text(x, y, labels.get(name, name), 
               ha='center', va='center', 
               fontsize=7.5, weight='bold',
               wrap=True)
    
    # Draw arrows with labels
    arrows = [
        # Main flow
        ('perception_input', 'active_functions', 'Perception Data', 'blue'),
        ('active_functions', 'personality_judgment', 'Active Functions', 'orange'),
        ('personality_judgment', 'feeling', 'Feeling', 'darkorange'),
        ('personality_judgment', 'thinking', 'Thinking', 'darkorange'),
        ('personality_judgment', 'perceiving', 'Perceiving', 'darkorange'),
        ('personality_judgment', 'judging', 'Judging', 'darkorange'),
        
        # Judgment processing
        ('feeling', 'dominant_judgment', 'Fi/Fe', 'darkorange'),
        ('thinking', 'dominant_judgment', 'Ti/Te', 'darkorange'),
        ('dominant_judgment', 'inferior_judgment', 'Primary', 'darkorange'),
        ('perceiving', 'inferior_judgment', 'P', 'darkorange'),
        ('judging', 'inferior_judgment', 'J', 'darkorange'),
        
        # Judgment evaluations
        ('dominant_judgment', 'needs_judgment', 'Needs', 'red'),
        ('inferior_judgment', 'goals_judgment', 'Goals', 'red'),
        ('dominant_judgment', 'conceptnet_judgment', 'Common Sense', 'red'),
        ('inferior_judgment', 'earthly_game', 'Game State', 'red'),
        
        # Values system
        ('needs_judgment', 'values_evaluation', 'Values Check', 'green'),
        ('goals_judgment', 'values_evaluation', 'Values Check', 'green'),
        ('values_evaluation', 'conflict_monitor', 'Conflicts', 'green'),
        ('conflict_monitor', 'moral_reasoning', 'Resolution', 'green'),
        
        # Values details
        ('values_evaluation', 'reward_system', 'Reward', 'darkgreen'),
        ('values_evaluation', 'prefrontal_cortex', 'Abstract', 'darkgreen'),
        ('values_evaluation', 'emotional_weighting', 'Emotion', 'darkgreen'),
        ('moral_reasoning', 'dmn_reflection', 'Reflection', 'darkgreen'),
        
        # Integration
        ('reward_system', 'priority_calc', 'Reward Signal', 'purple'),
        ('prefrontal_cortex', 'priority_calc', 'Value Weight', 'purple'),
        ('emotional_weighting', 'priority_calc', 'Emotion Weight', 'purple'),
        ('conceptnet_judgment', 'priority_calc', 'Validation', 'purple'),
        ('earthly_game', 'priority_calc', 'Game Context', 'purple'),
        ('dmn_reflection', 'priority_calc', 'Reflection', 'purple'),
        
        # Action generation
        ('priority_calc', 'action_generation', 'Priority', 'darkblue'),
        ('moral_reasoning', 'action_generation', 'Moral Guide', 'darkblue'),
        ('conflict_monitor', 'action_generation', 'Conflict Status', 'darkblue'),
        
        # Output
        ('action_generation', 'judgment_output', 'Actions', 'darkblue'),
        ('priority_calc', 'judgment_output', 'Priority', 'darkblue'),
        ('judgment_output', 'action_system', 'Execute', 'darkblue'),
    ]
    
    for start, end, label, color in arrows:
        x1, y1 = boxes[start][0], boxes[start][1] - boxes[start][3]/2
        x2, y2 = boxes[end][0], boxes[end][1] + boxes[end][3]/2
        
        # Adjust for horizontal connections
        if abs(x2 - x1) > 2:
            connectionstyle = "arc3,rad=0.2"
        else:
            connectionstyle = "arc3,rad=0.1"
        
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle='->', 
                               mutation_scale=25,
                               color=color,
                               linewidth=2,
                               alpha=0.8,
                               connectionstyle=connectionstyle)
        ax.add_patch(arrow)
        
        # Add label for important arrows
        if label and label not in ['']:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            # Adjust label position to avoid overlap
            if abs(y2 - y1) < 1:
                mid_y += 0.4
            ax.text(mid_x, mid_y, label, 
                   ha='center', va='center',
                   fontsize=6, style='italic',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))
    
    # Add title
    ax.text(12, 23.5, "CARL's Judgment System - Cognitive Architecture", 
           ha='center', va='center',
           fontsize=18, weight='bold')
    
    # Add subtitle
    ax.text(12, 23, "Perception → Personality Functions → Values → Priority → Actions", 
           ha='center', va='center',
           fontsize=11, style='italic', color='gray')
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=input_color, label='Input', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=personality_color, label='Personality Functions', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=judgment_color, label='Judgment Processing', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=values_color, label='Values System', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=integration_color, label='Integration', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=output_color, label='Output', edgecolor='black', linewidth=1.5),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9, framealpha=0.9)
    
    plt.tight_layout()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Flowchart saved to: {output_path}")
    plt.close()
    return output_path

if __name__ == "__main__":
    output_path = "docs/CARL_Judgment_System_Flowchart.png"
    create_judgment_flowchart_matplotlib(output_path)

