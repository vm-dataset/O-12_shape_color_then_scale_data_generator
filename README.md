# Shape Color-Then-Scale Task Generator

A specialized data generator for creating **two-step sequential visual reasoning tasks** where shapes undergo color transformation followed by scale transformation.

## 🎯 Task Format

This generator creates visual analogies in the **A→B→C :: D→?→?** format:

- **Example Sequence (A→B→C)**: Shows the complete two-step transformation
  - **A**: Original shape (e.g., blue small circle)
  - **B**: After step 1 - color change (e.g., red small circle)  
  - **C**: After step 2 - scale change (e.g., red large circle)

- **Question Sequence (D→?→?)**: User must solve both steps
  - **D**: Original shape (e.g., blue small square)
  - **First ?**: Apply step 1 - color change (e.g., red small square)
  - **Second ?**: Apply step 2 - scale change (e.g., red large square)

## 🌟 Key Features

### Sequential Two-Step Transformations
- **Step 1**: Color transformation (blue → red, green → orange, etc.)
- **Step 2**: Scale transformation (small → large, medium → extra_large, etc.)
- **Consistent Pattern**: Both example and question follow identical transformation sequence

### Enhanced Visual Design
- **Optimized Layout**: 800×400 image format for better horizontal spacing
- **Improved Spacing**: 80% space for shapes, 20% for arrows to prevent overlap
- **Clear Separation**: Proper margins between all visual elements
- **Moderate Scaling**: Scale factors from 0.8× to 1.6× to maintain visual clarity

### Rich Animation
- **Two-Step Video**: Shows sequential revelation of both question marks
- **Step 1 Animation**: First ? gradually changes color (25 frames)
- **Step 2 Animation**: Second ? gradually changes scale (25 frames)
- **Smooth Transitions**: Clear visual progression through transformation steps

## 🎨 Visual Elements

### Shapes
- **10 Shape Types**: square, triangle, circle, diamond, pentagon, hexagon, rectangle, oval, star, heart
- **Consistent Style**: All shapes have black outlines for clarity

### Colors
- **6 Distinct Colors**: blue, red, green, orange, purple, teal
- **High Contrast**: Colors chosen for maximum visual distinction

### Scale Levels
- **4 Scale Factors**: small (0.8×), medium (1.0×), large (1.3×), extra_large (1.6×)
- **Balanced Range**: Significant differences while preventing overlap

## 🚀 Quick Start

### Installation
```bash
pip install -e .
```

### Generate Tasks
```bash
python examples/generate.py --num-samples 10 --output data/my_tasks
```

### Configuration
Edit `src/config.py` to customize:
- Image dimensions (default: 800×400)
- Shape sizes and margins
- Video frame rates
- Output settings

## 📁 Output Structure

Each generated task includes:
```
task_id/
├── prompt.txt           # Task instruction
└── ground_truth.mp4     # Animated solution showing both steps
```

## 🎬 Video Animation Sequence

1. **Initial State**: Shows A→B→C :: D→?→? layout
2. **Step 1 Animation**: First ? reveals with color transformation
3. **Step 2 Animation**: Second ? reveals with scale transformation  
4. **Final State**: Complete sequence A→B→C :: D→E→F

## 🔧 Customization

### Adding New Transformations
Modify `valid_transformations` in `src/generator.py`:
```python
self.valid_transformations = [
    ("blue", "red", "small", "large"),      # Color + scale up
    ("red", "blue", "large", "small"),      # Color + scale down
    # Add your combinations...
]
```

### Adjusting Visual Spacing
Update spacing parameters in the rendering functions:
```python
shape_spacing = step_width * 0.8  # 80% for shapes
arrow_width = step_width * 0.2    # 20% for arrows
```

## 🧠 Cognitive Challenge

This task type tests:
- **Sequential Reasoning**: Understanding multi-step transformation patterns
- **Pattern Recognition**: Identifying consistent transformation rules
- **Visual Analysis**: Distinguishing color and scale changes
- **Analogical Thinking**: Applying learned patterns to new shapes

## 📊 Task Complexity

- **Transformation Steps**: 2 (color then scale)
- **Shape Variations**: 10 different shapes
- **Color Combinations**: 12 valid transformation pairs
- **Scale Combinations**: 12 valid transformation pairs
- **Total Unique Tasks**: 10 × 10 × 12 = 1,200 possible combinations

## 🎯 Use Cases

- **Visual Reasoning Research**: Multi-step transformation understanding
- **AI Training Data**: Sequential pattern recognition tasks
- **Cognitive Assessment**: Two-step analogical reasoning evaluation
- **Educational Tools**: Teaching sequential logical thinking

## 🔍 Example Task

**Visual Layout:**
```
blue_small_circle → red_small_circle → red_large_circle
blue_small_square →        ?         →        ?
```

**Solution:**
- First ?: red_small_square (apply color change)
- Second ?: red_large_square (apply scale change)

**Reasoning:** The pattern shows color change first (blue→red), then scale change (small→large). Apply the same sequence to the square.

---

Built with the Template Data Generator framework for creating high-quality visual reasoning datasets.