# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
import random
from itertools import chain, combinations
from itertools import product
from itertools import permutations
import math
import copy
from collections import OrderedDict


class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################

		#delete line 124 in world.py before submitting
		self.__rowDimension = rowDimension
		self.__colDimension = colDimension
		self.__totalMines = totalMines
		self.__startX = startX
		self.__startY = startY
		self.totalMines = totalMines
		self.prevX = 0
		self.prevY = 0
		self.validateX = 0
		self.validateY = 0
		self.board =  [[-2 for i in range(self.__rowDimension)] for j in range(self.__colDimension)]
		self.tilesLeft = (self.__rowDimension * self.__colDimension)
		self.totalTiles = self.tilesLeft+1
		self.seen = set()
		self.uncoverQueue = set()
		self.notuncoverQueue = set()
		self.minesPlaced = 0
		self.mines = set()
		self.unplacedMines = set()
		self.otherMinesToFlag = []
		self.mineToFlag = tuple()
		self.frontierEdge = set()
		
		
		

		pass
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

	def isValidTile(self, x, y):
		isValid = False
		if(x < self.__colDimension and x >= 0 and y < self.__rowDimension and y >= 0):
			isValid = True
		return isValid
	
	def numProbNoMines(self, x, y):
		num = 0
		for i in range(x-1, x+2):
			for j in range(y-1, y+2):
				if((i,j) != (x, y) and self.isValidTile(i, j) and self.board[i][j] >=0):
					num += 1
		return num

	def adjacentTiles(self, x, y):
		returnVal = set()
		for i in range(x-1, x+2):
			for j in range(y-1, y+2):
				if(self.isValidTile(i,j) and (i,j) != (x,y)):
					returnVal.add((i,j))
		return returnVal

	def getNeighbors(self, x, y):
		tilesToReturn = []
		neighbors = set()
		for i in range(x-2, x+3):
			for j in range(y-2, y+3):
				if(self.isValidTile(i,j) and (i,j) != (x,y)):
					neighbors.add((i,j))
		for n in neighbors:
			neighborNum = self.board[n[0]][n[1]]
			if(neighborNum < 1):
				continue
			adj = self.adjacentTiles(n[0], n[1])			
			if (x,y) in adj:
				adj.remove((x,y))
			inSeen = True
			for a in adj:
				if(a not in self.seen):
					inSeen = False
					break
			if(inSeen == True):
				continue
			adj2 = self.adjacentTiles(x, y)					
			if n in adj2:
				adj2.remove(n)
			notAdj = adj.difference(adj2)					
			notAdj2 = adj2.difference(adj)					
			minesAdj2 = self.setMinesNearby(x, y)			
			minesAdj = self.setMinesNearby(n[0], n[1])		
			bothOfTheMines = minesAdj2.intersection(adj)	
			minesNotAdj2 = minesAdj2.intersection(notAdj2)	
			minesNotAdj = minesAdj.intersection(notAdj)		
			lenBoth = len(bothOfTheMines)					
			lenNotAdj2 = len(minesNotAdj2)					
			lenNotAdj = len(minesNotAdj)					
			inSeen = True
			for a in notAdj:
				if(a not in self.seen):
					inSeen = False
					break
			if(inSeen == False):
				continue
			if(lenNotAdj == 0 and lenBoth == 0):
				continue
			if(self.board[x][y] - lenNotAdj2 == neighborNum - lenNotAdj):
				for tile in notAdj2:
					if(tile not in self.seen):
						tilesToReturn.append(tile)
		return tilesToReturn


	def numAdjacentCovered(self, x, y):
		num = 0
		for i in range(x-1, x+2):
			for j in range(y-1, y+2):
				if((i,j) != (x, y) and self.isValidTile(i, j) and self.board[i][j] == -2):
					num += 1
		return num
	def addAdjacentToQueue(self, currentX, currentY, queue):
		for i in range(currentX-1, currentX+2):
			for j in range(currentY-1, currentY+2):
				if((i,j) != (currentX, currentY) and self.isValidTile(i, j) and (i,j) not in queue and (i,j) not in self.mines):
					if((i,j) not in self.seen):
						if(isinstance(queue, list)):
							queue.append((i,j))
						if(isinstance(queue, set)):
							queue.add((i,j))
		return
	def minesNearby(self, x, y):
		mines = 0
		for i in range(x-1, x+2):
			for j in range(y-1, y+2):
				if((i,j) != (x, y) and self.isValidTile(i, j) and self.board[i][j] == -1):
					mines+=1
		return mines
	
	def setMinesNearby(self,x,y):
		mines = set()
		for i in range(x-1, x+2):
			for j in range(y-1, y+2):
				if((i,j) != (x, y) and self.isValidTile(i, j) and self.board[i][j] == -1):
					mines.add((i,j))
		return mines

	def isAdjacent(self, x,y, mine):

		return abs(mine[0]-x) < 2 and abs(mine[1]-y) < 2

	def deduceMines(self, x, y, possibleMines, number):
		numAdjacentPossibleMines = 0
		unmarked = 0
		unmarkedList = []
		adjacentMines = []
		for i in range(x-1, x+2):
			for j in range(y-1, y+2):
				if(self.isValidTile(i,j) == False):
					continue
				if(((i,j) != (x,y) and self.isValidTile(i,j)) and ((i,j) in possibleMines and (i,j) not in self.seen) or (self.board[i][j]) == -1):
						if(self.board[i][j] == -1):
							adjacentMines.append((i, j))
						numAdjacentPossibleMines += 1
				if((i,j) != (x,y) and self.isValidTile(i,j) and self.board[i][j] == -2):
					if((i,j) not in self.seen):
						unmarkedList.append((i,j))
						unmarked+=1
		number -= len(adjacentMines)
		adjacentMines.clear()
		if(number==0):
			for tile in self.frontierEdge:
				if(self.isAdjacent(x, y, tile) and tile not in self.seen):
					self.uncoverQueue.add(tile)
			return False
		if(number == numAdjacentPossibleMines):
			for mine in possibleMines:
				if(mine not in self.seen and self.isAdjacent(x,y,mine)):
					self.seen.add(mine)
					self.mines.add(mine)
					self.board[mine[0]][mine[1]] = -1
					if(mine in self.frontierEdge):
						self.frontierEdge.remove(mine)
					self.otherMinesToFlag.append(mine)
			self.prevX = x
			self.prevY = y
			self.mineToFlag = self.otherMinesToFlag[0]
			self.otherMinesToFlag.remove(self.mineToFlag)
			return True
		elif (unmarked == number):
			for mine in unmarkedList:
				self.seen.add(mine)
				self.mines.add(mine)
				self.board[mine[0]][mine[1]] = -1
				if(mine in self.frontierEdge):
					self.frontierEdge.remove(mine)
				self.otherMinesToFlag.append(mine)
			self.prevX = x
			self.prevY = y
			self.mineToFlag = self.otherMinesToFlag[0]
			self.otherMinesToFlag.remove(self.mineToFlag)
			return True
		else:
			for i in range(x-1, x+2):
				for j in range(y-1, y+2):
					if(self.isValidTile(i,j) == True and self.numAdjacentCovered(i,j)>0):
						neighbors = self.getNeighbors(i,j)
						if neighbors is not None and neighbors != []:
							for k in neighbors:
								if k not in self.seen and k not in self.uncoverQueue:
									self.uncoverQueue.add(k)
			
			# notZero = []
			# self.fillNotZero(x, y, notZero)
			# deduceList = []
			# allRelevantTiles = set()
			# #create combinations of possible mine locations
			# for tile in notZero:
			# 	if(self.board[tile[0]][tile[1]] == -1):
			# 		number-=1
			# for tile in notZero:
			# 	adjacentToTile = []
			# 	self.addAdjacentToQueue(tile[0], tile[1], adjacentToTile)
			# 	for relevant in adjacentToTile:
			# 		allRelevantTiles.add(relevant)
			# 	if(tile[0] == x and tile[1] == y):
			# 		num = number
			# 	else:
			# 		num = self.board[tile[0]][tile[1]]
			# 	comb = []
			# 	combCopy = copy.deepcopy(comb)
			# 	if(num > 1):
			# 		comb = list(combinations(adjacentToTile, num))
			# 		for i in comb:
			# 			if(self.isAdjacent(x, y, i[0]) == True):
			# 				combCopy.append(i)
			# 	elif(num == 1):
			# 		for i in adjacentToTile:
			# 			if(self.isAdjacent(x, y, i) == True):
			# 				combCopy.append(i)
			# 	else:
			# 		pass
				
			# 	comb = combCopy
			# 	if(len(comb) > 1):
			# 		deduceList.append(comb)
			# #deduction logic
			# pseudoAndList = []
			# for orList in deduceList:
			# 	orListCopy = copy.deepcopy(orList)
			# 	orList = orListCopy
			# 	pseudoAndList.clear()
			# 	for item in orList:
			# 		pseudoAndList.append(item)
			# 	for item in deduceList:
			# 		itemCopy = copy.deepcopy(item)
			# 		for i in itemCopy:
			# 			if(list(i) == pseudoAndList):
			# 				item.remove(i)
			# 				deduceList.remove(list(i))
			# #if mines have been narrowed down, mark them
			# if(len(deduceList) == 1):
			# 	for mines in deduceList[0]:
			# 		for mine in mines:
			# 			allRelevantTiles.remove(mine)
			# 			self.seen.add(mine)
			# 			self.mines.add(mine)
			# 			self.board[mine[0]][mine[1]] = -1
			# 			self.minesPlaced += 1
			# 		for tile in allRelevantTiles:
			# 			self.uncoverQueue.append(tile)
			# 		self.prevX = x
			# 		self.prevY = y
			# 		self.mineToFlag = mines[0]
			# 		return "uncover safe"
		return False

	def fillNotZero(self, x, y, notZero):
		for i in range(x-1, x+2):
			for j in range(y-1, y+2):
				#modified to make sure mines arent included
				if(self.isValidTile(i,j) and self.board[i][j] > 0):
					if(isinstance(notZero, list)):
						notZero.append((i,j))
					if(isinstance(notZero, set)):
						notZero.add((i,j))
		return
	def fillNegativeTwo(self, x, y, set):
		for i in range(x-1, x+2):
			for j in range(y-1, y+2):
				if(self.isValidTile(i,j) and self.board[i][j] == -2):
					set.add((i,j))

	def canUncoverAll(self, number, x, y):
		if (number == 0):
			return True
		if (self.minesEqualNumber(number, x, y)):
			return True
		return False

	def minesEqualNumber(self, number, x, y):
		numAdjacentMines = 0
		for i in range(x-1, x+2):
			for j in range(y-1, y+2):
				if(self.isValidTile(i,j) and self.board[i][j] == -1):
						numAdjacentMines+=1
		if(numAdjacentMines == number):
			return True
		else:
			return False
	def allUncovered(self, x, y):
		for i in range(x-1, x+2):
			for j in range(y-1, y+2):
				if((i,j) != (x,y) and self.isValidTile(i,j) and self.board[i][j] == -2):
					return False
		return True
	def probability(self):
		combinationsDict = OrderedDict()
		nonZeroTilesDict = OrderedDict()
		nonZeroTilesSet = set()
		for edge in self.frontierEdge:
			if edge not in self.seen:
				self.fillNotZero(edge[0], edge[1], nonZeroTilesSet)
			for tile in nonZeroTilesSet:
				if(len(combinationsDict) == 15):
					break
				if(self.isAdjacent(edge[0], edge[1], tile)):
					combinationsDict[edge] = None
					break
		for tile in nonZeroTilesSet:
			nonZeroTilesDict[tile] = self.board[tile[0]][tile[1]]
			mines = self.minesNearby(tile[0], tile[1])
			nonZeroTilesDict[tile]-=mines
		arrangements = self.generateArrangements(combinationsDict=combinationsDict, nonZeroTiles=nonZeroTilesDict, arrangements = [])
		totalArrangements = self.nCr(self.totalTiles, self.totalMines)
		arrangementsDict = OrderedDict()
		for arrangement in arrangements:
			mineCount = 0
			for val in arrangement:
				if(arrangement[val] == True):
					mineCount+=1
			possibleMinesLeft = self.totalMines-self.minesPlaced-mineCount
			possibleCombs = self.nCr(self.tilesLeft, mineCount)
			for val in arrangement:
				if(val not in arrangementsDict):
					arrangementsDict[val] = 0
				if(arrangement[val] == True):
					arrangementsDict[val] += possibleCombs
			pass
		for value in arrangementsDict:
			arrangementsDict[value] /= totalArrangements
			arrangementsDict[value] *= 100
		return arrangementsDict

		# for tile in self.frontierEdge:
		# 	nonZeroTiles = set()
		# 	self.fillNotZero(tile[0],tile[1],nonZeroTiles)
		# 	for cell in nonZeroTiles:
		# 		if(cell in combinationsDict):
		# 			continue
		# 		adjacentTiles = []
		# 		num = self.board[cell[0]][cell[1]]
		# 		if(num < 1):
		# 			continue
		# 		comb = []
		# 		self.addAdjacentToQueue(cell[0],cell[1], adjacentTiles)
		# 		adjacentTiles = sorted(adjacentTiles)
				
		# 		combinationsDict[cell] = adjacentTiles
		# all_configurations_set = set(self.solve(combinationsDict=combinationsDict))
		# all_configurations = [list(config) for config in all_configurations_set]
		# pass
		# return
	def isValidArrangement(self, nonZeroTiles):
		for tile in nonZeroTiles:
			if(nonZeroTiles[tile] < 0):
				return False
		return True

	def isValidFinalArrangement(self, nonZeroTiles):
		for tile in nonZeroTiles:
			if(nonZeroTiles[tile] != 0):
				return False
		return True
	def updateNonZeroTiles(self, nonZeroTiles, edgeTile):
		adjacent = []
		for tile in nonZeroTiles:
			if(self.isAdjacent(edgeTile[0], edgeTile[1], tile) and nonZeroTiles[tile] > 0):
				adjacent.append(tile)
		for cell in adjacent:
			nonZeroTiles[cell]-=1
		return
	def generateArrangements(self,combinationsDict, nonZeroTiles, index=0, arrangements=[], theoreticalMinesPlaced = 0):
		# if(self.isValidArrangement(nonZeroTiles) == False or theoreticalMinesPlaced >= (self.totalMines-self.minesPlaced)):
		# 	return arrangements
		# if(index == len(combinationsDict)):
		# 	if(self.isValidFinalArrangement(nonZeroTiles) and theoreticalMinesPlaced < (self.totalMines-self.minesPlaced)):
		# 		finalCombination = combinationsDict.copy()
		# 		if(finalCombination not in arrangements):
		# 			arrangements.append(finalCombination)
		# 	return arrangements
		# else:
		# 	key = list(combinationsDict.keys())[index]
		# 	nonZeroTilesCopy = nonZeroTiles.copy()
		# 	combinationsDictCopy = combinationsDict.copy()
		# 	combinationsDictCopy[key] = True
		# 	self.updateNonZeroTiles(nonZeroTilesCopy, key)
		# 	self.generateArrangements(combinationsDictCopy, nonZeroTilesCopy, index+1, arrangements,theoreticalMinesPlaced+1)

		# 	combinationsDictCopy[key] = False
		# 	self.generateArrangements(combinationsDictCopy,nonZeroTiles,index+1,arrangements,theoreticalMinesPlaced)
		# return arrangements


		if index == len(combinationsDict):
			arrangements.append(combinationsDict.copy())
		else:
			key = list(combinationsDict.keys())[index]
			combinationsDictCopy = combinationsDict.copy()
			nonZeroTilesCopy = nonZeroTiles.copy()
			if(self.canPlaceMine(key, nonZeroTilesCopy) == True and theoreticalMinesPlaced < (self.totalMines - self.minesPlaced)):
				combinationsDictCopy[key] = True
				self.generateArrangements(combinationsDictCopy, nonZeroTilesCopy, index+1, arrangements, theoreticalMinesPlaced+1)
			combinationsDictCopy[key] = False
			self.generateArrangements(combinationsDictCopy, nonZeroTiles, index+1, arrangements, theoreticalMinesPlaced)
		return arrangements

	def canPlaceMine(self, edgeTile, nonZeroTiles):
		adjacent = []
		for tile in nonZeroTiles:
			if(self.isAdjacent(edgeTile[0], edgeTile[1], tile) and nonZeroTiles[tile] > 0):
				adjacent.append(tile)
			elif(self.isAdjacent(edgeTile[0], edgeTile[1], tile) and nonZeroTiles[tile] == 0):
				return False
		for cell in adjacent:
			nonZeroTiles[cell]-=1
		return True
		#imperfect needs improving
	def canNotPlaceMine(self, edgeTile, combinationsDict):
		x = edgeTile[0]
		y = edgeTile[1]
		x-=1									# left
		y-=1									# upper left	case 1
		if(self.isValidTile(x, y) and self.board[x][y] >= 0):
			nearbyMines = -1
			if(self.board[x][y] != -1):
				nearbyMines = self.minesNearby(x, y)
			numCovered = self.numAdjacentCovered(x, y)
			numTheoretical = 0
			for tile in combinationsDict:
				if(combinationsDict[tile] == False or combinationsDict[tile] == None):
					numTheoretical+=1
			notMineAdj = self.numProbNoMines(x, y)
			if(nearbyMines >= numCovered - numTheoretical - notMineAdj):
				return False
		y+=1 									# direct left	case 2
		if(self.isValidTile(x, y) and self.board[x][y] >= 0):
			nearbyMines = -1
			if(self.board[x][y] != -1):
				nearbyMines = self.minesNearby(x, y)
			numCovered = self.numAdjacentCovered(x, y)
			numTheoretical = 0
			for tile in combinationsDict:
				if(combinationsDict[tile] == False or combinationsDict[tile] == None):
					numTheoretical+=1
			notMineAdj = self.numProbNoMines(x, y)
			if(nearbyMines >= numCovered - numTheoretical - notMineAdj):
				return False
		y+=1									# bottom left	case 3
		if(self.isValidTile(x, y) and self.board[x][y] >= 0):
			nearbyMines = -1
			if(self.board[x][y] != -1):
				nearbyMines = self.minesNearby(x, y)
			numCovered = self.numAdjacentCovered(x, y)
			numTheoretical = 0
			for tile in combinationsDict:
				if(combinationsDict[tile] == False or combinationsDict[tile] == None and self.isAdjacent(x, y, tile) and (x,y) != tile):
					numTheoretical+=1
			notMineAdj = self.numProbNoMines(x, y)
			if(nearbyMines >= numCovered - numTheoretical - notMineAdj):
				return False
		y-=1									# reset y

		x+=1									# center
		y-=1									# up			case 4
		if(self.isValidTile(x, y) and self.board[x][y] >= 0):
			nearbyMines = -1
			if(self.board[x][y] != -1):
				nearbyMines = self.minesNearby(x, y)
			numCovered = self.numAdjacentCovered(x, y)
			numTheoretical = 0
			for tile in combinationsDict:
				if(combinationsDict[tile] == False or combinationsDict[tile] == None):
					numTheoretical+=1
			notMineAdj = self.numProbNoMines(x, y)
			if(nearbyMines >= numCovered - numTheoretical - notMineAdj):
				return False
		y+=2									# down			case 5
		if(self.isValidTile(x, y) and self.board[x][y] >= 0):
			nearbyMines = -1
			if(self.board[x][y] != -1):
				nearbyMines = self.minesNearby(x, y)
			numCovered = self.numAdjacentCovered(x, y)
			numTheoretical = 0
			for tile in combinationsDict:
				if(combinationsDict[tile] == False or combinationsDict[tile] == None):
					numTheoretical+=1
			notMineAdj = self.numProbNoMines(x, y)
			if(nearbyMines >= numCovered - numTheoretical - notMineAdj):
				return False
		y-=1									# reset y

		x+=1									# right
		y-=1									# upper right	case 6
		if(self.isValidTile(x, y) and self.board[x][y] >= 0):
			nearbyMines = -1
			if(self.board[x][y] != -1):
				nearbyMines = self.minesNearby(x, y)
			numCovered = self.numAdjacentCovered(x, y)
			numTheoretical = 0
			for tile in combinationsDict:
				if(combinationsDict[tile] == False or combinationsDict[tile] == None):
					numTheoretical+=1
			notMineAdj = self.numProbNoMines(x, y)
			if(nearbyMines >= numCovered - numTheoretical - notMineAdj):
				return False			
		y+=1									# direct right	case 7
		if(self.isValidTile(x, y) and self.board[x][y] >= 0):
			nearbyMines = -1
			if(self.board[x][y] != -1):
				nearbyMines = self.minesNearby(x, y)
			numCovered = self.numAdjacentCovered(x, y)
			numTheoretical = 0
			for tile in combinationsDict:
				if(combinationsDict[tile] == False or combinationsDict[tile] == None):
					numTheoretical+=1
			notMineAdj = self.numProbNoMines(x, y)
			if(nearbyMines >= numCovered - numTheoretical - notMineAdj):
				return False
		y+=1									# lower right	case 8
		if(self.isValidTile(x, y) and self.board[x][y] >= 0):
			nearbyMines = -1
			if(self.board[x][y] != -1):
				nearbyMines = self.minesNearby(x, y)
			numCovered = self.numAdjacentCovered(x, y)
			numTheoretical = 0
			for tile in combinationsDict:
				if(combinationsDict[tile] == False or combinationsDict[tile] == None):
					numTheoretical+=1
			notMineAdj = self.numProbNoMines(x, y)
			if(nearbyMines >= numCovered - numTheoretical - notMineAdj):
				return False
		return True

		# keyAdjacencies = []
		# adjacencies = []
		# for i in range(0, len(combinationsDict)):
		# 	key = list(combinationsDict.keys())[i]
		# 	if(self.isAdjacent(edgeTile[0], edgeTile[1], key) and key is not edgeTile):
		# 		keyAdjacencies.append(key)
		# for tile in nonZeroTiles:
		# 	if(self.isAdjacent(edgeTile[0], edgeTile[1], tile)):
		# 		if(nonZeroTiles[tile] == 0):						#if this ever equals zero we can only not place a mine
		# 			return True
		# 		else:
		# 			adjacencies.append(tile)
		# nonZeroTilesCopy = nonZeroTiles.copy()
		# for edge in keyAdjacencies:
		# 	self.canPlaceMine(edge, nonZeroTilesCopy)
		# for tile in adjacencies:
		# 	if(nonZeroTilesCopy[tile] == 0):
		# 		return True
		# return False
			
		# return combinationsList
	def getFrontierEdge(self, x, y):
		for i in range(x-1, x+2):
			for j in range(y-1, y+2):
				if((i,j) != (x,y) and self.isValidTile(i,j) and self.board[i][j] == -2):
					self.frontierEdge.add((i,j))
		return
	def nCr(self, n, r):
		return math.factorial(n) / (math.factorial(r) * math.factorial(n-r))


	def getAction(self, number: int) -> "Action Object":

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		if(self.tilesLeft < 0):
			return Action(AI.Action.LEAVE)
		possibleMines = []
		
		if(number != -1):
			currentX = self.__startX
			currentY = self.__startY
			self.board[currentX][currentY] = number
		else:
			currentX = self.prevX
			currentY = self.prevY
		self.seen.add((currentX, currentY))
		self.getFrontierEdge(currentX, currentY)
		self.tilesLeft-=1
		
		# print(self.tilesLeft, "tiles left", end="\r")
		flaggedMines = self.otherMinesToFlag.copy()
		for mine in flaggedMines:
			self.prevX = mine[0]
			self.prevY = mine[1]
			self.otherMinesToFlag.remove(mine)
			self.getFrontierEdge(mine[0], mine[1])
			self.minesPlaced += 1
			return Action(AI.Action.FLAG, mine[0], mine[1])

		if(self.minesPlaced < self.totalMines):
			if(self.canUncoverAll(number, currentX, currentY)):
				self.addAdjacentToQueue(currentX, currentY, self.uncoverQueue)
				while(len(self.uncoverQueue) > 0):
					currentTuple = self.uncoverQueue.pop()
					if(self.board[currentTuple[0]][currentTuple[1]] != -2):
						continue
					self.__startX = currentTuple[0]
					self.__startY = currentTuple[1]
					if(currentTuple in self.frontierEdge):
						self.frontierEdge.remove(currentTuple)
					return Action(AI.Action.UNCOVER, currentTuple[0], currentTuple[1])
				else:
					uncoverCopy = self.notuncoverQueue.copy() 
					while(len(self.notuncoverQueue) > 0):
						currentTuple = self.notuncoverQueue.pop()
						currentNum = self.board[currentTuple[0]][currentTuple[1]]
						self.addAdjacentToQueue(currentTuple[0], currentTuple[1], possibleMines)
						if(self.deduceMines(currentTuple[0], currentTuple[1], possibleMines, currentNum)):
							if(currentTuple in self.frontierEdge):
								self.frontierEdge.remove(currentTuple)
							self.getFrontierEdge(currentTuple[0], currentTuple[1])
							self.minesPlaced += 1
							return Action(AI.Action.FLAG, self.mineToFlag[0], self.mineToFlag[1])
					# for tile in uncoverCopy:
					# 	self.uncoverQueue.add(tile)
					#probabilities start
					# while(len(self.uncoverQueue) > 0):
						# currentTuple = self.uncoverQueue.pop()
						# if(self.allUncovered(currentTuple[0], currentTuple[1])):
						# 	continue
						# elif(self.canUncoverAll(self.board[currentTuple[0]][currentTuple[1]], currentTuple[0], currentTuple[1])):
						# 	if(currentTuple in self.seen):
						# 		continue
					arrangementsDict = self.probability()
					if(len(arrangementsDict) < 1):
						# print("dont know what to do, number is ", number)
						currentTuple = self.frontierEdge.pop()
						self.__startX = currentTuple[0]
						self.__startY = currentTuple[1]
						return Action(AI.Action.UNCOVER, currentTuple[0], currentTuple[1])
					tile = tuple()
					tile = min(arrangementsDict, key=arrangementsDict.get)
					del arrangementsDict[tile]
					while(tile not in self.frontierEdge):
						tile = min(arrangementsDict, key=arrangementsDict.get)
						arrangementsDict.remove(tile)
					self.__startX = tile[0]
					self.__startY = tile[1]
					if(tile in self.frontierEdge):
						self.frontierEdge.remove(tile)
					self.notuncoverQueue.add(tile)
					if(tile in self.uncoverQueue):
						self.uncoverQueue.remove(tile)
					return Action(AI.Action.UNCOVER, tile[0], tile[1])

			else:
				# make sure that the tiles in uncover queue are all possible positive number tiles
				for tile in self.frontierEdge:
					notZero = []
					self.fillNotZero(tile[0], tile[1], notZero)
					for cell in notZero:
						if(cell not in self.notuncoverQueue):
							self.notuncoverQueue.add(cell)
				# self.notuncoverQueue.append((currentX, currentY))
				while(len(self.uncoverQueue) > 0):
					currentTuple = self.uncoverQueue.pop()
					if(self.board[currentTuple[0]][currentTuple[1]] != -2):
						continue
					if(currentTuple not in self.seen):
						self.__startX = currentTuple[0]
						self.__startY = currentTuple[1]
						if(currentTuple in self.frontierEdge):
							self.frontierEdge.remove(currentTuple)
						return Action(AI.Action.UNCOVER, currentTuple[0], currentTuple[1])
				else:
					uncoverCopy = self.notuncoverQueue.copy() 
					while(len(self.notuncoverQueue) > 0):
						possibleMines.clear()
						currentTuple = self.notuncoverQueue.pop()
						if(self.allUncovered(currentTuple[0], currentTuple[1])):
							continue
						elif(self.canUncoverAll(self.board[currentTuple[0]][currentTuple[1]], currentTuple[0], currentTuple[1])):
							if(currentTuple in self.seen):
								continue
							self.__startX = currentTuple[0]
							self.__startY = currentTuple[1]
							if(currentTuple in self.frontierEdge):
								self.frontierEdge.remove(currentTuple)
							return Action(AI.Action.UNCOVER, currentTuple[0], currentTuple[1])
						currentNum = self.board[currentTuple[0]][currentTuple[1]]
						self.addAdjacentToQueue(currentTuple[0], currentTuple[1], possibleMines)
						var = self.deduceMines(currentTuple[0], currentTuple[1], possibleMines, currentNum)
						if(var == True):
							if(currentTuple in self.frontierEdge):
								self.frontierEdge.remove(currentTuple)
							self.getFrontierEdge(currentTuple[0], currentTuple[1])
							self.minesPlaced += 1
							return Action(AI.Action.FLAG, self.mineToFlag[0], self.mineToFlag[1])
					# for tile in uncoverCopy:
					# 	self.notuncoverQueue.add(tile)
					#probabilities start
					# while(len(uncoverCopy) > 0):
					currentTuple = uncoverCopy.pop()
					# if(self.allUncovered(currentTuple[0], currentTuple[1])):
					# 	continue
					arrangementsDict = self.probability()
					if(len(arrangementsDict) < 1):
						# print("dont know what to do, number is ", number)
						currentTuple = self.frontierEdge.pop()
						self.__startX = currentTuple[0]
						self.__startY = currentTuple[1]
						return Action(AI.Action.UNCOVER, currentTuple[0], currentTuple[1])
					tile = tuple()
					tile = min(arrangementsDict, key=arrangementsDict.get)
					del arrangementsDict[tile]
					while(tile not in self.frontierEdge):
						tile = min(arrangementsDict, key=arrangementsDict.get)
						arrangementsDict.remove(tile)
					self.__startX = tile[0]
					self.__startY = tile[1]
					if(tile in self.frontierEdge):
						self.frontierEdge.remove(tile)
					self.notuncoverQueue.add(tile)
					if(tile in self.uncoverQueue):
						self.uncoverQueue.remove(tile)
					return Action(AI.Action.UNCOVER, tile[0], tile[1])

		else:
			if(self.tilesLeft == 0):
				print("solved board!!!")
				return Action(AI.Action.LEAVE)
			i=self.validateX
			j=self.validateY
			while(i < self.__rowDimension):
				while(j < self.__colDimension):
						if(self.board[i][j] == -2):
							self.validateX = i
							self.validateY = j
							self.__startX = i
							self.__startY = j
							return Action(AI.Action.UNCOVER, i, j)
						else:
							j+=1
				i+=1
				j=0
				
				
		
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################
