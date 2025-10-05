import pygame, asyncio
from pygame import Vector2
import classes, characters, functions

async def main() -> None:
    
    # PYGAME SETUP
    pygame.init()
    renderer = classes.Renderer()
    clock = pygame.time.Clock()
    running: bool = True

    # GAME VARIABLES
    stats: classes.GameStats = classes.GameStats(0)
    player: classes.Player = classes.Player(characters.knight_images, characters.knight_num_frames)
    spawn: classes.Spawn = classes.Spawn()

    # Level Variables
    world = 1
    level = 1
    room = 1
    room_debounce = False   

    # Menu Variables
    menu_active: bool = True
    selected_menu_button: str = "PLAY"
    selected_menu_index: int = 0
    menu_options: list[str] = ["PLAY", "COSMETICS", "OPTIONS", "CONTROLS", "QUIT"]
    menu_down_pressed: bool = False
    menu_up_pressed: bool = False

    # Drawn Variables
    menu_drawn: bool = False
    level_drawn: bool = False

    # Time variables
    cooldown_timer = 0

    # Audio
    pygame.mixer.set_num_channels(16)

    background_music = pygame.mixer.Sound("assets/sound/music/music_loop1.wav")
    background_music.set_volume(0.1)
    background_music.play(loops=-1)

    sound_effects: dict[str, pygame.mixer.Sound] = {
        "coin": pygame.mixer.Sound("assets/sound/coin.mp3"),
        "hurt": pygame.mixer.Sound("assets/sound/hurt.mp3"),
        "death": pygame.mixer.Sound("assets/sound/death.mp3"),
        "heal": pygame.mixer.Sound("assets/sound/heal.mp3"),
    }

    sound_effects["coin"].set_volume(0.1)
    sound_effects["hurt"].set_volume(0.5)
    sound_effects["death"].set_volume(0.8)
    sound_effects["heal"].set_volume(0.2)

    # Set player position
    player.position = spawn.position

    # GAME LOOP
    while running:
        delta_time = clock.tick()
        renderer.screen.fill((255,255,255)) # Default background colour

        # Detect if the pygame console has been quit.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # When the menu is active
        if menu_active:
            if not menu_drawn:
                spawn.position = Vector2(1300/2, 600)
                player.position = spawn.position
                functions.draw_level("menu.csv", renderer, spawn)
                menu_drawn = True
                level_drawn = False

            functions.draw_menu(renderer, menu_options, selected_menu_button)

            # Get inputs
            key_pressed = pygame.key.get_pressed()

            if key_pressed[pygame.K_RETURN]:
                if selected_menu_button == "PLAY":
                    menu_active = False
                    renderer.clear()
                elif selected_menu_button == "COSMETICS":
                    print("cosmetics")
                elif selected_menu_button == "OPTIONS":
                    print("options")
                elif selected_menu_button == "CONTROLS":
                    print("controls")
                elif selected_menu_button == "QUIT":
                    running = False

            # Handle inputs for moving between menu options
            if key_pressed[pygame.K_s] or key_pressed[pygame.K_DOWN]:
                if not menu_down_pressed: # Stop function if down was already pressed
                    selected_menu_index += 1

                    if selected_menu_index >= len(menu_options):
                        selected_menu_index = 0

                    selected_menu_button = menu_options[selected_menu_index]
                    menu_down_pressed = True
            else:
                menu_down_pressed = False

            if key_pressed[pygame.K_w] or key_pressed[pygame.K_UP]:
                if not menu_up_pressed: # Stop function if up was already pressed
                    selected_menu_index -= 1

                    if selected_menu_index < 0:
                        selected_menu_index = len(menu_options) - 1

                    selected_menu_button = menu_options[selected_menu_index]
                    menu_up_pressed = True
            else:
                menu_up_pressed = False


            renderer.update(player)

            player.update_frame()
            player.draw(renderer.screen)
            
            pygame.display.flip()
            continue
        
        # Draw level if not already drawn
        if not level_drawn:
            functions.draw_level(f"worlds/{world}/l{level}/r{room}.csv", renderer, spawn)
            player.position = spawn.position
            level_drawn = True
            menu_drawn = False

            # Rerender player
            renderer.objects.append(player)

        if cooldown_timer >= 100:
            cooldown_timer = 0
            player.cooldown = False

        functions.draw_lives(renderer, player)
        functions.draw_coins(renderer, stats)

        current_speed = Vector2(0.2, 0.15)

        # Detect key pressed
        moving = False # true when player is moving
        key_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        if key_pressed[pygame.K_q] and not player.dead:
            player.change_animation("block")
            current_speed = Vector2(0.1, 0.075)

        if key_pressed[pygame.K_m]:
            menu_active = True
            renderer.clear()

        if key_pressed[pygame.K_w]:
            player.move(Vector2(0, -current_speed.y) * delta_time)
            moving = True
        if key_pressed[pygame.K_s]:
            player.move(Vector2(0, current_speed.y) * delta_time)
            moving = True
        if key_pressed[pygame.K_a]:
            player.move(Vector2(-current_speed.x, 0) * delta_time)
            moving = True
        if key_pressed[pygame.K_d]:
            player.move(Vector2(current_speed.x, 0) * delta_time)
            moving = True

        if mouse_pressed[0] or key_pressed[pygame.K_e] and not player.dead:
            player.change_animation("attack", False)

        # Change animation to idle if player stops moving
        if not moving and player.playing == "walk":
            player.change_animation("idle")

        # Change animation back to idle if one of these animations are done
        if player.playing in ("attack", "block", "damage") and player.animation_done and not player.dead:
            player.change_animation("idle")

        if key_pressed[pygame.K_SPACE] and player.dead:
            # Reset to first room
            room = 1
            room_debounce = True
            
            renderer.clear()
            functions.draw_level(f"worlds/{world}/l{level}/r{room}.csv", renderer, spawn)
            player.position = spawn.position
            player.reload()
            
            # Rerender player
            renderer.objects.append(player)
            player.lives = 3
            player.dead = False
            player.change_animation("idle")

        # Get object collisions
        object_collisions: list[classes.RenderableObject] = functions.get_collisions(renderer, player)
        attack_collisions: list[classes.Enemy] = functions.get_attack_collisions(renderer, player)

        async with asyncio.TaskGroup() as attack:
            for object in attack_collisions:
                if player.playing == "attack":
                    attack.create_task(object.setLives(-1))
                    if object.lives <= 0:
                        renderer.objects.remove(object)
                    else:
                        object.change_animation("damage", False)

        for object in object_collisions:
            if isinstance(object, classes.Sprite):
                if object.object_type == "coin":
                    stats.add_coin()
                    sound_effects["coin"].play()
                    renderer.objects.remove(object) # type:ignore

                if isinstance(object, classes.Enemy) and not player.cooldown and not player.dead and not player.playing == "block":
                    player.setLives(-object.damage)
                    player.change_animation("damage", False)
                    object.change_animation("attack", False)
                    if player.lives > 0:
                        sound_effects["hurt"].play()
                    else:
                        sound_effects["death"].play()

                    player.cooldown = True
                    cooldown_timer = 0

                if object.object_type == "life" and not player.dead:
                    player.setLives(1)
                    renderer.objects.remove(object)
                    sound_effects["heal"].play()

                if isinstance(object, classes.RoomTeleport) and object.object_type == "exit":
                    if not room_debounce:
                        room = object.room_to
                        room_debounce = True
                        
                        renderer.clear()
                        functions.draw_level(f"worlds/{world}/l{level}/r{room}.csv", renderer, spawn)
                        player.position = spawn.position
                        player.reload()

                if object.collideable:
                    functions.manage_player_colliding(player, object)


        # Check if player is dead
        if player.lives <= 0:
            player.dead = True
            if player.playing != "dead":
                player.change_animation("dead", False)

        cooldown_timer += 1

        room_debounce = False
        
        renderer.update(player)

        # Draw the player
        if player.cooldown == False or cooldown_timer % 5 == 0 or player.dead: 
            player.draw(renderer.screen)

        player.update_frame()
        
        pygame.display.flip()


# Start the main function
if __name__ == "__main__":
    asyncio.run(main())

# Quit pygame once main function has ended
pygame.quit()