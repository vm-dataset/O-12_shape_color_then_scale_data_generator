"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK PROMPTS                                   ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define prompts/instructions for your task.            ║
║  Prompts are selected based on task type and returned to the model.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


# ══════════════════════════════════════════════════════════════════════════════
#  DEFINE YOUR PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {
    "default": [
        "Show the color-then-scale transformation being applied to the second shape. First change the color, then change the size according to the established pattern.",
        "Animate the two-step transformation where the shape first changes color and then changes scale. The question mark should smoothly transition through both steps.",
        "Complete the visual analogy by showing what the second shape becomes when the same color-then-scale transformation is applied.",
    ],
    
    "color_then_scale": [
        "Show the shape first changing color and then changing size. Both transformations should match the example pattern.",
        "Complete the analogy by revealing the shape with the correct color and scale.",
        "Animate the two-step transformation: color change followed by size change.",
    ],
}


def get_prompt(task_type: str = "default") -> str:
    """
    Select a random prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict)
        
    Returns:
        Random prompt string from the specified type
    """
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)


def get_all_prompts(task_type: str = "default") -> list[str]:
    """Get all prompts for a given task type."""
    return PROMPTS.get(task_type, PROMPTS["default"])
