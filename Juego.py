import pygame
import random
import sys
import math

# Inicialización de Pygame
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter Arcade - Modo Fácil")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Jugador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 5
        self.health = 100
        self.direction = pygame.math.Vector2(0, 0)
        self.last_direction = pygame.math.Vector2(0, -1)
        
    def update(self):
        keys = pygame.key.get_pressed()
        move_x = keys[pygame.K_d] - keys[pygame.K_a]
        move_y = keys[pygame.K_s] - keys[pygame.K_w]
        
        if move_x != 0 or move_y != 0:
            self.direction = pygame.math.Vector2(move_x, move_y).normalize()
            self.last_direction = self.direction
        
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))
            
    def shoot(self):
        shoot_direction = self.direction if self.direction.length() > 0 else self.last_direction
        bullet = Bullet(self.rect.centerx, self.rect.centery, shoot_direction)
        all_sprites.add(bullet)
        bullets.add(bullet)

# Enemigos (más lentos)
class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.player = player
        # Velocidad reducida (rango más bajo)
        self.speed = random.uniform(0.5, 1.5)  # Antes era 1.0-3.0
        
        side = random.randint(0, 3)
        if side == 0:
            self.rect.x = random.randrange(WIDTH)
            self.rect.y = -self.rect.height
        elif side == 1:
            self.rect.x = WIDTH
            self.rect.y = random.randrange(HEIGHT)
        elif side == 2:
            self.rect.x = random.randrange(WIDTH)
            self.rect.y = HEIGHT
        else:
            self.rect.x = -self.rect.width
            self.rect.y = random.randrange(HEIGHT)
        
    def update(self):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        
        if dist != 0:
            dx, dy = dx / dist, dy / dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.speed = 10
        
    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        if (self.rect.right < 0 or self.rect.left > WIDTH or 
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()

# Grupos de sprites
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Crear jugador
player = Player()
all_sprites.add(player)

# Crear menos enemigos iniciales (solo 4 en lugar de 8)
for i in range(4):
    enemy = Enemy(player)
    all_sprites.add(enemy)
    enemies.add(enemy)

# Puntuación y tiempo
score = 0
font = pygame.font.SysFont('Arial', 30)
enemy_spawn_timer = 0
# Intervalo de aparición aumentado (2000ms = 2 segundos)
enemy_spawn_interval = 2000  # Antes era 1000 (1 segundo)

# La reducción de intervalo con el tiempo será más lenta
difficulty_increase = 5  # Antes era 10

clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()

running = True
while running:
    clock.tick(60)
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
    
    # Generar nuevos enemigos más espaciados
    if current_time - enemy_spawn_timer > enemy_spawn_interval:
        enemy = Enemy(player)
        all_sprites.add(enemy)
        enemies.add(enemy)
        enemy_spawn_timer = current_time
        # Reducción más lenta del intervalo de spawn
        enemy_spawn_interval = max(1000, enemy_spawn_interval - difficulty_increase)
    
    all_sprites.update()
    
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 10
        enemy = Enemy(player)
        all_sprites.add(enemy)
        enemies.add(enemy)
    
    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        player.health -= 10
        enemy = Enemy(player)
        all_sprites.add(enemy)
        enemies.add(enemy)
        if player.health <= 0:
            running = False
    
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    score_text = font.render(f"Puntuación: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    health_text = font.render(f"Salud: {player.health}", True, WHITE)
    screen.blit(health_text, (10, 50))
    
    elapsed_time = (current_time - start_time) // 1000
    time_text = font.render(f"Tiempo: {elapsed_time}s", True, WHITE)
    screen.blit(time_text, (10, 90))
    
    # Mostrar cantidad de enemigos actuales
    enemies_count = font.render(f"Enemigos: {len(enemies)}", True, WHITE)
    screen.blit(enemies_count, (10, 130))
    
    pygame.display.flip()

pygame.quit()
sys.exit()