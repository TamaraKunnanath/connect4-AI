import numpy as np
import random
import pygame
import sys
import math

#### MACROS ####

RED = (237, 37, 78)
YELLOW = (249, 220, 92)
BLUE = (34, 108, 224)
BLACK = (0, 0, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

option_to_remove = True
comp_vs_comp = False
h1 = True
game_over = False
board = np.zeros((ROW_COUNT, COLUMN_COUNT))

#### SETUP ####

game_type = int(input("How many AIs? Type 1 or 2: "))
if game_type == 2:
    comp_vs_comp = True

option = input("Type no if you don't want the option to remove, else any key: ")
if option_to_remove == "no":
    option_to_remove = False

heuristic = int(input("Offensive (1) or defensive (2) heuristic? "))
if heuristic == 2:
    h1 == False


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def remove_bottom_peg(board, col):
    for i in range(0, 5):
        board[i, col] = board[i+1, col]

def is_valid_location(board, col):
    return not np.all(board[:, col])


def can_remove(board, col, piece):
    return board[0][col] == piece


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 10
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 4

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 6

    return score


def defence(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 10
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 4:
        score -= 50
    elif window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 9
    elif window.count(opp_piece) == 2 and window.count(EMPTY) == 2:
        score -= 1

    return score


def score_position(board, piece):
    score = 0
    block = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)
            block += defence(window, piece)

    # Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)
            block += defence(window, piece)

    # Score diagonals
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
            block += defence(window, piece)

    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
            block += defence(window, piece)

    if h1:
        return score
    return block


def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0


def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -np.inf
        column = random.choice(valid_locations)
        
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]

            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)

            if alpha >= beta:
                break

        return column, value

    else:  # Minimizing player
        value = np.inf
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]

            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)

            if alpha >= beta:
                break

        return column, value


def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def get_valid_removals(board, piece):
    valid_removals = []
    for col in range(COLUMN_COUNT):
        if can_remove(board, col, piece):
            valid_removals.append(col)
    return valid_removals


def pick_best_move(board, piece):

    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)

    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)

        if score > best_score:
            best_score = score
            best_col = col

    return best_col


def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r *
                                            SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(
                c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(
                    c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(
                    c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()


pygame.init()

screen = pygame.display.set_mode(size)
print_board(board)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("ariel", 75)

turn = PLAYER

if not comp_vs_comp:
    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == PLAYER:
                    pygame.draw.circle(
                        screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)

            pygame.display.update()
            
            if turn == PLAYER:

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))

                        col = int(math.floor(posx/SQUARESIZE))

                        if can_remove(board, col, PLAYER_PIECE):
                            row = 0
                            remove_bottom_peg(board, col)

                            if winning_move(board, PLAYER_PIECE):
                                label = myfont.render("Player wins!", 1, RED)
                                screen.blit(label, (40, 40))
                                game_over = True

                            turn += 1
                            turn = turn % 2

                            print_board(board)
                            draw_board(board)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))

                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE)

                        if winning_move(board, PLAYER_PIECE):
                            label = myfont.render("Player wins!", 1, RED)
                            screen.blit(label, (40, 40))
                            game_over = True

                        turn += 1
                        turn = turn % 2

                        print_board(board)
                        draw_board(board)

        if turn == AI and not game_over:
            col, minimax_score = minimax(board, 5, -np.inf, np.inf, True)

            if is_valid_location(board, col):

                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)

                if winning_move(board, AI_PIECE):
                    label = myfont.render("AI wins!", 1, YELLOW)
                    screen.blit(label, (40, 40))
                    game_over = True

                print_board(board)
                draw_board(board)

                turn += 1
                turn = turn % 2

        pygame.time.wait(500)

        if game_over:
            pygame.time.wait(3000)

else:
    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        if turn == PLAYER:

            chance = random.randint(0,10)
            col = random.randint(0, COLUMN_COUNT-1)

            if chance < 4:
                if len(get_valid_removals(board,PLAYER_PIECE)) > 0:
                    col = get_valid_removals(board, PLAYER_PIECE)[0]
                    remove_bottom_peg(board, col)
                    
                    print_board(board)
                    draw_board(board)

                    turn += 1
                    turn = turn % 2

            elif is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, PLAYER_PIECE)

                if winning_move(board, AI_PIECE):
                    label = myfont.render("Dumb AI wins!", 1, RED)
                    screen.blit(label, (40, 10))
                    game_over = True

                print_board(board)
                draw_board(board)

                turn += 1
                turn = turn % 2

            elif option_to_remove and can_remove(board, col, PLAYER_PIECE):
                remove_bottom_peg(board, col)
                print_board(board)
                draw_board(board)

                turn += 1
                turn = turn % 2

        if turn == AI and not game_over:

            col, minimax_score = minimax(
                board, 5, -np.inf, np.inf, True)

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)

                if winning_move(board, AI_PIECE):
                    label = myfont.render("Smart AI wins!", 1, YELLOW)
                    screen.blit(label, (40, 10))
                    game_over = True

                print_board(board)
                draw_board(board)

                turn += 1
                turn = turn % 2

        pygame.time.wait(500)

        if game_over:
            pygame.time.wait(3000)
