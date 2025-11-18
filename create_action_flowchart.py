#!/usr/bin/env python3
"""
Create a flowchart diagram illustrating CARL's Action System mechanisms.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

def create_action_flowchart_matplotlib(output_path="docs/CARL_Action_System_Flowchart.png"):
    """Create comprehensive action system flowchart using matplotlib."""
    fig, ax = plt.subplots(1, 1, figsize=(24, 20))
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 22)
    ax.axis('off')
    
    # Color scheme
    input_color = '#E3F2FD'  # Light blue - input
    analysis_color = '#FFF3E0'  # Light orange - analysis
    filtering_color = '#E8F5E9'  # Light green - filtering
    execution_color = '#F3E5F5'  # Light purple - execution
    tracking_color = '#FCE4EC'  # Light pink - tracking
    feedback_color = '#C8E6C9'  # Light green - feedback
    
    # Define positions (x, y, width, height)
    boxes = {
        # === INPUT LAYER (y=20) ===
        'judgment_input': (12, 20, 6, 1.2),
        
        # === ACTION CONTEXT ANALYSIS (y=18) ===
        'action_context': (12, 18, 6, 1),
        
        # === ACTION TYPE DETERMINATION (y=16) ===
        'action_type': (12, 16, 6, 1),
        
        # === ACTION TYPES (y=14) ===
        'physical': (3, 14, 3.5, 1),
        'verbal': (8, 14, 3.5, 1),
        'emotional': (13, 14, 3.5, 1),
        'social': (18, 14, 3.5, 1),
        'exploratory': (3, 12.5, 3.5, 1),
        'cognitive': (8, 12.5, 3.5, 1),
        
        # === SKILL FILTERING (y=10.5) ===
        'skill_filtering': (6, 10.5, 4, 1),
        'position_check': (12, 10.5, 4, 1),
        'prerequisite_check': (18, 10.5, 4, 1),
        
        # === PRIORITY & SELECTION (y=8.5) ===
        'priority_calc': (6, 8.5, 4, 1),
        'action_selection': (12, 8.5, 4, 1),
        'queue_management': (18, 8.5, 4, 1),
        
        # === EXECUTION SYSTEMS (y=6.5) ===
        'ez_robot_exec': (4, 6.5, 3.5, 1),
        'speech_exec': (9, 6.5, 3.5, 1),
        'eye_exec': (14, 6.5, 3.5, 1),
        'movement_exec': (19, 6.5, 3.5, 1),
        
        # === EXECUTION DETAILS (y=4.5) ===
        'body_movements': (3, 4.5, 3.5, 0.8),
        'head_movements': (8, 4.5, 3.5, 0.8),
        'eye_expressions': (13, 4.5, 3.5, 0.8),
        'speech_output': (18, 4.5, 3.5, 0.8),
        
        # === COMPLETION TRACKING (y=3) ===
        'completion_tracker': (6, 3, 4, 1),
        'action_history': (12, 3, 4, 1),
        'memory_storage': (18, 3, 4, 1),
        
        # === FEEDBACK (y=1) ===
        'feedback': (12, 1, 6, 1),
    }
    
    # Draw boxes with appropriate colors
    for name, (x, y, w, h) in boxes.items():
        # Determine color
        if name == 'judgment_input':
            color = input_color
        elif name in ['action_context', 'action_type']:
            color = analysis_color
        elif name in ['physical', 'verbal', 'emotional', 'social', 'exploratory', 'cognitive',
                      'skill_filtering', 'position_check', 'prerequisite_check', 'priority_calc',
                      'action_selection', 'queue_management']:
            color = filtering_color
        elif name in ['ez_robot_exec', 'speech_exec', 'eye_exec', 'movement_exec',
                      'body_movements', 'head_movements', 'eye_expressions', 'speech_output']:
            color = execution_color
        elif name in ['completion_tracker', 'action_history', 'memory_storage']:
            color = tracking_color
        else:
            color = feedback_color
        
        box = FancyBboxPatch((x-w/2, y-h/2), w, h,
                             boxstyle="round,pad=0.1", 
                             facecolor=color, 
                             edgecolor='black',
                             linewidth=2)
        ax.add_patch(box)
        
        # Add text with detailed labels
        labels = {
            'judgment_input': 'Judgment System Input\nRecommended Actions\nPriority Scores',
            'action_context': 'Action Context Analysis\nSkill Requirements\nEmotional State',
            'action_type': 'Action Type Determination\nPhysical/Verbal/Emotional\nSocial/Exploratory',
            'physical': 'Physical Actions\nBody Movements\nEZ-Robot Skills',
            'verbal': 'Verbal Actions\nSpeech Output\nCommunication',
            'emotional': 'Emotional Actions\nEye Expressions\nRGB Animations',
            'social': 'Social Actions\nInteractions\nTurn-Taking',
            'exploratory': 'Exploratory Actions\nLearning\nDiscovery',
            'cognitive': 'Cognitive Actions\nInternal Processing\nThought',
            'skill_filtering': 'Skill Filtering\nAvailable Skills\nCapability Check',
            'position_check': 'Position Awareness\nCurrent Position\nPrerequisites',
            'prerequisite_check': 'Prerequisite Check\nRequired States\nSafety Check',
            'priority_calc': 'Priority Calculation\nUrgency Assessment\nGoal Alignment',
            'action_selection': 'Action Selection\nBest Match\nContext Fit',
            'queue_management': 'Queue Management\nAction Ordering\nConflict Resolution',
            'ez_robot_exec': 'EZ-Robot Execution\nPhysical Commands\nARC Scripts',
            'speech_exec': 'Speech Execution\nText-to-Speech\nPC Audio',
            'eye_exec': 'Eye Expression\nRGB Animations\nEmotional Display',
            'movement_exec': 'Movement Execution\nExploration\nNavigation',
            'body_movements': 'Body Movements\nWave, Bow, Dance\nSit, Stand, Walk',
            'head_movements': 'Head Movements\nYes/No\nLook Directions',
            'eye_expressions': 'Eye Expressions\nJoy, Sad, Anger\nFear, Surprise',
            'speech_output': 'Speech Output\nVerbal Responses\nConversation',
            'completion_tracker': 'Completion Tracking\nAction Duration\nStatus Monitoring',
            'action_history': 'Action History\nLearning Data\nPattern Recognition',
            'memory_storage': 'Memory Storage\nEpisodic Memory\nExperience Log',
            'feedback': 'Feedback Loop\nSuccess/Failure\nLearning Update',
        }
        
        ax.text(x, y, labels.get(name, name), 
               ha='center', va='center', 
               fontsize=7.5, weight='bold',
               wrap=True)
    
    # Draw arrows with labels
    arrows = [
        # Main flow
        ('judgment_input', 'action_context', 'Judgment Data', 'blue'),
        ('action_context', 'action_type', 'Context Analyzed', 'orange'),
        ('action_type', 'physical', 'Physical', 'green'),
        ('action_type', 'verbal', 'Verbal', 'green'),
        ('action_type', 'emotional', 'Emotional', 'green'),
        ('action_type', 'social', 'Social', 'green'),
        ('action_type', 'exploratory', 'Exploratory', 'green'),
        ('action_type', 'cognitive', 'Cognitive', 'green'),
        
        # Filtering
        ('physical', 'skill_filtering', 'Skills', 'green'),
        ('verbal', 'skill_filtering', 'Skills', 'green'),
        ('emotional', 'skill_filtering', 'Skills', 'green'),
        ('social', 'skill_filtering', 'Skills', 'green'),
        ('exploratory', 'skill_filtering', 'Skills', 'green'),
        ('skill_filtering', 'position_check', 'Filtered', 'green'),
        ('position_check', 'prerequisite_check', 'Position OK', 'green'),
        
        # Selection
        ('prerequisite_check', 'priority_calc', 'Prerequisites OK', 'green'),
        ('priority_calc', 'action_selection', 'Priority Set', 'green'),
        ('action_selection', 'queue_management', 'Selected', 'green'),
        
        # Execution routing
        ('queue_management', 'ez_robot_exec', 'Physical', 'purple'),
        ('queue_management', 'speech_exec', 'Verbal', 'purple'),
        ('queue_management', 'eye_exec', 'Emotional', 'purple'),
        ('queue_management', 'movement_exec', 'Exploratory', 'purple'),
        
        # Execution details
        ('ez_robot_exec', 'body_movements', 'Body', 'purple'),
        ('ez_robot_exec', 'head_movements', 'Head', 'purple'),
        ('eye_exec', 'eye_expressions', 'RGB', 'purple'),
        ('speech_exec', 'speech_output', 'TTS', 'purple'),
        
        # Tracking
        ('body_movements', 'completion_tracker', 'Executing', 'pink'),
        ('head_movements', 'completion_tracker', 'Executing', 'pink'),
        ('eye_expressions', 'completion_tracker', 'Executing', 'pink'),
        ('speech_output', 'completion_tracker', 'Executing', 'pink'),
        ('movement_exec', 'completion_tracker', 'Executing', 'pink'),
        
        ('completion_tracker', 'action_history', 'Completed', 'pink'),
        ('action_history', 'memory_storage', 'Logged', 'pink'),
        
        # Feedback
        ('memory_storage', 'feedback', 'Stored', 'darkgreen'),
        ('feedback', 'action_context', 'Learning', 'darkgreen'),
    ]
    
    for start, end, label, color in arrows:
        x1, y1 = boxes[start][0], boxes[start][1] - boxes[start][3]/2
        x2, y2 = boxes[end][0], boxes[end][1] + boxes[end][3]/2
        
        # Adjust for horizontal connections
        if abs(x2 - x1) > 2:
            connectionstyle = "arc3,rad=0.2"
        else:
            connectionstyle = "arc3,rad=0.1"
        
        # Special handling for feedback loop
        if start == 'feedback' and end == 'action_context':
            # Create curved arrow for feedback
            arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                   arrowstyle='->', 
                                   mutation_scale=25,
                                   color=color,
                                   linewidth=2.5,
                                   alpha=0.8,
                                   connectionstyle="arc3,rad=-0.5")
        else:
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
            if start == 'feedback' and end == 'action_context':
                mid_x -= 2
                mid_y += 1
            ax.text(mid_x, mid_y, label, 
                   ha='center', va='center',
                   fontsize=6, style='italic',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))
    
    # Add title
    ax.text(12, 21.5, "CARL Action System - Behavior Execution", 
           ha='center', va='center',
           fontsize=18, weight='bold')
    
    # Add subtitle
    ax.text(12, 21, "Judgment → Analysis → Filtering → Execution → Tracking → Feedback", 
           ha='center', va='center',
           fontsize=11, style='italic', color='gray')
    
    # Add phase labels
    phase_y_positions = [20, 16, 14, 10.5, 8.5, 6.5, 4.5, 3, 1]
    phase_labels = [
        'Input',
        'Type Determination',
        'Action Types',
        'Filtering & Checks',
        'Selection',
        'Execution',
        'Execution Details',
        'Tracking',
        'Feedback'
    ]
    
    for i, (y_pos, label) in enumerate(zip(phase_y_positions, phase_labels)):
        ax.text(0.5, y_pos, label, 
               ha='left', va='center',
               fontsize=9, weight='bold', style='italic',
               color='gray',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='gray'))
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=input_color, label='Input', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=analysis_color, label='Analysis', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=filtering_color, label='Filtering & Selection', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=execution_color, label='Execution', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=tracking_color, label='Tracking', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=feedback_color, label='Feedback', edgecolor='black', linewidth=1.5),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9, framealpha=0.9)
    
    plt.tight_layout()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Flowchart saved to: {output_path}")
    plt.close()
    return output_path

if __name__ == "__main__":
    output_path = "docs/CARL_Action_System_Flowchart.png"
    create_action_flowchart_matplotlib(output_path)

