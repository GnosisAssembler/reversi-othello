import random
import sys

# Prints out the board that it was passed
def drawBoard(board):
    BORDER = '  +---+---+---+---+---+---+---+---+'
    COLUMNS = '  |   |   |   |   |   |   |   |   |'

    print('    1   2   3   4   5   6   7   8')
    print(BORDER)
    for y in range(8):
        print(COLUMNS)
        print(y+1, end=' ')
        for x in range(8):
            print('| %s' % (board[x][y]), end=' ')
        print('|')
        print(COLUMNS)
        print(BORDER)

# Resets all the positions of the board except for the starting ones
def resetBoard(board):
    for x in range(8):
        for y in range(8):
            board[x][y] = ' '

    # Starting pieces:
    board[3][3] = 'X'
    board[3][4] = 'O'
    board[4][3] = 'O'
    board[4][4] = 'X'

# Creates a new, blank board data structure
def getNewBoard():
    board = []
    for i in range(8):
        board.append([' '] * 8)
    return board

# Returns False if the player's move is invalid
# If it is a valid move, returns a list of spaces that would become the player's if they made a move here
def isValidMove(board, tile, xstart, ystart):
    if board[xstart][ystart] != ' ' or not isOnBoard(xstart, ystart):
        return False

    board[xstart][ystart] = tile # temporarily set the tile on the board

    if tile == 'X':
        otherTile = 'O'
    else:
        otherTile = 'X'

    tilesToFlip = []
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection # first step in the direction
        y += ydirection # first step in the direction
        if isOnBoard(x, y) and board[x][y] == otherTile:
            # There is a piece belonging to the other player next to our piece
            x += xdirection
            y += ydirection
            if not isOnBoard(x, y):
                continue
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not isOnBoard(x, y): # break out of while loop, then continue in for loop
                    break
            if not isOnBoard(x, y):
                continue
            if board[x][y] == tile:
                # There are pieces to flip over. Go in the reverse direction until we reach the original space, noting all the tiles along the way.
                while True:
                    x -= xdirection
                    y -= ydirection
                    if x == xstart and y == ystart:
                        break
                    tilesToFlip.append([x, y])

    board[xstart][ystart] = ' ' # restore the empty space
    if len(tilesToFlip) == 0: # If no tiles were flipped, this is not a valid move.
        return False
    return tilesToFlip

# Returns True if the coordinates are located on the board.
def isOnBoard(x, y):
    return x >= 0 and x <= 7 and y >= 0 and y <=7

# Returns a list of [x,y] lists of valid moves for the given player on the given board
def getValidMoves(board, tile):
    validMoves = []
    for x in range(8):
        for y in range(8):
            if isValidMove(board, tile, x, y) != False:
                validMoves.append([x, y])
    return validMoves

# Determine the score by counting the tiles. Returns a dictionary with keys 'X' and 'O'
def getScoreOfBoard(board):
    xscore = 0
    oscore = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] == 'X':
                xscore += 1
            if board[x][y] == 'O':
                oscore += 1
    return {'X':xscore, 'O':oscore}

# Lets the player type which tile they want to be.
# Returns a list with the player's tile as the first item, and the computer's tile as the second
def enterPlayerTile():
    tile = ''
    while not (tile == 'X' or tile == 'O'):
        print('Do you want to be X (black) or O (white)?')
        tile = input().upper()

    # the first element in the tuple is the player's tile, the second is the computer's tile
    if tile == 'X':
        return ['X', 'O']
    else:
        return ['O', 'X']

# Asks the player who goes first
def whoGoesFirst():
    print('Do you want to play first? Y or N?')
    answer = input().upper()
    if answer == "Y":
        return 'player'
    else:
        return 'computer'

# Place the tile on the board at xstart, ystart, and flip any of the opponent's pieces.
# Returns False if this is an invalid move, True if it is valid.
def makeMove(board, tile, xstart, ystart):
    tilesToFlip = isValidMove(board, tile, xstart, ystart)

    if tilesToFlip == False:
        return False

    board[xstart][ystart] = tile
    for x, y in tilesToFlip:
        board[x][y] = tile
    return True

# Make a duplicate of the board list and return the duplicate.
def getBoardCopy(board):
    dupeBoard = getNewBoard()

    for x in range(8):
        for y in range(8):
            dupeBoard[x][y] = board[x][y]

    return dupeBoard

# Returns True if the position is in one of the four corners.
def isOnCorner(x, y):
    return (x == 0 and y == 0) or (x == 7 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 7)

# Let the player type in their move.
# Returns the move as [x, y] (or returns the string 'quit')
def getPlayerMove(board, playerTile):
    COLUMN_NUMBERS = '1 2 3 4 5 6 7 8'.split()
    while True:
        print('Enter your move (first the x axis and then the y axis), or type quit to end the game.')
        move = input().lower()
        if move == 'quit':
            return 'quit'

        if len(move) == 2 and move[0] in COLUMN_NUMBERS and move[1] in COLUMN_NUMBERS:
            x = int(move[0]) - 1
            y = int(move[1]) - 1
            if isValidMove(board, playerTile, x, y) == False:
                continue
            else:
                break
        else:
            print('That is not a valid move. Type the x digit (1-8), then the y digit (1-8).')
            print('For example, 81 will be the top-right corner.')

    return [x, y]

# Given a board, the computer's tile and the depth (user's input) 
# determine where to move using Mini Max
# and return that move as a [x, y] list.
def getComputerMove(board, computerTile, depth):
    possibleMoves = getValidMoves(board, computerTile)

    # algorithm depth
    ai_range = int(depth) + 1

    # randomize the order of the possible moves
    random.shuffle(possibleMoves)

    # always go for a corner if available.
    for x, y in possibleMoves:
        if isOnCorner(x, y):
            return [x, y]

    # Go through all the possible moves and remember the best scoring move
    # according to user's given depth
    #if ai_range >= len(possibleMoves):
        bestScore = -1
        for x, y in possibleMoves:
            dupeBoard = getBoardCopy(board)
            makeMove(dupeBoard, computerTile, x, y)
            score = getScoreOfBoard(dupeBoard)[computerTile]
            if score > bestScore:
                bestMove = [x, y]
                bestScore = score
    #else:
    #    for x, y in range(ai_range):
    #        dupeBoard = getBoardCopy(board)
    #        makeMove(dupeBoard, computerTile, x, y)
    #        score = getScoreOfBoard(dupeBoard)[computerTile]
    #        if score > bestScore:
    #            bestMove = [x, y]
    #            bestScore = score
    return bestMove

# Prints out the current score.
def showPoints(playerTile, computerTile):
    scores = getScoreOfBoard(mainBoard)
    print('You have %s points. The computer has %s points.' % (scores[playerTile], scores[computerTile]))


#===========================================================
# START THE GAME
print('Welcome to Reversi Game. I am a smart AI and i am going to beat you. Lets play!')

while True:
    # Init the board and game.
    mainBoard = getNewBoard()
    resetBoard(mainBoard)
    playerTile, computerTile = enterPlayerTile()
    turn = whoGoesFirst()
    print('Enter a number how far the Algorith you want to go.')
    depth = input()
    print('The ' + turn + ' will go first.')

    while True:
        if turn == 'player':
            # Player's turn.
            drawBoard(mainBoard)
            showPoints(playerTile, computerTile)
            move = getPlayerMove(mainBoard, playerTile)
            if move == 'quit':
                print('Ohh too bad! Too scared to face me huh?')
                sys.exit() # terminate the program
            else:
                makeMove(mainBoard, playerTile, move[0], move[1])

            if getValidMoves(mainBoard, computerTile) == []:
                break
            else:
                turn = 'computer'

        else:
            # Computer's turn.
            drawBoard(mainBoard)
            showPoints(playerTile, computerTile)
            input('Press Enter to see the computer\'s move.')
            x, y = getComputerMove(mainBoard, computerTile, depth)
            makeMove(mainBoard, computerTile, x, y)

            if getValidMoves(mainBoard, playerTile) == []:
                break
            else:
                turn = 'player'

    # Display the final score.
    drawBoard(mainBoard)
    scores = getScoreOfBoard(mainBoard)
    print('X scored %s points. O scored %s points.' % (scores['X'], scores['O']))
    if scores[playerTile] > scores[computerTile]:
        print('You beat the computer by %s points! Congratulations!' % (scores[playerTile] - scores[computerTile]))
        break
    elif scores[playerTile] < scores[computerTile]:
        print('You lost. The computer beat you by %s points.' % (scores[computerTile] - scores[playerTile]))
        break
    else:
        print('The game was a tie!')
        break