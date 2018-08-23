from random import randint

####################################
# DEVELOPER        : VIKRAM SINGH  #
# TECHNOLOGY STACK : PYTHON        #
####################################


# Evaluation Definitions
X_WINS =  1000
O_WINS = -1000
DRAW   =  0


class TicTacToe():
	'''
	ALGO: MIN-MAX

	By making any of the move if in the upcoming possibilities if opponent has even
	one single winning move and all loosing move then I AM LOST.

	If opponent has all lost moves then I win.
	'''

	def __init__(self):

		self.outcomes     = []
		self.gameBoard    = ['.'] * 9
		self.coinsType    = ['x', 'o']
		self.gameOn       = True
		self.computerPlay = 0
		self.computerType = '-'
		self.humanType    = '-'


	def _checkIfWinner(self, playerType):
		# check verticals
		if self.gameBoard[0] == self.gameBoard[3] and self.gameBoard[0] == self.gameBoard[6] and self.gameBoard[0] == playerType:
			return True

		if self.gameBoard[1] == self.gameBoard[4] and self.gameBoard[1] == self.gameBoard[7] and self.gameBoard[1] == playerType:
			return True

		if self.gameBoard[2] == self.gameBoard[5] and self.gameBoard[2] == self.gameBoard[8] and self.gameBoard[2] == playerType:
			return True

		# check horizontals
		if self.gameBoard[0] == self.gameBoard[1] and self.gameBoard[0] == self.gameBoard[2] and  self.gameBoard[0] == playerType:
			return True
		if self.gameBoard[3] == self.gameBoard[4] and self.gameBoard[3] == self.gameBoard[5] and self.gameBoard[3] == playerType:
			return True
		if self.gameBoard[6] == self.gameBoard[7] and self.gameBoard[6] == self.gameBoard[8] and self.gameBoard[6] == playerType:
			return True

		# check diagonal
		if self.gameBoard[0] == self.gameBoard[4] and self.gameBoard[8] == self.gameBoard[0] and self.gameBoard[0] == playerType:
			return True
		if self.gameBoard[2] == self.gameBoard[4] and self.gameBoard[2] == self.gameBoard[6] and self.gameBoard[2] == playerType:
			return True

		return False

	def _switchPlayerType(self, playerType):
		if playerType == 'x':
			return 'o'
		return 'x'

	def _findPlayerTypeWins(self, playerType):
		if playerType == 'x':
			return X_WINS
		return O_WINS

	def _isBoardFull(self):
		if '.' in self.gameBoard:
			return False
		return True

	def _checkGameOver(self):
		if self._checkIfWinner('x'):
			return (True, 'x')
		if self._checkIfWinner('o'):
			return (True, 'o')
		if self._isBoardFull():
			return (True, 'd')

		return (False, '.')

	def _validPositionToEnterCoin(self, pos):
		return self.gameBoard[pos] == '.'

	def _positionEvaluation(self, playerType):
		if self._checkIfWinner(playerType):
			return self._findPlayerTypeWins(playerType)

		if self._checkIfWinner(self._switchPlayerType(playerType)):
			return self._findPlayerTypeWins(self._switchPlayerType(playerType))

		return DRAW

	def _findMove(self, depth, playerType):
		ans = 0
		possibilities = [-1] * 9

		if self._positionEvaluation(playerType) != DRAW:
			return (possibilities, self._positionEvaluation(playerType))

		if self._isBoardFull():
			return (possibilities, self._positionEvaluation(playerType))

		for idx, e in enumerate(self.gameBoard):
			if e == '.':
				self.gameBoard[idx] = playerType
				res = self._findMove(depth + 1, self._switchPlayerType(playerType))
				possibilities[idx] = res[1]
				self.gameBoard[idx] = '.'


		if self._findPlayerTypeWins(playerType) in possibilities:
			ans = self._findPlayerTypeWins(playerType)
		elif DRAW in possibilities:
			ans = DRAW
		else:
			ans = self._findPlayerTypeWins(self._switchPlayerType(playerType))

		return (possibilities, ans)

	def _printGameBoard(self):
		print "\n 0 1 2       |           " + self.gameBoard[0] + " " + self.gameBoard[1] + " " + self.gameBoard[2]
		print " 3 4 5       |           " + self.gameBoard[3] + " " + self.gameBoard[4] + " " + self.gameBoard[5]
		print " 6 7 8       |           " + self.gameBoard[6] + " " + self.gameBoard[7] + " " + self.gameBoard[8]
		print "\n"

		return

	def _getPossibilitiesInterpretation(self, playerType):
		possibilities = ["You Win" if possibility == self._findPlayerTypeWins(playerType) else possibility for possibility in self.outcomes]
		possibilities = ["You Loose" if possibility == self._findPlayerTypeWins(self._switchPlayerType(playerType)) else possibility for possibility in possibilities]
		interpreatation = zip([i for i in range(9)], ["Draw" if possibility == 0 else possibility for possibility in possibilities])

		return interpreatation

	def _printPossibilitiesInterpretation(self, playerType):
		interpreatation = self._getPossibilitiesInterpretation(playerType)
		for tup in interpreatation:
			print tup[0], " : ", tup[1]
		print

		return

	def _getBestPossibleIndexForPlaying(self, playerType):
		interpreatation = self._getPossibilitiesInterpretation(playerType)

		# first check if winning possible
		res = [tup[0] for tup in interpreatation if tup[1] == "You Win"]
		if res:
			return res[randint(0, len(res)-1)]

		# then check if draw possible
		res = [tup[0] for tup in interpreatation if tup[1] == "Draw"]
		if res:
			return res[randint(0, len(res)-1)]

		# last possible
		res = [tup[0] for tup in interpreatation if tup[1] == "You Loose"]
		if res:
			return res[randint(0, len(res)-1)]

		return -1


	def _startGameLoop(self):
		# Game Loop till it ends or crashes
		while(self.gameOn):

			humanValidPos = False
			self._printGameBoard()
			pos =  input("Enter position for `" + self.humanType + "` : ")
			while not humanValidPos:
				if not self._validPositionToEnterCoin(pos):
					pos = input("Please enter valid position for `" + self.humanType + "` : ")
				else:
					humanValidPos = True

			self.gameBoard[pos] = self.humanType

			# Checking If game over
			result = self._checkGameOver()
			if result[0]:
				self._printGameBoard()
				if result[1] == 'd':
					print "Game Over ! Result => DRAW"
				else:
					if self.computerType == result[1]:
						print "Game Over ! Result => Computer Wins"
					else:
						print "Game Over ! Result => Human Wins, Actually just writing, even though it will never happen"
				return 1


			self.outcomes = self._findMove(1, self.computerType)[0]

			print
			print self.outcomes
			self._printPossibilitiesInterpretation(self.computerType)

			pos = self._getBestPossibleIndexForPlaying(self.computerType)
			self.gameBoard[pos] = self.computerType


			# Checking If game over
			result = self._checkGameOver()
			if result[0]:
				self._printGameBoard()
				if result[1] == 'd':
					print "Game Over ! Result => DRAW"
				else:
					if self.computerType == result[1]:
						print "Game Over ! Result => Computer Wins"
					else:
						print "Game Over ! Result => Human Wins, Actually just writing, even though it will never happen"
				return 1

		return 0

	def startNewGameOnTerminal(self):
		self.gameBoard = ['.'] * 9;
		self.computerPlay = input("\nWho starts first ?\n 1: Computer\n 2: Player\n\n ")

		if self.computerPlay == 1:
			self.computerType = self.coinsType[randint(0,1)] # Random Selection
			self.humanType = self._switchPlayerType(self.computerType)
			print "\nComputer Selects : ", self.computerType
			print "You are now : ", self.humanType

			# Computer Making First Move
			firstPossibilities = [0, 2, 4, 6, 8] #best possible moves, though all are equal if played optimally.
			pos =  firstPossibilities[randint(0, len(firstPossibilities)-1)]
			self.gameBoard[pos] = self.computerType
		else:
			self.humanType = raw_input("Choose your coin type [`x` / `o`]: ")
			self.computerType = self._switchPlayerType(self.humanType)
			print "\nComputer is : ", self.computerType
			print "You are : ", self.humanType
		self._startGameLoop()

		return


	def robotsNextMove(self, humanMove):
		# while not humanValidPos:
		# 	if not self._validPositionToEnterCoin(pos):
		# 		pos = input("Please enter valid position for `" + self.humanType + "` : ")
		# 	else:
		# 		humanValidPos = True

		response = ""
		returnMove = -1
		self.gameBoard[humanMove] = self.humanType
		self._printGameBoard()
		# Checking If game over
		result = self._checkGameOver()
		if result[0]:
			if result[1] == 'd':
				print "Game Over ! Result => DRAW"
				response = "DR"
			else:
				if self.computerType == result[1]:
					print "Game Over ! Result => Computer Wins"
					response = "CW"
				else:
					print "Game Over ! Result => Human Wins, Actually just writing, even though it will never happen"
					response = "HW"
			return (True, returnMove, response)


		self.outcomes = self._findMove(1, self.computerType)[0]

		print
		print self.outcomes
		self._printPossibilitiesInterpretation(self.computerType)

		pos = self._getBestPossibleIndexForPlaying(self.computerType)
		returnMove = pos
		self.gameBoard[pos] = self.computerType
		self._printGameBoard()

		# Checking If game over
		result = self._checkGameOver()
		if result[0]:
			if result[1] == 'd':
				print "Game Over ! Result => DRAW"
				response = "DR"
			else:
				if self.computerType == result[1]:
					print "Game Over ! Result => Computer Wins"
					response = "CW"
				else:
					print "Game Over ! Result => Human Wins, Actually just writing, even though it will never happen"
					response = "HW"
			return (True, returnMove, response)

		return (False, returnMove, response)

	def startNewGameWithRobot(self, playerOne, playerType):
		self.gameBoard = ['.'] * 9
		pos = -1

		if playerOne == "COMPUTER":
			self.computerType = self.coinsType[randint(0,1)] # Random Selection
			self.humanType = self._switchPlayerType(self.computerType)
			print "\nComputer Selects : ", self.computerType
			print "You are now : ", self.humanType

			# Computer Making First Move
			firstPossibilities = [0, 2, 4, 6, 8] #best possible moves, though all are equal if played optimally.
			pos =  firstPossibilities[randint(0, len(firstPossibilities)-1)]
			self.gameBoard[pos] = self.computerType
			self._printGameBoard()

		if playerOne == "HUMAN":
			self.humanType = playerType
			self.computerType = self._switchPlayerType(self.humanType)
			print "\nComputer is : ", self.computerType
			print "You are : ", self.humanType
			self._printGameBoard()

		dic = {}
		dic["computerMove"] = pos
		dic["computerType"] = self.computerType
		dic["humanType"] = self.humanType

		return dic



	def run(self):
		self.startNewGameOnTerminal()

		return


if __name__ == "__main__":
	game = TicTacToe()
	game.run()
