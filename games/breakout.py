import pygame
import sys
import random
from supabase import create_client, Client
import config
import requests
import json

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
SERVER_URL = 'http://localhost:5000/api'

class Breakout:
    def __init__(self, cpu=True, room_id=None, access_token=None):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Breakout")
        self.clock = pygame.time.Clock()
        self.cpu = cpu
        self.room_id = room_id
        self.access_token = access_token
        self.paddle = pygame.Rect(350, 550, 100, 10)
        self.ball = pygame.Rect(395, 545, 10, 10)
        self.ball_speed = [0, -5]
        self.bricks = [pygame.Rect(50 + i*100, 50 + j*50, 80, 20) for i in range(7) for j in range(4)]
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        if not cpu and room_id:
            self.is_player1 = True
            self.subscribe_to_room()

    def subscribe_to_room(self):
        channel = supabase.realtime.channel(f'game_room_{self.room_id}')
        channel.on('UPDATE', self.on_state_update)
        channel.subscribe()

    def on_state_update(self, payload):
        state = json.loads(payload['record']['state'])
        # Sync ball, paddle, bricks for multiplayer (co-op or vs)
        self.ball.x = state['ball_x']
        self.ball.y = state['ball_y']
        self.ball_speed = state['ball_speed']
        self.bricks = state['bricks']
        self.score = state['score']

    def update_state(self):
        state = {
            'paddle_x': self.paddle.x,
            'ball_x': self.ball.x,
            'ball_y': self.ball.y,
            'ball_speed': self.ball_speed,
            'bricks': self.bricks,
            'score': self.score
        }
        requests.post(f"{SERVER_URL}/games/update_state", json={'room_id': self.room_id, 'state': state}, headers={"Authorization": f"Bearer {self.access_token}"})

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.report_result()
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.paddle.move_ip(-5, 0)
            if keys[pygame.K_RIGHT]:
                self.paddle.move_ip(5, 0)

            # Ball movement
            self.ball.move_ip(self.ball_speed)
            if self.ball.left <= 0 or self.ball.right >= 800:
                self.ball_speed[0] = -self.ball_speed[0]
            if self.ball.top <= 0:
                self.ball_speed[1] = -self.ball_speed[1]
            if self.ball.bottom >= 600:
                self.report_result()
                pygame.quit()
                sys.exit()  # Game over

            if self.ball.colliderect(self.paddle):
                self.ball_speed[1] = -self.ball_speed[1]

            for brick in self.bricks[:]:
                if self.ball.colliderect(brick):
                    self.bricks.remove(brick)
                    self.ball_speed[1] = -self.ball_speed[1]
                    self.score += 10

            if not self.cpu and self.room_id:
                self.update_state()

            self.screen.fill((0, 0, 0))
            pygame.draw.rect(self.screen, (255, 255, 255), self.paddle)
            pygame.draw.ellipse(self.screen, (255, 255, 255), self.ball)
            for brick in self.bricks:
                pygame.draw.rect(self.screen, (0, 255, 0), brick)
            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))
            pygame.display.flip()
            self.clock.tick(60)

    def report_result(self):
        requests.post(f"{SERVER_URL}/games/report_win", json={'game_type': 'breakout', 'won': len(self.bricks) == 0, 'score': self.score}, headers={"Authorization": f"Bearer {self.access_token}"})

def run_breakout(cpu=True, room_id=None, access_token=None):
    game = Breakout(cpu, room_id, access_token)
    game.run()

if __name__ == "__main__":
    run_breakout()
