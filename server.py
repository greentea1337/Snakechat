import sys
import socket
import threading

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QListWidget, QPushButton, QDialog, QLabel, QLineEdit


class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Configuration')

        # IP address input
        ip_label = QLabel('IP Address:', self)
        self.ip_input = QLineEdit(self)
        self.ip_input.setText('127.0.0.1')

        ip_layout = QHBoxLayout()
        ip_layout.addWidget(ip_label)
        ip_layout.addWidget(self.ip_input)

        # Port number input
        port_label = QLabel('Port Number:', self)
        self.port_input = QLineEdit(self)
        self.port_input.setText('8080')

        port_layout = QHBoxLayout()
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)

        # OK and Cancel buttons
        ok_button = QPushButton('OK', self)
        ok_button.clicked.connect(self.accept)

        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(ip_layout)
        main_layout.addLayout(port_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def get_config(self):
        ip = self.ip_input.text()
        port = int(self.port_input.text())
        return ip, port


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

        # Start/Stop/Exit/Config buttons
        self.start_button = QPushButton('Start Server', self)
        self.start_button.clicked.connect(self.start_server)

        self.stop_button = QPushButton('Stop Server', self)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_server)

        self.config_button = QPushButton('Config', self)
        self.config_button.clicked.connect(self.configure_server)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.config_button)

        # Chat and client list layout
        chat_layout = QHBoxLayout()
        chat_layout.addWidget(self.chat_history)
        chat_layout.addWidget(self.client_list)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(chat_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.ip = '127.0.0.1'
        self.port = 8080

    def configure_server(self):
        dialog = ConfigDialog(self)
        if dialog.exec_():
            self.ip, self.port = dialog.get_config()

    def start_server(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        server_thread = threading.Thread(target=self.receive)
        server_thread.daemon = True
        server_thread.start()

        self.chat_history.append(f'Server running on {self.ip}:{self.port}...')

    def stop_server(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        for client in clients:
            client.close()

        clients.clear()
        nicknames.clear()

        self.chat_history.append('Server stopped.')

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
        global server, clients, nicknames

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip, self.port))
        server.listen()

        clients = []
        nicknames = []

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
