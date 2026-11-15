import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 440
TILE_SIZE = 20
FPS = 60

# Define Colors (RGB)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PINK = (255, 182, 193)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WALL_BLUE = (33, 33, 255)
DOT_COLOR = (255, 183, 174)
POWER_PELLET_COLOR = (255, 255, 255)
FRIGHTENED_COLOR = (30, 144, 255)
WHITE = (255, 255, 255)

# Template Map Layout
INITIAL_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,3,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,3,1],
    [1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1],
    [1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,0,1,1,1,1,1,1,0,1,2,1,1,2,1],
    [1,2,2,2,2,1,0,0,0,1,1,0,0,0,1,2,2,2,2,1],
    [1,1,1,1,2,1,1,1,0,1,1,0,1,1,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,0,0,0,0,0,0,0,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,1,1,0,0,1,1,0,1,2,1,1,1,1],
    [1,1,1,1,2,0,0,1,0,0,0,0,1,0,0,2,1,1,1,1],
    [1,1,1,1,2,1,0,1,1,1,1,1,1,0,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,0,0,0,0,0,0,0,1,2,1,1,1,1],
    [1,2,2,2,2,2,2,1,1,1,1,1,1,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1],
    [1,3,2,1,2,2,2,2,2,0,0,2,2,2,2,2,1,2,3,1],
    [1,1,2,1,2,1,2,1,1,1,1,1,1,2,1,2,1,2,1,1],
    [1,2,2,2,2,1,2,2,2,1,1,2,2,2,1,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]


class Player:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, 16, 16)
        self.speed = 2
        self.direction = (2, 0)  # Default facing right
        self.mouth_anim = 0

    def reset_position(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.direction = (2, 0)

    def handle_movement(self, keys, world_map):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        elif keys[pygame.K_RIGHT]:
            dx = self.speed

        self.rect.x += dx
        if self._check_collision(self.rect, world_map):
            self.rect.x -= dx

        if keys[pygame.K_UP]:
            dy = -self.speed
        elif keys[pygame.K_DOWN]:
            dy = self.speed

        self.rect.y += dy
        if self._check_collision(self.rect, world_map):
            self.rect.y -= dy

        if dx != 0 or dy != 0:
            self.direction = (dx, dy)
            self.mouth_anim = (self.mouth_anim + 1) % 20

    def _check_collision(self, rect, world_map):
        for row_idx, row in enumerate(world_map):
            for col_idx, tile in enumerate(row):
                if tile == 1:
                    wall_rect = pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if rect.colliderect(wall_rect):
                        return True
        return False

    def draw(self, screen):
        center = (self.rect.centerx, self.rect.centery)
        radius = TILE_SIZE // 2 - 2
        
        # Draw base yellow circle for Pac-Man
        pygame.draw.circle(screen, YELLOW, center, radius)

        # Draw animated mouth wedge based on direction
        if self.mouth_anim < 10:
            angle = 0
            if self.direction == (-self.speed, 0):
                angle = math.pi
            elif self.direction == (0, -self.speed):
                angle = math.pi / 2
            elif self.direction == (0, self.speed):
                angle = 3 * math.pi / 2

            jaw_spread = 0.5
            p1 = center
            p2 = (center[0] + radius * math.cos(angle - jaw_spread), center[1] - radius * math.sin(angle - jaw_spread))
            p3 = (center[0] + radius * math.cos(angle + jaw_spread), center[1] - radius * math.sin(angle + jaw_spread))
            pygame.draw.polygon(screen, BLACK, [p1, p2, p3])


class Ghost:
    def __init__(self, x, y, color, personality, scatter_corner):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, 16, 16)
        self.color = color
        self.personality = personality  # "blinky", "pinky", "inky", "clyde"
        self.scatter_corner = scatter_corner  # (col, row)
        self.speed = 2
        self.direction = (0, -self.speed)
        self.frightened = False

    def reset_position(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.direction = (0, -self.speed)
        self.frightened = False

    def update(self, world_map, player_rect, player_direction, global_mode, blinky_rect):
        if self.rect.x % TILE_SIZE == 0 and self.rect.y % TILE_SIZE == 0:
            possible_directions = [(0, -self.speed), (0, self.speed), (-self.speed, 0), (self.speed, 0)]
            valid_moves = []

            for dx, dy in possible_directions:
                # Prevent immediate 180-degree reversals unless necessary
                if (dx == -self.direction[0] and dy == -self.direction[1]) and len(possible_directions) > 1:
                    continue

                test_rect = self.rect.copy()
                test_rect.x += dx
                test_rect.y += dy
                
                if not self._check_collision(test_rect, world_map):
                    valid_moves.append((dx, dy))

            if not valid_moves:
                for dx, dy in possible_directions:
                    test_rect = self.rect.copy()
                    test_rect.x += dx
                    test_rect.y += dy
                    if not self._check_collision(test_rect, world_map):
                        valid_moves.append((dx, dy))

            if not valid_moves:
                valid_moves.append((-self.direction[0], -self.direction[1]))

            if valid_moves:
                if self.frightened:
                    self.direction = random.choice(valid_moves)
                else:
                    target = self._get_target_tile(
                        player_rect, player_direction, blinky_rect, global_mode
                    )
                    best_move = valid_moves[0]
                    min_dist = float('inf')
                    
                    for dx, dy in valid_moves:
                        test_rect = self.rect.copy()
                        test_rect.x += dx
                        test_rect.y += dy
                        target_x = target[0] * TILE_SIZE + TILE_SIZE // 2
                        target_y = target[1] * TILE_SIZE + TILE_SIZE // 2
                        dist = math.hypot(
                            test_rect.centerx - target_x,
                            test_rect.centery - target_y,
                        )
                        if dist < min_dist:
                            min_dist = dist
                            best_move = (dx, dy)
                    self.direction = best_move

        self.rect.x += self.direction[0]
        self.rect.y += self.direction[1]

    def _get_target_tile(self, player_rect, player_direction, blinky_rect, global_mode):
        p_col = player_rect.centerx // TILE_SIZE
        p_row = player_rect.centery // TILE_SIZE

        if global_mode == "SCATTER" or self.frightened:
            return self.scatter_corner

        dx, dy = player_direction
        if abs(dx) >= abs(dy) and dx:
            dx, dy = (1 if dx > 0 else -1), 0
        elif dy:
            dx, dy = 0, (1 if dy > 0 else -1)
        else:
            dx, dy = 1, 0

        # CHASE mode personalities
        if self.personality == "blinky":
            return (p_col, p_row)
        elif self.personality == "pinky":
            return (p_col + 4 * dx, p_row + 4 * dy)
        elif self.personality == "inky":
            pivot_col = p_col + 2 * dx
            pivot_row = p_row + 2 * dy
            blinky_col = blinky_rect.centerx // TILE_SIZE
            blinky_row = blinky_rect.centery // TILE_SIZE
            return (2 * pivot_col - blinky_col, 2 * pivot_row - blinky_row)
        elif self.personality == "clyde":
            dist = math.hypot(self.rect.centerx - player_rect.centerx, self.rect.centery - player_rect.centery)
            if dist > 8 * TILE_SIZE:
                return (p_col, p_row)
            else:
                return self.scatter_corner
        return (p_col, p_row)

    def _check_collision(self, rect, world_map):
        for row_idx, row in enumerate(world_map):
            for col_idx, tile in enumerate(row):
                if tile == 1:
                    wall_rect = pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if rect.colliderect(wall_rect):
                        return True
        return False

    def draw(self, screen):
        current_color = FRIGHTENED_COLOR if self.frightened else self.color
        rx, ry, rw, rh = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        
        # Ghost head (semicircle) & body rect
        pygame.draw.rect(screen, current_color, (rx, ry + 4, rw, rh - 4), border_top_left_radius=8, border_top_right_radius=8)
        
        # Feet skirt dips
        pygame.draw.circle(screen, BLACK, (rx + 4, ry + rh - 2), 2)
        pygame.draw.circle(screen, BLACK, (rx + 12, ry + rh - 2), 2)

        # Eyes
        eye_color = WHITE if not self.frightened else RED
        pupil_color = BLUE if not self.frightened else WHITE
        
        ex_offset, ey_offset = 0, 0
        if self.direction[0] > 0: ex_offset = 2
        elif self.direction[0] < 0: ex_offset = -2
        elif self.direction[1] > 0: ey_offset = 2
        elif self.direction[1] < 0: ey_offset = -2

        pygame.draw.circle(screen, eye_color, (rx + 4, ry + 6), 3)
        pygame.draw.circle(screen, eye_color, (rx + 12, ry + 6), 3)
        pygame.draw.circle(screen, pupil_color, (rx + 4 + ex_offset, ry + 6 + ey_offset), 1)
        pygame.draw.circle(screen, pupil_color, (rx + 12 + ex_offset, ry + 6 + ey_offset), 1)


class GameManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Map-Pac Game - Vector Graphics & Ghost AI")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 40)
        
        self.mode_timer = 0
        self.global_mode = "SCATTER"

        self.player = Player(40, 20)
        self.ghosts = [
            Ghost(180, 180, RED, "blinky", (18, 1)),
            Ghost(200, 180, PINK, "pinky", (1, 1)),
            Ghost(180, 200, CYAN, "inky", (18, 18)),
            Ghost(200, 200, ORANGE, "clyde", (1, 18))
        ]
        self.reset_game()

        self.static_background = pygame.Surface((WIDTH, HEIGHT))
        self.static_background.fill(BLACK)
        self._bake_static_walls()

    def reset_game(self):
        self.world_map = [row[:] for row in INITIAL_MAP]
        self.score = 0
        self.lives = 3
        self.frightened_timer = 0
        self.game_state = "PLAYING"
        self.mode_timer = 0
        self.global_mode = "SCATTER"

        self.ghosts = [
            Ghost(180, 180, RED, "blinky", (18, 1)),
            Ghost(200, 180, PINK, "pinky", (1, 1)),
            Ghost(180, 200, CYAN, "inky", (18, 18)),
            Ghost(200, 200, ORANGE, "clyde", (1, 18))
        ]
        self.remaining_dots = 0
        for row in self.world_map:
            for tile in row:
                if tile in (2, 3):
                    self.remaining_dots += 1

        self.player.reset_position()
        for ghost in self.ghosts:
            ghost.reset_position()

    def _bake_static_walls(self):
        for row_idx, row in enumerate(self.world_map):
            for col_idx, tile in enumerate(row):
                if tile == 1:
                    wall_rect = pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(self.static_background, WALL_BLUE, wall_rect)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_state in ("GAME_OVER", "VICTORY"):
                    self.reset_game()

    def update(self):
        if self.game_state != "PLAYING":
            return

        # Mode cycling timer (Scatter vs Chase)
        self.mode_timer += 1
        if self.global_mode == "SCATTER" and self.mode_timer > 420:  # ~7 seconds
            self.global_mode = "CHASE"
            self.mode_timer = 0
        elif self.global_mode == "CHASE" and self.mode_timer > 1200:  # ~20 seconds
            self.global_mode = "SCATTER"
            self.mode_timer = 0

        keys = pygame.key.get_pressed()
        self.player.handle_movement(keys, self.world_map)
        
        col = self.player.rect.centerx // TILE_SIZE
        row = self.player.rect.centery // TILE_SIZE
        if 0 <= row < len(self.world_map) and 0 <= col < len(self.world_map[0]):
            tile_value = self.world_map[row][col]
            if tile_value == 2:
                self.world_map[row][col] = 0
                self.score += 10
                self.remaining_dots -= 1
            elif tile_value == 3:
                self.world_map[row][col] = 0
                self.score += 50
                self.remaining_dots -= 1
                self.frightened_timer = 420
                for ghost in self.ghosts:
                    ghost.frightened = True
                    
        if self.remaining_dots <= 0:
            self.game_state = "VICTORY"

        if self.frightened_timer > 0:
            self.frightened_timer -= 1
            if self.frightened_timer == 0:
                for ghost in self.ghosts:
                    ghost.frightened = False

        blinky_rect = self.ghosts[0].rect
        for ghost in self.ghosts:
            ghost.update(
                self.world_map,
                self.player.rect,
                self.player.direction,
                self.global_mode,
                blinky_rect,
            )

        for ghost in self.ghosts:
            if self.player.rect.colliderect(ghost.rect):
                if ghost.frightened:
                    self.score += 200
                    ghost.reset_position()
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_state = "GAME_OVER"
                    else:
                        self.player.reset_position()
                        for g in self.ghosts:
                            g.reset_position()

    def render(self):
        self.screen.blit(self.static_background, (0, 0))

        for row_idx, row in enumerate(self.world_map):
            for col_idx, tile in enumerate(row):
                center_pos = (col_idx * TILE_SIZE + TILE_SIZE // 2, row_idx * TILE_SIZE + TILE_SIZE // 2)
                if tile == 2:
                    pygame.draw.circle(self.screen, DOT_COLOR, center_pos, 3)
                elif tile == 3:
                    pygame.draw.circle(self.screen, POWER_PELLET_COLOR, center_pos, 6)

        self.player.draw(self.screen)
        for ghost in self.ghosts:
            ghost.draw(self.screen)

        score_surface = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_surface = self.font.render(f"Lives: {self.lives}", True, YELLOW)
        
        self.screen.blit(score_surface, (10, 412))
        self.screen.blit(lives_surface, (310, 412))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            
            go_text = self.big_font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press 'R' to Restart", True, WHITE)
            self.screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, 160))
            self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 220))

        elif self.game_state == "VICTORY":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            
            vic_text = self.big_font.render("VICTORY!", True, GREEN)
            restart_text = self.font.render("Press 'R' to Play Again", True, WHITE)
            self.screen.blit(vic_text, (WIDTH // 2 - vic_text.get_width() // 2, 160))
            self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 220))

        pygame.display.update()


if __name__ == "__main__":
    game = GameManager()
    game.run()