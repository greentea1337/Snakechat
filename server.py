import sys
import socket
import threading

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QListWidget, QPushButton


HOST = '127.0.0.1'  # localhost
PORT = 8080

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []


class ServerGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Chat Server')

        # Chat history display
        self.chat_history = QTextEdit(self)
        self.chat_history.setReadOnly(True)

        # Connected clients display
        self.client_list = QListWidget(self)
        self.client_list.setMaximumWidth(150)

        # Start/Stop/Exit buttons
        self.start_button = QPushButton('Start Server', self)
        self.start_button.clicked.connect(self.start_server)

        self.stop_button = QPushButton('Stop Server', self)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_server)

        self.exit_button = QPushButton('Exit', self)
        self.exit_button.clicked.connect(self.exit_program)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.exit_button)

        # Chat and client list layout
        chat_layout = QHBoxLayout()
        chat_layout.addWidget(self.chat_history)
        chat_layout.addWidget(self.client_list)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(chat_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def start_server(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        threading.Thread(target=self.receive).start()

        self.chat_history.append('Server running...')

    def stop_server(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        for client in clients:
            client.close()

        clients.clear()
        nicknames.clear()

        self.chat_history.append('Server stopped.')

    def exit_program(self):
        for client in clients:
            client.close()

        sys.exit()

    def broadcast(self, message):
        for client in clients:
            client.send(message)

    def handle(self, client):
        while True:
            try:
                message = client.recv(1024)
                self.broadcast(message)
            except:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                self.broadcast(f'{nickname} left the chat!'.encode('utf-8'))
                nicknames.remove(nickname)
                self.client_list.takeItem(index)
                break

    def receive(self):
        while True:
            client, address = server.accept()
            self.chat_history.append(f"Connected with {str(address)}")

            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            nicknames.append(nickname)
            clients.append(client)
            self.client_list.addItem(nickname)

            self.chat_history.append(f"Nickname of client is {nickname}!")
            self.broadcast(f"{nickname} joined the chat!".encode('utf-8'))
            client.send("Connected to the server!".encode('utf-8'))

            threading.Thread(target=self.handle, args=(client,)).start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    server_gui = ServerGUI()
    server_gui.show()
    sys.exit(app.exec_())
