import pygame
import sys
import random
import math
import asyncio  # Required for web compatibility

# --- CONFIGURATION ---
WIDTH, HEIGHT = 1000, 500
FPS = 60
FLOOR_Y = 450

# Character Models: (Name, Primary Color, Accents, CostumeType)
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

    def draw(self, surface, preview_pos=None):
        if preview_pos: x, y = preview_pos
        else: x, y = self.rect.centerx, self.rect.y
            
        if not self.alive:
            dead_c = (100, 100, 100)
            head_x = x + 45 * self.direction
            pygame.draw.circle(surface, dead_c, (head_x, FLOOR_Y - 12), 14) 
            pygame.draw.line(surface, dead_c, (x - 40*self.direction, FLOOR_Y - 8), (x + 30*self.direction, FLOOR_Y - 8), 8) 
            return

        main_c = (255, 255, 255) if self.hurt_timer > 0 else self.color
        if self.is_blocking: main_c = (120, 120, 120)
        
        bounce = math.sin(pygame.time.get_ticks() * 0.02) * 10 if self.is_winner else self.anim_offset
        head_y = int(y + 12 + bounce)
        arm_y = y + 38 + bounce
        leg_y = y + 75

        if self.costume == "knight" or self.is_villain:
            cape_c = (150, 0, 0) if self.is_villain else (100, 100, 120)
            pygame.draw.polygon(surface, cape_c, [(x, arm_y), (x - 35*self.direction, leg_y + 35), (x - 5*self.direction, leg_y + 40)])

        pygame.draw.rect(surface, self.accent, (x-15, arm_y-15, 30, 45), border_radius=5)
        pygame.draw.line(surface, main_c, (x, head_y+10), (x, leg_y), 7) 

        pygame.draw.circle(surface, main_c, (x, head_y), 15)
        if self.costume == "knight":
            pygame.draw.line(surface, (255, 0, 0), (x, head_y-15), (x-10*self.direction, head_y-25), 5)
        elif self.costume == "bandana":
            pygame.draw.line(surface, self.accent, (x-12*self.direction, head_y-5), (x-30*self.direction, head_y+5), 4)
        elif self.costume == "mohawk":
            for i in range(5): pygame.draw.line(surface, (255,20,147), (x-5+i*3, head_y-15), (x-5+i*3, head_y-25), 3)
        elif self.costume == "spiky" or self.is_villain:
            pygame.draw.line(surface, (0,0,0), (x-10, head_y-12), (x-15, head_y-25), 4)
            pygame.draw.line(surface, (0,0,0), (x+10, head_y-12), (x+15, head_y-25), 4)
        
        pygame.draw.line(surface, (255,255,255), (x, head_y), (x + 14*self.direction, head_y), 4)

        if self.is_winner:
            pygame.draw.line(surface, main_c, (x, arm_y), (x - 30, arm_y - 45), 6) 
            pygame.draw.line(surface, main_c, (x, arm_y), (x + 30, arm_y - 45), 6)
        elif self.is_punching and self.attack_timer > 0:
            pygame.draw.line(surface, main_c, (x, arm_y), (x + 70*self.direction, arm_y-5), 8)
        else:
            pygame.draw.line(surface, main_c, (x, arm_y), (x - 18*self.direction, arm_y+30), 5)
            pygame.draw.line(surface, main_c, (x, arm_y), (x + 12*self.direction, arm_y+35), 5)

        if self.is_winner:
            pygame.draw.line(surface, main_c, (x, leg_y), (x - 15, leg_y + 40), 8)
            pygame.draw.line(surface, main_c, (x, leg_y), (x + 15, leg_y + 40), 8)
        elif self.is_kicking and self.attack_timer > 0:
            pygame.draw.line(surface, main_c, (x, leg_y), (x - 8*self.direction, leg_y + 40), 8) 
            pygame.draw.line(surface, main_c, (x, leg_y), (x + 85*self.direction, leg_y + 5), 9) 
        else:
            pygame.draw.line(surface, main_c, (x, leg_y), (x - 15, leg_y + 40), 8)
            pygame.draw.line(surface, main_c, (x, leg_y), (x + 15, leg_y + 40), 8)

# --- ASYNC MENUS ---
async def welcome_screen(screen, clock):
    title_font = pygame.font.SysFont("Impact", 90)
    creator_font = pygame.font.SysFont("Arial", 28, italic=True)
    start_font = pygame.font.SysFont("Impact", 30)
    
    while True:
        screen.fill((5, 5, 10))
        title_surf = title_font.render("ASSASSIN BATTLE", True, (255, 0, 0))
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 140))
        creator_surf = creator_font.render("Created by Piyush Sharma", True, (200, 200, 200))
        screen.blit(creator_surf, (WIDTH//2 - creator_surf.get_width()//2, 240))
        
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            start_surf = start_font.render("PRESS  'J'  TO START MISSION", True, (255, 255, 255))
            screen.blit(start_surf, (WIDTH//2 - start_surf.get_width()//2, 360))
            
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_j: return
        
        pygame.display.flip()
        await asyncio.sleep(0) # Let the browser breathe
        clock.tick(FPS)

async def difficulty_menu(screen, clock):
    font = pygame.font.SysFont("Impact", 60)
    subfont = pygame.font.SysFont("Arial", 28, bold=True)
    instr_font = pygame.font.SysFont("Arial", 22, bold=True)
    levels = [("EASY", (0, 255, 100), 0.25), ("MEDIUM", (255, 255, 100), 0.65), ("HARD", (255, 50, 50), 0.95)]
    sel = 1
    while True:
        screen.fill((10, 10, 15))
        title = font.render("SELECT DIFFICULTY", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        
        for i, (name, color, val) in enumerate(levels):
            is_sel = (i == sel)
            c = color if is_sel else (80, 80, 80)
            txt = subfont.render(name, True, c)
            x_p, y_p = WIDTH//2 - txt.get_width()//2, 210 + i*70
            screen.blit(txt, (x_p, y_p))
            if is_sel:
                pygame.draw.circle(screen, color, (x_p - 45, y_p + 18), 12, 2)
                pygame.draw.circle(screen, color, (x_p - 45, y_p + 18), 6)
        
        instr = instr_font.render("USE 'W' / 'S' TO NAVIGATE  |  PRESS 'J' TO CONFIRM", True, (255, 255, 255))
        screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 430))
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_w: sel = (sel - 1) % 3
                if e.key == pygame.K_s: sel = (sel + 1) % 3
                if e.key == pygame.K_j: return levels[sel][2]
        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(FPS)

async def character_menu(screen, clock):
    font = pygame.font.SysFont("Impact", 50)
    subfont = pygame.font.SysFont("Arial", 18, bold=True)
    sel = 0
    previews = [Fighter(0,0, m, m[0], 1) for m in MODELS]
    while True:
        screen.fill((10, 10, 20))
        title = font.render("SELECT YOUR FIGHTER", True, (255,255,255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        for i, m in enumerate(MODELS):
            x_pos = 60 + i*135
            rect = pygame.Rect(x_pos, 180, 110, 180)
            box_c = (60, 60, 80) if i == sel else (40, 40, 50)
            pygame.draw.rect(screen, box_c, rect, border_radius=15)
            previews[i].draw(screen, preview_pos=(rect.centerx, rect.y + 40))
            if i == sel: pygame.draw.rect(screen, m[1], rect, 4, border_radius=15)
            name_t = subfont.render(m[0], True, (255,255,255) if i == sel else (150, 150, 150))
            screen.blit(name_t, (x_pos + (110 - name_t.get_width())//2, 370))
        
        instr = subfont.render("USE 'A' / 'D' TO NAVIGATE  |  PRESS 'J' TO CONFIRM", True, (255, 255, 255))
        screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 440))

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_d: sel = (sel + 1) % len(MODELS)
                if e.key == pygame.K_a: sel = (sel - 1) % len(MODELS)
                if e.key == pygame.K_j: return MODELS[sel]
        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(FPS)

# --- MAIN ASYNC ENGINE ---
async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Assassin Battle - AI Project")
    clock = pygame.time.Clock()
    
    # Use 'await' for the menu screens
    await welcome_screen(screen, clock)
    diff_val = await difficulty_menu(screen, clock)
    player_data = await character_menu(screen, clock)
    
    player = Fighter(200, 300, player_data, "PLAYER", 1)
    ai_bot = Fighter(750, 300, ("BOSS", (150, 0, 0), (30, 0, 0), "spiky"), "BOSS", -1, is_villain=True)
    
    history, last_p = {}, "IDLE"
    font = pygame.font.SysFont("Arial", 18, bold=True)
    ui_font = pygame.font.SysFont("Impact", 24)
    big_f = pygame.font.SysFont("Impact", 80)
    over = False

    while True:
        screen.fill((5, 5, 10))
        pygame.draw.rect(screen, (25, 25, 30), (0, FLOOR_Y, WIDTH, 50))
        pygame.draw.line(screen, player.color, (0, FLOOR_Y), (WIDTH, FLOOR_Y), 3)
        
        ctrls = ["A/D: Move", "W: Jump", "J: Punch", "L: Kick", "I: Block", "SHIFT+R: Reset"]
        for i, t in enumerate(ctrls): screen.blit(font.render(t, True, (120, 120, 140)), (20, 100 + i*22))

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and over:
                ks = pygame.key.get_pressed()
                if (ks[pygame.K_LSHIFT] or ks[pygame.K_RSHIFT]) and ks[pygame.K_r]: 
                    await main() # Restart
                    return

        if not over:
            ks = pygame.key.get_pressed()
            p_dx, p_m = 0, "IDLE"
            player.is_blocking = ks[pygame.K_i]
            if not player.is_blocking:
                if ks[pygame.K_a]: p_dx = -7; player.direction = -1
                if ks[pygame.K_d]: p_dx = 7; player.direction = 1
                if ks[pygame.K_w] and not player.is_jumping: player.velocity_y = -26; player.is_jumping = True; p_m="JUMP"
                if ks[pygame.K_j] and player.attack_timer == 0: player.is_punching=True; player.attack_timer=12; p_m="PUNCH"
                if ks[pygame.K_l] and player.attack_timer == 0: player.is_kicking=True; player.attack_timer=18; p_m="KICK"
            player.move(p_dx, 0)
            if p_m != "IDLE": history[(last_p, p_m)] = history.get((last_p, p_m), 0) + 1; last_p = p_m

            # AI logic
            ai_dx = 0
            weights = [history.get((last_p, m), 0) for m in ["PUNCH", "KICK"]]
            if sum(weights) > 0 and random.random() < diff_val: ai_bot.is_blocking = True
            else:
                ai_bot.is_blocking = False
                dist = abs(ai_bot.rect.x - player.rect.x)
                if dist > 140:
                    ai_dx = -5 if ai_bot.rect.x > player.rect.x else 5
                    if diff_val > 0.8: ai_dx *= 1.3
                    ai_bot.direction = -1 if ai_dx < 0 else 1
                elif ai_bot.attack_timer == 0:
                    chance = 0.03 if diff_val < 0.4 else 0.08
                    if random.random() < chance:
                        if random.random() > 0.5: ai_bot.is_punching, ai_bot.attack_timer = True, 12
                        else: ai_bot.is_kicking, ai_bot.attack_timer = True, 18
            ai_bot.move(ai_dx, 0)

            for att, tar in [(player, ai_bot), (ai_bot, player)]:
                if att.attack_timer > 0:
                    att.attack_timer -= 1
                    reach = 95 if att.is_kicking else 70
                    if att.rect.inflate(reach, 0).colliderect(tar.rect) and not tar.is_blocking:
                        tar.health -= 1.5; tar.hurt_timer = 5; tar.rect.x += 10 * att.direction
                else: att.is_punching = att.is_kicking = False

            if player.health <= 0: player.alive = False; over = True; ai_bot.is_winner = True
            if ai_bot.health <= 0: ai_bot.alive = False; over = True; player.is_winner = True

        for f, x_b, flip in [(player, 50, False), (ai_bot, 630, True)]:
            pygame.draw.rect(screen, (30, 30, 35), (x_b, 40, 320, 30), border_radius=10)
            w_h = (max(0, f.health)/100)*320
            pygame.draw.rect(screen, f.color if not f.is_villain else (200, 0, 0), (x_b + (320-w_h) if flip else x_b, 40, w_h, 30), border_radius=10)
            screen.blit(ui_font.render(f"{f.name}: {int(f.health)}%", True, (255,255,255)), (x_b+10 if not flip else x_b+180, 42))

        player.draw(screen); ai_bot.draw(screen)
        if over: screen.blit(big_f.render("VICTORY" if player.alive else "DEFEATED", True, (255,255,255)), (WIDTH//2-160, HEIGHT//2-60))
        
        pygame.display.flip()
        await asyncio.sleep(0) # IMPORTANT: Required for web browser loop
        clock.tick(FPS)

if __name__ == "__main__":
    asyncio.run(main())