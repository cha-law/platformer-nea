from abc import ABC
from typing import Optional, List
from pygame import Surface, Vector2
import pygame, time
import asyncio

import characters

pygame.font.init()

start_time: float = time.time()

class GameStats():
    def __init__(self, coins: int):
        self.coins = coins

    def add_coin(self):
        self.coins += 1

class Spawn:
    def __init__(self):
        self.position: Vector2 = Vector2(0, 0)

    def set_spawn(self, new_spawn: Vector2):
        self.position: Vector2 = new_spawn

class Renderer():
    def __init__(self, screen_size: Vector2 = Vector2(1375, 750)):
        self.objects: List[RenderableObject] = []
        self.screen = pygame.display.set_mode(screen_size)
        self.screen_size = screen_size

    def update(self, player: "Player"):
        for sprite in self.objects:
            # Update frame if sprite is animated
            if isinstance(sprite, AnimatableSprite):
                sprite.update_frame()

                if isinstance(sprite, Enemy):
                    if sprite.tracking == True: 
                        sprite.update_movement(player) # type: ignore
                    else: 
                        sprite.update_movement()

            if isinstance(sprite, Text):
                self.screen.blit(sprite.font.render(sprite.text, True, sprite.color), sprite.position)
            else:
                sprite.draw(self.screen)     

    def clear(self):
        self.objects = []

class GameObject(ABC):
    def __init__(self):
        self.position = Vector2()
        self.size = Vector2()

class RenderableObject(GameObject):
    def draw(self, screen: Surface) -> None:
        ...

class Text(RenderableObject):
    def __init__(self, text: str, font: pygame.font.Font, color: pygame.Color):
        super().__init__()
        self.text = text
        self.font = font
        self.color = color

    def draw(self, screen: Surface) -> None:
        screen.blit(self.font.render(self.text, True, self.color), self.position)

class MenuButton(Text):
    def __init__(self, text: str, font: pygame.font.Font, color: pygame.Color, page: int):
        super().__init__(text, font, color)
        self.page = page

class Sprite(RenderableObject):
    def __init__(self, image: str, object_type: str = "x", z_index: int = 1, collideable: bool = False):
        super().__init__()
        self.surface = Surface(self.size)
        self.z_index = 1
        self.image: Optional[str] = image
        self.direction = 1
        self.object_type = object_type
        self.collideable = collideable
    
    def load(self):
        if self.image == None:
            raise ValueError("Failed to load image: no image found")
        
        self.surface = pygame.image.load(self.image)

    def draw(self, screen: Surface):
        sprite: Surface = pygame.transform.scale(self.surface, self.size)
        # 
        screen.blit(sprite, self.position)

    def flip(self):
        self.surface = pygame.transform.flip(self.surface, True, False)
        self.direction *= -1

class AnimatableSprite(Sprite):
    def __init__(self, images: dict[str, str], num_frames: dict[str, int], frame_size: Vector2 = Vector2(64, 64), crop: bool = False, object_type: str = "x", z_index: int = 1, collideable: bool = False, rotation: int = 0):
        super().__init__("", object_type, z_index, collideable)
        self.images = images # Original image
        self.frames = extract_frames(images, frame_size, num_frames, crop)
        self.current_frame = 0 # Current frame
        self.dict_num_frames = num_frames # The amount of frames each image has.
        self.frame_size = frame_size # Size of each frame
        self.playing = "idle" # The animation currently being played
        self.num_frames = self.dict_num_frames["idle"] # The number of frames in the current animation.
        self.fps = 8 # Frames per second for the animation
        self.crop = crop
        self.rotation = rotation
        self.frozen = False
        self.loop = True
        self.animation_start_time = time.time()
        self.animation_done = False

    def change_animation(self, new_anim: str, loop: bool = True):
        self.playing = new_anim
        self.current_frame = 0 # Reset frame back to 0
        self.num_frames = self.dict_num_frames[new_anim]
        self.animation_start_time = time.time()
        self.animation_done = False
        self.loop = loop

    def reload(self) -> None:
        self.frames = extract_frames(self.images, self.frame_size, self.dict_num_frames, self.crop)

    def freeze(self) -> None:
        self.frozen = True
    
    def unfreeze(self) -> None:
        self.frozen = False

    def update_frame(self):
        if not self.frozen:

            number_frames: int = int((time.time() - self.animation_start_time) * self.fps)

            if self.loop:
                if self.num_frames > 0:
                    number_frames %= self.num_frames
                self.animation_done = False
            else:
                # Non-looping animation
                if number_frames >= self.num_frames: # When animation has exceeded playing
                    number_frames = self.num_frames - 1
                    self.animation_done = True
                else:
                    self.animation_done = False

            self.current_frame = max(0, number_frames)
            current_frame_surface = self.frames[self.playing][self.current_frame]

            if self.direction == -1:
                self.surface = pygame.transform.flip(current_frame_surface, True, False)
            else:
                self.surface = pygame.transform.rotate(current_frame_surface, self.rotation)

class RoomTeleport(AnimatableSprite):
    def __init__(self, room_to: int, z_index: int = 1, rotation: int = 0):
        super().__init__(characters.arrow_images, characters.arrow_num_frames, Vector2(32), False, "exit", z_index, False, rotation)
        self.room_to = room_to

class Enemy(AnimatableSprite):
    def __init__(self, images: dict[str, str], num_frames: dict[str, int], frame_size: Vector2 = Vector2(64, 64), crop: bool = False, object_type: str = "x", z_index: int = 1, damage: int = 1):
        super().__init__(images, num_frames, frame_size, crop, object_type, z_index, False)
        self.lives = 3
        self.tracking = False
        self.damage = damage
        self.attack_cooldown: bool = False
        self._lock = asyncio.Lock()

    def update_movement(self):
        ...

    async def setLives(self, life_multiplier: int):
        async with self._lock:
            if self.attack_cooldown: # Return if the enemy is on cooldown
                return
            pygame.mixer.Sound("assets/sound/hit_enemy.wav").play().set_volume(0.3)
            self.lives += life_multiplier # Remove life
            self.attack_cooldown = True # Prevent enemy from being attacked again

            asyncio.create_task(self.set_cooldown()) # Set cooldown for the enemy
    
    async def set_cooldown(self):
        await asyncio.sleep(2)
        self.attack_cooldown = False

class Small_Zombie(Enemy):
    def __init__(self, images: dict[str, str], num_frames: dict[str, int], frame_size: Vector2 = Vector2(64, 64), crop: bool = False, object_type: str = "x", z_index: int = 1):
        super().__init__(images, num_frames, frame_size, crop, object_type, z_index)
        self.lives = 2
        self.speed = 0.5
        self.steps = 0
        self.tracking = False

    def update_movement(self):
        self.position.x += (self.speed * self.direction)
        self.steps += (self.direction * self.speed)

        if self.steps >= 40:
            self.direction = -1
        
        if self.steps <= -40:
            self.direction = 1

class Small_Skeleton(Enemy):
    def __init__(self, object_type: str = "x", z_index: int = 1):
        super().__init__(characters.smallskeleton_images, characters.smallskeleton_num_frames, Vector2(64, 32), False, object_type, z_index)
        self.lives = 1
        self.speed = 0.6
        self.steps = 0
        self.range = 175
        self.tracking = True

    def update_movement(self, player: "Player"): # type: ignore
        self.change_animation("walk")

        player_center = Vector2(player.position.x + player.size.x/2, player.position.y + player.size.y/2) 
        enemy_center = Vector2(self.position.x + self.size.x/2, self.position.y + self.size.y/2)
        
        if player_center.distance_to(enemy_center) <= self.range and not player.dead:
            # Player is in range
            self.speed = 1.9
            direction = (player_center - enemy_center).normalize() # Direction to player from enemy
            self.position.x += round(self.speed * direction.x) 
            self.position.y += round(self.speed * direction.y)
            
            # Check direction
            if direction.x < 0:
                self.direction = -1
            else:
                self.direction = 1
        else:
            # Player is not in range
            self.speed = 0.6
            self.position.x += (self.speed * self.direction)
            self.steps += (self.direction * self.speed)
            
            if self.steps >= 40:
                self.direction = -1
            
            if self.steps <= -40:
                self.direction = 1

class Big_Skeleton(Enemy):
    def __init__(self, object_type: str = "x", z_index: int = 1):
        super().__init__(characters.bigskeleton_images, characters.bigskeleton_num_frames, Vector2(64, 48), False, object_type, z_index, 2)
        self.lives = 3
        self.speed = 0.3
        self.steps = 0
        self.range = 300
        self.tracking = True

    def update_movement(self, player: "Player"): # type: ignore
        self.change_animation("walk")

        player_center = Vector2(player.position.x + player.size.x/2, player.position.y + player.size.y/2) 
        enemy_center = Vector2(self.position.x + self.size.x/2, self.position.y + self.size.y/2)
        
        if player_center.distance_to(enemy_center) <= self.range and not player.dead:
            # Player is in range
            self.speed = 0.9
            direction = (player_center - enemy_center).normalize() # Direction to player from enemy
            self.position.x += round(self.speed * direction.x) 
            self.position.y += round(self.speed * direction.y)
            
            # Check direction
            if direction.x < 0:
                self.direction = -1
            else:
                self.direction = 1
        else:
            # Player is not in range
            self.speed = 0.3
            self.position.x += (self.speed * self.direction)
            self.steps += (self.direction * self.speed)
            
            if self.steps >= 40:
                self.direction = -1
            
            if self.steps <= -40:
                self.direction = 1

class Big_Zombie(Enemy):
    def __init__(self, object_type: str = "x", z_index: int = 1):
        super().__init__(characters.bigzombie_images, characters.bigzombie_num_frames, Vector2(32), False, object_type, z_index, 2)
        self.lives = 5
        self.speed = 0.3
        self.steps = 0
        self.range = 300
        self.tracking = True

    def update_movement(self, player: "Player"): # type: ignore
        self.change_animation("walk")

        player_center = Vector2(player.position.x + player.size.x/2, player.position.y + player.size.y/2) 
        enemy_center = Vector2(self.position.x + self.size.x/2, self.position.y + self.size.y/2)
        
        if player_center.distance_to(enemy_center) <= self.range and not player.dead:
            # Player is in range
            self.speed = 0.9
            direction = (player_center - enemy_center).normalize() # Direction to player from enemy
            self.position.x += round(self.speed * direction.x) 
            self.position.y += round(self.speed * direction.y)
            
            # Check direction
            if direction.x < 0:
                self.direction = -1
            else:
                self.direction = 1
        else:
            # Player is not in range
            self.speed = 0.3
            self.position.x += (self.speed * self.direction)
            self.steps += (self.direction * self.speed)
            
            if self.steps >= 40:
                self.direction = -1
            
            if self.steps <= -40:
                self.direction = 1

class Player(AnimatableSprite):
    def __init__(self, images: dict[str, str], dict_num_frames: dict[str, int], frame_size: Vector2 = Vector2(64, 64)):
        super().__init__(images, dict_num_frames, frame_size, False)
        self.lives = 3
        self.size = Vector2(80,80)
        self.cooldown = False
        self.dead = False
        self.last_move = Vector2(0)

    def move(self, move: Vector2):
        if self.lives > 0:
            self.position.x += move.x
            self.position.y += move.y
            self.last_move = move

            if self.position.x + 20 <= 0: self.position.x = -20
            elif self.position.x + self.size.x - 20 >= 1375: self.position.x = 1375 - self.size.x + 20

            if self.position.y + 20 <= 0: self.position.y = -20
            elif self.position.y + self.size.y - 20 >= 690: self.position.y = 690 - self.size.y + 20

            if self.direction * move.x < 0: self.direction *= -1

            if self.playing == "idle":
                self.playing = "walk"        

    def setLives(self, life_multiplier: int):
        self.lives += life_multiplier


class ButtonComponent(Sprite):
    def __init__(self, image: str):
        super().__init__(image)
        self.active = False  




# FUNCTIONS

def is_colliding(obj1: RenderableObject, obj2: RenderableObject) -> bool:
    return (
        obj1.position.x < obj2.position.x + obj2.size.x and
        obj1.position.x + obj1.size.x > obj2.position.x and
        obj1.position.y < obj2.position.y + obj2.size.y and
        obj1.position.y + obj1.size.y > obj2.position.y
    )

def is_player_colliding(obj1: RenderableObject, obj2: RenderableObject) -> bool:
    # Updated collisions for the insane space outside of the character
    return (
        obj1.position.x + 20 < obj2.position.x + obj2.size.x and
        obj1.position.x + obj1.size.x - 20 > obj2.position.x and
        obj1.position.y + 20 < obj2.position.y + obj2.size.y and
        obj1.position.y + obj1.size.y - 20 > obj2.position.y
    )

def extract_frames(images: dict[str, str], frame_size: Vector2, num_frames: dict[str, int], crop: bool) -> dict[str, List[Surface]]:
    seperated_images: dict[str, List[Surface]] = {}

    for anim in images: # Loop through each type of animation
        # Load each image
        loaded_image = pygame.image.load(images[anim])

        array_frames: List[Surface] = [] # Create a new array for the surface of each frame

        for i in range(num_frames[anim]): # Loop for the number of frames that animation has
            current_img = loaded_image.subsurface(pygame.Rect(i * frame_size.x, 0, frame_size.x, frame_size.y)) # type: ignore
            if crop:
                final_img = current_img.subsurface(pygame.Rect(frame_size.x * 0.35, frame_size.y * 0.35, frame_size.x * 0.5, frame_size.y * 0.5))
                array_frames.append(final_img) # type: ignore
            else:
                array_frames.append(current_img) # type: ignore

        seperated_images[anim] = array_frames

    return seperated_images