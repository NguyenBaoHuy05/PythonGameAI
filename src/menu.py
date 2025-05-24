import pygame
import sys
from button import Button

def get_font(size):
    try:
        return pygame.font.Font("../assets/font.ttf", size)
    except:
        return pygame.font.SysFont("arial", size)

def pause_menu(screen, font):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    title = font.render("PAUSED", True, (255, 255, 0))
    screen.blit(title, title.get_rect(center=(screen.get_width()//2, screen.get_height()//3)))

    resume_text = font.render("ESC: Resume", True, (255, 255, 255))
    screen.blit(resume_text, resume_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2)))

    menu_text = font.render("M: Main Menu", True, (255, 255, 255))
    screen.blit(menu_text, menu_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50)))

    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"
                elif event.key == pygame.K_m:
                    return "menu"

def game_over_menu(screen, font, score):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    title = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(title, title.get_rect(center=(screen.get_width()//2, screen.get_height()//3)))

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, score_text.get_rect(center=(screen.get_width()//2, screen.get_height()//3 + 50)))

    retry_text = font.render("R: Retry", True, (255, 255, 255))
    screen.blit(retry_text, retry_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2)))

    menu_text = font.render("M: Main Menu", True, (255, 255, 255))
    screen.blit(menu_text, menu_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50)))

    quit_text = font.render("Q: Quit", True, (255, 255, 255))
    screen.blit(quit_text, quit_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 100)))

    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"
                elif event.key == pygame.K_m:
                    return "menu"
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def victory_menu(screen, font, score):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    title = font.render("YOU WIN!", True, (255, 255, 0))
    screen.blit(title, title.get_rect(center=(screen.get_width()//2, screen.get_height()//3)))

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, score_text.get_rect(center=(screen.get_width()//2, screen.get_height()//3 + 50)))

    next_text = font.render("N: Next Level", True, (255, 255, 255))
    screen.blit(next_text, next_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2)))

    menu_text = font.render("M: Main Menu", True, (255, 255, 255))
    screen.blit(menu_text, menu_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50)))

    quit_text = font.render("Q: Quit", True, (255, 255, 255))
    screen.blit(quit_text, quit_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 100)))

    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    return "next"
                elif event.key == pygame.K_m:
                    return "menu"
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def show_controls(screen, from_main_menu=False):
    """Hiển thị màn hình điều khiển"""
    # Lưu trạng thái màn hình trước đó nếu không phải từ main menu
    if not from_main_menu:
        temp_surface = screen.copy()
    
    screen.fill((0, 0, 0))
    
    font = get_font(30)
    title = font.render("GAME CONTROLS", True, (255, 255, 0))
    screen.blit(title, title.get_rect(center=(screen.get_width()//2, 100)))

    controls = [
        "Arrow Keys: Move Pacman",
        "ESC: Pause Game",
        "M: Back to main menu (paused/ game over)",
        "R: Play Again (game over)",
        "Q: Quit Game (game over)",
        "N: Next Level (win)"
    ]
    
    # Hiển thị từng dòng điều khiển
    for i, control in enumerate(controls):
        text = font.render(control, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(screen.get_width()//2, 180 + i*40)))
    
    # Nút Back
    back_button = Button(
        image=None,
        pos=(screen.get_width()//2, 450),
        text_input="BACK",
        font=get_font(40),
        base_color="White",
        hovering_color="Green"
    )
    
    mouse_pos = pygame.mouse.get_pos()
    back_button.changeColor(mouse_pos)
    back_button.update(screen)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        mouse_pos = pygame.mouse.get_pos()
        back_button.changeColor(mouse_pos)
        back_button.update(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.checkForInput(mouse_pos):
                    waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
        
        pygame.display.flip()
    
    # Nếu gọi từ main menu thì không cần khôi phục màn hình trước đó
    if not from_main_menu:
        screen.blit(temp_surface, (0, 0))

def main_menu(screen):
    try:
        BG = pygame.image.load("../assets/menu/background.png")
        BG = pygame.transform.scale(BG, (screen.get_width(), screen.get_height()))
    except:
        BG = None
    
    font = get_font(50)
    title = font.render("PACMAN", True, (255, 255, 0))
    
    # Tạo các nút menu
    play_button = Button(
        image=None,
        pos=(screen.get_width()//2, 250),
        text_input="PLAY",
        font=get_font(45),
        base_color="White",
        hovering_color="Green"
    )
    
    controls_button = Button( 
        image=None,
        pos=(screen.get_width()//2, 350),
        text_input="CONTROLS",
        font=get_font(45),
        base_color="White",
        hovering_color="Green"
    )
    
    quit_button = Button(
        image=None,
        pos=(screen.get_width()//2, 450),
        text_input="QUIT",
        font=get_font(45),
        base_color="White",
        hovering_color="Green"
    )
    
    while True:
        if BG:
            screen.blit(BG, (0, 0))
        else:
            screen.fill((0, 0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(title, title.get_rect(center=(screen.get_width()//2, 100)))
        
        for button in [play_button, controls_button, quit_button]: 
            button.changeColor(mouse_pos)
            button.update(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(mouse_pos):
                    return "play"
                elif controls_button.checkForInput(mouse_pos): 
                    show_controls(screen, from_main_menu=True)
                    # Vẽ lại menu sau khi đóng controls
                    if BG:
                        screen.blit(BG, (0, 0))
                    else:
                        screen.fill((0, 0, 0))
                    screen.blit(title, title.get_rect(center=(screen.get_width()//2, 100)))
                    mouse_pos = pygame.mouse.get_pos()
                    for button in [play_button, controls_button, quit_button]:
                        button.changeColor(mouse_pos)
                        button.update(screen)
                    pygame.display.flip()
                elif quit_button.checkForInput(mouse_pos):
                    pygame.quit()
                    sys.exit()
        
        pygame.display.flip()