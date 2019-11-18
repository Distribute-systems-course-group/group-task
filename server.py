import socket
import sys
import threading
from datetime import datetime
import time
import json
import pickle

         


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
            UDP(self.worldstate, self.STOP,self.treasure)
        print("Closing "+self.name)


def UDP(worldstate, STOP,treasure):
    addresslist=[]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((socket.gethostname(), 5005))
    #Let's pick up player sent movement data
    while True:
        if "GAME OVER" in worldstate:
            break
        try:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        except:
            break
        data = data.decode("utf-8")
        clientmsg = data.split("_")
        print("Clientmsg is: {}".format(clientmsg))
        clientID = str(clientmsg[0])

        if clientID in worldstate:
            #If palyer isn't safe yet, update data to worldstate
            if worldstate[clientID] !="SAFE":
                if clientmsg[3] == "1":
                    print("up")
                    worldstate[clientID][3] = str(int(worldstate[clientID][3])+1)
                if clientmsg[3] == "-1":
                    print("down")
                    worldstate[clientID][3] = str(int(worldstate[clientID][3])-1)
                if clientmsg[4] == "1":
                    print("right")
                    worldstate[clientID][4] = str(int(worldstate[clientID][4])+1)
                if clientmsg[4] == "-1":
                    print("left")
                    worldstate[clientID][3] = str(int(worldstate[clientID][3])-1)
                worldstate[clientID][2] = clientmsg[2]
                #print("worldstate at " + clientID +" is {}".format(worldstate[clientID]))
            else:
                threadLock.release()
                break
        else:
            worldstate[clientID] = clientmsg

        for c in worldstate:
            #If palyer reached the SAFE coordinate, then mark him as safe.
            if worldstate[c]!="SAFE" and worldstate[c][3] == treasure[0] and worldstate[c][4] == treasure[1]:
               worldstate[c] = "SAFE"
        
        threadLock.release()
        time.sleep(1.5)
        threadLock.acquire()

#In TCP we handle connecting players and we send the worldstate to everyone.

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
            instanceID = instanceID+1
            
            for c in gameQueue.keys():
                #We are commencing game. Let's switch the STARTQUEUING parameter for each selected player from 1 to 0.
                clientdict[c][1]=0
                #TheThing gets a different starting point
                ws = "0.0"
                HEADER = str(instanceID) + "_" + c + "_" + str(len(ws))
                msg = HEADER + "_" + ws
                clientsocket = gameQueue[c][2]
                clientsocket.send(bytes(msg.encode("utf-8")))
                print("sent")
                
        threadLock.release()
        print("START GAME")
        break

    #The real game starts here. Each while loop we look where players are and if someone is SAFE we send and game ending message to everyone.
    #We also send the worldstate each while loop.
    endgame =False
    while True:
        threadLock.acquire()


            #Gamequeue has the list of players playing.
        for c in gameQueue.keys():
            clientsocket = gameQueue[c][2]
            
            #If the first player has fhound the treasure, send add to the worldstate "GAME OVER" message
            #that includes who won the game.

            if c in worldstate and worldstate[c] == "SAFE":
                print(" Player: "+ c + " IS SAFE and found the treasure")
                worldstate["GAME OVER"] = "GAME OVER! Player {} won the game!".format(c)
                msg = pickle.dumps(worldstate)
                #try:
                for c in gameQueue.keys():
                    clientsocket = gameQueue[c][2]
                    clientsocket.send(msg)
                endgame=True
            #If no one has found the treasure yet, send everyone the current worldstate   
            else:
                msg = pickle.dumps(worldstate)
                clientsocket.send(msg)
                for c in worldstate:
                    if worldstate[c] != "SAFE":
                        print("Game " + worldstate[c][1] + " Player: " + c + " at " + worldstate[c][3]+"."+worldstate[c][4])
                        #print("worldstate is: {}".format(worldstate))
                    else:
                        print(" Player: " + c + " is finnished")
        threadLock.release()
        time.sleep(1.5)
        if endgame == True:
            STOP = 1
            break        



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

