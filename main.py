import pygame
import sys
import random
import math

# --- CONFIGURATION ---
WIDTH, HEIGHT = 1000, 500
FPS = 60
FLOOR_Y = 450

MODELS = [
    ("SHADOW", (0, 150, 255), (20, 20, 20), "stealth"),
    ("WARRIOR", (192, 192, 192), (255, 215, 0), "knight"),
    ("REBEL", (210, 180, 140), (139, 69, 19), "bandana"),
    ("CYBORG", (50, 255, 50), (100, 100, 100), "robot"),
    ("PUNK", (255, 20, 147), (30, 30, 30), "mohawk"),
    ("ELITE", (34, 139, 34), (10, 20, 10), "tactical"),
    ("TITAN", (70, 70, 80), (255, 69, 0), "spiky")
]

class Fighter:
    def __init__(self, x, y, model_data, name, direction, is_villain=False):
        self.name = name
        self.rect = pygame.Rect(x, y, 60, 110)
        self.color = model_data[1]
        self.accent = model_data[2]
        self.costume = model_data[3]
        self.is_villain = is_villain
        self.health = 100
        self.alive = True
        self.is_winner = False
        self.velocity_y = 0
        self.is_jumping = False
        self.is_punching = False
        self.is_kicking = False
        self.attack_timer = 0 
        self.is_blocking = False
        self.hurt_timer = 0
        self.anim_offset = 0
        self.direction = direction

    def move(self, dx, dy):
        if not self.alive or self.is_winner: return
        self.velocity_y += 1.5
        dy += self.velocity_y
        
        if self.rect.bottom + dy > FLOOR_Y:
            dy = FLOOR_Y - self.rect.bottom
            self.velocity_y = 0
            self.is_jumping = False
            
        self.rect.x += dx
        self.rect.y += dy
        self.anim_offset = math.sin(pygame.time.get_ticks() * 0.005) * 4

    def draw(self, surface):
        x, y = self.rect.centerx, self.rect.y
        
        if not self.alive:
            dead_c = (100, 100, 100)
            head_x = x + 45 * self.direction
            pygame.draw.circle(surface, dead_c, (head_x, FLOOR_Y - 12), 14) 
            pygame.draw.line(surface, dead_c, (x - 40*self.direction, FLOOR_Y - 8), (x + 30*self.direction, FLOOR_Y - 8), 8) 
            return

        main_c = (255, 255, 255) if self.hurt_timer > 0 else self.color
        if self.is_blocking: main_c = (120, 120, 120)
        
        bounce = math.sin(pygame.time.get_ticks() * 0.02) * 10 if self.is_winner else self.anim_offset
        head_y, arm_y, leg_y = int(y + 12 + bounce), y + 38 + bounce, y + 75
        
        # Draw Body
        pygame.draw.rect(surface, self.accent, (x-15, arm_y-15, 30, 45), border_radius=5)
        pygame.draw.line(surface, main_c, (x, head_y+10), (x, leg_y), 7) 
        pygame.draw.circle(surface, main_c, (x, head_y), 15)
        
        # Eyes/Face Direction
        pygame.draw.line(surface, (255,255,255), (x, head_y), (x + 14*self.direction, head_y), 4)

        # Attack Animations
        if self.is_punching and self.attack_timer > 0:
            pygame.draw.line(surface, main_c, (x, arm_y), (x + 70*self.direction, arm_y-5), 8)
        elif self.is_kicking and self.attack_timer > 0:
            pygame.draw.line(surface, main_c, (x, leg_y), (x + 85*self.direction, leg_y + 5), 9) 
        else:
            # Idle/Walking Limbs
            pygame.draw.line(surface, main_c, (x, arm_y), (x - 18*self.direction, arm_y+30), 5)
            pygame.draw.line(surface, main_c, (x, leg_y), (x - 15, leg_y + 40), 8)
            pygame.draw.line(surface, main_c, (x, leg_y), (x + 15, leg_y + 40), 8)

# --- UI HELPER ---
def draw_text_btn(surface, text, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, (50, 50, 50), rect, border_radius=10)
    pygame.draw.rect(surface, (200, 200, 200), rect, 2, border_radius=10)
    f = pygame.font.SysFont("Arial", 24, bold=True)
    t_surf = f.render(text, True, (255, 255, 255))
    surface.blit(t_surf, (rect.centerx - t_surf.get_width()//2, rect.centery - t_surf.get_height()//2))
    return rect

# --- SCREENS ---
def welcome_screen(screen, clock):
    f = pygame.font.SysFont("Impact", 70)
    while True:
        screen.fill((5, 5, 10))
        screen.blit(f.render("ASSASSIN BATTLE", True, (255, 0, 0)), (WIDTH//2-220, 150))
        btn = draw_text_btn(screen, "CLICK TO START", WIDTH//2-150, 350, 300, 60)
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn.collidepoint(e.pos): return
        pygame.display.flip()
        clock.tick(FPS)

def difficulty_menu(screen, clock):
    levels = [("EASY", 0.25), ("MEDIUM", 0.65), ("HARD", 0.95)]
    while True:
        screen.fill((10, 10, 15))
        for i, (name, val) in enumerate(levels):
            rect = draw_text_btn(screen, name, WIDTH//2-100, 150+i*80, 200, 60)
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(e.pos): return val
        pygame.display.flip()
        clock.tick(FPS)

def character_menu(screen, clock):
    while True:
        screen.fill((10, 10, 20))
        for i, m in enumerate(MODELS):
            rect = draw_text_btn(screen, m[0], 50+i*130, 200, 110, 150)
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(e.pos): return m
        pygame.display.flip()
        clock.tick(FPS)

# --- MAIN GAME LOOP ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Assassin Battle - PC Version")
    clock = pygame.time.Clock()
    
    welcome_screen(screen, clock)
    diff_val = difficulty_menu(screen, clock)
    player_data = character_menu(screen, clock)
    
    player = Fighter(200, 300, player_data, "PLAYER", 1)
    ai_bot = Fighter(750, 300, ("BOSS", (150, 0, 0), (30, 0, 0), "spiky"), "BOSS", -1, is_villain=True)
    
    over = False

    while True:
        screen.fill((5, 5, 10))
        # Draw Floor
        pygame.draw.rect(screen, (25, 25, 30), (0, FLOOR_Y, WIDTH, 50))
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()

        if not over:
            ks = pygame.key.get_pressed()
            p_dx = 0
            
            # --- PLAYER CONTROLS (Based on your image) ---
            player.is_blocking = ks[pygame.K_i] # I Key to Block
            
            if not player.is_blocking:
                # Move: A / D keys
                if ks[pygame.K_a]: p_dx = -7; player.direction = -1
                if ks[pygame.K_d]: p_dx = 7; player.direction = 1
                
                # Jump: W key
                if ks[pygame.K_w] and not player.is_jumping: 
                    player.velocity_y = -26
                    player.is_jumping = True
                
                # Punch: J key
                if ks[pygame.K_j] and player.attack_timer == 0: 
                    player.is_punching = True
                    player.attack_timer = 12
                
                # Kick: L key
                if ks[pygame.K_l] and player.attack_timer == 0: 
                    player.is_kicking = True
                    player.attack_timer = 18
            
            player.move(p_dx, 0)
            if player.attack_timer > 0: player.attack_timer -= 1
            if player.hurt_timer > 0: player.hurt_timer -= 1

            # --- AI LOGIC ---
            ai_dx = 0
            if random.random() < diff_val and player.attack_timer > 0: 
                ai_bot.is_blocking = True
            else:
                ai_bot.is_blocking = False
                dist = abs(ai_bot.rect.x - player.rect.x)
                if dist > 140: 
                    ai_dx = -5 if ai_bot.rect.x > player.rect.x else 5
                elif ai_bot.attack_timer == 0 and random.random() < 0.05:
                    if random.random() > 0.5: 
                        ai_bot.is_punching, ai_bot.attack_timer = True, 12
                    else: 
                        ai_bot.is_kicking, ai_bot.attack_timer = True, 18
            
            ai_bot.move(ai_dx, 0)
            if ai_bot.attack_timer > 0: ai_bot.attack_timer -= 1
            if ai_bot.hurt_timer > 0: ai_bot.hurt_timer -= 1

            # --- COLLISION / DAMAGE ---
            for att, tar in [(player, ai_bot), (ai_bot, player)]:
                if att.attack_timer > 0:
                    reach = 95 if att.is_kicking else 70
                    # Check if attacker is facing target and close enough
                    if att.rect.inflate(reach, 0).colliderect(tar.rect) and not tar.is_blocking:
                        tar.health -= 1.0
                        tar.hurt_timer = 5
                else: 
                    att.is_punching = att.is_kicking = False
            
            if player.health <= 0: player.alive = False; over = True
            if ai_bot.health <= 0: ai_bot.alive = False; over = True

        # --- DRAW HEALTH BARS ---
        pygame.draw.rect(screen, (200, 0, 0), (50, 30, 300, 20))
        pygame.draw.rect(screen, (0, 255, 0), (50, 30, player.health * 3, 20))
        pygame.draw.rect(screen, (200, 0, 0), (WIDTH-350, 30, 300, 20))
        pygame.draw.rect(screen, (0, 255, 0), (WIDTH-350, 30, ai_bot.health * 3, 20))

        player.draw(screen)
        ai_bot.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
  
if __name__ == "__main__":
    main()
