import pygame
import random
import math

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()
fps = 120


WINDOWS_WIDTH = 1000
WINDOWS_HEIGHT = 600
MONSTER = 64
ROCKET_X = (WINDOWS_WIDTH // 2) - 20
ROCKET_Y = WINDOWS_HEIGHT - 100
ROCKET_Y_CHANGE = 0
BULLET_X = ROCKET_X
BULLET_Y = ROCKET_Y
BULLET_Y_CHANGE = -6
BULLET_STATE = "ready"
# Number of monsters you want
num_monsters = 6
MONSTER_CHANGE_X = [1.8] * num_monsters
MONSTER_CHANGE_Y = [20] * num_monsters
bgImg = []
monster_positions_collision = []
monster_positions = []
bg_cord = [(60, 160), (150, 350), (750, 390), (810, 50), (550, 189)]

# Create a Pygame window
screen = pygame.display.set_mode((WINDOWS_WIDTH, WINDOWS_HEIGHT))

# Set title, logo
pygame.display.set_caption("Space Invader")
icon = pygame.image.load("./assests/icon.png")
pygame.display.set_icon(icon)


# Load Rocket and Bullet
rocketImg = pygame.image.load("./assests/spaceship.png")
bulletImg = pygame.image.load("./assests/bullet.png")
bGImg = pygame.image.load("./assests/bg.png")
monster_image = pygame.image.load("./assests/monster.png")

for i in range(1, 6):
    image = pygame.image.load(f"./assests/bg_{i}.png")
    image.set_alpha(190)
    bgImg.append(image)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"./assests/exp{num}.png")
            img = pygame.transform.scale(img, (100, 100))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 6
        # update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # if the animation is complete, reset animation index
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()


explosion_group = pygame.sprite.Group()


def generate_random_position(img):
    while True:
        x = random.randint(10, WINDOWS_WIDTH - img.get_width())
        y = random.randint(10, 150 - img.get_height())
        rect = pygame.Rect(x, y, img.get_width(), img.get_height())
        overlap = any(
            rect.colliderect(existing_rect)
            for existing_rect in monster_positions_collision
        )
        if not overlap:
            return rect, x, y


for _ in range(num_monsters):
    rect, x, y = generate_random_position(monster_image)
    monster_positions_collision.append(rect)
    monster_positions.append([x, y])

score_value = 0
font = pygame.font.Font("freesansbold.ttf", 32)

textX = 5
testY = 5

# Game Over
over_font = pygame.font.Font("freesansbold.ttf", 64)


def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (WINDOWS_WIDTH // 2 - 200, WINDOWS_HEIGHT // 2))


def render_asset(img, cor):
    screen.blit(img, cor)


def isCollision(enemy_cor=None, bullet_cor=None):
    enemy_X, enemy_Y = enemy_cor
    bullet_X, bullet_y = bullet_cor
    distance = math.sqrt(
        math.pow((enemy_X - bullet_X), 2) + math.pow((enemy_Y - bullet_y), 2)
    )
    if distance < 30:
        return True

    return False


running = True
while running:
    clock.tick(fps)
    screen.blit(bGImg, (0, 0))
    # Background Image
    for j in range(len(bgImg)):
        render_asset(bgImg[j], bg_cord[j])

    # KeyStroke Detection for Movement
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Fix the event type comparison
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                ROCKET_Y_CHANGE = -4.5
            if event.key == pygame.K_RIGHT:
                ROCKET_Y_CHANGE = 4.5
            if event.key == pygame.K_SPACE:
                if BULLET_STATE == "ready":
                    BULLET_X = ROCKET_X
                    BULLET_STATE = "fire"
        if event.type == pygame.KEYUP:
            ROCKET_Y_CHANGE = 0

    # Rocket position change
    ROCKET_X += ROCKET_Y_CHANGE
    if ROCKET_X < 0:
        ROCKET_X = 1
    if ROCKET_X >= (WINDOWS_WIDTH - 64):
        ROCKET_X = WINDOWS_WIDTH - 65

    # Bullet position change
    if BULLET_Y <= 0:
        BULLET_STATE = "ready"
        BULLET_Y = ROCKET_Y
    if BULLET_STATE == "fire":
        render_asset(bulletImg, (BULLET_X + 16, BULLET_Y - 20))
        BULLET_Y += BULLET_Y_CHANGE

    # Monster position
    for i in range(num_monsters):
        enemyX, enemyY = monster_positions[i]
        if enemyY >= (ROCKET_Y - monster_image.get_height()):
            for j in range(num_monsters):
                monster_positions[j] = (2000, 2000)
            game_over_text()
            break
        enemyX += MONSTER_CHANGE_X[i]
        if enemyX <= 0:
            MONSTER_CHANGE_X[i] = 1.8
            enemyY += MONSTER_CHANGE_Y[i]
        if enemyX >= WINDOWS_WIDTH - 64:
            MONSTER_CHANGE_X[i] = -1.8
            enemyY += MONSTER_CHANGE_Y[i]
        collision = isCollision((enemyX, enemyY), (BULLET_X, BULLET_Y))
        if collision:
            explosion = Explosion(enemyX, enemyY+monster_image.get_height()//2)
            explosion_group.add(explosion)
            BULLET_STATE = "ready"
            BULLET_Y = 500
            score_value += 1
            rect, enemyX, enemyY = generate_random_position(monster_image)
            monster_positions_collision[i] = rect
        monster_positions[i][0] = enemyX
        monster_positions[i][1] = enemyY
        render_asset(monster_image, (monster_positions[i][0], monster_positions[i][1]))
    explosion_group.draw(screen)
    explosion_group.update()
    render_asset(rocketImg, (ROCKET_X, ROCKET_Y))
    show_score(textX, testY)
    pygame.display.update()


# # Quit Pygame properly when you're done
# pygame.quit()
