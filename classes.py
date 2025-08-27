from abc import ABC
from typing import Optional, List
from pygame import Surface, Vector2
import pygame, time

pygame.font.init()

start_time: float = time.time()

class GameStats():
    def __init__(self, coins: int):
        self.coins = coins

    def add_coin(self):
        self.coins += 1

class Renderer():
    def __init__(self, screen_size: Vector2 = Vector2(1300, 750)):
        self.objects: List[RenderableObject] = []
        self.screen = pygame.display.set_mode(screen_size)
        self.screen_size = screen_size

    def update(self):
        for sprite in self.objects:
            # Update frame if sprite is animated
            if isinstance(sprite, AnimatableSprite):
                sprite.update_frame()

                if isinstance(sprite, Enemy):
                    sprite.update_movement()

            sprite.draw(self.screen)     

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
    def __init__(self, image: str, object_type: str = "x", z_index: int = 1):
        super().__init__()
        self.surface = Surface(self.size)
        self.z_index = 1
        self.image: Optional[str] = image
        self.direction = 1
        self.object_type = object_type
    
    def load(self):
        if self.image == None:
            raise ValueError("Failed to load image: no image found")
        
        self.surface = pygame.image.load(self.image)

    def draw(self, screen: Surface):
        sprite: Surface = pygame.transform.scale(self.surface, self.size)
        screen.blit(sprite, self.position)

    def flip(self):
        self.surface = pygame.transform.flip(self.surface, True, False)
        self.direction *= -1

class AnimatableSprite(Sprite):
    def __init__(self, images: dict[str, str], num_frames: dict[str, int], frame_size: int = 64, crop: bool = False, object_type: str = "x", z_index: int = 1):
        super().__init__("", object_type, z_index)
        self.frames = extract_frames(images, frame_size, num_frames, crop)
        self.current_frame = 0 # Current frame
        self.dict_num_frames = num_frames # The amount of frames each image has.
        self.frame_size = frame_size # Size of each frame
        self.playing = "idle" # The animation currently being played
        self.num_frames = self.dict_num_frames["idle"] # The number of frames in the current animation.
        self.fps = 8 # Frames per second for the animation

    def change_animation(self, new_anim: str):
        self.playing = new_anim
        self.current_frame = 0 # Reset frame back to 0
        self.num_frames = self.dict_num_frames[new_anim]

    def update_frame(self):
        self.current_frame: int = int((time.time() - start_time) * self.fps % self.dict_num_frames[self.playing]) # type: ignore
        if self.current_frame >= len(self.frames[self.playing]): self.current_frame = 0

        if self.direction == -1:
            self.surface = pygame.transform.flip(self.frames[self.playing][self.current_frame], True, False)
        else:
            self.surface = self.frames[self.playing][self.current_frame]

class Enemy(AnimatableSprite):
    def __init__(self, images: dict[str, str], num_frames: dict[str, int], frame_size: int = 64, crop: bool = False, object_type: str = "x", z_index: int = 1):
        super().__init__(images, num_frames, frame_size, crop, object_type, z_index)
        self.lives = 3

    def update_movement(self):
        ...

class Small_Zombie(Enemy):
    def __init__(self, images: dict[str, str], num_frames: dict[str, int], frame_size: int = 64, crop: bool = False, object_type: str = "x", z_index: int = 1):
        super().__init__(images, num_frames, frame_size, crop, object_type, z_index)
        self.lives = 3
        self.speed = 0.5
        self.steps = 0

    def update_movement(self):
        self.position.x += (self.speed * self.direction)
        self.steps += (self.direction * self.speed)

        if self.steps >= 40:
            self.direction = -1
        
        if self.steps <= -40:
            self.direction = 1


class Player(AnimatableSprite):
    def __init__(self, images: dict[str, str], dict_num_frames: dict[str, int], frame_size: int = 64):
        super().__init__(images, dict_num_frames, frame_size, True)
        self.lives = 3
        self.size = Vector2(40,40)

    def move(self, move: Vector2):
        if self.lives > 0:
            self.position.x += move.x
            self.position.y += move.y

            if self.position.x <= 0: self.position.x = 0
            elif self.position.x + self.size.x >= 1300: self.position.x = 1300 - self.size.x

            if self.position.y <= 0: self.position.y = 0
            elif self.position.y + self.size.y >= 690: self.position.y = 690 - self.size.y

            if self.direction * move.x < 0: self.direction *= -1

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

def extract_frames(images: dict[str, str], frame_size: int, num_frames: dict[str, int], crop: bool) -> dict[str, List[Surface]]:
    seperated_images: dict[str, List[Surface]] = {}

    for anim in images: # Loop through each type of animation
        # Load each image
        loaded_image = pygame.image.load(images[anim])

        array_frames: List[Surface] = [] # Create a new array for the surface of each frame

        for i in range(num_frames[anim]): # Loop for the number of frames that animation has
            current_img = loaded_image.subsurface(pygame.Rect(i * frame_size, 0, frame_size, frame_size)) # type: ignore
            if crop:
                final_img = current_img.subsurface(pygame.Rect(frame_size * 0.35, frame_size * 0.35, frame_size * 0.5, frame_size * 0.5))
                array_frames.append(final_img) # type: ignore
            else:
                array_frames.append(current_img) # type: ignore

        seperated_images[anim] = array_frames

    return seperated_images