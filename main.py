# Flappy bird game using pygame + self-taught algorithm (tensorflow, keras)
#
# Ilya Zakharov, 2019
#

import gamecore as core

def main():

    game = core.Game()
    scene = game.scene

    game.drawNewGameMessage()

    # main game loop
    while True:

        game.displayUpdate()
        
        # Handle key presses
        game.controls()

        if game.started:  
            game.tick()
            game.drawScore()

if __name__ == "__main__":
    main()