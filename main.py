#full pipeline
#image => detect grid => recognize digits => solve => overlay sol


import copy
import sys
import cv2
import matplotlib.pyplot as plt

from src.grid_detector import detect_grid
from src.digit_recognizer import load_digit_model, recognize_board, print_confidence_report
from src.solver import validate_board, solve, print_board, verify_solution
from src.overlay import draw_solution, draw_comparison


def run(image_path):
    #detect grid
    try:
        warped, cells = detect_grid(image_path)
        print("      Grid detected")
    except (FileNotFoundError, ValueError) as e:
        print(f"    Failed - {e}")
        return
    

    #digit recognition
    model = load_digit_model()
    board, confidences = recognize_board(cells, model)
    print_confidence_report(board, confidences) 

    try:
        validate_board(board)
        print("     Board valid")
    except ValueError as e :
        print(f"    OCR conflict detected - {e}")
        print(f"    Cannot solve - check confidence report")
        return 
    

    solved = copy.deepcopy(board)
    success = solve(solved)

    if not success:
        print("     no sol exist")
        print("     likely OCR error in a high confidence cell")
        return 

    if not verify_solution(solved):
        print("      Solver produced invalid solution")
        print("      This means OCR missed a clue — check confidence report")
        print("\nOriginal Board (as recognized):")
        print_board(board)
        return


    print("\nOriginal Board")
    print_board(board)
    print("\nSolved Board: ")
    print_board(solved)

    #overlay
    comparison = draw_comparison(warped, board, solved)

    #show result
    plt.figure(figsize=(12, 6))
    plt.imshow(cv2.cvtColor(comparison, cv2.COLOR_BGR2RGB))
    plt.title("Original vs Solved")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <image_path>")
    else:
        run(sys.argv[1])
        