from micropython import *
from global_func import *

class rooms():
    def __init__(self): 
        self.rooms_sprites = ["PlaceHolder"]
        self.room_version = 0
        self.room_x = 0

    def draw_room(self):
        screen.drawSprite(self.rooms_sprites[self.room_version], self.room_x, 0, 1600,720)

    def room_pos(self):
        if -350 <= mouse.x <= -200 and self.room_x < 100:
            self.room_x += 2
        elif mouse.x < -350 and self.room_x < 100:
            self.room_x += 5
        if 350 >= mouse.x >= 200 and self.room_x > -100:
            self.room_x -= 2
        elif mouse.x > 350 and self.room_x > -100:
            self.room_x -= 5
    


class office_room(rooms):
    def __init__(self, rooms_sprites: list):
        super().__init__()
        self.rooms_sprites = rooms_sprites
        self.left_light = False
        self.right_light = False

        self.left_door = False
        self.right_door = False


    def variations(self):
        if self.left_light:
            self.room_version = 1 #left light on
            self.right_light = False
        
        elif self.right_light:
            self.room_version = 2 #right light on
            self.left_light = False
        else:
            self.room_version = 0


    def buttons(self):
        #update
        if click(-760+self.room_x,40,40,60):
            self.left_door = not self.left_door

        if click(-760+self.room_x,-40,40,60):
            self.left_light = not self.left_light

        if click(760+self.room_x,40,40,60):
            self.right_door = not self.right_door

        if click(760+self.room_x,-40,40,60):
            self.right_light = not self.right_light
        self.button_draw()

    def button_draw(self):
        # ===== SPRITES ===== #
        left_sprite = {
            (True, True): "left_buttons_on",
            (True, False): "left_buttons_light",
            (False, True): "left_buttons_door",
            (False, False): "left_buttons"
        }

        right_sprite = {
            (True, True): "right_buttons_on",
            (True, False): "right_buttons_light",
            (False, True): "right_buttons_door",
            (False, False): "right_buttons"
        }

        screen.drawSprite(
            left_sprite[(self.left_light, self.left_door)],
            self.room_x-760, 0, 92, 246
        )

        screen.drawSprite(
            right_sprite[(self.right_light, self.right_door)],
            self.room_x+760, 0, 92, 246
        )
