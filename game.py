# Import
import pygame
import random
import time

from pygame.locals import (
    RLEACCEL, #this is for bliting speed improvement
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

font_name = pygame.font.match_font('arial')
def scoreboard(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, (22,140,55))
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surf.blit(text_surface, text_rect)


# Define the Player object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("jet.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()

    # Moving sprite
    # def update(self, pressed_keys):
    #     if pressed_keys[K_UP]:
    #         self.rect.move_ip(0, -7)
    #     if pressed_keys[K_DOWN]:
    #         self.rect.move_ip(0, 7)
    #     if pressed_keys[K_LEFT]:
    #         self.rect.move_ip(-7, 0)
    #     if pressed_keys[K_RIGHT]:
    #         self.rect.move_ip(7, 0)
    #
    #     # Keep player on the screen
    #     if self.rect.left < 0:
    #         self.rect.left = 0
    #     elif self.rect.right > SCREEN_WIDTH:
    #         self.rect.right = SCREEN_WIDTH
    #     if self.rect.top <= 0:
    #         self.rect.top = 0
    #     elif self.rect.bottom >= SCREEN_HEIGHT:
    #         self.rect.bottom = SCREEN_HEIGHT

    def update(self, action):
        if action not in [0, 1, 2, 3, 4]:
            raise ValueError("action {} not in action space".format(action))
            
        if action == 1:
            self.rect.move_ip(0, -7)
        if action == 2:
            self.rect.move_ip(0, 7)
        if action == 3:
            self.rect.move_ip(-7, 0)
        if action == 4:
            self.rect.move_ip(7, 0)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def get_position(self):
        return [self.rect.left, self.rect.top]


# Define the enemy object
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        #speed and position
        y_coordinate = random.randint(0, SCREEN_HEIGHT)
        x_coordinate = random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 400)
        self.rect = self.surf.get_rect(
            center=(
                x_coordinate,
                y_coordinate,
            )
        )
        # missilespeed
        self.speed = random.randint(5, 25)
        #positions
        # print(self.rect.left)
        # print(self.rect.top)
        # print (self.rect)

    # Move the enemy based on speed
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()

    def get_position(self):
        return [self.rect.left, self.rect.top]

# Define the cloud object
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        self.surf = pygame.image.load("cloud.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        # The starting position is randomly generated
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 450),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    # Move the cloud based on a constant speed
    # Remove it when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-5, 0)
        if self.rect.right < 0:
            self.kill()

if __name__ == "__main__":
    # Initialize pygame
    pygame.init()

    # Clock for framerate
    clock = pygame.time.Clock()

    # screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Create custom events for adding a new enemy and cloud
    ADDENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDENEMY, 2000)
    ADDCLOUD = pygame.USEREVENT + 2
    pygame.time.set_timer(ADDCLOUD, 1100)

    # Create our 'player'
    player = Player()

    # Create groups to hold enemy sprites, cloud sprites, and all sprites
    enemies = pygame.sprite.Group()
    clouds = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    #Variables
    running = True
    score = 0

    # Our main loop
    while running:
        # Look at every event in the queue
        for event in pygame.event.get():
            # Did the user hit a key?
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop the loop
                if event.key == K_ESCAPE:
                    running = False

            # Did the user click the window close button? If so, stop the loop
            elif event.type == QUIT:
                running = False

            # Should we add a new enemy?
            elif event.type == ADDENEMY:
                # Create the new enemy, and add it to our sprite groups
                new_enemy = Enemy()
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)

            # Should we add a new cloud?
            elif event.type == ADDCLOUD:
                # Create the new cloud, and add it to our sprite groups
                new_cloud = Cloud()
                clouds.add(new_cloud)
                all_sprites.add(new_cloud)

        # Get the set of keys pressed and check for user input
        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)

        # Update the position of our enemies and clouds
        enemies.update()
        clouds.update()

        # background colour
        screen.fill((135, 206, 235))

        # Draw all our sprites
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        # Check if any enemies have collided with the player
        if pygame.sprite.spritecollideany(player, enemies):
            # If so, remove the player
            player.kill()
            running = False
        score += 1
        scoreboard(screen, str(score), 20, SCREEN_WIDTH/2, 10)
        # Flip everything to the display
        pygame.display.flip()

        # Ensure we maintain a 30 frames pe second rate
        clock.tick(30)

    scoreboard(screen, str(score), 50, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
    pygame.display.flip()

pygame.quit()
