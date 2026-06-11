#optical char recognition part 
#digit recognition pipeline 
#takes single cell image => returns (digit, confidence)
import cv2
import numpy as np
from tensorflow.keras.models import load_model


def load_digit_model(model_path="models/sudoku_digit_model.keras"):
    model = load_model(model_path)
    return model

#cell is empty if whiet pixel density is less after thresholding
def is_empty(cell):
    #pxls above the threshold become dark and others become white 
    #otsu helps decide the threshold automatically (useful for varying lighting)

    _, thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    white_pixels = cv2.countNonZero(thresh)
    density = white_pixels/thresh.size 
    if density < 0.04:  #too few white pxl
        return True
    
    if density > 0.6:       #too many white pxl
        return True

    #select largest contour area

    contours,_ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return True
    largest      = max(contours, key=cv2.contourArea)
    largest_area = cv2.contourArea(largest)
    cell_area    = cell.shape[0] * cell.shape[1]


    # Digit must occupy at least 4% of cell area
    if largest_area < cell_area * 0.02:
        return True
    
    #check if the largest contour is rougly digit shaped
    x, y, w, h = cv2.boundingRect(largest)
    aspect = h / w if w > 0 else 99

    #must be tall and wide to be real digit 
    if aspect < 0.5:
        return True
    cell_w = thresh.shape[1]
    if w > cell_w * 0.80:
        return True

    return False


#resize img to fit inside target dimension
def resize_with_padding(img, target_h, target_w):
    h, w = img.shape
    scale = min(target_h/h, target_w/w)
    new_h = int(h * scale)
    new_w = int(w * scale)

    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    canvas = np.zeros((target_h, target_w), dtype = np.uint8)   #creates a black img of the given dimension
    
    #offset values r used to cenetr the digit
    y_off = (target_h - new_h) // 2
    x_off = (target_w - new_w) // 2
    canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized  #places the resized digit at the center
    return canvas


def preprocess_cell(cell):
     #convert grayscale into binary
     _, thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
     
     coords = cv2.findNonZero(thresh)   #returns coords of every white pxl
     if coords is None:
        return None  # blank cell
     
     x,y,w,h = cv2.boundingRect(coords)     #finds the smallest rect covering the digit
     #roi = region of interest
     digit_roi = thresh[y:y+h, x:x+w]
     digit_20 = resize_with_padding(digit_roi, 20, 20)
     
     #place on the canvas center
     canvas = np.zeros((28, 28), dtype=np.uint8)
     canvas[4:24, 4:24] = digit_20
     

     canvas = canvas.astype("float32") / 255.0      #normalized

     return canvas


def recognize_digit(cell, model, confidence_threshold=0.80):
    if is_empty(cell):
        return 0, 1.0
    
    canvas = preprocess_cell(cell)
    if canvas is None:
        return 0, 1.0
    

    #check bounding box aspect ratio
    _, thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    coords = cv2.findNonZero(thresh)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        aspect = h / w if w > 0 else 99

        # Horizontal line = grid artifact, not a digit
        if aspect < 0.3:
            return 0, 1.0

        # Too small to be a real digit
        if w < 3 or h < 3:
            return 0, 1.0


    inp = canvas.reshape(1,28,28,1)
    pred = model.predict(inp, verbose = 0)[0]

    digit = int(np.argmax(pred))
    confidence = float(pred[digit])


    if confidence < confidence_threshold:
        return 0, confidence
    
    return digit, confidence


def recognize_board(cells, model):
    board       = []
    confidences = []

    for row in range(9):
        board_row = []
        conf_row  = []

        for col in range(9):
            digit, conf = recognize_digit(cells[row][col], model)
            board_row.append(digit)
            conf_row.append(conf)

        board.append(board_row)
        confidences.append(conf_row)

    return board, confidences


def print_confidence_report(board, confidences):
    print("\nRecognized Board (digit | confidence):")
    print("-" * 65)

    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 65)

        row_str = ""
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row_str += " | "

            d    = board[r][c]
            conf = confidences[r][c]

            if d == 0:
                row_str += "  .      "
            elif conf < 0.90:
                row_str += f"  {d}({conf:.2f})* "  # * = low confidence
            else:
                row_str += f"  {d}({conf:.2f})  "

        print(row_str)

    print("-" * 65)
    print("* = low confidence cell (possible OCR error)\n")