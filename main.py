from typing import Any
import pygame, csv, random, time
from pygame import Vector2
import classes
import ui.menu

def create_object(new_object: classes.Sprite, position: Vector2, size: Vector2, renderer: classes.Renderer):
    if not isinstance(new_object, classes.AnimatableSprite): new_object.load()
    new_object.position = position
    new_object.size = size
    renderer.objects.append(new_object)

def draw_level(world: int, level: int, room: int, renderer: classes.Renderer) -> None:
    roomArray: list[list[str]] = []

    # Open the file
    level_file = f"worlds/{world}/l{level}/r{room}.csv"
    file = open(level_file, "r")
    reader = csv.reader(file)
    
    for row in reader:
        roomArray.append(row)

    file.close()
    # Generate level

    x = 0
    y = 0

    additional_objects: list[dict[str, Any]] = []

    for row in roomArray:
        for cell in row:
            objects = cell.split("_")

            if "dg" in objects:
                create_object(classes.Sprite("assets/images/level_blocks/grass/grass-4.png"), Vector2(x, y), Vector2(30, 30), renderer)

            if "g" in objects:
                randomInt = random.randint(1, 12)
                if randomInt >= 6: randomInt = 4
                if randomInt == 5:
                    create_object(classes.Sprite(f"assets/images/level_blocks/plant/plant-{random.randint(1, 3)}.png"), Vector2(x, y), Vector2(30, 30), renderer)
                else:
                    create_object(classes.Sprite(f"assets/images/level_blocks/grass/grass-{randomInt}.png"), Vector2(x, y), Vector2(30, 30), renderer)

                # Additional objects

                if "rk" in objects:
                    create_object(classes.Sprite(f"assets/images/level_blocks/decor/rock-{random.randint(1,2)}.png", "rock", 1, True), Vector2(x, y), Vector2(30, 30), renderer)
                if "smz" in objects:
                    additional_objects.append({"object_class": classes.Small_Zombie({"idle": "assets/images/enemies/zombie/small/idle.png", "walk": "assets/images/enemies/zombie/small/walk.png", "attack": "assets/images/enemies/zombie/small/attack.png"}, {"idle": 4, "walk": 5, "attack": 4}, 32, False, "enemy", 2), "position": Vector2(x, y), "size": Vector2(30, 30), "renderer": renderer})
                if "tr-sm" in objects:
                    additional_objects.append({"object_class": classes.Sprite("assets/images/level_blocks/tree/tree-sm.png", "tree", 1, True), "position": Vector2(x, y), "size": Vector2(30, 60), "renderer": renderer})
                if "tr-lg" in objects:
                    additional_objects.append({"object_class": classes.Sprite("assets/images/level_blocks/tree/tree-lg.png", "tree", 1, True), "position": Vector2(x, y), "size": Vector2(60, 60), "renderer": renderer})
            
            if "cn" in objects:
                additional_objects.append({"object_class": classes.AnimatableSprite({"idle": "assets/images/misc/coins.png"}, {"idle": 5}, 16, False, "coin"), "position": Vector2(x, y), "size": Vector2(25, 25), "renderer": renderer})

            if "fence" in objects:
                additional_objects.append({"object_class": classes.Sprite("assets/images/level_blocks/fences/fence.png", "fence", 1, True), "position": Vector2(x, y), "size": Vector2(30, 30), "renderer": renderer})

            if "exit" in objects:
                additional_objects.append({"object_class": classes.AnimatableSprite({"idle": "assets/images/misc/arrow.png"}, {"idle": 2}, 32, False, "exit"), "position": Vector2(x, y), "size": Vector2(30, 30), "renderer": renderer})

            if "spawn" in objects:
                spawn.set_spawn(Vector2(x, y))   
            
            x += 30 # Add to x value after each block is loaded.
        # Reset x value and add to y value after each row is loaded.
        x = 0
        y += 30
    
    for object in additional_objects:
        create_object(object["object_class"], object["position"], object["size"], object["renderer"]) # type: ignore

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
                    new_block = classes.Sprite("assets/images/level_blocks/dirt.png")
                else:
                    new_block = classes.Sprite("assets/images/level_blocks/grass.png")
                new_block.load()
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

def draw_coins(renderer: classes.Renderer, stats: classes.GameStats):

    coin_symbol = classes.Sprite("assets/images/misc/coin.png")
    coin_symbol.position = Vector2(1150, 710)
    coin_symbol.size = Vector2(25, 25)
    coin_symbol.load()
    coin_symbol.draw(renderer.screen)

    font = pygame.font.Font("assets/fonts/pixel.ttf", 35)
    text = font.render(str(stats.coins), False, (200, 156, 4))
    renderer.screen.blit(text, (1185, 705))

def draw_lives(renderer: classes.Renderer, player: classes.Player):
    x = 20

    if player.lives <= 0:
        font = pygame.font.Font('assets/fonts/pixel.ttf', 20)
        text = font.render('Game Over! Press [SPACE] to restart', False, (0, 0, 0))
        renderer.screen.blit(text, (x,710))
    else:
        for _ in range(player.lives):
            new_life = classes.Sprite("assets/images/misc/icon_heart.png")
            new_life.position = Vector2(x, 710)
            new_life.size = Vector2(25, 25)
            new_life.load()
            new_life.draw(renderer.screen)
            x += 50

def is_colliding(obj1: classes.RenderableObject, obj2: classes.RenderableObject) -> bool:
    return (
        obj1.position.x < obj2.position.x + obj2.size.x and
        obj1.position.x + obj1.size.x > obj2.position.x and
        obj1.position.y < obj2.position.y + obj2.size.y and
        obj1.position.y + obj1.size.y > obj2.position.y
    )

def is_player_colliding(plr: classes.Player, obj2: classes.RenderableObject) -> None:
    if is_player_colliding_left(plr, obj2): 
        plr.position.x = obj2.position.x - plr.size.x - 20
        print("left")
    if is_player_colliding_right(plr, obj2): 
        plr.position.x = obj2.position.x + obj2.size.x + 20
        print("right")
    if is_player_colliding_top(plr, obj2): 
        plr.position.y = obj2.position.y - plr.size.y
        print("top")
    if is_player_colliding_bottom(plr, obj2): 
        plr.position.y = obj2.position.y + obj2.size.y
        print("bottom")

def is_player_colliding_left(obj1: classes.Player, obj2: classes.RenderableObject) -> bool: return obj1.position.x + 20 - 0.2 < obj2.position.x + obj2.size.x and obj1.position.x + 20 > obj2.position.x + obj2.size.x
def is_player_colliding_right(obj1: classes.Player, obj2: classes.RenderableObject) -> bool: return obj1.position.x + obj1.size.x - 20 + 0.2 > obj2.position.x and obj1.position.x + obj1.size.x - 20 < obj2.position.x
def is_player_colliding_top(obj1: classes.Player, obj2: classes.RenderableObject) -> bool: return obj1.position.y - 0.2 < obj2.position.y + obj2.size.y  and obj1.position.y > obj2.position.y + obj2.size.y
def is_player_colliding_bottom(obj1: classes.Player, obj2: classes.RenderableObject) -> bool: return obj1.position.y + obj1.size.y + 0.2 > obj2.position.y  and obj1.position.y + obj1.size.y + 0.2 < obj2.position.y

def get_collisions(renderer: classes.Renderer, player: classes.Player):
    collisions_list: list[classes.RenderableObject] = []

    for object in renderer.objects:
        if is_player_colliding(player, object):
            collisions_list.append(object)

    return collisions_list

player_images = {
    "idle": "assets/images/player/idle.png",
    "walk": "assets/images/player/walk.png",
    "attack": "assets/images/player/attack.png",
    "block": "assets/images/player/block.png",
    "damage": "assets/images/player/damage.png",
    "dead": "assets/images/player/dead.png",
}

player_num_frames = {
    "idle": 5,
    "walk": 8,
    "attack": 6,
    "block": 2,
    "damage": 1,
    "dead": 7
}

stats: classes.GameStats = classes.GameStats(0)
player: classes.Player = classes.Player(player_images, player_num_frames)
spawn: classes.Spawn = classes.Spawn()

def main() -> None:
    
    # PYGAME SETUP
    pygame.init()
    pygame.mixer.init()
    renderer = classes.Renderer()
    clock = pygame.time.Clock()
    running: bool = True

    # GAME VARIABLES
    #menu_active: bool = True
    #menu_page: int = 1

    world = 1
    level = 1
    room = 1
    room_debounce = False

    draw_level(world, level, room, renderer)
    player.position = spawn.position

    cooldown_timer = 0
    dead_time = None

    # GAME LOOP
    while running:
        delta_time = clock.tick()
        renderer.screen.fill((215, 252, 252)) # Default background colour

        player.change_animation("idle")

        if cooldown_timer >= 100:
            cooldown_timer = 0
            player.cooldown = False

        draw_lives(renderer, player)
        draw_coins(renderer, stats)

        # Detect if the pygame console has been quit.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        object_collisions: list[classes.RenderableObject] = get_collisions(renderer, player)

        for object in object_collisions:
            if isinstance(object, classes.Sprite):

                if object.object_type == "coin":
                    stats.add_coin()
                    pygame.mixer.Sound("assets/sound/coin.mp3").play().set_volume(0.03)
                    renderer.objects.remove(object) # type:ignore

                if object.object_type == "enemy" and not player.cooldown:
                    player.setLives(-1)
                    player.change_animation("damage")
                    pygame.mixer.Sound("assets/sound/hurt.mp3").play().set_volume(0.3)
                    player.cooldown = True
                    cooldown_timer = 0

                if object.object_type == "exit":
                    if not room_debounce:
                        room += 1
                        room_debounce = True
                        
                        renderer.clear()
                        draw_level(world, level, room, renderer)
                        player.position = spawn.position
                        player.reload()

                if object.collideable:
                    is_player_colliding(player, object)

        # Detect key pressed
        key_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        if key_pressed[pygame.K_w]:
            player.move(Vector2(0, -0.15) * delta_time) 
        if key_pressed[pygame.K_s]:
            player.move(Vector2(0, 0.15) * delta_time) 
        if key_pressed[pygame.K_a]:
            player.move(Vector2(-0.2, 0) * delta_time) 
        if key_pressed[pygame.K_d]:
            player.move(Vector2(0.2, 0) * delta_time)

        if mouse_pressed[0]:
            player.change_animation("attack")

        if key_pressed[pygame.K_SPACE] and player.dead:
            renderer.objects.append(player)
            player.position = Vector2(0, 0)
            player.lives = 3
            player.dead = False
            dead_time = None


        # Check if player is dead
        if player.lives <= 0:
            player.dead = True
            player.change_animation("dead")

            if not dead_time:
                dead_time = time.time()
            else:
                if time.time() - dead_time >= 0.4 and player in renderer.objects:
                    player.position = Vector2(0, 0)
                    renderer.objects.remove(player)

        cooldown_timer += 1
        
        renderer.update()

        player.update_frame()
        player.draw(renderer.screen)
        
        pygame.display.flip()

if __name__ == "__main__":
    main()

pygame.quit()