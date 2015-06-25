import select
import socket
import sys
import signal

from middleware import send, receive

BUFSIZ = 2048


class Server(object):
    
    def __init__(self, port=3490, backlog=5):
        self.clients = 0
        self.clientmap = {}
        self.outputs = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('',port))
        print 'Listening to port',port,'...'
        self.server.listen(backlog)
        signal.signal(signal.SIGINT, self.sighandler)
        
    def sighandler(self, signum, frame):
        print 'Shutting down server...'
        for o in self.outputs:
            o.close()
            
        self.server.close()

    def getname(self, client):
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '-->>'.join((name, host))
        
    def serve(self):
        
        inputs = [self.server,sys.stdin]
        self.outputs = []

        running = 1

        while running:

            try:
                inputready,outputready,exceptready = select.select(inputs, self.outputs, [])
            except select.error, e:
                break
            except socket.error, e:
                break

            for s in inputready:

                if s == self.server:
                    client, address = self.server.accept()
                    print 'chatserver: got connection %d from %s' % (client.fileno(), address)
                    cname = receive(client).split('NAME: ')[1]
                    
               
                    self.clients += 1
                    send(client, 'CLIENT: ' + str(address[0]))
                    inputs.append(client)
                    self.clientmap[client] = (address, cname)
                    msg = '\n(Connected: New client (%d) from %s)' % (self.clients, self.getname(client))
                    for o in self.outputs:
                        send(o, msg)
                    
                    self.outputs.append(client)

                elif s == sys.stdin:

                    junk = sys.stdin.readline()
                    running = 0
                else:
                    try:
                        
                        data = receive(s)
                        if data:
                            msg = '\n>>[' + self.getname(s) + ']>> ' + data
                            for o in self.outputs:
                                if o != s:
                                    send(o, msg)
                        else:
                            print 'chatserver: %d hung up' % s.fileno()
                            self.clients -= 1
                            s.close()
                            inputs.remove(s)
                            self.outputs.remove(s)
                            msg = '\n(Hung up: Client from %s)' % self.getname(s)
                            for o in self.outputs:
                                send(o, msg)
                                
                    except socket.error, e:
                        inputs.remove(s)
                        self.outputs.remove(s)
                        


        self.server.close()

if __name__ == "__main__":

    Server().serve()
