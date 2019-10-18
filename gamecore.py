import random
import pygame
import sys
import datetime
import copy
from pygame.locals import *

# constants
WINSIZE = [640, 480]
WINCENTER = [320, 240]

# Colors
COLOR_WHITE = 255, 255, 255
COLOR_BLACK = 0, 0, 0
COLOR_BACKGROUND = 107, 140, 255

# Pipes
PIPE_WIDTH = 100
PIPE_START_SPEED = 5
PIPE_GAP_MIN = 100
PIPE_GAP_MAX = 150
PIPE_HEADER_HEIGHT = 42

# Player
PLAYER_START_X = 100
PLAYER_START_Y = 50
PLAYER_SIZE = 40
PLAYER_JUMP_VELOCITY = 5
PLAYER_GRAVITY = 0.98
PLAYER_COLOR_OFFSET = 100

# Game
MODE_STANDARD = 'standard' # Standard game, 
MODE_NEURALGA = 'neuralGA' # Neural + GA, 
MODE_NEURALMT = 'neuralMT' # Neural based on player game style (manual training)
FPS = 60

# Sprites
PLAYER_SPRITE = pygame.transform.scale(pygame.image.load(
    'res/player.png'), (PLAYER_SIZE, PLAYER_SIZE))
PIPE_BODY_SPRITE = pygame.image.load('res/pipe.png')
PIPE_BOTTOM_SPRITE = pygame.transform.scale(pygame.image.load(
    'res/pipeTop.png'), (PIPE_WIDTH, PIPE_HEADER_HEIGHT))
PIPE_TOP_SPRITE = pygame.transform.flip(PIPE_BOTTOM_SPRITE, False, True)

class PipeLine():

    topPipeSprite = None
    bottomPipeSprite = None
    x = None
    passed = False

    def tick(self, scene, pipeSpeed):

        # workaround of bug when rect created outside the screen has negative width
        if self.topPipeSprite.width <= 0:
            self.topPipeSprite.width = PIPE_WIDTH
        if self.bottomPipeSprite.width <= 0:
            self.bottomPipeSprite.width = PIPE_WIDTH

        self.topPipeSprite.move_ip(-pipeSpeed, 0)
        self.bottomPipeSprite.move_ip(-pipeSpeed, 0)
        self.draw(scene)

        self.x = self.topPipeSprite.x

    def draw(self, scene):

        # Top pipe
        topPipeSprite = pygame.transform.scale(
            PIPE_BODY_SPRITE, (PIPE_WIDTH, self.topPipeSprite.h))
        scene.blit(topPipeSprite, self.topPipeSprite.topleft)
        scene.blit(
            PIPE_TOP_SPRITE, (self.topPipeSprite.bottomleft[0], self.topPipeSprite.bottomleft[1] - PIPE_HEADER_HEIGHT))

        # Bottom pipe
        bottomPipeSprite = pygame.transform.scale(
            PIPE_BODY_SPRITE, (PIPE_WIDTH, self.bottomPipeSprite.h))
        scene.blit(bottomPipeSprite, self.bottomPipeSprite.topleft)
        scene.blit(PIPE_BOTTOM_SPRITE, self.bottomPipeSprite.topleft)

    def __init__(self, scene):

        self.gap_pos_y = random.randint(50, WINSIZE[1] - PIPE_GAP_MAX)
        self.gap_size = random.randint(PIPE_GAP_MIN, PIPE_GAP_MAX)

        topPipeSpritePos = self.getpos(x=WINSIZE[0] + PIPE_WIDTH,
                                       y=0,
                                       width=PIPE_WIDTH,
                                       height=self.gap_pos_y)

        bottomPipeSpritePos = self.getpos(x=WINSIZE[0] + PIPE_WIDTH,
                                          y=self.gap_pos_y + self.gap_size,
                                          width=PIPE_WIDTH,
                                          height=WINSIZE[1] - self.gap_pos_y + self.gap_size)

        self.topPipeSprite = pygame.draw.rect(
            scene, COLOR_BACKGROUND, topPipeSpritePos)
        self.bottomPipeSprite = pygame.draw.rect(
            scene, COLOR_BACKGROUND, bottomPipeSpritePos)
        self.x = self.topPipeSprite.x

    def getpos(self, x, y, width, height):
        return (x, y, width, height)

class Player():

    pos = None
    sprite = None
    dead = False

    velocity = 0
    score = 0

    def __init__(self, scene, color=COLOR_WHITE):
        self.pos = pygame.draw.rect(
            scene, color, (PLAYER_START_X, PLAYER_START_Y, PLAYER_SIZE, PLAYER_SIZE))
        self.created = datetime.datetime.now()

        colorOffset = random.randint(1, 100) * PLAYER_COLOR_OFFSET
        sprite = copy.copy(PLAYER_SPRITE)
        image_pixel_array = pygame.PixelArray(sprite)
        for row in image_pixel_array:
            row[:] = [x + colorOffset for x in row]
        del image_pixel_array
        self.sprite = sprite

    def tick(self, scene):

        if self.dead:
            return

        y = int(self.pos.y - self.velocity)

        if y <= 0 or y >= WINSIZE[1]:
            self.kill()
        else:
            self.pos.move_ip(0, -self.velocity)
            self.velocity = self.velocity - PLAYER_GRAVITY
            self.draw(scene)

    def draw(self, scene):
        scene.blit(self.sprite, self.pos)

    def jump(self):
        self.velocity = PLAYER_JUMP_VELOCITY

    def overlaps(self, pipes):
        for pipe in pipes:
            if pipe.topPipeSprite.colliderect(self.pos) or pipe.bottomPipeSprite.colliderect(self.pos):
                return True
        return False

    def kill(self):
        if self.dead:
            return
        self.dead = True
        delta = (datetime.datetime.now() - self.created)
        self.lifeTime = float("{}.{}".format(delta.seconds, delta.microseconds))

                        
class Game():

    pygame.display.set_caption("Flappy bird + neural")

     # initialize and prepare scene
    clock = pygame.time.Clock()
    pygame.init()
    scene = pygame.display.set_mode(WINSIZE)
    frameCount = 0

    font = pygame.font.SysFont(pygame.font.get_default_font(), 20)
    
    pipeSpeed = PIPE_START_SPEED
    numberOfPlayers = 1
    mode = None

    def __init__(self):
        self.started = False
        self.players = []
        self.pipeLines = []
        self.maxScore = 0

        self.drawLoadingScreen()    

    def start(self):
        self.players = []
        for i in range(self.numberOfPlayers):
            self.players.append(Player(self.scene))

        self.pipeLines = [PipeLine(self.scene)]
        self.started = True

    def controls(self):
        actionsDone = []
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                elif e.key == K_UP:
                    for player in self.players:
                        player.jump()
                        actionsDone.append("JUMP")
                elif e.key == K_SPACE and not self.started:
                    self.start()
                    actionsDone.append("START")
                elif self.mode == None:
                    if e.key == K_1:
                        self.mode = MODE_STANDARD
                    elif e.key == K_2:
                        self.mode = MODE_NEURALGA
                    elif e.key == K_3:
                        self.mode = MODE_NEURALMT

        return actionsDone

    def drawScore(self):
        self.maxScore = max(player.score for player in self.players)
        self.drawTextMessage("Score: {}".format(self.maxScore), 20, 20)

    def drawNewGameMessage(self):
        self.drawTextMessage("Press SPACE to start the game", WINSIZE[0] // 3, WINSIZE[1] // 2)

    def drawModeSelection(self):
        self.scene.fill(COLOR_BLACK)
        self.drawTextMessage("Select game mode:", 20, 20)
        self.drawTextMessage("1 - Normal game", 20, 35)
        self.drawTextMessage("2 - Neural network", 20, 50)
        self.drawTextMessage("3 - Neural network (manual training)", 20, 65)

    def drawTextMessage(self, message, x, y, color=COLOR_WHITE, size=20):
        text = self.font.render(message, True, color, size)
        self.scene.blit(text, (x, y))      

    def displayUpdate(self):
        pygame.display.flip()

    def drawLoadingScreen(self, message="..."):
        self.scene.fill(COLOR_BLACK)
        self.drawTextMessage("Loading: {}".format(message), 20, 20)
        self.displayUpdate()
        pygame.event.get()

    def tick(self):

        self.displayUpdate()
        self.scene.fill(COLOR_BACKGROUND)

        scored = False
        for pipeLine in self.pipeLines:
            pipeLine.tick(self.scene, self.pipeSpeed)

            if not pipeLine.passed and pipeLine.x + PIPE_WIDTH < PLAYER_START_X:
                pipeLine.passed = True
                if len(self.pipeLines) == 1:
                    # The player has passed the pipe. Let's generate a new one
                    self.pipeLines.append(PipeLine(self.scene))
                scored = True

        for player in self.players:
            player.tick(self.scene)

            if player.dead:
                continue

            if player.overlaps(self.pipeLines):
                player.kill()
            if not player.dead and scored:
                player.score += 1

        # Delete pipes that were passed by the player and now out of screen
        for pipeToDelete in [pipe for pipe in self.pipeLines if pipe.x < -PIPE_WIDTH]:
            self.pipeLines.remove(pipeToDelete)

        # Speed slightly increases every 5 pipes
        self.pipeSpeed = PIPE_START_SPEED + self.maxScore // 5
      
        if all(player.dead for player in self.players):
            self.drawNewGameMessage()
            self.started = False

        self.clock.tick(FPS)
        self.frameCount += 1


