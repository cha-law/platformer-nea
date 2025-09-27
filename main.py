from typing import Any
import pygame, csv, random, time
from pygame import Vector2
import classes, characters

def create_object(new_object: classes.Sprite, position: Vector2, size: Vector2, renderer: classes.Renderer):
    if not isinstance(new_object, classes.AnimatableSprite): new_object.load()
    new_object.position = position
    new_object.size = size
    renderer.objects.append(new_object)

def draw_level(file_path: str, renderer: classes.Renderer) -> None:
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

            if "exit" in objects:
                additional_objects.append({"object_class": classes.AnimatableSprite({"idle": "assets/images/misc/arrow.png"}, {"idle": 2}, Vector2(32), False, "exit"), "position": Vector2(x, y), "size": Vector2(30, 30), "renderer": renderer})

            if "spawn" in objects:
                spawn.set_spawn(Vector2(x, y))   
            
            x += 30 # Add to x value after each block is loaded.
        # Reset x value and add to y value after each row is loaded.
        x = 0
        y += 30
    
    for object in additional_objects:
        create_object(object["object_class"], object["position"], object["size"], object["renderer"]) # type: ignore

def draw_menu():
    pass

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
        obj1.position.x < obj2.position.x + obj2.size.x - 20 and
        obj1.position.x + obj1.size.x > obj2.position.x + 20 and
        obj1.position.y < obj2.position.y + obj2.size.y - 30 and
        obj1.position.y + obj1.size.y > obj2.position.y + 20
    )

def manage_player_colliding(plr: classes.Player, obj2: classes.RenderableObject) -> None:
    player_center = Vector2(player.position.x + player.size.x/2, player.position.y + player.size.y/2) 
    object_center = Vector2(obj2.position.x + obj2.size.x/2, obj2.position.y + obj2.size.y/2)

    overlap_x = (plr.size.x / 2 + obj2.size.x/2) - abs(player_center.x - object_center.x)
    overlap_y = (plr.size.y / 2 + obj2.size.y/2) - abs(player_center.y - object_center.y)

    if overlap_x < overlap_y:
        # X-Axis
        if player_center.x < object_center.x:
            player.position.x -= overlap_x - 20 # move player left
        else:
            player.position.x += overlap_x - 20 # move player right
    else:
        # Y-Axis
        if player_center.y < object_center.y:
            player.position.y -= overlap_y - 20 # move player up
        else:
            player.position.y += overlap_y - 30 # move player down

def get_collisions(renderer: classes.Renderer, player: classes.Player):
    collisions_list: list[classes.RenderableObject] = []

    for object in renderer.objects:
        if is_colliding(player, object):
            collisions_list.append(object)

    return collisions_list


stats: classes.GameStats = classes.GameStats(0)
player: classes.Player = classes.Player(characters.knight_images, characters.knight_num_frames)
spawn: classes.Spawn = classes.Spawn()

def main() -> None:
    
    # PYGAME SETUP
    pygame.init()
    pygame.mixer.init()
    renderer = classes.Renderer()
    clock = pygame.time.Clock()
    running: bool = True

    # GAME VARIABLES
    menu_active: bool = False

    world = 1
    level = 1
    room = 1
    room_debounce = False

    #draw_level("menu.csv", renderer)
    draw_level(f"worlds/{world}/l{level}/r{room}.csv", renderer)
    player.position = spawn.position

    cooldown_timer = 0
    dead_time = None

    # GAME LOOP
    while running:
        delta_time = clock.tick()
        renderer.screen.fill((215, 252, 252)) # Default background colour

        # Detect if the pygame console has been quit.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # MENU SCRIPT
        if menu_active:
            renderer.update()

            player.update_frame()
            player.draw(renderer.screen)
            
            pygame.display.flip()
            continue

        player.change_animation("idle")

        if cooldown_timer >= 100:
            cooldown_timer = 0
            player.cooldown = False

        draw_lives(renderer, player)
        draw_coins(renderer, stats)

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
            # Reset to first room
            room = 1
            room_debounce = True
            
            renderer.clear()
            draw_level(f"worlds/{world}/l{level}/r{room}.csv", renderer)
            player.position = spawn.position
            player.reload()
            
            # Rerender player
            renderer.objects.append(player)
            player.lives = 3
            player.dead = False
            dead_time = None

        # Get object collisions
        object_collisions: list[classes.RenderableObject] = get_collisions(renderer, player)

        for object in object_collisions:
            if isinstance(object, classes.Sprite):

                if object.object_type == "coin":
                    stats.add_coin()
                    if soundtrack := pygame.mixer.Sound("assets/sound/coin.mp3").play():
                        soundtrack.set_volume(0.03)
                    renderer.objects.remove(object) # type:ignore

                if object.object_type == "enemy" and not player.cooldown and not player.dead:
                    player.setLives(-1)
                    player.change_animation("damage")
                    pygame.mixer.Sound("assets/sound/hurt.mp3").play().set_volume(0.3)
                    player.cooldown = True
                    cooldown_timer = 0

                if object.object_type == "life" and not player.dead:
                    player.setLives(1)
                    renderer.objects.remove(object)
                    pygame.mixer.Sound("assets/sound/heal.wav").play().set_volume(0.3)

                if object.object_type == "exit":
                    if not room_debounce:
                        room += 1
                        room_debounce = True
                        
                        renderer.clear()
                        draw_level(f"worlds/{world}/l{level}/r{room}.csv", renderer)
                        player.position = spawn.position
                        player.reload()

                if object.collideable:
                    manage_player_colliding(player, object)


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

        room_debounce = False
        
        renderer.update(player)

        # Draw the player
        if player.cooldown == False or cooldown_timer % 6 == 0 or player.dead: 
            player.draw(renderer.screen)

        player.update_frame()
        
        pygame.display.flip()

if __name__ == "__main__":
    main()

pygame.quit()