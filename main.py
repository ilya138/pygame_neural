import random, math, pygame
from pygame.locals import *

# constants
WINSIZE = [640, 480]
WINCENTER = [320, 240]
NUMSTARS = 150
white = 255, 255, 255
black = 0, 0, 0

class Bonus():

    speed = 1
    pos = (WINSIZE[1], random.randint(50, WINSIZE[1] - WINSIZE[1]//3))
    size = random.randint(5, 10)

    def tick(self, surface, pixel):
        
        pygame.draw.circle(surface, black, self.pos, self.size)
        self.pos = (self.pos[0] - self.speed, self.pos[1])

        circle = pygame.draw.circle(surface, white, self.pos, self.size)


        #check overlapping with pixel

class Pixel():

    #main object
    Rect = None
    velocity = 0

    def tick(self, surface):

        y = int(self.Rect.y - self.velocity)

        if y >= self.start_y:
            self.velocity = 0
        else:
            self.draw(surface, black)
            self.Rect.move_ip(0, -self.velocity)
            self.velocity = self.velocity - 0.5
            self.draw(surface, white)

    def draw(self, surface, color):
        pygame.draw.rect(surface, color, self.Rect)

    def __init__(self, surface):
        self.Rect = pygame.draw.rect(surface, white, (100, WINSIZE[1] - 50, 6, 6))
        self.start_y = self.Rect.y

def main():

    random.seed()
    clock = pygame.time.Clock()

    # initialize and prepare screen
    pygame.init()
    screen = pygame.display.set_mode(WINSIZE)
    pygame.display.set_caption("Neural test")

    pixel = Pixel(screen)
    #bonus = Bonus(screen)

    # main game loop
    while 1:

        pixel.tick(screen)
        #bonus.tick(screen, pixel)

        pygame.display.update()
        for e in pygame.event.get():
            if hasattr(e, "key") and e.key in [K_UP, K_SPACE]:
                pixel.velocity = 10
        clock.tick(60)


# if python says run, then we should run
if __name__ == "__main__":
    main()