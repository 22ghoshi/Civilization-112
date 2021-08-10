import math, copy, random

from cmu_112_graphics import *

class Map(object):
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
        for building in self.buildings:
            self.map[building.loc[0]][building.loc[1]] = building
        for unit in self.units:
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
                    color = 'white'
                if self.claimedTiles[row][col]:
                    outline = 'green'
                    width = 3
                if self.owner.selectedUnit != None and [row, col] == self.owner.selectedUnit.loc:
                    color = 'yellow'
                if self.movableTiles[row][col]:
                    outline = 'blue'
                    width = 5
                canvas.create_rectangle(x0, y0, x1, y1, fill = color, outline = outline, width = width)
                if self.map[row][col] != None:
                    self.map[row][col].draw(app, canvas)



class Player(object):
    def __init__(self, dimensions):
        self.buildings = []
        self.units = [Settler(self, [random.randrange(0, dimensions[0]), random.randrange(0, dimensions[1])])]
        self.selectedUnit = None
        self.movingSelectedUnit = False
        self.map = Map(self, dimensions, self.buildings, self.units)
    
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
    app.player = Player([app.rows, app.cols])

def mouseDragged(app, event):
    app.margin[0] += event.x - app.mouseLoc[0]
    app.margin[1] += event.y - app.mouseLoc[1]
    app.mouseLoc = (event.x, event.y)

def mouseMoved(app, event):
    app.mouseLoc = [event.x, event.y]

def mousePressed(app, event):
    selected = False
    for unit in app.player.units:
        if unit.loc == getCellClicked(app, event.x, event.y):
            app.player.selectedUnit = unit
            selected = True
    if not selected and not app.player.movingSelectedUnit:
        app.player.selectedUnit = None
    if app.player.movingSelectedUnit:
        if (getCellClicked(app, event.x, event.y) in app.player.selectedUnit.getMovableTiles(app.player.map.dimensions)):
            app.player.selectedUnit.loc = getCellClicked(app, event.x, event.y)
            app.player.movingSelectedUnit = False
    

def keyPressed(app, event):
    if event.key == 'm':
        if app.player.selectedUnit != None:
            app.player.movingSelectedUnit = not app.player.movingSelectedUnit
    if event.key == 's':
        if isinstance(app.player.selectedUnit, Settler):
            app.player.selectedUnit.settle()
            app.player.selectedUnit = None
    if event.key == 'n':
        app.player.units.append(Settler(app.player, [random.randrange(0, app.player.map.dimensions[0]), random.randrange(0, app.player.map.dimensions[1])]))
            
def getCellClicked(app, x, y):
    if x < app.margin[0] or x > (app.width - app.margin[0]) or y < app.margin[1] or y > (app.height - app.margin[1]):
        return None
    row = (y - app.margin[1]) // app.cellHeight
    col = (x - app.margin[0]) // app.cellWidth
    return [int(row), int(col)]

def redrawAll(app, canvas):
    app.player.map.drawMap(app, canvas)
    app.player.drawInstructions(app, canvas)

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