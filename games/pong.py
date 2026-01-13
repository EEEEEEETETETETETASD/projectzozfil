import pygame
import random

# Constants
WIDTH = 800
HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
BALL_SIZE = 10
PADDLE_SPEED = 5
CPU_SPEED = 3
BALL_SPEED = 5

class PongGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.max_score = 5
        self.reset()

    def reset(self):
        self.paddle1 = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.paddle2 = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        self.ball_dx = BALL_SPEED * (1 if random.random() > 0.5 else -1)
        self.ball_dy = BALL_SPEED * (1 if random.random() > 0.5 else -1)
        self.score1 = 0
        self.score2 = 0

    def ai_move(self):
        if abs(self.ball.centery - self.paddle2.centery) > 20:  # Tolerance
            if self.ball.centery < self.paddle2.centery:
                self.paddle2.y -= CPU_SPEED
            elif self.ball.centery > self.paddle2.centery:
                self.paddle2.y += CPU_SPEED
        self.paddle2.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def update(self):
        # Move ball
        self.ball.x += self.ball_dx
        self.ball.y += self.ball_dy

        # Bounce off top/bottom
        if self.ball.top <= 0 or self.ball.bottom >= HEIGHT:
            self.ball_dy = -self.ball_dy

        # Bounce off paddles
        if self.ball.colliderect(self.paddle1) or self.ball.colliderect(self.paddle2):
            self.ball_dx = -self.ball_dx

        # Score
        if self.ball.left <= 0:
            self.score2 += 1
            if self.score2 >= self.max_score:
                return False  # Player lost
            self.reset()
        if self.ball.right >= WIDTH:
            self.score1 += 1
            if self.score1 >= self.max_score:
                return True  # Player won
            self.reset()

        # AI
        self.ai_move()
        return None  # Continue

    def draw(self):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, self.paddle1)
        pygame.draw.rect(self.screen, WHITE, self.paddle2)
        pygame.draw.ellipse(self.screen, WHITE, self.ball)
        font = pygame.font.Font(None, 36)
        text1 = font.render(str(self.score1), True, WHITE)
        text2 = font.render(str(self.score2), True, WHITE)
        self.screen.blit(text1, (WIDTH // 4, 20))
        self.screen.blit(text2, (3 * WIDTH // 4, 20))
        pygame.display.flip()

    def play(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] and self.paddle1.top > 0:
                self.paddle1.y -= PADDLE_SPEED
            if keys[pygame.K_s] and self.paddle1.bottom < HEIGHT:
                self.paddle1.y += PADDLE_SPEED
            result = self.update()
            if result is not None:
                pygame.quit()
                return 10 if result else 0
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        return 0

if __name__ == "__main__":
    game = PongGame()
    earned = game.play()
    print(f"Earned: {earned}")