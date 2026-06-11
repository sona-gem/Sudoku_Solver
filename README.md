# Sudoku OCR Solver

An end-to-end computer vision pipeline that automatically detects, reads and solves Sudoku puzzles from images.

## Pipeline
1. **Grid Detection** — detects the Sudoku grid using contour detection and applies perspective transformation to produce a flat top-down view
2. **Digit Recognition** — segments the grid into 81 cells and recognizes digits using a CNN trained on MNIST + synthetic printed digits
3. **Solver** — solves the puzzle using a recursive backtracking algorithm
4. **Overlay** — draws the solution back onto the original grid image

## Tech Stack

- Python 3.1x
- OpenCV — grid detection, perspective transform, cell segmentation
- TensorFlow / Keras — CNN digit recognition
- NumPy — array operations
- Pillow — synthetic digit generation for training
- SciPy — image augmentation

## Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/SUDOKU_SOLVER.git
cd SUDOKU_SOLVER

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Train the model 
python -m src.train

# Run on an image
python main.py data/sudoku2.jpg
```

## Model Training

The CNN is trained on:
- **MNIST** handwritten digits (54,000 samples, digits 1-9)
- **Synthetic printed digits** (7,200 samples) generated using system fonts to bridge the domain gap between handwritten MNIST and printed Sudoku digits

Training achieves ~99.6% test accuracy on MNIST.

## Limitations

- Designed for **printed Sudoku puzzles**
- Handwritten puzzles with textured/noisy backgrounds are not currently supported
- Works best with clear, well-lit images where the grid is the dominant element
