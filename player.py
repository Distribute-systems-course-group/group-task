import socket
import sys
import threading
import time  
import keyboard
import json
HEADERSIZE = 10
BUFFER_SIZE = 1024
threadLock = threading.RLock()

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
        if self.name == "TCPThread":
            threadLock.acquire()
            TCP(self.worldstate, self.ClientID,self.playerstate)
        else:
            threadLock.acquire()
            UDP(self.playerstate,self.worldstate)
            threadLock.release()
        print("Exiting " + self.name)


def TCP(worldstate,ClientID,playerstate):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCP_IP = socket.gethostname()
    TCP_PORT = 12345
    tryagain= True
    mustend = time.time() + 120
    gamedata = False
    msg =""
    try:
        s.connect((TCP_IP, TCP_PORT))
    except:
        print("connection failed")
        sys.exit()

    HEADER= str(ClientID) +"_"+str(1)+"_"+str(len(msg)) +"_"
    MESSAGE = HEADER + msg
    s.send(bytes(MESSAGE,"utf-8"))

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

    while True:
        while time.time() < mustend:
            try:
                data = s.recv(BUFFER_SIZE)
                data = data.decode("utf-8")
                gamedata = True
                break
            except:
                print(mustend-time.time())
                time.sleep(1)    
        if gamedata == False:
            wait = int(input("No game was found. press 1 to continue waiting or 0 to stop."))
            if wait != 1:
                print("Quitting game")
                s.close()
                sys.exit()
        else:
            data = data.split("_")
            print(type(data[3]))
            instanceID= data[0] 
            worldstate = json.loads(data[3])
            print(type(worldstate))
            playerstate["InstanceID"] = data[0]
            break
    print("Joined game: {}".format(data))
    threadLock.release()
    time.sleep(0.3)

    while True:
        #print("trying to get something")
        threadLock.acquire()
        #print("acquired worked!")
        try:
            data = s.recv(BUFFER_SIZE)
            data = data.decode("utf-8")
            gamedata = True
            
        except:
            print("No data was recieved" + str(mustend-time.time()))
            time.sleep(0.1)    
        if gamedata == False:
            wait = int(input("No game was found. press 1 to continue waiting or 0 to stop."))
            if wait != 1:
                print("Quitting game")
                s.close()
                sys.exit()
        else:
            data = data.split("_")
            #print("GOT SOMETHING:  {}".format(data))
            if data[3] == "YOU ARE SAFE!!":
                playerstate["x"] = "STOP"
                threadLock.release()
                time.sleep(2)
                break
            worldstate = data[3]
            print("The current worldstate :{}".format(worldstate))
            threadLock.release()
            time.sleep(2)
    print("You got away! Finished game!")    

def UDP(playerstate,worldstate):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDP_IP = socket.gethostname()
    UDP_PORT = 5005
    #Let's check for player movement
    print("We are starting in Game {}".format(playerstate["InstanceID"]))
    print("READY,SET,GO!")
    while True:  
        if playerstate["x"] == "STOP":
            break
        #print("Player at:" + str(worldstate[playerstate["ClientID"]][3]) +"." + str(worldstate[playerstate["ClientID"]][4]) )
        if keyboard.is_pressed('up'):
            print("pressed up")
            playerstate["y"] = playerstate["y"]+1 
        if keyboard.is_pressed("down"):
            print("pressed down")
            playerstate["y"] = playerstate["y"]-1
        if keyboard.is_pressed('right'):
            print("pressed right")
            playerstate["x"] = playerstate["x"]+1 
        if keyboard.is_pressed('left'):
            print("pressed left")
            playerstate["x"] = playerstate["x"]-1
        if keyboard.is_pressed('esc'):
            break
        
        playerstate["timestamp"] = time.time()
        msg = str(playerstate["ClientID"])+"_"+ str(playerstate["InstanceID"])+"_"+ str(playerstate["timestamp"])+"_"+str(playerstate["x"])+"_"+ str(playerstate["y"])
        s.sendto(bytes(msg,"utf-8"),(UDP_IP, UDP_PORT))
        threadLock.release()
        time.sleep(0.7)
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
