"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None

utility_map = {X: 1, O: -1, EMPTY: 0}


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
    total = 0
    for i in range(len(board)):
        for j in range(len(board)):
            total = total + utility_map[board[i][j]]

    # If they cancel out then equal number so X's turn
    if total == 0:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    all_actions = set()

    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == EMPTY:
                all_actions.add((i, j))
    return all_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if board[action[0]][action[1]] != EMPTY:
        raise RuntimeError("Invalid action on board")
    else:
        player_id = player(board)
        new_board = copy.deepcopy(board)
        new_board[action[0]][action[1]] = player_id
        return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(len(board)):

        # Check rows
        if board[i][0] == board[i][1] == board[i][2] and not board[i][1] == EMPTY:
            return board[i][1]

        # Check columns
        elif board[0][i] == board[1][i] == board[2][i] and not board[1][i] == EMPTY:
            return board[1][i]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and not board[1][1] == EMPTY:
        return board[1][1]

    if board[2][0] == board[1][1] == board[0][2] and not board[1][1] == EMPTY:
        return board[1][1]

    # No winner if get to this point
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # If winner game is over
    if winner(board) is not None:
        return True
    else:
        # Check number of blanks remaining, if any left and no winner game is not over
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == EMPTY:
                    return False
        return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    return utility_map[winner(board)]


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    player_id = player(board)
    best_score = -math.inf if player_id == X else math.inf
    optimal_action = None

    for action in actions(board):
        if player_id == X:
            this_score = min_score(result(board, action))
            if this_score > best_score:
                optimal_action = action
                best_score = this_score
        else:
            this_score = max_score(result(board, action))
            if this_score < best_score:
                optimal_action = action
                best_score = this_score
    return optimal_action


def max_score(board):

    if terminal(board):
        return utility(board)

    best_score = -math.inf
    for action in actions(board):
        best_score = max(best_score, min_score(result(board, action)))
    return best_score


def min_score(board):

    if terminal(board):
        return utility(board)

    best_score = math.inf
    for action in actions(board):
        best_score = min(best_score, max_score(result(board, action)))
    return best_score
