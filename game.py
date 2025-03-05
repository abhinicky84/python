import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
FRICTION = 0.99  # Friction on walls
RADIUS = 15
HEX_SIZE = 200
HEX_CENTER = (WIDTH // 2, HEIGHT // 2)
HEX_ROTATION_SPEED = 0.5  # Degrees per frame

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BALL_COLOR = (255, 0, 0)
HEX_COLOR = (0, 255, 0)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in Spinning Hexagon")

# Ball class
class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity_x = 0
        self.velocity_y = 0
        self.color = BALL_COLOR

    def apply_gravity(self):
        self.velocity_y += GRAVITY

    def move(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

    def apply_friction(self):
        self.velocity_x *= FRICTION
        self.velocity_y *= FRICTION

# Hexagon class
class Hexagon:
    def __init__(self, center, size):
        self.center = center
        self.size = size
        self.rotation = 0

    def draw(self, screen):
        points = []
        for i in range(6):
            angle = math.radians(self.rotation + 60 * i)
            x = self.center[0] + self.size * math.cos(angle)
            y = self.center[1] + self.size * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(screen, HEX_COLOR, points)

    def rotate(self):
        self.rotation += HEX_ROTATION_SPEED

    def get_wall_normal(self, angle):
        """Returns a normal vector for a hexagonal wall at a given angle."""
        wall_angle = math.radians(self.rotation + angle)
        return (math.cos(wall_angle), math.sin(wall_angle))

    def check_collision(self, ball):
        for i in range(6):
            angle = 60 * i
            normal = self.get_wall_normal(angle)
            wall_x = self.center[0] + self.size * math.cos(math.radians(self.rotation + angle))
            wall_y = self.center[1] + self.size * math.sin(math.radians(self.rotation + angle))

            dx = ball.x - wall_x
            dy = ball.y - wall_y
            distance_to_wall = abs(dx * normal[0] + dy * normal[1])

            if distance_to_wall < ball.radius:
                # Reflect the ball based on the wall normal
                dot_product = ball.velocity_x * normal[0] + ball.velocity_y * normal[1]
                ball.velocity_x -= 2 * dot_product * normal[0]
                ball.velocity_y -= 2 * dot_product * normal[1]
                
                # Apply friction after collision
                ball.apply_friction()

                # Push ball out of the wall by the overlap amount
                overlap = ball.radius - distance_to_wall
                ball.x += normal[0] * overlap
                ball.y += normal[1] * overlap
                return True
        return False

# Create ball and hexagon
ball = Ball(WIDTH // 2, HEIGHT // 2, RADIUS)
hexagon = Hexagon(HEX_CENTER, HEX_SIZE)

# Main game loop
running = True
clock = pygame.time.Clock()
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Apply gravity
    ball.apply_gravity()

    # Move ball
    ball.move()

    # Check for collision with hexagon walls
    hexagon.check_collision(ball)

    # Draw hexagon and ball
    hexagon.draw(screen)
    pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), ball.radius)

    # Rotate hexagon
    hexagon.rotate()

    # Keep ball inside screen boundaries
    if ball.x - ball.radius < 0 or ball.x + ball.radius > WIDTH:
        ball.velocity_x = -ball.velocity_x
    if ball.y - ball.radius < 0 or ball.y + ball.radius > HEIGHT:
        ball.velocity_y = -ball.velocity_y

    # Apply friction to ball
    ball.apply_friction()

    # Update display
    pygame.display.flip()

    # Cap frame rate
    clock.tick(FPS)

pygame.quit()
