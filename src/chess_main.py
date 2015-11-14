from pygame import *
from chessGame import *

font.init()

mb = 0
cursor = (0, 0)

screen = display.set_mode((1920, 1080), FULLSCREEN)
chess = chessGame()

chess.start(screen, cursor, mb)

running = True
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False
        if e.type == KEYDOWN:
        	if e.key == K_ESCAPE:
        		running = False 
        mb = mouse.get_pressed()[0]
        cursor = mouse.get_pos()
        chess.main(screen, mb, cursor)

    display.flip()
quit()
