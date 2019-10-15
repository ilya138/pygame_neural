# Flappy bird game using pygame + self-taught algorithm (tensorflow, keras)
#
# Ilya Zakharov, 2019
#

import gamecore as core
import numpy as np

NUMBER_OF_PLAYERS = 5

# MODE:
# 1 = Standard game, 
# 2 = Neural + GA, 
# 3 = Neural based on player

def main():

    game = core.Game()
    scene = game.scene

    game.drawModeSelection()
    game.displayUpdate()
    
    while game.mode == 0:
        game.controls()
        game.clock.tick(10)

    game.numberOfPlayers = NUMBER_OF_PLAYERS
    game.start()

    if game.mode == 2:
        import neural
        # initialize neural network for each player
        for player in game.players:
            player.neural = lambda: None
            setattr(player, 'neural', neural.NeuralNetwork())

    # main game loop
    while True:

        game.displayUpdate()
        
        # Handle key presses
        game.controls()

        if game.started:  

            if game.mode == 2:
                # Neural
                gap = 0
                pos = 0
                for pipe in game.pipeLines:
                    if not pipe.passed:
                        gap = pipe.gap_pos_y + pipe.gap_size // 2
                        pos = pipe.x
                        break

                for player in game.players:
                    if player.dead:
                        continue

                    input_gap = abs(gap - player.y)
                    input_pos = abs(pos - player.sprite.x)
                    neural_input = np.array([[input_gap]])
                    jump_decision = player.neural.predict(neural_input)
                    
                    if jump_decision >= 0.6:
                        player.jump()

            game.tick()
            game.drawScore()

if __name__ == "__main__":
    main()