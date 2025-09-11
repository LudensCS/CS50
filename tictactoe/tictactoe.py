"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None
value = {}


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    cnt = 0
    for row in board:
        for unit in row:
            if unit != EMPTY:
                cnt += 1
    if cnt & 1 == 1:
        return O
    else:
        return X
    # raise NotImplementedError


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    acts = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                acts.add((i, j))
    return acts
    # raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if max(action[0], action[1]) >= 3 or min(action[0], action[1]) < 0 \
            or board[action[0]][action[1]] != EMPTY:
        raise NotImplementedError
    newboard = initial_state()
    for i in range(3):
        for j in range(3):
            newboard[i][j] = board[i][j]
    newboard[action[0]][action[1]] = player(board)
    return newboard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):
        cnt0, cnt1 = 0, 0
        for j in range(3):
            if board[i][j] == X:
                cnt0 += 1
            elif board[i][j] == O:
                cnt1 += 1
        if cnt0 == 3:
            return X
        elif cnt1 == 3:
            return O
        cnt0, cnt1 = 0, 0
        for j in range(3):
            if board[j][i] == X:
                cnt0 += 1
            elif board[j][i] == O:
                cnt1 += 1
        if cnt0 == 3:
            return X
        elif cnt1 == 3:
            return O
    if board[0][0] == board[1][1] and board[1][1] == board[2][2] and board[0][0] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] and board[1][1] == board[2][0] and board[0][2] != EMPTY:
        return board[0][2]
    return None
    # raise NotImplementedError


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    player = winner(board)
    if player != None:
        return True
    acts = actions(board)
    if len(acts) == 0:
        return True
    else:
        return False
    # raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    player = winner(board)
    if player == X:
        return 1
    elif player == O:
        return -1
    else:
        return 0
    # raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    acts = actions(board)
    user = player(board)
    res = 0
    bestact = (None, None)
    if user == X:
        res = -0x3f3f3f3f
    else:
        res = 0x3f3f3f3f
    for act in acts:
        if user == X:
            if getvalue(result(board, act)) > res:
                bestact = act
                res = getvalue(result(board, act))
        else:
            if getvalue(result(board, act)) < res:
                bestact = act
                res = getvalue(result(board, act))
    return bestact
    # raise NotImplementedError


def marshal(board):
    res = ""
    for row in board:
        for unit in row:
            if unit != EMPTY:
                res += unit
            else:
                res += " "
    return res


def getvalue(board):
    """
    Caculate the value of board
    """
    if marshal(board) in value:
        return value[marshal(board)]
    if terminal(board):
        value[marshal(board)] = utility(board)
        return value[marshal(board)]
    user = player(board)
    res = 0
    if user == X:
        res = -0x3f3f3f3f
    else:
        res = 0x3f3f3f3f
    acts = actions(board)
    for act in acts:
        if user == X:
            res = max(res, getvalue(result(board, act)))
        else:
            res = min(res, getvalue(result(board, act)))
    value[marshal(board)] = res
    return res
