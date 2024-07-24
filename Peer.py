import socket
import threading
import redis
import http.server
import PIL
import numpy as np
import json
from PIL import Image
import requests
from numpy import array
import numpysocket
import PySimpleGUI as sg

SERVER = '172.18.112.1'
PORT_SERVER = 8000

PORT_PEER = 8888
PEER = ''

PEER1 = '172.18.112.2'
PEER2 = '172.18.112.3'

def main():
    peer1 = Peer(PEER1, PORT_PEER, 'Peer 01')
    peer2 = Peer(PEER2, PORT_PEER, 'Peer 02')
    peer1.start()
    peer2.start()
    peer1.listen()
    peer2.listen()
    peer1.connect(PEER2, PORT_PEER)
    peer2.connect(PEER1, PORT_PEER)
    peer1.gui()
    peer2.gui()


class Peer:
    def __init__(self, host, port, username):
        self.host = host
        self.port = port
        self.username = username
        #self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connections = []

    def connect(self, peer_host, peer_port):
        try:
            connection = self.socket.connect((peer_host, peer_port))
            self.connections.append(connection)
            print(f"Connected to Peer : {peer_host} with Port : {peer_port}")
        except socket.error as e:
            print(f"Failed to connect to Peer : {peer_host} with Port : {peer_port} due to Error : {e}")

    def listen(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(10)
        print(f"Listening for connection on Host : {self.host} with Port : {self.port}")

        while True:
            connection, address = self.socket.accept()
            self.connections.append(connection)
            print(f"Accepted connection from Address : {address}")

    def send_data(self, data):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect()
        r = requests.post(SERVER, data=json.dumps(data))

    def send_media(self, image):
        temp = Image.open(image)
        matrix = array(temp)
        socket.socket.sendall(matrix)

    def receive_data(self):
        data = socket.recv(1024)
        data = json.loads(data.decode())

    def receive_image(self):
        image = socket.recv(1024)
        image = json.loads(image.decode())

    def start(self):
        listen_thread = threading.Thread(target=self.listen())
        listen_thread.start()

    def gui(self):
        layout = [[sg.Text("Hello from PySimpleGUI")], [sg.Button("OK")]]

        # Create the window
        window = sg.Window("Demo", layout)

        # Create an event loop
        while True:
            event, values = window.read()
            # End program if user closes window or
            # presses the OK button
            if event == "OK" or event == sg.WIN_CLOSED:
                break

        window.close()


if __name__ == '__main__':
    main()
