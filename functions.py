from typing import Any, Callable
import pygame, csv, random, asyncio
from pygame import Vector2
import classes, characters

def create_object(new_object: classes.Sprite, position: Vector2, size: Vector2, renderer: classes.Renderer):
    if not isinstance(new_object, classes.AnimatableSprite): new_object.load()
    new_object.position = position
    new_object.size = size
    renderer.objects.append(new_object)

def draw_level(file_path: str, renderer: classes.Renderer, spawn: classes.Spawn) -> None:
    roomArray: list[list[str]] = []

    # Open the file
    file = open(file_path, "r")
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
                additional_objects.append({"object_class": classes.Small_Zombie({"idle": "assets/images/enemies/zombie/small/idle.png", "walk": "assets/images/enemies/zombie/small/walk.png", "attack": "assets/images/enemies/zombie/small/attack.png"}, {"idle": 4, "walk": 5, "attack": 4}, Vector2(32), False, "enemy", 2), "position": Vector2(x, y), "size": Vector2(35), "renderer": renderer})
            if "bz" in objects:
                additional_objects.append({"object_class": classes.Big_Zombie("enemy", 2), "position": Vector2(x, y), "size": Vector2(40), "renderer": renderer})
            if "smsk" in objects:
                additional_objects.append({"object_class": classes.Small_Skeleton("enemy", 2), "position": Vector2(x, y), "size": Vector2(70, 35), "renderer": renderer})
            if "bgsk" in objects:
                additional_objects.append({"object_class": classes.Big_Skeleton("enemy", 2), "position": Vector2(x, y), "size": Vector2(80, 60), "renderer": renderer})
            if "tr-sm" in objects:
                additional_objects.append({"object_class": classes.Sprite("assets/images/level_blocks/tree/tree-sm.png", "tree", 1, True), "position": Vector2(x, y), "size": Vector2(30, 60), "renderer": renderer})
            if "tr-lg" in objects:
                additional_objects.append({"object_class": classes.Sprite("assets/images/level_blocks/tree/tree-lg.png", "tree", 1, True), "position": Vector2(x, y), "size": Vector2(60, 60), "renderer": renderer})
        
            if "cn" in objects:
                additional_objects.append({"object_class": classes.AnimatableSprite({"idle": "assets/images/misc/coins.png"}, {"idle": 5}, Vector2(16), False, "coin"), "position": Vector2(x, y), "size": Vector2(25), "renderer": renderer})
            if "life" in objects:
                additional_objects.append({"object_class": classes.AnimatableSprite(characters.life_images, characters.life_num_frames, Vector2(16), False, "life"), "position": Vector2(x, y), "size": Vector2(25), "renderer": renderer})
            if "fence" in objects:
                additional_objects.append({"object_class": classes.Sprite("assets/images/level_blocks/fences/fence.png", "fence", 1, True), "position": Vector2(x, y), "size": Vector2(30, 30), "renderer": renderer})
            if "flag" in objects:
                additional_objects.append({"object_class": classes.AnimatableSprite(characters.flag_images, characters.flag_num_frames, Vector2(60), False, "end"), "position": Vector2(x, y), "size": Vector2(60), "renderer": renderer})
            
            # Check for exits
            for  obj in objects:
                if "exit" in obj:
                    objs = obj.split("-") # Split to get separate values for room number and angle
                    room_number = int(objs[1])
                    rotation = int(objs[2])

                    # Create exit oddbject and rotate
                    new_exit = classes.RoomTeleport(room_number, 1, rotation)
                    additional_objects.append({"object_class": new_exit, "position": Vector2(x, y), "size": Vector2(30), "renderer": renderer}) 

            if "spawn" in objects:
                spawn.set_spawn(Vector2(x, y))   
            
            x += 30 # Add to x value after each block is loaded.
        # Reset x value and add to y value after each row is loaded.
        x = 0
        y += 30
    
    for object in additional_objects:
        create_object(object["object_class"], object["position"], object["size"], object["renderer"]) # type: ignore

def draw_cosmetics_menu(renderer: classes.Renderer, cosmetics: dict[str, bool]) -> None:
    menu_elements: list[classes.Text] = []

    # Create title
    title_font = pygame.font.Font("assets/fonts/pixelify.ttf", 50)
    button_font = pygame.font.Font("assets/fonts/pixelify.ttf", 35)
    game_title = classes.Text("COSMETICS", title_font, pygame.Color(255, 255, 255))
    game_title.position = Vector2(550, 170)
    menu_elements.append(game_title)
    selected_button = list(cosmetics.keys())[0]

    y = 300
    colour = pygame.Color(255, 255, 255)

    for item in cosmetics:
        if selected_button == item:
            colour = pygame.Color(50, 50, 50)
        else:
            colour = pygame.Color(255, 255, 255)

        if cosmetics[item]:
            button = classes.Text(f"{item} (Owned)", button_font, colour)
        else:
            button = classes.Text(f"{item} (100 coins)", button_font, colour)

        button.position = Vector2(500, y)
        menu_elements.append(button)
        y += 40

    # Load all elements
    for item in menu_elements:
        renderer.objects.append(item)

def draw_coins(renderer: classes.Renderer, stats: classes.GameStats):
    coin_symbol = classes.Sprite("assets/images/misc/coin.png")
    coin_symbol.position = Vector2(1150, 710)
    coin_symbol.size = Vector2(25, 25)
    coin_symbol.load()
    coin_symbol.draw(renderer.screen)

    font = pygame.font.Font("assets/fonts/pixelify.ttf", 35)
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
        obj1.position.x < obj2.position.x + obj2.size.x - 20 and
        obj1.position.x + obj1.size.x > obj2.position.x + 20 and
        obj1.position.y < obj2.position.y + obj2.size.y - 30 and
        obj1.position.y + obj1.size.y > obj2.position.y + 20
    )

def player_attack_colliding(plr: classes.Player, obj: classes.RenderableObject) -> bool:
    if plr.direction == -1:
        attack_direction = (
            plr.position.x - 5 < obj.position.x + obj.size.x and # hitbox extended for attack
            plr.position.x + plr.size.x > obj.position.x + 20
        )
    else:
        attack_direction = (
            plr.position.x < obj.position.x + obj.size.x - 20 and
            plr.position.x + plr.size.x + 5 > obj.position.x # hitbox extended for attack
        )

    return (
        attack_direction and
        plr.position.y < obj.position.y + obj.size.y - 30 and
        plr.position.y + plr.size.y > obj.position.y + 20
    )

def manage_player_colliding(plr: classes.Player, obj2: classes.RenderableObject) -> None:
    player_center = Vector2(plr.position.x + plr.size.x/2, plr.position.y + plr.size.y/2) 
    object_center = Vector2(obj2.position.x + obj2.size.x/2, obj2.position.y + obj2.size.y/2)

    overlap_x = (plr.size.x / 2 + obj2.size.x/2) - abs(player_center.x - object_center.x)
    overlap_y = (plr.size.y / 2 + obj2.size.y/2) - abs(player_center.y - object_center.y)

    if overlap_x < overlap_y:
        # X-Axis
        if player_center.x < object_center.x:
            plr.position.x -= overlap_x - 20 # move player left
        else:
            plr.position.x += overlap_x - 20 # move player right
    else:
        # Y-Axis
        if player_center.y < object_center.y:
            plr.position.y -= overlap_y - 20 # move player up
        else:
            plr.position.y += overlap_y - 30 # move player down

def get_collisions(renderer: classes.Renderer, player: classes.Player):
    collisions_list: list[classes.RenderableObject] = []

    for object in renderer.objects:
        if is_colliding(player, object):
            collisions_list.append(object)

    return collisions_list

def get_attack_collisions(renderer: classes.Renderer, player: classes.Player):
    collisions_list: list[classes.Enemy] = []

    for object in renderer.objects:
        if player_attack_colliding(player, object) and isinstance(object, classes.Enemy):
            collisions_list.append(object)

    return collisions_list


async def wait(time: int, function: Callable) -> None: # type: ignore
    await asyncio.sleep(time)
    function()

def new_level(renderer: classes.Renderer, player: classes.Player, spawn: classes.Spawn, stats: classes.GameStats, world: int, level: int) -> None:
    renderer.objects.clear()
    draw_level(f"worlds/{world}/l{level}/r1.csv", renderer, spawn)
    player.position = spawn.position
