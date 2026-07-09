#grid detection and segmentation pipeline 
#takes image => finds the puzzle => straighten it => splits into 81 cells
import cv2
import numpy as np



#for contour detection
def preprocess(image):      
    #image => grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    denoised = cv2.bilateralFilter(gray, 9, 75,75)      #remove noise & preserve edges (diameter of pixel neighbourhood, color similaruty threshold, spatial dist thresh)
    
    #converts img to balck & white 
    #white becomes 255 , thresh => computed from neighbourhood 
    #Inverse => dark = white & bright = black (grid lines become white), block size 11x11
    thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11,2)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))   #3x3 rect kernel used for morphological ops
    
    #connect broken grid lines , strengthen contour
    dilated = cv2.dilate(thresh, kernel, iterations =1)
    
    
    return dilated      #returns binary image

#find grid
def find_grid_contour(image, thresh):
    #RETR_EXTERNAL  -only retrieves outer contours
    #CHAIN_APPROX_SIMPLE - compress to 4 contour points 
    contours,_ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    image_area = image.shape[0] * image.shape[1]        
    candidates = []         #store all possible valid quadilaterals

    for c in contours:
        area = cv2.contourArea(c)
        if area < image_area * 0.10:    #must occupy atleast 10% of image
            continue
        peri = cv2.arcLength(c, True)

        approx = cv2.approxPolyDP(c, 0.02*peri, True)       #simplifies contour shape
        if len(approx) == 4:

            #check how much does this quadilateral resemble a square
            pts= approx.reshape(4,2).astype("float32")
            pts = order_points(pts)
            (tl,tr,br,bl) = pts

            width_a  = np.linalg.norm(br - bl)
            width_b  = np.linalg.norm(tr - tl)
            height_a = np.linalg.norm(tr - br)
            height_b = np.linalg.norm(tl - bl)

            avg_w = (width_a  + width_b)  / 2
            avg_h = (height_a + height_b) / 2

            squareness = min(avg_w, avg_h) / max(avg_w, avg_h) if max(avg_w, avg_h) > 0 else 0
            if squareness < 0.7:
                continue
            candidates.append((area, squareness, approx))
        
    if not candidates:
        raise ValueError(
            "No Sudoku grid found. "
            "Check that the puzzle is clearly visible and well-lit."
        )
    #sort by squareness then area
    candidates.sort(key = lambda x: (round(x[1], 1), x[0]), reverse=True)

    return candidates[0][2]     #return candidate with largest area


#ordering the corner points (top left, top right, bottom right, bottom left)
def order_points(pts):
    pts = pts.reshape(4,2).astype("float32")    #numpy array with 4 rows & 2 cols
    s = pts.sum(axis=1)         #x+y (sum of coordinates)
    ordered = np.zeros((4,2), dtype = "float32")

    ordered[0] = pts[np.argmin(s)]      #smallest x+y
    ordered[2] = pts[np.argmax(s)]      #max x+y

    diff = np.diff(pts, axis=1)
    ordered[1] = pts[np.argmin(diff)]   #min y-x
    ordered[3] = pts[np.argmax(diff)]   #max y-x

    return ordered


#straighten the board
def four_point_transform(image, contour):
    pts = order_points(contour)
    (tl, tr, br, bl) = pts

    def shrink(pt_a, pt_b, amount =8):
        direction = pt_b - pt_a
        length = np.linalg.norm(direction)
        if length == 0:
            return pt_a, pt_b
        unit = direction/ length 
        return pt_a + unit * amount , pt_b - unit * amount
    

    tl, br = shrink(tl, br)
    tr, bl = shrink(tr, bl)

    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_width = max(int(width_a), int(width_b))

    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_height = max(int(height_a), int(height_b))


    side = max(max_width, max_height)
    src = np.array([tl, tr, br, bl], dtype="float32")

    #coordinates of the perfect rect
    dst = np.array([[0,0], [side-1, 0],[side-1, side-1],[0, side-1]], dtype ="float32")

    M = cv2.getPerspectiveTransform(src, dst)   #transformation matrix

    #wrap image
    warped = cv2.warpPerspective(image, M, (side, side))

    return warped       #from titled to perfect sq


#cell segmentation
def segment_cells(warped):
    warped = cv2.resize(warped, (450, 450))
    gray  = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
  
    cell_size = 450//9      #50px per cell
      

    cells = []
    for row in range(9):
        row_cells = []
        for col in range(9):

            #use larger margin fro cells on 3x3 box boundaries
            top_margin = 6 if row%3 ==0 else 4
            bottom_margin = 6 if (row+1)%3 == 0 else 4
            left_margin = 6 if (col%3) == 0 else 4
            right_margin =6 if (col+1)%3 ==0 else 4


            y1 = row * cell_size + top_margin
            y2 = (row +1)* cell_size - bottom_margin

            x1 = col * cell_size + left_margin
            x2 = (col+1)* cell_size - right_margin

            cell = gray[y1:y2, x1:x2]           #slices the image
            row_cells.append(cell)
        cells.append(row_cells)
    return cells



#main pipeline 
#this function will accept a numpy array directly 
#this numpy array will be used by flask api which receives images as bytes
def detect_grid_from_array(image):
    
    if image is None:
        raise ValueError("Image array is None")
    
    image = cv2.resize(image, (900, 900))
    thresh = preprocess(image)
    contour = find_grid_contour(image, thresh)
    warped = four_point_transform(image, contour)
    cells = segment_cells(warped)

    return warped, cells

