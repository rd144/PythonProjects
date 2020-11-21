from math import isqrt
from random import sample


#TODO - Understand the code
#TODO - Run to large dataset
#TODO - Figure out if I can adjust the difficulty

def board_creation(base):

    side = base * base

    # pattern for a baseline valid solution
    def pattern(r, c): return (base * (r % base) + r // base + c) % side

    # randomize rows, columns and numbers (of valid base pattern)
    def shuffle(s): return sample(s, len(s))

    rBase = range(base)
    rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
    cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
    nums = shuffle(range(1, base * base + 1))

    # produce board using randomized baseline pattern
    board = [[nums[pattern(r, c)] for c in cols] for r in rows]

    return board

def validate(board):
    """
    Ruleset is as follows:
        1. No non-zero duplicates in a row
        2. No non-zero duplicates in a column
        3. The numbers in the subset NxN grids must include every number up to N^2
    :param board:
    :return True/False: Setting where True indicates a valid board and False an Invalid one
    """

    for index, row in enumerate(board):

        row_check = any(row.count(element) > 1 for element in row if element != 0)
        if row_check:
            print("Row Failure : {0}".format(index))
            return False

        column = [row[index] for row in board]
        column_check = any(column.count(element) > 1 for element in column if element != 0)
        if column_check:
            print("Column Failure : {0}".format(index))
            return False


    if len(board) == len(board[0]):

        square_lists = []
        root = isqrt(len(board))

        for row in board:

            squares = [row[i * root:(i + 1) * root] for i in range((len(row) + root - 1) // root)]

            for index,square in enumerate(squares):
                if len(square_lists) < len(squares):
                    square_lists.append([])

                square_lists[index].append(square)

        for square in square_lists:
            square_row = []
            for item in square:
                square_row.extend(item)
                if len(square_row) >= len(board):
                    square_check = any(square_row.count(element) > 1 for element in square_row if element != 0)
                    square_row = []
                    if square_check:
                        print("Square Failure")
                        print(square)
                        return False

    return True

def number_removal(board):

    side = len(board)
    squares = side * side
    empties = squares * 3 // 4
    for p in sample(range(squares), empties):
        board[p // side][p % side] = 0

    return board

"""
Generate N sudoku puzzles, train against validation
Iterate and generate a further N puzzles
Continue until it can solve the puzzles itself
"""

solution = board_creation(3)
board = number_removal(solution)

for line in board:
    print(line)
