# Flask API for Sudoku OCR Solver
# Endpoint: POST /api/solve
# Input: image file
# Output: original board, solved board, overlay image (base64)

import resource
import os
import copy
import time
import base64
import numpy as np
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add parent directory to path so we can import src/
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.grid_detector    import detect_grid_from_array
from src.digit_recognizer import load_digit_model, recognize_board
from src.solver           import validate_board, solve, verify_solution
from src.overlay          import draw_solution

app    = Flask(__name__)
CORS(app)  # allow requests from Vercel frontend

# Load model once at startup — not on every request
print("Loading model...")
model = load_digit_model()
print("Model loaded ✅")
print(f"Memory after model load: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024} MB")


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Sudoku Solver API"})


@app.route("/api/solve", methods=["POST"])
def solve_sudoku():
    # ── 1. Validate request ──────────────────────────────
    if "image" not in request.files:
        return jsonify({
            "success": False,
            "error"  : "No image provided"
        }), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({
            "success": False,
            "error"  : "Empty filename"
        }), 400

    # ── 2. Read image from upload ────────────────────────
    file_bytes = np.frombuffer(file.read(), np.uint8)
    image      = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({
            "success": False,
            "error"  : "Could not decode image"
        }), 400

    # ── 3. Detect grid ───────────────────────────────────
    try:
        warped, cells = detect_grid_from_array(image)
    except ValueError as e:
        return jsonify({
            "success": False,
            "error"  : f"Grid detection failed: {str(e)}"
        }), 422

    # ── 4. Recognize digits ──────────────────────────────
    board, confidences = recognize_board(cells, model)

    # ── 5. Validate board ────────────────────────────────
    try:
        validate_board(board)
    except ValueError as e:
        return jsonify({
            "success"   : False,
            "error"     : f"OCR conflict: {str(e)}",
            "board"     : board,
            "confidences": confidences
        }), 422

    # ── 6. Solve ─────────────────────────────────────────
    solved  = copy.deepcopy(board)
    start   = time.time()
    success = solve(solved)
    elapsed = (time.time() - start) * 1000

    if not success:
        return jsonify({
            "success": False,
            "error"  : "No solution exists — likely an OCR error",
            "board"  : board
        }), 422

    if not verify_solution(solved):
        return jsonify({
            "success": False,
            "error"  : "Solver produced invalid solution — OCR missed a clue",
            "board"  : board
        }), 422

    # ── 7. Generate overlay image ─────────────────────────
    overlay    = draw_solution(warped, board, solved)
    overlay    = cv2.resize(overlay, (450, 450))

    # Encode overlay as base64 so we can send it in JSON
    _, buffer  = cv2.imencode(".png", overlay)
    img_base64 = base64.b64encode(buffer).decode("utf-8")

    # Also encode original warped for comparison
    warped_resized = cv2.resize(warped, (450, 450))
    _, buffer2     = cv2.imencode(".png", warped_resized)
    orig_base64    = base64.b64encode(buffer2).decode("utf-8")

    # ── 8. Return response ───────────────────────────────
    return jsonify({
        "success"       : True,
        "original_board": board,
        "solved_board"  : solved,
        "confidences"   : confidences,
        "solve_time_ms" : round(elapsed, 2),
        "original_image": orig_base64,
        "solved_image"  : img_base64
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
