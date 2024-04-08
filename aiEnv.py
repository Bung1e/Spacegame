import pygame
import random
import os
import asyncio

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Infinite Galactic Shooter")

# Load images
player_image = pygame.image.load(os.path.join("images", "rocket-ship.png")).convert_alpha()
player_image = pygame.transform.scale(player_image, (50, 50))

alien_image = pygame.image.load(os.path.join("images", "space-invaders.png")).convert_alpha()
alien_image = pygame.transform.scale(alien_image, (30, 30))

life_image = pygame.image.load(os.path.join("images", "heart.png")).convert_alpha()
life_image = pygame.transform.scale(life_image, (25, 25))


pygame.mixer.init()




# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -5
        if keys[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x
        self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x))

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# Bullet class
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

# Sprite groups
all_sprites = pygame.sprite.Group()
aliens = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

score = 0
lives = 3


font = pygame.font.Font(None, 30)
font2 = pygame.font.Font(None, 24)

def reset():
    global lives, score, game_over, all_sprites, aliens, bullets, player
    score = 0
    lives = 3
    game_over = False

    for sprite in all_sprites:
        sprite.kill()
    for alien in aliens:
        alien.kill()
    for bullet in bullets:
        bullet.kill()

    all_sprites = pygame.sprite.Group()
    aliens = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)


def load_highscore():
    try:
        with open("highscore.txt", "r") as file:
            return int(file.readline())
    except FileNotFoundError:
        return 0

def save_highscore(score):
    with open("highscore.txt", "w") as file:
        file.write(str(score))

    # ! Main game loop
async def main():
    global lives, score
    running = True
    clock = pygame.time.Clock()

    game_over = False

    highscore = load_highscore()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        if game_over:
            screen.fill(BLACK)
            game_over_text = font.render("Game Over.", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 100))
            score_text = font.render(f"Your Score: {score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 50))
            highscore_text = font.render(f"Highscore: {highscore}", True, WHITE)
            screen.blit(highscore_text, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 ))
            

            exit_button = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH/2 - 50, 400, 100, 50))

            exit_text = font.render("Exit", True, BLACK)
            screen.blit(exit_text, (SCREEN_WIDTH/2 - 25, 415))
            
            highscore_text = font.render(f"Refresh the Page", True, WHITE)
            screen.blit(highscore_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100 ))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if exit_button.collidepoint(mouse_pos):
                        running = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.shoot()

            # ! Update
            all_sprites.update()

            # Check for collisions between bullets and aliens
            hits = pygame.sprite.groupcollide(bullets, aliens, True, True)

            # Check if a alien is destroyed and increase score
            if len(hits) > 0:
                score += 1
        
            # Check if player gets an extra life from destroying aliens
            if len(hits) > 0 and random.random() < 0.05:  # 5% chance
                lives += 1

            # Check if aliens reach the bottom
            for alien in aliens:
                if alien.rect.top > SCREEN_HEIGHT - 10:
                    lives -= 1
                    alien.kill()

            # Check for collisions between player and aliens
            hits_player = pygame.sprite.spritecollide(player, aliens, True)
            if hits_player:
                lives -= 1

            # Spawn new aliens
            if len(aliens) < 5 and random.random() < 0.02:
                new_alien = Alien()
                all_sprites.add(new_alien)
                aliens.add(new_alien)

            # Draw
            screen.fill(BLACK)
            all_sprites.draw(screen)

            # Draw score and lives
            score_text = font.render(f"HI-Score: {highscore}", True, WHITE)
            screen.blit(score_text, (10, 10))
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 50))
            life_text = font.render(f"Lives: ", True, WHITE)
            screen.blit(life_text, (10, 90))
            
            move_controls = font2.render(f"Movement: Arrow Keys", True, WHITE)
            screen.blit(move_controls, (610, 10))
            shoot_control = font2.render(f"Shoot: SpaceBar", True, WHITE)
            screen.blit(shoot_control, (610, 30))

            # Draw life icons
            for i in range(lives):
                screen.blit(life_image, (85 + i * 40, 85))

            pygame.display.flip()
            clock.tick(60)

            # Game over condition
            if lives <= 0:
                game_over = True
                if score > highscore:
                    highscore = score
                    save_highscore(highscore)
        await asyncio.sleep(0)
    
# Run the main function
asyncio.run(main())

# Quit Pygame
pygame.quit()