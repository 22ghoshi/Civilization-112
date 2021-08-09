import math, copy, random

from cmu_112_graphics import *

class Map(object):
    def __init__(self, dimensions, buildings, units):
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
    
    def getVisibleTiles(self):
        self.visibleTiles = []
        for row in range(self.dimensions[0]):
            r = []
            for col in range(self.dimensions[1]):
                r.append(False)
            self.visibleTiles.append(r)
        
    def drawMap(self, app, canvas):
        for row in range(self.dimensions[0]):
            for col in range(self.dimensions[1]):
                color = 'gray'
                outline = 'black'
                x0, y0, x1, y1 = getCellBounds(app, row, col)
                for unit in self.units:
                    if (row, col) in unit.getVisibleTiles():
                        color = 'white'
                for building in self.buildings:
                    if (row, col) in building.getVisibleTiles():
                        color = 'white'
                        outline = 'green'
                canvas.create_rectangle(x0, y0, x1, y1, fill = color, outline = outline)
                if self.map[row][col] != None:
                    self.map[row][col].draw(app, canvas)



class Player(object):
    def __init__(self, dimensions):
        self.buildings = []
        self.units = [Settler(self, [random.randrange(0, dimensions[0]), random.randrange(0, dimensions[1])])]
        self.map = Map(dimensions, self.buildings, self.units)
        
class Unit(object):
    def __init__(self, owner, loc):
        self.owner = owner
        self.loc = loc
        self.visRange = 3

class Settler(Unit):
    def __init__(self, owner, loc):
        super().__init__(owner, loc)
    
    def draw(self, app, canvas):
        x0, y0, x1, y1 = getCellBounds(app, self.loc[0], self.loc[1])
        canvas.create_oval(x0, y0, x1, y1, fill = 'green')
    
    def getVisibleTiles(self):
        visibleTiles = []
        for h in range(-self.visRange, self.visRange + 1):
            for v in range(-self.visRange, self.visRange + 1):
                if abs(h) + abs(v) <= self.visRange:
                    visibleTiles.append((self.loc[0] + h, self.loc[1] + v))
        return visibleTiles
    
    def settle(self):
        self.owner.buildings.append(City(self.owner, self.loc))
        self.owner.units.remove(self)
        self.owner.map.updateMap()

class City(object):
    def __init__(self, owner, loc):
        self.owner = owner
        self.loc = loc
        self.visRange = 5
        self.citizens = 1

    def draw(self, app, canvas):
        x0, y0, x1, y1 = getCellBounds(app, self.loc[0], self.loc[1])
        canvas.create_polygon(x0, y1, x0 + (0.5  * app.cellWidth), y0, x1, y1, fill = 'blue')
    
    def getVisibleTiles(self):
        visibleTiles = []
        for h in range(-self.visRange, self.visRange + 1):
            for v in range(-self.visRange, self.visRange + 1):
                if abs(h) + abs(v) <= self.visRange:
                    visibleTiles.append((self.loc[0] + h, self.loc[1] + v))
        return visibleTiles

def appStarted(app):
    app.rows = 15
    app.cols = 15
    app.cellWidth = 50
    app.cellHeight = 50
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
    if len(app.player.units) > 0: app.player.units[0].settle()

def redrawAll(app, canvas):
    app.player.map.drawMap(app, canvas)

def getCellBounds(app, row, col):
    x0 = app.margin[0] + (col * app.cellWidth)
    y0 = app.margin[1] + (row * app.cellHeight)
    x1 = app.margin[0] + ((col + 1) * app.cellWidth)
    y1 = app.margin[1] + ((row + 1) * app.cellHeight)
    return x0, y0, x1, y1


def main():
    runApp(width = 800, height = 800)

if __name__ == '__main__':
    main()