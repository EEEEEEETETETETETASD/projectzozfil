import pygame
import sys
import random
from supabase import create_client, Client
import config
import requests
import time
import json

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
SERVER_URL = 'http://localhost:5000/api'

class Snake:
    def __init__(self, cpu=True, room_id=None, access_token=None):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 600))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.cpu = cpu
        self.room_id = room_id
        self.access_token = access_token
        self.snake = [(300, 300)]
        self.direction = (0, -20)  # Up
        self.food = self.random_food()
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        if not cpu and room_id:
            self.is_player1 = True
            self.subscribe_to_room()
            # For multiplayer Snake, perhaps competitive scores or shared board

    def subscribe_to_room(self):
        channel = supabase.realtime.channel(f'game_room_{self.room_id}')
        channel.on('UPDATE', self.on_state_update)
        channel.subscribe()

    def on_state_update(self, payload):
        state = json.loads(payload['record']['state'])
        # Sync snake positions, food, etc. for multiplayer
        pass  # Implement sync logic

    def update_state(self):
        state = {
            'snake': self.snake,
            'direction': self.direction,
            'food': self.food,
            'score': self.score
        }
        requests.post(f"{SERVER_URL}/games/update_state", json={'room_id': self.room_id, 'state': state}, headers={"Authorization": f"Bearer {self.access_token}"})

    def random_food(self):
        return (random.randint(0, 29)*20, random.randint(0, 29)*20)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.report_result()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != (0, 20):
                        self.direction = (0, -20)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -20):
                        self.direction = (0, 20)
                    elif event.key == pygame.K_LEFT and self.direction != (20, 0):
                        self.direction = (-20, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-20, 0):
                        self.direction = (20, 0)

            head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])
            if head == self.food:
                self.snake.insert(0, head)
                self.food = self.random_food()
                self.score += 1
            else:
                self.snake.insert(0, head)
                self.snake.pop()

            if head[0] < 0 or head[0] >= 600 or head[1] < 0 or head[1] >= 600 or head in self.snake[1:]:
                self.report_result()
                pygame.quit()
                sys.exit()

            if not self.cpu and self.room_id:
                self.update_state()

            self.screen.fill((0, 0, 0))
            for segment in self.snake:
                pygame.draw.rect(self.screen, (0, 255, 0), (segment[0], segment[1], 20, 20))
            pygame.draw.rect(self.screen, (255, 0, 0), (self.food[0], self.food[1], 20, 20))
            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))
            pygame.display.flip()
            self.clock.tick(10)

    def report_result(self):
        # Report score as currency
        requests.post(f"{SERVER_URL}/games/report_win", json={'game_type': 'snake', 'won': True, 'score': self.score}, headers={"Authorization": f"Bearer {self.access_token}"})

def run_snake(cpu=True, room_id=None, access_token=None):
    game = Snake(cpu, room_id, access_token)
    game.run()

if __name__ == "__main__":
    run_snake()
