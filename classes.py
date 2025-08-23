from abc import ABC
#from pathlib import Path
from typing import Sequence, Optional, List
from pygame import Surface, Vector2
import pygame

pygame.font.init()

class Renderer():
    def __init__(self, screen_size: Vector2 = Vector2(1800, 900)):
        self.objects: List[RenderableObject] = []
        self.screen = pygame.display.set_mode(screen_size)
        self.screen_size = screen_size

    def update(self):
        for sprite in self.objects:
            sprite.draw(self.screen)     


class PhysicsEngine():
    def __init__(self):
        self.physics_objects: List[PhysicsObject] = []
    
    def update(self, delta_time: int):
        for object in self.physics_objects:
            object.update(self.physics_objects)

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
    def __init__(self, image: str):
        super().__init__()
        self.surface = Surface(self.size)
        self.z_index = 1
        self.image: Optional[str] = image
    
    def load(self):
        if self.image == None:
            raise ValueError("Failed to load image: no image found")
        
        self.surface = pygame.image.load(self.image)

    def draw(self, screen: Surface):
        sprite: Surface = pygame.transform.scale(self.surface, self.size)
        screen.blit(sprite, self.position)


def is_colliding(obj1: "PhysicsObject", obj2: "PhysicsObject") -> bool:
    return (
        obj1.position.x < obj2.position.x + obj2.size.x and
        obj1.position.x + obj1.size.x > obj2.position.x and
        obj1.position.y < obj2.position.y + obj2.size.y and
        obj1.position.y + obj1.size.y > obj2.position.y
    )

def is_grounded(obj1: "PhysicsObject", physics_objects: Sequence["RenderableObject"], overlap_tolerance: int = 1) -> bool:

    player_left = obj1.position.x
    player_right = obj1.position.x + obj1.size.x
    player_bottom = obj1.position.y + obj1.size.y

    for colliding_object in physics_objects:
        if hasattr(colliding_object, "image") and getattr(colliding_object, "image") is not None:

            block_left = colliding_object.position.x
            block_right = colliding_object.position.x + colliding_object.size.x
            block_top = colliding_object.position.y

            is_above = (
                player_bottom <= block_top and
                player_bottom + overlap_tolerance >= block_top
            )

            is_horizontal = (
                player_right >= block_left and
                player_left <= block_left or
                player_left <= block_right and
                player_right >= block_right
            )

            if is_above and is_horizontal:
                return True
        
    return False



class PhysicsObject(Sprite):
    def __init__(self, image: str):
        super().__init__(image)
        self.velocity = Vector2()
        self.gravity = Vector2(0, 9)
        self.anchored: bool = False
        self.grounded: bool = False

    def update(self, physics_objects: Sequence["RenderableObject"]):
        if self.anchored: return # Do not apply physics if the object is anchored.

        self.grounded = is_grounded(self, physics_objects) # Check if the object is touching the ground.

        if not self.grounded:
            self.velocity += self.gravity # Apply gravity to velocity

        for colliding_object in physics_objects:
            if hasattr(colliding_object, "image") and getattr(colliding_object, "image") is not None:
                overlap_tolerance = 0.1

                player_left = self.position.x
                player_right = self.position.x + self.size.x
                player_top = self.position.y
                player_bottom = self.position.y + self.size.y

                block_left = colliding_object.position.x
                block_right = colliding_object.position.x + colliding_object.size.x
                block_bottom = colliding_object.position.y + colliding_object.size.y

                if (player_left - overlap_tolerance <= block_right and player_right > block_right) or (player_right + overlap_tolerance >= block_left and player_left < block_left):
                    self.velocity = Vector2(0, self.velocity.y)
                
                if player_top - overlap_tolerance <= block_bottom and player_bottom < block_bottom:
                    self.velocity = Vector2(self.velocity.x, 0)
        
        self.position = Vector2(self.position.x + self.velocity.x, self.position.y + self.velocity.y) # Apply velocity to object's position
        self.velocity = Vector2() # Clear velocity

    def __repr__(self) -> str:
        return f"Player({self.position=} {self.velocity=} {self.grounded=})"

class Player(PhysicsObject):
    def __init__(self, image: str):
        super().__init__(image)
        self.lives = 3
        self.size = Vector2(45,45)

    def move(self, move: Vector2):
        self.velocity.x += move.x
        self.velocity.y += move.y

    def setLives(self, life_multiplier: int):
        self.lives += life_multiplier


class ButtonComponent(Sprite):
    def __init__(self, image: str):
        super().__init__(image)
        self.active = False  