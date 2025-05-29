import pygame
import random
import os

# GameObject class definition
class GameObject:
    def __init__(self, x, y, image_path):
        self.x = x  # X position of the object
        self.y = y  # Y position of the object
        self.image = pygame.image.load(image_path)  # Load object image
        self.rect = self.image.get_rect()  # Get the rectangular area of the image
        self.rect.topleft = (self.x, self.y)  # Set the initial position of the object

    def draw(self, screen):
        # Draw the object on the screen at its current position
        screen.blit(self.image, self.rect.topleft)

    def move(self, dx, dy):
        # Move the object by changing its x and y coordinates
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)  # Update the position of the object

    def add_boundaries(self, min_x, min_y, max_x, max_y):
        if self.x <= min_x: self.x = min_x
        if self.y <= min_y: self.y = min_y
        if self.x >= max_x: self.x = max_x
        if self.y >= max_y: self.y = max_y
        self.rect.topleft = (self.x, self.y)

# Player class inheriting from GameObject
class Player(GameObject):
    def __init__(self, x, y, image_path, speed_factor, hp = 100, power = 20):
        super().__init__(x, y, image_path)  # Inherit GameObject properties
        self.speed_factor = speed_factor  # Multiplier to adjust speed
        self.x_speed = 0
        self.y_speed = 0
        self.score = 0
        self.hp = hp
        self.power = power
        self.bullets = []  # List to store bullets

    def handle_input(self, event):
        # Handle keydown and keyup events for player movement
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.x_speed = self.speed_factor
            elif event.key == pygame.K_LEFT:
                self.x_speed = -self.speed_factor
            elif event.key == pygame.K_DOWN:
                self.y_speed = self.speed_factor
            elif event.key == pygame.K_UP:
                self.y_speed = -self.speed_factor
            elif event.key == pygame.K_SPACE:
                # Fire a bullet when space is pressed
                self.fire_bullet()

        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_RIGHT, pygame.K_LEFT]:
                self.x_speed = 0
            if event.key in [pygame.K_UP, pygame.K_DOWN]:
                self.y_speed = 0

    def update(self):
        # Update player position
        if self.x <= 5 and self.x_speed < 0: self.x_speed = 0
        if self.x >= 730 and self.x_speed > 0: self.x_speed = 0
        if self.y <= 5 and self.y_speed < 0: self.y_speed = 0
        if self.y >= 530 and self.y_speed > 0: self.y_speed = 0
        self.move(self.x_speed, self.y_speed)

    def fire_bullet(self):
        # Create a bullet at the current player position
        bullet = Bullet(self.x + self.rect.width // 2 - 5, self.y, "assets/images/playerBullet.png")
        self.bullets.append(bullet)

    def draw_hp(self, screen):
        font = pygame.font.Font(None, 36)
        hp_text = font.render(f"HP: {self.hp}", True, (230, 30, 30))
        screen.blit(hp_text, (700, 10))

    def draw_score(self, screen):
        font = pygame.font.Font(None, 24)
        score_text = font.render(f"Score: {self.score}", True, (30, 30, 230))
        screen.blit(score_text, (65, 30))

# Bullet class to handle bullet behavior
class Bullet(GameObject):
    def __init__(self, x, y, image_path, speed = 10, direction='up'):
        super().__init__(x, y, image_path)
        self.speed = speed
        self.direction = direction

        # Rotate the bullet image if direction is down (enemy bullet)
        if self.direction == 'down':
            self.image = pygame.transform.rotate(self.image, 180)

    def update(self):
        # Move the bullet upwards or downwards based on direction
        if self.direction == 'up':
            self.move(0, -self.speed)
        elif self.direction == 'down':
            self.move(0, self.speed)

    def is_off_screen(self):
        # Check if the bullet has moved off the screen
        return self.y < 0 or self.y > 600

# Enemy class with firing ability
class Enemy(GameObject):
    def __init__(self, x, y, image_path, x_speed, y_speed, health, damage = 5):
        super().__init__(x, y, image_path)
        self.image = pygame.transform.rotate(self.image, 180)
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.health = health
        self.max_health = health
        self.is_dead = False
        self.damage = damage
        self.small_explosion = None  # To store small explosion image
        self.explosion_timer = 0  # Timer to track small explosion duration
        self.death_timer = 0  # Timer to track big explosion duration
        self.bullets = []  # Store enemy bullets
        self.fire_cooldown = random.randint(60, 120)  # Random firing cooldown
        self.is_off_screen = False  # New property

    def update(self):
        if not self.is_dead:
            # Move enemy and bounce off edges
            self.move(self.x_speed, self.y_speed)
            if self.x <= 0 or self.x >= 736:
                self.x_speed *= -1  # Reverse direction when hitting boundaries

            # Check if out of bounds (below screen)
            if self.y >= 650 or self.is_dead:
                self.is_off_screen = True

            # Fire bullets periodically
            if self.fire_cooldown <= 0:
                self.fire_bullet()
                self.fire_cooldown = random.randint(60, 120)  # Reset firing cooldown
            else:
                self.fire_cooldown -= 1
        else:
            self.x_speed = 0
            self.y_speed = 0
            if self.death_timer > 0:
                self.death_timer -= 1
            else:
                self.image = None
                self.is_off_screen = True

    def fire_bullet(self):
        # Create a bullet that moves downwards
        bullet = Bullet(self.x + self.rect.width // 2 - 5, self.y + self.rect.height, "assets/images/playerBullet.png", speed=7, direction='down')
        self.bullets.append(bullet)

    def take_damage(self, damage, small_explosion_image):
        if not self.is_dead:
            self.health -= damage
            self.small_explosion = small_explosion_image
            self.explosion_timer = 30
            if self.health <= 0:
                self.health = 0
                self.is_dead = True
                self.image = pygame.image.load("assets/images/bigExplosion.png")
                self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
                self.death_timer = 60

    def draw_health_bar(self, screen):
        if not self.is_dead:
            bar_width = 50
            bar_height = 5
            fill_width = int(bar_width * (self.health / self.max_health))
            pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, fill_width, bar_height))
            pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y - 10, bar_width, bar_height), 1)

    def draw_explosion(self, screen):
        if self.small_explosion and self.explosion_timer > 0:
            screen.blit(self.small_explosion, (self.x + self.rect.width // 2 - 16, self.y))
            self.explosion_timer -= 1
        if self.image and self.is_dead and self.death_timer > 0:
            screen.blit(self.image, (self.x, self.y))

class Landmine(GameObject):
    def __init__(self, x, y, image_path):
        super().__init__(x, y, image_path)
        self.exploded = False
        self.explosion_image = pygame.image.load("assets/images/bigExplosion.png")
        self.explosion_timer = 0  # Timer to track explosion duration
        self.speed = 1  # Speed for moving downwards

        # Increase the size of the landmine
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()  # Update the rect with the new size
        self.rect.topleft = (self.x, self.y)  # Set the initial position of the landmine

    def update(self):
        if not self.exploded:
            # Move downwards
            self.move(0, self.speed)

        if self.exploded:
            if self.explosion_timer > 0:
                self.explosion_timer -= 1
            else:
                self.image = None  # Remove landmine after explosion

    def draw(self, screen):
        if self.image is not None:  # Only draw if the image is valid
            screen.blit(self.image, self.rect.topleft)
        if self.exploded and self.explosion_timer > 0:  # Draw explosion if exploded and timer active
            self.draw_explosion(screen)

    def draw_explosion(self, screen):
        # Draw the explosion at the landmine’s position
        screen.blit(self.explosion_image, (self.x, self.y+20))

class BossEnemy(Enemy):
    def __init__(self, x, y, image_path, x_speed, health, damage=20):
        super().__init__(x, y, image_path, x_speed, 0, health, damage)
        self.fire_cooldown = random.randint(20, 40)  # Boss fires more frequently
        self.direction = 1  # 1 for right, -1 for left

    def update(self):
        if not self.is_dead:
            # Boss moves side-to-side only
            self.move(self.direction * self.x_speed, 0)

            # Reverse direction when hitting the edges of the screen
            if self.x <= 0 or self.x >= 736:
                self.direction *= -1

            # Fire bullets frequently
            if self.fire_cooldown <= 0:
                self.fire_bullet()
                self.fire_cooldown = random.randint(60, 120)  # Faster firing rate for boss
            else:
                self.fire_cooldown -= 1
        else:
            # Same explosion behavior as the regular enemy
            super().update()

    def fire_bullet(self):
        # Create a bullet that moves downwards faster than regular enemies
        bullet = Bullet(self.x + self.rect.width // 2 - 5, self.y + self.rect.height, "assets/images/atomic-bomb.png", speed=10, direction='down')
        self.bullets.append(bullet)


def newEnemy():
    return Enemy(x=random.randint(0, 736), y=random.randint(-200, -50), image_path="assets/images/enemyTank.png", x_speed=1,
          y_speed=0.5, health=100)

def newLandmine():
    return Landmine(x=random.randint(0, 736), y=random.randint(-200, -50), image_path="assets/images/mine.png")

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Tank Game")

# Load images
background = pygame.image.load("assets/images/top-view-city-with-desert_70347-2005.jpg")
small_explosion_image = pygame.image.load("assets/images/smallExplosion.png")
small_explosion_image = pygame.transform.scale(small_explosion_image, (32, 32))
mine_image = pygame.image.load("assets/images/mine.png")  # Load landmine image
clock = pygame.time.Clock()

# game first home page
is_home = True
game_over = True
is_running = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    # Create player object
    greenPlayer = Player(x=380, y=500, image_path="assets/images/playerTank.png", speed_factor=3, hp=200, power=20)
    bluePlayer = Player(x=380, y=500, image_path="assets/images/Player2tank.png", speed_factor=3, hp=100, power=40)
    player = greenPlayer

    # Create 5 enemy tanks for level 1
    enemies = [
        newEnemy()
        for _ in range(5)
    ]

    # Create land mines for level 2 (you can adjust the count as needed)
    landmines = [
        newLandmine()
        for _ in range(5)
    ]

    mineDamage = 10
    # File to store high score
    high_score_file = "assets/files/high_score.txt"

    # Function to read the high score from the files
    def read_high_score():
        if os.path.exists(high_score_file):
            with open(high_score_file, 'r') as file:
                try:
                    return int(file.read().strip())
                except ValueError:
                    return 0  # If files is empty or invalid, set high score to 0
        return 0

    # Function to reset the high score in the files
    def reset_high_score():
        with open(high_score_file, 'w') as file:
            file.write("0")
        return 0

    high_score = read_high_score() # read from a file
    font = pygame.font.Font(None, 36)  # Font for text

    # Flags for box clicks
    blue_box_clicked = False
    green_box_clicked = True

    while is_home:
        game_over = True
        is_running = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Check if Play button is clicked
                if play_button_rect.collidepoint(mouse_pos):
                    is_home = False  # Break the loop to start the game

                # Check if Reset button is clicked
                if reset_button_rect.collidepoint(mouse_pos):
                    high_score = reset_high_score()  # Reset the high score

                # Check if blue box is clicked
                if blue_box_rect.collidepoint(mouse_pos):
                    blue_box_clicked = True
                    green_box_clicked = False  # Unselect the green box if blue box is clicked
                    player = bluePlayer

                # Check if green box is clicked
                if green_box_rect.collidepoint(mouse_pos):
                    green_box_clicked = True
                    blue_box_clicked = False  # Unselect the blue box if green box is clicked
                    player = greenPlayer

        # Render the background
        screen.blit(pygame.image.load("assets/images/top-view-countryside_70347-2007.jpg"), (0, 0))

        # Display the high score
        high_score_text = pygame.font.Font(None, 64).render(f"High Score: {high_score}", True, (200, 50, 50))
        screen.blit(high_score_text, (250, 120))

        # Draw Play button
        play_button_rect = pygame.Rect(320, 200, 160, 50)
        pygame.draw.rect(screen, (0, 180, 100), play_button_rect)  # Green button for Play
        play_text = font.render("Play", True, (0, 0, 0))  # Black text
        screen.blit(play_text, (play_button_rect.x + 50, play_button_rect.y + 10))

        # Draw Reset High Score button
        reset_button_rect = pygame.Rect(320, 270, 160, 50)
        pygame.draw.rect(screen, (0, 180, 100), reset_button_rect)  # Red button for Reset
        reset_text = font.render("Reset", True, (0, 0, 0))  # Black text
        screen.blit(reset_text, (reset_button_rect.x + 50, reset_button_rect.y + 10))

        # Draw blue box for Power
        blue_box_rect = pygame.Rect(100, 350, 150, 150)
        pygame.draw.rect(screen, (0, 100, 220), blue_box_rect)  # Blue color
        power_text = font.render("Power", True, (0, 0, 0))  # Black text
        screen.blit(power_text, (blue_box_rect.x + 37, blue_box_rect.y + 10))

        # Draw green box for Defence
        green_box_rect = pygame.Rect(550, 350, 150, 150)
        pygame.draw.rect(screen, (0, 255, 100), green_box_rect)  # Green color
        defence_text = font.render("Defence", True, (0, 0, 0))  # Black text
        screen.blit(defence_text, (green_box_rect.x + 27, green_box_rect.y + 10))

        # Draw red border around the clicked box
        if blue_box_clicked:
            pygame.draw.rect(screen, (255, 0, 0), blue_box_rect, 5)  # Red border around blue box
        if green_box_clicked:
            pygame.draw.rect(screen, (255, 0, 0), green_box_rect, 5)  # Red border around green box

        # Load and center images in boxes
        power_image = pygame.image.load("assets/images/Player2tank.png")
        defence_image = pygame.image.load("assets/images/playerTank.png")
        screen.blit(power_image, (blue_box_rect.x + (blue_box_rect.width - power_image.get_width()) // 2,
                                  blue_box_rect.y + (blue_box_rect.height - power_image.get_height()) // 2))
        screen.blit(defence_image, (green_box_rect.x + (green_box_rect.width - defence_image.get_width()) // 2,
                                    green_box_rect.y + (green_box_rect.height - defence_image.get_height()) // 2))

        pygame.display.update()

    # when boss appare
    boss_coming = 40
    boss = BossEnemy(300, 50, "assets/images/jet-plane.png", x_speed=1.5, health=1000)
    # Game loop
    while is_running:
        is_home = True
        game_over = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            player.handle_input(event)

        screen.blit(background, (0, 0))
        # Update player position
        player.update()
        if boss_coming <= 0:
            boss.update()

            for bullet in boss.bullets:
                bullet.update()
                # Check if enemy bullets hit the player
                if bullet.rect.colliderect(player.rect):
                    player.hp -= boss.damage
                    if player.hp <= 0:
                        is_running = False  # End the game if HP is zero
                    boss.bullets.remove(bullet)
                if bullet.is_off_screen():
                    boss.bullets.remove(bullet)

        alive = 0
        # Update enemies and their bullets
        for enemy in enemies:
            enemy.update()
            for bullet in enemy.bullets:
                bullet.update()

                # Check if enemy bullets hit the player
                if bullet.rect.colliderect(player.rect):
                    player.hp -= enemy.damage  # Reduce player HP by 5
                    if player.hp <= 0:
                        is_running = False  # End the game if HP is zero
                    enemy.bullets.remove(bullet)

                # Remove bullets that are off-screen
                if bullet.is_off_screen():
                    enemy.bullets.remove(bullet)

                if enemy.is_dead:
                    player.score += 10

                # If the enemy goes out of bounds or is dead
                if enemy.is_off_screen or enemy.is_dead:
                    if enemies.count(enemy): enemies.remove(enemy)
                    enemies.append(newEnemy())
                    enemies.append(newEnemy())
                    player.score += 1
                    boss_coming -= 1

            if not enemy.is_dead: alive += 1

        if alive < 5 and boss_coming > 0:
            for i in range(0, 5 - alive):
                enemies.append(newEnemy())
            alive = 5

        # Update landmines
        for landmine in landmines:
            landmine.update()

            if (landmine.exploded and landmine.explosion_timer <= 0) or landmine.y > 650:
                landmines.append(newLandmine())
                landmines.remove(landmine)
                player.score += 1
                if random.randint(1, 20) % 17 == 0:
                    landmines.append(newLandmine())

            # Check for collision with player
            if not landmine.exploded and landmine.rect.colliderect(player.rect):
                landmine.exploded = True
                landmine.explosion_timer = 30
                player.hp -= mineDamage

        # Update and draw player bullets
        for bullet in player.bullets:
            bullet.update()

            # Check for collision with any enemy
            for enemy in enemies:
                if bullet.rect.colliderect(enemy.rect) and not enemy.is_dead:
                    enemy.take_damage(player.power, small_explosion_image)
                    if player.bullets.count(bullet) : player.bullets.remove(bullet)

            if boss.rect.colliderect(bullet.rect) and not boss.is_dead:
                boss.take_damage(player.power, small_explosion_image)  # Apply 10 damage when hit
                if player.bullets.count(bullet) : player.bullets.remove(bullet)

            # Remove bullets that are off-screen
            if bullet.is_off_screen():
                if player.bullets.count(bullet) != 0:
                    player.bullets.remove(bullet)

        # Draw background, player, enemies, bullets, health bars, explosions, and land mines
        player.draw(screen)
        player.draw_hp(screen)
        player.draw_score(screen)
        if boss_coming <= 0:
            enemies.clear()
            boss.update()
            boss.draw(screen)
            boss.draw_health_bar(screen)  # Optional: Draw a health bar for the boss

            # Draw explosions if the boss takes damage
            boss.draw_explosion(screen)

            for bullet in boss.bullets:
                bullet.draw(screen)

        for enemy in enemies:
            if enemy.image:
                enemy.draw(screen)
            for bullet in enemy.bullets:
                bullet.draw(screen)
            enemy.draw_health_bar(screen)
            enemy.draw_explosion(screen)
        for bullet in player.bullets:
            bullet.draw(screen)
        for landmine in landmines:
            landmine.update()
            landmine.draw(screen)
            if not landmine.exploded and landmine.rect.colliderect(player.rect):
                landmine.exploded = True
                landmine.explosion_timer = 30

        if boss.is_dead and boss.death_timer == 0:
            player.score += 1000

        # Ending the game
        if player.hp <= 0 or (boss.is_dead and boss.death_timer <= 0):
            # Trigger level end or move to next stage
            print("Boss defeated!")
            is_running = False

        # Update the display
        pygame.display.update()

        # Cap the frame rate at 60 FPS
        clock.tick(60)

    while game_over:
        is_home = True
        is_running = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Check if Home button is clicked
                if home_button_rect.collidepoint(mouse_pos):
                    is_home = True
                    game_over = False

            # Clear the screen
        screen.fill((0, 0, 0))  # Black background

        # Display "Game Over" text
        game_over_text = pygame.font.Font(None, 64).render("GAME OVER", True, (255, 0, 0))  # Red text
        screen.blit(game_over_text, (260, 120))

        if high_score <= player.score:
            high_score_label = pygame.font.Font(None, 36).render(f"Wow you scored highest", True, (255, 255, 100))
            screen.blit(high_score_label, (260, 250))

        if high_score < player.score:
            high_score = player.score
            with open("assets/files/high_score.txt", "w") as file:
                file.write(str(high_score))


        # draw score
        score = pygame.font.Font(None, 48).render(f"Your Score: {player.score}", True, (200, 50, 50))
        screen.blit(score, (280, 300))

        # Draw Home button
        home_button_rect = pygame.Rect(320, 370, 160, 50)
        pygame.draw.rect(screen, (180, 0, 0), home_button_rect)  # Red button for Home
        home_text = font.render("Home", True, (0, 0, 0))  # Black text
        screen.blit(home_text, (home_button_rect.x + 45, home_button_rect.y + 10))

        pygame.display.update()
