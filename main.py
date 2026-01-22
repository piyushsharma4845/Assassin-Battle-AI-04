import pygame
import sys
import random
import math

# --- CONFIGURATION ---
WIDTH, HEIGHT = 1000, 500
FPS = 60
FLOOR_Y = 430  # Raised floor to ensure visibility

# Colors
BG_COLOR = (5, 5, 15)
TEXT_COLOR = (255, 255, 255)
ACCENT_RED = (200, 0, 0)
HIGHLIGHT_COLOR = (255, 215, 0)

MODELS = [
    ("SHADOW", (0, 150, 255), (20, 20, 20)),
    ("WARRIOR", (192, 192, 192), (255, 215, 0)),
    ("REBEL", (210, 180, 140), (139, 69, 19)),
    ("CYBORG", (50, 255, 50), (100, 100, 100)),
    ("PUNK", (255, 20, 147), (30, 30, 30)),
    ("ELITE", (34, 139, 34), (10, 20, 10)),
    ("TITAN", (70, 70, 80), (255, 69, 0))
]

# --- DRAWING UTILITY ---
def draw_fighter_model(surface, x, y, color, accent, direction=1, scale=1.0, anim_offset=0, punching=False, kicking=False, timer=0, winning=False):
    head_size = int(15 * scale)
    body_h = int(50 * scale)
    limb_w = int(6 * scale)
    
    head_y = y - int(45 * scale) + anim_offset
    torso_top = head_y + head_size - 5
    torso_bottom = torso_top + body_h
    
    # Body/Torso
    pygame.draw.rect(surface, accent, (x - int(15*scale), torso_top, int(30*scale), int(45*scale)), border_radius=int(5*scale))
    pygame.draw.line(surface, color, (x, torso_top), (x, torso_bottom), limb_w)
    
    # Head
    pygame.draw.circle(surface, color, (x, head_y), head_size)
    pygame.draw.line(surface, (255, 255, 255), (x, head_y), (x + int(12*scale)*direction, head_y), 3)
    
    # Victory Emote / Combat Animations
    if winning:
        # Arms raised in victory
        pygame.draw.line(surface, color, (x, torso_top + 10), (x - 25, torso_top - 20), limb_w)
        pygame.draw.line(surface, color, (x, torso_top + 10), (x + 25, torso_top - 20), limb_w)
    elif punching and timer > 0:
        pygame.draw.line(surface, color, (x, torso_top + 15), (x + int(70*scale)*direction, torso_top + 10), limb_w)
    elif kicking and timer > 0:
        pygame.draw.line(surface, color, (x, torso_bottom), (x + int(80*scale)*direction, torso_bottom + 5), limb_w + 2)
    else:
        # Idle Limbs
        pygame.draw.line(surface, color, (x, torso_top + 15), (x - int(15*scale)*direction, torso_top + 40), int(5*scale))
    
    # Legs (Always drawn)
    pygame.draw.line(surface, color, (x, torso_bottom), (x - int(12*scale), torso_bottom + int(30*scale)), int(7*scale))
    pygame.draw.line(surface, color, (x, torso_bottom), (x + int(12*scale), torso_bottom + int(30*scale)), int(7*scale))

class Fighter:
    def __init__(self, x, y, model_data, name, direction):
        self.rect = pygame.Rect(x, y, 60, 110)
        self.name = name
        self.color = model_data[1]
        self.accent = model_data[2]
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
        self.direction = direction

    def move(self, dx):
        if not self.alive: return
        self.velocity_y += 1.5
        dy = self.velocity_y
        if self.rect.bottom + dy > FLOOR_Y:
            dy = FLOOR_Y - self.rect.bottom
            self.velocity_y = 0
            self.is_jumping = False
        self.rect.x += dx
        self.rect.y += dy

    def draw(self, surface):
        if not self.alive:
            pygame.draw.circle(surface, (100, 100, 100), (self.rect.centerx + 45 * self.direction, FLOOR_Y - 12), 14)
            return
        
        main_c = (255, 255, 255) if self.hurt_timer > 0 else self.color
        if self.is_blocking: main_c = (120, 120, 120)
        
        # Win emote jump
        anim = math.sin(pygame.time.get_ticks() * 0.02) * 15 if self.is_winner else math.sin(pygame.time.get_ticks() * 0.01) * 3
        draw_fighter_model(surface, self.rect.centerx, self.rect.centery + 50, main_c, self.accent, self.direction, 1.0, anim, self.is_punching, self.is_kicking, self.attack_timer, self.is_winner)

# --- UI HELPERS ---
def draw_ui_text(surface, text, size, x, y, color=TEXT_COLOR):
    font = pygame.font.SysFont("Impact", size)
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect(center=(x, y))
    surface.blit(text_surf, rect)

def draw_control_guide(surface, menu_type="fighting"):
    pygame.draw.rect(surface, (20, 20, 30), (0, HEIGHT-40, WIDTH, 40))
    if menu_type == "fighting":
        guide = "MOVE: A/D | JUMP: W | PUNCH: J | KICK: L | BLOCK: I | RESTART: Shift + R"
    else:
        guide = "NAVIGATE: W/S or A/D | SELECT: J | RESTART: Shift + R"
    draw_ui_text(surface, guide, 20, WIDTH//2, HEIGHT-20, (150, 150, 150))

# --- SCREENS ---
def welcome_screen(screen, clock):
    while True:
        screen.fill(BG_COLOR)
        draw_ui_text(screen, "ASSASSIN BATTLE", 80, WIDTH//2, 180, ACCENT_RED)
        draw_ui_text(screen, "Step 1: Press J to Start", 30, WIDTH//2, 280)
        draw_control_guide(screen, "menu")
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_j: return
        pygame.display.flip()
        clock.tick(FPS)

def difficulty_menu(screen, clock):
    options = [("EASY", 0.1), ("MEDIUM", 0.5), ("HARD", 0.9)]
    selected = 0
    while True:
        screen.fill(BG_COLOR)
        draw_ui_text(screen, "Step 2: Select Difficulty", 40, WIDTH//2, 80)
        for i, (name, val) in enumerate(options):
            is_sel = i == selected
            rect = pygame.Rect(WIDTH//2-100, 160 + i*80, 200, 60)
            pygame.draw.rect(screen, (60,60,80) if is_sel else (40,40,50), rect, border_radius=10)
            pygame.draw.rect(screen, HIGHLIGHT_COLOR if is_sel else (200,200,200), rect, 2 if is_sel else 1, border_radius=10)
            draw_ui_text(screen, name, 24, rect.centerx, rect.centery)
        draw_control_guide(screen, "menu")
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_w: selected = (selected - 1) % 3
                if e.key == pygame.K_s: selected = (selected + 1) % 3
                if e.key == pygame.K_j: return options[selected][1]
        pygame.display.flip()
        clock.tick(FPS)

def character_menu(screen, clock):
    selected = 0
    while True:
        screen.fill(BG_COLOR)
        draw_ui_text(screen, "Step 3: Choose Fighter", 40, WIDTH//2, 80)
        for i, m in enumerate(MODELS):
            x_pos = 50 + i * 130
            rect = pygame.Rect(x_pos, 180, 110, 200)
            is_sel = i == selected
            pygame.draw.rect(screen, (60,60,80) if is_sel else (40,40,50), rect, border_radius=10)
            pygame.draw.rect(screen, HIGHLIGHT_COLOR if is_sel else (200,200,200), rect, 3 if is_sel else 1, border_radius=10)
            draw_fighter_model(screen, rect.centerx, rect.centery+30, m[1], m[2], 1, 0.7)
            draw_ui_text(screen, m[0], 20, rect.centerx, rect.top+25)
        draw_control_guide(screen, "menu")
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_a: selected = (selected - 1) % 7
                if e.key == pygame.K_d: selected = (selected + 1) % 7
                if e.key == pygame.K_j: return MODELS[selected]
        pygame.display.flip()
        clock.tick(FPS)

# --- MAIN GAME ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    while True: # Outer loop for Shift+R restart
        welcome_screen(screen, clock)
        diff = difficulty_menu(screen, clock)
        p_data = character_menu(screen, clock)
        
        player = Fighter(200, 300, p_data, "PLAYER", 1)
        enemy = Fighter(750, 300, ("BOSS", (150, 0, 0), (30, 0, 0)), "BOSS", -1)
        over = False
        reset_game = False

        while not reset_game:
            screen.fill(BG_COLOR)
            pygame.draw.rect(screen, (25, 25, 30), (0, FLOOR_Y, WIDTH, 70)) # Thick Floor
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN:
                    # Shift + R to Restart logic
                    if e.key == pygame.K_r and (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                        reset_game = True

            if not over:
                # Player Logic
                ks = pygame.key.get_pressed()
                p_dx = 0
                player.is_blocking = ks[pygame.K_i]
                if not player.is_blocking:
                    if ks[pygame.K_a]: p_dx = -7; player.direction = -1
                    if ks[pygame.K_d]: p_dx = 7; player.direction = 1
                    if ks[pygame.K_w] and not player.is_jumping: player.velocity_y = -26; player.is_jumping = True
                    if ks[pygame.K_j] and player.attack_timer == 0: player.is_punching, player.attack_timer = True, 12
                    if ks[pygame.K_l] and player.attack_timer == 0: player.is_kicking, player.attack_timer = True, 18
                player.move(p_dx)

                # AI Logic
                e_dx = 0
                dist = abs(enemy.rect.x - player.rect.x)
                if dist > 120: 
                    e_dx = -5 if enemy.rect.x > player.rect.x else 5
                    enemy.direction = -1 if enemy.rect.x > player.rect.x else 1
                elif enemy.attack_timer == 0:
                    if random.random() < 0.05:
                        if random.random() > 0.5: enemy.is_punching, enemy.attack_timer = True, 12
                        else: enemy.is_kicking, enemy.attack_timer = True, 18
                enemy.move(e_dx)

                # Combat Handling
                for f in [player, enemy]:
                    if f.attack_timer > 0: f.attack_timer -= 1
                    else: f.is_punching = f.is_kicking = False
                    if f.hurt_timer > 0: f.hurt_timer -= 1
                
                for att, tar in [(player, enemy), (enemy, player)]:
                    if att.attack_timer > 0:
                        reach = 90 if att.is_kicking else 70
                        if att.rect.inflate(reach, 0).colliderect(tar.rect) and not tar.is_blocking:
                            tar.health -= 1.5; tar.hurt_timer = 5

                if player.health <= 0:
                    player.health, player.alive = 0, False
                    enemy.is_winner, over = True, True
                elif enemy.health <= 0:
                    enemy.health, enemy.alive = 0, False
                    player.is_winner, over = True, True

            # HEALTH BARS (Visible at the top)
            pygame.draw.rect(screen, (100, 0, 0), (50, 30, 300, 25))
            pygame.draw.rect(screen, (0, 200, 0), (50, 30, max(0, int(player.health * 3)), 25))
            pygame.draw.rect(screen, (100, 0, 0), (WIDTH-350, 30, 300, 25))
            pygame.draw.rect(screen, (0, 200, 0), (WIDTH-350, 30, max(0, int(enemy.health * 3)), 25))

            player.draw(screen)
            enemy.draw(screen)
            
            if over:
                msg = "PLAYER WINS!" if player.is_winner else "BOSS WINS!"
                draw_ui_text(screen, msg, 60, WIDTH//2, HEIGHT//2, HIGHLIGHT_COLOR)
                draw_ui_text(screen, "Shift + R to Restart", 30, WIDTH//2, HEIGHT//2 + 60)
            
            draw_control_guide(screen)
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()
