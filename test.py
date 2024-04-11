import pygame
import random
import os
from enum import Enum

pygame.init()
font = pygame.font.Font(None, 25)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Infinite Galactic Shooter")

player_image = pygame.image.load(os.path.join("images", "rocket-ship.png")).convert_alpha()
player_image = pygame.transform.scale(player_image, (50, 50))

alien_image = pygame.image.load(os.path.join("images", "space-invaders.png")).convert_alpha()
alien_image = pygame.transform.scale(alien_image, (30, 30))

life_image = pygame.image.load(os.path.join("images", "heart.png")).convert_alpha()
life_image = pygame.transform.scale(life_image, (25, 25))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0

    def update(self):
        # self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -5
        if keys[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x
        self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x))

    def shoot(self, bullets, all_sprites):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((3, 15))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# Alien class
class Alien(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = alien_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(1, 4)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 4) 

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    SHOOT = 2
    DO_NOTHING = 3

class GalacticShooterAI:
    def __init__(self):
        self.display = screen 
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.player = Player()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.aliens = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.place_alien()

    def place_alien(self):
        alien = Alien()
        self.all_sprites.add(alien)
        self.aliens.add(alien)

    def play_step(self, action):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        self.move(action)
        self.all_sprites.update()

        reward = 0
        game_over = False
        if self.is_collision():
            game_over = True
            reward = -10
            return reward, game_over, self.score

        hits = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        for hit in hits:
            self.score += 1
            reward = 10
            self.place_alien()
            
        if len(self.aliens) < 3 and random.random() < 0.02:
            self.place_alien()

        self.update_ui()
        self.clock.tick(60)
        return reward, game_over, self.score

    def is_collision(self):
        if pygame.sprite.spritecollide(self.player, self.aliens, False):
            self.lives -= 1
            if self.lives <= 0:
                return True
        return False

    def update_ui(self):
        self.display.fill(BLACK)
        self.all_sprites.draw(self.display)

        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.display.blit(score_text, (10, 10))

        for i in range(self.lives):
            self.display.blit(life_image, (85 + i * 40, 85))

        pygame.display.flip()

    def move(self, action):
        if action == Direction.LEFT:
            self.player.speed_x = -5
        elif action == Direction.RIGHT:
            self.player.speed_x = 5
        elif action == Direction.SHOOT:
            self.player.shoot(self.bullets, self.all_sprites)
        elif action == Direction.DO_NOTHING:
            self.player.speed_x = 0

if __name__ == "__main__":
    game = GalacticShooterAI()
    while True:
        action = random.choice(list(Direction))
        game.play_step(action)
