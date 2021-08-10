import math, copy, random

from cmu_112_graphics import *

# CITATION: idea / pseudocode for map generation algorithm obtained from https://ijdykeman.github.io/ml/2017/10/12/wang-tile-procedural-generation.html
class GlobalMap(object):
    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.terrainTypes = ['ocean', 'lake', 'sand', 'plain', 'forest', 'snow', 'mountain']
        self.initTerrainMap(dimensions)
        self.generateTerrain(dimensions)
    
    def initTerrainMap(self, dimensions):
        terrainMapTypes = [False, 'ocean', 'lake', 'sand', 'plain', 'forest', 'snow', 'mountain']
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
        while not self.fullTerrain(dimensions): #not self.fullTerrain(dimensions)
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
                self.terrainMap[arow][acol] = [False, 'ocean', 'lake', 'sand', 'plain', 'forest', 'snow', 'mountain']
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
                        self.terrainMap[arow][acol].remove(tileType)
    
    def getTerrainColor(self, app, row, col):
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
        
    def drawMap(self, app, canvas):
        self.updateMap()
        for row in range(self.dimensions[0]):
            for col in range(self.dimensions[1]):
                color = 'gray'
                outline = 'black'
                width = 1
                x0, y0, x1, y1 = getCellBounds(app, row, col)
                if self.visibleTiles[row][col]:
                    color = app.globalMap.getTerrainColor(app, row, col)
                if self.claimedTiles[row][col]:
                    outline = 'green'
                    width = 3
                if self.owner.selectedUnit != None and [row, col] == self.owner.selectedUnit.loc:
                    outline = 'yellow'
                    width = 3
                if self.movableTiles[row][col]:
                    outline = 'blue'
                    width = 5
                canvas.create_rectangle(x0, y0, x1, y1, fill = color, outline = outline, width = width)
                if self.map[row][col] != None and self.visibleTiles[row][col]:
                    self.map[row][col].draw(app, canvas)



class Player(object):
    players = []
    
    def __init__(self, dimensions):
        self.buildings = []
        self.units = [Settler(self, [random.randrange(0, dimensions[0]), random.randrange(0, dimensions[1])])]
        self.selectedUnit = None
        self.movingSelectedUnit = False
        self.map = PlayerMap(self, dimensions, self.buildings, self.units)
        Player.players.append(self)
    
    def drawInstructions(self, app, canvas):
        if self.selectedUnit != None:
            self.selectedUnit.drawInstructions(app, canvas)
        else:
            canvas.create_text(app.width / 2, 20, text = 'click on a unit to select it. press n for a new settler')
        
        
class Unit(object):
    def __init__(self, owner, loc, moveRange, visRange):
        self.owner = owner
        self.loc = loc
        self.moveRange = moveRange
        self.visRange = visRange

class Settler(Unit):
    def __init__(self, owner, loc):
        super().__init__(owner, loc, 3, 4)
    
    def draw(self, app, canvas):
        x0, y0, x1, y1 = getCellBounds(app, self.loc[0], self.loc[1])
        canvas.create_oval(x0, y0, x1, y1, fill = 'green')
        if app.currentPlayer != self.owner:
            canvas.create_oval(x0, y0, x1, y1, fill = 'green', outline = 'red', width = 5)
    
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
    
    def settle(self):
        self.owner.buildings.append(City(self.owner, self.loc))
        self.owner.units.remove(self)
    
    def drawInstructions(self, app, canvas):
        if self.owner.movingSelectedUnit:
            canvas.create_text(app.width / 2, 20, text = 'click a blue tile to move')
        else:
            canvas.create_text(app.width / 2, 20, text = 'press m to move, s to settle')

class City(object):
    def __init__(self, owner, loc):
        self.owner = owner
        self.loc = loc
        self.visRange = 5
        self.citizens = 1

    def draw(self, app, canvas):
        x0, y0, x1, y1 = getCellBounds(app, self.loc[0], self.loc[1])
        canvas.create_polygon(x0, y1, x0 + (0.5  * app.cellWidth), y0, x1, y1, fill = 'blue')
    
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

def appStarted(app):
    app.rows = 30
    app.cols = 30
    app.cellWidth = 30
    app.cellHeight = 30
    app.margin = [(app.width - (app.rows * app.cellWidth)) / 2, (app.height - (app.cols * app.cellHeight)) / 2]
    app.mouseLoc = None
    app.players = [Player([app.rows, app.cols]), Player([app.rows, app.cols])]
    app.currentPlayer = app.players[0]
    app.globalMap = GlobalMap([app.rows, app.cols])

def mouseDragged(app, event):
    app.margin[0] += event.x - app.mouseLoc[0]
    app.margin[1] += event.y - app.mouseLoc[1]
    app.mouseLoc = (event.x, event.y)

def mouseMoved(app, event):
    app.mouseLoc = [event.x, event.y]

def mousePressed(app, event):
    selected = False
    for unit in app.currentPlayer.units:
        if unit.loc == getCellClicked(app, event.x, event.y):
            app.currentPlayer.selectedUnit = unit
            selected = True
    if not selected and not app.currentPlayer.movingSelectedUnit:
        app.currentPlayer.selectedUnit = None
    if app.currentPlayer.movingSelectedUnit:
        if (getCellClicked(app, event.x, event.y) in app.currentPlayer.selectedUnit.getMovableTiles(app.currentPlayer.map.dimensions)):
            app.currentPlayer.selectedUnit.loc = getCellClicked(app, event.x, event.y)
            app.currentPlayer.movingSelectedUnit = False
    

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
    if event.key == '0':
        app.currentPlayer = app.players[0]
    if event.key == '1':
        app.currentPlayer = app.players[1]
    if event.key == 'm':
        if app.currentPlayer.selectedUnit != None:
            app.currentPlayer.movingSelectedUnit = not app.currentPlayer.movingSelectedUnit
    if event.key == 's':
        if isinstance(app.currentPlayer.selectedUnit, Settler):
            app.currentPlayer.selectedUnit.settle()
            app.currentPlayer.selectedUnit = None
    if event.key == 'n':
        app.currentPlayer.units.append(Settler(app.currentPlayer, [random.randrange(0, app.currentPlayer.map.dimensions[0]), random.randrange(0, app.currentPlayer.map.dimensions[1])]))
            
def getCellClicked(app, x, y):
    if x < app.margin[0] or x > (app.width - app.margin[0]) or y < app.margin[1] or y > (app.height - app.margin[1]):
        return None
    row = (y - app.margin[1]) // app.cellHeight
    col = (x - app.margin[0]) // app.cellWidth
    return [int(row), int(col)]

def redrawAll(app, canvas):
    app.currentPlayer.map.drawMap(app, canvas)
    app.currentPlayer.drawInstructions(app, canvas)

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