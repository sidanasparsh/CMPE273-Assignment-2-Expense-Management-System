import socket
import threading
import redis
from CircuitBreaker import CircuitBreaker


HOSTNAME = 'localhost'
SERVERBINDPORT = 8000
MAX_REQUEST_LEN= 1024


class ProxyServer:
    """ ProxyServer Class """
    def __init__(self, hostName, bindPort):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((hostName, bindPort))
        self.serverSocket.listen(5)

    def listenForClient(self):
        """ Method to wait for client conncetions """
        currentServerURLNumber=-1
        while True:
            (clientSocket, clientAddress) = self.serverSocket.accept()   # Establish the connection
            currentServerURLNumber=currentServerURLNumber+1
            redisCon = redis.Redis('localhost')
            serverList = redisCon.lrange('activeServersList', 0, redisCon.llen("activeServersList"))
            serverSet = set(serverList)
            serverList = list(serverSet)
            print ("The list is:")
            print serverList
            serverCount = len(serverList)
            currentServerURL=serverList[currentServerURLNumber%serverCount]
            host,port=currentServerURL.split(':')
            targetServer = serverList[currentServerURLNumber % serverCount]
            try:
                proxyThread = threading.Thread(name=clientAddress, target=self.proxyServerThread, args=(clientSocket, host, port, targetServer))
            except Exception as e:
                print e
            proxyThread.setDaemon(True)
            proxyThread.start()
        self.serverSocket.close()

    @CircuitBreaker(max_failure_to_open=3, reset_timeout=10)
    def proxyServerThread(self, clientConnection, host, port, targetServer):
        request = clientConnection.recv(MAX_REQUEST_LEN)   # retrieving rerquest from browser
        try:
            print port
            proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxySocket.settimeout(5)
            proxySocket.connect((host, int(port)))
            proxySocket.send(request)   # sending to web server
            while True:
                receievedData = proxySocket.recv(MAX_REQUEST_LEN)
                if (len(receievedData) > 0):
                    clientConnection.send(receievedData)       #seding to browser
                else:
                    break
            proxySocket.close()
            clientConnection.close()
        except Exception as errorOutput:
            if proxySocket:
                proxySocket.close()
            if clientConnection:
                clientConnection.close()
            raise errorOutput

if __name__ == "__main__":
    proxyServer = ProxyServer(HOSTNAME, SERVERBINDPORT)
    proxyServer.listenForClient()
