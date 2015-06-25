import socket
import sys
import select

from middleware import send, receive

BUFSIZ = 2048

class Client(object):

    def __init__(self, name,port=3490):
        self.name = name
        self.flag = False
        self.port = int(port)
        self.host = '127.0.0.1'
        
        self.prompt='[' + ': '.join((name, socket.gethostname().split('.')[0])) + ']> '
       
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print 'Connected to chat server: %d' % self.port
           
            send(self.sock,'NAME: ' + self.name) 
            data = receive(self.sock)
           
            addr = data.split('CLIENT: ')[1]
            self.prompt = '[' + ': '.join((self.name, addr)) + ']> '
        except socket.error, e:
            print 'Could not connect to chat server : %d' % self.port
            sys.exit(1)

    def cmdloop(self):

        while not self.flag:
            try:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()

                inputready, outputready,exceptrdy = select.select([0, self.sock], [],[])
                
                for i in inputready:
                    if i == 0:
                        data = sys.stdin.readline().strip()
                        if data: send(self.sock, data)
                    elif i == self.sock:
                        data = receive(self.sock)
                        if not data:
                            print 'Shutting down.'
                            self.flag = True
                            break
                        else:
                            sys.stdout.write(data + '\n')
                            sys.stdout.flush()
                            
            except KeyboardInterrupt:

                print 'Interrupted.'
                self.sock.close()
                break
            
            
if __name__ == "__main__":
    import sys

    if len(sys.argv)<2:
        sys.exit('Usage: %s chatid host portno' % sys.argv[0])
       
    client = Client(sys.argv[1], int(sys.argv[2]))
    client.cmdloop()
# middlewareClintchtbox
