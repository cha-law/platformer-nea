from typing import List
import classes
import pygame
from pygame import Vector2

title = classes.Text("Platformer Game", pygame.font.SysFont("Arial", 36), pygame.Color(0,0,0))
title.position = Vector2(1800/2 - 100, 900/2 - 300)

# Initial page
pages: List[dict[str, int]] = [
    {
        "PLAY": 1,
        "COSMETICS": 2,
        "SETTINGS": 3
    }
]
