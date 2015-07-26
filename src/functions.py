#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Abhi
# @Date:   2015-04-14 17:47:59
# @Last Modified by:   Abhi
# @Last Modified time: 2015-06-22 00:36:27
from pygame import *
from pygame import gfxdraw
from peyetribe import *						# Author:	Pei Beageark, 	EyeTribe API for Eye-Tracking with Significant Changes Made by Abhi Gupta
from surfaces import *						# Contains all of the loaded images and surfaces
from random import *
from math import *
import PAdLib as padlib 					# Author: Ian Mallet	
import GazePlotter2 as GazePlotter 			# Custom Cython Module Used to Plot Gaze Data on Screen
import os
from parse_rest.connection import register # imports the module neccesarry to register the app with the author's credentials
from parse_rest.user import User 		   # imports the module to sign up, log in, add and delete users
import datetime
from speech import *
import urllib.request 						# Email verification to send HTTP requests
import json
from chessGame import * 					
from connect4 import * 						
from tictactoe import *						

"""
Contains all of the neccesarry classes in order to run various modes of the program in the main loop.
"""

display.init()

def setScreen(defaultx, defaulty):
	"Sets the default position of the pygame window"
	os.environ['SDL_VIDEO_WINDOW_POS'] = str(defaultx)+','+str(defaulty) 


class Tracker:
	"""Handles all of the custom calls to the EyeTribe Server and establishes a connection to collect live gazeData. If no gazeData is available, the class
	   will switch over to live mouse data instead so the program can be operated with the mouse rather than the eye tracker. Also, the gazeData coordinates
	   or mouse coordinates are plotted here on the display using a surface to cover up the tracks."""
	def __init__(self, surface):
		self.trackerConnected = False
		self.tracker = EyeTribe()
		self.connect()
		self.tracker_state = 1
		self.tracker_state = self.getTrackerState()
		self.changeToPushmode()

		self.raw_gazeData = (0,0)
		self.mx, self.my = (0,0)
		self.oldmx, self.oldmy = (self.mx, self.my)
		self.ex, self.ey = (0,0)
		self.oldex, self.oldey = (self.ex, self.ey)

		self.circ = [200,200]
		self.speed = 0.0
		self.maxSpeed = 60
		self.maxAccel = 50
		self.cover = surface.subsurface(Rect(0,0,20,20)).copy()

	def connect(self):
		"""Attempts to connect to the EyeTribe server if it is on and if the eye-tracker is connected"""
		try:
			self.tracker.connect()
			self.trackerConnected = True
		except:
			self.trackerConnected = False

	def changeToPushmode(self):
		"""Changes the mode of the eye-tracker so that requests can be made to server for data as long as the tracker is connected"""
		if self.trackerConnected and self.tracker_state == 0:
			self.raw_gazeData = self.tracker.next()
			self.tracker.pushmode()

	def disconnect(self):
		"""Closes the conection to the Eye-Tribe server if it was previously connected"""
		if self.trackerConnected:
			self.tracker.pullmode()
			self.tracker.close()

	def updateGazeData(self, surface):
		"""Makes a request to the server to get the average gaze points and normalizes them relative to the screen resolution, otherwise returns the updated mouse position"""
		if self.trackerConnected:
			self.raw_gazeData = self.tracker.next().avg
			self.ex, self.ey = int(self.raw_gazeData.x), int(self.raw_gazeData.y)-40
			self.ex, self.ey = GazePlotter.getPoints((self.ex, self.ey), (self.oldex, self.oldey), self.circ, self.speed, self.maxAccel, self.maxSpeed)
			self.ex, self.ey = self.gazeNormalize(surface, (self.ex, self.ey))
			return (self.ex, self.ey)
		else:
			self.mx, self.my = mouse.get_pos()
			self.mx, self.my = GazePlotter.getPoints((self.mx, self.my), (self.oldmx, self.oldmy), self.circ, self.speed, self.maxAccel, self.maxSpeed)
			self.mx, self.my =  self.gazeNormalize(surface, (self.mx, self.my))
			return (self.mx, self.my)

	def getGazeData(self):
		"""Returns the current gaze/mouse data"""
		if self.trackerConnected:
			return (self.ex, self.ey)
		else:
			return (self.mx, self.my)

	def getOldGazeData(self):
		"""Returns the old gaze/mouse data"""
		if self.trackerConnected:
			return (self.oldex, self.oldey)
		else:
			return (self.oldmx, self.oldmy)

	def gazeNormalize(self, surface, currentPos, size = 10):
		"""Ensures that the gaze data isn't out of bounds of the screen by normalizing it"""
		resX, resY = surface.get_size()
		ex, ey = currentPos
		if ex < size:	ex = size
		if ex > resX-size:	ex = resX-size
		if ey < size:	ey = size
		if ey > resY-size:	ey = resY-size
		return (ex,ey)

	def drawGaze(self, surface, colour, gazePos, old_gazePos, size = 10):
		"""Plots the gaze/mouse data on the diplay, covering up its tracks by blitting back the same area of the circle"""
		surface.blit(self.cover, (old_gazePos[0]-size, old_gazePos[1]-size))
		self.cover = surface.subsurface(Rect(gazePos[0]-size, gazePos[1]-size, size*2, size*2)).copy()
		draw.circle(surface, colour, gazePos, size)
		#return self.cover

	def getTrackerState(self):
		"""Returns the tracker state - 1: OFF and 0: ON"""
		if self.trackerConnected:
			self.tracker_state = self.tracker.getTrackerState()
		if self.tracker_state != 0:
			self.tracker_state = 1
			self.trackerConnected = False
		elif self.tracker_state == 0:
			self.trackerConnected = True
		return self.tracker_state

class Server:
	"""Contains all of the API SID Keys and verifys the auth. Token in order to save data to our own server"""
	def __init__(self):
		register("viNLvbxfYcOE0PL7VtwjUUptkDx60lnxcs24VR8U", "fxNz8ImcDOvmwm88snWe0flHvB1iD3QYWtLQ3wJ2") # Parse Core APP Key
		self.emailKey = "2bc1e17c8d1ca087d01292a5aa5e11c652ccb48b38e3e2c8e455d66710a324d9"				 # Kickbox APP Key
		
		self.signUpCredentials = {
					'full_name'	:	'',
					'email'		:	'',
					'userID'	:	'',
					'password'	:	'',
			}

		self.signUpKeys = ['full_name', 'email', 'userID', 'password']
		self.signUpSuccessful = None

		self.logInCredentials = {
					'userID or email'	:	'',
					'password'		:	'',
			}

		self.logInKeys = ['userID or email', 'password']
		self.logInSuccessful = None

		self.user = 0
		self.full_name = ''

		self.response = 'Email Verification'
		self.emailVerfication = 'Invalid'

	
	def signUp(self):
		"""Sends a HTTP request to verify email address and attemps to create a new user in the database if all of the credentials are valid"""
		self.response = json.loads(urllib.request.urlopen("https://api.kickbox.io/v2/verify?email="+self.signUpCredentials['email']+"&apikey="+self.emailKey).read().decode("utf-8"))
		if self.response['result'] != 'deliverable' and self.response['reason'] != 'accepted_email':
			self.emailVerfication = 'Invalid'
		else:
			self.emailVerfication = 'Valid'
		try:
			if self.emailVerfication == 'Valid':
				self.user = User.signup(self.signUpCredentials['userID'], self.signUpCredentials['password'], email=self.signUpCredentials['email'], full_name=self.signUpCredentials['full_name'])	  # creates a new user in the database (user, password, other records)
				self.signUpSuccessful = True
				self.full_name = self.signUpCredentials['full_name']
		except:
		 	self.signUpSuccessful = False
		return self.signUpSuccessful

	def logIn(self):
		"""Attempts to log in the user with the given credentials by checking if the user exits within the database"""
		try:
			self.user = User.login(self.logInCredentials['userID or email'], self.logInCredentials['password'])
			self.full_name = self.user.full_name
			self.logInSuccessful = True
		except:
			self.logInSuccessful = False
		return self.logInSuccessful

	def getFullName(self):
		"""Returns the full name of the logged in user"""
		return self.full_name

class keyBoard:
	def __init__(self, surface):
		"""Initializes the universal keyboard that is used to type everywhere except for the FREE-TYPE app"""
		self.old_state = 'ON'
		self.state = 'OFF'
		self.enterReady = True 

		data = [["`"], [], [], [], []]
		data[0] += [str(i) for i in range(1,10)]
		data[0] += ["0"]
		data[0] += ["-", "=", "delete"]
		data[1] += ["tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\"]
		data[2] += ["caps", "a", "s","d", "f", "g", "h", "j", "k", "l", ";", "'", "return"]
		data[3] += ["shift!", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "shift@"]
		data[4] += ["clear", "back", "?", "spacebar", "@", ".com", ".ca", "!"]

		self.keyboard = {}
		self.key = {					# Contains all of the data about a key that is used to perform operations
			'current'		:	None,
			'duration'		:	 0,
			'previous'		:	None,
			'activated_key'	:	'',
			'typed'			:	''
			}
		self.durationPerKey = 20

		self.data = data
		self.keyCols = self.genGradient()	# Generates a list of all the colours between col A and col B 
		self.keyboardCounter = 0
		self.hardwareKeyboard = key.get_pressed()

		self.changeToUpper = False		# CAPS is on / off
		self.changeToLower = True
		self.drawnForShift = True
		self.shiftMode = False


	def drawKeyboard(self, surface, gazePos, mode, language = "ENG"):
		"""Draws the on-screen keyboard on a seperate pygame surface"""
		surf = Surface((1425,485), SRCALPHA) 

		if mode != 'CAPS':
			draw.rect(surf, (255,255,255,90), (1,1,1423,485))					# draws the transluecent surface behind the keyboard so that it looks as if the keys are part of this frame
			padlib.draw.rrect(surf, (147,147,147), (0,0,1425,485), 6, 1)

		#----------------------TOP ROW--------------------------------------------------------------
		for key in range(14):
			size = 170 if self.data[0][key] == "delete" else 85
			padlib.draw.rrect(surf, (18,28,39), (10+85*key+10*key,10,size,85), 6)																							# draws rounded rectangle at that key's position in the 2D list
			makeText(surf, self.data[0][key], 60, (255,255,255), None, (10+85*key+10*key)+self.getSpacing(self.data[0][key], size), 14)										# writes the text of the key
			padlib.draw.rrect(surf, (255,255,255,90), (10+85*key+10*key,10,size,85), 6, 1)																					# draws a rounded border around the key
			self.keyboard[self.data[0][key]] = ((247+10+85*key+10*key,590+10,size,85), ((247+10+85*key+10*key)+self.getSpacing(self.data[0][key], size), 590+14))			# stores all of the characters with their corresponding locations and text locations

		#----------------------SECOND ROW--------------------------------------------------------------
		for key in range(14):
			# first key has different attributes
			if key == 0:
				size = 127
				padlib.draw.rrect(surf, (18,28,39), (10+85*key+10*key,105,size,85), 6)																							# draws rounded rectangle at that key's position in the 2D list
				makeText(surf, self.data[1][key], 60, (255,255,255), None, (10+85*key+10*key)+self.getSpacing(self.data[1][key], size), 109)									# writes the text of the key
				padlib.draw.rrect(surf, (255,255,255,90), (10+85*key+10*key,105,size,85), 6, 1)																					# draws a rounded border around the key
				self.keyboard[self.data[1][key]] = ((247+10+85*key+10*key,590+105,size,85), ((247+10+85*key+10*key)+self.getSpacing(self.data[1][key], size), 590+109))			# stores all of the characters with their corresponding locations
			# rest of the keys have the same attributes 
			else:
				size = 128 if self.data[1][key] == "\\" else 85
				offset = 52
				padlib.draw.rrect(surf, (18,28,39), (offset+85*key+10*key,105,size,85), 6)
				makeText(surf, self.data[1][key], 60, (255,255,255), None, (offset+85*key+10*key)+self.getSpacing(self.data[1][key], size), 109)									# writes the text of the key
				padlib.draw.rrect(surf, (255,255,255,90), (offset+85*key+10*key,105,size,85), 6, 1)																					# draws a rounded border around the key
				self.keyboard[self.data[1][key]] = ((247+offset+85*key+10*key,590+105,size,85), ((247+offset+85*key+10*key)+self.getSpacing(self.data[1][key], size), 590+109)) 	# stores all of the characters with their corresponding locations

		#----------------------THIRD ROW--------------------------------------------------------------
		for key in range(13):
			# first key has different attributes
			if key == 0:
				size = 170
				padlib.draw.rrect(surf, (18,28,39), (10+85*key+10*key,200,size,85), 6)
				makeText(surf, self.data[2][key], 60, (255,255,255), None, (10+85*key+10*key)+self.getSpacing(self.data[2][key], size), 204)
				padlib.draw.rrect(surf, (255,255,255,90), (10+85*key+10*key,200,size,85), 6, 1)
				self.keyboard[self.data[2][key]] = ((247+10+85*key+10*key,590+200,size,85), ((247+10+85*key+10*key)+self.getSpacing(self.data[2][key], size), 590+204))	# stores all of the characters with their corresponding locations
				continue
			# rest of the key have the same attributes
			else:
				size = 180 if self.data[2][key] == "return" else 85
				offset = 95
				padlib.draw.rrect(surf, (18,28,39), (offset+85*key+10*key,200,size,85), 6)
				makeText(surf, self.data[2][key], 60, (255,255,255), None, (offset+85*key+10*key)+self.getSpacing(self.data[2][key], size), 204)
				padlib.draw.rrect(surf, (255,255,255,90), (offset+85*key+10*key,200,size,85), 6, 1)
				self.keyboard[self.data[2][key]] = ((247+offset+85*key+10*key,590+200,size,85), ((247+offset+85*key+10*key)+self.getSpacing(self.data[2][key], size), 590+204))	# stores all of the characters with their corresponding locations

		#----------------------FOURTH ROW--------------------------------------------------------------
		for key in range(12):
			# first key has different attributes
			if key == 0:
				size = 223
				padlib.draw.rrect(surf, (18,28,39), (10+85*key+10*key,295,size,85), 6)
				makeText(surf, self.data[3][key].strip("@").strip("!"), 60, (255,255,255), None, (10+85*key+10*key)+self.getSpacing(self.data[3][key].strip("@").strip("!"), size), 299)
				padlib.draw.rrect(surf, (255,255,255,90), (10+85*key+10*key,295,size,85), 6, 1)
				self.keyboard[self.data[3][key]] = ((247+10+85*key+10*key,590+295,size,85), ((247+10+85*key+10*key)+self.getSpacing(self.data[3][key].strip("@").strip("!"), size), 590+299))	# stores all of the characters with their corresponding locations
				continue
			# rest of the key have the same attributes				
			else:
				size = 223 if "shift" in self.data[3][key] else 85
				offset = 147
				padlib.draw.rrect(surf, (18,28,39), (offset+85*key+10*key,295,size,85), 6)
				makeText(surf, self.data[3][key].strip("@").strip("!"), 60, (255,255,255), None, (offset+85*key+10*key)+self.getSpacing(self.data[3][key].strip("@").strip("!"), size), 299)
				padlib.draw.rrect(surf, (255,255,255,90), (offset+85*key+10*key,295,size,85), 6, 1)
				self.keyboard[self.data[3][key]] = ((247+offset+85*key+10*key,590+295,size,85), ((247+offset+85*key+10*key)+self.getSpacing(self.data[3][key].strip("@").strip("!"), size), 590+299))	# stores all of the characters with their corresponding locations

		#----------------------FIFTH ROW--------------------------------------------------------------
		for key in range(8):
			# third key has different attributes
			if key == 3:
				width = 120
				size = 560 
				offset = 10
				padlib.draw.rrect(surf, (18,28,39), (offset+width*key+10*key,390,size,85), 6)
				padlib.draw.rrect(surf, (255,255,255,90), (offset+width*key+10*key,390,size,85), 6, 1)
				self.keyboard[self.data[4][key]] = ((247+offset+width*key+10*key,590+390,size,85), ((247+offset+width*key+10*key)+self.getSpacing(self.data[4][key], size), 590+394))	# stores all of the characters with their corresponding locations
			
			# rest of the key have the same attributes		
			elif key > 3:
				width = 120
				size = 55 if self.data[4][key] == "!" else width
				offset = 450
				padlib.draw.rrect(surf, (18,28,39), (offset+width*key+10*key,390,size,85), 6)
				makeText(surf, self.data[4][key].strip("1").strip("2"), 60, (255,255,255), None, (offset+width*key+10*key)+self.getSpacing(self.data[4][key].strip("1").strip("2"), size), 394)
				padlib.draw.rrect(surf, (255,255,255,90), (offset+width*key+10*key,390,size,85), 6, 1)
				self.keyboard[self.data[4][key]] = ((247+offset+width*key+10*key,590+390,size,85), ((247+offset+width*key+10*key)+self.getSpacing(self.data[4][key], size), 590+394))	# stores all of the characters with their corresponding locations
			
			# fourth key has different attributes (spacebar)
			else:
				width = 120
				size = 223 if self.data[4][key] == "spacebar" else width
				offset = 10
				padlib.draw.rrect(surf, (18,28,39), (offset+width*key+10*key,390,size,85), 6)
				makeText(surf, self.data[4][key].strip("1").strip("2"), 60, (255,255,255), None, (offset+width*key+10*key)+self.getSpacing(self.data[4][key].strip("1").strip("2"), size), 394)
				padlib.draw.rrect(surf, (255,255,255,90), (offset+width*key+10*key,390,size,85), 6, 1)
				self.keyboard[self.data[4][key]] = ((247+offset+width*key+10*key,590+390,size,85), ((247+offset+width*key+10*key)+self.getSpacing(self.data[4][key], size), 590+394))	# stores all of the characters with their corresponding locations

		# blits the entire keyboard on to the screen after it has been drawn
		surface.blit(surf, (247, 590))

	def genGradient(self, primeCol = (18,28,39), secCol = (26,157,130), duration = 20, contrast = 1150, delay = 1):
		"""Takes in two colours and returns a list of all the colours that exist between the two to form a gradient using a linear interpolation algorithm"""
		gradient = []
		for i in range(1200,0,-1200//duration):			# the duration controls how many colours are produced in the spectrum, hence causing it to take longer when looping through a list of gradient colours
			R = round(primeCol[0] * (i/contrast) + secCol[0] * ((contrast-i)/contrast))
			G = round(primeCol[1] * (i/contrast) + secCol[1] * ((contrast-i)/contrast))
			B = round(primeCol[2] * (i/contrast) + secCol[2] * ((contrast-i)/contrast))
			R = 255 if R > 255 else 0 if R < 0 else R
			G = 255 if G > 255 else 0 if G < 0 else G
			B = 255 if B > 255 else 0 if B < 0 else B
			gradient += [(R,G,B) for i in range(delay)]
		gradient += [(26,157,130) for i in range(delay)]
		gradient += [(18,28,39)]
		return gradient

	def getSpacing(self, text, Size = 85):
		"""Returns the x position at which the text will blitted in order for it to be centered between a specified width"""
		space = font.Font('fonts/HelveNueThin/HelveticaNeueThn.ttf', 60).size(text)
		return (Size-space[0])//2

	def getActivity(self, gazePos):
		"""Notifies if the user is looking at a key on the keyboard"""
		for character in self.keyboard:
			if Rect(self.keyboard[character]).collidepoint(gazePos):
				return character
		return False

	def getState(self):
		"""Returns the state of the keyboard - ON/OFF based on whether it is being drawn on the display"""
		last_state = self.state
		if self.hardwareKeyboard[K_RETURN]: 
			if self.enterReady:
				if last_state == 'ON':
					self.state = 'OFF' 
				elif last_state == 'OFF':
					self.state = 'ON'
				self.enterReady = False
		else:
			self.enterReady = True 

		return self.state

	def getKey(self, gazePos, state):
		"""Returns the current key that the user is looking at"""
		if state == 'ON':
			for character in self.keyboard:
				if Rect(self.keyboard[character][0]).collidepoint(gazePos):
					return character
		else:
			self.key['duration'] = 0

	def drawSelectedKey(self, surface, gazePos, state):
		"""Peforms the corresponding key's action"""
		goBack = False
		if state == 'ON':
			if self.changeToUpper and self.key['current'] != None and self.key['previous'] != None:
				if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
					self.key['current'] = self.key['current'].upper()
					self.key['previous'] = self.key['previous'].upper()
			elif self.changeToLower and self.key['current'] != None and self.key['previous'] != None:			# resets the duration or dwell delay to 0 if the user stops focusing on a certain key
				if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
					self.key['current'] = self.key['current'].lower()
					self.key['previous'] = self.key['previous'].lower()		

			if self.key['current'] != None and self.key['previous'] != None:
				if self.key['current'] != self.key['previous']:
					self.key['duration'] = 0
					
					# draws the previous key by going through each colour in the list of gradient colours and then redreaws the text and border for the specified key
					padlib.draw.rrect(surface, self.keyCols[self.key['duration']], (self.keyboard[self.key['previous']][0]), 6)		 
					if self.key['previous'] not in ('spacebar', 'hide'):
						if self.key['previous'] == 'shift!' or self.key['previous'] == 'shift@':
							makeText(surface, self.key['previous'].strip("!").strip("@"), 60, (255,255,255), None, self.keyboard[self.key['previous']][1][0], self.keyboard[self.key['previous']][1][1])
						else:	
							makeText(surface, self.key['previous'], 60, (255,255,255), None, self.keyboard[self.key['previous']][1][0], self.keyboard[self.key['previous']][1][1])
					padlib.draw.rrect(surface, (255,255,255,90), (self.keyboard[self.key['previous']][0]), 6, 1)

				if Rect(self.keyboard[self.key['current']][0]).collidepoint(gazePos): 
					self.key['duration'] += 1		# increases the amount of time that you looked at a key for 
					
					# draws the current key by going through each colour in the list of gradient colours and then redreaws the text and border for the specified key
					if self.key['duration'] <= len(self.keyCols)-1:
						padlib.draw.rrect(surface, self.keyCols[self.key['duration']], (self.keyboard[self.key['current']][0]), 6)
					if self.key['current'] not in ('spacebar', 'hide'):
						if self.key['current'] == 'shift!' or self.key['current'] == 'shift@':
							makeText(surface, self.key['current'].strip("!").strip("@"), 60, (255,255,255), None, self.keyboard[self.key['current']][1][0], self.keyboard[self.key['current']][1][1])
						else:
							makeText(surface, self.key['current'], 60, (255,255,255), None, self.keyboard[self.key['current']][1][0], self.keyboard[self.key['current']][1][1])
					padlib.draw.rrect(surface, (255,255,255,90), (self.keyboard[self.key['current']][0]), 6, 1)

					if self.key['duration'] == self.durationPerKey:			# performs an action if the max duration is reached based on what key was selected
						self.key['activated_key'] = self.key['current']
						if self.key['current'] not in ('tab', 'return', "ctrl", "option!", "command!", "command@", "option@", "hide"):	# checks to make sure that no action is performed for non-active keys
							#------------SPACE BAR--------------
							if self.key['current'] == 'spacebar':
								self.key['typed'] += ' '
							#------------DELETE--------------
							elif self.key['current'] == 'delete':
								if len(self.key['typed']) >= 1:
									self.key['typed'] = self.key['typed'][:len(self.key['typed'])-1]
							#------------CLEAR--------------
							elif self.key['current'] == 'clear':
		 						self.key['typed'] = ''
		 					#------------BACK--------------
							elif self.key['current'] == 'back':
		 						goBack = True
		 					#------------CAPS--------------
							elif self.key['current'] == 'caps':
			 					if self.changeToUpper == False and self.changeToLower:
				 					for x in range(len(self.data)):			# to capitalize the keys
				 						for y in range(len(self.data[x])):
				 							if len(self.data[x][y]) == 1:	# capitalize only alphabet keys
			 									self.data[x][y] = self.data[x][y].upper()
			 									if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
				 									self.key['current'] = self.key['current'].upper()
				 									self.key['previous'] = self.key['previous'].upper()

			 						self.changeToUpper = True
			 						self.changeToLower = False
			 					elif self.changeToLower == False and self.changeToUpper:
			 						for x in range(len(self.data)):			# lowercase keys
				 						for y in range(len(self.data[x])):
				 							if len(self.data[x][y]) == 1:	# lowercase only alphabet keys
			 									self.data[x][y] = self.data[x][y].lower()
			 									if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
				 									self.key['current'] = self.key['current'].lower()
				 									self.key['previous'] = self.key['previous'].lower()
			 						self.changeToLower = True
			 						self.changeToUpper = False

			 					self.drawKeyboard(surface, gazePos, 'CAPS')		# redraw keyboard to see changes in the lettering
		 					#------------SHIFT--------------
							elif self.key['current'] == "shift!" or self.key['current'] == "shift@":
			 					if self.changeToUpper == False and self.changeToLower:
				 					for x in range(len(self.data)):			# to capitalize the keys
				 						for y in range(len(self.data[x])):
				 							if len(self.data[x][y]) == 1:	# capitalize only alphabet keys
			 									self.data[x][y] = self.data[x][y].upper()
			 									if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
				 									self.key['current'] = self.key['current'].upper()
				 									self.key['previous'] = self.key['previous'].upper()

			 						self.changeToUpper = True
			 						self.changeToLower = False
			 					elif self.changeToLower == False and self.changeToUpper:
			 						for x in range(len(self.data)):			# lowercase keys
				 						for y in range(len(self.data[x])):
				 							if len(self.data[x][y]) == 1:	# lowercase only alphabet keys
			 									self.data[x][y] = self.data[x][y].lower()
			 									if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
				 									self.key['current'] = self.key['current'].lower()
				 									self.key['previous'] = self.key['previous'].lower()
			 						self.changeToLower = True
			 						self.changeToUpper = False

			 					self.drawKeyboard(surface, gazePos, 'CAPS')	# redraw keyboard to see changes and then reverts back to default
		 					#------------ALPHABET KEY--------------
							else:
								# checks to see if data is capitalized or lowercase 
								if self.data[1][1] == "Q" and len(self.key['current']) == 1:	
									self.key['typed'] += self.key['current'].upper()
								elif self.data[1][1] == "q" and len(self.key['current']) == 1:
									self.key['typed'] += self.key['current'].lower()
								else:
									self.key['typed'] += self.key['current']
		 					#------------SHIFT MODE--------------
							if self.key['previous'] == 'shift!' or self.key['previous'] == 'shift@': 
			 					self.shiftMode = True
							if self.shiftMode:
			 					if self.key['activated_key'] != 'shift!' and self.key['activated_key'] != 'shift@':
				 					self.drawnForShift = False
				 					if self.changeToUpper == False and self.changeToLower:
					 					for x in range(len(self.data)):			# to capitalize the keys
					 						for y in range(len(self.data[x])):
					 							if len(self.data[x][y]) == 1:	# capitalize only alphabet keys
				 									self.data[x][y] = self.data[x][y].upper()
				 									if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
					 									self.key['current'] = self.key['current'].upper()
					 									self.key['previous'] = self.key['previous'].upper()
			 							self.changeToUpper = True
			 							self.changeToLower = False

				 					elif self.changeToLower == False and self.changeToUpper:
				 						for x in range(len(self.data)):			# lowercase keys
					 						for y in range(len(self.data[x])):
					 							if len(self.data[x][y]) == 1:	# lowercase only alphabet keys
				 									self.data[x][y] = self.data[x][y].lower()
				 									if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
					 									self.key['current'] = self.key['current'].lower()
					 									self.key['previous'] = self.key['previous'].lower()
			 							self.changeToLower = True
			 							self.changeToUpper = False

			 						self.drawKeyboard(surface, gazePos, 'CAPS')
			 						self.shiftMode = False
						self.key['duration'] = 0
			else:
				self.key['duration'] = 0	# reset the duration of the key to 0 since the user is no longer focusing on the same key, focus has changed
			return goBack

class FreeType(keyBoard):
	"""This class runs the FREE-TYPE app in the homescreen using some of the same concepts as the keyboard class"""
	def __init__(self):
		data = [[], [], [], [], []]
		data[0] += ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "Delete"]
		data[1] += ["a", "s","d", "f", "g", "h", "j", "k", "l", "'", "Enter"]
		data[2] += ["shift!", "z", "x", "c", "v", "b", "n", "m", ",", ".", "?", "shift@"]
		data[3] += ["&123", "CAPS", "Spacebar", "Speak", "Clear"]

		self.voiceOver = {
			'rect'	:	(1801,12,107,155),
			'ON'	: False,
			'OFF'	: True
		}

		self.icons = {
			'Delete'	:	(deleteIcon, (1687,450)),
			'Enter'		:	(enterIcon, (1687, 572)),
			'shift!'	:	(shiftIcon, (47,697)),
			'shift@'	:	(shiftIcon, (1796, 697)),
			'CAPS'		:	(capsIcon, (307,810)),
			'Speak'		:	(speakIcon, (1548, 813)),
			'Clear'		:	(clearIcon, (1768,815)),
			'VoiceOverOn'	:	(voiceOverOnIcon, (1823,33)),
			'VoiceOverOff'	:	(voiceOverOffIcon, (1821,33))
		}

		self.keyboard = {'VoiceOver'	:	(self.voiceOver['rect'], (0,0))}	# the voice over button 
		self.key = {					# Contains all of the data about a key that is used to perform operations
			'current'		:	None,
			'duration'		:	 0,
			'previous'		:	None,
			'activated_key'	:	'',
			'typed'			:	''
			}

		self.durationPerKey = 30	# the lower the value, the faster a key will be selected

		self.bgCol = (62,70,73)
		self.fgCol = (44,168,112)

		self.data = data
		self.keyCols = self.genGradient(primeCol = self.fgCol, secCol = (255,255,255), duration = 30)	# Generates a list of all the colours between col A and col B
		self.keyboardCounter = 0
		self.hardwareKeyboard = key.get_pressed()	# keyboard events
	

		self.defaulText = 'Type your thoughts . . .'
		self.text = self.defaulText

		self.bgDrawn = False
		self.typeBarDrawn = False

		self.changeToUpper = False
		self.changeToLower = True
		self.drawnForShift = True
		self.shiftMode = False

	def drawSetting(self, surface):
		"""Draws the background and the initial app on the display when the user first selects it"""
		if self.bgDrawn == False:
			draw.rect(surface, self.bgCol, (0,0,1920,1080))			# draws background
			draw.rect(surface, (101,107,109), (1800,0,120,180))
			self.drawKeyboard(surface)
			self.bgDrawn = True
		if self.typeBarDrawn == False:
			draw.rect(surface, (101,107,109), (0,0,1800,180))		# draws typing bar
			if self.key['typed'] == '':
				makeText(surface, self.text, 90, (255,255,255), None, 24, 39)
			else:
				makeText(surface, self.key['typed'], 90, (255,255,255), None, 24, 39)
			self.typeBarDrawn = True

	def drawKeyboardForShift(self, surface):
		"""Indicates if the keyboard has to be redrawn based on whether or not shift is selected"""
		if self.drawnForShift == False:
			self.drawKeyboard(surface)
			self.drawnForShift = True

	def getSpacing(text, Size, font_size, fontselection = 'fonts/HelveNueThin/HelveticaNeueThn.ttf', alignment = 'center'):
		"""Returns the x position at which the text will blitted in order for it to be centered/right aligned in a specified width"""
		space = font.Font(fontselection, font_size).size(text)
		if alignment == 'center':
			return (Size-space[0])//2
		elif alignment == 'right':
			return (Size-space[0])

	def drawKeyboard(self, surface):
		"""Draws the on-screen keyboard on a seperate pygame surface by going through the data (2D LIST) and blittig the value at the index as the text"""
		draw.rect(surface, self.fgCol, self.keyboard['VoiceOver'][0])
		if self.voiceOver['ON'] == False and self.voiceOver['OFF']:
			# blits the voice over off icon
			surface.blit(self.icons['VoiceOverOff'][0], self.icons['VoiceOverOff'][1])
		else:
			# blits the voice over on icon
			surface.blit(self.icons['VoiceOverOn'][0], self.icons['VoiceOverOn'][1])

		for row in range(len(self.data)):
			start = 15						# the offset from the left side of the screen
			y = row 						# the current row of the keyboard that is being drawn
			if row == 0 or row == 1:
				odd_key = [i for i in self.data[row] if len(i) > 1]	# finds out whether there are larger keys than normal in the row 
				alternative_size = 144	
				# if the key is larger, this is their size							
				if len(odd_key) == 1:
					if odd_key[0] == 'Delete':
						alternative_size = 302
					elif odd_key[0] == 'Enter':
						start = 53
						alternative_size = 262
					#----------TOP ROW-----------	
					for key in range(len(self.data[row])):
						size = 144 if self.data[row][key] != odd_key[0] else alternative_size
						pos = (start+144*key+15*key,427+(110+15)*y,size,110)
						draw.rect(surface, self.fgCol, pos)							# draws the key's background
						if self.data[row][key] != odd_key[0]:
							# writes the text of the key
							makeText(surface, self.data[row][key], 60, (43,48,55), None, pos[0]+getSpacing(self.data[row][key], size, 60, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'), pos[1]+18, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf')
						else:
							# blits the icon of the key if its larger than normal
							surface.blit(self.icons[odd_key[0]][0], self.icons[odd_key[0]][1])
						self.keyboard[self.data[row][key]] = (pos, (pos[0]+getSpacing(self.data[row][key], size, 60, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'), pos[1]+18))
			if row == 3:
				index_pos = [(0,-1), (1, -2)]			# because the keys from the left are the same size as the keys from the right, its a reflection in keyboard so you can invert the position at which everything is drawn for that row
				#----------THIRD ROW-----------	
				for pos in [(15,802,184,110), (212,802,263,110)]:
					invert_pos = (1920-pos[0]-pos[2],pos[1],pos[2],pos[3])	# reflected position
					draw.rect(surface, self.fgCol, pos)						# draws keys
					draw.rect(surface, self.fgCol, invert_pos)
					text1 = ''
					text2 = ''
					if pos == (15,802,184,110):	# first key from left and last key from right
						text1 = self.data[row][0]
						text2 = self.data[row][-1]
						self.keyboard[self.data[row][0]] = (pos, (pos[0]+getSpacing(text1, pos[2], 60, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'), pos[1]+18, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'))
						self.keyboard[self.data[row][-1]] = (invert_pos, (invert_pos[0]+getSpacing(text2, invert_pos[2], 60, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'), invert_pos[1]+18, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'))
					else:						# second key from left and second last key from right
						text1 = self.data[row][1]
						text2 = self.data[row][-2]
						self.keyboard[self.data[row][1]] = (pos, (pos[0]+getSpacing(text1, pos[2], 60, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'), pos[1]+18, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'))
						self.keyboard[self.data[row][-2]] = (invert_pos, (invert_pos[0]+getSpacing(text2, invert_pos[2], 60, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'), invert_pos[1]+18, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'))
					if text1 == 'CAPS':
						surface.blit(self.icons['CAPS'][0], self.icons['CAPS'][1])
					if text2 == 'Speak':
						surface.blit(self.icons['Speak'][0], self.icons['Speak'][1])
					if text2 == 'Clear':
						surface.blit(self.icons['Clear'][0], self.icons['Clear'][1])
					if text1 == '&123':
						makeText(surface, text1, 60, (43,48,55), None, pos[0]+getSpacing(text1, pos[2], 60, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'), pos[1]+18, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf')
				draw.rect(surface, self.fgCol, (490,802,939,110))
				self.keyboard[self.data[row][2]] = ((490,802,939,110), (0,0))								# doesnt need to hold a value for where to blit to text as it is the spacebar
			if row == 2:
				#----------SECOND ROW-----------	
				for key in range(len(self.data[row])):
					size = 144 
					pos = (15+144*key+15*key,427+(110+15)*y,size,110)
					draw.rect(surface, self.fgCol, pos)
					if self.data[row][key] == 'shift!' or self.data[row][key] == 'shift@':
						if self.key['activated_key'] == "shift!" or self.key['activated_key'] == "shift@":		# draws the shift key with a white
							draw.rect(surface, (255,255,255), self.keyboard['shift!'][0])						# background if has been selected
							draw.rect(surface, (255,255,255), self.keyboard['shift@'][0])
							surface.blit(self.icons['shift!'][0], self.icons['shift!'][1])
							surface.blit(self.icons['shift@'][0], self.icons['shift@'][1])
						else:
							draw.rect(surface, self.fgCol, pos)
							surface.blit(self.icons[self.data[row][key]][0], self.icons[self.data[row][key]][1])	# shift key reverts back to default colour
					else:
						draw.rect(surface, self.fgCol, pos)		# makes regular alphabet keys for the current row
						makeText(surface, self.data[row][key], 60, (43,48,55), None, pos[0]+getSpacing(self.data[row][key], size, 60, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'), pos[1]+18, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf')
					self.keyboard[self.data[row][key]] = (pos, (pos[0]+getSpacing(self.data[row][key], size, 60, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'), pos[1]+18, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf'))

	def getActivity(self, gazePos):
		"""Notifies if the user is looking at a key on the keyboard"""
		for character in self.keyboard:
			if Rect(self.keyboard[character][0]).collidepoint(gazePos):
				return character
		return False

	def getKey(self, gazePos):
		"""Notifies if the user is looking at a key on the keyboard and sets the duration of the key to false if the focus has changed"""
		for character in self.keyboard:
			if Rect(self.keyboard[character][0]).collidepoint(gazePos):
				return character
		else:
			self.key['duration'] = 0

	def drawSelectedKey(self, surface, gazePos):
		"""Peforms the corresponding key's action"""
		if self.changeToUpper and self.key['current'] != None and self.key['previous'] != None:
			if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
				self.key['current'] = self.key['current'].upper()
				self.key['previous'] = self.key['previous'].upper()
		elif self.changeToLower and self.key['current'] != None and self.key['previous'] != None:		# resets the duration or dwell delay to 0 if the user stops focusing on a certain key
			if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
				self.key['current'] = self.key['current'].lower()
				self.key['previous'] = self.key['previous'].lower()

		if self.key['current'] != None and self.key['previous'] != None:
			if self.key['current'] != self.key['previous']:
				self.key['duration'] = 0
				draw.rect(surface, self.keyCols[self.key['duration']],  (self.keyboard[self.key['previous']][0]))

				# draws the previous key by going through each colour in the list of gradient colours and then redreaws the text and border for the specified key
				if len(self.key['previous']) == 1 or self.key['previous'] == '&123': 
					makeText(surface, self.key['previous'].strip("!").strip("@"), 60, (43,48,55), None, self.keyboard[self.key['previous']][1][0], self.keyboard[self.key['previous']][1][1], 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf')
				else:
					if self.key['previous'] != self.data[3][2]:#'Spacebar':
						if self.key['previous'] == 'VoiceOver':
		 					draw.rect(surface, self.keyCols[self.key['duration']], self.keyboard['VoiceOver'][0])
		 					if self.voiceOver['ON'] == False and self.voiceOver['OFF']:
		 						surface.blit(self.icons['VoiceOverOff'][0], self.icons['VoiceOverOff'][1])
		 					if self.voiceOver['OFF'] == False and self.voiceOver['ON']:
		 						surface.blit(self.icons['VoiceOverOn'][0], self.icons['VoiceOverOn'][1])
						else:
							surface.blit(self.icons[self.key['previous']][0], self.icons[self.key['previous']][1])

			if Rect(self.keyboard[self.key['current']][0]).collidepoint(gazePos): 
		 		self.key['duration'] += 1		# increases the amount of time that you looked at a key for 
					
				# draws the current key by going through each colour in the list of gradient colours and then redreaws the text and border for the specified key
		 		if self.key['duration'] <= len(self.keyCols)-1:
		 			draw.rect(surface, self.keyCols[self.key['duration']],  (self.keyboard[self.key['current']][0]))
		 		if len(self.key['current']) == 1 or self.key['current'] == '&123':
		 			makeText(surface, self.key['current'].strip("!").strip("@"), 60, (43,48,55), None, self.keyboard[self.key['current']][1][0], self.keyboard[self.key['current']][1][1], 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf')
		 		else:
		 			if self.key['current'] != self.data[3][2]:	# checks to make sure that the key is not 'Spacebar' 
		 				# draws the icon of voice-over based on whether its activated or not
		 				if self.key['current'] == 'VoiceOver':
		 					draw.rect(surface, self.keyCols[self.key['duration']], self.keyboard['VoiceOver'][0])
		 					#---OFF---
		 					if self.voiceOver['ON'] == False and self.voiceOver['OFF']:
		 						surface.blit(self.icons['VoiceOverOff'][0], self.icons['VoiceOverOff'][1])
		 					#---ON---
		 					if self.voiceOver['OFF'] == False and self.voiceOver['ON']:
		 						surface.blit(self.icons['VoiceOverOn'][0], self.icons['VoiceOverOn'][1])
		 				else:
		 					surface.blit(self.icons[self.key['current']][0], self.icons[self.key['current']][1])

		 		if self.key['duration'] == self.durationPerKey:			# performs an action if the max duration is reached based on what key was selected
		 			self.key['activated_key'] = self.key['current']
		 			if self.key['current'] not in (self.data[1][-1], self.data[3][0]):	# checks to make sure that no action is performed for non-active keys
		 				#------------SPACE BAR--------------
		 				if self.key['current'] == self.data[3][2]:		
		 					self.key['typed'] += ' '
		 					if self.voiceOver['ON']:					# when voice over is activated and space bar is hit, the last word typed will be spoken
		 						text = self.key['typed'].split()[-1]
		 						text2speech(text)
		 				#------------DELETE--------------
		 				elif self.key['current'] == self.data[0][-1]:
		 					if len(self.key['typed']) >= 1:
		 						self.key['typed'] = self.key['typed'][:len(self.key['typed'])-1]
		 						self.typeBarDrawn = False
		 				#------------CAPS--------------
		 				elif self.key['current'] == 'CAPS':
		 					self.drawnForShift = False
		 					if self.changeToUpper == False and self.changeToLower:
			 					for x in range(len(self.data)):			# to capitalize the keys
			 						for y in range(len(self.data[x])):
			 							if len(self.data[x][y]) == 1:	# capitalize only alphabet keys 
		 									self.data[x][y] = self.data[x][y].upper()
		 									if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
			 									self.key['current'] = self.key['current'].upper()
			 									self.key['previous'] = self.key['previous'].upper()

		 						self.changeToUpper = True
		 						self.changeToLower = False
		 					elif self.changeToLower == False and self.changeToUpper:
		 						for x in range(len(self.data)):			# lowercase keys
			 						for y in range(len(self.data[x])):
			 							if len(self.data[x][y]) == 1:	# lowercase alphabet keys 
		 									self.data[x][y] = self.data[x][y].lower()
		 									if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
			 									self.key['current'] = self.key['current'].lower()
			 									self.key['previous'] = self.key['previous'].lower()
		 						self.changeToLower = True
		 						self.changeToUpper = False
		 					self.drawKeyboardForShift(surface)			# redraw keyboard to see changes in the lettering
		 				#------------SHIFT--------------
		 				elif self.key['current'] == self.data[2][0] or self.key['current'] == self.data[2][-1]:
		 					self.drawnForShift = False
		 					if self.changeToUpper == False and self.changeToLower:
			 					for x in range(len(self.data)):			# to capitalize the keys
			 						for y in range(len(self.data[x])):
			 							if len(self.data[x][y]) == 1:	# capitalize only alphabet keys 
		 									self.data[x][y] = self.data[x][y].upper()
		 									if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
			 									self.key['current'] = self.key['current'].upper()
			 									self.key['previous'] = self.key['previous'].upper()

		 						self.changeToUpper = True
		 						self.changeToLower = False
		 					elif self.changeToLower == False and self.changeToUpper:
		 						for x in range(len(self.data)):			# lowercase keys
			 						for y in range(len(self.data[x])):
			 							if len(self.data[x][y]) == 1:	# lowercase alphabet keys 
		 									self.data[x][y] = self.data[x][y].lower()
		 									if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
			 									self.key['current'] = self.key['current'].lower()
			 									self.key['previous'] = self.key['previous'].lower()
		 						self.changeToLower = True
		 						self.changeToUpper = False

		 					self.drawKeyboardForShift(surface)	# redraw keyboard to see changes and then reverts back to default
		 				#------------CLEAR--------------
		 				elif self.key['current'] == self.data[3][-1]:
		 					self.key['typed'] = ''
		 					self.typeBarDrawn = False 	# makes sure that the drawSetting(surface) will blit the type bar by making its drawn value to false or else it wont reblit since it's already been drawn
		 					self.drawSetting(surface)	# redraws only the type bar to show that there is no text (it has been clear)
		 				#------------SPEAK--------------
		 				elif self.key['current'] == self.data[3][-2]:
		 					text2speech(self.key['typed'])
		 				#------------VOICE-OVER--------------
		 				elif self.key['current'] == 'VoiceOver':
		 					if self.voiceOver['ON'] == False and self.voiceOver['OFF']:
		 						# sets voice-over to ON
		 						self.voiceOver['ON'] = True  	
		 						self.voiceOver['OFF'] = False
		 					elif self.voiceOver['OFF'] == False and self.voiceOver['ON']:
		 						# sets voice-over to OFF
		 						self.voiceOver['ON'] = False
		 						self.voiceOver['OFF'] = True
		 				#------------ALPHABET KEY--------------
		 				else:
		 					self.key['typed'] += self.key['current']
		 					self.typeBarDrawn = False  	# set to False to make sure type bar is blitted again to see the new typed word at the top

		 				if self.key['previous'] == 'shift!' or self.key['previous'] == 'shift@': 
		 					draw.rect(surface, (255,255,255), self.keyboard[self.key['previous']][0])
		 					#print(self.keyboard[self.key['previous']][0])
		 					self.shiftMode = True
		 				#------------SHIFT MODE--------------
		 				if self.shiftMode:
		 					if self.key['activated_key'] != 'shift!' and self.key['activated_key'] != 'shift@':
			 					self.drawnForShift = False
			 					if self.changeToUpper == False and self.changeToLower:
				 					for x in range(len(self.data)):			# to capitalize the keys
				 						for y in range(len(self.data[x])):
				 							if len(self.data[x][y]) == 1:
			 									self.data[x][y] = self.data[x][y].upper()
			 									if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
				 									self.key['current'] = self.key['current'].upper()
				 									self.key['previous'] = self.key['previous'].upper()
		 							self.changeToUpper = True
		 							self.changeToLower = False

			 					elif self.changeToLower == False and self.changeToUpper:
			 						for x in range(len(self.data)):			# lowercase keys
				 						for y in range(len(self.data[x])):
				 							if len(self.data[x][y]) == 1:
			 									self.data[x][y] = self.data[x][y].lower()
			 									if len(self.key['current']) == 1 and len(self.key['previous']) == 1:
				 									self.key['current'] = self.key['current'].lower()
				 									self.key['previous'] = self.key['previous'].lower()
		 							self.changeToLower = True
		 							self.changeToUpper = False

		 						self.drawKeyboardForShift(surface)
		 						self.shiftMode = False

		 			self.key['duration'] = 0

		else:
			self.key['duration'] = 0


def drawStar(screen, col, x, y, size, filled = 0):
	'''Draws a star that is proportional to the specified size'''
	verts = [(x,y-40*size),(x+10*size,y-10*size)]			#top center cone
	verts += [(x+40*size,y-10*size),(x+15*size,y+10*size)]	#top right cone
	verts += [(x+25*size,y+40*size),(x,y+20*size)]			#bottom right cone
	verts += [(x-25*size,y+40*size),(x-15*size,y+10*size)]	#bottom left cone
	verts += [(x-40*size,y-10*size),(x-10*size,y-10*size)]	#top leftcone
	draw.polygon(screen, col, verts, filled)

class CatchMe(keyBoard):
	"""Runs the Catch Me tile in the home screen to validate the calibration results"""
	def __init__(self, surface, box_size = 50):
		self.resX, self.resY = self.getRes(surface)
		self.background = Surface((self.resX,self.resY), SRCALPHA)
		self.backgroundImg = image.load("imgs/background.png").convert()
		self.background_alpha = 200
		self.text_alpha = 0
		self.text_colours = self.genGradient(primeCol = (13,47,48), duration = 100, delay = 2)
		self.display_title = False
		self.stop_blitting = False
		self.caption = True

		self.statsBar = Surface((self.resX,40), SRCALPHA)
		self.stats = {
			'score'	:	0
		}
		self.boxColours = self.genGradient(primeCol = (255,255,255), secCol = (26,157,130))


	def getRes(self, surface):
		"""Gets the resolution of the screen"""
		return surface.get_size()

	def getSpacing(self, text, Size, font_size):
		"""Returns the x position at which the text will blitted in order for it to be centered between a specified width"""
		space = font.Font('fonts/HelveNueThin/HelveticaNeueThn.ttf', font_size).size(text)
		return (Size-space[0])//2

	def drawBackground(self, surface, title="CATCH ME"):
		"""Draws the background setting for this game, including the stats bar that displays time and score"""
		surface.blit(self.backgroundImg, (0,0))
		draw.rect(self.background, (1,10,21,self.background_alpha), (0,0,self.resX,self.resY))
		draw.rect(self.background, (26,157,130,self.background_alpha), (0,0,self.resX, 40))
		draw.line(self.background, (255,255,255), (0,40), (self.resX,40))
		makeText(self.background, title, 20, (222,222,222), None, 20, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		makeText(self.background, "Score: %s" % str(self.stats['score']), 20, (222,222,222), None, self.resX-300, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		makeText(self.background, "Time: 60s", 20, (222,222,222), None, self.resX-145, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')

	def incrementCounter(self):
		"""Adjusts the alpha value of the background while the intro screen to the game is running to shown a blur out effect"""
		if self.display_title:
			self.background_alpha += 1 if self.background_alpha <= 250 else 0
		if self.background_alpha >= 226 and self.display_title:
			self.text_alpha += 2
		if self.display_title == False:
		 	self.text_alpha -= 2
		if self.display_title == False and self.text_alpha <= 150:
		 	self.background_alpha -= 2 if self.background_alpha >= 240 else 0

	def drawLevel(self, surface, level = "CATCH ME", caption = "Stare at the boxes until they disappear.", gameover = False):
		"""Draws the intro screen to each level of the game, displaying the instructions of the next level"""
		text = level
		hint = caption
		if self.text_alpha >= len(self.text_colours):	
			self.text_alpha = len(self.text_colours)-1	# stops blitting text if max alpha reached
			self.display_title = False
		if self.text_alpha <= 0 and self.display_title == False:
			self.stop_blitting = True
			self.text_alpha = 0
		if self.display_title == False and self.stop_blitting == False:	# blits background while the text is being blitted
			self.drawBackground(surface, level)
			if gameover == False:
				makeText(self.background, hint, 90, self.text_colours[self.text_alpha], None, self.getSpacing(hint, self.resX, 90), self.resY//2-150)
			if gameover:
				makeText(self.background, text, 250, self.text_colours[self.text_alpha], None, self.getSpacing(text, self.resX, 250), self.resY//2-200)
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
		"""Resets variables to default in order to run the game again"""
		self.background_alpha = 200
		self.text_alpha = 0
		self.display_title = True
		self.stop_blitting = False
		self.caption = True

	def getStats(self, score):
		"""Gets the stats of the current level and saves it in the class"""
		self.stats['score'] += score

	def drawStats(self, surface, countdown, title = "CATCH ME"):
		"""Draws the stats of the current level at the top bar"""		
		draw.rect(self.statsBar, (26,157,130,200), (0,0,self.resX, 40))
		draw.line(self.statsBar, (255,255,255), (0,40), (self.resX,40))
		makeText(self.statsBar, title, 20, (222,222,222), None, 20, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		makeText(self.statsBar, "Score: %s" % str(self.stats['score']), 20, (222,222,222), None, self.resX-300, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		makeText(self.statsBar, "Time: %ss" % str(round(countdown,2)), 20, (222,222,222), None, self.resX-145, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		surface.blit(self.statsBar, (0,0))

	class Box():
		"""Defines the rules that govern how a box will regenerate, react to collision with gazeData and change colours depending on dwell_delay during Catch Me"""
		def __init__(self, surface, boxColours):
			self.resX, self.resY = self.getRes(surface)
			self.alphaVal = 40
			self.colIndex = 0
			self.boxColours = boxColours
			self.colour = (self.boxColours[self.colIndex][0],self.boxColours[self.colIndex][1],self.boxColours[self.colIndex][2], self.alphaVal)
			self.boxSize = randint(75,150)
			self.boxResize = 29
			self.offset = 10
			self.boxLocation = randint(self.offset, self.resX-self.boxSize-self.offset), randint(self.offset+41, self.resY-self.boxSize-self.offset)
			self.cover = surface.subsurface(Rect(self.boxLocation[0], self.boxLocation[1], self.boxSize, self.boxSize)).copy()
			self.score = 0

		def getRes(self, surface):
			"Gets the resolution of the screen"
			return surface.get_size()

		def getSpacing(self, text, Size, font_size):
			"""Returns the x position at which the text will blitted in order for it to be centered between a specified width"""
			space = font.Font('fonts/HelveNueThin/HelveticaNeueThn.ttf', font_size).size(text)
			return (Size-space[0])//2

		def logic(self, surface, gazePos):
			"""Sets the rules for how the colour and size of the box will change as dwell increases and where it will reappear"""
			if Rect(self.boxLocation[0]+self.boxResize, self.boxLocation[1]+self.boxResize, self.boxSize-self.boxResize*2, self.boxSize-self.boxResize*2).collidepoint(gazePos):
				self.boxResize += 1	# increases box size
			else:
				# decreases box size when user is not focusing at the box anymore
				self.boxResize -= 1 if self.boxResize > 0 else 0 

			if Rect(self.boxLocation[0], self.boxLocation[1], self.boxSize, self.boxSize).collidepoint(gazePos):
				if self.alphaVal <= 253:
					self.alphaVal += 2		# increases the alpha value of the box as dwell_delay increase
				if self.colIndex < len(self.boxColours)-4:
					if self.colIndex < 1:
						self.colIndex += 1
					else:
						self.colIndex += 1 		# when the program has gone through all the colours in the list of gradient colours, it goes back to the first one
			else:
				self.alphaVal -= 2 if self.alphaVal >= 42 else 0
				if self.colIndex >= 1:
					self.colIndex -= 1 
			try:
				self.colour = (self.boxColours[self.colIndex][0],self.boxColours[self.colIndex][1],self.boxColours[self.colIndex][2], self.alphaVal)	# sets the colour of the box based on the dwell
			except:
				pass

			if self.alphaVal >= 254 or self.boxResize > 30:		# when the box changes to a certain colour or size drops to certain threshold, a new box generates at a new location
				surface.blit(self.cover, (self.boxLocation[0], self.boxLocation[1]))
				self.boxLocation = randint(self.offset, self.resX-self.boxSize-self.offset), randint(self.offset+41, self.resY-self.boxSize-self.offset)
				self.cover = surface.subsurface(Rect(self.boxLocation[0], self.boxLocation[1], self.boxSize, self.boxSize)).copy()
				self.alphaVal = 40
				self.colIndex = 0
				self.boxResize = 29
				self.score = 1									# score increases by 1
			else:
				self.score = 0

		def drawBox(self, surface):
			"""Draws the box on the screen"""
			surf = Surface((self.boxSize, self.boxSize), SRCALPHA)
			draw.rect(surf, self.colour, (0+self.boxResize, 0+self.boxResize, self.boxSize-self.boxResize*2, self.boxSize-self.boxResize*2))
			surface.blit(self.cover, (self.boxLocation[0], self.boxLocation[1]))
			surface.blit(surf, (self.boxLocation[0], self.boxLocation[1]))

class Game2:
	"""Runs the Catch Me game by initialzing the minigame's requirements"""
	def __init__(self, surface, screen_size):
		self.screen_size = screen_size
		self.catchMe = CatchMe(surface)
		self.boxes = [self.catchMe.Box(surface, self.catchMe.boxColours) for i in range(1)]
		#-----------------------------------------------------------------------------------
		self.drawn = False
		self.countdown = 60
		self.level_drawn = ''
		self.gameover = False
		self.gameoverCounter = 125
		self.resetDone = False

	def run(self, surface, gazePos, old_gazePos):
		"""Runs the Catch Me process"""
		if self.resetDone == False:
			self.catchMe.resetVars()	# resets the game's variables
			self.resetDone = True
		if self.gameover == False:
			if self.drawn == False:
				self.level_drawn = self.catchMe.drawLevel(surface)		# draws intro screen to game
			#-----------RUNS GAME------------
			if self.level_drawn == 'LEVEL DRAWN' and self.drawn == False:
				self.catchMe.resetVars()
				self.drawn = True
				self.level_drawn = ''
				for box in self.boxes:
					box.cover = surface.subsurface(Rect(box.boxLocation[0], box.boxLocation[1], box.boxSize, box.boxSize)).copy()
			if self.countdown == 0:
				return 'GAME OVER'
			if self.drawn:
				self.catchMe.drawStats(surface, self.countdown)
				for box in self.boxes:
					self.catchMe.getStats(box.score)
					box.logic(surface, gazePos)
					box.drawBox(surface)

				self.catchMe.getStats(score = 0)
				
				self.countdown -= 0.035
				if self.countdown < 0:
					self.countdown = 0
					self.gameover = True
		else:
			self.catchMe.drawLevel(surface, "GAME OVER", None, self.gameover)
			self.gameoverCounter -= 1 if self.gameoverCounter != 0 else 0

		self.catchMe.incrementCounter()
		if self.gameoverCounter == 0:	
			return 'GAMEOVER'
	

class Pong:
	"""Runs the Pong tile in the home screen to validate the calibration results"""
	def __init__(self, surface):
		self.resX, self.resY = self.getRes(surface)
		self.background = Surface((self.resX,self.resY), SRCALPHA)
		self.backgroundImg = image.load("imgs/background.png").convert()
		self.background_alpha = 200
		self.text_alpha = 0
		self.text_colours = keyBoard(surface).genGradient(primeCol = (13,47,48), duration = 100, delay = 2)
		self.display_title = True
		self.stop_blitting = False
		self.caption = True

		self.statsBar = Surface((self.resX,40), SRCALPHA)
		self.statsLevel1 = {
			'misses'	:	0,
			'longest_streak'	:	0,
			'streak'	:	0
		}

	def getRes(self, surface):
		"Gets the resolution of the screen"
		return surface.get_size()

	def getSpacing(self, text, Size, font_size):
		"""Returns the x position at which the text will blitted in order for it to be centered between a specified width"""
		space = font.Font('fonts/HelveNueThin/HelveticaNeueThn.ttf', font_size).size(text)
		return (Size-space[0])//2

	def drawBackground(self, surface, level):
		"""Draws the upper bar that displays the stats of the game (score, time left) and the background image"""
		surface.blit(self.backgroundImg, (0,0))
		draw.rect(self.background, (1,10,21,self.background_alpha), (0,0,self.resX,self.resY))
		draw.rect(self.background, (26,157,130,self.background_alpha), (0,0,self.resX, 40))
		draw.line(self.background, (255,255,255), (0,40), (self.resX,40))
		makeText(self.background, level, 20, (222,222,222), None, 20, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		makeText(self.background, "Streak: %s" % str(self.statsLevel1['longest_streak']), 20, (222,222,222), None, self.resX-450, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		makeText(self.background, "Misses: %s" % str(self.statsLevel1['misses']), 20, (222,222,222), None, self.resX-300, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		makeText(self.background, "Time: 60s", 20, (222,222,222), None, self.resX-145, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')

	def incrementCounter(self):
		"""Adjusts the alpha value of the background while the intro screen to the game is running to shown a blur out effect"""
		if self.display_title:
			self.background_alpha += 1 if self.background_alpha <= 250 else 0
		if self.background_alpha >= 226 and self.display_title:
			self.text_alpha += 2
		if self.display_title == False:
		 	self.text_alpha -= 2
		if self.display_title == False and self.text_alpha <= 150:
		 	self.background_alpha -= 1 if self.background_alpha >= 214 else 0

	def drawLevel(self, surface, level, caption, gameover = False):
		"""Draws the intro screen to each level of the game, displaying the instructions of the next level"""
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
			if gameover:
				text1 = "Longest Streak:  %s balls" % str(self.statsLevel1['longest_streak'])
				text2 = "    Total Misses:  %s balls" % str(self.statsLevel1['misses'])
				text3_1, text3_2 = "CALIBRATION", "RESULT"
				text4 = "PERFECT"
				makeText(self.background, text1, 90, self.text_colours[self.text_alpha], None, self.getSpacing(text1, self.resX, 90), self.resY//2-310)
				makeText(self.background, text2, 90, self.text_colours[self.text_alpha], None, self.getSpacing(text2, self.resX, 90), self.resY//2-190)
				draw.line(self.background, (255,255,255, self.text_alpha), (300,545), (self.resX-300, 545), 5)
				makeText(self.background, text3_1, 50, (222,222,222,self.text_alpha), None, 300, self.resY//2+90)
				makeText(self.background, text3_2, 50, (222,222,222,self.text_alpha), None, 300, self.resY//2+145)
				makeText(self.background, text4, 110, self.text_colours[self.text_alpha], None, 690, self.resY//2+80)
				for x in range(5):
					drawStar(self.background, self.text_colours[self.text_alpha], 1250+83*x, self.resY//2+140, 0.9, 1)
					if x < 4:
						drawStar(self.background, (222,222,222,self.text_alpha), 1250+83*x, self.resY//2+140, 0.9)
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
		"""Resets variables to default in order to run the game again"""
		self.background_alpha = 200
		self.text_alpha = 0
		self.display_title = True
		self.stop_blitting = False
		self.caption = True

	def getStats_Level1(self, streak, misses):
		"""Gets the stats of the current level and saves it in the class"""
		self.statsLevel1['misses']	+= misses
		self.statsLevel1['streak'] += streak
		if misses == 1:	self.statsLevel1['streak'] = 0
		if self.statsLevel1['streak'] > self.statsLevel1['longest_streak']:
			self.statsLevel1['longest_streak'] += streak 

	def drawStats_Level1(self, surface, level, countdown):
		"""Draws the stats of the current level at the top bar"""
		draw.rect(self.statsBar, (26,157,130,200), (0,0,self.resX, 40))
		draw.line(self.statsBar, (255,255,255), (0,40), (self.resX,40))
		makeText(self.statsBar, level, 20, (222,222,222), None, 20, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		makeText(self.statsBar, "Streak: %s" % str(self.statsLevel1['longest_streak']), 20, (222,222,222), None, self.resX-450, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		makeText(self.statsBar, "Misses: %s" % str(self.statsLevel1['misses']), 20, (222,222,222), None, self.resX-300, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		makeText(self.statsBar, "Time: %ss" % str(round(countdown,2)), 20, (222,222,222), None, self.resX-145, 10, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		surface.blit(self.statsBar, (0,0))


	class Ball:
		def __init__(self, surface, ball_size, paddle_size, screen_size):
			"""Contains each ball's attributes and rules that govern how it moves during Pong"""
			self.screen_size = screen_size
			self.ball_size = ball_size
			self.ball_x, self.ball_y = randint(self.ball_size, 800), randint(self.ball_size, 600)	# the position of the ball on the screen
			self.ball_oldx, self.ball_oldy = self.ball_x, self.ball_y
			self.vel_x, self.vel_y = 10, 10					# the velocity of the ball
			self.reverse_x, self.reverse_y = False, False 	# the direction that the ball is travelling in
			self.resx, self.resy = screen_size
			self.past_screen = False
			self.paddle_size = paddle_size

			self.initCover = False
			self.hiddenBg = Surface((1920,1080))
			self.hiddenBg.blit(image.load("imgs/hidden_background.png").convert(), (0,0))	# the hidden background allows the program to get a copy of the screen from the background image so that anything blitted on the screen that shouldnt be there isn't reblitted when blitting the cover
			self.hiddenCover = 0

			self.streak = 0
			self.misses = 0

		def getCover(self, surface):
			"""Gets the initial cover for the ball so it can be used to cover the ball's tracks"""
			if self.initCover == False:
				self.hiddenCover = self.hiddenBg.subsurface(Rect(self.ball_x-self.ball_size, self.ball_y-self.ball_size, self.ball_size*2, self.ball_size*2)).copy()
				self.initCover = True

		def logic(self, paddle_location, paddle_location_AI, gazePos, old_gazePos, orientation, AI):
			"""A set of rules that define how the ball will move and where it will ricochet"""
			if self.ball_x >= self.resx-self.ball_size:
				if orientation == 'HORIZONTAL':
					self.reverse_x = True
				if orientation == 'VERTICAL':
					if AI:
						self.ball_x, self.ball_y = self.resx//2, randint(0, self.resy)
					else:
						self.ball_x, self.ball_y = 0, randint(0, self.resy)
					self.past_screen = True
					self.reverse_x = choice([True, False])
					self.vel_x, self.vel_y = randint(5,20), randint(5,20)	# this means that the ball has hit past the paddle and so it will define the ball with a new starting position
					self.misses = 1
			else:
				self.past_screen = False
				self.misses = 0

			if self.ball_x <= self.ball_size:
				self.reverse_x = False

			if AI:
				#-------When it is level 4, AI runs with this set of rules-----------
				if Rect(paddle_location_AI[0], paddle_location_AI[1], self.paddle_size[1], self.paddle_size[0]).collidepoint((self.ball_x-self.ball_size, self.ball_y)):#ball_y >= 590:
					self.reverse_x = False
					self.vel_y += abs(self.ball_y-self.ball_oldy)//6	# dividing its velocity by 6 slows down the AI's responsiveness to the ball and it will gradually get faster as the ball approaches the AI paddle
				else:
					pass
				if self.ball_x <= self.ball_size:
					self.ball_x, self.ball_y = self.resx//2, randint(0, self.resy)
					self.past_screen = True
					self.reverse_x = choice([True, False])
					self.vel_x, self.vel_y = randint(5,20), randint(5,20)

			if orientation == 'HORIZONTAL':
				if Rect(paddle_location).collidepoint((self.ball_x, self.ball_y+self.ball_size)):#ball_y >= 590:
					self.reverse_y = True
					self.vel_x += abs(gazePos[0]-old_gazePos[0])//6
					self.streak = 1
				else:
					self.streak = 0

				if self.ball_y >= self.resy-self.ball_size:
					self.ball_x, self.ball_y = randint(0, self.resx), 0
					self.past_screen = True
					self.reverse_x = choice([True, False])
					self.vel_x, self.vel_y = randint(5,20), randint(5,20)
					self.misses = 1
					self.streak = 0
				else:
					self.past_screen = False
					self.misses = 0

			if orientation == 'VERTICAL':
				if self.ball_y >= self.resy-self.ball_size:
					self.reverse_y = True
				if Rect(paddle_location).collidepoint((self.ball_x+self.ball_size, self.ball_y)):#ball_y >= 590:
					self.reverse_x = True
					self.vel_y += abs(gazePos[1]-old_gazePos[1])//6
					self.streak = 1
				else:
					self.streak = 0

			if self.ball_y <= self.ball_size+40:
				self.reverse_y = False
			if self.reverse_x:
				self.ball_x -= self.vel_x
			if self.reverse_x == False:
				self.ball_x += self.vel_x
			if self.reverse_y:
				self.ball_y -= self.vel_y
			if self.reverse_y == False:
				self.ball_y += self.vel_y

			return self.past_screen

		def drawBall(self, surface, colour):
			"""Draws the ball onto the screen"""
			surface.blit(self.hiddenCover, (self.ball_oldx-self.ball_size, self.ball_oldy-self.ball_size))
			# Normalizes the ball's position so that it isn't out of bounds
			if self.ball_x+self.ball_size > 1920:
				self.ball_x -= self.ball_x+self.ball_size-1920
			if self.ball_x-self.ball_size < 0:
				self.ball_x += abs(self.ball_x-self.ball_size)
			if self.ball_y+self.ball_size > 1080:
				self.ball_y -= self.ball_y+self.ball_size-1080
			if self.ball_y-self.ball_size < 0:
				self.ball_y += abs(self.ball_y-self.ball_size)
			x1, y1 = self.ball_x-self.ball_size, self.ball_y-self.ball_size
			x2, y2 = self.ball_size*2, self.ball_size*2
			self.hiddenCover = self.hiddenBg.subsurface(Rect(x1, y1, x2, y2)).copy()
			draw.circle(surface, colour, (self.ball_x, self.ball_y), self.ball_size)

	class Paddle:
		"""Defines the rules that govern how a paddle will move along the x-axis or y-axis"""
		def __init__(self, surface, paddle_size, screen_size):
			self.screen_size = screen_size
			self.paddle_size = paddle_size
			self.offsetFromWall = 40
			self.paddle_location = paddle_size[0]//2-50, self.screen_size[1]-self.paddle_size[1], self.paddle_size[0], self.paddle_size[1]
			self.paddle_location_AI = [self.offsetFromWall, 100-self.paddle_size[0]//2]
			self.hiddenBg = Surface((1920,1080))
			self.hiddenBg.blit(image.load("imgs/hidden_background.png").convert(), (0,0))
			self.coverHorizontal = self.hiddenBg.subsurface(Rect(self.paddle_location)).copy()
			self.platform = surface.subsurface(Rect(0, self.screen_size[1]-self.paddle_size[1], self.screen_size[0], self.paddle_size[1])).copy()
			self.coverVertical = self.hiddenBg.subsurface(Rect(self.screen_size[0]-self.paddle_size[1]-self.offsetFromWall, 100-self.paddle_size[0]//2, self.paddle_size[1], self.paddle_size[0])).copy()
			self.coverVertical_AI = self.hiddenBg.subsurface(Rect(self.offsetFromWall, 100-self.paddle_size[0]//2, self.paddle_size[1], self.paddle_size[0])).copy()

		def movePaddle_AI(self, ballPos, old_ballPos, difficulty = 1.8):
			"""Moves the AI's paddle based on the specified difficulty"""
			if self.paddle_location_AI[1] < ballPos[1]-self.paddle_size[0]//2:
	 			self.paddle_location_AI[1] += 20//(ballPos[0]/difficulty/100) if self.paddle_location_AI[1] < self.screen_size[1]-self.paddle_size[0]/2 else 0
			if self.paddle_location_AI[1] > ballPos[1]-self.paddle_size[0]//2:
	 			self.paddle_location_AI[1] -= 20//(ballPos[0]/difficulty/100) if self.paddle_location_AI[1] >= 41 else 0		# the greater the difficulty, the quicker the paddle will follow the ball

		def drawPaddle(self, surface, colour, gazePos, old_gazePos, ballPos, old_ballPos, orientation, AI):
			"""Draws the paddle on the screen based on whether the game is running along the x or y axis"""
			if orientation == 'HORIZONTAL':
				self.paddle_location = gazePos[0]-self.paddle_size[0]//2, self.screen_size[1]-self.paddle_size[1]-self.offsetFromWall, self.paddle_size[0], self.paddle_size[1]
				surface.blit(self.coverHorizontal, (old_gazePos[0]-self.paddle_size[0]//2, self.screen_size[1]-self.paddle_size[1]-self.offsetFromWall))
				self.coverHorizontal = self.hiddenBg.subsurface(Rect(gazePos[0]-self.paddle_size[0]//2, self.screen_size[1]-self.paddle_size[1]-self.offsetFromWall, self.paddle_size[0], self.paddle_size[1])).copy()
				draw.rect(surface, colour, Rect(self.paddle_location))
			if orientation == 'VERTICAL':
				self.paddle_location = self.screen_size[0]-self.paddle_size[1]-self.offsetFromWall, gazePos[1]-self.paddle_size[0]//2, self.paddle_size[1], self.paddle_size[0]
				surface.blit(self.coverVertical, (self.screen_size[0]-self.paddle_size[1]-self.offsetFromWall, old_gazePos[1]-self.paddle_size[0]//2))
				self.coverVertical = self.hiddenBg.subsurface(Rect(self.screen_size[0]-self.paddle_size[1]-self.offsetFromWall, gazePos[1]-self.paddle_size[0]//2, self.paddle_size[1], self.paddle_size[0])).copy()
				draw.rect(surface, colour, Rect(self.paddle_location))
			if AI:
				# Normalizes paddle location to ensure its within the screen dimensions
				if self.paddle_location_AI[1]+self.paddle_size[0] <= self.screen_size[1] and self.paddle_location_AI[1] >= 41:
					surface.blit(self.hiddenBg.subsurface(Rect(self.paddle_location_AI[0], self.paddle_location_AI[1], self.paddle_size[1], self.paddle_size[0])).copy(), (self.paddle_location_AI[0], self.paddle_location_AI[1]))
				self.movePaddle_AI(ballPos, old_ballPos)
				if self.paddle_location_AI[1]+self.paddle_size[0] <= self.screen_size[1] and self.paddle_location_AI[1] >= 45:
					draw.rect(surface, colour, Rect(self.paddle_location_AI[0], self.paddle_location_AI[1], self.paddle_size[1], self.paddle_size[0]-10))
				else:
					if self.paddle_location_AI[1]+self.paddle_size[0] > self.screen_size[1]-10:
						draw.rect(surface, colour, Rect(self.paddle_location_AI[0], self.screen_size[1]-self.paddle_size[0]-10, self.paddle_size[1], self.paddle_size[0]))
					if self.paddle_location_AI[1] < 51:
						draw.rect(surface, colour, Rect(self.paddle_location_AI[0], 51, self.paddle_size[1], self.paddle_size[0]))

class Game:
	"""Runs the Pong game by initialzing the minigame's requirements"""
	def __init__(self, surface, screen_size, number_of_balls=1):
		self.screen_size = screen_size
		self.pong = Pong(surface)
		self.paddle = self.pong.Paddle(surface, (150, 30), self.screen_size)	
		self.number_of_balls = number_of_balls
		self.balls = [self.pong.Ball(surface, randint(15,20), self.paddle.paddle_size, self.screen_size) for i in range(self.number_of_balls)]
		#-----------------------------------------------------------------------------------
		self.drawn = False
		self.countdown = 60
		self.levelNum = 1
		self.level="LEVEL %s" % str(self.levelNum)
		self.captions = ["Follow the ball to hit it with your paddle.", "How many balls can you hit?", "Let's invert your orientation.", "I bet you can't beat me!"]
		self.level_drawn = ''
		self.past_screen = False
		self.orientation = 'HORIZONTAL'
		self.gameover = False
		self.AI = False

	def normalizeGazePos(self, gazePosX, gazePosY):
		"""Normalizes the gazePos so that the paddle always remains in bounds"""
		if self.orientation == 'HORIZONTAL':
			if gazePosX >= self.screen_size[0]-self.paddle.paddle_size[0]//2:  
				gazePosX = self.screen_size[0]-self.paddle.paddle_size[0]//2
			if gazePosX <= self.paddle.paddle_size[0]//2: 
				gazePosX = self.paddle.paddle_size[0]//2
		if self.orientation == 'VERTICAL':
			if gazePosY >= self.screen_size[1]-self.paddle.paddle_size[0]//2:  
				gazePosY = self.screen_size[1]-self.paddle.paddle_size[0]//2
			if gazePosY <= self.paddle.paddle_size[0]//2+41: 
				gazePosY = self.paddle.paddle_size[0]//2+41
		return (gazePosX, gazePosY)

	def normalizeGazePos_AI(self):
		"""Normalizes the AI's paddle position so that the paddle always remains in bounds as well"""
		if self.AI:
			if self.balls[0].ball_y >= self.screen_size[1]-self.paddle.paddle_size[0]//2:  
				self.balls[0].ball_y = self.screen_size[1]-self.paddle.paddle_size[0]//2
			if self.balls[0].ball_y <= self.paddle.paddle_size[0]//2+41:
				self.balls[0].ball_y = self.paddle.paddle_size[0]//2+41

	def run(self, surface, gazePos, old_gazePos):
		"""Runs the Pong process"""
		if self.gameover == False:
			if 3 <= self.levelNum <= 4:	self.orientation = 'VERTICAL'		# when level is 3 or 4, the orientation becomes vertical
			if self.levelNum == 4:	self.AI = True
			if self.drawn == False:
				self.level_drawn = self.pong.drawLevel(surface, self.level, self.captions[self.levelNum-1])		# draws intro screen to game
			if self.level_drawn == 'LEVEL DRAWN' and self.drawn == False:
				self.pong.resetVars()
				self.drawn = True
				self.level_drawn = ''
			if self.countdown == 0:
				self.levelNum += 1
				self.pong.resetVars()
				self.countdown = 60
				self.level = "LEVEL %s" % str(self.levelNum)
				self.drawn = False
				if self.levelNum == 5:
					self.gameover = True
			if self.drawn:
				#------RUNS PONG----
				self.pong.drawStats_Level1(surface, self.level, self.countdown)
				for ball in self.balls:
					ball.getCover(surface)
					self.past_screen = ball.logic(self.paddle.paddle_location, self.paddle.paddle_location_AI, gazePos, old_gazePos, self.orientation, self.AI)
					if self.past_screen:
						pass#time.sleep(1)
					ball.drawBall(surface, (255,255,255))
					self.pong.getStats_Level1(ball.streak, ball.misses)
				self.countdown -= 0.035
				if self.countdown < 0:
					self.countdown = 0
			self.paddle.drawPaddle(surface, (26,157,130), self.normalizeGazePos(gazePos[0], gazePos[1]), self.normalizeGazePos(old_gazePos[0], old_gazePos[1]), (self.balls[0].ball_x, self.balls[0].ball_y), (self.balls[0].ball_oldx, self.balls[0].ball_oldy), self.orientation, self.AI)
			self.balls[0].ball_oldx, self.balls[0].ball_oldy = self.balls[0].ball_x, self.balls[0].ball_y
		else:
			self.pong.drawLevel(surface, "GAME OVER", None, self.gameover)
		if self.gameover:
			return 'GAMEOVER'
		self.pong.incrementCounter()


#-----GRAPHICS-----
def drawAACircle(surface, x, y, r, colour, size, layout="center"):
	"""Draws anti-aliased circle"""
	if size == 1:
		gfxdraw.aacircle(surface, x, y, r, colour)
	else:
		if layout == "center":
			for i in range(size//2+1):
				gfxdraw.aacircle(surface, x, y, r+i, colour)
		elif layout == "inwards":
			for i in range(size+1):
				gfxdraw.aacircle(surface, x, y, r-i, colour)
		elif layout == "outwards":
			for i in range(size+1):
				gfxdraw.aacircle(surface, x, y, r+i, colour)

def makeText(surface, text, text_size, color, background_color, x, y, fontselection = 'fonts/HelveNueThin/HelveticaNeueThn.ttf'):
	"""Renders text onto the screen"""
	surface.blit(font.Font(fontselection, text_size).render(str(text), True, color), (x, y))

def makeTextFreetype(surface, text, text_size, color, background_color, x, y, fontselection = 'fonts/HelveNueThin/HelveticaNeueThn.ttf'):
	"""Render text onto the screen with any FreeType font"""
	surface.blit(freetype.Font(None).render(str(text), color, None, size = text_size)[0], (x, y))

#-----SCREENS-----
def getSpacing(text, Size, font_size, fontselection = 'fonts/HelveNueThin/HelveticaNeueThn.ttf', alignment = 'center'):
	"""Returns the x position at which the text will blitted in order for it to be centered/right aligned in a specified width"""
	space = font.Font(fontselection, font_size).size(text)
	if alignment == 'center':
		return (Size-space[0])//2
	elif alignment == 'right':
		return (Size-space[0])

def drawOutline(surface, colour, box, guestLineX, guestLineY, guestLineLength, thickness = 5):
	"""Draws the outline of a rectangle slowly pixel by pixel in the direction: Right, Down, Left, Up"""
	spx, epx = 0, 0
	spy, epy = 0, 0

	if guestLineX == 'FORWARD':
		spx, epx = box[0], box[0]+guestLineLength
	if guestLineX == 'BACKWARDS':
		spx, epx = box[0]+box[2], box[0]+box[2]-guestLineLength
	if guestLineX == None:
		if guestLineY == 'DOWN':
			spx, epx = box[0]+box[2], box[0]+box[2]
		if guestLineY == 'UP':
			spx, epx = box[0], box[1]

	if guestLineY == 'DOWN':
		spy, epy = box[1], box[1]+guestLineLength
	if guestLineY == 'UP':
		spy, epy = box[1]+box[3], box[1]+box[3]-guestLineLength
	if guestLineY == None:
		if guestLineX == 'FORWARD':
			spy, epy = box[1], box[1]
		if guestLineX == 'BACKWARDS':
			spy, epy = box[1]+box[3], box[1]+box[3]

	if guestLineX == 'FORWARD' and box[0]+guestLineLength > box[0]+box[2]:
		guestLineY = 'DOWN'
		guestLineX = None
		guestLineLength = 0
		epx, epy = box[0]+box[2],box[1]
	if guestLineY == 'DOWN' and guestLineX == None and box[1]+guestLineLength > box[1]+box[3]:
		guestLineY = None
		guestLineX = 'BACKWARDS'
		guestLineLength = 0
		epx, epy = box[0]+box[2], box[1]+box[3]
	if guestLineX == 'BACKWARDS' and guestLineY == None and box[0]+box[2]-guestLineLength < box[0]:
		guestLineX = None
		guestLineY = 'UP'
		guestLineLength = 0
		epx, epy = box[0], box[1]+box[3]
	if guestLineY == 'UP' and guestLineX == None and box[1]+box[3]-guestLineLength < box[1]:
		epx, epy = box[0], box[1]

	draw.line(surface, colour, (spx,spy), (epx, epy), thickness)

def createTextFields(surf, login, signup, number, fields, fieldNum = 0, spacing = 76):
	"""Draws text fields onto the screen and highlights the current field that is being edited"""
	time1, time2 = 0,0
	startPos = 0
	outlineCol = (44,219,180,100)
	outlineThickness = 1
	if login and signup == False:
		startPos = 342
		spacing = 90
	else:	startPos = 282
	constant = 0
	time1 = time.get_ticks()
	for i in range(number):
		if i == 2:	constant = 10
		if i == fieldNum:	outlineCol, outlineThickness = (255,255,255), 3
		else:	outlineCol, outlineThickness = (44,219,180,100), 1
		draw.rect(surf, (44,219,180,20), (2, startPos+spacing*i+constant, 596, 56))
		padlib.draw.rrect(surf, outlineCol, (0, startPos-2+spacing*i+constant, 600, 60), 7, outlineThickness)
		makeText(surf, fields[i], 30, (216,216,216), None, 100, startPos+11+spacing*i+constant)
	time2 = time.get_ticks()

	#print('Text Fields: ', time2-time1)

class IntroScreen():
	"""Runs the initial screen when the user first starts up the program with the options of logging in, signing up, or as guest user"""
	def __init__(self, surface):
		self.resX, self.resY = self.getRes(surface)
		self.background = Surface((self.resX-375*2,self.resY), SRCALPHA)

		#----SURFS---
		self.loginSurfs = {
				'cover'	:	Surface((375,self.resY), SRCALPHA),
				'surf'	:	Surface((375,self.resY), SRCALPHA)		
			}

		self.signupSurfs = {
				'cover'	:	Surface((375,self.resY), SRCALPHA),
				'surf'	:	Surface((375,self.resY), SRCALPHA)		
			}

		self.calibSurfs = {
				'cover' :	Surface((1170,300), SRCALPHA),
				'surf'	:	Surface((1170,300), SRCALPHA),
			}

		#----DWELL DELAYS---
		self.login_dwell_delay = 1			#setting value to 0 will mean that program will not blit log in and sign up prompts
		self.signup_dwell_delay = 1
		self.calibPanel_dwell_delay = 6

		#---LOGIN, SIGNUP and GUEST---
		self.login = False
		self.signup = False
		self.guest = True

		self.loggingIn = False
		self.signingUp = False

		self.signupCover = signupCover.convert()
		self.loginCover = loginCover.convert()
		self.calibCover = calibCover.convert()
		self.textFieldsCover = 0

		self.logIn_alreadyChecked = False
		self.signUp_alreadyChecked = False

		self.defaultLoginFields = ["User ID or Email", "Password", False, False]
		#self.defaultLoginFieldsDrawn = [False, False]
		self.defaultSignUpFields = ["Full Name", "Email", "User ID", "Password", False, False, False, False]
		#self.defaultSignUpFieldsDrawn = [False, False, False, False]


		self.guestButtonCover = surface.subsurface(Rect(705,415, 510,90)).copy()
		self.guestLineLength = 0
		self.guestLineY = None
		self.guestLineX = 'FORWARD'

		#----ANIMATION---
		self.animate = False
		self.animationCounter = 0
		self.animationPicCounter = 0
		self.logo_rect = logo.get_rect()
		self.logo = logo
		self.angle = 0
		self.size = 0
		self.fullrotations = 0

		self.centerViewCover = centerViewCover.convert()
		self.user_name = user_name.convert_alpha()
		self.password = password.convert_alpha()
		self.fullname = fullname.convert_alpha()
		self.email = email.convert_alpha()
		self.logo = logo.convert_alpha()
		self.logoLeft = logoLeft.convert_alpha()
		self.logoRight = logoRight.convert_alpha()


	def drawScreen(self, surface, gazePos, tracker_state, state, old_state):
		"""Draws log in, signup and calibration and center screens"""
		self.drawLogIn(surface, gazePos, state)			# makes eye-tracking laggy
		self.drawSignUp(surface, gazePos, state)		# makes eye-tracking laggy
		self.drawCalibPanel(surface, gazePos, state)	# makes eye-tracking laggy
		centerView = self.drawCenterView(surface, gazePos, tracker_state, state, old_state)
		return centerView

	def getRes(self, surface):
		"Gets the resolution of the screen"
		return surface.get_size()

	def getActivity(self, surface, gazePos):
		"""Gets the activity of the start screen"""
		if Rect(0,0,375,1080).collidepoint(gazePos):
			return "Log In"
		if Rect(1545,0,375,1080).collidepoint(gazePos):
			return "Sign Up"
		if Rect(375, self.resY-300, 1170, 300).collidepoint(gazePos):
			return "Calibrate"
		if Rect(710, 420, 500, 80).collidepoint(gazePos):
			return "Guest"

	def centerView(self, surface, gazePos, tracker_state, field = '', fieldNum = 0):
		"Creates the main area where the user will enter data into text fields"
		surface.blit(self.centerViewCover, (375,0))
		draw.rect(self.background, (1,10,21,229), (0,0,self.resX-375*2,self.resY))
		surface.blit(self.background, (375,0))
		surf = Surface((600,self.resY), SRCALPHA)
		self.textFieldsCover = surface.subsurface((Rect(659,277,603,303))).copy()
		
		if self.login and self.signup == False:
			fields = ["User ID or Email", "Password"]
			if len(field) > 0:
				fields[fieldNum] = field
			createTextFields(surf, self.login, self.signup, 2, fields)		# creates fields (2) specifically for log in 
			surf.blit(self.user_name, (18, 353))
			surf.blit(self.password, (25, 437))									# blits the log in screen

		elif self.signup and self.login == False:
			fields = ["Full Name", "Email", "User ID", "Password"]
			if len(field) > 0:												# creates fields (4) specifically for sign up
				fields[fieldNum] = field
			createTextFields(surf, self.login, self.signup, 4, fields)		# blits the sign up screen
			surf.blit(self.fullname, (22, 289))
			surf.blit(self.email, (20, 367))
			surf.blit(self.user_name, (18, 456))
			surf.blit(self.password, (26, 525))

		else:
			draw.rect(surf, (44,219,180,60), (50, 420, 500, 80))
			padlib.draw.rrect(surf, (44,219,180,20), (50, 420, 500, 80), 7, 1)
			makeText(surf, "GUEST", 40, (216,216,216), None, getSpacing("GUEST", 600, 40, 'fonts/HelveNueBold/HelveticaNeueBold.ttf'), 436, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')

			# diplays the tracker state as connected or disconnected
			draw.rect(surf, (44,219,180,60), (50, 540, 500, 80))
			padlib.draw.rrect(surf, (44,219,180,100), (50, 540, 500, 80), 7, 1)
			if tracker_state != 0:
				makeText(surf, "DISCONNECTED", 40, (216,216,216), None, getSpacing("DISCONNECTED", 600, 40, 'fonts/HelveNueBold/HelveticaNeueBold.ttf'), 556, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
			elif tracker_state == 0:
				makeText(surf, "CONNECTED", 40, (216,216,216), None, getSpacing("CONNECTED", 600, 40, 'fonts/HelveNueBold/HelveticaNeueBold.ttf'), 556, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')
		surface.blit(self.logo, (800,50))
		surface.blit(surf, (660,0))

	def logIn(self, surface, dwell_delay, gazePos):
		"Creates the login panel as an independent surface"
		surface.blit(self.loginCover, (0,0))									#.covert() reduces the image load time by nearly 60 %
		draw.rect(self.loginSurfs['cover'], (1,10,21,229), (0,0,375,self.resY))
		surface.blit(self.loginSurfs['cover'], (0,0))
		draw.rect(self.loginSurfs['surf'], (0,255,198,10+dwell_delay), (0,0,375,self.resY))
		gfxdraw.filled_circle(self.loginSurfs['surf'], 186, 450, 60, (44,219,180,100))
		self.loginSurfs['surf'].blit(login, (139,420))
		drawAACircle(surface, 186, 450, 60,(44,219,180,215), 8)
		makeText(surface, "Log in", 28, (216,216,216), None, 148, 535)
		makeText(surface, "Look to the left to log in!", 24, (216,216,216), None, 65, 50)
		surface.blit(self.loginSurfs['surf'], (0,0))

	def signUp(self, surface, dwell_delay, gazePos):
		"Creates the sign in panel as an independent surface"
		surface.blit(self.signupCover, (1545,0))
		draw.rect(self.signupSurfs['cover'], (1,10,21,229), (0,0,375,self.resY))
		surface.blit(self.signupSurfs['cover'], (1545,0))
		draw.rect(self.signupSurfs['surf'], (0,201,215,12+dwell_delay), (0,0,375,self.resY))
		gfxdraw.filled_circle(self.signupSurfs['surf'], 189, 450, 60, (34,173,210,150))
		self.signupSurfs['surf'].blit(signup, (144,405))
		drawAACircle(surface, 1734, 450, 60,(34,173,210,215), 8)
		makeText(surface, "Sign up", 28, (216,216,216), None, 1690, 535)
		makeText(surface, "Look to the right to sign up!", 24, (216,216,216), None, 1598, 50)
		surface.blit(self.signupSurfs['surf'], (self.resX-375,0))

	def calibrationPanel(self, surface, dwell_delay, gazePos):
		"Creates the calibration panel as an independent surface near the bottom"
		surface.blit(self.calibCover, (375,self.resY-300))
		draw.rect(self.calibSurfs['cover'], (1,10,21,229), (0,0,1170,300))
		surface.blit(self.calibSurfs['cover'], (375,self.resY-300))
		draw.rect(self.calibSurfs['surf'], (255,255,255,50+dwell_delay), (0,0,1170,300))
		surface.blit(self.calibSurfs['surf'], (375,self.resY-300))
		makeText(surface, "Look here to . . .", 28, (6,16,26), None, 375+getSpacing("Look here to . . .", 1170, 28), 840)
		makeText(surface, "CALIBRATE EYE-TRACKER", 90, (6,16,26), None, 375+getSpacing("CALIBRATE EYE-TRACKER", 1170, 90), 900)
		
	def dwellNormalize(self, dwell_delay, maximum = 140, minimum = 0):
		"""Normailzes the dwell_delay so that it doesn't exceed the maximum or the minimum"""
		if dwell_delay > maximum: dwell_delay = maximum
		if dwell_delay < minimum:	dwell_delay = minimum
		return dwell_delay

	def drawCenterView(self, surface, gazePos, tracker_state, state, old_state):
		"""Draws the center screen where the text fields and guest button are located"""
		#-----------KEYBOARD STATE----------
		if state != old_state or (self.login or self.signup):
			if state == 'OFF':
				self.centerView(surface, gazePos, tracker_state)	#blit background
				if self.login_dwell_delay == 0:						# sets the dwell delay to greater than 0
					self.login_dwell_delay = 1						# so that side covers can be blitted once
				if self.login_dwell_delay == 140:
					self.login_dwell_delay = 139
				if self.signup_dwell_delay == 0:
					self.signup_dwell_delay = 1	
				if self.signup_dwell_delay == 142:
					self.signup_dwell_delay = 141
				if self.calibPanel_dwell_delay == 0:
					self.calibPanel_dwell_delay = 6
				if self.calibPanel_dwell_delay == 142:
					self.calibPanel_dwell_delay = 141
				self.drawLogIn(surface, gazePos, state)						
				self.drawSignUp(surface, gazePos, state)
				self.drawCalibPanel(surface, gazePos, state)
			elif state == 'ON' and (self.login or self.signup):
				self.centerView(surface, gazePos, tracker_state)	#blit background
				return 'DRAW KEYBOARD'
			elif state == 'ON':
				return 'DRAW KEYBOARD'

	def drawLogIn(self, surface, gazePos, state):
		"""Draws the log in side panel everytime the user looks at it"""
		self.login_dwell_delay = self.dwellNormalize(self.login_dwell_delay)
		if self.login_dwell_delay > 0 and self.login_dwell_delay < 138 and state != 'ON':
			self.logIn(surface, self.login_dwell_delay, gazePos)	# this line makes eye-tracking laggy
		if state != 'ON':
			if self.getActivity(surface, gazePos) == "Log In":
				self.login_dwell_delay += 3
			elif self.login_dwell_delay != 0:
				self.login_dwell_delay -= 3

	def drawSignUp(self, surface, gazePos, state):
		"""Draws the sign up side panel everytime the user looks at it"""
		self.signup_dwell_delay = self.dwellNormalize(self.signup_dwell_delay, 142)
		if self.signup_dwell_delay != 0 and self.signup_dwell_delay != 142 and state != 'ON':			
			self.signUp(surface, self.signup_dwell_delay, gazePos)	# this line makes eye-tracking laggy
		if state != 'ON':
			if self.getActivity(surface, gazePos) == "Sign Up":
				self.signup_dwell_delay += 3
			elif self.signup_dwell_delay != 0:
				self.signup_dwell_delay -= 3

	def drawCalibPanel(self, surface, gazePos, state):
		"""Draws the calibration bottom panel everytime the user looks at it"""
		self.calibPanel_dwell_delay =  self.dwellNormalize(self.calibPanel_dwell_delay, 142)
		if self.calibPanel_dwell_delay != 0 and self.calibPanel_dwell_delay != 142 and state != 'ON':
			self.calibrationPanel(surface, self.calibPanel_dwell_delay, gazePos)
		if state != 'ON':
			if self.getActivity(surface, gazePos) == "Calibrate":
				self.calibPanel_dwell_delay += 3
			elif self.calibPanel_dwell_delay != 0:
				self.calibPanel_dwell_delay -= 3

	def logIn_check(self):
		"""Checks if the user is looking at the log in panel"""
		if (self.login_dwell_delay == 143 or self.login_dwell_delay == 140) and self.signup_dwell_delay != 142:
			self.login = True
		else:
			self.login = False
		return self.login

	def signUp_check(self):
		"""Checks if the user is looking at the sign up panel"""
		if self.signup_dwell_delay >= 144 and self.login_dwell_delay != 140:
			self.signup = True
		else:
			self.signup = False
		return self.signup

	def fillForm(self, surface, fields = ["User ID or Email", "Password"], fieldNum = 0):
		"""Fills the log in or sign up form"""
		time1, time2 = 0,0
		surface.blit(self.textFieldsCover, (659,277))
		surf = Surface((600,self.resY), SRCALPHA)
		if self.loggingIn and self.signingUp == False:
			for i in range(len(fields)):
				if len(fields[i]) < 1:
					fields[i] = self.defaultLoginFields[i]
			createTextFields(surf, True, False, 2, fields, fieldNum)
			surf.blit(self.user_name, (18, 353))
			surf.blit(self.password, (25, 437))
			surface.blit(surf, (660,0))
		elif self.signingUp and self.loggingIn == False:
			for i in range(len(fields)):
				if len(fields[i]) < 1:
					fields[i] = self.defaultSignUpFields[i]
			time1 = time.get_ticks()
			createTextFields(surf, False, True, 4, fields, fieldNum)	# takes 13 ms
			time2 = time.get_ticks()

			surf.blit(self.fullname, (22, 289))
			surf.blit(self.email, (20, 367))
			surf.blit(self.user_name, (18, 456))
			surf.blit(self.password, (26, 525))
			surface.blit(surf, (660,0))
		#print("Form: ", time2-time1)

	def guestButton(self, surface, gazePos):
		"""Draws the guestButton as well as a growing border that indicates if it has been selected"""
		spx, epx = 0, 0
		spy, epy = 0, 0
		col = (255,255,255)
		if self.guestLineX == 'FORWARD':					# Border going Forwards
			spx, epx = 710, 710+self.guestLineLength
		if self.guestLineX == 'BACKWARDS':						
			spx, epx = 1210, 1210-self.guestLineLength		# Border going Backwards
		if self.guestLineX == None:
			if self.guestLineY == 'DOWN':					# Border going Down
				spx, epx = 1210, 1210
			if self.guestLineY == 'UP':						# Border going up
				spx, epx = 710, 710
		if self.guestLineY == 'DOWN':
			spy, epy = 420, 420+self.guestLineLength
		if self.guestLineY == 'UP':
			spy, epy = 500, 500-self.guestLineLength
		if self.guestLineY == None:
			if self.guestLineX == 'FORWARD':
				spy, epy = 420, 420
			if self.guestLineX == 'BACKWARDS':
				spy, epy = 500, 500
		if self.guestLineX == 'FORWARD' and 710+self.guestLineLength > 1210:
			self.guestLineY = 'DOWN'
			self.guestLineX = None
			self.guestLineLength = 0
			epx, epy = 1210,420
		if self.guestLineY == 'DOWN' and self.guestLineX == None and 420+self.guestLineLength > 500:
			self.guestLineY = None
			self.guestLineX = 'BACKWARDS'
			self.guestLineLength = 0
			epx, epy = 1210,500
		if self.guestLineX == 'BACKWARDS' and self.guestLineY == None and 1210-self.guestLineLength < 710:
			self.guestLineX = None
			self.guestLineY = 'UP'
			self.guestLineLength = 0
			epx, epy = 710, 500
		if self.guestLineY == 'UP' and self.guestLineX == None and 500-self.guestLineLength < 420:
			epx, epy = 710, 420
			self.animate = True
			self.guest = True
		draw.line(surface, col, (spx,spy), (epx, epy), 5)
		if self.getActivity(surface, gazePos) == "Guest":
			self.guestLineLength += 20
		else:
			if self.guestLineLength > 0:
				surface.blit(self.guestButtonCover, (705,415))
				self.guestLineLength = 0
				self.guestLineY = None
				self.guestLineX = 'FORWARD'

	def goToHome_animation(self, surface):
		"""Displays the animation to transition between the start screen and home screen"""
		if self.animate and self.angle != 360:
			draw.rect(surface, (6,16,26), (0,10*self.animationCounter,self.resX, 10))
			draw.rect(surface, (6,16,26), (0,self.resY-10*self.animationCounter,self.resX, 10))
			if self.animationPicCounter > 0:
				draw.rect(surface, (6,16,26), (800,40+10*self.animationPicCounter, 283, 220))
			if self.animationPicCounter != 40:
				surface.blit(self.logo, (800,50+10*self.animationPicCounter))
			if self.animationCounter < 54:
				self.animationCounter += 1
			if self.animationCounter >= 36:
				if self.animationPicCounter < 40:
					self.animationPicCounter += 1

			# rotates the project logo
			if self.animationPicCounter == 40:
				self.angle += 10
				if self.angle >= 360:
					self.fullrotations += 1
					self.angle = 0
					if self.fullrotations == 2:
						self.angle = 360
					self.animationCounter = 0
				self.size += 5
				rot_image = transform.rotate(self.logo, self.angle)
				rot_im_rect = rot_image.get_rect()
				rot_im_rect[2] -= 1600
				rot_im_rect[3] -= 900
				rot_im_rect.center = self.logo_rect.center
				surface.fill((6,16,26))
				surface.blit(rot_image, rot_im_rect)

		if self.angle == 360:
			surface.blit(homeScreen.convert(), (0,0))
			# cuts the screen and seperates into two
			draw.rect(surface, (6,16,26), (0,0,945-10*self.animationCounter,1080))
			surface.blit(self.logoLeft, (800-10*self.animationCounter, 450))
			draw.rect(surface, (6,16,26), (945+10*self.animationCounter,0,1000,1080))
			surface.blit(self.logoRight, (945+10*self.animationCounter, 450))

			if self.animationCounter < 101:
				self.animationCounter += 1
			if self.animationCounter == 101:
				return False

	def resetVars(self):
		"""Resets all of the variables of the start Screen"""
		self.login_dwell_delay = 10								#setting value to 0 will mean that program will not blit log in and sign up prompts
		self.signup_dwell_delay = 10
		self.calibPanel_dwell_delay = 6
		self.textFieldsCover = 0

		self.logIn_alreadyChecked = False
		self.signUp_alreadyChecked = False

		self.guestLineLength = 0
		self.guestLineY = None
		self.guestLineX = 'FORWARD'

		self.animate = False
		self.animationCounter = 0
		self.animationPicCounter = 0

		self.angle = 0
		self.size = 0
		self.fullrotations = 0

class HomeScreen(IntroScreen):
	"""Runs the main screen where the user can write notes, their thoughts and control all of the applications in the program"""
	def __init__(self, surface, screen_size):
		self.startTime = datetime.datetime.now()
		self.goToHome = False
		self.resX, self.resY = screen_size[0], screen_size[1]

		self.coverCreated = False
		self.CPcover = 0

		# the bottom tiles (Control Panel) from where the user controls the transition from the home screen to the start screen
		self.controlPanel = {
				'tracker_state'	:	{'blit_pos'	:	(15, 945),		'surf'	:	Surface((218, 120), SRCALPHA),	'cover'	:	None,	'copied'	:	False,	'dwell_delay'	:	104,	'colour'	:	(121,255,187),	'img'	:	trackerStateDisconnected.convert_alpha(),	'img_pos'	:	(25,956),	'img2'	:	trackerStateConnected.convert_alpha(),	'img_pos2'	:	(25,956)},
				'usage'			:	{'blit_pos'	:	(248, 945),		'surf'	:	Surface((218, 120), SRCALPHA),	'cover'	:	None,	'copied'	:	False,	'dwell_delay'	:	104,	'colour'	:	(123,83,146),	'img'	:	usage.convert_alpha(),						'img_pos'	:	(260,956)},
				'calibration'	:	{'blit_pos'	:	(481, 945),		'surf'	:	Surface((958, 120), SRCALPHA),	'cover'	:	None,	'copied'	:	False,	'dwell_delay'	:	104,	'colour'	:	(255,255,255)},
				'log_out'		:	{'blit_pos'	:	(1454, 945),	'surf'	:	Surface((218, 120), SRCALPHA),	'cover'	:	None,	'copied'	:	False,	'dwell_delay'	:	104,	'colour'	:	(49,255,255),	'img'	:	logout.convert_alpha(),						'img_pos'	:	(1465,956)},
				'shutdown'		:	{'blit_pos'	:	(1687, 945),	'surf'	:	Surface((218, 120), SRCALPHA),	'cover'	:	None,	'copied'	:	False,	'dwell_delay'	:	104,	'colour'	:	(186,31,74),	'img'	:	shutdown.convert_alpha(),					'img_pos'	:	(1698,956)},
		}

		self.homeButton = {'home' :	{'blit_pos'	:	(1687, 945),	'surf'	:	Surface((218, 120), SRCALPHA),	'cover'	:	None,	'copied'	:	False,	'dwell_delay'	:	104,	'colour'	:	(186,31,74),	'img'	:	home.convert_alpha(),						'img_pos'	:	(1698, 956)}}
		
		self.usage = 0

		self.dwell_delay_reset = False

		self.nameDrawn = False
		self.dateCoverCopied = False
		self.dateCover = 0

		self.tiles = {
				#-----COMMUNICATION TILES------
				'MESSAGES'		:	{											'rect'	:	Rect(15,195,612,225),	'colour'	:	(213,84,60),	'img'	:	messagesIcon.convert_alpha(),	'img_pos'	:	(25,215), 'drawn'	:	False,	'lineLength'	:	0,	'directX'	:	'FORWARDS',	'directY'	:	None,	'activate'	:	False},		
				'FREE-TYPE'		:	{'app'	:	FreeType(),						'rect'	:	Rect(15,438,297,463),	'colour'	:	(44,168,112),	'img'	:	freeTypeIcon.convert_alpha(),	'img_pos'	:	(25,591), 'drawn'	:	False,	'lineLength'	:	0,	'directX'	:	'FORWARDS',	'directY'	:	None,	'activate'	:	False, 	'reset'	:	False,	'alreadyReset'	:	False},		
				'MAIL'			:	{											'rect'	:	Rect(330,438,297,463),	'colour'	:	(55,137,220),	'img'	:	mailIcon.convert_alpha(),		'img_pos'	:	(341,586), 'drawn'	:	False,	'lineLength'	:	0,	'directX'	:	'FORWARDS',	'directY'	:	None,	'activate'	:	False},	
				#-----ENTERTAINMENT TILES------
				'TIC-TAC-TOE'	:	{'game'	:	tictactoe(surface),				'rect'	:	Rect(1294,195,249,172),	'colour'	:	(251,217,56),	'img'	:	ticTacToeIcon.convert_alpha(),	'img_pos'	:	(1305,205), 'drawn'	:	False,	'lineLength'	:	0,	'directX'	:	'FORWARDS',	'directY'	:	None,	'activate'	:	False, 	'reset'	:	False,	'alreadyReset'	:	False},
				'CHESS'			:	{'game'	:	chessGame(),					'rect'	:	Rect(1562,195,342,316),	'colour'	:	(162,35,170),	'img'	:	chessIcon.convert_alpha(),		'img_pos'	:	(1573,226), 'drawn'	:	False,	'lineLength'	:	0,	'directX'	:	'FORWARDS',	'directY'	:	None,	'activate'	:	False,	'reset'	:	False,	'alreadyReset'	:	False},
				'CONNECT 4'		:	{'game'	:	connect4(surface),				'rect'	:	Rect(1295,385,249,336),	'colour'	:	(178,32,69),	'img'	:	connect4Icon.convert_alpha(),	'img_pos'	:	(1306,437), 'drawn'	:	False,	'lineLength'	:	0,	'directX'	:	'FORWARDS',	'directY'	:	None,	'activate'	:	False,	'reset'	:	False,	'alreadyReset'	:	False},
				'CATCH ME'		:	{'game'	:	Game2(surface, screen_size),	'rect'	:	Rect(1563,529,342,192),	'colour'	:	(70,236,184),	'img'	:	catchMeIcon.convert_alpha(),	'img_pos'	:	(1574,546), 'drawn'	:	False,	'lineLength'	:	0,	'directX'	:	'FORWARDS',	'directY'	:	None,	'activate'	:	False,	'reset'	:	False,	'alreadyReset'	:	False},
				'PONG'			:	{'game'	:	Game(surface, screen_size, 1),	'rect'	:	Rect(1295,739,610,162),	'colour'	:	(58,43,174),	'img'	:	pongIcon.convert_alpha(),		'img_pos'	:	(1305,755), 'drawn'	:	False,	'lineLength'	:	0,	'directX'	:	'FORWARDS',	'directY'	:	None,	'activate'	:	False,	'reset'	:	False,	'alreadyReset'	:	False},
				'ON-MIND'		:	{											'rect'	:	Rect(18,17,1106,87),	'colour'	:	(159,171,177),															'drawn'	:	False,	'lineLength'	:	0,	'directX'	:	'FORWARDS',	'directY'	:	None,	'activate'	:	False,	'text'	:	'',	'textInit'	:	False},
				'NOTES'			:	{											'rect'	:	Rect(669,193,583,375),	'colour'	:	(0,0,0),		'img'	:	notesBg,		'img_pos'	:	(669,193), 	'drawn'	:	False,	'lineLength'	:	0,	'directX'	:	'FORWARDS',	'directY'	:	None,	'activate'	:	False,	'text'	:	['', '', '', '', '', '', ''],	'textInit'	:	False,	'height'	:	[206, 252, 298, 348, 396, 446, 492]}

		}

		self.currentApp = 'HOME'
		self.updatedNotes = ''

	def getCovers(self, surface):
		"""Gets all of the control panel covers to ensure an alpha value on them even when they are reblitted"""
		if self.dateCoverCopied == False:
			self.dateCover = surface.subsurface(Rect(1132, 13, 220, 64)).copy()
			self.dateCoverCopied = True
		for tile in self.controlPanel:
			if self.controlPanel[tile]['copied'] == False:
				if self.coverCreated == False:
					self.CPcover = Surface((1920,150))
					self.CPcover.blit(homeScreenCover, (0,0))
					self.coverCreated = True
				bx, by = self.controlPanel[tile]['blit_pos']
				sx, sy = self.controlPanel[tile]['surf'].get_size()
				self.controlPanel[tile]['cover'] = self.CPcover.subsurface(Rect(bx,0,sx,sy)).copy() 
				self.controlPanel[tile]['copied'] = True

	def ControlPanel(self, surface, gazePos, guest, fullname, tracker_state):
		"""The logic that the control panel follows when being drawed at the bottom of the screen"""
		if self.nameDrawn == False:
			self.writeFullname(surface, guest, fullname)
			self.nameDrawn = True
		for tile in self.controlPanel:
			sx, sy = self.controlPanel[tile]['surf'].get_size()
			draw.rect(self.controlPanel[tile]['surf'], (self.controlPanel[tile]['colour'][0], self.controlPanel[tile]['colour'][1], self.controlPanel[tile]['colour'][2], self.controlPanel[tile]['dwell_delay']), (0,0,sx,sy))
			if tile != 'calibration' and tile != 'tracker_state':
				if tile == 'shutdown':
					if self.getCurrentApp(surface, gazePos) != 'HOME':
						self.controlPanel[tile]['surf'].blit(self.homeButton['home']['img'], (11,11))
					else:
						self.controlPanel[tile]['surf'].blit(self.controlPanel[tile]['img'], (11,11))
				else:
					self.controlPanel[tile]['surf'].blit(self.controlPanel[tile]['img'], (11,11))
			if tile == 'tracker_state':
				if tracker_state != 0:
					self.controlPanel[tile]['surf'].blit(self.controlPanel[tile]['img'], (11,11))
				elif tracker_state == 0:
					self.controlPanel[tile]['surf'].blit(self.controlPanel[tile]['img2'], (11,11))
			surface.blit(self.controlPanel[tile]['cover'], self.controlPanel[tile]['blit_pos'])
			surface.blit(self.controlPanel[tile]['surf'], self.controlPanel[tile]['blit_pos'])
			if tile == 'calibration':
				makeText(surface, "CALIBRATE", 70, (6,16,54), None, 483+getSpacing("CALIBRATE", sx, 70, 'fonts/HelveNueBold/HelveticaNeueBold.ttf'), 960, 'fonts/HelveNueBold/HelveticaNeueBold.ttf')

	def drawControlPanel(self, surface, gazePos, tracker_state, state, guest, fullname = ''):
		"""Draws the control panel at the bottom of the screen including the amount of time spent using the program"""
		for tile in self.controlPanel:
			self.controlPanel[tile]['dwell_delay'] = self.dwellNormalize(self.controlPanel[tile]['dwell_delay'], maximum = 220, minimum = 101)
			if self.controlPanel[tile]['dwell_delay'] != 101 and self.controlPanel[tile]['dwell_delay'] != 220 and state != 'ON': #and tile != 'usage':
				self.ControlPanel(surface, gazePos, guest, fullname, tracker_state)
			if state != 'ON':
				if self.getActivity(surface, gazePos) == tile:
					self.controlPanel[tile]['dwell_delay'] += 3
				elif self.controlPanel[tile]['dwell_delay'] != 101:
					self.controlPanel[tile]['dwell_delay'] -= 3
		if state == 'OFF':
			tile = 'usage'
			if tile == 'usage':
				sx, sy = self.controlPanel[tile]['surf'].get_size()
				draw.rect(self.controlPanel[tile]['surf'], (self.controlPanel[tile]['colour'][0], self.controlPanel[tile]['colour'][1], self.controlPanel[tile]['colour'][2], self.controlPanel[tile]['dwell_delay']), (0,0,sx,sy))
				self.controlPanel[tile]['surf'].blit(self.controlPanel[tile]['img'], (11,11))
				surface.blit(self.controlPanel[tile]['cover'], self.controlPanel[tile]['blit_pos'])
				surface.blit(self.controlPanel[tile]['surf'], self.controlPanel[tile]['blit_pos'])
				if len(str(self.usage)) == 1:
					makeText(surface, str(self.usage), 60, (255,255,255), None, 270, 983)
					makeText(surface, 'MIN', 20, (255,255,255), None, 310, 1023, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf')
				else:
					makeText(surface, str(self.usage), 60, (255,255,255), None, 252, 983)
					makeText(surface, 'MIN', 20, (255,255,255), None, 322, 1023, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf')

	def getUsage(self):
		"""Returns the difference in time from when the user entered the home screen and the current time"""
		self.currentTime = datetime.datetime.now()
		self.usage = round((self.currentTime-self.startTime)/datetime.timedelta(minutes=1))
		return self.usage

	def getActivity(self, surface, gazePos):
		"""Gets the activity of the control panel tiles"""
		for tile in self.controlPanel:
			bx, by = self.controlPanel[tile]['blit_pos']
			sx, sy = self.controlPanel[tile]['surf'].get_size()
			if Rect(bx,by,sx,sy).collidepoint(gazePos):
				return tile

	def writeFullname(self, surface, guest, fullname):
		"""Writes the name of the user if they are logged in or else just writes Guest User"""
		first, last = '',''
		if guest and len(fullname) == 0:
			first, last = "Guest", "User"
		else:
			name = fullname.title().split()
			if len(name) == 2:
				first, last = name
			elif len(name) == 1:
				first, last = name[0], ''
		makeText(surface, first, 40, (255,255,255), None, getSpacing(first, 1758, 40, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf', 'right'), 20, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf')
		makeText(surface, last, 30, (255,255,255), None, getSpacing(last, 1758, 30, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf', 'right'), 60, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf')
		self.nameDrawn = True
	
	def writeDate(self, surface):
		tm = datetime.datetime.now().time()
		hr, mn, nightOrDay = tm.strftime("%I"), tm.strftime("%M"), tm.strftime("%p")
		ans = datetime.datetime.now()
		weekday, month, day = ans.strftime("%A"), ans.strftime("%B"), ans.strftime("%d")
		if len(day) == 2 and day[0] == '0':
			day = day[1]
		if len(hr) == 2 and hr[0] == '0':
			hr = hr[1]

		date = "%s, %s %s" %(weekday, month, day)
		tim = "%s:%s" %(hr, mn)

		surface.blit(self.dateCover, (1132,13))
		makeText(surface, date, 24, (255,255,255), None, 1132, 13, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf')
		makeText(surface, tim, 38, (255,255,255), None, 1132, 38, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf')
		if len(hr) == 2:
			makeText(surface, nightOrDay, 24, (255,255,255), None, 1232, 50, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf')
		else:
			makeText(surface, nightOrDay, 24, (255,255,255), None, 1210, 50, 'fonts/HelveNueRegular/HelveticaNeueRegular.ttf')

	def activateKeyboard(self, state, old_state):
		if state != old_state:
			if state == 'ON':
				return 'DRAW KEYBOARD'
			elif state == 'OFF':
				pass

	def mainTiles(self, surface, gazePos, text): #text = "What's on your mind?"):
		for tile in self.tiles:
			bounds = (self.tiles[tile]['rect'][0]+1, self.tiles[tile]['rect'][1]+1, self.tiles[tile]['rect'][2]-3, self.tiles[tile]['rect'][3]-3)
			if self.tiles[tile]['drawn'] == False:
				if tile != 'NOTES':
					draw.rect(surface, self.tiles[tile]['colour'], self.tiles[tile]['rect'])
					if tile != 'ON-MIND':
						surface.blit(self.tiles[tile]['img'], self.tiles[tile]['img_pos'])
					else:

						makeText(surface, text, 70, (96,98,110), None, 37, 16)	# this is where the type bar on the home screen is drawn
				self.tiles[tile]['drawn'] = True
			self.tiles[tile]['lineLength'], self.tiles[tile]['directX'], self.tiles[tile]['directY'] = self.linePath(surface, bounds, gazePos, tile, self.tiles[tile]['lineLength'], self.tiles[tile]['directX'], self.tiles[tile]['directY'])

	def drawTypeBar(self, surface, text = "What's on your mind?"):
		draw.rect(surface, self.tiles['ON-MIND']['colour'], self.tiles['ON-MIND']['rect'])
		makeText(surface, text, 70, (96,98,110), None, 37, 16)	# this is where the type bar on the home screen is drawn

	def writeNotes(self, surface, text = "Quickly jot down a reminder!", pos = 0):
		if self.updatedNotes != text:
			self.updatedNotes = text
			surface.blit(self.tiles['NOTES']['img'], self.tiles['NOTES']['img_pos'])

			for i in range(len(self.tiles['NOTES']['height'])):
				if i != pos:
					makeText(surface, self.tiles['NOTES']['text'][i], 27, (255,255,255), None, 702, self.tiles['NOTES']['height'][i])
			makeText(surface, text, 27, (255,255,255), None, 702, self.tiles['NOTES']['height'][pos])

	def getMainTileActivity(self, surface, gazePos):
		for tile in self.tiles:
			if self.tiles[tile]['rect'].collidepoint(gazePos):
				return tile

	def getCurrentApp(self, surface, gazePos):
		for tile in self.tiles:
			if self.tiles[tile]['activate']:
				self.currentApp = tile
				return self.currentApp
		self.currentApp = 'HOME'
		return self.currentApp

	def linePath(self, surface, rect, gazePos, tile, lineLength, directX, directY, thickness = 3):
		spx, epx = rect[0], rect[0]
		spy, epy = rect[1], rect[1]
		col = (255,255,255)

		if directX == 'FORWARDS':
			spx, epx = rect[0], rect[0]+lineLength
		if directX == 'BACKWARDS':
			spx, epx = rect[0]+rect[2], rect[0]+rect[2]-lineLength
		if directX == None:
			if directY == 'DOWN':
				spx, epx = rect[0]+rect[2], rect[0]+rect[2]
			if directY == 'UP':
				spx, epx = rect[0], rect[0]

		if directY == 'DOWN':
			spy, epy = rect[1], rect[1]+lineLength
		if directY == 'UP':
			spy, epy = rect[1]+rect[3], rect[1]+rect[3]-lineLength
		if directY == None:
			if directX == 'FORWARDS':
				spy, epy = rect[1], rect[1]
			if directX == 'BACKWARDS':
				spy, epy = rect[1]+rect[3], rect[1]+rect[3]

		if directX == 'FORWARDS' and rect[0]+lineLength > rect[0]+rect[2]:
			directY = 'DOWN'
			directX = None
			lineLength = 0
			epx, epy = rect[0]+rect[2],rect[1]
		if directY == 'DOWN' and directX == None and rect[1]+lineLength > rect[1]+rect[3]:
			directY = None
			directX = 'BACKWARDS'
			lineLength = 0
			epx, epy = rect[0]+rect[2],rect[1]+rect[3]
		if directX == 'BACKWARDS' and directY == None and rect[0]+rect[2]-lineLength < rect[0]:
			directX = None
			directY = 'UP'
			lineLength = 0
			epx, epy = rect[0], rect[1]+rect[3]
		if directY == 'UP' and directX == None and rect[1]+rect[3]-lineLength < rect[1]:
			epx, epy = rect[0], rect[1]
			self.tiles[tile]['activate'] = True
		draw.line(surface, col, (spx,spy), (epx, epy), thickness)

		if self.getMainTileActivity(surface, gazePos) == tile:
			lineLength += 20
		else:
			if lineLength > 0:
				draw.rect(surface, self.tiles[tile]['colour'], Rect(self.tiles[tile]['rect'][0]+1, self.tiles[tile]['rect'][1]+1, self.tiles[tile]['rect'][2]-2, self.tiles[tile]['rect'][3]-2), 3)
				lineLength = 0
				directY = None
				directX = 'FORWARDS'

		return [lineLength, directX, directY]

	def getTilesState(self):
		for tile in self.tiles:
			if tile != 'MESSAGES' and tile != 'MAIL':
				if self.tiles[tile]['activate']:
					return tile
		return False

	def runTiles(self, surface, gazePos, old_gazePos):
		if self.tiles['CHESS']['activate']:
			if self.dwell_delay_reset == False:
				for tile in self.controlPanel:
					self.controlPanel[tile]['dwell_delay'] = 104
				self.dwell_delay_reset = True
			if self.tiles['CHESS']['reset']:
				self.tiles['CHESS']['game'] = chessGame()
				self.tiles['CHESS']['reset'] = False
			self.tiles['CHESS']['game'].performAction(gazePos, old_gazePos)
			self.tiles['CHESS']['game'].main(surface, self.tiles['CHESS']['game'].mb, self.tiles['CHESS']['game'].cursor)	#self, screen, mb, cursor

		if self.tiles['CONNECT 4']['activate']:
			if self.dwell_delay_reset == False:
				for tile in self.controlPanel:
					self.controlPanel[tile]['dwell_delay'] = 104
				self.dwell_delay_reset = True

			if self.tiles['CONNECT 4']['reset']:
				self.tiles['CONNECT 4']['game'] = connect4(surface)
				self.tiles['CONNECT 4']['reset'] = False
			self.tiles['CONNECT 4']['game'].performAction(gazePos, old_gazePos)
			if self.tiles['CONNECT 4']['game'].backgroundValue:
				for tile in self.controlPanel:
					self.controlPanel[tile]['dwell_delay'] = 104
			self.tiles['CONNECT 4']['game'].main(self.tiles['CONNECT 4']['game'].cursor, self.tiles['CONNECT 4']['game'].mb)

		if self.tiles['TIC-TAC-TOE']['activate']:
			if self.dwell_delay_reset == False:
				for tile in self.controlPanel:
					self.controlPanel[tile]['dwell_delay'] = 104
				self.dwell_delay_reset = True

			if self.tiles['TIC-TAC-TOE']['reset']:
				self.tiles['TIC-TAC-TOE']['game'] = tictactoe(surface)

				self.tiles['TIC-TAC-TOE']['reset'] = False
			self.tiles['TIC-TAC-TOE']['game'].performAction(gazePos, old_gazePos)
			if self.tiles['TIC-TAC-TOE']['game'].blitBackground:
				for tile in self.controlPanel:
					self.controlPanel[tile]['dwell_delay'] = 104
			self.tiles['TIC-TAC-TOE']['game'].main(self.tiles['TIC-TAC-TOE']['game'].mb, self.tiles['TIC-TAC-TOE']['game'].cursor)	#self, screen, mb, cursor

		if self.tiles['PONG']['activate']:
			if self.dwell_delay_reset == False:
				for tile in self.controlPanel:
					self.controlPanel[tile]['dwell_delay'] = 104
				self.dwell_delay_reset = True

			a = self.tiles['PONG']['game'].run(surface, gazePos, old_gazePos)
			if a == 'GAMEOVER':
				self.tiles['PONG']['activate'] = False
				surface.blit(homeScreen, (0,0))

			if self.tiles['PONG']['reset']:
				self.tiles['PONG']['game'] = Game(surface, (1920,1080), 1)
				self.tiles['PONG']['reset'] = False

		if self.tiles['CATCH ME']['activate']:
			if self.dwell_delay_reset == False:
				for tile in self.controlPanel:
					self.controlPanel[tile]['dwell_delay'] = 104
				self.dwell_delay_reset = True

			a = self.tiles['CATCH ME']['game'].run(surface, gazePos, old_gazePos)
			if a == 'GAMEOVER':
				self.tiles['CATCH ME']['activate'] = False
				surface.blit(homeScreen, (0,0))

			if self.tiles['CATCH ME']['reset']:
				self.tiles['CATCH ME']['game'] = Game2(surface, (1920,1080))
				self.tiles['CATCH ME']['reset'] = False

		if self.tiles['FREE-TYPE']['activate']:
			if self.dwell_delay_reset == False:
				for tile in self.controlPanel:
					self.controlPanel[tile]['dwell_delay'] = 104
				self.dwell_delay_reset = True
			if self.tiles['FREE-TYPE']['reset']:
				self.tiles['FREE-TYPE']['app'].bgDrawn = False			#this is to reset the variables so that the game can be started again with the backgrounds blitted
				self.tiles['FREE-TYPE']['app'].typeBarDrawn = False
				self.tiles['FREE-TYPE']['reset'] = False

			self.tiles['FREE-TYPE']['app'].drawSetting(surface) 
			self.tiles['FREE-TYPE']['app'].key['current'] = self.tiles['FREE-TYPE']['app'].getKey(gazePos)
			self.tiles['FREE-TYPE']['app'].drawSelectedKey(surface, gazePos) 
			if self.tiles['FREE-TYPE']['app'].key['current'] != None:
				self.tiles['FREE-TYPE']['app'].key['previous'] = self.tiles['FREE-TYPE']['app'].key['current'] 
			
	def performAction(self, gazePos, runTile = False):
		activity = self.getActivity(surface, gazePos)
		if activity == 'log_out':
			if self.controlPanel['log_out']['dwell_delay'] >= 220:
				self.goToHome = False
				return 'LOG OUT'
		elif activity == 'shutdown':
			if runTile == False:
				if self.controlPanel['shutdown']['dwell_delay'] >= 220:
					self.goToHome = False
					return 'SHUTDOWN'
			elif runTile:
				if self.controlPanel['shutdown']['dwell_delay'] >= 110:
					self.controlPanel['shutdown']['dwell_delay'] = 101
					return 'HOME'
		elif activity == 'calibration':
			if self.controlPanel['calibration']['dwell_delay'] >= 220:
				return 'CALIBRATION'




