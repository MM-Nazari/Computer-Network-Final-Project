import redis
from http.server import *
import requests

SERVER = '172.18.112.1'
PORT = 8000
status1 = 'OK'
status2 = 'bad request'


def main():
    STUNdb = redis.Redis(host='localhost', port=6379, db=0)
    server = HTTPServer((SERVER, PORT), STUN)
    server.serve_forever()


class STUN(BaseHTTPRequestHandler):
    global status

    def _set_response(self):
        if status == status1:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'user successfuly addded to server')
        if status == status2:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'user didnt add to to server')

    def do_GET(self):
        for i in STUNdb.keys():
            if status == status1:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(i, 'utf-8')
            if status == status2:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Bad request')

    def do_POST(self, username, host):
        STUNdb.set(username, host)


if __name__ == '__main__':
    main()
