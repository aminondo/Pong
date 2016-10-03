# Pong

Authors: Keith Kinnard, Antonio Minondo

Note: Have to edit game_client.py to the computer's IP address in order to communicate to the game host


Two-Player pong game, each player has a paddle controlled using the arrow keys. The point of the game is to prevent the ball from going past your paddle. First one to three points wins.

The game is run by a player host, the other player connects to the game server. The player host runs the file game_host.py, and the other player runs game_client.py. The game will start once both players press spacebar. After someone scores, the game resets, the score is updated, and the game waits for both players to press spacebar again. Once someone wins, the players have the option of playing again by pressing spacebar.



 
