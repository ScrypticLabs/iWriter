__author__ = 'Masoud Harati'

from pygame import *
from connect4 import *
from connect4Images import *


screen = display.set_mode((1920,1080), FULLSCREEN)

font.init()

connect4 = connect4(screen)
cursor = (0, 0)
oldCursor = 0

running = True
while running:
	for e in event.get():
		if e.type == QUIT:
			running = False
	if key.get_pressed()[K_ESCAPE]:
		running = False

	mb = mouse.get_pressed()[0]
	cursor = mouse.get_pos()

	connect4.performAction(cursor, oldCursor)
	connect4.main(connect4.cursor, connect4.mb)
	# draw.circle(screen, (255, 255, 255), (cursor), 5)

	oldCursor = cursor

	display.flip()
quit()
