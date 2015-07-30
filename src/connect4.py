__author__ = 'Masoud Harati'
__editor__ = 'Abhi Gupta'

"""
An interactive game that is short but fun. This game can be played several times without dedicating too much of your personal time. 
It doesn’t require very accurate eye tracking, as selecting what column to place the chip in only requires the x-coordinates. 
In general, the selection of the columns is based on gaze and dwell.
"""

from pygame import *
from connect4Images import *
from random import randint

class connect4:
	def __init__(self, screen):
		"Initializes the class of connect4"
		self.screen = screen
		self.gameBoard = [['_', '_', '_', '_', '_', '_', '_', '_', '_'],
						  ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
						  ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
						  ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
						  ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
						  ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
						  ['_', '_', '_', '_', '_', '_', '_', '_', '_']]
		self.currentTurn = 1
		self.winner = ""
		self.backgroundValue = True
		self.countBlue = 0
		self.countPurple = 0 
		self.connect4boardRect = Rect(350, 15, 1260, 840)
		self.cursor = 0
		self.mb = 0
		self.dwell_delay = 0
		self.maxDelay = 100

	def getActivity(self, gazePos, old_gazePos):
		"""Gets the user activity of each piece"""
		if self.connect4boardRect.collidepoint(gazePos) or ((gazePos[1]-15)//140 < 6 and (gazePos[0]-350)//140 < 9):
			if self.dwell_delay < self.maxDelay:
				self.dwell_delay += 1

		else:
			if self.dwell_delay > 0:
				self.dwell_delay -= 1

	def performAction(self, gazePos, old_gazePos):
		"""Sets clicked to True when there is user activity for a certain duration"""
		self.getActivity(gazePos, old_gazePos)
		if self.dwell_delay == self.maxDelay:
			self.mb = 1
			self.cursor = gazePos
			self.dwell_delay = 0
		else:
			self.mb = 0

	def main(self, cursor, mb):
		"Call this in while loop to run all needed components of the game"
		if self.backgroundValue == True:
			self.screen.blit(background, (0, -400))
			self.drawboard()
			self.backgroundValue = False

		if mb == 1:
			self.drawboard()
			self.gameplay(cursor, mb)
			self.checkwinner()
			self.gameover(cursor)

	def text(self, screen, text, size, color, location):
		"Used to display text on the screen"
		screen.blit(font.Font("Fonts/HelveticaNeue-Light.otf", size).render(str(text), True, color), location)

	def drawboard(self):
		"Draws the connect4 board and the chips on the screen"
		cover = Surface((1920, 1080), SRCALPHA)
		self.screen.blit(board, (350, 15))

		for x in range(9): 
			for y in range(6):
				if self.gameBoard[y][x] == "B":
					draw.circle(cover, (35, 107, 172, 230), (420+(x*140), 85+(y*140)), 60)
				elif self.gameBoard[y][x] == "P":
					draw.circle(cover, (123, 43, 157, 230), (420+(x*140), 85+(y*140)), 60)

		self.screen.blit(cover, (0, 0))

	def gameplay(self, cursor, mb):
		"This function does the move for the artificial inteeligence and also display the user and artififcial intelligences move"
		if self.currentTurn == 1:
			clickX = (cursor[0]-350)//140
		if self.currentTurn == 2:
			clickX = randint(0, 8)

		for y in range(0, 6):
			if self.gameBoard[y][clickX] != "_":
				break

			elif self.gameBoard[y][clickX] == "_":
				if self.currentTurn == 1:
					self.gameBoard[y][clickX] = "B"
				elif self.currentTurn == 2:
					self.gameBoard[y][clickX] = "P"

				self.gameBoard[y-1][clickX] = "_"

				self.drawboard()
				display.flip()

		for row in self.gameBoard:
			self.countBlue += row.count("B")
			self.countPurple += row.count("P")


		if self.currentTurn == 1:
			if (self.countBlue - self.countPurple) == 1:
				self.currentTurn = 2

		elif self.currentTurn == 2:
			if (self.countPurple - self.countBlue) == 0:
				self.currentTurn = 1

		self.countBlue = 0
		self.countPurple = 0

	def checkwinner(self):
		"Checks to see if any of the players have won. if yes which one"
		for y in range(6):
			for x in range(9):
				if self.gameBoard[y][x] != "_":	
					if x < 6 and y < 3:
						if self.gameBoard[y][x] == self.gameBoard[y+1][x+1] == self.gameBoard[y+2][x+2] == self.gameBoard[y+3][y+3]:
							self.winner = self.gameBoard[y][x]

					if x < 6:
						if self.gameBoard[y][x] == self.gameBoard[y][x+1] == self.gameBoard[y][x+2] == self.gameBoard[y][x+3]:
							self.winner = self.gameBoard[y][x]

					if y < 3:
						if self.gameBoard[y][x] == self.gameBoard[y+1][x] == self.gameBoard[y+2][x] == self.gameBoard[y+3][x]:
							self.winner = self.gameBoard[y][x]

	def gameover(self, cursor):
		"Displays the gameover screen and the user gets to chose whether or not they want to play again"
		if self.winner != "":
			cover = Surface((1260, 840), SRCALPHA)
			draw.rect(cover, (0, 0, 0, 225), (0, 0, 1260, 840))
			self.screen.blit(cover, (350, 15))
			if self.winner == "P":
				self.text(self.screen, "Purple Won", 160, (255, 255, 255), (640, 30))
			if self.winner == "B":
				self.text(self.screen, "Blue Won", 160, (255, 255, 255), (645, 30))

			self.screen.blit(button, (810, 300))
			self.text(self.screen, "Play Again", 60, (255, 255, 255), (850, 315))
			againRect = Rect(825, 315, 320, 80)

			if againRect.collidepoint(cursor):
				connect4.__init__(self, self.screen)






				
