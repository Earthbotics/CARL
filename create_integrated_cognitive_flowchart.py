#!/usr/bin/env python3
"""
Create a comprehensive flowchart diagram illustrating CARL's Integrated Cognitive Process Framework.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

def create_integrated_cognitive_flowchart(output_path="docs/CARL_Integrated_Cognitive_Process_Flowchart.png"):
    """Create comprehensive integrated cognitive process flowchart."""
    fig, ax = plt.subplots(1, 1, figsize=(26, 24))
    ax.set_xlim(0, 26)
    ax.set_ylim(0, 26)
    ax.axis('off')
    
    # Color scheme
    agent_color = '#BBDEFB'  # Medium blue - CARL agent
    input_color = '#E3F2FD'  # Light blue - inputs
    reflex_color = '#FFF9C4'  # Light yellow - reflex
    perception_color = '#E1BEE7'  # Light purple - perception
    judgment_color = '#FFE0B2'  # Light amber - judgment
    action_color = '#C8E6C9'  # Light green - action
    support_color = '#F8BBD0'  # Light pink - support systems
    memory_color = '#B2DFDB'  # Light teal - memory
    output_color = '#FFCCBC'  # Light orange - output
    
    # Define positions (x, y, width, height)
    boxes = {
        # === CARL AGENT (y=25) ===
        'carl_agent': (13, 25, 8, 1.2),
        
        # === INPUT LAYER (y=22.5) ===
        'speech_input': (3, 22.5, 3.5, 1),
        'vision_input': (8, 22.5, 3.5, 1),
        'motion_input': (13, 22.5, 3.5, 1),
        'text_input': (18, 22.5, 3.5, 1),
        
        # === REFLEX CHECK (y=20) ===
        'aiml_reflex': (13, 20, 6, 1),
        
        # === PERCEPTION PHASE (y=18) ===
        'perception_phase': (13, 18, 6, 1),
        
        # === PERCEPTION SYSTEMS (y=16) ===
        'vision_processing': (4, 16, 3.5, 1),
        'intent_classification': (9, 16, 3.5, 1),
        'context_awareness': (14, 16, 3.5, 1),
        'personality_perception': (19, 16, 3.5, 1),
        
        # === JUDGMENT PHASE (y=14) ===
        'judgment_phase': (13, 14, 6, 1),
        
        # === JUDGMENT SYSTEMS (y=12) ===
        'dominant_judgment': (4, 12, 3.5, 1),
        'values_evaluation': (9, 12, 3.5, 1),
        'needs_goals': (14, 12, 3.5, 1),
        'conceptnet_validation': (19, 12, 3.5, 1),
        
        # === ACTION PHASE (y=10) ===
        'action_phase': (13, 10, 6, 1),
        
        # === ACTION SYSTEMS (y=8) ===
        'action_selection': (4, 8, 3.5, 1),
        'skill_execution': (9, 8, 3.5, 1),
        'speech_output': (14, 8, 3.5, 1),
        'emotional_expression': (19, 8, 3.5, 1),
        
        # === SUPPORT SYSTEMS (y=6) ===
        'neucogar': (4, 6, 3.5, 1),
        'inner_self': (9, 6, 3.5, 1),
        'attention': (14, 6, 3.5, 1),
        'exploration': (19, 6, 3.5, 1),
        
        # === MEMORY SYSTEMS (y=4) ===
        'working_memory': (4, 4, 3.5, 1),
        'episodic_memory': (9, 4, 3.5, 1),
        'semantic_memory': (14, 4, 3.5, 1),
        'procedural_memory': (19, 4, 3.5, 1),
        
        # === OUTPUT & FEEDBACK (y=2) ===
        'behavior_output': (8, 2, 4, 1),
        'learning_feedback': (16, 2, 4, 1),
    }
    
    # Draw boxes with appropriate colors
    for name, (x, y, w, h) in boxes.items():
        # Determine color
        if name == 'carl_agent':
            color = agent_color
        elif name in ['speech_input', 'vision_input', 'motion_input', 'text_input']:
            color = input_color
        elif name == 'aiml_reflex':
            color = reflex_color
        elif name in ['perception_phase', 'vision_processing', 'intent_classification',
                      'context_awareness', 'personality_perception']:
            color = perception_color
        elif name in ['judgment_phase', 'dominant_judgment', 'values_evaluation',
                      'needs_goals', 'conceptnet_validation']:
            color = judgment_color
        elif name in ['action_phase', 'action_selection', 'skill_execution',
                      'speech_output', 'emotional_expression']:
            color = action_color
        elif name in ['neucogar', 'inner_self', 'attention', 'exploration']:
            color = support_color
        elif name in ['working_memory', 'episodic_memory', 'semantic_memory', 'procedural_memory']:
            color = memory_color
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
            'carl_agent': 'CARL: Embodied AI\nCognitive Agent',
            'speech_input': 'Speech Input\nFlask Server\nAudio Processing',
            'vision_input': 'Vision Input\nARC Camera\nObject Detection',
            'motion_input': 'Motion Input\nExploration System\nDynamic Sensing',
            'text_input': 'Text Input\nDirect Entry\nNatural Language',
            'aiml_reflex': 'AIML Reflex Check\nFast Pattern Match\nBypass if Match',
            'perception_phase': 'PERCEPTION PHASE\n(40% Processing Time)\nMulti-Modal Integration',
            'vision_processing': 'Vision Processing\nTransport/Dedup\nOpenAI Analysis',
            'intent_classification': 'Intent Classification\nOpenAI Analysis\nSpeech Act Detection',
            'context_awareness': 'Context Awareness\nConversation History\nEmotional State',
            'personality_perception': 'Personality Functions\nExtroversion/Introversion\nSensation/Intuition',
            'judgment_phase': 'JUDGMENT PHASE\n(60% Processing Time)\nDecision Making',
            'dominant_judgment': 'Dominant Judgment\nFeeling/Thinking\nMBTI Functions',
            'values_evaluation': 'Values Evaluation\nMoral Reasoning\nConflict Resolution',
            'needs_goals': 'Needs & Goals\nSatisfaction Assessment\nProgress Evaluation',
            'conceptnet_validation': 'ConceptNet Validation\nCommon Sense\nKnowledge Base',
            'action_phase': 'ACTION PHASE\nBehavior Execution\nPhysical/Verbal/Emotional',
            'action_selection': 'Action Selection\nPriority Calculation\nSkill Filtering',
            'skill_execution': 'Skill Execution\nEZ-Robot Commands\nARC Scripts',
            'speech_output': 'Speech Output\nText-to-Speech\nPC Audio',
            'emotional_expression': 'Emotional Expression\nEye RGB Animations\nFacial Display',
            'neucogar': 'NEUCOGAR Engine\n8 Neurotransmitters\nEmotional Regulation',
            'inner_self': 'Inner Self\nInternal Thoughts\nSelf-Reflection',
            'attention': 'Attention Manager\nFocus Control\nContext Awareness',
            'exploration': 'Exploration System\nIntelligent Motion\nNeed-Based',
            'working_memory': 'Working Memory\nActive Context\nCurrent State',
            'episodic_memory': 'Episodic Memory\nEvent Storage\nExperience Log',
            'semantic_memory': 'Semantic Memory\nConcept Knowledge\nRelationships',
            'procedural_memory': 'Procedural Memory\nSkill Knowledge\nBehavior Patterns',
            'behavior_output': 'Behavior Output\nPhysical Actions\nVerbal Responses',
            'learning_feedback': 'Learning Feedback\nPattern Recognition\nAdaptation',
        }
        
        ax.text(x, y, labels.get(name, name), 
               ha='center', va='center', 
               fontsize=7.5, weight='bold',
               wrap=True)
    
    # Draw arrows with labels
    arrows = [
        # From CARL agent to inputs
        ('carl_agent', 'speech_input', 'Multi-Modal', 'blue'),
        ('carl_agent', 'vision_input', 'Input', 'blue'),
        ('carl_agent', 'motion_input', 'Sources', 'blue'),
        ('carl_agent', 'text_input', '', 'blue'),
        
        # Input to reflex
        ('speech_input', 'aiml_reflex', 'Input', 'yellow'),
        ('vision_input', 'aiml_reflex', 'Input', 'yellow'),
        ('text_input', 'aiml_reflex', 'Input', 'yellow'),
        
        # Reflex to perception (if no match)
        ('aiml_reflex', 'perception_phase', 'No Match', 'purple'),
        
        # Perception phase
        ('perception_phase', 'vision_processing', 'Vision', 'purple'),
        ('perception_phase', 'intent_classification', 'Intent', 'purple'),
        ('perception_phase', 'context_awareness', 'Context', 'purple'),
        ('perception_phase', 'personality_perception', 'Personality', 'purple'),
        
        # Perception to judgment
        ('vision_processing', 'judgment_phase', 'Visual Data', 'orange'),
        ('intent_classification', 'judgment_phase', 'Intent Data', 'orange'),
        ('context_awareness', 'judgment_phase', 'Context Data', 'orange'),
        ('personality_perception', 'judgment_phase', 'Personality Data', 'orange'),
        
        # Judgment phase
        ('judgment_phase', 'dominant_judgment', 'Primary', 'orange'),
        ('judgment_phase', 'values_evaluation', 'Values', 'orange'),
        ('judgment_phase', 'needs_goals', 'Needs/Goals', 'orange'),
        ('judgment_phase', 'conceptnet_validation', 'Validation', 'orange'),
        
        # Judgment to action
        ('dominant_judgment', 'action_phase', 'Decision', 'green'),
        ('values_evaluation', 'action_phase', 'Moral Guide', 'green'),
        ('needs_goals', 'action_phase', 'Priority', 'green'),
        ('conceptnet_validation', 'action_phase', 'Validated', 'green'),
        
        # Action phase
        ('action_phase', 'action_selection', 'Selection', 'green'),
        ('action_selection', 'skill_execution', 'Physical', 'green'),
        ('action_selection', 'speech_output', 'Verbal', 'green'),
        ('action_selection', 'emotional_expression', 'Emotional', 'green'),
        
        # Support systems connections
        ('neucogar', 'perception_phase', 'Regulation', 'pink'),
        ('neucogar', 'judgment_phase', 'Regulation', 'pink'),
        ('neucogar', 'action_phase', 'Regulation', 'pink'),
        ('inner_self', 'judgment_phase', 'Reflection', 'pink'),
        ('attention', 'perception_phase', 'Focus', 'pink'),
        ('attention', 'judgment_phase', 'Focus', 'pink'),
        ('exploration', 'action_phase', 'Exploration', 'pink'),
        
        # Memory connections
        ('perception_phase', 'working_memory', 'Store', 'teal'),
        ('judgment_phase', 'episodic_memory', 'Store', 'teal'),
        ('action_phase', 'episodic_memory', 'Store', 'teal'),
        ('working_memory', 'semantic_memory', 'Consolidate', 'teal'),
        ('episodic_memory', 'semantic_memory', 'Consolidate', 'teal'),
        ('skill_execution', 'procedural_memory', 'Learn', 'teal'),
        
        # Memory feedback
        ('working_memory', 'perception_phase', 'Context', 'teal'),
        ('episodic_memory', 'judgment_phase', 'Experience', 'teal'),
        ('semantic_memory', 'judgment_phase', 'Knowledge', 'teal'),
        ('procedural_memory', 'action_selection', 'Skills', 'teal'),
        
        # Output
        ('skill_execution', 'behavior_output', 'Actions', 'orange'),
        ('speech_output', 'behavior_output', 'Speech', 'orange'),
        ('emotional_expression', 'behavior_output', 'Emotions', 'orange'),
        
        # Feedback loop
        ('behavior_output', 'learning_feedback', 'Results', 'orange'),
        ('learning_feedback', 'perception_phase', 'Adaptation', 'darkgreen'),
        ('learning_feedback', 'judgment_phase', 'Learning', 'darkgreen'),
        ('learning_feedback', 'action_phase', 'Improvement', 'darkgreen'),
    ]
    
    for start, end, label, color in arrows:
        x1, y1 = boxes[start][0], boxes[start][1] - boxes[start][3]/2
        x2, y2 = boxes[end][0], boxes[end][1] + boxes[end][3]/2
        
        # Adjust for horizontal connections and feedback loops
        if abs(x2 - x1) > 2:
            connectionstyle = "arc3,rad=0.2"
        else:
            connectionstyle = "arc3,rad=0.1"
        
        # Special handling for feedback loops
        if start in ['learning_feedback'] and end in ['perception_phase', 'judgment_phase', 'action_phase']:
            # Create curved arrow for feedback
            arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                   arrowstyle='->', 
                                   mutation_scale=25,
                                   color=color,
                                   linewidth=2.5,
                                   alpha=0.8,
                                   connectionstyle="arc3,rad=-0.6")
        elif start in ['working_memory', 'episodic_memory', 'semantic_memory', 'procedural_memory'] and end in ['perception_phase', 'judgment_phase', 'action_selection']:
            # Memory feedback arrows
            arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                   arrowstyle='->', 
                                   mutation_scale=25,
                                   color=color,
                                   linewidth=2,
                                   alpha=0.8,
                                   connectionstyle="arc3,rad=0.3")
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
            # Adjust label position
            if abs(y2 - y1) < 1:
                mid_y += 0.4
            if start == 'learning_feedback':
                mid_x -= 1.5
                mid_y += 1.2
            ax.text(mid_x, mid_y, label, 
                   ha='center', va='center',
                   fontsize=6, style='italic',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))
    
    # Add title
    ax.text(13, 25.8, "CARL's Integrated Cognitive Process Framework", 
           ha='center', va='center',
           fontsize=20, weight='bold')
    
    # Add subtitle
    ax.text(13, 25.3, "Embodied AI Cognitive Agent: Perception → Judgment → Action with Supporting Systems", 
           ha='center', va='center',
           fontsize=12, style='italic', color='gray')
    
    # Add phase labels on the side
    phase_y_positions = [22.5, 20, 18, 14, 10, 6, 4, 2]
    phase_labels = [
        'Input Sources',
        'Reflex Check',
        'Perception',
        'Judgment',
        'Action',
        'Support Systems',
        'Memory',
        'Output/Feedback'
    ]
    
    for i, (y_pos, label) in enumerate(zip(phase_y_positions, phase_labels)):
        ax.text(0.5, y_pos, label, 
               ha='left', va='center',
               fontsize=10, weight='bold', style='italic',
               color='gray',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='gray', linewidth=2))
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=agent_color, label='CARL Agent', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=input_color, label='Input Sources', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=reflex_color, label='Reflex System', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=perception_color, label='Perception Phase', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=judgment_color, label='Judgment Phase', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=action_color, label='Action Phase', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=support_color, label='Support Systems', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=memory_color, label='Memory Systems', edgecolor='black', linewidth=1.5),
        mpatches.Patch(facecolor=output_color, label='Output/Feedback', edgecolor='black', linewidth=1.5),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8, framealpha=0.9, ncol=2)
    
    plt.tight_layout()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Flowchart saved to: {output_path}")
    plt.close()
    return output_path

if __name__ == "__main__":
    output_path = "docs/CARL_Integrated_Cognitive_Process_Flowchart.png"
    create_integrated_cognitive_flowchart(output_path)

