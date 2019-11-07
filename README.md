# Distributed system course group 

## Multiplayer game
Here is the multiplayer game I have done. It requires at the moment 2 players. Both the player ad server make an UDP thread and a TCP thread for communication. UDP is used to send player action data and TCP for handling connections and sending world state (though I would suggest switching the worldstate to UDP.)

### Gameplay
The game instance begins when we have 2 players online queuing for a game. All players start at coordinates 0.0 (x=0. y=0). By pressing arrow buttons the players move and they are safe when they reach the point 5.5. At the moment the game does not end until all players reach this point. It could be switch so that when anyone reaches the goal, the game ends.

### Fixes required
At the moment the server is slow to update the worldstate. It could be fixed by putting the worldstate updates to UDP instead of TCP.
