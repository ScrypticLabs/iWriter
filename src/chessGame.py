"""
The user is able to play a long-lasting game that requires him/her to formulate various strategies 
throughout the course. In order to make a move, the user has to first select the piece that they 
wish to play by looking at the location of the piece. Then, a series of possible paths that the 
chess piece can move is displayed. The selection is determined by the same method, location of 
gaze and dwell duration. Following the user’s turn, another player or the computer makes a move 
and the game continues.
"""

from pygame import *
from chessImage import *
from random import randint, shuffle
from math import hypot

class chessGame:
	def __init__(self):
		"Initialize the chessGame class"
		self.gameBoard = [['r', 'h', 'b', 'q', 'k', 'b', 'h', 'r'], 
						  ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
						  ['_', '_', '_', '_', '_', '_', '_', '_'],
						  ['_', '_', '_', '_', '_', '_', '_', '_'],
						  ['_', '_', '_', '_', '_', '_', '_', '_'],
						  ['_', '_', '_', '_', '_', '_', '_', '_'],
						  ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
						  ['R', 'H', 'B', 'Q', 'K', 'B', 'H', 'R']] 

		self.rects = [(645, 35, 105, 105), (540, 140, 105, 105), (540, 35, 105, 105), (645, 140, 105, 105), (645, 245, 105, 105), (540, 350, 105, 105), (540, 245, 105, 105), (645, 350, 105, 105), (645, 455, 105, 105), (540, 560, 105, 105), (540, 455, 105, 105), (645, 560, 105, 105), (645, 665, 105, 105), (540, 770, 105, 105), (540, 665, 105, 105), (645, 770, 105, 105), (855, 35, 105, 105), (750, 140, 105, 105), (750, 35, 105, 105), (855, 140, 105, 105), (855, 245, 105, 105), (750, 350, 105, 105), (750, 245, 105, 105), (855, 350, 105, 105), (855, 455, 105, 105), (750, 560, 105, 105), (750, 455, 105, 105), (855, 560, 105, 105), (855, 665, 105, 105), (750, 770, 105, 105), (750, 665, 105, 105), (855, 770, 105, 105), (1065, 35, 105, 105), (960, 140, 105, 105), (960, 35, 105, 105), (1065, 140, 105, 105), (1065, 245, 105, 105), (960, 350, 105, 105), (960, 245, 105, 105), (1065, 350, 105, 105), (1065, 455, 105, 105), (960, 560, 105, 105), (960, 455, 105, 105), (1065, 560, 105, 105), (1065, 665, 105, 105), (960, 770, 105, 105), (960, 665, 105, 105), (1065, 770, 105, 105), (1275, 35, 105, 105), (1170, 140, 105, 105), (1170, 35, 105, 105), (1275, 140, 105, 105), (1275, 245, 105, 105), (1170, 350, 105, 105), (1170, 245, 105, 105), (1275, 350, 105, 105), (1275, 455, 105, 105), (1170, 560, 105, 105), (1170, 455, 105, 105), (1275, 560, 105, 105), (1275, 665, 105, 105), (1170, 770, 105, 105), (1170, 665, 105, 105), (1275, 770, 105, 105)]


		self.abbrLocation = {"P": [25, 6],	
							 "R": [20, 10],
							 "H": [10, 8],
							 "B": [9, 10],
							 "Q": [10, 10],
							 "K": [10, 10],
							 "p": [22, 10],
							 "r": [20, 10],
							 "h": [10, 8],
							 "b": [9, 10],
							 "q": [10, 10],
							 "k": [10, 10]}

		self.abbrImage = {"P": whitePond, 
						  "R": whiteRook,
					   	  "H": whiteKnight,
						  "B": whiteBishop,
						  "Q": whiteQueen,
						  "K": whiteKing,
						  "p": blackPond,
						  "r": blackRook,
						  "h": blackKnight,
						  "b": blackBishop,
						  "q": blackQueen,
						  "k": blackKing}

		self.takenImage = {"P": small_whitePond, 
						   "R": small_whiteRook,
						   "H": small_whiteKnight,
					       "B": small_whiteBishop,
						   "Q": small_whiteQueen,
						   "K": small_whiteKing,
						   "p": small_blackPond,
						   "r": small_blackRook,
						   "h": small_blackKnight,
						   "b": small_blackBishop,
						   "q": small_blackQueen,
						   "k": small_blackKing}

		self.takenLocation = {"P": [12, 3],
							  "R": [10, 5],
							  "H": [5, 4],
							  "B": [5, 5],
							  "Q": [5, 5],
							  "K": [5, 5],
							  "p": [11, 5],
							  "r": [10, 5],
							  "h": [5, 4],
							  "b": [5, 5],
							  "q": [5, 5],
							  "k": [5, 5]}

		self.currentSide = "WHITE" 
		self.checkValue = False 
		self.checkmateValue = False 
		self.winner = "" 
		self.movePossible = [] 
		self.moves = [] 
		self.piecePos = (8, 8) 
		self.startImage = startImage.convert()
		self.boardImage = boardImage.convert() 
		self.pondX, self.pondY = 0, 0 
		self.startValue = True 
		self.numPlayers = 0 
		self.takenBlack = [] 
		self.takenWhite = []
		self.promoteTo = "" 
		self.highestPieceValue = 0 

		self.bgDrawn = False
		self.chessBoardRect = Rect(520,100,880,880)
		self.dwell_delay = 0
		self.maxDelay = 100

		self.mb = 0
		self.cursor = 0

	def getActivity(self, gazePos, old_gazePos):
		"""Gets the user activity of each piece"""
		if (self.chessBoardRect.collidepoint(gazePos) and self.startValue == True) or ((gazePos[1]-35)//105 < 8 and (gazePos[0]-540)//105 < 8):
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



	def drawBg(self, screen):
		if self.bgDrawn == False:
			screen.blit(image.load("imgs/chessImgs/flower.jpg").convert(), (0, 0))
			self.bgDrawn = True

	def start(self, screen, cursor, mb):
		"Start screen for chess"
		if self.startValue == True:
			screen.blit(self.startImage, (520, 15))
			self.text(screen, "CHESS", 250, (255, 255, 255), (550, 15), False)

			screen.blit(buttonImage, (780, 415)) # Single PLayer Button
			self.text(screen, "Single Player", 50, (255, 255, 255), (815, 440), True)
			singleButton = Rect(795, 430, 320, 80) # Rect for single player button

			screen.blit(buttonImage, (780, 515)) # Two-Player Button
			self.text(screen, "Two Player", 50, (255, 255, 255), (830, 540), True)
			twoButton = Rect(795, 530, 320, 80)

			if mb == 1:
				if singleButton.collidepoint(cursor):
					self.numPlayers = 1
					self.startValue = False
					screen.blit(self.boardImage, (520, 15)) # Chessboard Image

				if twoButton.collidepoint(cursor):
					self.numPlayers = 2
					self.startValue = False
					screen.blit(self.boardImage, (520, 15)) # Chessboard Image

	def main(self, screen, mb, cursor):
		"Call to play chess"
		self.drawBg(screen)
		self.start(screen, cursor, mb)
		if mb == 1 and not self.startValue:
			clickX, clickY = (cursor[0]-540)//105, (cursor[1]-35)//105
			screen.blit(self.boardImage, (520, 15)) # Chessboard Image
			self.knightMove(screen, clickX, clickY, cursor)
			self.pondMove(screen, clickX, clickY, cursor)
			self.rookMove(screen, clickX, clickY, cursor)
			self.bishopMove(screen, clickX, clickY, cursor)
			self.kingMove(screen, clickX, clickY, cursor)
			self.queenMove(screen, clickX, clickY, cursor)
			self.noCollide(screen, self.movePossible, self.gameBoard, False)
			self.collide(screen, self.movePossible, self.gameBoard, self.currentSide, False)
			self.drawPiece(screen)
			self.check(screen, cursor)
			self.movePiece(screen, cursor, clickX, clickY)
			self.ai(screen, cursor)
			self.promotion(screen, mb, cursor, clickX, clickY)

#-------------------------------------------------------------------------------- Graphics ------------------------------------------------------------------------------------
	def text(self, screen, text, size, color, location, boldValue):
		"Use to Write text on the screen"
		screen.blit(font.Font("fonts/HelveticaNeue-Light.otf", size).render(str(text), boldValue, color), location)

	def drawPiece(self, screen):
		"Draws all the chess pieces onto the chess board"
		for y in range(8):
			for x in range(8):
				if self.gameBoard[y][x] == "_":
					pass
				else:
					screen.blit(self.abbrImage[self.gameBoard[y][x]], (self.abbrLocation[self.gameBoard[y][x]][0]+(x*105)+535, self.abbrLocation[self.gameBoard[y][x]][1]+(y*105)+30)) # Blits the chess pieces in the centered of the square
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------- Game Pieces ---------------------------------------------------------------------------------
	def knightMove(self, screen, clickX, clickY, mpos):
		"Makes a list of all the possible moves for the Knight"
		if self.gameBoard[clickY][clickX] == "h" and self.currentSide == "BLACK" or self.gameBoard[clickY][clickX] == "H" and self.currentSide == "WHITE":
			self.piecePos = (clickX, clickY)
			self.moves = []
			self.movePossible = []
			
			for x in range(0, 8):
				for y in range(0, 8):
					if abs(x-clickX) == 1 and abs(y-clickY) == 2 or abs(x-clickX) == 2 and abs(y-clickY) == 1:
						self.movePossible.append((x, y))

	def pondMove(self, screen, clickX, clickY, mpos):
		"Makes a list of all the possible moves for the Pond"
		if self.gameBoard[clickY][clickX] == "p" and self.currentSide == "BLACK" or self.gameBoard[clickY][clickX] == "P" and self.currentSide == "WHITE":
			self.piecePos = (clickX, clickY)
			self.moves = []
			self.movePossible = []

			
			if self.gameBoard[clickY-1][clickX] == "_":
				self.movePossible.append((clickX, clickY-1))
				self.pondX, self.pondY = (mpos[0]-540)//105, (mpos[1]-35)//105
				if clickY == 6 and self.gameBoard[clickY-2][clickX] == "_":
					self.movePossible.append((clickX, clickY-2))
					self.pondX, self.pondY = (mpos[0]-540)//105, (mpos[1]-35)//105
			try: 
				if self.gameBoard[clickY-1][clickX-1] != "_":
					self.movePossible.append((clickX-1, clickY-1))
					self.pondX, self.pondY = (mpos[0]-540)//105, (mpos[1]-35)//105
				if self.gameBoard[clickY-1][clickX+1] != "_":
					self.movePossible.append((clickX+1, clickY-1))
					self.pondX, self.pondY = (mpos[0]-540)//105, (mpos[1]-35)//105
			except:
				pass

	def rookMove(self, screen, clickX, clickY, mpos):
		"Makes a list of all the possible moves for the Rook"
		if self.gameBoard[clickY][clickX] == "r" and self.currentSide == "BLACK" or self.gameBoard[clickY][clickX] == "R" and self.currentSide == "WHITE":
			self.piecePos = (clickX, clickY)
			self.moves = []
			self.movePossible = []

			for movesUp in range(1, 8):
				if clickY-movesUp < 0:
					break
				if self.gameBoard[clickY-movesUp][clickX].islower() and self.currentSide == "BLACK" or self.gameBoard[clickY-movesUp][clickX].isupper() and self.currentSide == "WHITE":
					break
				self.movePossible.append((clickX, clickY-movesUp))
				if self.gameBoard[clickY-movesUp][clickX].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY-movesUp][clickX].isupper() and self.currentSide == "BLACK":
					break

			for movesDown in range(1, 8):
				if clickY+movesDown > 7:
					break
				if self.gameBoard[clickY+movesDown][clickX].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY+movesDown][clickX].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX, clickY+movesDown))
				if self.gameBoard[clickY+movesDown][clickX].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY+movesDown][clickX].isupper() and self.currentSide == "BLACK":
					break

			for movesRight in range(1, 8):
				if clickX+movesRight > 7:
					break
				if self.gameBoard[clickY][clickX+movesRight].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY][clickX+movesRight].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX+movesRight, clickY))
				if self.gameBoard[clickY][clickX+movesRight].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY][clickX+movesRight].isupper() and self.currentSide == "BLACK":
					break

			for movesLeft in range(1, 8):
				if clickX-movesLeft < 0:
					break
				if self.gameBoard[clickY][clickX-movesLeft].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY][clickX-movesLeft].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX-movesLeft, clickY))
				if self.gameBoard[clickY][clickX-movesLeft].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY][clickX-movesLeft].isupper() and self.currentSide == "BLACK":
					break

	def bishopMove(self, screen, clickX, clickY, mpos):
		"Makes a list of all the possible moves for the Bishop"
		if self.gameBoard[clickY][clickX] == "b" and self.currentSide == "BLACK" or self.gameBoard[clickY][clickX] == "B" and self.currentSide == "WHITE":
			self.piecePos = (clickX, clickY)
			self.moves = []
			self.movePossible = []

			for upLeft in range(1, 8):
				if clickX-upLeft < 0 or clickY-upLeft < 0:
					break
				if self.gameBoard[clickY-upLeft][clickX-upLeft].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY-upLeft][clickX-upLeft].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX-upLeft, clickY-upLeft))
				if self.gameBoard[clickY-upLeft][clickX-upLeft].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY-upLeft][clickX-upLeft].isupper() and self.currentSide == "BLACK":
					break

			for downRight in range(1, 8):
				if clickX+downRight > 7 or clickY+downRight > 7:
					break
				if self.gameBoard[clickY+downRight][clickX+downRight].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY+downRight][clickX+downRight].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX+downRight, clickY+downRight))
				if self.gameBoard[clickY+downRight][clickX+downRight].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY+downRight][clickX+downRight].isupper() and self.currentSide == "BLACK":
					break

			for downLeft in range(1, 8):
				if clickX-downLeft < 0 or clickY+downLeft > 7:
					break 
				if self.gameBoard[clickY+downLeft][clickX-downLeft].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY+downLeft][clickX-downLeft].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX-downLeft, clickY+downLeft))
				if self.gameBoard[clickY+downLeft][clickX-downLeft].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY+downLeft][clickX-downLeft].isupper() and self.currentSide == "BLACK":
					break

			for upRight in range(1, 8):
				if clickX+upRight > 7 or clickY-upRight < 0:
					break
				if self.gameBoard[clickY-upRight][clickX+upRight].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY-upRight][clickX+upRight].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX+upRight, clickY-upRight))
				if self.gameBoard[clickY-upRight][clickX+upRight].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY-upRight][clickX+upRight].isupper() and self.currentSide == "BLACK":
					break

	def kingMove(self, screen, clickX, clickY, mpos):
		"Makes a list of all the posiible moves for the King"
		if self.gameBoard[clickY][clickX] == "k" and self.currentSide == "BLACK" or self.gameBoard[clickY][clickX] == "K" and self.currentSide == "WHITE":
			self.piecePos = (clickX, clickY)
			self.moves = []
			self.movePossible = []

			if clickX+1 <= 7 and clickY+1 <= 7:
				self.movePossible.append((clickX+1, clickY+1))
			if clickX-1 >= 0 and clickY-1 >= 0:
				self.movePossible.append((clickX-1, clickY-1))
			if clickX+1 <= 7 and clickY-1 >= 0:
				self.movePossible.append((clickX+1, clickY-1))
			if clickX-1 >= 0 and clickY+1 <= 7:
				self.movePossible.append((clickX-1, clickY+1))
			if clickX+1 <= 7:
				self.movePossible.append((clickX+1, clickY))
			if clickX-1 >= 0:
				self.movePossible.append((clickX-1, clickY))
			if clickY-1 >= 0:
				self.movePossible.append((clickX, clickY-1))
			if clickY+1 <= 7:
				self.movePossible.append((clickX, clickY+1))

	def queenMove(self, screen, clickX, clickY, mpos):
		"Makes a list of all the possible moves for the Queen"
		if self.gameBoard[clickY][clickX] == "q" and self.currentSide == "BLACK" or self.gameBoard[clickY][clickX] == "Q" and self.currentSide == "WHITE":
			self.piecePos = (clickX, clickY)
			self.moves = []
			self.movePossible = []

			for movesUp in range(1, 8):
				if clickY-movesUp < 0:
					break
				if self.gameBoard[clickY-movesUp][clickX].islower() and self.currentSide == "BLACK" or self.gameBoard[clickY-movesUp][clickX].isupper() and self.currentSide == "WHITE":
					break
				self.movePossible.append((clickX, clickY-movesUp))
				if self.gameBoard[clickY-movesUp][clickX].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY-movesUp][clickX].isupper() and self.currentSide == "BLACK":
					break

			for movesDown in range(1, 8):
				if clickY+movesDown > 7:
					break
				if self.gameBoard[clickY+movesDown][clickX].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY+movesDown][clickX].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX, clickY+movesDown))
				if self.gameBoard[clickY+movesDown][clickX].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY+movesDown][clickX].isupper() and self.currentSide == "BLACK":
					break

			for movesRight in range(1, 8):
				if clickX+movesRight > 7:
					break
				if self.gameBoard[clickY][clickX+movesRight].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY][clickX+movesRight].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX+movesRight, clickY))
				if self.gameBoard[clickY][clickX+movesRight].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY][clickX+movesRight].isupper() and self.currentSide == "BLACK":
					break

			for movesLeft in range(1, 8):
				if clickX-movesLeft < 0:
					break
				if self.gameBoard[clickY][clickX-movesLeft].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY][clickX-movesLeft].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX-movesLeft, clickY))
				if self.gameBoard[clickY][clickX-movesLeft].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY][clickX-movesLeft].isupper() and self.currentSide == "BLACK":
					break

			for upLeft in range(1, 8):
				if clickX-upLeft < 0 or clickY-upLeft < 0:
					break
				if self.gameBoard[clickY-upLeft][clickX-upLeft].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY-upLeft][clickX-upLeft].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX-upLeft, clickY-upLeft))
				if self.gameBoard[clickY-upLeft][clickX-upLeft].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY-upLeft][clickX-upLeft].isupper() and self.currentSide == "BLACK":
					break

			for downRight in range(1, 8):
				if clickX+downRight > 7 or clickY+downRight > 7:
					break
				if self.gameBoard[clickY+downRight][clickX+downRight].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY+downRight][clickX+downRight].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX+downRight, clickY+downRight))
				if self.gameBoard[clickY+downRight][clickX+downRight].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY+downRight][clickX+downRight].isupper() and self.currentSide == "BLACK":
					break

			for downLeft in range(1, 8):
				if clickX-downLeft < 0 or clickY+downLeft > 7:
					break
				if self.gameBoard[clickY+downLeft][clickX-downLeft].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY+downLeft][clickX-downLeft].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX-downLeft, clickY+downLeft))
				if self.gameBoard[clickY+downLeft][clickX-downLeft].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY+downLeft][clickX-downLeft].isupper() and self.currentSide == "BLACK":
					break

			for upRight in range(1, 8):
				if clickX+upRight > 7 or clickY-upRight < 0:
					break
				if self.gameBoard[clickY-upRight][clickX+upRight].isupper() and self.currentSide == "WHITE" or self.gameBoard[clickY-upRight][clickX+upRight].islower() and self.currentSide == "BLACK":
					break
				self.movePossible.append((clickX+upRight, clickY-upRight))
				if self.gameBoard[clickY-upRight][clickX+upRight].islower() and self.currentSide == "WHITE" or self.gameBoard[clickY-upRight][clickX+upRight].isupper() and self.currentSide == "BLACK":
					break
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------- Game Play --------------------------------------------------------------------------------
	def noCollide(self, mainSurface, locations, board, drawRect):
		"Finds the possible positions of the chess piece when it doesn't hit another chess piece"
		coverAlpha = Surface((1920, 1080), SRCALPHA)
		for location in locations:
			if board[location[1]][location[0]] == "_" and location[0] in range(0, 8) and location[1] in range(0, 8):
				if self.numPlayers == 2 and drawRect == False or self.currentSide == "WHITE" and drawRect == False:
					draw.rect(coverAlpha, (255, 255, 255, 255), ((location[0]*105)+540, (location[1]*105)+35, 105, 105))
					draw.rect(coverAlpha, (255, 0, 0, 150), ((location[0]*105)+540, (location[1]*105)+35, 105, 105))
				self.moves.append(location)
		mainSurface.blit(coverAlpha, (0, 0))
	
	def collide(self, mainSurface, locations, board, turn, drawRect):
		"Finds the possible positions of the chess piece when it hits another chess piece"
		coverAlpha = Surface((1920, 1080), SRCALPHA)
		for location in locations:
			if board[location[1]][location[0]] != "_" and location[0] in range(0, 8) and location[1] in range(0, 8):
				if board[location[1]][location[0]].isupper() and turn == "BLACK":
					if self.numPlayers == 2 and drawRect == False:
						draw.rect(coverAlpha, (255, 255, 255, 255), ((location[0]*105)+540, (location[1]*105)+35, 105, 105))
						draw.rect(coverAlpha, (0, 255, 0, 150), ((location[0]*105)+540, (location[1]*105)+35, 105, 105))
					self.moves.append(location)
				elif board[location[1]][location[0]].islower() and turn == "WHITE":
					draw.rect(coverAlpha, (255, 255, 255, 255), ((location[0]*105)+540, (location[1]*105)+35, 105, 105))
					draw.rect(coverAlpha, (0, 255, 0, 150), ((location[0]*105)+540, (location[1]*105)+35, 105, 105))
					self.moves.append(location)
		mainSurface.blit(coverAlpha, (0, 0))

	def movePiece(self, screen, mpos, clickX, clickY, aiX = 0, aiY = 0):
		"Moves the selected chess piece to the desired position"
		if self.numPlayers == 1 and self.currentSide == "BLACK":
			x = aiX
			y = aiY
			if self.gameBoard[aiY][aiX].isalpha():
				self.takenWhite.append(self.gameBoard[aiY][aiX])
			self.gameBoard[y][x] = self.gameBoard[clickY][clickX]
			self.gameBoard[clickY][clickX] = "_"
			count = 0
			self.gameBoard = self.gameBoard[::-1]
			for row in self.gameBoard:
				self.gameBoard[count] = row[::-1]
				count += 1
		
			screen.blit(self.boardImage, (520, 15))
			self.drawPiece(screen)

			if self.currentSide == "BLACK":
				self.currentSide = "WHITE"
			elif self.currentSide == "WHITE":
				self.currentSide = "BLACK"
			self.moves = []
			self.movePossible = []
			self.check(screen, mpos)
			self.taken(screen)

			
		if self.numPlayers == 2 or self.currentSide == "WHITE":
			x = (mpos[0]-540)//105
			y = (mpos[1]-35)//105
			if (x, y) in self.moves:
				if self.gameBoard[y][x].isalpha():
					if self.gameBoard[y][x].isupper():
						self.takenWhite.append(self.gameBoard[y][x])
					elif self.gameBoard[y][x].islower():
						self.takenBlack.append(self.gameBoard[y][x])

				self.gameBoard[y][x] = self.gameBoard[self.piecePos[1]][self.piecePos[0]]
				self.gameBoard[self.piecePos[1]][self.piecePos[0]] = "_"

				count = 0
				self.gameBoard = self.gameBoard[::-1]
				for row in self.gameBoard:
					self.gameBoard[count] = row[::-1]
					count += 1
			
				screen.blit(self.boardImage, (520, 15)) 
				self.drawPiece(screen)

				if self.currentSide == "BLACK":
					self.currentSide = "WHITE"
				elif self.currentSide == "WHITE":
					self.currentSide = "BLACK"
				self.moves = []
				self.movePossible = []
				self.check(screen, mpos)
				self.taken(screen)

	def taken(self, screen):
		"Displays the taken pieces on the sides of the screen"
		count = 0
		for white in self.takenWhite:
			screen.blit(self.takenImage[white], (self.takenLocation[white][0]+460, self.takenLocation[white][1]+(count*50)+50))
			count += 1

		count = 0
		for black in self.takenBlack:
			screen.blit(self.takenImage[black], (self.takenLocation[black][0]+1400, self.takenLocation[black][1]+(count*50)+50))
			count += 1

	def promotion(self, screen, mb, cursor, clickX, clickY):
		"Used for promotions. when pond reaches the end of the screen"
		for x in range(8):
			if self.numPlayers == 1 and self.gameBoard[7][x] == "p":
				self.gameBoard[7][x] = "q"
				screen.blit(self.boardImage, (520, 15))
				self.drawPiece(screen)
			elif self.gameBoard[0][x] == "P":
				draw.rect(screen, (200, 200, 200), (520, 15, 880, 880))
				self.text(screen, "Promotion", 100, (0, 0, 0), (740, 45), True)
				screen.blit(buttonImage, (1050, 785))
				self.text(screen, "Select", 60, (255, 255, 255), (1145, 800), True)
				buttonRect = Rect(1065, 800, 320, 80)

				knightRect = draw.rect(screen, (0, 0, 0), (600, 265, 180, 300), 2)
				bishopRect = draw.rect(screen, (0, 0, 0), (780, 265, 180, 300), 2)
				rookRect = draw.rect(screen, (0, 0, 0), (960, 265, 180, 300), 2)
				queenRect = draw.rect(screen, (0, 0, 0), (1140, 265, 180, 300), 2)

				self.text(screen, "Knight", 50, (0, 0, 0), (620, 445), True)
				self.text(screen, "Bishop", 50, (0, 0, 0), (795, 445), True)
				self.text(screen, "Rook", 50, (0, 0, 0), (990, 445), True)
				self.text(screen, "Queen", 50, (0, 0, 0), (1160, 445), True)

				screen.blit(whiteKnight, (640, 295))
				screen.blit(whiteBishop, (822, 295))
				screen.blit(whiteRook, (1010, 295))
				screen.blit(whiteQueen, (1180, 295))

				if mb == 1:
					if knightRect.collidepoint(cursor):
						self.promoteTo = "Knight"
					elif bishopRect.collidepoint(cursor):
						self.promoteTo = "Bishop"
					elif rookRect.collidepoint(cursor):
						self.promoteTo = "Rook"
					elif queenRect.collidepoint(cursor):
						self.promoteTo = "Queen"
					elif buttonRect.collidepoint(cursor) and self.promoteTo != "":
						if self.promoteTo == "Knight":
							self.gameBoard[0][x] = "H"
							self.promoteTo = ""
						if self.promoteTo == "Bishop":
							self.gameBoard[0][x] = "B"
							self.promoteTo = ""
						if self.promoteTo == "Rook":
							self.gameBoard[0][x] = "R"
							self.promoteTo = ""
						if self.promoteTo == "Queen":
							self.gameBoard[0][x] = "Q"
							self.promoteTo = ""

			elif self.currentSide  == "BLACK" and self.gameBoard[7][x] == "P" or self.currentSide == "WHITE" and self.gameBoard[7][x] == "p":
				draw.rect(screen, (200, 200, 200), (520, 15, 880, 880))
				self.text(screen, "Promotion", 100, (0, 0, 0), (740, 45), True)
				screen.blit(buttonImage, (1050, 785))
				self.text(screen, "Select", 60, (255, 255, 255), (1145, 800), True)
				buttonRect = Rect(1065, 800, 320, 80)

				knightRect = draw.rect(screen, (0, 0, 0), (600, 265, 180, 300), 2)
				bishopRect = draw.rect(screen, (0, 0, 0), (780, 265, 180, 300), 2)
				rookRect = draw.rect(screen, (0, 0, 0), (960, 265, 180, 300), 2)
				queenRect = draw.rect(screen, (0, 0, 0), (1140, 265, 180, 300), 2)

				self.text(screen, "Knight", 50, (0, 0, 0), (620, 445), True)
				self.text(screen, "Bishop", 50, (0, 0, 0), (795, 445), True)
				self.text(screen, "Rook", 50, (0, 0, 0), (990, 445), True)
				self.text(screen, "Queen", 50, (0, 0, 0), (1160, 445), True)

				if self.currentSide == "BLACK":
					screen.blit(whiteKnight, (640, 295))
					screen.blit(whiteBishop, (822, 295))
					screen.blit(whiteRook, (1010, 295))
					screen.blit(whiteQueen, (1180, 295))

				elif self.currentSide == "WHITE":
					screen.blit(blackKnight, (640, 295))
					screen.blit(blackBishop, (822, 295))
					screen.blit(blackRook, (1010, 295))
					screen.blit(blackQueen, (1180, 295))

				if knightRect.collidepoint(cursor):
					self.promoteTo = "Knight"
				elif bishopRect.collidepoint(cursor):
					self.promoteTo = "Bishop"
				elif rookRect.collidepoint(cursor):
					self.promoteTo = "Rook"
				elif queenRect.collidepoint(cursor):
					self.promoteTo = "Queen"
				elif buttonRect.collidepoint(cursor) and self.promoteTo != "":
					if self.currentSide == "BLACK":
						if self.promoteTo == "Knight":
							self.gameBoard[7][x] = "H"
							self.promoteTo = ""
						if self.promoteTo == "Bishop":
							self.gameBoard[7][x] = "B"
							self.promoteTo = ""
						if self.promoteTo == "Rook":
							self.gameBoard[7][x] = "R"
							self.promoteTo = ""
						if self.promoteTo == "Queen":
							self.gameBoard[7][x] = "Q"
							self.promoteTo = ""

					else:
						if self.promoteTo == "Knight":
							self.gameBoard[7][x] = "h"
							self.promoteTo = ""
						if self.promoteTo == "Bishop":
							self.gameBoard[7][x] = "b"
							self.promoteTo = ""
						if self.promoteTo == "Rook":
							self.gameBoard[7][x] = "r"
							self.promoteTo = ""
						if self.promoteTo == "Queen":
							self.gameBoard[7][x] = "q"
							self.promoteTo = ""

	def check(self, screen, cursor):
		"Checks if the king is out of the game to end game"
		if "K" in self.takenWhite:
			self.gameover(screen, cursor, "Black")
		elif "k" in self.takenBlack:
			self.gameover(screen, cursor, "White")

	def gameover(self, screen, mpos, winner):
		"Game over screen which allows the user to either go to the home screen or play again"
		cover = Surface((880, 880), SRCALPHA)
		draw.rect(cover, (0, 0, 0, 230), (0, 0, 880, 880))
		screen.blit(cover, (520, 15))
		self.text(screen, "%s Won!" % winner, 150, (255, 255, 255), (600, 15), True)

		screen.blit(buttonImage, (790, 315))
		self.text(screen, "Play Again", 65, (255, 255, 255), (820, 330), True)
		againRect = Rect(805, 330, 320, 80)

		if againRect.collidepoint(mpos):
			self.__init__()

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------- Artificial Intelligence ------------------------------------------------------------------------
	def ai(self, screen, cursor):
		"The Artificial Intelligence choses its moves here"
		if self.currentSide == "BLACK" and self.numPlayers == 1:
			for px in range(8):
				for py in range(8):
					if self.gameBoard[py][px].isalpha() and self.gameBoard[py][px].islower():
						aiPiece = {"p": self.pondMove(screen, px, py, cursor),
								   "r": self.rookMove(screen, px, py, cursor),
								   "h": self.knightMove(screen, px, py, cursor),
								   "b": self.bishopMove(screen, px, py, cursor),
								   "q": self.queenMove(screen, px, py, cursor),
								   "k": self.kingMove(screen, px, py, cursor)}

						pieceValue = {"P": 1,
									  "R": 5,
									  "H": 3,
									  "B": 3,
									  "Q": 9,
									  "K": 10,
									  "p": 0,
									  "r": 0,
									  "h": 0,
									  "b": 0,
									  "q": 0,
									  "k": 0,
									  "_": 0}

						aiPiece[self.gameBoard[py][px]]
						self.noCollide(screen, self.movePossible, self.gameBoard, True)
						self.collide(screen, self.movePossible, self.gameBoard, self.currentSide, True)
						if len(self.movePossible) > 0:
							for move in self.moves:
								if pieceValue[self.gameBoard[move[1]][move[0]]] > self.highestPieceValue and self.gameBoard[move[1]][move[0]].isupper():
									self.highestPieceValue = pieceValue[self.gameBoard[move[1]][move[0]]]
									highestPiecePos = (move[0], move[1])
									aiPiecePos = (px, py)
						self.moves = []
						self.movePossible = []

			if self.highestPieceValue > 0:
				aiPiece[self.gameBoard[aiPiecePos[1]][aiPiecePos[0]]]
				self.noCollide(screen, self.movePossible, self.gameBoard, True)
				self.collide(screen, self.movePossible, self.gameBoard, self.currentSide, True)
				self.drawPiece(screen)
				self.movePiece(screen, cursor, aiPiecePos[0], aiPiecePos[1], highestPiecePos[0], highestPiecePos[1])

			if self.highestPieceValue == 0:
				while True:
					if self.highestPieceValue > 0:
						break
					x = randint(0, 7)
					y = randint(0, 7)
					if self.gameBoard[y][x].isalpha() and self.gameBoard[y][x].islower():
						aiPiece = {"p": self.pondMove(screen, x, y, cursor),
								   "r": self.rookMove(screen, x, y, cursor),
								   "h": self.knightMove(screen, x, y, cursor),
								   "b": self.bishopMove(screen, x, y, cursor),
								   "q": self.queenMove(screen, x, y, cursor),
								   "k": self.kingMove(screen, x, y, cursor)}
						aiPiece[self.gameBoard[y][x]]
						self.noCollide(screen, self.movePossible, self.gameBoard, True)
						self.collide(screen, self.movePossible, self.gameBoard, self.currentSide, True)
					
					if len(self.moves) > 0:
						shuffle(self.moves)
						chosenMove = self.moves[0]
						self.drawPiece(screen)
						self.movePiece(screen, cursor, x, y, chosenMove[0], chosenMove[1])
						break
			self.highestPieceValue = 0
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------





			













			