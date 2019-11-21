import socket
import sys
import threading
import time  
import keyboard
import json
import pickle 
HEADERSIZE = 10
BUFFER_SIZE = 1024
threadLock = threading.RLock()

#We make 2 threads for the palyer. One TCP and UDP. 
#UDP sends user movement data, TCP creates thee connection
class myThread (threading.Thread):
    def __init__(self, threadID, name,playerstate,worldstate):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.playerstate = playerstate
        self.ClientID = self.playerstate["ClientID"]
        self.worldstate = worldstate

    def run(self):
        print("Starting " + self.name)
        #The TCP thread gets the lock first to get access to resources
        if self.name == "TCPThread":
            threadLock.acquire()
            TCP(self.worldstate, self.ClientID,self.playerstate)
        else:
            #When the TCP releases the lock when the game will start, the UDP thread commences.
            threadLock.acquire()
            UDP(self.playerstate,self.worldstate)
            threadLock.release()
        print("Exiting " + self.name)

#The TCP thread starts first, connecting to the server
def TCP(worldstate,ClientID,playerstate):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCP_IP = socket.gethostname()
    TCP_PORT = 12345
    tryagain= True
    mustend = time.time() + 120
    gamedata = False
    msg =""
    
    #Trying to connect to server
    try:
        s.connect((TCP_IP, TCP_PORT))
    except:
        print("connection failed")
        sys.exit()
    #The header includes also the length of the message, it is unneeded but removing it means changes to all array indexes
    #We separate headers with _ character
    HEADER= str(ClientID) +"_"+str(1)+"_"+str(len(msg)) +"_"
    MESSAGE = HEADER + msg
    
    #And we send the first message to start queuing
    s.send(bytes(MESSAGE,"utf-8"))
    
    #We wait until we get a reply from the server that we are in queue
    while tryagain == True:
        try:
            data = s.recv(BUFFER_SIZE)
            data = data.decode("utf-8")
            print(data)
            tryagain= False
        except:
            print("Server did not answer your request.")
            tryagain = int(input("Do you want to try again? True for yes False for no."))
    print("Waiting for a game...")
    
    #Here we queue for 2 min(=mustend time) for a game. If not game in that time, then we quit
    while True:
        while time.time() < mustend:
            try:
                data = s.recv(BUFFER_SIZE)
                data = data.decode("utf-8")
                gamedata = True
                break
            except:
                time.sleep(1)    
        if gamedata == False:
            wait = int(input("No game was found. press 1 to continue waiting or 0 to stop."))
            if wait != 1:
                print("Quitting game")
                s.close()
                sys.exit()
        else:
            #We have a game. The server has sent the Instance ID and worldstate
            data = data.split("_")
            instanceID= data[0]
            playerstate["InstanceID"] = data[0]
            break
    print("Joined game: {}".format(data))
    threadLock.release()
    time.sleep(0.3)

    #We begin game by trying to aquire worldstate from the server.
    while True:
        threadLock.acquire()
        try:
            msg = s.recv(BUFFER_SIZE)
            gamedata = True
            
        except:
            print("No data was recieved" + str(mustend-time.time()))
            threadLock.release()
            time.sleep(0.1)
            continue  
        if gamedata == False:
           wait = int(input("No game was found. press 1 to continue waiting or 0 to stop."))
           if wait != 1:
               print("Quitting game")
               s.close()
               sys.exit()
        #We have worldstate coming from server.
        else:
            try:
                data = pickle.loads(msg)
            except:
                threadLock.release()
                break
            for id in data:
                worldstate[id] = data[id]
            

            print("The current worldstate :{}".format(worldstate))
            threadLock.release()
            time.sleep(1.5)
    if "GAME OVER" in worldstate:
        print(worldstate["GAME OVER"])
    print("Finished game!")    

#UDP send user arrow input data to the server. UDP starts running when TCP releases the lock after the game starts.
def UDP(playerstate,worldstate):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDP_IP = socket.gethostname()
    UDP_PORT = 5005
    
    #Let's check for player movement
    print("We are starting in Game {}".format(playerstate["InstanceID"]))
    print("READY,SET,GO!")
    #We loop here to catch player input. Playerstate is the players local understanding of positioning.
    #This should be fixed,so that when we get the worldtstate from the server we take our positioning from there.
    while True:  
        #print(worldstate)
        if playerstate["x"] == "STOP":
            break
        if "GAME OVER" in worldstate:
            break

        if len(worldstate) !=0:
            print("Player is at: "+ worldstate[str(playerstate["ClientID"])][3] + "." + worldstate[str(playerstate["ClientID"])][4])

        if keyboard.is_pressed('up'):
            print("pressed up")
            playerstate["y"] = 1 
        if keyboard.is_pressed("down"):
            print("pressed down")
            playerstate["y"] = -1
        if keyboard.is_pressed('right'):
            print("pressed right")
            playerstate["x"] = +1 
        if keyboard.is_pressed('left'):
            print("pressed left")
            playerstate["x"] = -1
        if keyboard.is_pressed('esc'):
            break
        #After a button push, we send our local state, with client ID,instance and timestamp to the server.
        playerstate["timestamp"] = time.time()
        msg = str(playerstate["ClientID"])+"_"+ str(playerstate["InstanceID"])+"_"+ str(playerstate["timestamp"])+"_"+str(playerstate["x"])+"_"+ str(playerstate["y"])
        #print("Send to server playerstate : {}".format(playerstate))
        s.sendto(bytes(msg,"utf-8"),(UDP_IP, UDP_PORT))
        threadLock.release()
        time.sleep(1.5)
        threadLock.acquire()







def main():

    worldstate = {}
    ClientDict = {}
    playerstate = {
        "ClientID": 0,
        "InstanceID": 0,
        "timestamp": time.time(),
        "x" : 0,
        "y" : 0

    }

    while True:
        try:
            ClientID = int(input("Give me your ClientID"))
            playerstate["ClientID"]= ClientID
            break
        except:
            print("I need an integer number please.")
   
    threads =[]
    TCPThread = myThread(1,"TCPThread",playerstate,worldstate)
    TCPThread.start()
    UDPThread = myThread(2,"UDPThread",playerstate,worldstate)
    UDPThread.start()
    threads.append(TCPThread)
    threads.append(UDPThread)
    for t in threads:
        t.join()
    print("Goodbye.")   

     


if __name__ == "__main__":
    main()

sys.exit()
