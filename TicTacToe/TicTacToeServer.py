"""
@author Gokberk Keskinkilic
@version 1.0
@date 25.05.2023
----------------
METHODS:
accept_connections()
start_game()
send_game_over_message()
handle_client()
handle_turn()
print_move_message()
send_board_state()
is_valid_move()
is_game_over()
board_to_string()
"""

import socket
import threading
import sys

class TicTacToeServer:

    def __init__(self, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', port))
        self.server.listen(2)
        self.clients = []
        self.symbols = ['X', 'O']
        self.board = [['_' for _ in range(3)] for _ in range(3)]
        self.turn = 0
        self.turn_lock = threading.Lock()
        self.message_sent = [False, False]

    def accept_connections(self):
        print("Server runs...")
        while len(self.clients) < 2:
            conn, addr = self.server.accept()
            self.clients.append((conn, addr))
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

        print("The game has started.")
        self.start_game()

    def start_game(self):
        while True:
            self.send_board_state()
            self.handle_turn()
            if self.is_game_over():
                winner = (self.turn + 1) % 2  # the player who made the last move is the winner
                print(f"\nFinal Board State:\n{self.board_to_string()}")
                print(f"Player {winner} ({self.symbols[winner]}) has won the game!")
                self.send_game_over_message(winner, True)
                break
            elif not any('_' in row for row in self.board):
                print(f"\nFinal Board State:\n{self.board_to_string()}")
                print("The game is a draw!")
                self.send_game_over_message(None, False)
                break

        for conn, addr in self.clients:
            conn.close()
        print("Connections to clients closed.")

        self.server.close()
        print("Server stopped.")

    def send_game_over_message(self, winner, is_win):
        for i, (conn, addr) in enumerate(self.clients):
            if is_win:
                message = f"\nFinal Board State:\n{self.board_to_string()}\nPlayer {winner} ({self.symbols[winner]}) has won the game!\nThe game has ended."
            else:
                message = f"\nFinal Board State:\n{self.board_to_string()}\nThe game is a draw!\nThe game has ended."
            conn.send(message.encode())
            #conn.close()
    

    def handle_client(self, conn, addr):
        player_id = len(self.clients) - 1
        symbol = self.symbols[player_id]
        conn.send(f"{symbol}#{player_id}".encode())
        print(f"A client is connected, and it is assigned with the symbol {symbol} and ID={player_id}.")

    def handle_turn(self):
        with self.turn_lock:
            conn, addr = self.clients[self.turn]
            move = conn.recv(1024).decode().strip().split(',')
            row, col = int(move[0]), int(move[1])

            if self.is_valid_move(row, col):
                self.board[row][col] = self.symbols[self.turn]
                self.print_move_message(self.turn, row, col, True)
                self.turn = (self.turn + 1) % 2
                self.message_sent = [False, False]  # Reset the message_sent flags
            else:
                conn.send("Invalid move. Try again.".encode())
                self.print_move_message(self.turn, row, col, False)

    def print_move_message(self, player, row, col, is_legal):
        if is_legal:
            message = f"Received {self.symbols[player]} on ({row},{col}). It is a legal move."
        else:
            message = f"Received {self.symbols[player]} on ({row},{col}). It is an illegal move."
        print(message)


    def send_board_state(self):
        for i, (conn, addr) in enumerate(self.clients):
            if i == self.turn:
                message = f"\nBoard State:\n{self.board_to_string()}\nYour turn!"
                conn.send(message.encode())
            elif not self.message_sent[i]:
                message = f"\nBoard State:\n{self.board_to_string()}\nWaiting for Player {self.turn}'s move."
                conn.send(message.encode())
                self.message_sent[i] = True

    def is_valid_move(self, row, col):
        if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == '_':
            return True
        return False

    def is_game_over(self):
        for row in self.board:
            if row[0] == row[1] == row[2] != '_':
                return True
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '_':
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '_':
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '_':
            return True
        return False

    def board_to_string(self):
        board_string = ''
        for row in self.board:
            board_string += '|'.join(row) + '\n'
        return board_string

if __name__ == "__main__":
    port = int(sys.argv[1])
    server = TicTacToeServer(port)
    server.accept_connections()
