__author__ = 'Masoud Harati'
__editor__ = 'Abhi Gupta'

"""
A simple game that will not take the user more than a couple of seconds to play. The game 
is multi-player and the user plays agains an AI.
"""

from pygame import *
from random import randint

class tictactoe:
	def __init__(self, screen):
		"initializes the tic tac toe game"
		self.gameboard = [["_", "_", "_"],
						  ["_", "_", "_"],
						  ["_", "_", "_"]]
		self.backgroundImage = image.load("imgs/TTTimgs/background.jpg").convert()
		self.screen = screen
		self.currentTurn = 1
		self.winner = ""
		self.oWon = 0
		self.xWon = 0
		self.countEmpty = 0
		self.blitBackground = True
		self.tictactoeRect = Rect(520, 15, 879, 879)
		self.cursor = 0
		self.mb = 0
		self.dwell_delay = 0
		self.maxDelay = 100

	def reinitialize(self):
		"Used for reinitialization. Allows the user to play again"
		self.gameboard = [["_", "_", "_"],
						  ["_", "_", "_"],
						  ["_", "_", "_"]]
		self.currentTurn = 1
		self.countEmpty = 0
		self.blitBackground = True
		self.winner = ""

	def getActivity(self, gazePos, old_gazePos):
		"""Gets the user activity of each piece"""
		if self.tictactoeRect.collidepoint(gazePos) or (gazePos[1]-15)//293 < 3 and (gazePos[0]-520)//293 < 3:
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


	def text(self, screen, text, size, color, location, boldValue):
		"used to display text on the screen"
		screen.blit(font.Font("Fonts/HelveticaNeue-Light.otf", size).render(str(text), boldValue, color), location)

	def main(self, mb, mpos):
		"main file call this in while loop"
		self.board()

		if mb == 1:
			self.gameplay(mb, mpos)
			self.checkWinner()

	def board(self):
		"Draws the tic tac toe board and puts a background"
		if self.blitBackground == True:
			self.screen.blit(self.backgroundImage, (0, 0))

			for column in range(2):
				draw.line(self.screen, (255, 255, 255, 150), (813+(column*293), 15), (813+(column*293), 895), 20)

			for row in range(2):
				draw.line(self.screen, (255, 255, 255, 150), (520, 308+(row*293)), (1400, 308+(row*293)), 20)

			self.text(self.screen, "X: %s" % self.xWon, 80, (255, 255, 255), (50, 50), False)
			self.text(self.screen, "O: %s" % self.oWon, 80, (255, 255, 255), (250, 50), False)

			self.blitBackground = False

	def drawMoves(self):
		"Draw the X and O onto the screen"
		cover = Surface((880, 880), SRCALPHA)

		for x in range(3):
			for y in range(3):

				if self.gameboard[y][x] == "X":
					draw.line(cover, (11, 81, 91, 200), (40+(x*293), 40+(y*293)), (253+(x*293), 253+(y*293)), 30)
					draw.line(cover, (11, 81, 91, 200), (40+(x*293), 253+(y*293)), (253+(x*293), 40+(y*293)), 30)

				elif self.gameboard[y][x] == "O":
					draw.circle(cover, (11, 81, 91, 200), (146+(x*293), 146+(y*293)), 120, 25)
					draw.circle(cover, (11, 81, 91, 200), (145+(x*293), 145+(y*293)), 120, 25)
					draw.circle(cover, (11, 81, 91, 200), (147+(x*293), 147+(y*293)), 120, 25)
					draw.circle(cover, (11, 81, 91, 200), (146+(x*293), 145+(y*293)), 120, 25)
					draw.circle(cover, (11, 81, 91, 200), (145+(x*293), 146+(y*293)), 120, 25)
					draw.circle(cover, (11, 81, 91, 200), (147+(x*293), 145+(y*293)), 120, 25)
					draw.circle(cover, (11, 81, 91, 200), (147+(x*293), 146+(y*293)), 120, 25)
					draw.circle(cover, (11, 81, 91, 200), (145+(x*293), 147+(y*293)), 120, 25)
					draw.circle(cover, (11, 81, 91, 200), (146+(x*293), 147+(y*293)), 120, 25)

		self.screen.blit(cover, (520, 15))

	def gameplay(self, mb, mpos):
		"Responsible for gameplay. Places X or O in the desired location"
		
		clickX = (mpos[0]-520)//293
		clickY = (mpos[1]-15)//293

		if self.currentTurn == 1 and self.gameboard[clickY][clickX] == "_":
			self.gameboard[clickY][clickX] = "X"
			self.drawMoves()
			self.gameplay(mb, mpos)
			self.currentTurn = 2

		elif self.currentTurn == 2 and self.gameboard[clickY][clickX] == "_":
			self.gameboard[clickY][clickX] = "O"
			self.drawMoves()
			self.gameplay(mb, mpos)
			self.currentTurn = 1

	def checkWinner(self):
		"Check to see if anyone has one and if yes who"
		if self.gameboard[0][0] == self.gameboard[0][1] == self.gameboard[0][2]:
			if self.gameboard[0][0] != "_":
				self.drawMoves()
				self.winner = self.gameboard[0][0]

		elif self.gameboard[0][0] == self.gameboard[1][0] == self.gameboard[2][0]:
			if self.gameboard[0][0] != "_":
				self.drawMoves()
				self.winner = self.gameboard[0][0]

		elif self.gameboard[0][0] == self.gameboard[1][1] == self.gameboard[2][2]:
			if self.gameboard[0][0] != "_":
				self.drawMoves()
				self.winner = self.gameboard[0][0]

		elif self.gameboard[0][1] == self.gameboard[1][1] == self.gameboard[2][1]:
			if self.gameboard[0][1] != "_":
				self.drawMoves()
				self.winner = self.gameboard[0][1]

		elif self.gameboard[0][2] == self.gameboard[1][2] == self.gameboard[2][2]:
			if self.gameboard[0][2] != "_":
				self.drawMoves()
				self.winner = self.gameboard[0][2]

		elif self.gameboard[1][0] == self.gameboard[1][1] == self.gameboard[1][2]:
			if self.gameboard[1][0] != "_":
				self.drawMoves()
				self.winner = self.gameboard[1][0]

		elif self.gameboard[2][0] == self.gameboard[2][1] == self.gameboard[2][2]:
			if self.gameboard[2][0] != "_":
				self.drawMoves()
				self.winner = self.gameboard[2][0]

		elif self.gameboard[0][2] == self.gameboard[1][1] == self.gameboard[2][0]:
			if self.gameboard[0][2] != "_":
				self.drawMoves()
				self.winner = self.gameboard[0][2]

		else:
			self.countEmpty = 0
			for checkY in range(3):
				for checkX in range(3):
					if self.gameboard[checkY][checkX] == "_":
						self.countEmpty += 1

			if self.countEmpty == 0:
				self.winner = "None"

		if self.winner != "":
			display.flip()
			time.wait(300)
			if self.winner == "X":
				self.xWon += 1
			elif self.winner == "O":
				self.oWon += 1

			self.reinitialize()

			
			
		

		



















