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
PIPE_START_SPEED = 3
PIPE_GAP_MIN = 100
PIPE_GAP_MAX = 150
PIPE_HEADER_HEIGHT = 42

# Player
PLAYER_START_X = 100
PLAYER_START_Y = 50
PLAYER_SIZE = 40
PLAYER_JUMP_VELOCITY = 5
PLAYER_GRAVITY = 0.98
PLAYER_COLOR_OFFSET = 10000

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

    sprite = None
    velocity = 0
    score = 0
    dead = False
    color = None
    y = 0

    def __init__(self, scene, color=COLOR_WHITE):
        self.sprite = pygame.draw.rect(
            scene, color, (PLAYER_START_X, PLAYER_START_Y, PLAYER_SIZE, PLAYER_SIZE))
        self.created = datetime.datetime.now()

        colorOffset = random.randint(1, 10) * PLAYER_COLOR_OFFSET
        sprite = copy.copy(PLAYER_SPRITE)
        image_pixel_array = pygame.PixelArray(sprite)
        for row in image_pixel_array:
            row[:] = [x + colorOffset for x in row]
        del image_pixel_array
        self.image = sprite

    def tick(self, scene):

        if self.dead:
            return

        self.y = int(self.sprite.y - self.velocity)

        if self.y <= 0 or self.y >= WINSIZE[1]:
            self.kill()
        else:
            self.sprite.move_ip(0, -self.velocity)
            self.velocity = self.velocity - PLAYER_GRAVITY
            self.draw(scene)

    def draw(self, scene):
        scene.blit(self.image, self.sprite)

    def jump(self):
        self.velocity = PLAYER_JUMP_VELOCITY

    def overlaps(self, pipes):
        for pipe in pipes:
            if pipe.topPipeSprite.colliderect(self.sprite) or pipe.bottomPipeSprite.colliderect(self.sprite):
                return True
        return False

    def kill(self):
        self.dead = True
        self.lifeTime = (datetime.datetime.now() - self.created).microseconds
                        
class Game():

     # initialize and prepare scene
    random.seed()
    clock = pygame.time.Clock()
    pygame.init()
    scene = pygame.display.set_mode(WINSIZE)

    font = pygame.font.SysFont(pygame.font.get_default_font(), 20)
    pygame.display.set_caption("Flappy bird + neural")
    
    pipeSpeed = PIPE_START_SPEED

    text = font.render("Loading...", True, COLOR_WHITE, 20)
    scene.blit(text, (20, 20))
    pygame.display.update()

    numberOfPlayers = 1
    mode = 0

    def __init__(self):
        self.started = False
        self.players = []
        self.pipeLines = []
        self.maxScore = 0

    def start(self):
        self.players = []
        for i in range(self.numberOfPlayers):
            self.players.append(Player(self.scene))

        self.pipeLines = [PipeLine(self.scene)]
        self.started = True
        self.scene.fill(COLOR_BACKGROUND)

    def controls(self):
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                elif e.key == K_UP:
                    for player in self.players:
                        player.jump()
                elif e.key == K_SPACE and not self.started:
                    self.start()
                elif self.mode == 0:
                    if e.key == K_1:
                        self.mode = 1
                    elif e.key == K_2:
                        self.mode = 2

    def drawScore(self):
        self.maxScore = max(player.score for player in self.players)
        self.drawTextMessage("Score: {}".format(self.maxScore), 20, 20)

    def drawNewGameMessage(self):
        self.drawTextMessage("Press SPACE to start the game", WINSIZE[0] // 3, WINSIZE[1] // 2)

    def drawModeSelection(self):
        self.scene.fill(COLOR_BLACK)
        self.drawTextMessage("Select the game mode:", 20, 40)
        self.drawTextMessage("1 - Just play", 20, 55)
        self.drawTextMessage("2 - Neural network", 20, 70)
        self.drawTextMessage("3 - Neural network (manual training)", 20, 85)

    def drawTextMessage(self, message, x, y, color=COLOR_WHITE, size=20):
        text = self.font.render(message, True, color, size)
        self.scene.blit(text, (x, y))      

    def displayUpdate(self):
        pygame.display.update()

    def tick(self):

        self.displayUpdate()
        self.scene.fill(COLOR_BACKGROUND)

        scored = False
        for pipeLine in self.pipeLines:
            pipeLine.tick(self.scene, self.pipeSpeed)

            if not pipeLine.passed and pipeLine.x < PLAYER_START_X:
                pipeLine.passed = True
                if len(self.pipeLines) == 1:
                    # player has passed the pipe. Let's generate a new one
                    self.pipeLines.append(PipeLine(self.scene))
                scored = True

        for player in self.players:
            player.tick(self.scene)

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


