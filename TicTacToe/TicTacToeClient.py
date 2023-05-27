import socket
import sys

class TicTacToeClient:
    def __init__(self, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('localhost', port))

    def listen_server(self):
        while True:
            data = self.client.recv(1024)
            if data:
                message = data.decode()
                #if is taken only at the first message for symbol and client_id
                if "#" in message:
                    symbol, client_id = message.split('#')
                    print(f"Connected to the server.\nYour symbol is {symbol} and your ID is {client_id}.")
                else:
                    print(message)
                    if "Your turn!" in message:
                        self.make_move()

    def make_move(self):
        while True:
            try:
                move = input("Put your mark to (row, col): ")
                row, col = map(int, move.split(","))
                self.client.send(move.encode())
                break
            except ValueError:
                print("Invalid input format. Please enter row and column in the format 'row,col'. i.e. 1,1")


if __name__ == "__main__":
    port = int(sys.argv[1])
    client = TicTacToeClient(port)
    client.listen_server()





