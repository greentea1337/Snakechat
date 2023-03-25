import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QDialog, QGridLayout
from PyQt5.QtCore import Qt
import socket
import threading

class NicknameDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set dialog properties
        self.setWindowTitle('Enter Nickname')
        self.setModal(True)

        # Create nickname input textbox and OK button
        self.nickname_input = QLineEdit(self)
        self.ok_button = QPushButton('OK', self)

        # Create layout for nickname input and OK button
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.nickname_input)
        input_layout.addWidget(self.ok_button)

        # Set dialog layout
        self.setLayout(input_layout)

        # Connect OK button to accept() method
        self.ok_button.clicked.connect(self.accept)

    def get_nickname(self):
        return self.nickname_input.text()

class ClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set window properties
        self.setWindowTitle('Web Chat Client')
        self.setGeometry(100, 100, 400, 600)

        # Create chat history textbox
        self.chat_history = QTextEdit(self)
        self.chat_history.setReadOnly(True)

        # Create message input textbox and send button
        self.message_input = QLineEdit(self)
        self.send_button = QPushButton('Send', self)

        # Create exit button
        self.exit_button = QPushButton('Exit', self)

        # Create layout for message input, send button, and exit button
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.exit_button)

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.chat_history)
        main_layout.addLayout(input_layout)

        # Set main layout
        self.setLayout(main_layout)

        # Connect send button to send_message() method
        self.send_button.clicked.connect(self.send_message)

        # Connect message input to send_button using return key
        self.message_input.returnPressed.connect(self.send_button.click)

        # Connect exit button to exit_chat() method
        self.exit_button.clicked.connect(self.exit_chat)

        # Create socket object and connect to server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('127.0.0.1', 8080))

        # Prompt user to enter nickname and send to server
        nickname_dialog = NicknameDialog()
        nickname_dialog.exec_()
        self.nickname = nickname_dialog.get_nickname()
        self.client_socket.send(self.nickname.encode('utf-8'))

        # Create thread to receive messages from server
        receive_thread = threading.Thread(target=self.receive_message)
        receive_thread.start()

    def receive_message(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.chat_history.append(message)
            except:
                self.client_socket.close()
                break

    def send_message(self):
        message = self.message_input.text()
        if message != '':
            self.client_socket.send(f"{self.nickname}: {message}".encode('utf-8'))
            self.message_input.setText('')

    def exit_chat(self):
        self.client_socket.close()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()
    sys.exit(app.exec_())
