"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SHAPE TWO-STEP SEQUENTIAL TASK GENERATOR                  ║
║                                                                               ║
║  Generates two-step sequential tasks (A→B→C :: D→?→?)                        ║
║  Example: blue_small_circle → red_small_circle → red_large_circle            ║
║           blue_small_square → red_small_square → red_large_square             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import tempfile
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Any

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class TaskGenerator(BaseGenerator):
    """
    Shape two-step sequential task generator.
    
    Creates visual analogies in the format A→B→C :: D→?→?
    where shapes undergo two sequential transformations: color change then scale change.
    """
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)
        
        # Initialize video generator if enabled
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
        
        # Shape definitions - expanded set for more variety
        self.base_shapes = [
            "square", "triangle", "circle", "diamond", "pentagon", "hexagon",
            "rectangle", "oval", "star", "heart", "cross", "arrow", "trapezoid",
            "rhombus", "octagon", "crescent", "plus", "minus", "L_shape", "T_shape"
        ]
        
        # Color palette - expanded with more distinct colors
        self.colors = {
            "blue": (70, 130, 180),
            "red": (220, 20, 60),
            "green": (34, 139, 34),
            "orange": (255, 140, 0),
            "purple": (147, 112, 219),
            "teal": (0, 128, 128),
            "pink": (255, 20, 147),
            "brown": (165, 42, 42),
            "indigo": (75, 0, 130),
            "lime": (50, 205, 50),
            "crimson": (220, 20, 60),
            "navy": (0, 0, 128),
            "olive": (128, 128, 0),
            "maroon": (128, 0, 0),
            "steel_blue": (70, 130, 180)
        }
        
        # Scale factors - expanded with more granular options
        self.scale_factors = {
            "tiny": 0.6,
            "small": 0.8,
            "medium": 1.0,
            "large": 1.3,
            "extra_large": 1.6,
            "huge": 1.9
        }
        
        # Generate all valid transformation combinations dynamically
        self.valid_transformations = self._generate_all_valid_transformations()
        
        # Track generated combinations to prevent duplicates
        self.generated_combinations = set()
    
    def _generate_all_valid_transformations(self) -> List[Tuple[str, str, str, str]]:
        """Generate all valid transformation combinations dynamically."""
        transformations = []
        color_names = list(self.colors.keys())
        scale_names = list(self.scale_factors.keys())
        
        # Generate all combinations where colors and scales are different
        for color_from in color_names:
            for color_to in color_names:
                if color_from != color_to:  # Colors must be different
                    for scale_from in scale_names:
                        for scale_to in scale_names:
                            if scale_from != scale_to:  # Scales must be different
                                transformations.append((color_from, color_to, scale_from, scale_to))
        
        return transformations
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one shape two-step sequential task pair."""
        
        # Generate task data
        task_data = self._generate_task_data()
        
        # Render images
        first_image = self._render_initial_state(task_data)
        final_image = self._render_final_state(task_data)
        
        # Generate video (optional)
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(first_image, final_image, task_id, task_data)
        
        # Select prompt
        prompt = get_prompt(task_data.get("transformation_type", "default"))
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TASK DATA GENERATION
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_task_data(self) -> Dict[str, Any]:
        """Generate two-step sequential transformation task data with duplicate prevention."""
        
        # Calculate total possible unique combinations
        num_shapes = len(self.base_shapes)
        num_transformations = len(self.valid_transformations)
        max_unique_combinations = num_shapes * (num_shapes - 1) * num_transformations
        
        # If we haven't exhausted all combinations, ensure uniqueness
        if len(self.generated_combinations) < max_unique_combinations:
            max_attempts = 1000  # Increase attempts for better coverage
            for attempt in range(max_attempts):
                # Select two different shapes for the analogy
                shape_example, shape_question = random.sample(self.base_shapes, 2)
                # Select a valid transformation sequence (color and scale changes)
                color_from, color_to, scale_from, scale_to = random.choice(self.valid_transformations)
                
                # Create a unique identifier for this combination
                combination_key = (shape_example, shape_question, color_from, color_to, scale_from, scale_to)
                
                # Check if this combination has been used before
                if combination_key not in self.generated_combinations:
                    self.generated_combinations.add(combination_key)
                    return self._generate_two_step_task(shape_example, shape_question, color_from, color_to, scale_from, scale_to)
            
            # If we still can't find a unique combination after many attempts,
            # generate all remaining combinations systematically
            return self._generate_systematic_unique_combination()
        
        # If we've exhausted unique combinations, allow duplicates but warn
        if len(self.generated_combinations) == max_unique_combinations:
            print(f"⚠️  Warning: Generated all {max_unique_combinations} unique combinations. Allowing duplicates for remaining tasks.")
        
        shape_example, shape_question = random.sample(self.base_shapes, 2)
        color_from, color_to, scale_from, scale_to = random.choice(self.valid_transformations)
        return self._generate_two_step_task(shape_example, shape_question, color_from, color_to, scale_from, scale_to)
    
    def _generate_systematic_unique_combination(self) -> Dict[str, Any]:
        """Generate a unique combination systematically when random selection fails."""
        # Generate all possible combinations and find one not yet used
        for shape_example in self.base_shapes:
            for shape_question in self.base_shapes:
                if shape_example == shape_question:
                    continue
                for color_from, color_to, scale_from, scale_to in self.valid_transformations:
                    combination_key = (shape_example, shape_question, color_from, color_to, scale_from, scale_to)
                    if combination_key not in self.generated_combinations:
                        self.generated_combinations.add(combination_key)
                        return self._generate_two_step_task(shape_example, shape_question, color_from, color_to, scale_from, scale_to)
        
        # This should never happen if our math is correct
        raise RuntimeError("Failed to generate unique combination - this should not happen!")
    
    def _generate_two_step_task(self, shape_example: str, shape_question: str, color_from: str, color_to: str, scale_from: str, scale_to: str) -> Dict[str, Any]:
        """Generate a two-step sequential transformation task."""
        
        return {
            "transformation_type": "color_then_scale",
            # Example sequence: A → B → C
            "shape_a": shape_example,  # Original
            "shape_b": shape_example,  # After step 1 (color change)
            "shape_c": shape_example,  # After step 2 (scale change)
            # Question sequence: D → ? → ?
            "shape_d": shape_question,  # Original
            "shape_e": shape_question,  # After step 1 (color change) - first ?
            "shape_f": shape_question,  # After step 2 (scale change) - second ?
            "color_from": color_from,
            "color_to": color_to,
            "scale_from": scale_from,
            "scale_to": scale_to,
            "description": f"Step 1: {color_from} → {color_to}, Step 2: {scale_from} → {scale_to}"
        }
    
    # ══════════════════════════════════════════════════════════════════════════
    #  IMAGE RENDERING
    # ══════════════════════════════════════════════════════════════════════════
    
    def _render_initial_state(self, task_data: Dict[str, Any]) -> Image.Image:
        """Render the initial state with A→B→C :: D→?→? layout."""
        img = self.renderer.create_blank_image()
        draw = ImageDraw.Draw(img)
        
        width, height = self.config.image_size
        margin = self.config.margin
        base_shape_size = self.config.shape_size
        
        # Layout positions for sequential format with better spacing
        # A  →  B  →  C
        # D  →  ?  →  ?
        
        # Use wider spacing for better visual separation
        total_content_width = width - 2 * margin
        step_width = total_content_width // 3
        shape_spacing = step_width * 0.8  # Leave more space between shapes
        arrow_width = step_width * 0.2
        
        positions = {
            # Example row (top) - centered vertically in upper half
            "A": (margin + shape_spacing//2, height//3),
            "arrow1": (margin + shape_spacing + arrow_width//2, height//3),
            "B": (margin + shape_spacing + arrow_width + shape_spacing//2, height//3),
            "arrow2": (margin + 2*shape_spacing + arrow_width + arrow_width//2, height//3),
            "C": (margin + 2*shape_spacing + 2*arrow_width + shape_spacing//2, height//3),
            
            # Question row (bottom) - centered vertically in lower half
            "D": (margin + shape_spacing//2, 2*height//3),
            "arrow3": (margin + shape_spacing + arrow_width//2, 2*height//3),
            "question1": (margin + shape_spacing + arrow_width + shape_spacing//2, 2*height//3),
            "arrow4": (margin + 2*shape_spacing + arrow_width + arrow_width//2, 2*height//3),
            "question2": (margin + 2*shape_spacing + 2*arrow_width + shape_spacing//2, 2*height//3)
        }
        
        # Draw example sequence: A → B → C
        self._draw_shape_at_position(draw, task_data["shape_a"], positions["A"], base_shape_size, 
                                   task_data["color_from"], task_data["scale_from"])  # A: Original
        self._draw_arrow(draw, positions["arrow1"])
        self._draw_shape_at_position(draw, task_data["shape_b"], positions["B"], base_shape_size, 
                                   task_data["color_to"], task_data["scale_from"])  # B: Color changed
        self._draw_arrow(draw, positions["arrow2"])
        self._draw_shape_at_position(draw, task_data["shape_c"], positions["C"], base_shape_size, 
                                   task_data["color_to"], task_data["scale_to"])  # C: Color + Scale changed
        
        # Draw question sequence: D → ? → ?
        self._draw_shape_at_position(draw, task_data["shape_d"], positions["D"], base_shape_size, 
                                   task_data["color_from"], task_data["scale_from"])  # D: Original
        self._draw_arrow(draw, positions["arrow3"])
        self._draw_question_mark(draw, positions["question1"])  # First ?
        self._draw_arrow(draw, positions["arrow4"])
        self._draw_question_mark(draw, positions["question2"])  # Second ?
        
        return img
    
    def _render_final_state(self, task_data: Dict[str, Any]) -> Image.Image:
        """Render the final state with both answers revealed."""
        img = self.renderer.create_blank_image()
        draw = ImageDraw.Draw(img)
        
        width, height = self.config.image_size
        margin = self.config.margin
        base_shape_size = self.config.shape_size
        
        # Same improved layout as initial state
        total_content_width = width - 2 * margin
        step_width = total_content_width // 3
        shape_spacing = step_width * 0.8
        arrow_width = step_width * 0.2
        
        positions = {
            # Example row (top)
            "A": (margin + shape_spacing//2, height//3),
            "arrow1": (margin + shape_spacing + arrow_width//2, height//3),
            "B": (margin + shape_spacing + arrow_width + shape_spacing//2, height//3),
            "arrow2": (margin + 2*shape_spacing + arrow_width + arrow_width//2, height//3),
            "C": (margin + 2*shape_spacing + 2*arrow_width + shape_spacing//2, height//3),
            
            # Question row (bottom)
            "D": (margin + shape_spacing//2, 2*height//3),
            "arrow3": (margin + shape_spacing + arrow_width//2, 2*height//3),
            "E": (margin + shape_spacing + arrow_width + shape_spacing//2, 2*height//3),
            "arrow4": (margin + 2*shape_spacing + arrow_width + arrow_width//2, 2*height//3),
            "F": (margin + 2*shape_spacing + 2*arrow_width + shape_spacing//2, 2*height//3)
        }
        
        # Draw example sequence: A → B → C (same as initial)
        self._draw_shape_at_position(draw, task_data["shape_a"], positions["A"], base_shape_size, 
                                   task_data["color_from"], task_data["scale_from"])  # A: Original
        self._draw_arrow(draw, positions["arrow1"])
        self._draw_shape_at_position(draw, task_data["shape_b"], positions["B"], base_shape_size, 
                                   task_data["color_to"], task_data["scale_from"])  # B: Color changed
        self._draw_arrow(draw, positions["arrow2"])
        self._draw_shape_at_position(draw, task_data["shape_c"], positions["C"], base_shape_size, 
                                   task_data["color_to"], task_data["scale_to"])  # C: Color + Scale changed
        
        # Draw answer sequence: D → E → F (answers revealed)
        self._draw_shape_at_position(draw, task_data["shape_d"], positions["D"], base_shape_size, 
                                   task_data["color_from"], task_data["scale_from"])  # D: Original
        self._draw_arrow(draw, positions["arrow3"])
        self._draw_shape_at_position(draw, task_data["shape_e"], positions["E"], base_shape_size, 
                                   task_data["color_to"], task_data["scale_from"])  # E: Color changed (first answer)
        self._draw_arrow(draw, positions["arrow4"])
        self._draw_shape_at_position(draw, task_data["shape_f"], positions["F"], base_shape_size, 
                                   task_data["color_to"], task_data["scale_to"])  # F: Color + Scale changed (second answer)
        
        return img
    
    def _draw_shape_at_position(self, draw: ImageDraw.Draw, shape: str, position: Tuple[int, int], base_size: int, color_name: str, scale_name: str):
        """Draw a shape at the specified position with the given color and scale."""
        x, y = position
        
        color = self.colors[color_name]
        scale_factor = self.scale_factors[scale_name]
        actual_size = int(base_size * scale_factor)
        
        self._draw_base_shape(draw, shape, x, y, actual_size, color)
    
    def _draw_base_shape(self, draw: ImageDraw.Draw, shape: str, x: int, y: int, size: int, color: Tuple[int, int, int]):
        """Draw a basic geometric shape with specified color and size."""
        half_size = size // 2
        outline_color = (0, 0, 0)  # Black outline
        outline_width = 2
        
        if shape == "square":
            draw.rectangle([x-half_size, y-half_size, x+half_size, y+half_size], 
                         fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "circle":
            draw.ellipse([x-half_size, y-half_size, x+half_size, y+half_size], 
                        fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "triangle":
            points = [
                (x, y-half_size),  # top
                (x-half_size, y+half_size),  # bottom left
                (x+half_size, y+half_size)   # bottom right
            ]
            draw.polygon(points, fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "diamond":
            points = [
                (x, y-half_size),  # top
                (x+half_size, y),  # right
                (x, y+half_size),  # bottom
                (x-half_size, y)   # left
            ]
            draw.polygon(points, fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "pentagon":
            points = []
            for i in range(5):
                angle = i * 2 * math.pi / 5 - math.pi/2  # Start from top
                px = x + half_size * math.cos(angle)
                py = y + half_size * math.sin(angle)
                points.append((px, py))
            draw.polygon(points, fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "hexagon":
            points = []
            for i in range(6):
                angle = i * 2 * math.pi / 6
                px = x + half_size * math.cos(angle)
                py = y + half_size * math.sin(angle)
                points.append((px, py))
            draw.polygon(points, fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "rectangle":
            # Rectangle (wider than tall)
            width_factor = 1.4
            rect_width = int(half_size * width_factor)
            rect_height = int(half_size * 0.7)
            draw.rectangle([x-rect_width, y-rect_height, x+rect_width, y+rect_height], 
                         fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "oval":
            # Oval (wider than tall)
            width_factor = 1.4
            oval_width = int(half_size * width_factor)
            oval_height = int(half_size * 0.7)
            draw.ellipse([x-oval_width, y-oval_height, x+oval_width, y+oval_height], 
                        fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "star":
            # 5-pointed star
            points = []
            outer_radius = half_size
            inner_radius = half_size * 0.4
            
            for i in range(10):  # 5 outer + 5 inner points
                if i % 2 == 0:  # Outer points
                    angle = i * math.pi / 5 - math.pi/2
                    px = x + outer_radius * math.cos(angle)
                    py = y + outer_radius * math.sin(angle)
                else:  # Inner points
                    angle = i * math.pi / 5 - math.pi/2
                    px = x + inner_radius * math.cos(angle)
                    py = y + inner_radius * math.sin(angle)
                points.append((px, py))
            
            draw.polygon(points, fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "heart":
            # Heart shape using curves (approximate with polygon)
            points = [
                (x, y + half_size),                    # bottom point
                (x - half_size*0.7, y),              # left curve
                (x - half_size*0.3, y - half_size*0.5), # left top
                (x, y - half_size*0.2),              # center top
                (x + half_size*0.3, y - half_size*0.5),  # right top
                (x + half_size*0.7, y),               # right curve
            ]
            draw.polygon(points, fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "cross":
            # Cross shape
            thickness = half_size // 4
            # Vertical bar
            draw.rectangle([x-thickness, y-half_size, x+thickness, y+half_size],
                         fill=color, outline=outline_color, width=outline_width)
            # Horizontal bar
            draw.rectangle([x-half_size, y-thickness, x+half_size, y+thickness],
                         fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "arrow":
            # Arrow pointing right
            points = [
                (x-half_size, y-half_size//2),  # left top
                (x, y-half_size//2),            # middle top
                (x, y-half_size),               # tip top
                (x+half_size, y),               # tip point
                (x, y+half_size),               # tip bottom
                (x, y+half_size//2),            # middle bottom
                (x-half_size, y+half_size//2)   # left bottom
            ]
            draw.polygon(points, fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "trapezoid":
            # Trapezoid (wider at bottom)
            top_width = half_size // 2
            points = [
                (x-top_width, y-half_size),     # top left
                (x+top_width, y-half_size),     # top right
                (x+half_size, y+half_size),     # bottom right
                (x-half_size, y+half_size)      # bottom left
            ]
            draw.polygon(points, fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "rhombus":
            # Rhombus (diamond with different proportions)
            points = [
                (x, y-half_size),               # top
                (x+half_size*0.7, y),           # right
                (x, y+half_size),               # bottom
                (x-half_size*0.7, y)            # left
            ]
            draw.polygon(points, fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "octagon":
            # Regular octagon
            points = []
            for i in range(8):
                angle = i * 2 * math.pi / 8
                px = x + half_size * math.cos(angle)
                py = y + half_size * math.sin(angle)
                points.append((px, py))
            draw.polygon(points, fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "crescent":
            # Crescent moon shape (two overlapping circles)
            # Draw larger circle
            draw.ellipse([x-half_size, y-half_size, x+half_size, y+half_size],
                        fill=color, outline=outline_color, width=outline_width)
            # Draw smaller circle to create crescent (using background color)
            offset = half_size // 3
            smaller_radius = int(half_size * 0.7)
            draw.ellipse([x-smaller_radius+offset, y-smaller_radius, x+smaller_radius+offset, y+smaller_radius],
                        fill=(255,255,255), outline=outline_color, width=outline_width)
        
        elif shape == "plus":
            # Plus sign (thicker cross)
            thickness = half_size // 3
            # Vertical bar
            draw.rectangle([x-thickness, y-half_size, x+thickness, y+half_size],
                         fill=color, outline=outline_color, width=outline_width)
            # Horizontal bar
            draw.rectangle([x-half_size, y-thickness, x+half_size, y+thickness],
                         fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "minus":
            # Minus sign (horizontal bar)
            thickness = half_size // 4
            draw.rectangle([x-half_size, y-thickness, x+half_size, y+thickness],
                         fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "L_shape":
            # L shape
            thickness = half_size // 3
            # Vertical part
            draw.rectangle([x-half_size, y-half_size, x-half_size+thickness, y+half_size],
                         fill=color, outline=outline_color, width=outline_width)
            # Horizontal part
            draw.rectangle([x-half_size, y+half_size-thickness, x+half_size, y+half_size],
                         fill=color, outline=outline_color, width=outline_width)
        
        elif shape == "T_shape":
            # T shape
            thickness = half_size // 3
            # Horizontal top part
            draw.rectangle([x-half_size, y-half_size, x+half_size, y-half_size+thickness],
                         fill=color, outline=outline_color, width=outline_width)
            # Vertical part
            draw.rectangle([x-thickness//2, y-half_size, x+thickness//2, y+half_size],
                         fill=color, outline=outline_color, width=outline_width)
    
    def _draw_arrow(self, draw: ImageDraw.Draw, position: Tuple[int, int]):
        """Draw a right-pointing arrow."""
        x, y = position
        length = 40  # Shorter arrows for sequential layout
        
        # Arrow shaft
        draw.line([x-length//2, y, x+length//2-8, y], fill=(0,0,0), width=2)
        
        # Arrow head
        points = [
            (x+length//2, y),
            (x+length//2-10, y-6),
            (x+length//2-10, y+6)
        ]
        draw.polygon(points, fill=(0,0,0))
    
    def _draw_question_mark(self, draw: ImageDraw.Draw, position: Tuple[int, int]):
        """Draw a question mark."""
        x, y = position
        size = self.config.question_mark_size
        
        try:
            font = ImageFont.truetype("arial.ttf", size)
        except:
            font = ImageFont.load_default()
        
        # Get text bounds for centering
        bbox = draw.textbbox((0, 0), "?", font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        
        text_x = x - w // 2
        text_y = y - h // 2
        
        draw.text((text_x, text_y), "?", font=font, fill=(100, 100, 100))
    
    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO GENERATION
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_video(self, first_image: Image.Image, final_image: Image.Image, task_id: str, task_data: Dict[str, Any]) -> str:
        """Generate ground truth video showing the transformation."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Create animation frames
        frames = self._create_transformation_frames(first_image, final_image, task_data)
        
        result = self.video_generator.create_video_from_frames(frames, video_path)
        return str(result) if result else None
    
    def _create_transformation_frames(self, first_image: Image.Image, final_image: Image.Image, task_data: Dict[str, Any], hold_frames: int = 20, step_frames: int = 25) -> List[Image.Image]:
        """Create animation frames showing the two-step sequential transformation."""
        frames = []
        
        # Hold initial state
        for _ in range(hold_frames):
            frames.append(first_image.copy())
        
        # Create two-step animation: first ? then second ?
        frames.extend(self._create_sequential_morph_frames(task_data, step_frames))
        
        # Hold final state
        for _ in range(hold_frames):
            frames.append(final_image.copy())
        
        return frames
    
    def _create_sequential_morph_frames(self, task_data: Dict[str, Any], step_frames: int) -> List[Image.Image]:
        """Create frames showing the sequential two-step transformation."""
        frames = []
        
        width, height = self.config.image_size
        margin = self.config.margin
        base_shape_size = self.config.shape_size
        
        step_width = (width - 2 * margin) // 3
        arrow_offset = step_width // 4
        
        # Calculate improved positions for the question marks that will be revealed
        total_content_width = width - 2 * margin
        step_width = total_content_width // 3
        shape_spacing = step_width * 0.8
        arrow_width = step_width * 0.2
        
        question1_pos = (margin + shape_spacing + arrow_width + shape_spacing//2, 2*height//3)
        question2_pos = (margin + 2*shape_spacing + 2*arrow_width + shape_spacing//2, 2*height//3)
        
        shape_d = task_data["shape_d"]
        color_from = self.colors[task_data["color_from"]]
        color_to = self.colors[task_data["color_to"]]
        scale_from = self.scale_factors[task_data["scale_from"]]
        scale_to = self.scale_factors[task_data["scale_to"]]
        
        # Step 1: Reveal first ? (color change)
        for i in range(step_frames):
            img = self._render_static_elements(task_data, base_shape_size, step_width, arrow_offset, margin, width, height)
            draw = ImageDraw.Draw(img)
            
            # Interpolate color for first question mark
            progress = i / (step_frames - 1) if step_frames > 1 else 1.0
            current_color = (
                int(color_from[0] + (color_to[0] - color_from[0]) * progress),
                int(color_from[1] + (color_to[1] - color_from[1]) * progress),
                int(color_from[2] + (color_to[2] - color_from[2]) * progress)
            )
            current_size = int(base_shape_size * scale_from)  # Keep original scale
            
            # Draw first answer (color changed)
            self._draw_base_shape(draw, shape_d, question1_pos[0], question1_pos[1], current_size, current_color)
            
            # Keep second question mark
            self._draw_question_mark(draw, question2_pos)
            
            frames.append(img)
        
        # Step 2: Reveal second ? (scale change)
        for i in range(step_frames):
            img = self._render_static_elements(task_data, base_shape_size, step_width, arrow_offset, margin, width, height)
            draw = ImageDraw.Draw(img)
            
            # First answer is now complete (color changed)
            first_answer_size = int(base_shape_size * scale_from)
            self._draw_base_shape(draw, shape_d, question1_pos[0], question1_pos[1], first_answer_size, color_to)
            
            # Interpolate scale for second question mark
            progress = i / (step_frames - 1) if step_frames > 1 else 1.0
            current_scale = scale_from + (scale_to - scale_from) * progress
            current_size = int(base_shape_size * current_scale)
            
            # Draw second answer (color + scale changed)
            self._draw_base_shape(draw, shape_d, question2_pos[0], question2_pos[1], current_size, color_to)
            
            frames.append(img)
        
        return frames
    
    def _render_static_elements(self, task_data: Dict[str, Any], base_shape_size: int, step_width: int, arrow_offset: int, margin: int, width: int, height: int) -> Image.Image:
        """Render the static elements that don't change during animation."""
        img = self.renderer.create_blank_image()
        draw = ImageDraw.Draw(img)
        
        # Use same improved spacing as other rendering functions
        total_content_width = width - 2 * margin
        step_width = total_content_width // 3
        shape_spacing = step_width * 0.8
        arrow_width = step_width * 0.2
        
        positions = {
            # Example row (top) - these never change
            "A": (margin + shape_spacing//2, height//3),
            "arrow1": (margin + shape_spacing + arrow_width//2, height//3),
            "B": (margin + shape_spacing + arrow_width + shape_spacing//2, height//3),
            "arrow2": (margin + 2*shape_spacing + arrow_width + arrow_width//2, height//3),
            "C": (margin + 2*shape_spacing + 2*arrow_width + shape_spacing//2, height//3),
            
            # Question row (bottom) - D and arrows are static
            "D": (margin + shape_spacing//2, 2*height//3),
            "arrow3": (margin + shape_spacing + arrow_width//2, 2*height//3),
            "arrow4": (margin + 2*shape_spacing + arrow_width + arrow_width//2, 2*height//3),
        }
        
        # Draw static example sequence: A → B → C
        self._draw_shape_at_position(draw, task_data["shape_a"], positions["A"], base_shape_size, 
                                   task_data["color_from"], task_data["scale_from"])
        self._draw_arrow(draw, positions["arrow1"])
        self._draw_shape_at_position(draw, task_data["shape_b"], positions["B"], base_shape_size, 
                                   task_data["color_to"], task_data["scale_from"])
        self._draw_arrow(draw, positions["arrow2"])
        self._draw_shape_at_position(draw, task_data["shape_c"], positions["C"], base_shape_size, 
                                   task_data["color_to"], task_data["scale_to"])
        
        # Draw static question elements: D and arrows
        self._draw_shape_at_position(draw, task_data["shape_d"], positions["D"], base_shape_size, 
                                   task_data["color_from"], task_data["scale_from"])
        self._draw_arrow(draw, positions["arrow3"])
        self._draw_arrow(draw, positions["arrow4"])
        
        return img
