#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Abhi
# @Date:   2015-04-14 17:47:10
# @Last Modified by:   Abhi
# @Last Modified time: 2015-06-21 23:48:35

"""
iWriter is a platform for games and other productivity applications that can be interfaced with the eyes or the cursor. 
It is specfiically designed for ALS patients who suffer from a poorer quality of life and hence, with this program
patients and users can create their own web-enabled accounts, write notes, play games such as chess, pong, connect4, etc.
and most importantly, communicate by typing on a virtual keyboard (speech-enabled). Users can also send text 
messages to specified numbers but currently, there is no GUI for the messages app yet. Mail is another outlet for exapansion
and the program has been designed so that several tiles can be added to the home screen to diverse iWriter and provide 
the user with a better and more productive experience.
"""

from pygame import *
from random import *
from functions import *
import GazePlotter2 as GazePlotter
#-----CALIBRATION IMPORTS----
from pygame import gfxdraw
from math import *
from peyetribe import *
from pygame import time

#-----INITIALIZE SCREEN-----
setScreen(6,29)
#init() CANNOT BE USED WITH EYE TRACKERs
flags = FULLSCREEN | DOUBLEBUF | HWSURFACE
screen = display.set_mode((1920,1080), flags)
display.set_caption("PyEye")
running = True
font.init()
event.set_allowed([QUIT, KEYDOWN, KEYUP])

#-----INITIALIZE FPS-----
myClock = time.Clock()
#-----INITIALIZE CLASSES-----

#----------------------------------CALIBRATION ONLY-----------------------------------
def drawStar(screen, col, x, y, size, filled = 0):
	'''Draws a star that is proportional to the specified size'''
	verts = [(x,y-40*size),(x+10*size,y-10*size)]			#top center cone
	verts += [(x+40*size,y-10*size),(x+15*size,y+10*size)]	#top right cone
	verts += [(x+25*size,y+40*size),(x,y+20*size)]			#bottom right cone
	verts += [(x-25*size,y+40*size),(x-15*size,y+10*size)]	#bottom left cone
	verts += [(x-40*size,y-10*size),(x-10*size,y-10*size)]	#top leftcone
	draw.polygon(screen, col, verts, filled)

def circleCollidepoint(cx, cy, mx, my, radius): 
	"""Checks collision with a circle with circle using distance formula"""
	dist = hypot(mx-cx, my-cy)
	if dist <= radius:  return True
	else:   return False

def dist(p1,p2):
	"""Finds the distance between the old and new position"""
	return hypot(p1[0]-p2[0],p1[1]-p2[1])

def normal(x,y):
	"""Normalizes the movement"""
	d = hypot(x,y)
	return x/d,y/d

def add(v1,v2):
	"""adds vectors"""
	v1[0]+=v2[0]
	v1[1]+=v2[1]

def mult(v1,m):
	"""multiplies two vector"""
	return v1[0]*m,v1[1]*m

def intt(tup):
	"""Returns a tuple components as ints"""
	return (int(tup[0]),int(tup[1]))

class Calibration:
	"""This class is used to calibrate the eye tracker"""
	def __init__(self, surface, points = 9):
		"Initializes the variables for the class Calibration"
		self.resX, self.resY = self.getRes(surface)
		self.background = Surface((self.resX,self.resY), SRCALPHA)
		self.backgroundImg = image.load("imgs/background.png").convert()
		self.background_alpha = 200
		self.text_alpha = 0
		self.text_colours = keyBoard(surface).genGradient(primeCol = (13,47,48), duration = 100, delay = 2)
		self.display_title = True
		self.stop_blitting = False
		self.caption = True
		# -----------------------------------------
		self.calibPoints = points		

	def getRes(self, surface):
		"Gets the resolution of the screen"
		return surface.get_size()

	def getSpacing(self, text, Size, font_size):
		"""Finds the socing for the font"""
		space = font.Font('fonts/HelveNueThin/HelveticaNeueThn.ttf', font_size).size(text)
		return (Size-space[0])//2

	def drawBackground(self, surface, title="CATCH ME"):
		"""Draws the background for catch me"""
		surface.blit(self.backgroundImg, (0,0))
		draw.rect(self.background, (1,10,21,self.background_alpha), (0,0,self.resX,self.resY))

	def incrementCounter(self):
		"""Counter for the alpha value of the background"""
		if self.display_title:
			self.background_alpha += 1 if self.background_alpha <= 250 else 0
		if self.background_alpha >= 226 and self.display_title:
			self.text_alpha += 2
		if self.display_title == False:
		 	self.text_alpha -= 2
		if self.display_title == False and self.text_alpha <= 150:
		 	self.background_alpha -= 2 if self.background_alpha >= 240 else 0

	def drawLevel(self, surface, level = "CALIBRATION", caption = "Follow the circle.", gameover = False):
		"""Shows Follow the circle which is used for calibration."""
		text = level
		hint = caption
		if self.text_alpha >= len(self.text_colours):	
			self.text_alpha = len(self.text_colours)-1
			self.display_title = False
		if self.text_alpha <= 0 and self.display_title == False:
			self.stop_blitting = True
			self.text_alpha = 0
		if self.display_title == False and self.stop_blitting == False:
			self.drawBackground(surface, level)
			if gameover == False:
				makeText(self.background, hint, 90, self.text_colours[self.text_alpha], None, self.getSpacing(hint, self.resX, 90), self.resY//2-150)
			surface.blit(self.background, (0,0))
		if self.display_title:
			self.drawBackground(surface, level)
			makeText(self.background, text, 250, self.text_colours[self.text_alpha], None, self.getSpacing(text, self.resX, 250), self.resY//2-200)
			surface.blit(self.background, (0,0))
		if self.stop_blitting:
			if self.caption:
				self.drawBackground(surface, level)
				surface.blit(self.background, (0,0))
				self.caption = False
			if self.background_alpha > 220:
				self.drawBackground(surface, level)
				surface.blit(self.background, (0,0))
			return "LEVEL DRAWN"

	def resetVars(self):
		"""Resets the Variables"""
		self.background_alpha = 200
		self.text_alpha = 0
		self.display_title = True
		self.stop_blitting = False
		self.caption = True

	def getStats(self, score):
		"""Gets the score of the user"""
		self.stats['score'] += score

	def drawStats(self, surface, countdown, title = "CATCH ME"):
		"""Displays the statistics to the user"""
		draw.rect(self.statsBar, (26,157,130,200), (0,0,self.resX, 40))
		draw.line(self.statsBar, (255,255,255), (0,40), (self.resX,40))
		makeText(self.statsBar, title, 20, (222,222,222), None, 20, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		makeText(self.statsBar, "Score: %s" % str(self.stats['score']), 20, (222,222,222), None, self.resX-300, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		makeText(self.statsBar, "Time: %ss" % str(round(countdown,2)), 20, (222,222,222), None, self.resX-145, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		surface.blit(self.statsBar, (0,0))

class Dot:
	"""Is a small game that is used for calibration of the eye-tracker"""
	def __init__(self, surface, screen_size):
		"""initializes the Dot class"""
		self.screen_size = screen_size
		self.calibpoints = []
		self.calibrated = False
		self.calibresult = None

		self.gridX = []
		self.gridY = []

		self.getPoints(screen_size)
		#--------------------
		self.circ = self.calibpoints[0]
		self.dest = (200,200)
		self.old_dest = self.dest
		self.speed = 0
		self.maxSpeed = 40
		self.maxAccel = 60
		#--------------------
		self.calibpoint = 1
		self.calibpoint_size = 8.0

		self.decreaseSize = False
		self.decrease = True
		self.decreaseAgain = False
		self.calibpoint_speed = 1

		self.initCover = False
		self.cover = None

		self.postCalib_drawn = False

		self.start_new_calibration = True
		self.startCalibratingDot = False
		self.stopCalibratingDot = False
	
	def getCover(self, surface):
		"""Where every the dot goes, it copys its surface to displays it after words"""
		if self.initCover == False:
			self.cover = surface.subsurface(Rect(self.calibpoints[0][0]-18, self.calibpoints[0][1]-18, 36, 36)).copy()
			self.initCover = True

	def getPoints(self, screen_size, points = 9):
		"""Gets the location of the dots"""
		xaxis = []
		yaxis = []
		if points == 9:
			xaxis, yaxis = [0.1, 0.5, 0.9], [0.1, 0.5, 0.9]
		if points == 12:
			xaxis, yaxis = [0.1, 0.36666, 0.63333, 0.9], [0.1, 0.5, 0.9]
		if points == 16:
			xaxis, yaxis = [0.1, 0.36666, 0.63333, 0.9], [0.1, 0.36666, 0.63333, 0.9]

		self.gridX = [int(x*screen_size[0]) for x in xaxis]
		self.gridY = [int(y*screen_size[1]) for y in yaxis]

		for x in xaxis:	
			for y in yaxis:
			    self.calibpoints.append([int(x*screen_size[0]), int(y*screen_size[1])])
		shuffle(self.calibpoints)
		self.calibpoints.insert(0, [int(xaxis[1]*screen_size[0]), int(yaxis[1]*screen_size[1])])

	def calibrate(self, surface, gazePos):
		"""Calibrates the eye tracker"""
		if self.start_new_calibration:
			self.start_new_calibration = False

		if self.calibpoint <= len(self.calibpoints)-1:
			self.dest = self.calibpoints[self.calibpoint]

			#OLD POSITION OCCURS HERE
			surface.blit(self.cover, (intt(self.circ)[0]-18, intt(self.circ)[1]-18))
			d = dist(self.circ,self.dest)
			if d > 0:
				direct = normal(self.dest[0]-self.circ[0],self.dest[1]-self.circ[1])
				self.speed = min(self.speed+self.maxAccel,min(self.maxSpeed,d))
				add(self.circ,mult(direct,self.speed))
			self.cover = surface.subsurface(Rect(intt(self.circ)[0]-18, intt(self.circ)[1]-18, 36, 36)).copy()
			draw.circle(surface, (50,168,134), intt(self.circ), 17)
			drawAACircle(surface, intt(self.circ)[0], intt(self.circ)[1], 16, (50,168,134), 2)
			draw.rect(surface, (255,255,255), (intt(self.circ)[0]-16, intt(self.circ)[1]-3, 33, 6))
			draw.rect(surface, (255,255,255), (intt(self.circ)[0]-3, intt(self.circ)[1]-16, 6, 33))
			drawAACircle(surface, intt(self.circ)[0], intt(self.circ)[1], int(self.calibpoint_size), (50,168,134), 2)

			if d == 0:

				if self.decreaseSize == False and self.calibpoint_size <= 7:
					self.calibpoint_size += self.calibpoint_speed
					if self.decreaseAgain and self.calibpoint_size == 8:
						self.calibpoint += 1
						self.decreaseAgain = False
				else:
					self.decreaseSize = True
				if self.decreaseSize:
					if self.calibpoint_size > 1 and self.decrease:
						self.calibpoint_size -= self.calibpoint_speed
						if self.calibpoint_size == 2 and self.decreaseAgain:
							self.decreaseSize = False
					else:
						self.decrease = False
						self.calibpoint_size += self.calibpoint_speed
						if self.calibpoint_size == 8:
							self.decrease = True
							self.decreaseAgain = True

				if self.calibpoint_size == 1.0 and self.decreaseAgain: 
					self.startCalibratingDot = True

				if self.calibpoint_size == 5.0 and self.decreaseAgain == False:
					self.stopCalibratingDot = True

				if self.startCalibratingDot:
					tracker.tracker.calibration_point_start(self.calibpoints[self.calibpoint][0], self.calibpoints[self.calibpoint][1])
					if self.stopCalibratingDot:
						tracker.tracker.calibration_point_end()
						self.startCalibratingDot = False
						self.stopCalibratingDot = False

		else:
			self.calibrated = True
			self.calibresult = tracker.tracker.latest_calibration_result()
			print(str(self.calibresult))

		self.postCalibration(surface, gazePos)

	def postCalibration(self, surface, gazePos):
		"""Displays a grid with all of the calibration points"""
		if self.postCalib_drawn == False and self.calibrated:
			for x in self.gridX:
				draw.line(surface, (255,255,255), (x,0), (x,1080))
			for y in self.gridY:
				draw.line(surface, (255,255,255), (0,y), (1920,y))
			for i in self.calibpoints:
			 	draw.circle(surface, (255,255,255), intt(i), 25)
			 	drawAACircle(surface, int(i[0]), int(i[1]), 24, (255,255,255), 2)
			self.postCalib_drawn = True
		if self.postCalib_drawn:
			for i in self.calibpoints:
				if circleCollidepoint(i[0], i[1], gazePos[0], gazePos[1], 25):
					draw.circle(surface, (50,168,134), intt(i), 25)
					drawAACircle(surface, int(i[0]), int(i[1]), 24, (255,255,255), 2)
				if surface.get_at(intt(i)) != (255,255,255) and circleCollidepoint(i[0], i[1], gazePos[0], gazePos[1], 25) == False:
					draw.circle(surface, (255,255,255), intt(i), 25)
					drawAACircle(surface, int(i[0]), int(i[1]), 24, (255,255,255), 2)

	def resetVars(self):
		"""Used to reset the variables for the Dot class"""
		self.dest = (200,200)

		self.calibpoint = 1
		self.calibrated = False
		self.calibpoint_size = 8.0

		self.decreaseSize = False
		self.decrease = True
		self.decreaseAgain = False
		self.calibpoint_speed = 1

		self.initCover = False
		self.cover = None

		self.postCalib_drawn = False

		self.start_new_calibration = True
		self.startCalibratingDot = False
		self.stopCalibratingDot = False

class CalibrationProcess:
	"""Class for the calibration process"""
	def __init__(self, surface, screen_size):
		"""Initializes the CalibrationProcess class"""
		self.screen_size = screen_size
		self.calibration = Calibration(surface)
		#-----------------------------------------------------------------------------------
		self.drawn = False
		self.countdown = 60
		self.level_drawn = ''
		self.gameover = False
		#-----------------------------------------------------------------------------------
		self.dot = Dot(surface, screen_size)
		self.counter = 300

	def run(self, surface, gazePos, old_gazePos):
		"""Used to run the calibration process"""
		if self.gameover == False:
			if self.drawn == False:
				self.level_drawn = self.calibration.drawLevel(surface)
			if self.level_drawn == 'LEVEL DRAWN' and self.drawn == False:
				self.calibration.resetVars()
				self.drawn = True
				self.level_drawn = ''
				self.dot.resetVars()
			if self.drawn:
				self.dot.getCover(surface)
				self.dot.calibrate(surface, gazePos)
		
		self.calibration.incrementCounter()

		if self.dot.calibrated:	self.counter -= 1
		if self.counter == 0:	
			self.gameover = False
			self.drawn = False
			self.counter = 300			
			return True
#----------------------------------CALIBRATION ONLY-----------------------------------

#----------------------------------MAIN-----------------------------------
tracker = Tracker(screen)
startScreen = IntroScreen(screen)
keyboard = keyBoard(screen)
calibration = CalibrationProcess(screen, screen.get_size())
home = HomeScreen(screen, screen.get_size())
if home.goToHome == False:
	startScreen.drawScreen(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, keyboard.old_state)	# takes 96 ms
	startScreen.guestButtonCover = screen.subsurface(Rect(705,415, 510,90)).copy()
else:
	screen.blit(homeScreen, (0,0))
database = Server()

#-----SCREEN RESOLUTION-----
resX, resY = screen.get_size()

#-----TESTS-----
stop_to_calibrate = False
field_num = 0
check_for_existing_text = False
notesPos = 0
check_for_existing_text_notes = False
runTile = False
drawName = False

#-----MAIN LOOP-----
while running:
	for e in event.get():
	    if e.type == QUIT: 
	        running = False
	tracker.getTrackerState()	# update eye-tracker state		

	#--------------------------------------------------INTRO SCREEN CODE START-----------------------------------------------
	keyboard.old_state = keyboard.state
	keyboard.hardwareKeyboard = key.get_pressed()	# takes 0 ms

	# everything in the if below takes 20 ms
	if startScreen.animate == False and home.goToHome == False:
		# checking for login/signup activation takes 0 ms
		#------------------LOGGING IN ACTIVATION------------------------
		if startScreen.logIn_check():	
			keyboard.state = 'ON'
			startScreen.login = True
			startScreen.loggingIn = True
			if startScreen.logIn_alreadyChecked:
				startScreen.login = False # Sets login screen to False
				startScreen.logIn_alreadyChecked = False
			startScreen.logIn_alreadyChecked = True
		else:
			startScreen.login = False
			startScreen.logIn_alreadyChecked = False
		if keyboard.state == 'OFF':
			startScreen.loggingIn = False
		#------------------SIGNING UP ACTIVATION------------------------
		if startScreen.signUp_check():	
			keyboard.state = 'ON'
			startScreen.signup = True # For if thr user wants to sign up or not
			startScreen.signingUp = True
			if startScreen.signUp_alreadyChecked:
				startScreen.signup = False
				startScreen.signUp_alreadyChecked = False
			startScreen.signUp_alreadyChecked = True # Declares sign up as valid
		else:
			startScreen.signup = False
			startScreen.signUp_alreadyChecked = False
		if keyboard.state == 'OFF':
			startScreen.loggingIn = False
			startScreen.signingUp = False

		#------------------SIGNING UP ACTION------------------------
		# login/signup actions take 18 ms
		if startScreen.signingUp:
			if len(database.signUpCredentials[database.signUpKeys[field_num]]) > 0 and check_for_existing_text:
				 keyboard.key['typed'] = database.signUpCredentials[database.signUpKeys[field_num]]
				 check_for_existing_text = False
			database.signUpCredentials[database.signUpKeys[field_num]] = keyboard.key['typed']
			if keyboard.key['activated_key'] == 'tab':	
				field_num += 1
				check_for_existing_text = True
				keyboard.key['typed'] = ''
				keyboard.key['activated_key'] = ''
			if keyboard.key['activated_key'] == 'return':
				if database.signUp():
					keyboard.state = False
				keyboard.key['activated_key'] = ''
			if field_num > 3:	field_num = 0
			time3 = time.get_ticks()
			# takes 24 ms - slows down the entire program
			startScreen.fillForm(screen, [database.signUpCredentials['full_name'], database.signUpCredentials['email'], database.signUpCredentials['userID'], database.signUpCredentials['password']], field_num) # Used to store all the users login database
			time4 = time.get_ticks()
			if database.signUpSuccessful:	startScreen.animate = True
		#------------------LOGGING IN ACTION-----------------------
		if startScreen.loggingIn:
			if len(database.logInCredentials[database.logInKeys[field_num]]) > 0 and check_for_existing_text:
				 keyboard.key['typed'] = database.logInCredentials[database.logInKeys[field_num]]
				 check_for_existing_text = False
			database.logInCredentials[database.logInKeys[field_num]] = keyboard.key['typed']
			if keyboard.key['activated_key'] == 'tab':	
				field_num += 1
				check_for_existing_text = True	
				keyboard.key['typed'] = ''
				keyboard.key['activated_key'] = ''
			if keyboard.key['activated_key'] == 'return':
				if database.logIn():
					keyboard.state = False
				keyboard.key['activated_key'] = ''
			if field_num > 1:	field_num = 0
			startScreen.fillForm(screen, [database.logInCredentials['userID or email'], database.logInCredentials['password']], field_num)
			if database.logInSuccessful:	startScreen.animate = True
		if startScreen.loggingIn == False and startScreen.signingUp == False:
			field_num = 0
		
	#------------------GETTING RAW DATA------------------------
	if startScreen.animate == False:
		tracker.updateGazeData(screen)

	#------------------LAUNCH KEYBOARD------------------------
	keyboard.state = keyboard.getState()
	keyboard.key['current'] = keyboard.getKey(tracker.getGazeData(), keyboard.state)
	if startScreen.animate == False:
		if home.tiles['CHESS']['activate'] and 10 <= home.tiles['CHESS']['game'].dwell_delay <= 30:
			pass 		
		else:
			if stop_to_calibrate == False and home.tiles['PONG']['activate'] == False:
				tracker.drawGaze(screen, (0,255,0), tracker.getGazeData(), tracker.getOldGazeData()) # Displays the gaze data 
	goBack = keyboard.drawSelectedKey(screen, tracker.getGazeData(), keyboard.state)
	if goBack:
		startScreen.login, startScreen.signup = False, False
		startScreen.loggingIn, startScreen.signingUp = False, False
		keyboard.state = 'OFF'

	if keyboard.key['current'] != None:
		keyboard.key['previous'] = keyboard.key['current'] 

	#------------------LAUNCH START SCREEN------------------------
	if startScreen.animate == False and home.goToHome == False:
		if stop_to_calibrate == False:
			start_screen = startScreen.drawScreen(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, keyboard.old_state) # Displays the start screen upon login
			if start_screen == 'DRAW KEYBOARD':
				keyboard.drawKeyboard(screen, tracker.getGazeData(), 'UPPER')
		if startScreen.calibPanel_dwell_delay == 145:
			stop_to_calibrate = True
			startScreen.calibPanel_dwell_delay = 0
		if stop_to_calibrate == False and startScreen.loggingIn == False and startScreen.signingUp == False and home.goToHome == False:
			startScreen.guestButton(screen, tracker.getGazeData())
			
	if startScreen.animate:
		keyboard.key['typed'], keyboard.key['activated_key'], keyboard.key['previous'] = '', '', None
		animate = startScreen.goToHome_animation(screen)
		if animate == False:
			startScreen.animate = False
			home.goToHome = True

	#------------------RUN CALIBRATION------------------------
	if stop_to_calibrate and home.goToHome == False:
		calibrated = calibration.run(screen, tracker.getGazeData(), tracker.getOldGazeData())
		if calibrated:
			startScreen.centerView(screen, tracker.getGazeData(), tracker.tracker_state)
			startScreen.logIn(screen, startScreen.login_dwell_delay, tracker.getGazeData())
			startScreen.signUp(screen, startScreen.signup_dwell_delay, tracker.getGazeData())
			startScreen.calibrationPanel(screen, startScreen.calibPanel_dwell_delay, tracker.getGazeData())
			stop_to_calibrate = False
	#--------------------------------------------------INTRO SCREEN CODE END-----------------------------------------------

	#--------------------------------------------------HOME SCREEN CODE START-----------------------------------------------
	if home.goToHome:
		home.getUsage()
		action = home.performAction(tracker.getGazeData(), runTile)
		if action == 'CALIBRATION':	stop_to_calibrate = True
		if runTile == False:
			if stop_to_calibrate == False:
				if drawName:				
					home.nameDrawn = False
					drawName = False
				home.getCovers(screen)
				home.drawControlPanel(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, startScreen.guest, database.getFullName())
				home.writeDate(screen)
				home.mainTiles(screen, tracker.getGazeData(), keyboard.key['typed'] if keyboard.key['typed'] != '' else "What's on your mind?")
				if home.activateKeyboard(keyboard.state, keyboard.old_state) == 'DRAW KEYBOARD':
					keyboard.drawKeyboard(screen, tracker.getGazeData(), 'UPPER')
				state = home.getTilesState()
				if state != False:
					runTile = state
			if home.goToHome == False:
				for tile in home.controlPanel:
					home.controlPanel[tile]['dwell_delay'] = 104
				if action == 'LOG OUT':
					startScreen.signup = False
					startScreen.signingUp = False
					startScreen.login = False
					startScreen.loggingIn = False
					startScreen.resetVars()
					startScreen.centerView(screen, tracker.getGazeData(), tracker.tracker_state)
					startScreen.drawScreen(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, keyboard.old_state)	# takes 96 ms
					startScreen.guestButtonCover = screen.subsurface(Rect(705,415, 510,90)).copy()
					for tile in home.tiles:
						home.tiles[tile]['activate'] = False
						home.tiles[tile]['drawn'] = False
					runTile = False
				elif action == 'SHUTDOWN':
					running = False
		elif runTile == 'FREE-TYPE':
			if home.tiles['FREE-TYPE']['activate'] and home.tiles['FREE-TYPE']['alreadyReset'] == False:
				home.tiles['FREE-TYPE']['reset'] = True # Resets the Free-type
				home.tiles['FREE-TYPE']['alreadyReset'] = True
				for tile in home.controlPanel:
					home.controlPanel[tile]['dwell_delay'] = 108
			home.runTiles(screen, tracker.getGazeData(), tracker.getOldGazeData())
			if home.tiles['PONG']['activate'] == False and home.tiles['CATCH ME']['activate'] == False:
				home.drawControlPanel(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, startScreen.guest, database.getFullName())
		elif runTile == 'CHESS':
			if home.tiles['CHESS']['activate'] and home.tiles['CHESS']['alreadyReset'] == False:
				home.tiles['CHESS']['reset'] = True # Resets Chess
				home.tiles['CHESS']['alreadyReset'] = True
				for tile in home.controlPanel:
					home.controlPanel[tile]['dwell_delay'] = 108
			home.runTiles(screen, tracker.getGazeData(), tracker.getOldGazeData())
			if home.tiles['PONG']['activate'] == False and home.tiles['CATCH ME']['activate'] == False:
				home.drawControlPanel(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, startScreen.guest, database.getFullName())
		elif runTile == 'CONNECT 4':
			if home.tiles['CONNECT 4']['activate'] and home.tiles['CONNECT 4']['alreadyReset'] == False:
				home.tiles['CONNECT 4']['reset'] = True # Resets connect4
				home.tiles['CONNECT 4']['alreadyReset'] = True
				for tile in home.controlPanel:
					home.controlPanel[tile]['dwell_delay'] = 108
			home.runTiles(screen, tracker.getGazeData(), tracker.getOldGazeData())
			if home.tiles['PONG']['activate'] == False and home.tiles['CATCH ME']['activate'] == False:
				home.drawControlPanel(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, startScreen.guest, database.getFullName())
		elif runTile == 'TIC-TAC-TOE':
			if home.tiles['TIC-TAC-TOE']['activate'] and home.tiles['TIC-TAC-TOE']['alreadyReset'] == False:
				home.tiles['TIC-TAC-TOE']['reset'] = True # Resets tic tac toe
				home.tiles['TIC-TAC-TOE']['alreadyReset'] = True
				for tile in home.controlPanel:
					home.controlPanel[tile]['dwell_delay'] = 108
			home.runTiles(screen, tracker.getGazeData(), tracker.getOldGazeData())
			if home.tiles['PONG']['activate'] == False and home.tiles['CATCH ME']['activate'] == False:
				home.drawControlPanel(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, startScreen.guest, database.getFullName())
		elif runTile == 'ON-MIND':
			if home.tiles['ON-MIND']['activate']:
				keyboard.state = 'ON'
				if home.tiles['ON-MIND']['textInit'] == False:
					if home.tiles['ON-MIND']['text'] != '':
						if keyboard.key['typed'] != home.tiles['ON-MIND']['text']:
							 keyboard.key['typed'] = home.tiles['ON-MIND']['text']
							 home.tiles['ON-MIND']['textInit'] = True
				home.drawTypeBar(screen, keyboard.key['typed'] if keyboard.key['typed'] != '' else "What's on your mind?")
				if home.activateKeyboard(keyboard.state, keyboard.old_state) == 'DRAW KEYBOARD':
					keyboard.drawKeyboard(screen, tracker.getGazeData(), 'UPPER')
				if keyboard.key['activated_key'] == 'return':
					keyboard.state = 'OFF'
					runTile = False
					screen.blit(homeScreen, (0,0))
					for tile in home.controlPanel:
						home.controlPanel[tile]['dwell_delay'] = 104
					home.writeDate(screen)
					home.nameDrawn = False
					for tile in home.tiles:
						home.tiles[tile]['drawn'] = False
					home.tiles['ON-MIND']['text'] = keyboard.key['typed']
					home.mainTiles(screen, tracker.getGazeData(),  keyboard.key['typed'] if keyboard.key['typed'] != '' else "What's on your mind?")
					keyboard.key['activated_key'], keyboard.key['typed'] = '', ''
					home.tiles['ON-MIND']['textInit'] = False
					home.tiles['ON-MIND']['activate'] = False
		elif runTile == 'NOTES':
			if home.tiles['NOTES']['activate']:
				keyboard.state = 'ON'
				if home.tiles['NOTES']['textInit'] == False:
					if home.tiles['NOTES']['text'][0] != '':
						if keyboard.key['typed'] != home.tiles['NOTES']['text'][0]:
							 keyboard.key['typed'] = home.tiles['NOTES']['text'][0]
							 home.tiles['NOTES']['textInit'] = True
				if len(home.tiles['NOTES']['text'][notesPos]) > 0 and check_for_existing_text_notes:
					keyboard.key['typed'] = home.tiles['NOTES']['text'][notesPos]
					check_for_existing_text_notes = False
				home.tiles['NOTES']['text'][notesPos] = keyboard.key['typed']
				if keyboard.key['activated_key'] == 'tab':	
					notesPos += 1
					check_for_existing_text_notes = True
					keyboard.key['typed'] = ''
					keyboard.key['activated_key'] = ''
				if notesPos > len(home.tiles['NOTES']['height'])-1:
					notesPos = 0
				home.writeNotes(screen, keyboard.key['typed'] if keyboard.key['typed'] != '' else "|", notesPos)
				if home.activateKeyboard(keyboard.state, keyboard.old_state) == 'DRAW KEYBOARD':
					keyboard.drawKeyboard(screen, tracker.getGazeData(), 'UPPER')

				if keyboard.key['activated_key'] == 'return':
					keyboard.state = 'OFF'
					runTile = False
					screen.blit(homeScreen, (0,0))
					for tile in home.controlPanel:
						home.controlPanel[tile]['dwell_delay'] = 104
					home.writeDate(screen)
					home.nameDrawn = False
					for tile in home.tiles:
						if tile != 'ON-MIND':
							home.tiles[tile]['drawn'] = False
					home.mainTiles(screen, tracker.getGazeData(), keyboard.key['typed'] if keyboard.key['typed'] != '' else "What's on your mind?")
					keyboard.key['activated_key'], keyboard.key['typed'] = '', ''
					home.tiles['NOTES']['textInit'] = False
					home.tiles['NOTES']['activate'] = False
					home.writeNotes(screen, keyboard.key['typed'], notesPos)
					notesPos += 1
		else:
			if home.tiles['PONG']['activate'] and home.tiles['PONG']['alreadyReset'] == False:
				home.tiles['PONG']['reset'] = True # Resets pong
				home.tiles['PONG']['alreadyReset'] = True
				for tile in home.controlPanel:
					home.controlPanel[tile]['dwell_delay'] = 108
			elif action != 'LOG OUT' and home.tiles['PONG']['activate'] == False and home.tiles['FREE-TYPE']['activate'] == False and home.tiles['CHESS']['activate'] == False and home.tiles['CONNECT 4']['activate'] == False and home.tiles['TIC-TAC-TOE']['activate'] == False and home.tiles['CATCH ME']['activate'] == False and keyboard.state == 'OFF':
				home.tiles['PONG']['alreadyReset'] = False
				home.drawControlPanel(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, startScreen.guest, database.getFullName())
				home.writeDate(screen)
				home.mainTiles(screen, tracker.getGazeData(), keyboard.key['typed'] if keyboard.key['typed'] != '' else "What's on your mind?")
			#-----------------------------------------------------------------------------------------
			if home.tiles['CATCH ME']['activate'] and home.tiles['CATCH ME']['alreadyReset'] == False:
				home.tiles['CATCH ME']['reset'] = True
				home.tiles['CATCH ME']['alreadyReset'] = True
				for tile in home.controlPanel:
					home.controlPanel[tile]['dwell_delay'] = 108
			elif action != 'LOG OUT' and home.tiles['CATCH ME']['activate'] == False and home.tiles['FREE-TYPE']['activate'] == False and home.tiles['CHESS']['activate'] == False and home.tiles['CONNECT 4']['activate'] == False and home.tiles['TIC-TAC-TOE']['activate'] == False and home.tiles['PONG']['activate'] == False and keyboard.state == 'OFF':
				home.tiles['CATCH ME']['alreadyReset'] = False
				home.drawControlPanel(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, startScreen.guest, database.getFullName())
				home.writeDate(screen)
				home.mainTiles(screen, tracker.getGazeData(), keyboard.key['typed'] if keyboard.key['typed'] != '' else "What's on your mind?")
			home.runTiles(screen, tracker.getGazeData(), tracker.getOldGazeData())
			if home.tiles['PONG']['activate'] == False and home.tiles['CATCH ME']['activate'] == False:
				home.drawControlPanel(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, startScreen.guest, database.getFullName())
		if home.tiles['FREE-TYPE']['activate'] == False and home.tiles['FREE-TYPE']['alreadyReset'] != False:
			home.tiles['FREE-TYPE']['alreadyReset'] = False
		if home.tiles['CHESS']['activate'] == False and  home.tiles['CHESS']['alreadyReset'] != False:
			home.tiles['CHESS']['alreadyReset'] = False
		if home.tiles['CONNECT 4']['activate'] == False and home.tiles['CONNECT 4']['alreadyReset'] != False:
			home.tiles['CONNECT 4']['alreadyReset'] = False
		if home.tiles['TIC-TAC-TOE']['activate'] == False and home.tiles['TIC-TAC-TOE']['alreadyReset'] != False:
			home.tiles['TIC-TAC-TOE']['alreadyReset'] = False
		if action == 'HOME':
			drawName = True
			screen.blit(homeScreen, (0,0))
			for tile in home.tiles:
				home.tiles[tile]['activate'] = False
				home.tiles[tile]['drawn'] = False
			home.drawControlPanel(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, startScreen.guest, database.getFullName())
			home.writeDate(screen)
			home.mainTiles(screen, tracker.getGazeData(), keyboard.key['typed'] if keyboard.key['typed'] != '' else "What's on your mind?")
			runTile = False
		elif action == 'LOG OUT':
			drawName = True
			startScreen.signup = False
			startScreen.signingUp = False
			startScreen.login = False
			startScreen.loggingIn = False
			startScreen.resetVars()
			startScreen.centerView(screen, tracker.getGazeData(), tracker.tracker_state)
			startScreen.drawScreen(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, keyboard.old_state)	# takes 96 ms
			startScreen.guestButtonCover = screen.subsurface(Rect(705,415, 510,90)).copy()
			for tile in home.tiles:
				home.tiles[tile]['activate'] = False
				home.tiles[tile]['drawn'] = False
			runTile = False
		elif stop_to_calibrate:
			drawName = True
			calibrated = calibration.run(screen, tracker.getGazeData(), tracker.getGazeData())
			if calibrated:
				home.getCurrentApp(screen, tracker.getGazeData())
				if home.currentApp == 'HOME':
					screen.blit(homeScreen, (0,0))
					for tile in home.tiles:
						home.tiles[tile]['drawn'] = False
					home.drawControlPanel(screen, tracker.getGazeData(), tracker.tracker_state, keyboard.state, startScreen.guest, database.getFullName())
					home.writeDate(screen)
					home.mainTiles(screen, tracker.getGazeData(), keyboard.key['typed'] if keyboard.key['typed'] != '' else "What's on your mind?")
				elif home.currentApp == 'FREE-TYPE':
					home.tiles['FREE-TYPE']['app'].bgDrawn = False
					home.tiles['FREE-TYPE']['app'].typeBarDrawn = False
					home.tiles['FREE-TYPE']['ap8p'].drawSetting(screen) 
				elif home.currentApp == 'CHESS':
					home.tiles['CHESS']['game'] = chessGame()
				stop_to_calibrate = False
	#---------------------------------------------------HOME SCREEN CODE END-----------------------------------------------

	#------------------SAVE OLD POSITIONS------------------------
	tracker.oldex, tracker.oldey = tracker.ex, tracker.ey
	tracker.oldmx, tracker.oldmy = tracker.mx, tracker.my
	myClock.tick(60)
	if keyboard.hardwareKeyboard[K_ESCAPE]:	running = False
	#print(myClock.get_fps())
	display.flip()
tracker.disconnect()
quit()
