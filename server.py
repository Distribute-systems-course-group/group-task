import socket
import sys
import threading
#import socketserver
from datetime import datetime
import time

         


threadLock = threading.RLock()

#Creating UDP thread and TCP thread. UDP for player movement, TCP for bigger connections
class myThread (threading.Thread):
    def __init__(self, threadID, name,clientdict,instanceID,gameQueue,worldstate,treasure):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.clientdict = clientdict
        self.instanceID = instanceID
        self.gameQueue = gameQueue
        self.worldstate = worldstate
        self.STOP =0
        self.treasure = treasure.split(".")

    def run(self):
        print("Starting " + self.name)
        if self.name == "TCPThread":
            threadLock.acquire()
            TCP(self.clientdict, self.instanceID,self.gameQueue, self.worldstate,self.STOP)
        else:
            threadLock.acquire()
            UDP(self.worldstate, self.instanceID, self.STOP,self.treasure)
        print("Closing "+self.name)


def UDP(worldstate, instanceID, STOP,treasure):

    UDP_IP = socket.gethostname()
    UDP_PORT = 5005
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    #Let's pick up player sent movement data
    while True:
        if STOP == 1:
            sys.exit()
            break
        try:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        except:
            break
        data = data.decode("utf-8")
        clientmsg = data.split("_")
        clientID = str(clientmsg[0])
        if "stop" in worldstate:
            break
        if clientID in worldstate:
            #If palyer isn't safe yet, update data to worldstate
            if worldstate[clientID] !="SAFE":
                worldstate[clientID] = clientmsg
        else:
            worldstate[clientID] = clientmsg

        sent =[]
        
        for c in worldstate:
            HEADER = str(instanceID) + "_" + c + "_" + str(len(worldstate))
            
            #If the player is finally safe, send them a packet so they know
            if worldstate[c] == "SAFE" and c not in sent:
                sent.append(c)
                
                print(" Player: "+ c + " IS SAFE")
                
                msg = HEADER + "_YOU ARE SAFE!!"
                
                sock.sendto(bytes(msg.encode("utf-8")),(UDP_IP, UDP_PORT))
            
            #If palyer reached the SAFE coordinate, then mark him as safe.
            if worldstate[c]!="SAFE" and worldstate[c][3] == treasure[0] and worldstate[c][4] == treasure[1]:
               worldstate[c] = "SAFE"
               msg = HEADER + "_" + str(worldstate)
               sock.sendto(bytes(msg.encode("utf-8")),(UDP_IP, UDP_PORT))

        threadLock.release()
        time.sleep(0.5)
        threadLock.acquire()
    print("closing UDP")

def TCP(clientdict, instanceID,gameQueue,worldstate,STOP):
    MAXPLAYERS =2

    s =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), 12345))
    s.listen(100)
    print("Server up and running")

    while True:
        clientsocket, address = s.accept()
        print("Connection from {} has been established.".format(address))
        clientmsg = clientsocket.recv(1024)
        clientmsg = clientmsg.decode("utf-8")
        clientmsg = clientmsg.split("_")
        if not clientmsg: break
        clientID = clientmsg[0]
        
        # Adding new client to Client Dictionary
        if clientID not in clientdict: 
            clientdict[clientID] = [address,1,clientsocket]
            print("Added new client {} to list".format(clientID))
            msg = "Connection accepted, Welcome to the game! You are in queue"
            clientsocket.send(bytes(msg.encode("utf-8")))
        
        # Check if we have enough players to begin a game round
        # by counting the number of clients with startqueue as 1 
        if clientdict[clientID][1] == 1:
            gameQueue[clientID]= clientdict[clientID]
        if len(gameQueue)% MAXPLAYERS != 0:
            continue
        if len(gameQueue)% MAXPLAYERS == 0:
            print("We have enough players. Let's start an instance.")
            #Players starting coordinates
            intanceID = instanceID+1
            
            for c in gameQueue.keys():
                #We are commencing game. Let's switch the STARTQUEUING parameter for each selected player from 1 to 0.
                clientdict[c][1]=0
                #TheThing gets a different starting point
                if c == MAXPLAYERS-1:
                    ws = "10.10"
                else:
                    ws = "0.0"
                HEADER = str(instanceID) + "_" + c + "_" + str(len(ws))
                msg = HEADER + "_" + ws
                clientsocket = gameQueue[c][2]
                clientsocket.send(bytes(msg.encode("utf-8")))
                
        threadLock.release()
        print("START GAME")
        break
 
 remove =[]
    #The real game starts here. Each while loop we look where players are and if someone is SAFE.
    while True:
        threadLock.acquire()
        if len(gameQueue) == 0:
            STOP = 1
            print("Everyone has completed the game!")
            worldstate.clear()
            worldstate["stop"] =1
            s.close()
            sys.exit()
            break

            #Gamequeue has the list of players still not safe and playing.
        for c in gameQueue.keys():
            clientsocket = gameQueue[c][2]
            
            #If the player is finally safe, remove them form the Gamequeue

            if c in worldstate and worldstate[c] == "SAFE"
                remove.append(c)
            
            if c in gameQueue.keys() and c not in remove:
                for c in worldstate.keys(): 
                    if worldstate[c] != "SAFE":
                        print("Game " + worldstate[c][1] + " Player: " + c + " at " + worldstate[c][3]+"."+worldstate[c][4])
        for r in remove:
            if r in gameQueue:
                gameQueue.pop(r)
        if len(gameQueue) == 0:
            STOP = 1
            print("Everyone has completed the game!")
            worldstate.clear()
            worldstate["stop"] =1
            threadLock.release()
            s.close()
            sys.exit()
            
        else:
            threadLock.release()
            time.sleep(1.5)        



def main():
    HEADERSIZE = 10
    clientdict = {}
    instanceID = 1
    gameQueue = {}
    worldstate = {}
    treasure = str(input("In what coordinate will we hide the treasure? Write the coordinate in form x.y (example: 2.3)"))
    threads =[]
    TCPThread = myThread(1,"TCPThread",clientdict,instanceID,gameQueue,worldstate,treasure)
    TCPThread.start()
    UDPThread = myThread(2,"UDPThread",clientdict,instanceID,gameQueue,worldstate,treasure)
    UDPThread.start()
    threads.append(TCPThread)
    threads.append(UDPThread)
    for t in threads:
        t.join()

    print("Shutting down server. Thank you for playing.")



if __name__ == '__main__':
    main()

