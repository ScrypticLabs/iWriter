__author__ = 'Masoud Harati'

from pygame import *
from tictactoe import *

font.init()

screen = display.set_mode((1920,1080), FULLSCREEN)

game = tictactoe(screen)
oldCursor = 0
cursor = 0

game.board()
running = True
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False
        if e.type == KEYDOWN:
        	if e.key == K_ESCAPE:
        		running = False

    mb = mouse.get_pressed()[0]
    mpos = mouse.get_pos()

    game.performAction(mpos, oldCursor)
    game.main(game.mb, game.cursor)

    oldCursor = cursor
    display.flip()
quit()