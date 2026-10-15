import pygame
from game.maze import generate_maze, CELL
from game.entities import Player, Enemy

COLS, ROWS = 13, 11
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 50
FPS = 60


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Chase")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont("monospace", 38, bold=True)
        self.reset()

    def reset(self):
        self.walls = generate_maze(COLS, ROWS)
        self.player = Player(0, 0)

        # Task 1: Three independent enemies
        self.enemies = [
            Enemy(ROWS - 1, COLS - 1),
            Enemy(0, COLS - 1),
            Enemy(ROWS - 1, 0),
        ]

        self.exit_rect = pygame.Rect(
            (COLS // 2) * CELL + 5,
            (ROWS // 2) * CELL + 5,
            CELL - 10,
            CELL - 10,
        )

        self.caught = False
        self.won = False

        # Task 2: Difficulty timer
        self.start_time = pygame.time.get_ticks()
        self.speed_tier = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()

        return True

    def update(self):
        if self.caught or self.won:
            return

        # Task 2: Increase enemy speed every 15 seconds
        elapsed_seconds = (
            pygame.time.get_ticks() - self.start_time
        ) // 1000

        self.speed_tier = elapsed_seconds // 15
        move_interval = max(5, 20 - self.speed_tier * 2)

        for enemy in self.enemies:
            enemy.move_interval = move_interval

        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, ROWS, COLS)

        # Task 1: Each enemy independently uses its update method
        for enemy in self.enemies:
            enemy.update(self.walls, self.player, ROWS, COLS)

            if self.player.rect.colliderect(enemy.rect):
                self.caught = True

        if self.player.rect.colliderect(self.exit_rect):
            self.won = True

    def draw(self):
        self.screen.fill((230, 220, 210))
        wall_color = (50, 40, 60)

        for r in range(ROWS):
            for c in range(COLS):
                x, y = c * CELL, r * CELL
                wall = self.walls[r][c]

                if wall[0]:
                    pygame.draw.line(
                        self.screen, wall_color,
                        (x, y), (x + CELL, y), 3
                    )

                if wall[1]:
                    pygame.draw.line(
                        self.screen, wall_color,
                        (x, y + CELL), (x + CELL, y + CELL), 3
                    )

                if wall[2]:
                    pygame.draw.line(
                        self.screen, wall_color,
                        (x + CELL, y), (x + CELL, y + CELL), 3
                    )

                if wall[3]:
                    pygame.draw.line(
                        self.screen, wall_color,
                        (x, y), (x, y + CELL), 3
                    )

        pygame.draw.rect(
            self.screen,
            (80, 200, 80),
            self.exit_rect,
            border_radius=4,
        )

        exit_label = self.font.render("EXIT", True, (20, 80, 20))
        self.screen.blit(
            exit_label,
            (self.exit_rect.x + 2, self.exit_rect.y + 6),
        )

        self.player.draw(self.screen)

        # Task 1: Draw all enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # HUD
        hud = pygame.Rect(0, ROWS * CELL, WIDTH, 50)
        pygame.draw.rect(self.screen, (30, 30, 50), hud)

        info = self.font.render(
            f"Speed Tier: {self.speed_tier}  R=Restart",
            True,
            (200, 200, 200),
        )
        self.screen.blit(info, (8, ROWS * CELL + 14))

        if self.caught:
            self._overlay("CAUGHT!", (220, 60, 60))

        if self.won:
            self._overlay("ESCAPED!", (80, 220, 80))

        pygame.display.flip()

    def _overlay(self, text, color):
        overlay = pygame.Surface(
            (WIDTH, ROWS * CELL),
            pygame.SRCALPHA,
        )
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        message = self.big_font.render(text, True, color)
        subtitle = self.font.render(
            "Press R to Restart",
            True,
            (200, 200, 200),
        )

        self.screen.blit(
            message,
            (
                WIDTH // 2 - message.get_width() // 2,
                ROWS * CELL // 2 - 30,
            ),
        )

        self.screen.blit(
            subtitle,
            (
                WIDTH // 2 - subtitle.get_width() // 2,
                ROWS * CELL // 2 + 20,
            ),
        )

    def run(self):
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
