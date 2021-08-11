import math, copy, random, time, decimal

from cmu_112_graphics import *


# CITATION: idea / pseudocode for map generation algorithm obtained from https://ijdykeman.github.io/ml/2017/10/12/wang-tile-procedural-generation.html
class GlobalMap(object):
    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.terrainTypes = ['ocean', 'lake', 'sand', 'plain', 'forest', 'snow', 'mountain']
        self.initTerrainMap(dimensions)
        self.generateTerrain(dimensions)
    
    def initTerrainMap(self, dimensions):
        terrainMapTypes = [False, 'ocean', 'ocean', 'lake', 'lake', 'sand', 'sand', 'sand', 'plain', 'plain', 'plain', 'plain', 'forest', 'forest', 'forest', 'snow', 'snow', 'mountain', 'mountain']
        self.terrainMap = []
        for row in range(dimensions[0]):
            r = []
            for col in range(dimensions[1]):
                r.append(copy.copy(terrainMapTypes))
            self.terrainMap.append(r)
        
    def fullTerrain(self, dimensions):
        for row in range(dimensions[0]):
            for col in range(dimensions[1]):
                if not self.terrainMap[row][col][0]:
                    return False
        return True

    def generateTerrain(self, dimensions):
        while not self.fullTerrain(dimensions):
            row = random.randrange(0, dimensions[0])
            col = random.randrange(0, dimensions[1])
            if self.terrainMap[row][col][0]:
                continue
            else:
                if len(self.terrainMap[row][col]) > 1:
                    self.terrainMap[row][col] = [True, random.choice(self.terrainMap[row][col][1:])]
                    self.adjustNearbyTiles(row, col, dimensions)
                else:
                    self.resetNearbyTiles(row, col, dimensions)
    
    def resetNearbyTiles(self, row, col, dimensions):
        dirs = []
        for h in range(-2, 3):
            for v in range(-2, 3):
                if abs(h) + abs(v) <= 2:
                    dirs.append((h, v))
        for dir in dirs:
            arow = row + dir[0]
            acol = col + dir[1]
            if (0 <= arow < dimensions[0]) and (0 <= acol < dimensions[1]):
                self.terrainMap[arow][acol] = [False, 'ocean', 'ocean', 'lake', 'lake', 'sand', 'sand', 'sand', 'plain', 'plain', 'plain', 'plain', 'forest', 'forest', 'forest', 'snow', 'snow', 'mountain', 'mountain']
        dirs = []
        for h in range(-4, 5):
            for v in range(-4, 5):
                if 3 <= abs(h) + abs(v) <= 4:
                    dirs.append((h, v))
        for dir in dirs:
            arow = row + dir[0]
            acol = col + dir[1]
            if (0 <= arow < dimensions[0]) and (0 <= acol < dimensions[1]) and (self.terrainMap[arow][acol][0]):
                self.adjustNearbyTiles(arow, acol, dimensions)

    
    def adjustNearbyTiles(self, row, col, dimensions):
        centerTileType = self.terrainMap[row][col][1]
        dirs1 = []
        for h in range(-1, 2):
            for v in range(-1, 2):
                if abs(h) + abs(v) <= 1:
                    dirs1.append((h, v))
        for dir in dirs1:
            if dir == (0, 0):
                continue
            arow = row + dir[0]
            acol = col + dir[1]
            if (0 <= arow < dimensions[0]) and (0 <= acol < dimensions[1]) and (not self.terrainMap[arow][acol][0]):
                for tileType in self.terrainMap[arow][acol][1:]:
                    if tileType != centerTileType and tileType != self.terrainTypes[self.terrainTypes.index(centerTileType) - 1] and tileType != self.terrainTypes[(self.terrainTypes.index(centerTileType) + 1) % 7]:
                        while(tileType in self.terrainMap[arow][acol]):
                            self.terrainMap[arow][acol].remove(tileType)
        dirs2 = []
        for h in range(-2, 3):
            for v in range(-2, 3):
                if abs(h) + abs(v) == 2:
                    dirs2.append((h, v))
        for dir in dirs2:
            if (0 <= row + dir[0] < dimensions[0]) and (0 <= col + dir[1] < dimensions[1]):
                arow = row + dir[0]
                acol = col + dir[1]
                for tileType in self.terrainMap[arow][acol][1:]:
                    if tileType != centerTileType and tileType != self.terrainTypes[self.terrainTypes.index(centerTileType) - 1] and tileType != self.terrainTypes[self.terrainTypes.index(centerTileType) - 2] and tileType != self.terrainTypes[(self.terrainTypes.index(centerTileType) + 1) % 7] and tileType != self.terrainTypes[(self.terrainTypes.index(centerTileType) + 2) % 7]:
                        while(tileType in self.terrainMap[arow][acol]):
                            self.terrainMap[arow][acol].remove(tileType)
    
    def getTerrainColor(self, row, col):
        if self.terrainMap[row][col][1] == 'ocean':
            color = 'blue4'
        if self.terrainMap[row][col][1] == 'lake':
            color = 'turquoise'
        if self.terrainMap[row][col][1] == 'sand':
            color = 'yellow'
        if self.terrainMap[row][col][1] == 'plain':
            color = 'SpringGreen2'
        if self.terrainMap[row][col][1] == 'forest':
            color = 'dark green'
        if self.terrainMap[row][col][1] == 'snow':
            color = 'white'
        if self.terrainMap[row][col][1] == 'mountain':
            color = 'brown4'
        return color
    
    def getTerrainResources(self, terrain):
        resourceValues = {'food': 0, 'gold': 0, 'prod': 0}
        if terrain == 'ocean':
            resourceValues['food'] = 4
        if terrain == 'lake':
            resourceValues['food'] = 3
            resourceValues['gold'] = 1
        if terrain == 'sand':
            resourceValues['gold'] = 4
        if terrain == 'plain':
            resourceValues['food'] = 3
            resourceValues['prod'] = 1
        if terrain == 'forest':
            resourceValues['prod'] = 3
            resourceValues['food'] = 1
        if terrain == 'snow':
            resourceValues['prod'] = 1
        if terrain == 'mountain':
            resourceValues['prod'] = 4
        return resourceValues


class PlayerMap(object):
    def __init__(self, owner, dimensions, buildings, units):
        self.owner = owner
        self.dimensions = dimensions
        self.buildings = buildings
        self.units = units
        self.updateMap()
    
    def updateMap(self):
        self.map = []
        for row in range(self.dimensions[0]):
            r = []
            for col in range(self.dimensions[1]):
                r.append(None)
            self.map.append(r)
        for player in Player.players:
            for building in player.buildings:
                self.map[building.loc[0]][building.loc[1]] = building
        for player in Player.players:
            for unit in player.units:
                self.map[unit.loc[0]][unit.loc[1]] = unit
        self.getVisibleTiles()
        self.getMovableTiles()
        self.getAttackableTiles()
    
    def getVisibleTiles(self):
        self.visibleTiles = []
        for row in range(self.dimensions[0]):
            r = []
            for col in range(self.dimensions[1]):
                r.append(False)
            self.visibleTiles.append(r)
        self.claimedTiles = []
        for row in range(self.dimensions[0]):
            r = []
            for col in range(self.dimensions[1]):
                r.append(False)
            self.claimedTiles.append(r)
        for unit in self.units:
            for (row, col) in unit.getVisibleTiles(self.dimensions):
                self.visibleTiles[row][col] = True
        for building in self.buildings:
            for (row, col) in building.getVisibleTiles(self.dimensions):
                self.visibleTiles[row][col] = True
                self.claimedTiles[row][col] = True

    def getMovableTiles(self):
        self.movableTiles = []
        for row in range(self.dimensions[0]):
            r = []
            for col in range(self.dimensions[1]):
                r.append(False)
            self.movableTiles.append(r)
        if self.owner.selectedUnit != None and self.owner.movingSelectedUnit:
            for (row, col) in self.owner.selectedUnit.getMovableTiles(self.dimensions):
                self.movableTiles[row][col] = True
    
    def getAttackableTiles(self):
        self.attackableTiles = []
        for row in range(self.dimensions[0]):
            r = []
            for col in range(self.dimensions[1]):
                r.append(False)
            self.attackableTiles.append(r)
        if self.owner.selectedUnit != None and self.owner.selectedUnitAttacking:
            for (row, col) in self.owner.selectedUnit.getAttackableTiles(self.dimensions):
                self.attackableTiles[row][col] = True
        
    def drawMap(self, app, canvas):
        self.updateMap()
        for row in range(self.dimensions[0]):
            for col in range(self.dimensions[1]):
                color = 'gray'
                outline = 'black'
                width = 1
                x0, y0, x1, y1 = getCellBounds(app, row, col)
                if self.visibleTiles[row][col]:
                    color = app.globalMap.getTerrainColor(row, col)
                if self.claimedTiles[row][col]:
                    outline = 'green'
                    width = 3
                if (self.owner.selectedUnit != None and [row, col] == self.owner.selectedUnit.loc) or (self.owner.selectedBuilding != None and [row, col] == self.owner.selectedBuilding.loc):
                    outline = 'yellow'
                    width = 3
                if self.movableTiles[row][col]:
                    outline = 'blue'
                    width = 5
                if self.attackableTiles[row][col]:
                    outline = 'red'
                    width = 5
                canvas.create_rectangle(x0, y0, x1, y1, fill = color, outline = outline, width = width)
                if self.map[row][col] != None and self.visibleTiles[row][col]:
                    self.map[row][col].draw(app, canvas)



class Player(object):
    players = []
    
    def __init__(self, dimensions):
        self.buildings = []
        self.units = [Settler(self, [random.randrange(0, dimensions[0]), random.randrange(0, dimensions[1])])]
        wardir = 1
        if self.units[0].loc[1] == dimensions[1] - 1:
            wardir = -1
        self.units.append(Warrior(self, [self.units[0].loc[0], self.units[0].loc[1] + wardir]))
        self.selectedUnit = None
        self.movingSelectedUnit = False
        self.selectedUnitAttacking = False
        self.selectedBuilding = None
        self.map = PlayerMap(self, dimensions, self.buildings, self.units)
        self.food = 0
        self.gold = 0
        self.prod = 0
        self.totalCitizens = 0
        self.fpt = 0
        self.gpt = 0
        self.ppt = 0
        Player.players.append(self)
    
    def allActionsTaken(self):
        res = True
        for unit in self.units:
            if unit.actionTaken == False:
                res = False
        for building in self.buildings:
            if building.actionTaken == False:
                if building.producingUnit != None:
                    continue
                res = False
        return res

    def updateResources(self, app):
        self.totalCitizens = 0
        self.fpt = 0
        self.gpt = 0
        self.ppt = 0
        for building in self.buildings:
            self.totalCitizens += building.citizens
            for tile in building.getVisibleTiles(self.map.dimensions):
                terrainType = app.globalMap.terrainMap[tile[0]][tile[1]][1]
                resourceValues = app.globalMap.getTerrainResources(terrainType)
                self.food += roundHalfUp(((building.citizens / 5) * resourceValues['food']))
                self.gold += roundHalfUp(((building.citizens / 5) * resourceValues['gold']))
                self.prod += roundHalfUp(((building.citizens / 5) * resourceValues['prod']))
                self.fpt += roundHalfUp(((building.citizens / 5) * resourceValues['food']))
                self.gpt += roundHalfUp(((building.citizens / 5) * resourceValues['gold']))
                self.ppt += roundHalfUp(((building.citizens / 5) * resourceValues['prod']))
        for building in self.buildings:
            building.checkProduction()
        self.food = max(0, self.food - 10 * self.totalCitizens)
        while self.food >= 2 ** self.totalCitizens:
            self.food -= 2 ** self.totalCitizens
            random.choice(self.buildings).citizens += 1
            self.totalCitizens += 1
        
    def nextTurn(self, app):
        self.updateResources(app)
        self.selectedUnit = None
        self.movingSelectedUnit = False
        self.selectedUnitAttacking = False
        self.selectedBuilding = None
        for unit in self.units:
            unit.actionTaken = False
            if isinstance(unit, Warrior) and unit.hp < 200:
                unit.hp = min(200, unit.hp + 20)
            if isinstance(unit, Archer) and unit.hp < 75:
                unit.hp = min(200, unit.hp + 10)
            if isinstance(unit, Settler) and unit.hp < 100:
                unit.hp = min(200, unit.hp + 15)
        # for building in self.buildings:
        #     building.actionTaken = False
        #     if building.hp < 500:
        #         building.hp = min(500, building.hp + 25)
        
    def drawInstructions(self, app, canvas):
        if self.allActionsTaken():
            canvas.create_text(app.width / 2, 80, text = 'all actions taken for this turn. press t to finish turn and switch to next player')
        else:
            canvas.create_text(app.width / 2, 80, text = 'there are available actions remaining. click on a unit or building to select it. press t to end turn early')
        if self.selectedUnit != None:
            canvas.create_text(app.width / 2, 20, text = f'selected unit: {self.selectedUnit}, hp = {self.selectedUnit.hp}, dmg = {self.selectedUnit.dmg}')
            self.selectedUnit.drawInstructions(app, canvas)
        elif self.selectedBuilding != None:
            canvas.create_text(app.width / 2, 20, text = f'selected building: {self.selectedBuilding}, hp = {self.selectedBuilding.hp}, dmg = {self.selectedBuilding.dmg}')
            self.selectedBuilding.drawInstructions(app, canvas)
    
    def drawResources(self, app, canvas):
        canvas.create_text(app.width - 110, 25, text = f'food = {self.food} (+{self.fpt} per turn)\ncitizens require {10 * self.totalCitizens} food per turn\n{2 ** self.totalCitizens} surplus food needed for growth')
        canvas.create_text(app.width - 140, 55, text = f'gold = {self.gold} (+{self.gpt} per turn)')
        canvas.create_text(app.width - 140, 70, text = f'prod = {self.prod} (+{self.ppt} per turn)')
        
        
class Unit(object):
    def __init__(self, owner, loc, moveRange, visRange, hp, dmg):
        self.owner = owner
        self.loc = loc
        self.moveRange = moveRange
        self.visRange = visRange
        self.actionTaken = False
        self.hp = hp
        self.dmg = dmg
    
    def getVisibleTiles(self, dimensions):
        allTiles = []
        for h in range(-self.visRange, self.visRange + 1):
            for v in range(-self.visRange, self.visRange + 1):
                if abs(h) + abs(v) <= self.visRange:
                    allTiles.append((self.loc[0] + h, self.loc[1] + v))
        visibleTiles = []
        for tile in allTiles:
            if not (tile[0] < 0 or tile[1] < 0 or tile[0] >= dimensions[0] or tile[1] >= dimensions[1]):
                visibleTiles.append(tile)
        return visibleTiles
    
    def getMovableTiles(self, dimensions):
        allTiles = []
        for h in range(-self.moveRange, self.moveRange + 1):
            for v in range(-self.moveRange, self.moveRange + 1):
                if abs(h) + abs(v) <= self.moveRange:
                    allTiles.append([self.loc[0] + h, self.loc[1] + v])
        movableTiles = []
        for tile in allTiles:
            if not (tile[0] < 0 or tile[1] < 0 or tile[0] >= dimensions[0] or tile[1] >= dimensions[1] or self.owner.map.map[tile[0]][tile[1]] != None):
                movableTiles.append(tile)
        return movableTiles
    
    def move(self, app, x, y):
        if (getCellClicked(app, x, y) in self.getMovableTiles(self.owner.map.dimensions)):
            self.owner.selectedUnit.loc = getCellClicked(app, x, y)
            self.owner.movingSelectedUnit = False
            self.actionTaken = True
    
    def checkHP(self):
        if self.hp <= 0:
            self.owner.units.remove(self)
            self.owner.selectedUnit = None
            return False

class Settler(Unit):
    def __init__(self, owner, loc):
        super().__init__(owner, loc, 2, 4, 100, 0)

    def __repr__(self):
        return 'Settler'
    
    def draw(self, app, canvas):
        x0, y0, x1, y1 = getCellBounds(app, self.loc[0], self.loc[1])
        canvas.create_oval(x0, y0, x1, y1, fill = 'green')
        if app.currentPlayer != self.owner:
            canvas.create_oval(x0, y0, x1, y1, fill = 'green', outline = 'red', width = 5)
    
    def settle(self):
        self.owner.buildings.append(City(self.owner, self.loc))
        self.owner.units.remove(self)
        self.owner.selectedBuilding = self.owner.buildings[-1]

    def drawInstructions(self, app, canvas):
        if self.owner.movingSelectedUnit:
            canvas.create_text(app.width / 2, 40, text = 'click a blue tile to move')
        else:
            if self.actionTaken:
               canvas.create_text(app.width / 2, 40, text = 'this settler has moved already this turn') 
            else:
                canvas.create_text(app.width / 2, 40, text = 'press m to move, s to settle (create a city)')

class Warrior(Unit):
    def __init__(self, owner, loc):
        super().__init__(owner, loc, 3, 3, 200, 30)
        self.attackRange = 1
    
    def __repr__(self):
        return 'Warrior'
    
    def draw(self, app, canvas):
        x0, y0, x1, y1 = getCellBounds(app, self.loc[0], self.loc[1])
        canvas.create_oval(x0, y0, x1, y1, fill = 'gray')
        if app.currentPlayer != self.owner:
            canvas.create_oval(x0, y0, x1, y1, fill = 'gray', outline = 'red', width = 5)
    
    def attack(self, app, x, y):
        if (getCellClicked(app, x, y) in self.getAttackableTiles(self.owner.map.dimensions)):
            attackloc = getCellClicked(app, x, y)
            if self.owner.map.map[attackloc[0]][attackloc[1]] != None:
                self.owner.map.map[attackloc[0]][attackloc[1]].hp -= self.dmg
                self.hp -= int(0.2 * self.owner.map.map[attackloc[0]][attackloc[1]].dmg)
                self.checkHP()
                self.owner.map.map[attackloc[0]][attackloc[1]].checkHP()
                if not self.owner.map.map[attackloc[0]][attackloc[1]].checkHP() and isinstance(self.owner.map.map[attackloc[0]][attackloc[1]], City):
                    self.owner.buildings.append(self.owner.map.map[attackloc[0]][attackloc[1]])
                self.owner.selectedUnitAttacking = False
                self.actionTaken = True

    def getAttackableTiles(self, dimensions):
        allTiles = []
        for h in range(-self.attackRange, self.attackRange + 1):
            for v in range(-self.attackRange, self.attackRange + 1):
                if abs(h) + abs(v) <= self.attackRange:
                    allTiles.append([self.loc[0] + h, self.loc[1] + v])
        attackableTiles = []
        for tile in allTiles:
            if not (tile[0] < 0 or tile[1] < 0 or tile[0] >= dimensions[0] or tile[1] >= dimensions[1]):
                attackableTiles.append(tile)
        return attackableTiles
        
    def drawInstructions(self, app, canvas):
        if self.owner.movingSelectedUnit:
            canvas.create_text(app.width / 2, 40, text = 'click a blue tile to move')
        elif self.owner.selectedUnitAttacking:
            canvas.create_text(app.width / 2, 40, text = 'click a red tile with an enemy unit or building to attack')
        else:
            if self.actionTaken:
               canvas.create_text(app.width / 2, 40, text = 'this warrior has acted already this turn') 
            else:
                canvas.create_text(app.width / 2, 40, text = 'press m to move, a to attack')

class Archer(Unit):
    def __init__(self, owner, loc):
        super().__init__(owner, loc, 100, 4, 75, 60)
        self.attackRange = 3
    
    def __repr__(self):
        return 'Archer'
    
    def draw(self, app, canvas):
        x0, y0, x1, y1 = getCellBounds(app, self.loc[0], self.loc[1])
        canvas.create_oval(x0, y0, x1, y1, fill = 'brown')
        if app.currentPlayer != self.owner:
            canvas.create_oval(x0, y0, x1, y1, fill = 'brown', outline = 'red', width = 5)
    
    def attack(self, app, x, y):
        if (getCellClicked(app, x, y) in self.getAttackableTiles(self.owner.map.dimensions)):
            attackloc = getCellClicked(app, x, y)
            if self.owner.map.map[attackloc[0]][attackloc[1]] != None:
                self.owner.map.map[attackloc[0]][attackloc[1]].hp -= self.dmg
                if not self.owner.map.map[attackloc[0]][attackloc[1]].checkHP() and isinstance(self.owner.map.map[attackloc[0]][attackloc[1]], City):
                    self.owner.buildings.append(self.owner.map.map[attackloc[0]][attackloc[1]])
                self.owner.selectedUnitAttacking = False
                self.actionTaken = True

    def getAttackableTiles(self, dimensions):
        allTiles = []
        for h in range(-self.attackRange, self.attackRange + 1):
            for v in range(-self.attackRange, self.attackRange + 1):
                if abs(h) + abs(v) <= self.attackRange:
                    allTiles.append([self.loc[0] + h, self.loc[1] + v])
        attackableTiles = []
        for tile in allTiles:
            if not (tile[0] < 0 or tile[1] < 0 or tile[0] >= dimensions[0] or tile[1] >= dimensions[1]):
                attackableTiles.append(tile)
        return attackableTiles
    
    def drawInstructions(self, app, canvas):
        if self.owner.movingSelectedUnit:
            canvas.create_text(app.width / 2, 40, text = 'click a blue tile to move')
        elif self.owner.selectedUnitAttacking:
            canvas.create_text(app.width / 2, 40, text = 'click a red tile with an enemy unit or building to attack')
        else:
            if self.actionTaken:
               canvas.create_text(app.width / 2, 40, text = 'this archer has acted already this turn') 
            else:
                canvas.create_text(app.width / 2, 40, text = 'press m to move, a to attack')

class City(object):
    def __init__(self, owner, loc):
        self.owner = owner
        self.loc = loc
        self.visRange = 4
        self.citizens = 1
        self.actionTaken = True
        self.producingUnit = None
        self.justFinished = False
        self.hp = 500
        self.dmg = 100
    
    def __repr__(self):
        return 'City'

    def draw(self, app, canvas):
        x0, y0, x1, y1 = getCellBounds(app, self.loc[0], self.loc[1])
        canvas.create_polygon(x0, y1, x0 + (0.5  * app.cellWidth), y0, x1, y1, fill = 'blue')
        if app.currentPlayer != self.owner:
            canvas.create_polygon(x0, y1, x0 + (0.5  * app.cellWidth), y0, x1, y1, fill = 'blue', outline = 'red', width = 5)
    
    def checkProduction(self):
        self.justFinished = False
        if self.producingUnit != None and self.owner.prod >= self.getUnitProdValue(repr(self.producingUnit)):
            self.owner.units.append(self.producingUnit)
            self.owner.prod -= self.getUnitProdValue(repr(self.producingUnit))
            self.producingUnit = None
            self.justFinished = True
    
    def getUnitProdValue(self, unit):
        val = 100
        if unit == 'Settler':
            val = 150
        if unit == 'Warrior':
            val = 100
        if unit == 'Archer':
            val = 75
        return val
    
    def checkHP(self):
        if self.hp <= 0:
            self.owner.buildings.remove(self)
            return False

    def getVisibleTiles(self, dimensions):
        allTiles = []
        for h in range(-self.visRange, self.visRange + 1):
            for v in range(-self.visRange, self.visRange + 1):
                if abs(h) + abs(v) <= self.visRange:
                    allTiles.append((self.loc[0] + h, self.loc[1] + v))
        visibleTiles = []
        for tile in allTiles:
            if not (tile[0] < 0 or tile[1] < 0 or tile[0] >= dimensions[0] or tile[1] >= dimensions[1]):
                visibleTiles.append(tile)
        return visibleTiles
    
    def drawInstructions(self, app, canvas):
        if self.actionTaken:
            if self.producingUnit != None:
                canvas.create_text(app.width / 2, 40, text = f'city cannot do anything else this turn, now producing {repr(self.producingUnit)}')
            else:
                canvas.create_text(app.width / 2, 40, text = 'city cannot do anything else this turn')
        elif self.producingUnit == None:
            canvas.create_text(app.width / 2, 40, text = 'press 1 to start producing a warrior, 2 to start producing an archer, 3 to start producing a settler')
        else:
            canvas.create_text(app.width / 2, 40, text = f'producing {self.producingUnit}, needs {(self.getUnitProdValue(repr(self.producingUnit)))} total production to finish')
        if self.justFinished:
            canvas.create_text(app.width / 2, 60, text = f'finished producing {self.owner.units[-1]}, spawned to the right of city')


def appStarted(app):
    app.rows = 30
    app.cols = 30
    app.cellWidth = 30
    app.cellHeight = 30
    app.margin = [(app.width - (app.rows * app.cellWidth)) / 2, (app.height - (app.cols * app.cellHeight))]
    app.mouseLoc = None
    app.players = [Player([app.rows, app.cols]), Player([app.rows, app.cols])]
    app.currentPlayer = app.players[0]
    app.globalMap = GlobalMap([app.rows, app.cols])
    app.turnCounter = 1
    app.gameOver = False

#CITATION: taken from past hw
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

def mouseDragged(app, event):
    app.margin[0] += event.x - app.mouseLoc[0]
    app.margin[1] += event.y - app.mouseLoc[1]
    app.mouseLoc = (event.x, event.y)

def mouseMoved(app, event):
    app.mouseLoc = [event.x, event.y]

def mousePressed(app, event):
    selected = False
    if app.currentPlayer.movingSelectedUnit:
        app.currentPlayer.selectedUnit.move(app, event.x, event.y)
    elif app.currentPlayer.selectedUnitAttacking:
        app.currentPlayer.selectedUnit.attack(app, event.x, event.y)
    else:
        for unit in app.currentPlayer.units:
            if unit.loc == getCellClicked(app, event.x, event.y):
                app.currentPlayer.selectedUnit = unit
                app.currentPlayer.selectedBuilding = None
                app.currentPlayer.movingSelectedUnit = False
                app.currentPlayer.selectedUnitAttacking = False
                selected = True
        for building in app.currentPlayer.buildings:
            if building.loc == getCellClicked(app, event.x, event.y):
                app.currentPlayer.selectedBuilding = building
                app.currentPlayer.selectedUnit = None
                selected = True
    if not selected and not app.currentPlayer.movingSelectedUnit and not app.currentPlayer.selectedUnitAttacking:
        app.currentPlayer.selectedUnit = None
        app.currentPlayer.selectedBuilding = None
    

def keyPressed(app, event):
    if event.key == 'r':
        appStarted(app)
    if event.key == '=':
        app.cellWidth += 5
        app.cellHeight += 5
        # app.margin = [(app.width - ((app.rows * app.cellWidth) + app.margin[0])) / 2, (app.height - ((app.cols * app.cellHeight) + app.margin[1])) / 2]
    if event.key == '-':
        app.cellWidth = max(app.cellWidth - 5, 10)
        app.cellHeight = max(app.cellHeight - 5, 10)
        # app.margin = [(app.width - ((app.rows * app.cellWidth) + app.margin[0])) / 2, (app.height - ((app.cols * app.cellHeight) + app.margin[1])) / 2]
    if event.key == '1':
        if isinstance(app.currentPlayer.selectedBuilding, City):
            app.currentPlayer.selectedBuilding.producingUnit = Warrior(app.currentPlayer, [app.currentPlayer.selectedBuilding.loc[0], app.currentPlayer.selectedBuilding.loc[1] + 1])
            app.currentPlayer.selectedBuilding.actionTaken = True
    if event.key == '2':
        if isinstance(app.currentPlayer.selectedBuilding, City):
            app.currentPlayer.selectedBuilding.producingUnit = Archer(app.currentPlayer, [app.currentPlayer.selectedBuilding.loc[0], app.currentPlayer.selectedBuilding.loc[1] + 1])
            app.currentPlayer.selectedBuilding.actionTaken = True
    if event.key == '3':
        if isinstance(app.currentPlayer.selectedBuilding, City):
            app.currentPlayer.selectedBuilding.producingUnit = Settler(app.currentPlayer, [app.currentPlayer.selectedBuilding.loc[0], app.currentPlayer.selectedBuilding.loc[1] + 1])
            app.currentPlayer.selectedBuilding.actionTaken = True
    if event.key == 'm':
        if app.currentPlayer.selectedUnit != None and not app.currentPlayer.selectedUnit.actionTaken:
            app.currentPlayer.movingSelectedUnit = not app.currentPlayer.movingSelectedUnit
            app.currentPlayer.selectedUnitAttacking = False
    if event.key == 'a':
        if app.currentPlayer.selectedUnit != None and not app.currentPlayer.selectedUnit.actionTaken:
            app.currentPlayer.selectedUnitAttacking = not app.currentPlayer.selectedUnitAttacking
            app.currentPlayer.movingSelectedUnit = False
    if event.key == 's':
        if isinstance(app.currentPlayer.selectedUnit, Settler):
            app.currentPlayer.selectedUnit.settle()
            app.currentPlayer.selectedUnit = None
    if event.key == 'n':
        app.currentPlayer.units.append(Warrior(app.currentPlayer, [random.randrange(0, app.currentPlayer.map.dimensions[0]), random.randrange(0, app.currentPlayer.map.dimensions[1])]))
    if event.key == 't':
        app.currentPlayer.nextTurn(app)
        if app.players.index(app.currentPlayer) == len(app.players) - 1:
            app.turnCounter += 1
        checkForWin(app)
        if app.gameOver:
            return
        app.currentPlayer = app.players[(app.players.index(app.currentPlayer) + 1) % len(app.players)]

def checkForWin(app):
    for player in app.players:
        if player.buildings == [] and player.units == []:
            app.gameOver = True

def getCellClicked(app, x, y):
    if x < app.margin[0] or x > (app.width - app.margin[0]) or y < app.margin[1] or y > (app.height - app.margin[1]):
        return None
    row = (y - app.margin[1]) // app.cellHeight
    col = (x - app.margin[0]) // app.cellWidth
    return [int(row), int(col)]

def redrawAll(app, canvas):
    app.currentPlayer.map.drawMap(app, canvas)
    canvas.create_rectangle(0, 0, app.width, 90, fill = 'white')
    if app.gameOver:
        canvas.create_text(app.width / 2, 40, text = f'game over! player {app.players.index(app.currentPlayer) + 1} wins!')
    else:
        drawTurnAndPlayer(app, canvas)
        app.currentPlayer.drawInstructions(app, canvas)
        app.currentPlayer.drawResources(app, canvas)

def drawTurnAndPlayer(app, canvas):
    canvas.create_text(80, 30, text = f'turn: {app.turnCounter}')
    canvas.create_text(80, 50, text = f'player: {app.players.index(app.currentPlayer) + 1}')

def getCellBounds(app, row, col):
    x0 = app.margin[0] + (col * app.cellWidth)
    y0 = app.margin[1] + (row * app.cellHeight)
    x1 = app.margin[0] + ((col + 1) * app.cellWidth)
    y1 = app.margin[1] + ((row + 1) * app.cellHeight)
    return x0, y0, x1, y1


def main():
    runApp(width = 1000, height = 1000)

if __name__ == '__main__':
    main()