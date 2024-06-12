import pygame
import os
from leaderboard import Result, Player, Game, Score

# Load pygame
pygame.init()
Game.initialize_database()

# Load mixer mode for music
pygame.mixer.init()

# Set resolution
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set Window Name
pygame.display.set_caption('Mû.F.O')

# Set framerate
clock = pygame.time.Clock()
FPS = 60

# Define player action variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False

scroll_thresh = SCREEN_WIDTH // 2
screen_scroll = [0, 0]
bg_scroll = [0, 0] 

# Define global variable for Score
current_score = Score(None, None)

# Load sound effects
navigation_sound = pygame.mixer.Sound("assets/sounds/effects/navigation.mp3")
selected_sound = pygame.mixer.Sound("assets/sounds/effects/selected.mp3")

# Global game state
game_active = False
paused = False

# Load background frames for title screen
current_frame = 0
background_frames = []
frame_folder = "assets/frames"
for filename in sorted(os.listdir(frame_folder)):
    if filename.endswith(".png"):
        frame = pygame.image.load(os.path.join(frame_folder, filename))
        background_frames.append(frame)
print(f"Loaded {len(background_frames)} frames.")

# Load game font
font_path = "assets/fonts/press-start-2p.ttf"
font_size = 24
custom_font = pygame.font.Font(font_path, font_size)

# Create Button
class Button():
    def __init__(self, text, x, y, width, height, color, selected_color, function):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.selected_color = selected_color
        self.function = function
        self.font = pygame.font.Font(font_path, 20)
        self.selected = False

    def draw(self, screen):
        color = self.selected_color if self.selected else self.color
        text_surf = self.font.render(self.text, True, color)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        screen.blit(text_surf, text_rect)

    def click(self):
        selected_sound.play()
        self.function()

# Create Character
class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.flip = False
        img_path = f'assets/img/{self.char_type}/idle/0.png'
        img = pygame.image.load(img_path)
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right, moving_up, moving_down, threshold_x, threshold_y):
        screen_scroll = [0, 0]
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        if moving_up:
            dy = -self.speed
        if moving_down:
            dy = self.speed

        self.rect.x += dx
        self.rect.y += dy

        # Check horizontal threshold
        if self.rect.right > SCREEN_WIDTH - threshold_x:
            self.rect.right = SCREEN_WIDTH - threshold_x
            screen_scroll[0] = dx
        elif self.rect.left < threshold_x:
            self.rect.left = threshold_x
            screen_scroll[0] = dx

        # Check vertical threshold
        if self.rect.bottom > SCREEN_HEIGHT - threshold_y:
            self.rect.bottom = SCREEN_HEIGHT - threshold_y
            screen_scroll[1] = dy
        elif self.rect.top < threshold_y:
            self.rect.top = threshold_y
            screen_scroll[1] = dy

        return screen_scroll

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

player = Character('player', SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 2, 5)
target = Character('target', 800, 450, .15, 5)

# Define the threshold area
threshold_x = SCREEN_WIDTH // 3 
threshold_y = SCREEN_HEIGHT // 4

def draw_title_bg(background_frames):
    global current_frame
    screen.blit(background_frames[current_frame], (0, 0))
    current_frame = (current_frame + 1) % len(background_frames)

def draw_game_bg(game_bg):
    # scaled_bg = pygame.transform.scale(game_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(game_bg, (0, 0))

def start_game():
    global game_active, paused
    game_active = True
    paused = False
    # pygame.mixer.music.stop()

def show_leaderboard():
    global game_active
    game_active = True
    leaderboard_data = Result.get_leaderboard()
    print(f"Leaderboard data to display: {leaderboard_data}")

    colors = [
        (192, 192, 192), (192, 192, 192),  # Silver
        (255, 165, 0), (255, 165, 0),      # Orange
        (0, 0, 255), (0, 0, 255),          # Blue
        (0, 128, 0), (0, 128, 0),          # Green
        (255, 0, 0), (255, 0, 0)           # Red
    ]

    while game_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_active = False  # Exit leaderboard screen on ESC key

        draw_title_bg(background_frames)  # Use the same background animation as the title screen
        title = custom_font.render("Leaderboard", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        # Display column headers with increased spacing
        name_header = custom_font.render("Name", True, (255, 255, 255))
        score_header = custom_font.render("Score", True, (255, 255, 255))
        header_x = SCREEN_WIDTH // 2 - (name_header.get_width() + score_header.get_width()) // 2
        screen.blit(name_header, (header_x, 150))
        screen.blit(score_header, (header_x + name_header.get_width() + 100, 150))  # Adjusting spacing

        y_offset = 200
        rank_x = SCREEN_WIDTH // 2 - 200

        # Display placeholders for ranks in the first column
        for i in range(10):
            rank_text = custom_font.render(f"{i + 1}", True, colors[i])
            screen.blit(rank_text, (rank_x, y_offset + i * 40))

        # Display actual leaderboard data with increased spacing
        for i, (username, game_title, score) in enumerate(leaderboard_data[:10]):
            username_text = custom_font.render(f"{username}", True, colors[i])
            screen.blit(username_text, (header_x, y_offset + i * 40))

            score_text = custom_font.render(f"{score}", True, colors[i])
            screen.blit(score_text, (header_x + name_header.get_width() + 100, y_offset + i * 40))  # Adjusting spacing

        pygame.display.update()
        clock.tick(FPS)

def pause_screen():
    global paused, current_frame

    buttons = [
        Button('Resume', SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, 200, 50, (100, 100, 100), (255, 255, 255), resume_game),
        Button('Quit', SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, 200, 50, (100, 100, 100), (255, 255, 255), quit_game)
    ]

    selected_button = 0
    buttons[selected_button].selected = True

    while paused:
        draw_title_bg(background_frames)  # Use the same background animation as the title screen

        for button in buttons:
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    buttons[selected_button].selected = False
                    selected_button = (selected_button - 1) % len(buttons)
                    buttons[selected_button].selected = True
                    navigation_sound.play()
                if event.key == pygame.K_DOWN:
                    buttons[selected_button].selected = False
                    selected_button = (selected_button + 1) % len(buttons)
                    buttons[selected_button].selected = True
                    navigation_sound.play()
                if event.key == pygame.K_SPACE:
                    buttons[selected_button].click()
        
        pygame.display.update()
        clock.tick(FPS)

def quit_game():
    pygame.quit()
    exit()

def resume_game():
    global paused
    paused = False

def title_screen():
    
    pygame.mixer.music.load("assets/sounds/music/title_screen.mp3")
    pygame.mixer.music.play(-1)

    buttons = [
        Button('Start', SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100, 200, 50, (100, 100, 100), (255, 255, 255), start_game),
        Button('Leaderboard', SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 200, 50, (100, 100, 100), (255, 255, 255), show_leaderboard),
        Button('Quit', SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, 200, 50, (100, 100, 100), (255, 255, 255), quit_game)
    ]

    selected_button = 0
    buttons[selected_button].selected = True

    while not game_active:
        draw_title_bg(background_frames)

        for button in buttons:
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    buttons[selected_button].selected = False
                    selected_button = (selected_button - 1) % len(buttons)
                    buttons[selected_button].selected = True
                    navigation_sound.play()
                if event.key == pygame.K_DOWN:
                    buttons[selected_button].selected = False
                    selected_button = (selected_button + 1) % len(buttons)
                    buttons[selected_button].selected = True
                    navigation_sound.play()
                if event.key == pygame.K_SPACE:
                    buttons[selected_button].click()
                    selected_sound.play()
        
        pygame.display.update()
        clock.tick(FPS)

def run_game():
    global game_active, paused, moving_left, moving_right, moving_up, moving_down, screen_scroll, bg_scroll, current_score
    
    # Load game background image for active play
    game_bg = pygame.image.load("assets/img/map/map-0.png")
    bg_width = game_bg.get_width()
    bg_height = game_bg.get_height()

    while game_active:
        clock.tick(FPS)

        # Draw the game background
        screen.blit(game_bg, (bg_scroll[0], bg_scroll[1]))

        player.draw()

        screen_scroll = player.move(moving_left, moving_right, moving_up, moving_down, threshold_x, threshold_y)
        bg_scroll[0] -= screen_scroll[0]
        bg_scroll[1] -= screen_scroll[1]

        # Background scrolls within bounds
        bg_scroll[0] = max(-(bg_width - SCREEN_WIDTH), min(0, bg_scroll[0]))
        bg_scroll[1] = max(-(bg_height - SCREEN_HEIGHT), min(0, bg_scroll[1]))

        if player.rect.colliderect(target.rect):
            current_score.update_score(target_points=10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_active = False
                current_score.save_score()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_w:
                    moving_up = True
                if event.key == pygame.K_s:
                    moving_down = True
                if event.key == pygame.K_ESCAPE:
                    paused = True
                    pause_screen()
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                if event.key == pygame.K_w:
                    moving_up = False
                if event.key == pygame.K_s:
                    moving_down = False

        pygame.display.update()

    current_score.save_score()
    pygame.quit()
    exit()

def main():
    global game_active
    
    while True:
        if not game_active:
            title_screen()
        else:
            run_game()

main()