def isSafe(board, dig, row, col):

    #horizontally
    if dig in board[row]:
        return False
    #vertically
    for i in range(9):
        if dig == board[i][col]:
            return False
    
    #check the 3x3 grid
    srow = (row//3)*3
    scol = (col//3)*3
    for i in range(srow, srow+3):
        for j in range(scol, scol+3):
            if board[i][j] == dig:
                return False

    return True


def find_empty(board):     
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return(row, col)
    return None


def solve(board):   #using recursive backtracking
    empty = find_empty(board)

    if empty == None:
        return True         # means all cells are solved
    
    row, col = empty 

    for num in range(1,10):
        if isSafe(board, num, row, col):
            board[row][col] = num
            if solve(board):
                return True
            board[row][col] = 0     #backtrack

    return False

#identify duplicate values from the OCR step before solving 
def validate_board(board):
    #check rows
    for row in range(9):
        vals = []
        for val in board[row]:
            if val != 0:
                vals.append(val)
        if len(vals) != len(set(vals)):
            raise ValueError(f"Duplicate in the row {row}: {vals}")
        
    #check cols
    for col in range(9):        #sinec we r checking col cols must beb constant
        vals =[]
        for row in range(9):
            if board[row][col] != 0:
                vals.append(board[row][col])
        if len(vals) != len(set(vals)):
            raise ValueError(f"Duplicate in the col {col}: {vals}")
        

    #check the 3x3 grid
    for br in range(3):
        for bc in range(3):
            vals = []
            for i in range(3):
                for j in range(3):
                    if board[br*3+i][bc*3+j] != 0:
                        vals.append(board[br*3+i][bc*3+j])
            if len(vals) != len(set(vals)):
                raise ValueError(f"Duplicate in the box ({br}, {bc}): {vals}")
    return True


def verify_solution(board):
    expected = set(range(1, 10))

    #check rows
    for i in range(9):
        if set(board[i]) !=  expected:
            return False
    
    #check cols
    for c in range(9):
        col = [board[r][c] for r in range(9)]
        if set(col) != expected:
            return False
        
    #check 3x3 grid
    for br in range(3):
        for bc in range(3):
            box = [board[br*3+i][bc*3+j] 
                   for i in range(3)
                   for j in range(3)]
            if set(box) != expected:
                return False
    return True

def print_board(board):
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("-" * 25)
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")
            print(board[i][j], end=" ")
        print()  