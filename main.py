import random, math, pygame, sys, datetime
from pygame.locals import *

# constants
WINSIZE = [640, 480]
WINCENTER = [320, 240]
COLOR_WHITE = 255, 255, 255
COLOR_BLACK = 0, 0, 0
COLOR_BACKGROUND = 107, 140, 255
PIPE_WIDTH = 50
PIPE_SPEED = 3
GRAVITY = 0.98
PLAYER_START_X = 100
PLAYER_START_Y = 50
PLAYER_SIZE = 20
PLAYER_JUMP_VELOCITY = 5

PLAYER_SPRITE = pygame.image.load('res/player.png')
PLAYER_SPRITE = pygame.transform.scale(PLAYER_SPRITE, (PLAYER_SIZE, PLAYER_SIZE))
PIPE_SPRITE = pygame.image.load('res/pipe.png')

class PipeLine():

    topPipeSprite = None
    bottomPipeSprite = None 
    x = None

    def tick(self, scene):
        
        self.clear(scene)
        self.topPipeSprite.move_ip(-PIPE_SPEED, 0)
        self.bottomPipeSprite.move_ip(-PIPE_SPEED, 0)
        self.draw(scene)

        self.x = self.topPipeSprite.x

    def clear(self, scene):
            pygame.draw.rect(scene, COLOR_BACKGROUND, self.topPipeSprite)
            pygame.draw.rect(scene, COLOR_BACKGROUND, self.bottomPipeSprite)
            
    def draw(self, scene):
        topPipeSprite = pygame.transform.flip(PIPE_SPRITE, False, True)
        topPipeSprite = pygame.transform.scale(topPipeSprite, (PIPE_WIDTH, self.topPipeSprite.h))
        bottomPipeSprite = pygame.transform.scale(PIPE_SPRITE, (PIPE_WIDTH, self.bottomPipeSprite.h))
        scene.blit(topPipeSprite, self.topPipeSprite.topleft)
        scene.blit(bottomPipeSprite, self.bottomPipeSprite.topleft)

    def __init__(self, scene):

        self.gap_pos_y = random.randint(50, WINSIZE[1] - 120)
        self.gap_size = random.randint(80, 120)
        
        topPipeSpritePos = (WINSIZE[0] - PIPE_WIDTH, 0, PIPE_WIDTH, self.gap_pos_y)
        bottomPipeSpritePos = (WINSIZE[0] - PIPE_WIDTH, self.gap_pos_y + self.gap_size, PIPE_WIDTH, WINSIZE[1] - self.gap_pos_y + self.gap_size)
        self.topPipeSprite = pygame.draw.rect(scene, COLOR_WHITE, topPipeSpritePos)
        self.bottomPipeSprite = pygame.draw.rect(scene, COLOR_BLACK, bottomPipeSpritePos)
        self.x = self.topPipeSprite.x
        
class Player():

    sprite = None
    velocity = 0
    score = 0
    dead = False
    color = None

    def __init__(self, scene, color=COLOR_WHITE):
        self.sprite = pygame.draw.rect(scene, color, (PLAYER_START_X, PLAYER_START_Y, PLAYER_SIZE, PLAYER_SIZE))
        self.created = datetime.datetime.now()

    def tick(self, scene):

        if self.dead:
            return

        y = int(self.sprite.y - self.velocity)

        if y <= 0 or y >= WINSIZE[1]:
            self.kill()
        else:
            self.clear(scene)
            self.sprite.move_ip(0, -self.velocity)
            self.velocity = self.velocity - GRAVITY
            self.draw(scene)

    def draw(self, scene):
        scene.blit(PLAYER_SPRITE, self.sprite)

    def clear(self, scene):
        pygame.draw.rect(scene, COLOR_BACKGROUND, self.sprite)

    def jump(self):
        self.velocity = PLAYER_JUMP_VELOCITY

    def overlaps(self, pipes):
        return pipes.topPipeSprite.colliderect(self.sprite) or pipes.bottomPipeSprite.colliderect(self.sprite)

    def kill(self):
        self.dead = True
        self.lifeTime = (datetime.datetime.now() - self.created).microseconds

def main():

    global font

    # initialize and prepare scene
    random.seed()
    clock = pygame.time.Clock()
    pygame.init()
    scene = pygame.display.set_mode(WINSIZE)

    font = pygame.font.SysFont(pygame.font.get_default_font(), 20)
    pygame.display.set_caption("Flappy bird + neural")

    pipeLines = []
    players = []
    game_started = False

    # main game loop
    while True:

        # Controls and stuff
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                elif e.key == K_UP:
                    for player in players:
                        player.jump()
                elif e.key == K_SPACE and not game_started:
                    pipeLines = [PipeLine(scene)]
                    players = [Player(scene)]
                    game_started = True
                    scene.fill(COLOR_BACKGROUND)

        if not game_started:
            text = font.render("Press SPACE to start the game", True, COLOR_WHITE)
            scene.blit(text, (WINSIZE[0] // 3, WINSIZE[1] // 2))
        else:    
            for player in players:
                
                player.tick(scene)

                for pipeLine in pipeLines:
                    pipeLine.tick(scene)

                    if player.overlaps(pipeLine):
                        player.kill()

                if player.sprite.x >= pipeLine.x and len(pipeLines) == 1:
                    pipeLines.append(PipeLine(scene))
                    player.score += 1

            maxScore = max(player.score for player in players)
            text = font.render("Score: {}".format(maxScore), True, COLOR_WHITE)
            scene.blit(text, (50, 20))

        if all(player.dead for player in players):
            game_started = False

        for pipeToDelete in [pipe for pipe in pipeLines if pipe.x < -PIPE_WIDTH]:
            pipeLines.remove(pipeToDelete)

        clock.tick(60)

if __name__ == "__main__":
    main()