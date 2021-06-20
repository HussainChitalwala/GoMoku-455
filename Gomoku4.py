#!/usr/bin/env python
#/usr/local/bin/python3
# Set the path to your python3 above

from gtp_connection import GtpConnection
from board_util import PASS, EMPTY, BLACK, WHITE, GoBoardUtil
from simple_board import SimpleGoBoard

import random
import numpy as np

def undo(board,move):
    board.board[move]=EMPTY
    board.current_player=GoBoardUtil.opponent(board.current_player)

def play_move(board, move, color):
    board.play_move_gomoku(move, color)

def game_result(board):
    game_end, winner = board.check_game_end_gomoku()
    moves = board.get_empty_points()
    board_full = (len(moves) == 0)
    if game_end:
        #return 1 if winner == board.current_player else -1
        return winner
    if board_full:
        return 'draw'
    return None

class GomokuSimulationPlayer(object):
    """
    For each move do `n_simualtions_per_move` playouts,
    then select the one with best win-rate.
    playout could be either random or rule_based (i.e., uses pre-defined patterns) 
    """
    def __init__(self, n_simualtions_per_move=10, playout_policy='random', board_size=7):
        assert(playout_policy in ['random', 'rule_based'])
        self.n_simualtions_per_move=n_simualtions_per_move
        self.board_size=board_size
        self.playout_policy=playout_policy

        #NOTE: pattern has preference, later pattern is ignored if an earlier pattern is found
        self.pattern_list=['Win', 'BlockWin', 'OpenFour', 'BlockOpenFour', 'Random']

        self.name="Gomoku3"
        self.version = 3.0
        self.best_move=None
    
    def set_playout_policy(self, playout_policy='random'):
        assert(playout_policy in ['random', 'rule_based'])
        self.playout_policy=playout_policy

    def _random_moves(self, board, color_to_play):
        return GoBoardUtil.generate_legal_moves_gomoku(board)
    
    def policy_moves(self, board, color_to_play):
        if(self.playout_policy=='random'):
            return "Random", self._random_moves(board, color_to_play)
        else:
            assert(self.playout_policy=='rule_based')
            assert(isinstance(board, SimpleGoBoard))
            ret=board.get_pattern_moves()
            if ret is None:
                return "Random", self._random_moves(board, color_to_play)
            movetype_id, moves=ret
            return self.pattern_list[movetype_id], moves
    
    def _do_playout(self, board, color_to_play):
        res=game_result(board)
        simulation_moves=[]
        while(res is None):
            _ , candidate_moves = self.policy_moves(board, board.current_player)
            playout_move=random.choice(candidate_moves)
            play_move(board, playout_move, board.current_player)
            simulation_moves.append(playout_move)
            res=game_result(board)
        for m in simulation_moves[::-1]:
            undo(board, m)
        if res == color_to_play:
            return 1.0
        elif res == 'draw':
            return 0.0
        else:
            assert(res == GoBoardUtil.opponent(color_to_play))
            return -1.0

    def get_move(self, board, color_to_play):
        """
        The genmove function called by gtp_connection
        """
        '''moves=GoBoardUtil.generate_legal_moves_gomoku(board)
        toplay=board.current_player
        best_result, best_move=-1.1, None
        best_move=moves[0]
        wins = np.zeros(len(moves))
        visits = np.zeros(len(moves))
        while True:
            for i, move in enumerate(moves):
                play_move(board, move, toplay)
                res=game_result(board)
                if res == toplay:
                    undo(board, move)
                    #This move is a immediate win
                    self.best_move=move
                    return move
                ret=self._do_playout(board, toplay)
                wins[i] += ret
                visits[i] += 1
                win_rate = wins[i] / visits[i]
                if win_rate > best_result:
                    best_result=win_rate
                    best_move=move
                    self.best_move=best_move
                undo(board, move)
        assert(best_move is not None)
        return best_move'''
        b = GoBoardUtil.get_twoD_board(board)
        s = len(b)+1
        rem_moves = board.get_empty_points()
        rem_moves_alpha = []
        for move in rem_moves:
            rem_moves_alpha.append(chr(ord('A') + move%s - 1) + str(move // s))
        if len(rem_moves) == 49:
            return "D4"
        if len(rem_moves) == 1: 
            # If the board has only 1 open piece, you can play only there. 
            return rem_moves_alpha[0]
        result = self.solve_cmd(board)
        if len(result) > 0:
            return result
        '''move_score_dict = {}
        for move in rem_moves:
            win = 0
            original_player = board.current_player
            original_opponent_player = 0
            if original_player == 1:
                original_opponent_player = 2
            elif original_player == 2:
                original_opponent_player = 1
            for i in range(10):
                copy_of_board = board.copy()
                copy_of_board.play_move(move, original_player)
                a = GoBoardUtil.generate_legal_moves(copy_of_board, copy_of_board.current_player)
                random.shuffle(a)
                while len(a):
                    winner = copy_of_board.detect_five_in_a_row()
                    if original_player == winner:
                        win = win + 1
                        break
                    if original_opponent_player == winner:
                        win = win - 1
                        break
                    if len(a) > 0:
                        copy_of_board.play_move(a.pop(), copy_of_board.current_player)
                    else:
                        break
            move_score_dict[move] = win
        move_score_dict = {k: v for k, v in sorted(move_score_dict.items(), key=lambda item:item[1], reverse=True)}
        temp_list = list(move_score_dict)
        return [chr(ord('A') + temp_list[0]%s - 1) + str(temp_list[0] // s)]'''
        random.shuffle(rem_moves_alpha)
        return rem_moves_alpha[0]
        
    def solve_cmd(self, board, flag=0): # A lot of this is taken from Assignment 2'code made by our team
        """
        Figures out next best move or whether someone has already won
        """
        b = GoBoardUtil.get_twoD_board(board)
        s = len(b) + 1
        empty_bool = self.check_empty(board)
        rem_moves = GoBoardUtil.generate_legal_moves(board, board.current_player)
        rem_moves_alpha = []
        for move in rem_moves:
            rem_moves_alpha.append(chr(ord('A') + move%s - 1) + str(move // s))
        rem_moves_alpha = sorted(dict.fromkeys(rem_moves_alpha))
        if empty_bool: 
            # If the board is empty, play anywhere
            return rem_moves_alpha
        
        # Check if you can win and play there
        player = board.current_player
        results = self.check_next_move_wins(board, player)
        results = sorted(dict.fromkeys(results))
        if len(results) > 0:
            return results[0]
        if len(rem_moves) == 1:
            return rem_moves_alpha[0]
        
        # Chcek if opponent can win and block
        player = board.current_player
        if player == BLACK:
            player = WHITE
        elif player == WHITE:
            player = BLACK
        results = self.check_next_move_wins(board, player)
        results = sorted(dict.fromkeys(results))
        if len(results) == 0 and len(rem_moves) == 2:
            return rem_moves_alpha[0]
        elif len(results) == 1:
            return results[0]
        elif len(results) == 2:
            return results[0]
        
        # Check if you can make 4 and do it
        player = board.current_player
        results = self.three_in_six(board, player)
        if len(results) > 0:
            return results[0]
         
        # Check if opponent can make 4 and block it
        player = board.current_player
        results = self.three_in_six_for_opp(board, player)
        if len(results) > 0:
            return max(results, key=results.count)
        
        # Check if you can make 3 and make maximum of those
        player = board.current_player
        results = self.two_in_six(board, player)
        if len(results) > 0:
            return max(results, key=results.count)
        
        # Check if opponent can make 3 and block maximum of those
        player = board.current_player
        if player == BLACK:
            player = WHITE
        elif player == WHITE:
            player = BLACK        
        results = self.two_in_six(board, player)
        if len(results) > 0:
            return max(results, key=results.count)
        
        # Check if you can make 2 and make maximum of those
        player = board.current_player
        results = self.one_in_six(board, player)
        if len(results) > 0:
            return max(results, key=results.count)
        
        # Check if opponent can make 2 and block maximum of those
        player = board.current_player
        if player == BLACK:
            player = WHITE
        elif player == WHITE:
            player = BLACK        
        results = self.one_in_six(board, player)
        if len(results) > 0:
            return max(results, key=results.count)        
        
        return ''

    def check_empty(self, board):
        b = GoBoardUtil.get_twoD_board(board)
        s = len(b)
        count = 0
        for i in range(s):
            for j in b[i]:
                if j != EMPTY:
                    return False
        return True

    def check_next_move_wins(self, board, player): 
        # Check if the passed player can win in 1 move
        b = GoBoardUtil.get_twoD_board(board)
        s = len(b)
        moves = []
        for i in range(s):
            for j in range(s - 4):
                pieces = [b[i][j], b[i][j + 1], b[i][j + 2], b[i][j + 3], b[i][j + 4]]
                if pieces.count(player) == 4 and pieces.count(EMPTY) == 1:
                    x = pieces.index(EMPTY)
                    moves.append(chr(ord('A') + j + x) + str(i + 1))
        for i in range(s - 4):
            for j in range(s):
                pieces = [b[i][j], b[i + 1][j], b[i + 2][j], b[i + 3][j], b[i + 4][j]]
                if pieces.count(player) == 4 and pieces.count(EMPTY) == 1:
                    x = pieces.index(EMPTY)
                    moves.append(chr(ord('A') + j) + str(i + x + 1))
        for i in range(s - 4):
            for j in range(4, s):
                pieces = [b[i][j], b[i + 1][j - 1], b[i + 2][j - 2], b[i + 3][j - 3], b[i + 4][j - 4]]
                if pieces.count(player) == 4 and pieces.count(EMPTY) == 1:
                    x = pieces.index(EMPTY)
                    moves.append(chr(ord('A') + j - x) + str(i + x + 1))
        for i in range(s - 4):
            for j in range(s - 4):
                pieces = [b[i][j], b[i + 1][j + 1], b[i + 2][j + 2], b[i + 3][j + 3], b[i + 4][j + 4]]
                if pieces.count(player) == 4 and pieces.count(EMPTY) == 1:
                    x = pieces.index(EMPTY)
                    moves.append(chr(ord('A') + j + x) + str(i + x + 1))
        return moves

    def three_in_six(self, board, player): 
        # Check if the current player can make 4 in a row by checking for certain patterns of 3 pieces in segments of 6 pieces
        b = GoBoardUtil.get_twoD_board(board)
        s = len(b)
        types = [[0, 0, player, player, player, 0],
                 [0, player, player, player, 0, 0],
                 [0, player, player, 0, player, 0],
                 [0, player, 0, player, player, 0]]
        moves = []
        for i in range(s):
            for j in range(s - 5):
                pieces = [b[i][j], b[i][j + 1], b[i][j + 2], b[i][j + 3], b[i][j + 4], b[i][j + 5]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A') + j + 1) + str(i + 1))
                    elif pieces == types[1]:
                        moves.append(chr(ord('A') + j + 4) + str(i + 1))
                    elif pieces == types[2]:
                        moves.append(chr(ord('A') + j + 3) + str(i + 1))
                    elif pieces == types[3]:
                        moves.append(chr(ord('A') + j + 2) + str(i + 1))
        for i in range(s - 5):
            for j in range(s):
                pieces = [b[i][j], b[i + 1][j], b[i + 2][j], b[i + 3][j], b[i + 4][j], b[i + 5][j]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A') + j) + str(i + 2))
                    elif pieces == types[1]:
                        moves.append(chr(ord('A') + j) + str(i + 5))
                    elif pieces == types[2]:
                        moves.append(chr(ord('A') + j) + str(i + 4))
                    elif pieces == types[3]:
                        moves.append(chr(ord('A') + j) + str(i + 3))
        for i in range(s - 5):
            for j in range(5, s):
                pieces = [b[i][j], b[i + 1][j - 1], b[i + 2][j - 2], b[i + 3][j - 3], b[i + 4][j - 4],
                          b[i + 5][j - 5]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A') + j - 1) + str(i + 2))
                    elif pieces == types[1]:
                        moves.append(chr(ord('A') + j - 4) + str(i + 5))
                    elif pieces == types[2]:
                        moves.append(chr(ord('A') + j - 3) + str(i + 4))
                    elif pieces == types[3]:
                        moves.append(chr(ord('A') + j - 2) + str(i + 3))
        for i in range(s - 5):
            for j in range(s - 5):
                pieces = [b[i][j], b[i + 1][j + 1], b[i + 2][j + 2], b[i + 3][j + 3], b[i + 4][j + 4],
                          b[i + 5][j + 5]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A') + j + 1) + str(i + 2))
                    elif pieces == types[1]:
                        moves.append(chr(ord('A') + j + 4) + str(i + 5))
                    elif pieces == types[1]:
                        moves.append(chr(ord('A') + j + 3) + str(i + 4))
                    elif pieces == types[1]:
                        moves.append(chr(ord('A') + j + 2) + str(i + 3))
        return moves

    def three_in_six_for_opp(self, board, playero): 
        # Check if opponent has a certain pattern of 3 pieces in segments of 6 pieces
        player = 0
        if playero == BLACK:
            player = WHITE
        elif playero == WHITE:
            player = BLACK
        b = GoBoardUtil.get_twoD_board(board)
        s = len(b)
        types = [[0, 0, player, player, player, 0],
                 [0, player, player, player, 0, 0],
                 [0, player, player, 0, player, 0],
                 [0, player, 0, player, player, 0]]
        moves = []
        for i in range(s):
            for j in range(s - 5):
                pieces = [b[i][j], b[i][j + 1], b[i][j + 2], b[i][j + 3], b[i][j + 4], b[i][j + 5]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A') + j + 1) + str(i + 1))
                        moves.append(chr(ord('A') + j + 5) + str(i + 1))
                        if j + 6 == s:
                            moves.append(chr(ord('A') + j + 0) + str(i + 1)) # These are the deepest if statements, taking care of boundary conditions
                    elif pieces == types[1]:
                        moves.append(chr(ord('A') + j + 4) + str(i + 1))
                        moves.append(chr(ord('A') + j + 0) + str(i + 1))
                        if j == 0:
                            moves.append(chr(ord('A') + j + 5) + str(i + 1)) #
                    elif pieces == types[2]:
                        moves.append(chr(ord('A') + j + 3) + str(i + 1))
                        moves.append(chr(ord('A') + j + 0) + str(i + 1))
                        moves.append(chr(ord('A') + j + 5) + str(i + 1))
                    elif pieces == types[3]:
                        moves.append(chr(ord('A') + j + 2) + str(i + 1))
                        moves.append(chr(ord('A') + j + 0) + str(i + 1))
                        moves.append(chr(ord('A') + j + 5) + str(i + 1))
        for i in range(s - 5):
            for j in range(s):
                pieces = [b[i][j], b[i + 1][j], b[i + 2][j], b[i + 3][j], b[i + 4][j], b[i + 5][j]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A') + j) + str(i + 2))
                        moves.append(chr(ord('A') + j) + str(i + 6))
                        if i + 6 == s:
                            moves.append(chr(ord('A') + j) + str(i + 1)) #
                    elif pieces == types[1]:
                        moves.append(chr(ord('A') + j) + str(i + 5))
                        moves.append(chr(ord('A') + j) + str(i + 1))
                        if i == 0:
                            moves.append(chr(ord('A') + j) + str(i + 6)) #
                    elif pieces == types[2]:
                        moves.append(chr(ord('A') + j) + str(i + 4))
                        moves.append(chr(ord('A') + j) + str(i + 1))
                        moves.append(chr(ord('A') + j) + str(i + 6))
                    elif pieces == types[3]:
                        moves.append(chr(ord('A') + j) + str(i + 3))
                        moves.append(chr(ord('A') + j) + str(i + 1))
                        moves.append(chr(ord('A') + j) + str(i + 6))
        for i in range(s - 5):
            for j in range(5, s):
                pieces = [b[i][j], b[i + 1][j - 1], b[i + 2][j - 2], b[i + 3][j - 3], b[i + 4][j - 4],
                          b[i + 5][j - 5]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A') + j - 1) + str(i + 2))
                        moves.append(chr(ord('A') + j - 5) + str(i + 6))
                        if i + 6 == s or j - 6 == 0:
                            moves.append(chr(ord('A') + j - 0) + str(i + 1)) #
                    elif pieces == types[1]:
                        moves.append(chr(ord('A') + j - 4) + str(i + 5))
                        moves.append(chr(ord('A') + j - 0) + str(i + 1))
                        if i == 0 or j == s:
                            moves.append(chr(ord('A') + j - 0) + str(i + 6)) #
                    elif pieces == types[2]:
                        moves.append(chr(ord('A') + j - 3) + str(i + 4))
                        moves.append(chr(ord('A') + j - 0) + str(i + 1))
                        moves.append(chr(ord('A') + j - 5) + str(i + 6))
                    elif pieces == types[3]:
                        moves.append(chr(ord('A') + j - 2) + str(i + 3))
                        moves.append(chr(ord('A') + j - 0) + str(i + 1))
                        moves.append(chr(ord('A') + j - 5) + str(i + 6))
        for i in range(s - 5):
            for j in range(s - 5):
                pieces = [b[i][j], b[i + 1][j + 1], b[i + 2][j + 2], b[i + 3][j + 3], b[i + 4][j + 4],
                          b[i + 5][j + 5]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A') + j + 1) + str(i + 2))
                        moves.append(chr(ord('A') + j + 5) + str(i + 6))
                        if i + 6 == s or j + 6 == s:
                            moves.append(chr(ord('A') + j + 0) + str(i + 1)) #
                    elif pieces == types[1]:
                        moves.append(chr(ord('A') + j + 4) + str(i + 5))
                        moves.append(chr(ord('A') + j + 0) + str(i + 1))
                        if i == 0 or j == 0:
                            moves.append(chr(ord('A') + j + 5) + str(i + 6)) #
                    elif pieces == types[1]:
                        moves.append(chr(ord('A') + j + 3) + str(i + 4))
                        moves.append(chr(ord('A') + j + 0) + str(i + 1))
                        moves.append(chr(ord('A') + j + 5) + str(i + 6))
                    elif pieces == types[1]:
                        moves.append(chr(ord('A') + j + 2) + str(i + 3))
                        moves.append(chr(ord('A') + j + 0) + str(i + 1))
                        moves.append(chr(ord('A') + j + 5) + str(i + 6))
        return moves
    
    def two_in_six(self, board, player):
        b = GoBoardUtil.get_twoD_board(board)
        s = len(b)
        types = [[0,0,player,player,0,0], 
                 [0,player,player,0,0,0], 
                 [0,0,0,player,player,0],
                 [0,player,0,player,0,0],
                 [0,0,player,0,player,0]]
        moves = []
        for i in range(s):
            for j in range(s-5):
                pieces = [b[i][j], b[i][j+1], b[i][j+2], b[i][j+3], b[i][j+4], b[i][j+5]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A')+j+1)+str(i+1))
                        moves.append(chr(ord('A')+j+4)+str(i+1))
                    elif pieces == types[1] or pieces == types[4]:
                        moves.append(chr(ord('A')+j+3)+str(i+1))
                    elif pieces == types[2] or pieces == types[3]:
                        moves.append(chr(ord('A')+j+2)+str(i+1))
        for i in range(s-5):
            for j in range(s):
                pieces = [b[i][j], b[i+1][j], b[i+2][j], b[i+3][j], b[i+4][j], b[i+5][j]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A')+j)+str(i+2))
                        moves.append(chr(ord('A')+j)+str(i+5))
                    elif pieces == types[1] or pieces == types[4]:
                        moves.append(chr(ord('A')+j)+str(i+4))
                    elif pieces == types[2] or pieces == types[3]:
                        moves.append(chr(ord('A')+j)+str(i+3))
        for i in range(s-5):
            for j in range(5, s):
                pieces = [b[i][j], b[i+1][j-1], b[i+2][j-2], b[i+3][j-3], b[i+4][j-4], b[i+5][j-5]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A')+j-1)+str(i+2))
                        moves.append(chr(ord('A')+j-4)+str(i+5))
                    elif pieces == types[1] or pieces == types[4]:
                        moves.append(chr(ord('A')+j-3)+str(i+4))
                    elif pieces == types[2] or pieces == types[3]:
                        moves.append(chr(ord('A')+j-2)+str(i+3))
        for i in range(s-5):
            for j in range(s-5):
                pieces = [b[i][j], b[i+1][j+1], b[i+2][j+2], b[i+3][j+3], b[i+4][j+4], b[i+5][j+5]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A')+j+1)+str(i+2))
                        moves.append(chr(ord('A')+j+4)+str(i+5))
                    elif pieces == types[1] or pieces == types[4]:
                        moves.append(chr(ord('A')+j+3)+str(i+4))
                    elif pieces == types[2] or pieces == types[3]:
                        moves.append(chr(ord('A')+j+2)+str(i+3))
        return moves
    
    def one_in_six(self, board, player):
        b = GoBoardUtil.get_twoD_board(board)
        s = len(b)
        types = [[0,player,0,0,0,0], 
                 [0,0,player,0,0,0], 
                 [0,0,0,player,0,0],
                 [0,0,0,0,player,0]]
        moves = []
        for i in range(s):
            for j in range(s-5):
                pieces = [b[i][j], b[i][j+1], b[i][j+2], b[i][j+3], b[i][j+4], b[i][j+5]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A')+j+2)+str(i+1))
                    elif pieces == types[1]:
                        moves.append(chr(ord('A')+j+1)+str(i+1))
                        moves.append(chr(ord('A')+j+3)+str(i+1))
                    elif pieces == types[2]:
                        moves.append(chr(ord('A')+j+2)+str(i+1))
                        moves.append(chr(ord('A')+j+4)+str(i+1))
                    elif pieces == types[3]:
                        moves.append(chr(ord('A')+j+3)+str(i+1))
        for i in range(s-5):
            for j in range(s):
                pieces = [b[i][j], b[i+1][j], b[i+2][j], b[i+3][j], b[i+4][j], b[i+5][j]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A')+j)+str(i+3))
                    elif pieces == types[1]:
                        moves.append(chr(ord('A')+j)+str(i+2))
                        moves.append(chr(ord('A')+j)+str(i+4))
                    elif pieces == types[2]:
                        moves.append(chr(ord('A')+j)+str(i+3))
                        moves.append(chr(ord('A')+j)+str(i+5))
                    elif pieces == types[3]:
                        moves.append(chr(ord('A')+j)+str(i+4))
        for i in range(s-5):
            for j in range(5, s):
                pieces = [b[i][j], b[i+1][j-1], b[i+2][j-2], b[i+3][j-3], b[i+4][j-4], b[i+5][j-5]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A')+j-2)+str(i+3))
                    elif pieces == types[1]:
                        moves.append(chr(ord('A')+j-1)+str(i+2))
                        moves.append(chr(ord('A')+j-3)+str(i+4))
                    elif pieces == types[2]:
                        moves.append(chr(ord('A')+j-2)+str(i+3))
                        moves.append(chr(ord('A')+j-4)+str(i+5))
                    elif pieces == types[3]:
                        moves.append(chr(ord('A')+j-3)+str(i+4))
        for i in range(s-5):
            for j in range(s-5):
                pieces = [b[i][j], b[i+1][j+1], b[i+2][j+2], b[i+3][j+3], b[i+4][j+4], b[i+5][j+5]]
                if pieces in types:
                    if pieces == types[0]:
                        moves.append(chr(ord('A')+j+2)+str(i+3))
                    elif pieces == types[1]:
                        moves.append(chr(ord('A')+j+1)+str(i+2))
                        moves.append(chr(ord('A')+j+3)+str(i+4))
                    elif pieces == types[2]:
                        moves.append(chr(ord('A')+j+2)+str(i+3))
                        moves.append(chr(ord('A')+j+4)+str(i+5))
                    elif pieces == types[3]:
                        moves.append(chr(ord('A')+j+3)+str(i+4))
        return moves      

def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnection(GomokuSimulationPlayer(), board)
    con.start_connection()

if __name__=='__main__':
    run()
