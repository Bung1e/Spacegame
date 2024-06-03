import pygame
import random
import os
import numpy as np
import cv2
from enum import Enum
import gym
from gym import spaces

# Параметры игры
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Инициализация Pygame
pygame.init()
font = pygame.font.Font(None, 25)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Infinite Galactic Shooter")

# Загрузка изображений
player_image = pygame.image.load(os.path.join("images", "rocket-ship.png")).convert_alpha()
player_image = pygame.transform.scale(player_image, (50, 50))
alien_image = pygame.image.load(os.path.join("images", "space-invaders.png")).convert_alpha()
alien_image = pygame.transform.scale(alien_image, (40, 40))

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    SHOOT = 2
    DO_NOTHING = 3

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0

    def update(self):
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
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

class Alien(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = alien_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(1, 2)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 2)

class GalacticShooterEnv(gym.Env):
    def __init__(self):
        super(GalacticShooterEnv, self).__init__()
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=255, shape=(84, 84, 1), dtype=np.uint8)
        self.reset()

    def reset(self):
        self.player = Player()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.aliens = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.score = 0
        self.lives = 3
        self.steps_survived = 0
        self.game_over = False
        self.place_alien()
        return self._get_obs()

    def place_alien(self):
        alien = Alien()
        self.all_sprites.add(alien)
        self.aliens.add(alien)

    def _get_obs(self):
        raw_pixels = pygame.surfarray.array3d(pygame.display.get_surface())
        raw_pixels = np.transpose(raw_pixels, (1, 0, 2))
        gray_pixels = cv2.cvtColor(raw_pixels, cv2.COLOR_RGB2GRAY)
        gray_pixels = cv2.resize(gray_pixels, (84, 84), interpolation=cv2.INTER_AREA)
        obs = np.expand_dims(gray_pixels, axis=-1)
        return obs

    def step(self, action):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self.move(action)
        self.all_sprites.update()

        reward = 0
        self.steps_survived += 1
        reward += 0.0001  # Награда за выживание

        if self.is_collision():
            self.lives -= 1
            reward -= 1
            if self.lives <= 0:
                self.game_over = True
                return self._get_obs(), reward, self.game_over, {}

        for alien in self.aliens:
            if self.lives <= 0:
                self.game_over = True
            if alien.rect.top > SCREEN_HEIGHT:
                reward -= 1
                self.lives -= 1
                alien.kill()
                

        hits = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        for hit in hits:
            self.score += 1
            reward += 1
            self.place_alien()

        if len(self.aliens) < 2 and random.random() < 0.02:
            self.place_alien()

        obs = self._get_obs()
        done = self.game_over
        self.render()
        return obs, reward, done, {}

    def is_collision(self):
        if pygame.sprite.spritecollide(self.player, self.aliens, False):
            return True
        return False

    def render(self, mode='human'):
        screen.fill(BLACK)
        self.all_sprites.draw(screen)
        pygame.display.flip()

    def move(self, action):
        if action == Direction.LEFT.value:
            self.player.speed_x = -5
        elif action == Direction.RIGHT.value:
            self.player.speed_x = 5
        elif action == Direction.SHOOT.value:
            self.player.shoot(self.bullets, self.all_sprites)
        elif action == Direction.DO_NOTHING.value:
            self.player.speed_x = 0

    def close(self):
        pygame.quit()
