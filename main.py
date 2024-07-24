from time import time
from twisted.internet.task import LoopingCall
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
import json
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import socket
import threading

class MyProtocol(Protocol):
    def __init__(self, factory, peertype):
        self.factory = factory
        self.state = "HELLO"
        self.remote_nodeid = None
        self.nodeid = self.factory.nodeid
        self.lc_ping = LoopingCall(self.send_ping)
        self.peertype = peertype
        self.lastping = None

    def connectionMade(self):
        remote_ip = self.transport.getPeer()
        host_ip = self.transport.getHost()
        self.remote_ip = remote_ip.host + ":" + str(remote_ip.port)
        self.host_ip = host_ip.host + ":" + str(host_ip.port)
        print("Connection from", self.transport.getPeer())


    def connectionLost(self, reason):
        if self.remote_nodeid in self.factory.peers:
            self.factory.peers.pop(self.remote_nodeid)
            self.lc_ping.stop()
        print(self.nodeid, "disconnected")


    def dataReceived(self, data):
        for line in data.splitlines():
            line = line.strip()
            msgtype = json.loads(line)['msgtype']
            if self.state == "HELLO" or msgtype == "hello":
                self.handle_hello(line)
                self.state = "READY"
            elif msgtype == "ping":
                self.handle_ping()
            elif msgtype == "pong":
                self.handle_pong()
            elif msgtype == "getaddr":
                self.handle_getaddr()

    ###The methods for ping and pong remain unchanged and are omitted
    ###for brevity

    def gotProtocol(p):
        """The callback to start the protocol exchange. We let connecting
        nodes start the hello handshake"""
        p.send_hello()

    def send_addr(self, mine=False):
        now = time()
        if mine:
            peers = [self.host_ip]
        else:
            peers = [(peer.remote_ip, peer.remote_nodeid)
                     for peer in self.factory.peers
                     if peer.peertype == 1 and peer.lastping > now - 240]
        addr = json.puts({'msgtype': 'addr', 'peers': peers})
        self.transport.write(peers + "\n")

    def send_addr(self, mine=False):
        now = time()
        if mine:
            peers = [self.host_ip]
        else:
            peers = [(peer.remote_ip, peer.remote_nodeid)
                     for peer in self.factory.peers
                     if peer.peertype == 1 and peer.lastping > now - 240]
        addr = json.puts({'msgtype': 'addr', 'peers': peers})
        self.transport.write(peers + "\n")

    def handle_addr(self, addr):
        data = json.loads(addr)
        for remote_ip, remote_nodeid in data["peers"]:
            if remote_nodeid not in self.factory.peers:
                host, port = remote_ip.split(":")
                point = TCP4ClientEndpoint(reactor, host, int(port))
                d = connectProtocol(point, MyProtocol(2))
                d.addCallback(self.gotProtocol)

    def handle_getaddr(self, getaddr):
        self.send_addr()

    def handle_hello(self, hello):
        hello = json.loads(hello)
        self.remote_nodeid = hello["nodeid"]
        if self.remote_nodeid == self.nodeid:
            print("Connected to myself.")
            "Connected to myself."
            self.transport.loseConnection()
        else:
            self.factory.peers[self.remote_nodeid] = self
            self.lc_ping.start(60)
            ###inform our new peer about us
            self.send_addr(mine=True)
            ###and ask them for more peers
            self.send_getaddr()