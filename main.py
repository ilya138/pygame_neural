import random, math, pygame
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

    rect_Top_Pipe = None
    rect_Bottom_Pipe = None 
    x = None

    def tick(self, scene):
        
        pygame.draw.rect(scene, COLOR_BLACK, self.rect_Top_Pipe)
        pygame.draw.rect(scene, COLOR_BLACK, self.rect_Bottom_Pipe)

        self.rect_Top_Pipe.move_ip(-PIPE_SPEED, 0)
        self.rect_Bottom_Pipe.move_ip(-PIPE_SPEED, 0)

        pygame.draw.rect(scene, COLOR_WHITE, self.rect_Top_Pipe)
        pygame.draw.rect(scene, COLOR_WHITE, self.rect_Bottom_Pipe)

        self.x = self.rect_Top_Pipe.x

    def __init__(self, scene):

        self.gap_pos_y = random.randint(50, WINSIZE[1] - 120)
        self.gap_size = random.randint(80, 120)
        
        topPipePos = (WINSIZE[0] - PIPE_WIDTH, 0, PIPE_WIDTH, self.gap_pos_y)
        bottomPipePos = (WINSIZE[0] - PIPE_WIDTH, self.gap_pos_y + self.gap_size, PIPE_WIDTH, WINSIZE[1] - self.gap_pos_y + self.gap_size)
        self.rect_Top_Pipe = pygame.draw.rect(scene, COLOR_WHITE, topPipePos)
        self.rect_Bottom_Pipe = pygame.draw.rect(scene, COLOR_BLACK, bottomPipePos)
        self.x = self.rect_Top_Pipe.x
        

class Bird():

    rect = None
    velocity = 0
    score = 0
    dead = False

    def tick(self, scene):

        if self.dead:
            return

        y = int(self.rect.y - self.velocity)

        if y <= 0 or y >= WINSIZE[1]:
            self.kill()
        else:
            self.draw(scene, COLOR_BLACK)
            self.rect.move_ip(0, -self.velocity)
            self.velocity = self.velocity - GRAVITY
            self.draw(scene, COLOR_WHITE)

    def draw(self, scene, color):

        global font
        pygame.draw.rect(scene, color, self.rect)
        score_text = font.render("{}".format(self.score), True, COLOR_BLACK)
        scene.blit(score_text, self.rect)

    def jump(self):
        self.velocity = BIRD_JUMP_VELOCITY

    def overlaps(self, pipes):
        return pipes.rect_Top_Pipe.colliderect(self.rect) or pipes.rect_Bottom_Pipe.colliderect(self.rect)

    def __init__(self, scene):
        self.rect = pygame.draw.rect(scene, COLOR_WHITE, (BIRD_START_X, BIRD_START_Y, BIRD_SIZE, BIRD_SIZE))

    def kill(self):
        self.dead = True

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
            if hasattr(e, "key"):
                if e.key == K_UP:
                    for bird in birds:
                        bird.jump()
                elif e.key == K_SPACE and not game_started:
                    pipeLines = [PipeLine(scene)]
                    birds = [Bird(scene)]
                    game_started = True
                    scene.fill(COLOR_BLACK)
            elif e.type == MOUSEBUTTONDOWN:
                for bird in birds:
                    bird.jump()  

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

                if bird.rect.x >= pipeLine.rect_Top_Pipe.x and len(pipeLines) == 1:
                    pipeLines.append(PipeLine(scene))
                    bird.score += 1

        if all(bird.dead for bird in birds):
            game_started = False

        for lineToDelete in [pipe for pipe in pipeLines if pipe.x < -PIPE_WIDTH]:
            pipeLines.remove(lineToDelete)

        clock.tick(60)

# if python says run, then we should run
if __name__ == "__main__":
    main()