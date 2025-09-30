import pygame, time
from pygame import Vector2
import classes, characters, functions

def main() -> None:
    
    # PYGAME SETUP
    pygame.init()

    renderer = classes.Renderer()
    clock = pygame.time.Clock()
    running: bool = True

    # GAME VARIABLES
    stats: classes.GameStats = classes.GameStats(0)
    player: classes.Player = classes.Player(characters.knight_images, characters.knight_num_frames)
    spawn: classes.Spawn = classes.Spawn()

    # MENU VARIABLES
    menu_active: bool = False

    # LEVEL VARIABLES
    world = 1
    level = 1
    room = 1
    room_debounce = False

    #draw_level("menu.csv", renderer)
    functions.draw_level(f"worlds/{world}/l{level}/r{room}.csv", renderer, spawn)
    player.position = spawn.position

    cooldown_timer = 0
    dead_time = None

    # GAME LOOP
    while running:
        delta_time = clock.tick()
        renderer.screen.fill((255,255,255)) # Default background colour

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
        
        # Change animation back to idle if player stops moving
        if player.playing == "walk" or cooldown_timer == 100: 
            player.change_animation("idle")

        if cooldown_timer >= 100:
            cooldown_timer = 0
            player.cooldown = False

        functions.draw_lives(renderer, player)
        functions.draw_coins(renderer, stats)

        current_speed = Vector2(0.2, 0.15)

        # Detect key pressed
        key_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        if key_pressed[pygame.K_q]:
            player.change_animation("block")
            current_speed = Vector2(0.1, 0.075)

        if key_pressed[pygame.K_w]:
            player.move(Vector2(0, -current_speed.y) * delta_time) 
        if key_pressed[pygame.K_s]:
            player.move(Vector2(0, current_speed.y) * delta_time) 
        if key_pressed[pygame.K_a]:
            player.move(Vector2(-current_speed.x, 0) * delta_time) 
        if key_pressed[pygame.K_d]:
            player.move(Vector2(current_speed.x, 0) * delta_time)

        if mouse_pressed[0]:
            player.change_animation("attack")

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
            dead_time = None

        # Get object collisions
        object_collisions: list[classes.RenderableObject] = functions.get_collisions(renderer, player)

        for object in object_collisions:
            if isinstance(object, classes.Sprite):

                if object.object_type == "coin":
                    stats.add_coin()
                    if soundtrack := pygame.mixer.Sound("assets/sound/coin.mp3"):
                        soundtrack.play().set_volume(0.03)
                    renderer.objects.remove(object) # type:ignore

                if isinstance(object, classes.Enemy) and not player.cooldown and not player.dead and not player.playing == "block":
                    player.setLives(-object.damage)
                    player.change_animation("damage")
                    if player.lives > 0:
                        if soundtrack := pygame.mixer.Sound("assets/sound/hurt.mp3"):
                            soundtrack.play().set_volume(0.3)
                    else:
                        if soundtrack := pygame.mixer.Sound("assets/sound/death.mp3"):
                            soundtrack.play().set_volume(0.8)

                    player.cooldown = True
                    cooldown_timer = 0

                if object.object_type == "life" and not player.dead:
                    player.setLives(1)
                    renderer.objects.remove(object)
                    pygame.mixer.Sound("assets/sound/heal.mp3").play().set_volume(0.2)

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
        if player.cooldown == False or cooldown_timer % 5 == 0 or player.dead: 
            player.draw(renderer.screen)

        player.update_frame()
        
        pygame.display.flip()


# Start the main function
if __name__ == "__main__":
    main()

# Quit pygame once main function has ended
pygame.quit()