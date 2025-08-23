import pygame, csv
from pygame import Vector2
import classes
import ui.menu

def draw_level(world: int, level: int) -> None:
    #level_file = f"{world}/{level}.csv"
    pass

def draw_menu(renderer: classes.Renderer, menu_page: int):
    level_array: list[list[str]] = []

    menu_file_name: str = "menu.csv"
    menu_file = open(menu_file_name, "r")
    reader = csv.reader(menu_file)

    # Append rows of csv file to array
    for row in reader:
        level_array.append(row)

    menu_file.close()

    # Draw menu
    # Positions to place blocks
    x: int = 0
    x_array: int = 0
    y: int = 0
    y_array: int = 0

    for row in level_array:
        for block in row:
            if block == "G": # Grass Block
                # Check if grass block is underneath another grass block
                if level_array[y_array - 1][x_array] == "G":
                    new_block = classes.PhysicsObject("assets/images/level_blocks/dirt.png")
                else:
                    new_block = classes.PhysicsObject("assets/images/level_blocks/grass.png")
                new_block.load()
                new_block.anchored = True
                new_block.position = Vector2(x, y)
                new_block.size = Vector2(45, 45)
                renderer.objects.append(new_block)

            elif block == "PLR":
                #player_spawn = Vector2(x, y)
                pass
            x += 45 # Add 45 to x value to move onto next block
            x_array += 1

        x = 0 # Reset x value for a new row
        x_array = 0
        y += 45 # Add 45 onto y value for new row
        y_array += 1
    
    # Draw buttons depending on page
    renderer.objects.append(ui.menu.title)


player: classes.Player = classes.Player("assets/images/player/player.png")
player_spawn = Vector2(50, 20)

def main() -> None:
    
    # PYGAME SETUP
    pygame.init()
    renderer = classes.Renderer()
    clock = pygame.time.Clock()
    running: bool = True

    player.load()
    renderer.objects.append(player)

    # GAME VARIABLES
    menu_active: bool = True
    menu_page: int = 1
    

    # GAME LOOP
    while running:
        delta_time = clock.tick()
        renderer.screen.fill((215, 252, 252)) # Default background colour
        key_pressed = pygame.key.get_pressed()

        if key_pressed[pygame.K_w]:
            pass
        if key_pressed[pygame.K_s]:
            pass
        if key_pressed[pygame.K_a]:
            player.move(Vector2(-0.3, 0) * delta_time) 
        if key_pressed[pygame.K_d]:
            player.move(Vector2(0.3, 0) * delta_time)

        if key_pressed[pygame.K_SPACE]:
            player.move(Vector2(0, -0.5) * delta_time)

        player.update(renderer.objects)
        # Detect if the pygame console has been quit.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if menu_active:
                # MENU LOGIC
                draw_menu(renderer, menu_page)

        
        renderer.update()
        pygame.display.flip()

if __name__ == "__main__":
    main()