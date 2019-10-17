# Flappy bird game using pygame + self-taught algorithm (tensorflow, keras)
#
# Ilya Zakharov, 2019
#

import gamecore as core
import numpy as np

GA_NUMBER_OF_PLAYERS = 5
MT_TRAINING_DATA_FRAMERATE = 10
MT_PIPES_TO_LEARN = 5
JUMP_DECISION_RATE = 0.6

def GeneticAlgorithm_Initialize(game):
    game.numberOfPlayers = GA_NUMBER_OF_PLAYERS
    game.drawLoadingScreen()

    import neural

    # initialize neural network for each player
    for player in game.players:
        setattr(player, 'neural', neural.NeuralNetwork(fillInitialData=True))

def GeneticAlgorithm_tick(game):
    neuralJump(game)

def ManualTraining_Initialize(game):
    # In this mode player teaches the neural network with the following approach:
    #  When player jumped, a new training data element is added with appropriate inputs and "1" as output data;
    #  Every [MT_TRAINING_DATA_FRAMERATE] frames, a new training data element is added with appropriate inputs and "0" as output data;
    #  The process continues for the first [MT_PIPES_TO_LEARN] pipes. After that, the keyboard input is disabled and the neural network takes control. 

    game.drawLoadingScreen()

    import neural
    for player in game.players:
        setattr(player, 'neural', neural.NeuralNetwork())
        setattr(player, 'learning', True)

def ManualTraining_tick(game, actionsDone):
    neuralJump(game)

    pipePos = getNextPipePositions(game)
    for player in game.players:
        if player.learning:

            input = getNeuralInput(player, pipePos)
            if  "JUMP" in actionsDone:  
                player.neural.addTrainingDataElement(input, [1])
            elif game.frameCount % MT_TRAINING_DATA_FRAMERATE == 0:
                player.neural.addTrainingDataElement(input, [0])

            if player.score == MT_PIPES_TO_LEARN:
                player.learning = False
                player.neural.train()
    
def getNeuralInput(player, params):

    # The distance between player's y-axis coordinate and the middle of pipe's gap.
    input_gap = params["gap"] - player.pos.y
    # The distance between player's x-axis coordinate and the pipe center.
    input_pos = abs(params["pos"] - player.pos.x)

    neural_input = [input_gap, input_pos]
    return neural_input

def getNextPipePositions(game):
    gap, pos = 0, 0
    for pipe in game.pipeLines:
        if not pipe.passed:
            gap = pipe.gap_pos_y + pipe.gap_size // 2 # The y-axis coordinate of the middle of pipe's gap.
            pos = pipe.x + core.PIPE_WIDTH // 2 # The x-axis coordinate of the pipe center.
    return {"gap":gap, "pos":pos}

def neuralJump(game):
    pipePos = getNextPipePositions(game)

    for player in game.players:

        if player.dead or not hasattr(player, "neural"):
            continue

        if hasattr(player, "learning") and player.learning:
            continue

        neural_input = getNeuralInput(player, pipePos)
        jump_decision = player.neural.predict(neural_input)
        
        if jump_decision > JUMP_DECISION_RATE:
            player.jump()

def main():
    game = core.Game()
    game.drawModeSelection()
    game.displayUpdate()
    
    while game.mode == None:
        # Waiting for game mode to be selected
        game.controls()
        game.clock.tick(10)

    if game.mode == core.MODE_NEURALGA:
        game.numberOfPlayers = GA_NUMBER_OF_PLAYERS

    game.start()

    if game.mode == core.MODE_NEURALGA:
        GeneticAlgorithm_Initialize(game)
    elif game.mode == core.MODE_NEURALMT:
        ManualTraining_Initialize(game)
    elif game.mode == core.MODE_STANDARD:
        pass

    # main game loop
    while True:

        game.displayUpdate()
        
        # Handle key presses
        actionsDone = game.controls()

        if "START" in actionsDone:
            if game.mode == core.MODE_NEURALGA:
                GeneticAlgorithm_Initialize(game)
            elif game.mode == core.MODE_NEURALMT:
                ManualTraining_Initialize(game)
            elif game.mode == core.MODE_STANDARD:
                pass

        if game.started:  

            if game.mode == core.MODE_NEURALGA:
                GeneticAlgorithm_tick(game)
            elif game.mode == core.MODE_NEURALMT:
                ManualTraining_tick(game, actionsDone)
            elif game.mode == core.MODE_STANDARD:
                pass

            game.tick()
            game.drawScore()
            

if __name__ == "__main__":
    main()