import qi
import sys
import json
import math
import time
import numpy
import base64
import motion
import random
import argparse
import requests
from random import randint
from tic_tac_toe import TicTacToe
from basic_awareness import HumanTrackedEventWatcher
from PIL import Image, ImageDraw, ImageFont


####################################
# DEVELOPER        : VIKRAM SINGH  #
# TECHNOLOGY STACK : PYTHON        #
####################################


# ==============================================================================
#                      --- CAMERA INFORMATION ---

# AL_resolution
AL_kQQQQVGA       = 8 # Image of 40*30px
AL_kQQQVGA        = 7 # Image of 80*60px
AL_kQQVGA         = 0 # Image of 160*120px
AL_kQVGA          = 1 # Image of 320*240px
AL_kVGA           = 2 # Image of 640*480px
AL_k4VGA          = 3 # Image of 1280*960px
AL_k16VGA         = 4 # Image of 2560*1920px

# Camera IDs
AL_kTopCamera     = 0
AL_kBottomCamera  = 1
AL_kDepthCamera   = 2

# Need to add All color space variables
AL_kBGRColorSpace = 13

# ==============================================================================

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# =============================== CONFIG =======================================

ONEUNITDIST = 0.5
MOVEMENT_WAIT = 1  # In seconds
TIME_CALIBERATED = 4660  # For calculating use program robot_velocity_caliberatoion.py

NODE_IP = "10.9.43.90"  # IP Address of the node in which you are running this program
DL_SERVER_URL = "http://10.9.42.46:5000/getPredictions"

TOPIC_NAME = "tic_tac_toe.top" # Name of topic file situated at robots dir => `/home/nao/chat/`

# ==============================================================================


# =============== ORIENTATION BASED ON INITIAL BOT POSITION ====================
PHI = 0 # AMOUNT TO MOVE TO FACE TOWARDS EAST (0`)
#               0
#   math.pi/2       -math.pi/2
#            math.pi
PENDING_PHI = 0
# ==============================================================================


class Bcolors():
	# COLOUR SCHEME FOR PRINTING
	HEADER    = '\033[95m'
	OKBLUE    = '\033[94m'
	OKGREEN   = '\033[92m'
	WARNING   = '\033[93m'
	FAIL      = '\033[91m'
	ENDC      = '\033[0m'
	BOLD      = '\033[1m'
	UNDERLINE = '\033[4m'


class TicTacToeGame(object):

	def __init__(self, app, human_tracked_event_watcher, tic_tac_toe):
		super(TicTacToeGame, self).__init__()

		try:
			app.start()
		except RuntimeError:
			print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " +
				   str(args.port) + ".\n")

			sys.exit(1)

		session = app.session
		self.subscribers_list = []

		# SUBSCRIBING SERVICES
		self.memory_service           = session.service("ALMemory")
		self.motion_service           = session.service("ALMotion")
		self.dialog_service           = session.service("ALDialog")
		self.posture_service          = session.service("ALRobotPosture")
		self.speaking_movement        = session.service("ALSpeakingMovement")
		self.video_service            = session.service("ALVideoDevice")
		self.tts                      = session.service("ALTextToSpeech")
		self.animation_player_service = session.service("ALAnimationPlayer")
		self.tablet_service           = session.service("ALTabletService")

		self.human_watcher            = human_tracked_event_watcher
		self.game                     = tic_tac_toe

		# INITIALISING CAMERA POINTERS
		self.imageNo2d = 1
		self.imageNo3d = 1

		# DETECTION CODES
		self.MULTIPLE_ENTRY_CODE        = -7
		self.WRONG_TYPE_CODE            = -5
		self.EMPTY_BOARD_CODE           = -3
		self.IDENTIFICATION_ERROR_CODE  = -1
		self.MISMATCH_ERROR_CODE        = 0
		self.SUCCESSFULL_DETECTION_CODE = 1
		self.NO_DETECTION_CODE          = 3

		# BOARD SPECS
		self.gameOn            = False
		self.gameBoard         = ['.'] * 9
		self.heuristicBoard    = ['-1'] * 9
		self.lastMemoizedBoard = [((-1, -1), "")] * 9
		self.boardFound        = False
		self.boardImgNo        = 0
		self.computerType      = '-'
		self.humanType         = '-'
		self.reGameCall        = False
		self.overLapBoard      = False
		self.affirmativeCall   = False
		self.negativeCall      = False
		self.tossAsked         = False
		self.boardIndexToText  = [
									"first row first column",
									"first row second column",
									"first row third column",
									"second row first column",
									"second row second column",
									"second row third column",
									"third row first column",
									"third row second column",
									"third row third column"
								]

	def _printLogs(self, log, pType):
		# PRINTING LOGS
		printObjects = ["NORMAL", "WARNING", "OKBLUE", "FAIL", "LINE"]

		if pType == "NORMAL":
			print str(log) + "\n"

		if pType == "WARNING":
			print Bcolors.WARNING + str(log) + Bcolors.ENDC + "\n"

		if pType == "OKBLUE":
			print Bcolors.OKBLUE + str(log) + Bcolors.ENDC + "\n"

		if pType == "FAIL":
			print Bcolors.BOLD + Bcolors.FAIL + str(log) + Bcolors.ENDC + "\n"

		if pType == "LINE":
			if log == "":
				print
			if log == "+":
				print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
			if log == "-":
				print "-------------------------------------------------------\n"
			if log == "=":
				print "=======================================================\n"

		if pType not in printObjects:
			# pType unknown, hence do normal print
			print str(log) + "\n"

		return


	def create_callbacks(self):
		self.connect_callback("affirmative_event",
							  self.affirmative_event)

		self.connect_callback("negative_event",
							  self.negative_event)

		self.connect_callback("game_toss_event",
							  self.game_toss_event)

		self.connect_callback("play_again_game_event",
							  self.play_again_game_event)

		return

	def connect_callback(self, event_name, callback_func):
		self._printLogs("Callback connection", "NORMAL")
		subscriber = self.memory_service.subscriber(event_name)
		subscriber.signal.connect(callback_func)
		self.subscribers_list.append(subscriber)

		return

	def play_again_game_event(self, value):
		if self.gameOn:
			self.reGameCall = True
			self._makePepperSpeak(
				"There is already a game on, do you still want to play a new game")
		else:
			self._makePepperSpeak("Alright then lets play a game")
			self.game_toss_event(True)

		return

	def game_toss_event(self, value):
		if self.gameOn:
			self._makePepperSpeak("Sorry a game is already on")
			return
		self._makePepperSpeak(
			"Hey I choose Heads, but don't worry I promise you this toss is completely random")
		self._makePepperSpeak(
			"And whosoever wins the toss will have a chance to play first and choose their type between cross and circle")


		# Stopping Awareness
		self.human_watcher.stop_basic_awareness()
		self._moveHead(0, 1)


		time.sleep(1)
		# Display gif
		toss = ["Heads", "Tails"]
		outcome = toss[randint(0, 1)]
		self._printLogs("TOSS : " + str(outcome), "WARNING")
		# Display toss
		self._showOnTablet("toss.mp4", video=True)
		time.sleep(5)
		if outcome == "Heads":
			# computer wins toss
			self._showOnTablet("heads.jpg", video=False)
			time.sleep(4)
			self._clearTablet()
			self._makePepperSpeak("Yess ! I won the toss")
			self.playTicTacToe(playerOne="COMPUTER", playerType="")
		else:
			self._showOnTablet("tails.jpg", video=False)
			time.sleep(4)
			self._clearTablet()
			self.tossAsked = True
			self._makePepperSpeak("Ohh No ! You won the toss, I lost")
			self._makePepperSpeak(
				"Say yes or no ! Do you want cross to play with")

		self.human_watcher.start_basic_awareness()

		return

	def affirmative_event(self, value):
		self.affirmativeCall = True
		if self.tossAsked:
			self.tossAsked = False
			self.playTicTacToe(playerOne="HUMAN", playerType="x")

		if self.reGameCall:
			self.reGameCall = False
			self._resetGame()
			self._makePepperSpeak("Alright then lets play a fresh game")
			self.game_toss_event(True)

		return

	def negative_event(self, value):
		self.negativeCall = True
		if self.tossAsked:
			self.tossAsked = False
			self.playTicTacToe(playerOne="HUMAN", playerType="o")

		return


	def _moveHand(self):

		JointNamesL = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"]
		JointNamesR = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]

		# ArmL/R
		# [   hand            { - : up, + : down }
		#     shoulder        { - : right side horizontal movement, + : left side horizontal movement }
		#     Palm rotation   { + : clockwise, - : anti-clockwise }
		#     Elbow movement  { + : right to left, - : left to right }
		# ]
		# these hand movements will only work if rotation are possible in those directions
		# ArmL1 = [-50,  30, 0, 0]
		# ArmL1 = [ x * motion.TO_RAD for x in ArmL1]

		ArmR1 = [0, 0, 50, 0]
		ArmR1 = [x * motion.TO_RAD for x in ArmR1]

		pFractionMaxSpeed = 0.1
		self.motion_service.angleInterpolationWithSpeed(
			JointNamesR, ArmR1, pFractionMaxSpeed)

		return

	def _clearTablet(self):
		# Hide the web view
		self.tablet_service.hideImage()

		return

	def _showOnTablet(self, imageName, video):
		# Display Image On Tablet
		base_url = "http://{}/pepper_hack/images/".format(NODE_IP)
		view_url = base_url + str(imageName)
		try:
			if video:
				self.tablet_service.playVideo(view_url)
			else:
				# self.tablet_service.showImageNoCache(view_url) # wont use this because we have toss images which are constant here
				self.tablet_service.showImage(view_url)

			self._printLogs("Displaying on tablet : " + view_url, "OKBLUE")
		except Exception, err:
			self._printLogs("Error Showing On Tablet : " + str(err), "FAIL")
			self._printLogs("+", "LINE")

		return

	def _moveHead(self, amntX, amntY):

		JointNamesH = ["HeadPitch", "HeadYaw"] # range ([-1,1],[-0.5,0.5]) // HeadPitch :{(-)up,(+)down} , HeadYaw :{(-)left,(+)right}
		pFractionMaxSpeed = 0.1
		HeadA = [float(amntY), float(amntX)]

		self.motion_service.angleInterpolationWithSpeed(
			JointNamesH, HeadA, pFractionMaxSpeed)

		return

	def _makePepperSpeak(self, userMsg):
		# MAKING PEPPER SPEAK
		# future = self.animation_player_service.run("animations/Stand/Gestures/Give_3", _async=True)
		sentence = "\RSPD=" + str(80) + "\ "  # Speed
		sentence += "\VCT=" + str(100) + "\ "  # Voice Shaping
		sentence += userMsg
		sentence += "\RST\ "
		self.tts.say(str(sentence))
		# future.value()

		return

	def _moveForward(self, distToMove):
		X = min(distToMove, ONEUNITDIST)
		Y = 0.0
		Theta = 0.0

		x = 0
		t0 = time.time()

		# Blocking call
		a = self.motion_service.moveTo(X, Y, Theta)

		t1 = time.time()
		t = t1 - t0
		t *= 1000

		units = float(t) * (1.0 / TIME_CALIBERATED)
		# TIME_CALIBERATED is an average time per m length. Need to caliberate according to the flooring.

		resDist = 0
		if units >= 0.2:
			resDist = units

		if not a:
			self._printLogs(
				"Obstacle found in btw, bot moved dist : " + str(resDist), "NORMAL")
		else:
			self._printLogs("Movement Complete : " +
							str(ONEUNITDIST), "NORMAL")

		# print "dist in m : ",units
		possible = True  # movement possible in direction
		if units < 0.2:
			possible = False
			units = resDist

		return [possible, units]

	def _moveLeft(self, distToMove):
		X = 0.0
		Y = min(distToMove, ONEUNITDIST)
		Theta = 0.0

		x = 0
		t0 = time.time()

		# Blocking call
		a = self.motion_service.moveTo(X, Y, Theta)

		t1 = time.time()
		t = t1 - t0
		t *= 1000

		units = float(t) * (1.0 / TIME_CALIBERATED)
		# TIME_CALIBERATED is an average time per m length. Need to caliberate according to the flooring.

		resDist = 0
		if units >= 0.2:
			resDist = units

		if not a:
			self._printLogs(
				"Obstacle found in btw, bot moved dist : " + str(resDist), "NORMAL")
		else:
			self._printLogs("Movement Complete : " +
							str(ONEUNITDIST), "NORMAL")

		# print "dist in m : ",units
		possible = True  # movement possible in direction
		if units < 0.2:
			possible = False
			units = resDist

		return [possible, units]

	def _moveRight(self, distToMove):
		X = 0.0
		Y = - min(distToMove, ONEUNITDIST)  # forward
		Theta = 0.0

		x = 0
		t0 = time.time()

		# Blocking call
		a = self.motion_service.moveTo(X, Y, Theta)

		t1 = time.time()
		t = t1 - t0
		t *= 1000

		units = float(t) * (1.0 / TIME_CALIBERATED)
		# TIME_CALIBERATED is an average time per m length. Need to caliberate according to the flooring.

		resDist = 0
		if units >= 0.2:
			resDist = units

		if not a:
			self._printLogs(
				"Obstacle found in btw, bot moved dist : " + str(resDist), "NORMAL")
		else:
			self._printLogs("Movement Complete : " +
							str(ONEUNITDIST), "NORMAL")

		# print "dist in m : ",units
		possible = True  # movement possible in direction
		if units < 0.2:
			possible = False
			units = resDist

		return [possible, units]

	def _moveBack(self, distToMove):
		X = - min(distToMove, ONEUNITDIST)  # forward
		Y = 0.0
		Theta = 0.0

		x = 0
		t0 = time.time()

		# Blocking call
		a = self.motion_service.moveTo(X, Y, Theta)

		t1 = time.time()
		t = t1 - t0
		t *= 1000

		units = float(t) * (1.0 / TIME_CALIBERATED)
		# TIME_CALIBERATED is an average time per m length. Need to caliberate according to the flooring.

		resDist = 0
		if units >= 0.2:
			resDist = units

		if not a:
			self._printLogs(
				"Obstacle found in btw, bot moved dist : " + str(resDist), "NORMAL")
		else:
			self._printLogs("Movement Complete : " +
							str(ONEUNITDIST), "NORMAL")

		# print "dist in m : ",units
		possible = True  # movement possible in direction
		if units < 0.2:
			possible = False
			units = resDist

		return [possible, units]

	def _turnTheta(self, theta):
		X = 0.0
		Y = 0.0
		Theta = theta
		# theta = math.radians(-45)
		# theta = -math.pi/2

		# Blocking call
		a = self.motion_service.moveTo(X, Y, Theta)

		if not a:
			self._printLogs("Obstacle found in between cannot move", "NORMAL")
		else:
			self._printLogs("Movement Complete", "NORMAL")

		return a


	def _insideCircle(self, p1, p2):
		# p1 being centre of the circle, check wether p2 is inside the circle for given radius
		radius = 10  # here taking 10px
		return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) <= radius

	def _sortOnX(self, elem):
		return elem[0]

	def _sortOnY(self, elem):
		return elem[1]

	def _resolveCellType(self, name):
		if name == "blank":
			return '.'
		if name == "cross":
			return 'x'
		if name == "circle":
			return 'o'

		return -1

	def _coinInterpretation(self, coinType):
		if coinType == 'x':
			return "cross"
		if coinType == 'o':
			return "circle"
		if coinType == '.':
			return "blank"

		return -1

	def _checkBoardInVicinity(self, cameraId):
		coinConfidence = 4  # min no of coins identified to tell possibility of a board present

		self._printLogs("Capturing Image For Board", "NORMAL")
		# Capture Image in RGB

		# WARNING : The same Name could be used only six time.
		strName = "capture2DImage_{}".format(random.randint(1, 10000000000))

		clientRGB = self.video_service.subscribeCamera(
			strName, cameraId, AL_kVGA, 11, 10)
		imageRGB = self.video_service.getImageRemote(clientRGB)

		imageWidth = imageRGB[0]
		imageHeight = imageRGB[1]
		array = imageRGB[6]
		image_string = str(bytearray(array))

		# Create a PIL Image from our pixel array.
		im = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)

		# CHECK IF BOARD IS IN THE IMAGE OR NOT
		metadata = self._sendImageToServer(
			imageWidth, imageHeight, image_string)
		res = metadata["isPresent"]

		boxX0 = 640  # max width
		boxX1 = 0
		boxY0 = 480  # max height
		boxY1 = 0

		if res:
			objects = metadata["objects"]
			coins = []
			self._printLogs("Number of Objects : " +
							str(len(objects)), "NORMAL")

			# Creating Bounding Box
			for coin in objects:
				label = coin["label"]
				x0 = float(coin["Left"])
				y0 = float(coin["Top"])
				x1 = float(coin["Right"])
				y1 = float(coin["Bottom"])
				boxX0 = min(boxX0, x0)
				boxY0 = min(boxY0, y0)
				boxX1 = max(boxX1, x1)
				boxY1 = max(boxY1, y1)

			if len(objects) >= coinConfidence:
				return (True, (boxX0, boxY0), (boxX1, boxY1))

		return (False, (boxX0, boxY0), (boxX1, boxY1))

	def _localiseRobot(self):
		print "Starting Localisation"

		''' Work in progress on this, Presently Hardcoding '''
		for i in range(3):
			res = False
			x = 45
			if i == 2:
				x = 25
			while not res:
				res = self._turnTheta(math.radians(x))
			time.sleep(2)

		self._turnTheta(math.radians(-25))
		time.sleep(2) # adding time between movements for smoothe transition
		self._moveLeft(0.4)
		time.sleep(2)
		self._moveRight(0.1)
		time.sleep(2)
		self._moveForward(0.5)
		time.sleep(2)
		self._moveForward(0.2)
		time.sleep(2)
		self._moveHead(0, 0.2)


		# # LOCALISATION ALGORITHM
		# cameraId = 0
		# for i in range(8):
		# 	self._turnTheta(math.radians(-45))
		# 	res = self._checkBoardInVicinity(cameraId)
		# 	success = res[0]
		# 	boxP1 = res[1]
		# 	boxP2 = res[2]
		# 	if success:
		# 		'''
		# 		-> Board Found
		# 		-> align with zero skewness first
		# 		-> do lateral movements align left right properly with help of
		# 		   box points and image dimensions
		# 		-> do forward / backward movement with respect to box ratio to image ratio
		# 		   If box covers 60% and more can stop movement
		# 		-> do head movements to align centre of board
		# 		'''

		return

	def _resetGame(self):
		self._printLogs("Reseting the game", "NORMAL")

		self.gameOn = False
		self.gameBoard = ['.'] * 9
		self.heuristicBoard = ['-1'] * 9
		self.lastMemoizedBoard = [((-1, -1), "")] * 9
		self.boardFound = False
		self.computerType = '-'
		self.humanType = '-'
		self.affirmativeCall = False
		self.negativeCall = False
		self.tossAsked = False
		self.overLapBoard = False

		self.human_watcher.start_basic_awareness()

		return

	def _printBoard(self, board):
		print "\n ", board[0], board[1], board[2]
		print " ", board[3], board[4], board[5]
		print " ", board[6], board[7], board[8]
		print "\n"

		return

	def _compareBoard(self, tempBoard):
		newCellCount = 0
		referenceCode = 0
		metadata = {}
		metadata["success"] = False
		metadata["pos"] = -1
		metadata["cellType"] = ''
		metadata["referenceCode"] = ''

		for i in range(9):
			if self.gameBoard[i] != tempBoard[i]:
				if self.gameBoard[i] == '.':
					metadata["pos"] = i
					metadata["cellType"] = tempBoard[i]

					newCellCount += 1
					if newCellCount >= 2:  # more than one new entries found
						metadata["success"] = False
						metadata["referenceCode"] = self.MULTIPLE_ENTRY_CODE
						return metadata
				else:
					metadata["success"] = False
					metadata["referenceCode"] = self.MISMATCH_ERROR_CODE
					return metadata

		if newCellCount == 1:
			metadata["success"] = True
			metadata["referenceCode"] = self.SUCCESSFULL_DETECTION_CODE
		else:
			metadata["success"] = False
			metadata["referenceCode"] = self.NO_DETECTION_CODE

		# return {success, pos, cellType, referenceCode=self.MISMATCH_ERROR_CODE}
		return metadata

	def _sendImageToServer(self, imageWidth, imageHeight, imageString):
		result = {}
		coordinates = {}
		metadata = {}
		isPresent = False

		try:
			self._printLogs("Sending Image To DL Server...", "NORMAL")

			url = DL_SERVER_URL
			payload = {
						"imageWidth"   : imageWidth,
						"imageHeight"  : imageHeight,
						"image_string" : base64.b64encode(imageString),
						"imageID"      : self.imageNo2d
						}
			headers = {'content-type': 'application/json'}

			res = requests.post(url, data=json.dumps(payload), headers=headers)
			result = res.json()
			self._printLogs("[*] Sent to  : " + str(url), "OKBLUE")
			self._printLogs(
				"[*] Response to finding board is : " + str(result), "OKBLUE")

		except Exception, err:
			self._printLogs(
				"Error Found on connecting to server : " + str(err), "FAIL")
			self._printLogs("+", "LINE")

		if result and result["boardFound"]:
			# print " *** Board Found *** \n"
			self.boardFound = True
			metadata["objects"] = result["objects"]
			isPresent = True
		else:
			# print "Board Not Found\n"
			self.boardFound = False

		metadata["isPresent"] = isPresent

		return metadata

	def _understandingBoard(self, coins):
		tempBoard = [-1] * 9
		rawBoard = [((-1, -1), "")] * 9
		cs = []  # centeroids

		for obj in coins:
			label = obj["label"]
			x0 = float(obj["Left"])
			y0 = float(obj["Top"])
			x1 = float(obj["Right"])
			y1 = float(obj["Bottom"])

			xc = float(x0 + x1) / 2
			yc = float(y0 + y1) / 2

			cs.append((xc, yc, label))

		''' LOGIC
		0 -> min (3 of all)x, min(1 of 3(x))y
		2 -> max (3 of all)x, min(1 of 3(x))y
		6 -> max (3 of all)y, min(1 of 3(y))x
		8 -> max (3 of all)y, max(1 of 3(y))x

		remove above coordinates

		3 -> min of x
		5 -> max of x

		1 -> min of y
		7 -> max of y

		remove all obove

		4 -> last left coordinate
		'''

		listLeft = []
		listLeft.extend(cs) # as disk cannot be copied with x=y as both will have same reference then
		onX = sorted(cs, key=self._sortOnX)
		onY = sorted(cs, key=self._sortOnY)

		temp = sorted([onX[i] for i in range(3)], key=self._sortOnY)[0]
		listLeft.remove(temp)
		rawBoard[0] = ((temp[0], temp[1]), temp[2])
		tempBoard[0] = self._resolveCellType(temp[2])

		temp = sorted([onX[i] for i in range(6, 9)], key=self._sortOnY)[0]
		listLeft.remove(temp)
		rawBoard[2] = ((temp[0], temp[1]), temp[2])
		tempBoard[2] = self._resolveCellType(temp[2])

		temp = sorted([onY[i] for i in range(6, 9)], key=self._sortOnX)[0]
		listLeft.remove(temp)
		rawBoard[6] = ((temp[0], temp[1]), temp[2])
		tempBoard[6] = self._resolveCellType(temp[2])

		temp = sorted([onY[i] for i in range(6, 9)], key=self._sortOnX)[2]
		listLeft.remove(temp)
		rawBoard[8] = ((temp[0], temp[1]), temp[2])
		tempBoard[8] = self._resolveCellType(temp[2])

		onX = sorted(listLeft, key=self._sortOnX)
		onY = sorted(listLeft, key=self._sortOnY)

		temp = onX[0]
		listLeft.remove(temp)
		rawBoard[3] = ((temp[0], temp[1]), temp[2])
		tempBoard[3] = self._resolveCellType(temp[2])

		temp = onX[-1]
		listLeft.remove(temp)
		rawBoard[5] = ((temp[0], temp[1]), temp[2])
		tempBoard[5] = self._resolveCellType(temp[2])

		temp = onY[0]
		listLeft.remove(temp)
		rawBoard[1] = ((temp[0], temp[1]), temp[2])
		tempBoard[1] = self._resolveCellType(temp[2])

		temp = onY[-1]
		listLeft.remove(temp)
		rawBoard[7] = ((temp[0], temp[1]), temp[2])
		tempBoard[7] = self._resolveCellType(temp[2])

		temp = listLeft[0]
		listLeft.remove(temp)  # list empty by now
		rawBoard[4] = ((temp[0], temp[1]), temp[2])
		tempBoard[4] = self._resolveCellType(temp[2])

		self.lastMemoizedBoard = []
		self.lastMemoizedBoard.extend(rawBoard)
		# self._printBoard(self.lastMemoizedBoard)
		self._printBoard(tempBoard)

		return tempBoard


	''' _heuristicUnderstadingFromPast():

		The thing I am trying to achieve here is incase of poor recognition as the points
		can only be evaluated with respect to each other, so if all 9 coins are not detected
		it will be unable to position the coin at right index at the board, hence I am using a memoized board
		to help situating the present coordinates and understanding their position from past.

		DISCLAIMER -> Will work once robot and board are stationary.
		Result => Finally it will help us detect the positions even if incomplete detections are made, i.e. all 9 detections not necessary

	'''
	def _heuristicUnderstadingFromPast(self, point, label):
		multipleMatch = 0
		for idx, cell in enumerate(self.lastMemoizedBoard):
			if self._insideCircle(cell[0], point):
				self.heuristicBoard[idx] = self._resolveCellType(label)
				multipleMatch += 1
				if multipleMatch >= 2:
					self._printLogs("Change Radius Measurement", "FAIL")

		return

	def _tryOverlappingWithHeuristic(self):
		tempBoard = ['-'] * 9
		for i in range(9):
			# as heuristicBoard is the latest updated board though with incomplete updation.
			if self.heuristicBoard[i] != '-1':
				# if self.heuristicBoard[i] == '.' and self.gameBoard[i] != '.':
				# 	# ASSUMPTION : donot update any earlier detected coin with a present detected blank
				# 	tempBoard[i] = self.gameBoard[i]
				# else:
				# 	tempBoard[i] = self.heuristicBoard[i]
				tempBoard[i] = self.heuristicBoard[i]
			else:
				tempBoard[i] = self.gameBoard[i]

		self._printLogs("Overlaped Board with heuristicBoard", "NORMAL")
		self._printBoard(tempBoard)

		data = self._compareBoard(tempBoard)
		success = data["success"]
		update = {}
		if success:
			if data["cellType"] != self.humanType:
				update["code"] = self.WRONG_TYPE_CODE
				return (False, update)
			else:
				update["code"] = self.SUCCESSFULL_DETECTION_CODE
				update["pos"] = data["pos"]
				self.gameBoard[data["pos"]] = self.humanType  # updating board
				return (True, update)
		else:
			update["code"] = data["referenceCode"]
			return (False, update)

		return

	def _checkBoardComposition(self, cameraId):
		self._printLogs("Capturing Image For Board", "NORMAL")
		# Capture Image in RGB

		# WARNING : The same Name could be used only six time.
		strName = "capture2DImage_{}".format(random.randint(1, 10000000000))

		clientRGB = self.video_service.subscribeCamera(
			strName, cameraId, AL_kVGA, 11, 10)
		imageRGB = self.video_service.getImageRemote(clientRGB)

		imageWidth   = imageRGB[0]
		imageHeight  = imageRGB[1]
		array        = imageRGB[6]
		image_string = str(bytearray(array))

		# Create a PIL Image from our pixel array.
		im = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)

		# CHECK IF BOARD IS IN THE IMAGE OR NOT
		metadata = self._sendImageToServer(
			imageWidth, imageHeight, image_string)
		res = metadata["isPresent"]
		update = {}

		if res:
			self.heuristicBoard = ['-1'] * 9 # reseting the board for new image
			objects = metadata["objects"]
			coins = []
			self._printLogs("Number of Objects : " +
							str(len(objects)), "NORMAL")

			# Creating Bounding Box
			for coin in objects:
				label = coin["label"]
				x0 = float(coin["Left"])
				y0 = float(coin["Top"])
				x1 = float(coin["Right"])
				y1 = float(coin["Bottom"])

				# Because my cross and circle training is weak,still minimum threshold of 50% is set at DL Servers end
				if float(coin["confidence"]) > 70.0 or label == "cross" or label == "circle":
					coins.append(coin)

				xc = float(x0 + x1) / 2
				yc = float(y0 + y1) / 2
				self._heuristicUnderstadingFromPast((xc, yc), label)

				draw = ImageDraw.Draw(im)
				draw.rectangle([(x0, y0), (x1, y1)], fill=None, outline="red")
				del draw

			# Save the image.
			base_url = "./images/captured/"
			image_name_2d = base_url + "img2d-" + str(self.imageNo2d) + ".png"
			im.save(image_name_2d, "PNG") # Stored in images folder in the pwd, if not present then create one
			self.boardImgNo = self.imageNo2d
			self.imageNo2d += 1

			try:
				self._printLogs("Number of Detections : " +
								str(len(coins)), "NORMAL")
				self._printLogs("-", "LINE")
				self._printLogs("Printing heuristicBoard", "NORMAL")
				self._printBoard(self.heuristicBoard)
				self._printLogs("-", "LINE")

				if len(coins) == 0:
					update["code"] = self.EMPTY_BOARD_CODE
					return (False, update)

				if len(coins) != len(objects):
					update["code"] = self.IDENTIFICATION_ERROR_CODE
					return (False, update)

				tempBoard = self._understandingBoard(coins)
				data = self._compareBoard(tempBoard)
				success = data["success"]

				if success:
					if data["cellType"] != self.humanType:
						update["code"] = self.WRONG_TYPE_CODE
						return (False, update)
					else:
						update["code"] = self.SUCCESSFULL_DETECTION_CODE
						update["pos"] = data["pos"]
						self.gameBoard[data["pos"]] = self.humanType # updating board
						return (True, update)
				else:
					update["code"] = data["referenceCode"]
					return (False, update)

			except Exception as err:
				self._printLogs(err, "FAIL")
				update["code"] = self.IDENTIFICATION_ERROR_CODE
				return (False, update)
		else:
			update["code"] = self.IDENTIFICATION_ERROR_CODE

		return (False, update)

	def _narrateBoard(self):
		self._printLogs("Narrating the board", "NORMAL")
		for i in range(9):
			sent = str(
				self.boardIndexToText[i] + " is " + self._coinInterpretation(self.gameBoard[i]))
			self._makePepperSpeak(sent)
			time.sleep(0.5)

		return

	def _playerMove(self):
		time.sleep(3) # time for human to make move and make move which robot spoke for itself

		failCount = 0
		cameraId = 0

		pos = -1

		while failCount <= 3:
			if not self.gameOn:
				# game has been closed
				return

			time.sleep(3)
			result = self._checkBoardComposition(cameraId)
			success = result[0]
			data = result[1]

			if not success and failCount == 3:
				# Try overlaping board and check if better results found.
				self.overLapBoard = True
				res = self._tryOverlappingWithHeuristic()
				success = res[0]
				data = res[1]

			if not self.gameOn:
				# game has been closed
				return

			if success:
				pos = data["pos"]
				break
			else:
				failCount += 1
				if data["code"] == self.MISMATCH_ERROR_CODE:
					self._makePepperSpeak(
						"I see mismatch there are chances that you are cheating")
				if data["code"] == self.WRONG_TYPE_CODE:
					self._makePepperSpeak(
						"I see you have drawn wrong coin choice you are " + self._coinInterpretation(self.humanType))
				if data["code"] == self.EMPTY_BOARD_CODE:
					self._makePepperSpeak("I see an empty board")
				if data["code"] == self.NO_DETECTION_CODE:
					self._makePepperSpeak("I see you haven't made your move")
				if data["code"] == self.MULTIPLE_ENTRY_CODE:
					self._makePepperSpeak(
						"I see there is some problem, you are a little bit confused there")

		cnt = 0
		while failCount > 3:
			if not self.gameOn:
				# game has been closed
				return

			if cnt == 0 or cnt % 5 == 0:
				self.affirmativeCall = False
				self._makePepperSpeak(
					"I find some misunderstanding between us, do you want me to narrate the board")
				time.sleep(3)

				if not self.gameOn:
					# game has been closed
					return

				if self.affirmativeCall:
					self._narrateBoard()
				else:
					self._makePepperSpeak(
						"Alright then, If you dont want to hear the board please play a legal move quickly, why to waste time, sorry to say but specially mine")
			cnt += 1

			time.sleep(2)
			result = self._checkBoardComposition(cameraId)
			success = result[0]
			data = result[1]

			if not success and cnt % 5 == 0:
				# Try overlaping board and check if better results found.
				self.overLapBoard = True
				res = self._tryOverlappingWithHeuristic()
				success = res[0]
				data = res[1]

			if not self.gameOn:
				# game has been closed
				return

			if success:
				pos = data["pos"]
				break
			else:
				failCount += 1
				if data["code"] == self.MISMATCH_ERROR_CODE:
					self._makePepperSpeak(
						"I see mismatch there are chances that you are cheating")
				if data["code"] == self.WRONG_TYPE_CODE:
					self._makePepperSpeak(
						"I see you have drawn wrong coin choice you are " + self._coinInterpretation(self.humanType))
				if data["code"] == self.EMPTY_BOARD_CODE:
					self._makePepperSpeak("I see an empty board")
				if data["code"] == self.NO_DETECTION_CODE:
					self._makePepperSpeak("I see you haven't made your move")
				if data["code"] == self.MULTIPLE_ENTRY_CODE:
					self._makePepperSpeak(
						"I see there is some problem, you are a little bit confused there")

		return pos

	def _startNewGame(self, playerOne, playerType):
		# if player one is computer then function will decide playerType otherwise give playerType
		dic = self.game.startNewGameWithRobot(playerOne, playerType)
		self.computerType = dic["computerType"]
		self.humanType = dic["humanType"]

		sent = str("Alright then, I am " + self._coinInterpretation(self.computerType) +
				   " and you are " + self._coinInterpretation(self.humanType))
		self._makePepperSpeak(sent)
		time.sleep(2)
		# returns -1 if human plays first otherwise prints the pos where computer plays
		return dic["computerMove"]

	def _gameLoop(self, playerOne, pos):
		if playerOne == "COMPUTER" and pos != -1:
			self.gameBoard[pos] = self.computerType
			sent = str("Please make " + self._coinInterpretation(self.computerType) +
					   " at " + self.boardIndexToText[pos] + "for me and then make your move")
			self._makePepperSpeak(sent)

		while self.gameOn:
			pos = self._playerMove()
			result = self.game.robotsNextMove(pos)

			if result[0]:
				# Game Over
				computerMove = result[1]
				verdict = result[2]
				if computerMove != -1:
					self.gameBoard[computerMove] = self.computerType
					sent = str("Please make " + self._coinInterpretation(
						self.computerType) + " at " + self.boardIndexToText[computerMove])
					self._makePepperSpeak(sent)
					time.sleep(1)

				if verdict == "CW":
					self._makePepperSpeak(
						"Yipeee ! I won ! Better Luck Next Time")

				if verdict == "DR":
					self._makePepperSpeak("Ohh ! Nevermind its a draw")

				if verdict == "HW":
					self._makePepperSpeak("You Win ! It can never happen")

				self._resetGame()

			else:
				computerMove = result[1]
				self.gameBoard[computerMove] = self.computerType
				sent = str("Please make " + self._coinInterpretation(self.computerType) +
						   " at " + self.boardIndexToText[computerMove] + "for me and then make your move")
				self._makePepperSpeak(sent)

		return


	def playTicTacToe(self, playerOne, playerType):
		# Stopping Awareness
		self.human_watcher.stop_basic_awareness()

		self._printLogs("Start Playing Game", "NORMAL")
		try:
			self.gameOn = True
			pos = self._startNewGame(playerOne, playerType)
			self._makePepperSpeak(
				"Give me some time till I relocate myself to correct position")
			self._localiseRobot()
			self._makePepperSpeak(
				"Okay, Im ready lets start playing within few seconds")
			time.sleep(3)  # cushion time
			self._gameLoop(playerOne, pos)

		except KeyboardInterrupt:
			self._resetGame()
			self._printLogs("KeyBoard Interrupt initiated", "FAIL")
			self.motion_service.stopMove()
			return

		self._resetGame()
		time.sleep(1)

		return


	def _addTopic(self):
		self._printLogs("Starting topic adding process", "NORMAL")

		# Disabling hand gestures and movement while speaking
		self.speaking_movement.setEnabled(False)

		self.dialog_service.setLanguage("English")
		# Loading the topic given by the user (absolute path is required)

		topic_path = "/home/nao/chat/{}".format(TOPIC_NAME)

		topf_path = topic_path.decode('utf-8')
		self.topic_name = self.dialog_service.loadTopic(
			topf_path.encode('utf-8'))

		# Activating the loaded topic
		self.dialog_service.activateTopic(self.topic_name)

		# Starting the dialog engine - we need to type an arbitrary string as the identifier
		# We subscribe only ONCE, regardless of the number of topics we have activated
		self.dialog_service.subscribe('tic_tac_toe_example')

		self._printLogs(
			"\nSpeak to the robot using rules. Robot is ready", "NORMAL")

		return

	def _cleanUp(self):
		self._printLogs("Starting Clean Up process", "FAIL")
		self.human_watcher.stop_basic_awareness()

		# Stopping any movement if there
		self.motion_service.stopMove()
		# stopping the dialog engine
		self.dialog_service.unsubscribe('tic_tac_toe_example')
		# Deactivating the topic
		self.dialog_service.deactivateTopic(self.topic_name)

		# now that the dialog engine is stopped and there are no more activated topics,
		# we can unload our topic and free the associated memory
		self.dialog_service.unloadTopic(self.topic_name)

		self._clearTablet()
		self.posture_service.goToPosture("StandInit", 0.1)

		return

	def run(self):
		self._printLogs(
			"Waiting for the robot to be in wake up position", "OKBLUE")

		self.motion_service.wakeUp()
		self.posture_service.goToPosture("StandInit", 0.1)

		# self._localiseRobot()

		self.create_callbacks()
		self._addTopic()
		self.human_watcher.start_basic_awareness()

		# loop on, wait for events until manual interruption
		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			self._printLogs("Interrupted by user, shutting down", "FAIL")
			self._cleanUp()
			self._printLogs("Waiting for the robot to be in rest position", "FAIL")
			# self.motion_service.rest()
			sys.exit(0)

		return


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--ip", type=str, default="10.9.45.11",
						help="Robot IP address. On robot or Local Naoqi: use \
						'127.0.0.1'.")
	parser.add_argument("--port", type=int, default=9559,
						help="Naoqi port number")

	args = parser.parse_args()

	# Initialize qi framework.
	connection_url = "tcp://" + args.ip + ":" + str(args.port)
	app = qi.Application(["TicTacToeGame",
						  "--qi-url=" + connection_url])

	tic_tac_toe = TicTacToe()
	human_tracked_event_watcher = HumanTrackedEventWatcher(app)
	event_watcher = TicTacToeGame(
		app, human_tracked_event_watcher, tic_tac_toe)
	event_watcher.run()
