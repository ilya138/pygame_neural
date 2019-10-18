# Flappy bird game using pygame + self-taught algorithm (tensorflow, keras)
#
# Ilya Zakharov, 2019
#

import gamecore as core
import numpy as np
import time
import random

GA_NUMBER_OF_PLAYERS = 5
MT_TRAINING_DATA_FRAMERATE = 10
MT_PIPES_TO_LEARN = 5
JUMP_DECISION_RATE = 0.55

def GeneticAlgorithm_Initialize(game, children=None):
    import neural

    if not hasattr(game, 'generation'):
        setattr(game, 'generation', 1)
    else:
        game.generation += 1

    # initialize neural network for each player
    count = 0
    for player in game.players:
        count += 1

        game.drawLoadingScreen("Training players {}/{}".format(count, game.numberOfPlayers))
        core.pygame.event.get()

        if children:
            network = neural.NeuralNetwork(False)
            child = children.pop()
            network.training_data = child["input"]
            network.target_data = child["output"]
            network.train()
        else:
            network = neural.NeuralNetwork(True)

        setattr(player, 'neural', network)            


def GeneticAlgorithm_tick(game):

    if game.started:
        neuralJump(game)

        playersAlive = len([player for player in game.players if not player.dead])
        Text = "Players alive: {}/{}".format(playersAlive, game.numberOfPlayers)
        game.drawTextMessage(Text, 20, 40)
        game.drawTextMessage("Generation: {}".format(game.generation), 20, 60)

    else:

        game.players.sort(key=lambda player: player.lifeTime, reverse=True)
        parent1 = {"input" : game.players[0].neural.training_data, 
                   "output" : game.players[0].neural.target_data}
        parent2 = {"input" : game.players[1].neural.training_data, 
                   "output" : game.players[1].neural.target_data}
        
        # crossover
        children = crossover(parent1, parent2)

        # repeat
        game.start()
        GeneticAlgorithm_Initialize(game, children)

def crossover(parent1, parent2):

    numberOfGens = len(parent1["input"])
    children = []

    for iteration in range(GA_NUMBER_OF_PLAYERS):
        child = {"input" : [],
                 "output" : []}

        for gen in range(numberOfGens):
            genOwner = random.choice([parent1, parent2])

            childInput = genOwner["input"][gen]
            childOutput = genOwner["output"][gen]

            if random.random() < 0.05:
                # mutate gen
                if random.random() > 0.5:
                    # mutate output
                    childOutput = [random.random()]
                else:
                    # mutate input
                    childInput = neural.getRandomInput()

            child["input"].append(childInput)
            child["output"].append(childOutput)

        children.append(child)

    return children

def ManualTraining_Initialize(game):
    # In this mode player teaches the neural network with the following approach:
    #  When player jumped, a new training data element is added with appropriate inputs and "1" as output data;
    #  Every [MT_TRAINING_DATA_FRAMERATE] frames, a new training data element is added with appropriate inputs and "0" as output data;
    #  The process continues for the first [MT_PIPES_TO_LEARN] pipes. After that, the keyboard input is disabled and the neural network takes control. 
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
            if "JUMP" in actionsDone:  
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
            pos = pipe.x + core.PIPE_WIDTH # The x-axis coordinate of the pipe center.
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
        game.clock.tick(1)

    if game.mode == core.MODE_NEURALGA:
        game.numberOfPlayers = GA_NUMBER_OF_PLAYERS

    game.drawLoadingScreen("Initializing Tensorflow")
    game.displayUpdate()
    core.pygame.event.get()
    game.start()

    if game.mode == core.MODE_NEURALGA:
        GeneticAlgorithm_Initialize(game)
    elif game.mode == core.MODE_NEURALMT:
        ManualTraining_Initialize(game)

    # main game loop
    while True:

        game.displayUpdate()
        
        # Handle key presses
        actionsDone = game.controls()

        if "START" in actionsDone:
            if game.mode == core.MODE_NEURALMT:
                ManualTraining_Initialize(game)

        if game.started:  

            game.tick()
            game.drawScore()

            if game.mode == core.MODE_NEURALMT:
                ManualTraining_tick(game, actionsDone)
            elif game.mode == core.MODE_STANDARD:
                pass

        if game.mode == core.MODE_NEURALGA:
            GeneticAlgorithm_tick(game)

if __name__ == "__main__":
    main()