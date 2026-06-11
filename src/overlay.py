import cv2
import numpy as np

def draw_solution(warped, original_board, solved_board):
    overlay = warped.copy() #creates a copy
    overlay = cv2.resize(overlay, (450, 450))

    cell_size = 450 // 9        #50px per cell
    for row in range(9):
        for col in range(9):
            if original_board[row][col] != 0:
                continue

            value = solved_board[row][col]
            if value == 0:
                continue

            x = col * cell_size + cell_size // 2-8
            y = row * cell_size + cell_size // 2+8

            #func to draw text
            cv2.putText(overlay, str(value),
                         (x, y),        #ocation where text begins
                         cv2.FONT_HERSHEY_SIMPLEX,      #font name
                         0.7,       #controls size
                         (0, 180, 0),       # B G R - color
                         2, cv2.LINE_AA)    #smooth text

    return overlay

def draw_comparison(warped, original_board, solved_board):
    original_side = cv2.resize(warped, (450, 450))
    solved_side   = draw_solution(warped, original_board, solved_board)

    gap = np.ones((450, 20, 3), dtype=np.uint8) * 255
    header_h = 40
    header   = np.ones((header_h, 920, 3), dtype=np.uint8) * 255

    cv2.putText(header, "Original",
                (150, 28), cv2.FONT_HERSHEY_SIMPLEX,
                0.9, (0, 0, 0), 2, cv2.LINE_AA)

    cv2.putText(header, "Solved",
                (610, 28), cv2.FONT_HERSHEY_SIMPLEX,
                0.9, (0, 0, 0), 2, cv2.LINE_AA)

    side_by_side = np.hstack([original_side, gap, solved_side])
    comparison   = np.vstack([header, side_by_side])
    return comparison