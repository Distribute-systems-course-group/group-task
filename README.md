# Distributed system course group 

## The purpose and core functionality of the project

Our project is a multi-player treasure hunt game that consist of the controlling server and requires two player clients. The server will get x and y coordinates where the treasure will be hidden. The game instance begins when we have 2 players online queuing for a game. All players start at coordinates 0.0 (x=0. y=0). By pressing arrow buttons the players move and the player who reaches the given treasure coordinates first will win the game.

## System design (using the 3 principles from the lectures; architecture, processes, communication)

Both the player and server make an UDP thread for handling player action data and a TCP thread for communication between connections. The player client sends with the worldstate what arrow buttons have been pressed and the game management server makes the decicion where the user will be moved based on that information. The players get the information about their locations by reading their own indexes from the worldstate coming from the server. For the better server performance the worldstate is updated using UDP and sent through TCP.

![alt test](/system%20discription.PNG)

## Problems encountered, lessons learned

## Instructions for installation and execution

1. For testing the game on three separate nodes, install the Virtual Box or make sure you can install the project code to three different endpoints. For each end, ...
2. Clone or download the project code from https://github.com/Distribute-systems-course-group/group-task.
3. Make sure that you have Python and Keyboard library installed (pip install keyboard). 
4. From your own computer terminal, go to the project root file and run python server.py If running correctly, server asks you to give x.y coordinates for hiding the treasure. Feed the coordinates and then the server should be up and running.
5. From the other end point terminal, go to the project root file and run python client.py If running correctly, client asks you to give a client id for the player. Feed the client id and then the client should be waiting for a game. Now server should declare that the connection has been established and the client has been added to the list.
6. Connect a second player from the third end point to the game. Now the server should start the game. Players will get notified that the game has started.

## Questions and answers

### What is the average time for sending 50 messages between two nodes (random payload)?

### Choose 3 different fixed message sizes (payloads for min, average, max), what is the average time when sending 25 in each case?

### Choose a unique payload, e.g., average size, and then measure the inter arrival rate between messages?

### How reliable is your architecture? What kind of applications can benefit from this architectural flavor?
