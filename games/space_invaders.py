import pygame
import sys
import random
from supabase import create_client, Client
import config
import requests
import json

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
SERVER_URL = 'http://localhost:5000/api'

class SpaceInvaders:
    def __init__(self, cpu=True, room_id=None, access_token=None):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.player = pygame.Rect(370, 550, 60, 20)
        self.invaders = [pygame.Rect(50 + i*100, 50 + j*50, 40, 20) for i in range(6) for j in range(3)]
        self.bullets = []
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.access_token = access_token
        self.room_id = room_id
        self.cpu = cpu
        if not cpu and room_id:
            self.subscribe_to_room()

    def subscribe_to_room(self):
        channel = supabase.realtime.channel(f'game_room_{self.room_id}')
        channel.on('UPDATE', self.on_state_update)
        channel.subscribe()

    def on_state_update(self, payload):
        state = json.loads(payload['record']['state'])
        self.invaders = state['invaders']
        self.bullets = state['bullets']
        self.score = state['score']

    def update_state(self):
        state = {
            'player_x': self.player.x,
            'invaders': [(r.x, r.y) for r in self.invaders],
            'bullets': [(b.x, b.y) for b in self.bullets],
            'score': self.score
        }
        requests.post(f"{SERVER_URL}/games/update_state", json={'room_id': self.room_id, 'state': state}, headers={"Authorization": f"Bearer {self.access_token}"})

    def run(self):
        direction = 5
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.report_result()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bullet = pygame.Rect(self.player.centerx - 2, self.player.top, 5, 10)
                        self.bullets.append(bullet)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move_ip(-5, 0)
            if keys[pygame.K_RIGHT]:
                self.player.move_ip(5, 0)

            # Move invaders
            for inv in self.invaders:
                inv.x += direction
            if any(inv.right >= 800 or inv.left <= 0 for inv in self.invaders):
                direction = -direction
                for inv in self.invaders:
                    inv.y += 20

            # Move bullets
            for bullet in self.bullets[:]:
                bullet.y -= 10
                if bullet.bottom <= 0:
                    self.bullets.remove(bullet)
                for inv in self.invaders[:]:
                    if bullet.colliderect(inv):
                        self.invaders.remove(inv)
                        self.bullets.remove(bullet)
                        self.score += 10
                        break

            if any(inv.bottom >= 600 for inv in self.invaders) or not self.invaders:
                self.report_result()
                pygame.quit()
                sys.exit()

            if not self.cpu and self.room_id:
                self.update_state()

            self.screen.fill((0, 0, 0))
            pygame.draw.rect(self.screen, (255, 255, 255), self.player)
            for inv in self.invaders:
                pygame.draw.rect(self.screen, (0, 255, 0), inv)
            for bullet in self.bullets:
                pygame.draw.rect(self.screen, (255, 0, 0), bullet)
            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))
            pygame.display.flip()
            self.clock.tick(60)

    def report_result(self):
        won = not self.invaders
        requests.post(f"{SERVER_URL}/games/report_win", json={'game_type': 'space_invaders', 'won': won, 'score': self.score}, headers={"Authorization": f"Bearer {self.access_token}"})

def run_space_invaders(cpu=True, room_id=None, access_token=None):
    game = SpaceInvaders(cpu, room_id, access_token)
    game.run()

if __name__ == "__main__":
    run_space_invaders()
