from micropython import *
from room import *
from global_func import *
#room_x = 0 #position x de l'office



# ================== #
#    CLASS INITS
# ================== #
office = office_room(["office","office_ll","office_rl","office_ll_b"])

def debug(hitboxes: bool, info: bool):
    if hitboxes:
        screen.drawRect(-760+office.room_x,40,40,60,(0,255,0))
        screen.drawRect(760+office.room_x,40,40,60,(0,255,0))
        screen.drawRect(-760+office.room_x,-40,40,60,(0,255,0))
        screen.drawRect(760+office.room_x,-40,40,60,(0,255,0))
    if info:
        screen.drawText(f"cursor postiton: {mouse.x}, {mouse.y}", -582,350)


def draw():
    # ===== OFFICE ====== #
    office.draw_room()
    office.room_pos()
    office.variations()
    office.buttons()
    debug(hitboxes = True, info = True)
    
    if click(-760+office.room_x,0,40,60):
        screen.drawText("clicked !!",0,30)
    
    
    #screen.drawSprite("office", room_x, 0, 1600,720)   # lit sprites/player.png

run(width=1400, height=720, scale=1, title="FNAF")
