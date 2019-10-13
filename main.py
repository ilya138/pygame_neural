import random, math, pygame, sys, datetime
from pygame.locals import *

# constants
WINSIZE = [640, 480]
WINCENTER = [320, 240]
COLOR_WHITE = 255, 255, 255
COLOR_BLACK = 0, 0, 0
PIPE_WIDTH = 50
PIPE_SPEED = 3
GRAVITY = 0.98
BIRD_START_X = 100
BIRD_START_Y = 50
BIRD_SIZE = 20
BIRD_JUMP_VELOCITY = 5

class PipeLine():

    topPipeSprite = None
    bottomPipeSprite = None 
    x = None

    def tick(self, scene):
        
        pygame.draw.rect(scene, COLOR_BLACK, self.topPipeSprite)
        pygame.draw.rect(scene, COLOR_BLACK, self.bottomPipeSprite)

        self.topPipeSprite.move_ip(-PIPE_SPEED, 0)
        self.bottomPipeSprite.move_ip(-PIPE_SPEED, 0)

        pygame.draw.rect(scene, COLOR_WHITE, self.topPipeSprite)
        pygame.draw.rect(scene, COLOR_WHITE, self.bottomPipeSprite)

        self.x = self.topPipeSprite.x

    def __init__(self, scene):

        self.gap_pos_y = random.randint(50, WINSIZE[1] - 120)
        self.gap_size = random.randint(80, 120)
        
        topPipeSpritePos = (WINSIZE[0] - PIPE_WIDTH, 0, PIPE_WIDTH, self.gap_pos_y)
        bottomPipeSpritePos = (WINSIZE[0] - PIPE_WIDTH, self.gap_pos_y + self.gap_size, PIPE_WIDTH, WINSIZE[1] - self.gap_pos_y + self.gap_size)
        self.topPipeSprite = pygame.draw.rect(scene, COLOR_WHITE, topPipeSpritePos)
        self.bottomPipeSprite = pygame.draw.rect(scene, COLOR_BLACK, bottomPipeSpritePos)
        self.x = self.topPipeSprite.x
        
class Bird():

    sprite = None
    velocity = 0
    score = 0
    dead = False
    color = None

    def __init__(self, scene, color=COLOR_WHITE):
        self.sprite = pygame.draw.rect(scene, color, (BIRD_START_X, BIRD_START_Y, BIRD_SIZE, BIRD_SIZE))
        self.created = datetime.datetime.now()

    def tick(self, scene):

        if self.dead:
            return

        y = int(self.sprite.y - self.velocity)

        if y <= 0 or y >= WINSIZE[1]:
            self.kill()
        else:
            self.draw(scene, COLOR_BLACK)

            self.sprite.move_ip(0, -self.velocity)
            self.velocity = self.velocity - GRAVITY
            self.draw(scene, COLOR_WHITE)

    def draw(self, scene, color):

        global font
        pygame.draw.rect(scene, color, self.sprite)
        score_text = font.render("{}".format(self.score), True, COLOR_BLACK)
        scene.blit(score_text, self.sprite)

    def jump(self):
        self.velocity = BIRD_JUMP_VELOCITY

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
    birds = []
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
                    for bird in birds:
                        bird.jump()
                elif e.key == K_SPACE and not game_started:
                    pipeLines = [PipeLine(scene)]
                    birds = [Bird(scene)]
                    game_started = True
                    scene.fill(COLOR_BLACK)

        if not game_started:
            text = font.render("Press SPACE to start the game", True, COLOR_WHITE)
            scene.blit(text, (WINSIZE[0] // 3, WINSIZE[1] // 2))
        else:    
            for bird in birds:
                bird.tick(scene)

                for pipeLine in pipeLines:
                    pipeLine.tick(scene)

                    if bird.overlaps(pipeLine):
                        bird.kill()

                if bird.sprite.x >= pipeLine.x and len(pipeLines) == 1:
                    pipeLines.append(PipeLine(scene))
                    bird.score += 1

        if all(bird.dead for bird in birds):
            game_started = False

        for pipeToDelete in [pipe for pipe in pipeLines if pipe.x < -PIPE_WIDTH]:
            pipeLines.remove(pipeToDelete)

        clock.tick(60)

if __name__ == "__main__":
    main()