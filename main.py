import pygame
from pygame.locals import *
from sys import exit
import random

pygame.init()

health = 3
totalwaves = 11
wave = 0
score = 0
running = True
enforcer = False
sniper = False
machine = False
shooting = False
auto_fire = False  
screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
screen_width, screen_height = screen.get_size()
pygame.display.set_caption("Space Shooter")
last_time = pygame.time.get_ticks()

close_button = pygame.Surface((int(screen_width * 0.04), int(screen_width * 0.04)))
close_button.fill((255, 0, 0))
pygame.draw.line(close_button, (255, 255, 255), (0, 0), (int(screen_width * 0.04), int(screen_width * 0.04)), 5)
pygame.draw.line(close_button, (255, 255, 255), (0, int(screen_width * 0.04)), (int(screen_width * 0.04), 0), 5)
close_button_rect = close_button.get_rect(topright=(screen_width - int(screen_width * 0.01), int(screen_width * 0.01)))

font = pygame.font.Font(None, 74)
wave_font = pygame.font.Font(None, 36)
score_font = pygame.font.Font(None, 36)

password = "specialship"
password_input = ""
use_special_ship = False
special_ship_unlocked = False

class Player(pygame.sprite.Sprite):
    def __init__(self, special=False, enforcer=False, sniper=False, machine=False):
        super().__init__()
        if special:
            self.image = pygame.image.load("graphics/special_player.png").convert_alpha()
        elif enforcer:
            self.image = pygame.image.load("graphics/enforcer_player.png").convert_alpha()
        elif sniper:
            self.image = pygame.image.load("graphics/sniper_player.png").convert_alpha()
        elif machine:
            self.image = pygame.image.load("graphics/machine_player.png").convert_alpha()
        else:
            self.image = pygame.image.load("graphics/player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(screen_width * 0.055), int(screen_width * 0.045)))
        self.rect = self.image.get_rect(center=(int(screen_width * 0.5), int(screen_height) - 30))
        self.special = special
        self.enforcer = enforcer
        self.sniper = sniper
        self.machine = machine
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        global running, health
        keys = pygame.key.get_pressed()
        if keys[K_a]:
            self.rect.x -= 5
        if keys[K_d]:
            self.rect.x += 5
        if self.rect.x < 10:
            self.rect.x = 10
        if self.rect.x > (int(screen_width)) - 70:
            self.rect.x = (int(screen_width)) - 70
        if pygame.sprite.spritecollide(self, enemy_bullet_group, True):
            health -= 1
            

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, damage=1):
        super().__init__()
        self.image = pygame.image.load("graphics/bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(screen_width * 0.02), int(screen_width * 0.04)))
        self.rect = self.image.get_rect(center=pos)
        self.damage = damage

    def update(self):
        self.rect.y -= 15
        if self.rect.y < -50:
            self.kill()

class MachineBullet(Bullet):
    def __init__(self, pos):
        super().__init__(pos, damage=0.3)

class SniperBullet(Bullet):
    def __init__(self, pos):
        super().__init__(pos, damage=5)

class HomingBullet(Bullet):
    def __init__(self, pos, target_group):
        super().__init__(pos, damage=0.5)
        self.target_group = target_group

    def update(self):
        closest_enemy = min(self.target_group, key=lambda e: pygame.Vector2(self.rect.center).distance_to(e.rect.center), default=None)
        if closest_enemy:
            direction = pygame.Vector2(closest_enemy.rect.center) - pygame.Vector2(self.rect.center)
            direction = direction.normalize()
            self.rect.center += direction * 5
        else:
            self.rect.y -= 8
        if self.rect.y < -50:
            self.kill()

class ShieldBullet(Bullet):
    def __init__(self, pos):
        super().__init__(pos, damage=1)
        self.image = pygame.image.load('graphics/shield.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(screen_width * 0.06), int(screen_width * 0.02)))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, stop_position, health):
        super().__init__()
        self.image = pygame.image.load("graphics/enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(screen_width * 0.05), int(screen_height * 0.05)))
        self.rect = self.image.get_rect(center=pos)
        self.stop_position = stop_position
        self.health = health
        self.last_shot = pygame.time.get_ticks()
        self.shoot_interval = random.randint(800, 2000)
        self.move_speed = random.randint(1, 4)

    def update(self):
        global score
        if self.rect.y < self.stop_position:
            self.rect.y += 3
        else:
            if pygame.time.get_ticks() - self.last_shot > self.shoot_interval:
                ebullet = EBullet(self.rect.center)
                enemy_bullet_group.add(ebullet)
                self.last_shot = pygame.time.get_ticks()
                self.shoot_interval = random.randint(800, 2000)

        self.rect.x += self.move_speed
        if self.rect.x < 0 or self.rect.x > screen_width:
            self.move_speed *= -1  
        if pygame.sprite.spritecollide(self, bullet_group, True):
            self.health -= 1
            if self.health <= 0:
                self.kill()
                score += 10
        if pygame.sprite.spritecollide(self, shield_bullet_group, True):
            self.health -= 1
            if self.health <= 0:
                self.kill()
                score += 10
        if pygame.sprite.spritecollide(self, sniper_bullet_group, True):
            self.health -= 5
            if self.health <= 0:
                self.kill()
                score += 10
        if pygame.sprite.spritecollide(self, machine_bullet_group, True):
            self.health -= 0.3
            if self.health <= 0:
                self.kill()
                score += 10
        if pygame.sprite.spritecollide(self, homing_bullet_group, True):
            self.health -= 0.5
            if self.health <= 0:
                self.kill()
                score += 10
class EBullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("graphics/enemy_bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(screen_width * 0.02), int(screen_width * 0.04)))
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.y += 5
        if self.rect.y > screen_height:
            self.kill()

        collisions = pygame.sprite.spritecollide(self, shield_bullet_group, True)
        if collisions:
            self.kill()

def spawn_wave(wave):
    base_enemies_per_wave = 0
    rows_per_wave = 3
    row_height = 100
    max_row_width = screen_width * 0.9
    enemies_per_wave = base_enemies_per_wave + wave
    enemy_health = (wave // 3) * 2 + 3  

    x_spacing = min(screen_width // (enemies_per_wave + 1), max_row_width // (enemies_per_wave + 1))

    for row in range(rows_per_wave):
        row_width = x_spacing * enemies_per_wave
        if row_width > max_row_width:
            x_spacing = min(max_row_width // enemies_per_wave, x_spacing)
            row_width = x_spacing * enemies_per_wave
        start_x = (screen_width - row_width) // 2
        for i in range(enemies_per_wave):
            x_pos = start_x + i * x_spacing
            y_pos = -50 - row * row_height
            stop_position = 50 + row * row_height
            enemy = Enemy((x_pos, y_pos), stop_position, enemy_health)
            enemy_group.add(enemy)

player_group = pygame.sprite.GroupSingle()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()
shield_bullet_group = pygame.sprite.Group()
sniper_bullet_group = pygame.sprite.Group()
machine_bullet_group = pygame.sprite.Group()
homing_bullet_group = pygame.sprite.Group()
heart = pygame.image.load("graphics/health.png").convert_alpha()
heart = pygame.transform.scale(heart, (60, 60))

clock = pygame.time.Clock()
wave_time = pygame.time.get_ticks()

win_text = font.render("You Win!", True, (255, 255, 255))
lose_text = font.render("You Lose!", True, (255, 0, 0))
password_prompt_text = font.render("Enter Password:", True, (255, 255, 255))

input_active = True
while input_active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                password_input = password_input[:-1]
            elif event.key == pygame.K_RETURN:
                input_active = False
            else:
                password_input += event.unicode

    screen.fill((0, 0, 0))
    password_display = font.render(password_input, True, (255, 255, 255))
    screen.blit(password_prompt_text, ((screen_width - password_prompt_text.get_width()) // 2, (screen_height - password_prompt_text.get_height()) // 2 - 50))
    screen.blit(password_display, ((screen_width - password_display.get_width()) // 2, (screen_height - password_display.get_height()) // 2))
    pygame.display.update()
    clock.tick(60)

if password_input == password:
    player = Player(special=True)
    player_group.add(player)
    special_ship_unlocked = True
elif password_input == "enforcer":
    player = Player(enforcer=True)
    player_group.add(player)
    enforcer = True
elif password_input == "sniper":
    player = Player(sniper=True)
    player_group.add(player)
    sniper = True
elif password_input == "machine gunner":
    player = Player(machine=True)
    player_group.add(player)
    machine = True
else:
    player = Player()
    player_group.add(player)

while True:
    x = 100
    if health <= 0:
        running = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if running:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if close_button_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_SPACE:
                    if auto_fire:
                        auto_fire = False
                    else:
                        auto_fire = True
    
    if auto_fire:
        player_firerate = 100
        enforcer_firerate = 200
        sniper_firerate = 200
        specialship_firerate = 120
        machinegunner_firerate = 50
        if enforcer:
            fire_rate = enforcer_firerate
        elif sniper:
            fire_rate = sniper_firerate
        elif special_ship_unlocked:
            fire_rate = specialship_firerate
        elif machine:
            fire_rate = machinegunner_firerate
        else:
            fire_rate = player_firerate
        current_time = pygame.time.get_ticks()
        if current_time - player.last_shot > fire_rate:  
            if enforcer:
                bullet = ShieldBullet(player.rect.center)
                shield_bullet_group.add(bullet)
            elif sniper:
                bullet = SniperBullet(player.rect.center)
                sniper_bullet_group.add(bullet)
            elif special_ship_unlocked:
                bullet = HomingBullet(player.rect.center, enemy_group)
                homing_bullet_group.add(bullet)
            elif machine:
                bullet = MachineBullet(player.rect.center)
                machine_bullet_group.add(bullet)
            else:
                bullet = Bullet(player.rect.center)
                bullet_group.add(bullet)
            
            player.last_shot = current_time

    screen.fill((0, 0, 0))
    screen.blit(close_button, close_button_rect)
    for _ in range(health):
        screen.blit(heart, (20, x))
        x += 70
    if running:
        if len(enemy_group) == 0 and wave < totalwaves:
            wave += 1
            if wave > totalwaves:
                break
            spawn_wave(wave)
            wave_time = pygame.time.get_ticks()

        wave_text = wave_font.render(f"Wave: {wave}", True, (255, 255, 255))
        screen.blit(wave_text, (10, 10))

        score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 50))

        player_group.update()
        player_group.draw(screen)
        bullet_group.update()
        bullet_group.draw(screen)
        enemy_group.update()
        enemy_group.draw(screen)
        enemy_bullet_group.update()
        enemy_bullet_group.draw(screen)
        shield_bullet_group.update()
        shield_bullet_group.draw(screen)
        sniper_bullet_group.update()
        sniper_bullet_group.draw(screen)
        machine_bullet_group.update()
        machine_bullet_group.draw(screen)
        homing_bullet_group.update()
        homing_bullet_group.draw(screen)
        pygame.display.update()
        clock.tick(60)
        
    if not running:
        screen.fill((0, 0, 0))
        screen.blit(lose_text, ((screen_width - lose_text.get_width()) // 2, (screen_height - lose_text.get_height()) // 2))
        final_score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        screen.blit(final_score_text, ((screen_width - final_score_text.get_width()) // 2, (screen_height - final_score_text.get_height()) // 2 + 50))
        pygame.display.update()
        pygame.time.wait(3000)
        pygame.quit()
        exit()
if running:
    screen.blit(win_text, ((screen_width - win_text.get_width()) // 2, (screen_height - win_text.get_height()) // 2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()
    exit()