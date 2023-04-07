from cmu_cs3_graphics import *
import math
import random
import numpy as np
import copy

########
#Citation:
#The refrence for Raycasting part is the thought in 3D mini lecture
#Also I checked this page for my 2D maths:
#https://permadi.com/1996/05/ray-casting-tutorial-7/
#And for the maze generation, it thoughts come from the "Tp guide on mazes" in 15-112 website 

def onAppStart(app):
    app.gameStarted = False
    app.hint_2D = False
    app.hint_2DTimer = 0
    app.mazeHint = False
    app.mazeHintTimer = 0
    app.optionStarted = False
    app.levelClicked1 = False
    app.levelClicked2 = False
    app.mazeClicked1 = False
    app.mazeClicked2 = False
    app.passGame = False
    app.passTimer = 0
    app.lifeTimer = 0
    app.gameOver = False
    app.gameOverTimer = 0
    app.rows = gameDimensions(app)[0]
    app.cols = gameDimensions(app)[1]

    app.cellSize = gameDimensions(app)[2]
    app.margin = gameDimensions(app)[3]
    app.colorList = colorListGeneration(app)
    app.hintColorList = hintColorListGeneration(app)
    app.playerPosition = [32,32]
    app.playerRadius = 2
    app.moveStep = 1
    app.playerFacingAngle = 270
    app.stepsPerSecond = 100
    app.time = 0
    app.manTimer = 0
    

def onStep(app):
    
    if app.gameStarted == False:
        app.manTimer += 0.2
    elif app.gameStarted == True:
        app.time += 1
        app.lifeTimer += 0.01
        if app.hint_2D == True:
            app.hint_2DTimer += 0.25
            if app.hint_2DTimer == 5:
                app.hint_2D = False
                app.hint_2DTimer = 0
            if app.hint_2D == True & app.mazeHint == True:
                app.mazeHintTimer += 0.5
                if app.mazeHintTimer == 5:
                    app.mazeHint = False
                    app.mazeHintTimer = 0
    if (app.margin + (app.cols-2) * app.cellSize) < app.playerPosition[0] < \
    (app.margin + (app.cols-1) * app.cellSize) and \
    (app.margin + (app.rows-2) * app.cellSize) < app.playerPosition[1] < \
    (app.margin + (app.rows-1) * app.cellSize):
        app.gameStarted = False
        app.optionStarted = False
        app.passGame = True
    if app.passGame == True:
        app.passTimer += 0.5
    if app.lifeTimer > 1:
        app.gameStarted = False
        app.hint_2D = False
        app.optionStarted = False
        app.gameOver = True
        if app.gameOver == True:
            app.gameOverTimer += 0.2

def onMousePress(app,mouseX,mouseY):
    if 120 < mouseX < 420 and 465 < mouseY < 585:
        app.optionStarted = True
        # app.gameStarted = True
    if app.optionStarted == True:
        if 250 < mouseX < 350 and 175 < mouseY < 225:
            app.levelClicked1 = True
            app.levelClicked2 = False
            
            app.rows = gameDimensions(app)[0]
            app.cols = gameDimensions(app)[1]
            app.colorList = colorListGeneration(app)
            app.hintColorList = hintColorListGeneration(app)
            # app.colorList,app.hintColorList = colorListGeneration(app)
        elif 550 < mouseX < 650 and 175 < mouseY < 225:
            app.levelClicked2 = True
            app.levelClicked1 = False
            
            app.rows = gameDimensions(app)[0]
            app.cols = gameDimensions(app)[1]
            app.colorList = colorListGeneration(app)
            app.hintColorList = hintColorListGeneration(app)
            # app.colorList,app.hintColorList = colorListGeneration(app)
        if 250 < mouseX < 350 and 375 < mouseY < 425:
            app.mazeClicked1 = True
            app.mazeClicked2 = False
            app.colorList = colorListGeneration(app)
            app.hintColorList = hintColorListGeneration(app)   
        elif 550 < mouseX < 650 and 375 < mouseY < 425:
            app.mazeClicked2 = True
            app.mazeClicked1 = False
            app.colorList = dFScolorListGeneration(app)
            app.hintColorList = hintColorListGeneration(app)  
        if (app.levelClicked1 == True or app.levelClicked2 == True) and \
            (app.mazeClicked1 == True or app.mazeClicked2 == True) and \
            400 < mouseX < 500 and  475 < mouseY < 525:
            app.gameStarted = True
            
                        
    if app.gameStarted == True:
        if 800 < mouseX < 850 and 50 < mouseY < 80:
            app.hint_2D = True
        if 700 < mouseX < 780 and 50 < mouseY < 80:
            app.mazeHint = True

def onKeyPress(app,key):
    rad = math.radians(app.playerFacingAngle)
    if key == 'w':
        (dX,dY)=(+math.cos(rad)*app.moveStep,-math.sin(rad)*app.moveStep)
        playerMove(app,dX,dY)
    elif key == 's':
        (dX,dY)=(-math.cos(rad)*app.moveStep,+math.sin(rad)*app.moveStep)
        playerMove(app,dX,dY)
    elif key == 'a':
        app.playerFacingAngle += 10
    elif key == 'd':
        app.playerFacingAngle -= 10

def moveLegal(app,centreX,centreY):
    wallset = wallGeneration(app)
    for (i,j) in wallset:
        topI = app.margin + i * app.cellSize
        topJ = app.margin + j * app.cellSize
        bottomI = app.margin + (i + 1) * app.cellSize 
        bottomJ = app.margin + (j + 1) * app.cellSize
        if (topI <= (centreY - app.playerRadius) <= bottomI and \
            topJ <= (centreX - app.playerRadius) <= bottomJ) or \
            (topI <= (centreY + app.playerRadius) <= bottomI and \
            topJ <= (centreX + app.playerRadius) <= bottomJ):
            return False
    return True

def playerMove(app,dX,dY):
    app.playerPosition[0] += dX
    app.playerPosition[1] += dY
    if moveLegal(app,app.playerPosition[0],app.playerPosition[1]) == False:
        app.playerPosition[0] -= dX
        app.playerPosition[1] -= dY

#Raycasting Part
####################

#these two functions calculate the first intersection of the line with the grid
#horizontally and vertically
def rayCastingHorizontal_Initial(app,angle,centreX,centreY):
    rad=math.radians(angle)
    if 0 < angle % 360 < 180:
        rowNum = math.floor((centreY - app.margin)/app.cellSize)
        initialDY = (app.margin + rowNum * app.cellSize) - centreY
        initialDX = - initialDY / math.tan(rad)
        return (initialDX,initialDY)
    elif 180 < angle % 360 < 360:
        rowNum = math.ceil((centreY - app.margin)/app.cellSize)
        initialDY = (app.margin + rowNum * app.cellSize) - centreY
        initialDX = - initialDY / math.tan(rad)
        return (initialDX,initialDY)
    elif angle % 360 == 0:
        colNum = math.ceil((centreX - app.margin) / app.cellSize)
        initialDY = 0
        initialDX = (app.margin + colNum * app.cellSize) - centreX
        return (initialDX,initialDY)
    elif angle % 360 == 180:
        colNum = math.floor((centreX - app.margin)/app.cellSize)
        initialDX = (app.margin + colNum * app.cellSize) - centreX
        initialDY = 0
        return (initialDX,initialDY)

def rayCastingVertical_Initial(app,angle,centreX,centreY):
    rad=math.radians(angle)
    if 0 <= angle % 360 < 90:
        colNum = math.ceil((centreX - app.margin) / app.cellSize)
        initialDX = (app.margin + colNum * app.cellSize) - centreX
        initialDY = - initialDX * math.tan(rad)
        return (initialDX,initialDY)
    elif 90 < angle % 360 < 180:
        colNum = math.floor((centreX - app.margin)/app.cellSize)
        initialDX = (app.margin + colNum * app.cellSize) - centreX
        initialDY = - initialDX * math.tan(rad)
        return (initialDX,initialDY)
    elif 180<= angle % 360 < 270:
        colNum = math.floor((centreX - app.margin)/app.cellSize)
        initialDX = (app.margin + colNum * app.cellSize) - centreX
        initialDY = - initialDX * math.tan(rad)
        return (initialDX,initialDY)
    elif 270< angle % 360 < 360:
        colNum = math.ceil((centreX - app.margin) / app.cellSize)
        initialDX = (app.margin + colNum * app.cellSize) - centreX
        initialDY = - initialDX * math.tan(rad)
        return (initialDX,initialDY)
    elif angle % 360 == 90:
        initialDX = 0
        rowNum = math.floor((centreY - app.margin)/app.cellSize)
        initialDY = (app.margin + rowNum * app.cellSize) - centreY
        return (initialDX,initialDY)
    elif angle % 360 == 270:
        initialDX = 0
        rowNum = math.ceil((centreY - app.margin)/app.cellSize)
        initialDY = (app.margin + rowNum * app.cellSize) - centreY
        return (initialDX,initialDY)

#these two functions calculate the #unit# intersection of the line with the grid
#horizontally and vertically
def rayCastingHorizontalUnit(app,angle):
    rad=math.radians(angle)
    unit = app.cellSize/2
    if 0 < angle % 360 < 180:
        unitX = unit/math.tan(rad)
        unitY = -unit
        return (unitX,unitY)
    elif 180 < angle % 360 < 360:
        unitX = - unit/math.tan(rad)
        unitY = unit
        return (unitX,unitY)
    elif angle % 360 == 0:
        unitX = unit
        unitY = 0
        return (unitX,unitY)
    elif angle % 360 == 180:
        unitX = - unit
        unitY = 0
        return (unitX,unitY)


def rayCastingVerticalUnit(app,angle):
    rad=math.radians(angle)
    unit = app.cellSize/2
    if 0 <= angle % 360 < 90:
        unitX = unit
        unitY = - unit * math.tan(rad)
        return (unitX,unitY)
    elif 90 <= angle % 360 < 180:
        unitX = - unit
        unitY = unit * math.tan(rad)
        return (unitX,unitY)
    elif 180 <= angle % 360 < 270:
        unitX = -unit
        unitY = unit * math.tan(rad)
        return (unitX,unitY)
    elif 270 <= angle % 360 < 360:
        unitX = unit
        unitY = - unit * math.tan(rad)
        return (unitX,unitY)

def rayCastingLineWrapper_Horizontal(app,x,y,angle,centreX,centreY,dX,dY):
#helper function for rayCasting intersects with horizontal grid lines recursion   
    distance = math.sqrt((x-centreX)**2 + (y-centreY)**2)
    if hitWall(app,x,y)[0] == True:
        return [(x,y),distance]
    elif x<app.margin or x>app.margin+app.cols*app.cellSize or y<app.margin \
        or y>app.margin+app.rows*app.cellSize:
        return [(x,y),distance]
    else:
        x+=2*dX
        y+=2*dY
        return rayCastingLineWrapper_Horizontal(app,x,y,angle,centreX,centreY,
        dX,dY)

def rayCastingLineWrapper_Vertical(app,x,y,angle,centreX,centreY,dX,dY):
#helper function for rayCasting intersects with horizontal grid lines recursion
    distance = math.sqrt((x-centreX)**2 + (y-centreY)**2)
    if hitWall(app,x,y)[0] == True:
        return [(x,y),distance]
    elif x<app.margin or x>app.margin+app.cols*app.cellSize or y<app.margin \
        or y>app.margin+app.rows*app.cellSize:
        return [(x,y),distance]
    else:
        x+=2*dX
        y+=2*dY
        return rayCastingLineWrapper_Vertical(app,x,y,angle,centreX,centreY,
        dX,dY)
    
def rayCastingLine(app,angle):
    centreX = app.playerPosition[0]
    centreY = app.playerPosition[1]
    
    (horizontalDX,horizontalDY) = rayCastingHorizontalUnit(app,angle)
    (verticalDX,verticalDY) = rayCastingVerticalUnit(app,angle)

    (horizontal_Initial_DX,horizontal_Initial_DY) = \
    rayCastingHorizontal_Initial(app,angle,centreX,centreY)
    (vertical_Initial_DX,vertical_Initial_DY) = \
    rayCastingVertical_Initial(app,angle,centreX,centreY)

    (horizontalDX,horizontalDy) = rayCastingHorizontalUnit(app,angle)
    (verticalDX,verticalDY) = rayCastingVerticalUnit(app,angle)

    horInitialX,horInitialY = (centreX+horizontal_Initial_DX,
    centreY+horizontal_Initial_DY)
    verInitialX,verInitialY = (centreX+vertical_Initial_DX,
    centreY+vertical_Initial_DY)

    [(hX,hY),distanceH] = rayCastingLineWrapper_Horizontal(app,horInitialX,
    horInitialY,angle,centreX,centreY,horizontalDX,horizontalDY)
    [(vX,vY),distanceV] = rayCastingLineWrapper_Vertical(app,verInitialX,
    verInitialY,angle,centreX,centreY,verticalDX,verticalDY)

    if distanceH < distanceV:
        return [(hX,hY),distanceH,'H']
    elif distanceV <= distanceH:
        return [(vX,vY),distanceV,'V']
    # elif distanceH == distanceV:
    #     if angle % 360 == 90 or angle % 360 == 270:
    #         return [(hX,hY),distanceH,'H']
    #     elif angle % 360 == 180 or angle % 360 == 0:
    #         return [(vX,vY),distanceV,'V']


def hitWall(app,x,y):
    wallset = wallGeneration(app)
    for (i,j) in wallset:
        topI = app.margin + i * app.cellSize
        topJ = app.margin + j * app.cellSize
        bottomI = app.margin + (i + 1) * app.cellSize 
        bottomJ = app.margin + (j + 1) * app.cellSize
        if topJ<= x <= bottomJ and topI<= y <= bottomI:
            color = app.colorList[i][j]
            return [True,color]
    return [False,None]


#Fun Part! Some Animation~
#########

#####Kruskal Maze generation
###########
def initialPathGeneration(app):
    initialPath = list()
    mazeList = list()
    move = [(+1,0),(-1,0),(0,+1),(0,-1)]
    rows = (app.rows-1)//2
    cols = (app.cols-1)//2
    for i in range(rows):
        mazeList.append([]*cols)
    
    for i in range(rows):
        for j in range(cols):
            for (drow,dcol) in move:
                if 0 <= i+dcol < rows and 0 <= j+drow < cols:
                    if ((i,j),(i+dcol,j+drow)) not in initialPath \
                        and ((i+dcol,j+drow),(i,j)) not in initialPath:
                        initialPath.append(((i,j),(i+dcol,j+drow)))
    randomPath = random.sample(initialPath,len(initialPath))
    presentPath = []
    for ((a,b),(c,d)) in randomPath:
        previousPath = []
        if isConnectTest(app,a,b,c,d,presentPath,previousPath) != True:
            if ((a,b),(c,d)) not in presentPath:
                presentPath.append(((a,b),(c,d))) 
    return presentPath 
      
def isConnectTest(app,a,b,c,d,presentPath,previousPath):
    if len(presentPath) == 0:
        return None
    if a == c and b == d:
        return True
    else:
        for move in [(+1,0),(-1,0),(0,+1),(0,-1)]:
            drow,dcol = move
            newRow,newCol = a+drow,b+dcol
            if legalCheck1(app,newRow,newCol) == True and \
                (((a,b),(newRow,newCol)) in presentPath or \
                ((newRow,newCol),(a,b)) in presentPath) and \
                ((a,b),(newRow,newCol)) not in previousPath and \
                ((newRow,newCol),(a,b)) not in previousPath:
                previousPath.append(((a,b),(newRow,newCol)))
                solution = isConnectTest(app,newRow,newCol,c,d, presentPath,
                previousPath)
                if solution != None:
                    return solution
        return None

def legalCheck1(app,newRow,newCol):
    rows = (app.rows-1)//2
    cols = (app.cols-1)//2
    if 0 <= newRow < rows and 0 <= newCol < cols:
        return True

#DFS maze generation
#############

def dFSmazePathGeneration(app):
    pointList = []
    for i in range((app.rows-1)//2):
        for j in range((app.cols-1)//2):
            pointList.append(((2*i+1),(2*j+1)))
    curRow,curCol = 1,1
    curList = [(1,1)]
    whiteCellList = [(1,1)]
    return dFS_wrapper(app,pointList,curRow,curCol,curList,whiteCellList )

def dFS_wrapper(app,pointList,curRow,curCol,curList,whiteCellList):
    if len(curList) == len(pointList):
        return whiteCellList 
    else:
        moveset = [(-2,0),(0,+2),(0,-2),(+2,0)]
        for move in moveset:
            drow,dcol = move
            newRow,newCol = curRow+drow,curCol+dcol
            if legalCheck2(app,newRow,newCol,curList)==True:
                if newRow == curRow:
                    whiteCellList.append((newRow,newCol))
                    whiteCellList.append((curRow,(curCol+newCol)//2))
                    curRow,curCol = newRow,newCol
                    curList.append((curRow,curCol))
                elif newCol == curCol:
                    whiteCellList.append((newRow,newCol))
                    whiteCellList.append(((curRow+newRow)//2,curCol))
                    curRow,curCol = newRow,newCol
                    curList.append((curRow,curCol))
                    
                possibleSolution = dFS_wrapper(app,pointList,curRow,\
                    curCol,curList,whiteCellList )
                if possibleSolution != None:
                    return possibleSolution
                whiteCellList.pop()
                whiteCellList.pop()
                curList.pop()
        return None        

def legalCheck2(app,newRow,newCol,curList):
    if newRow%2 == 1 and newCol%2 == 1 and 1 <= newRow <app.rows and \
        1 <= newCol <app.cols and (newRow,newCol) not in curList:
        return True
    return False    

def dFSgridGeneration(app):
    gridList = []
    for i in range(app.rows):
        gridList.append(['grey']*app.cols)
    whiteCellList = dFSmazePathGeneration(app)
    print('white:',whiteCellList)
    for (x,y) in whiteCellList:
        gridList[x][y] = 'white'
        print((x,y))
        print('!!!',gridList)
    return gridList

#Maze solver
############

def mazeHint(app):
    gridList = app.colorList
    print(gridList)
    row = 1
    col = 1
    hintList = [(row,col)]
    previousList = [(row,col)]
    # print(mazeHint_Wrapper(app,row,col,hintList,gridList,previousList))
    return(mazeHint_Wrapper(app,row,col,hintList,gridList,previousList))

def mazeHint_Wrapper(app,row,col,hintList,gridList,previousList):
    if row == app.rows - 2 and col == app.cols - 2:
        return hintList
    else:
        moveset = {(+1,0),(-1,0),(0,+1),(0,-1)}
        for move in moveset:
            drow,dcol = move
            if gridList[row + drow][col + dcol] == 'white' and \
                1 <= row + drow < app.rows and 1 <= col + dcol < app.cols \
                and (row + drow,col + dcol) not in previousList:
                row += drow
                col += dcol
                hintList.append((row,col))
                previousList.append((row,col))
                possibleSolution = mazeHint_Wrapper(app,row,col,hintList,gridList,previousList)
                if possibleSolution != None:
                    return possibleSolution
                row -= drow
                col -= dcol
                hintList.pop()
                previousList.pop()
        return None

def gridGeneration(app):
    gridList = []
    for i in range(app.rows):
        gridList.append(['grey']*app.cols)
    list = initialPathGeneration(app)
    for ((a,b),(c,d)) in list:
        
        gridList[2*a+1][2*b+1] = 'white'
        gridList[2*c+1][2*d+1] = 'white'
        if a == c:
            gridList[2*a+1][2*b+2] = 'white'
        elif b == d:
            gridList[2*a+2][2*b+1] = 'white'
    # gridList[0][0] = 'white'
    # gridList[1][0] = 'white'
    # gridList[0][1] = 'white'
    # gridList[app.rows-1][app.cols-1] = 'white'
    # gridList[app.rows-2][app.cols-1] = 'white'
    # gridList[app.rows-1][app.cols-2] = 'white'
    
    return gridList



#Drawing Part!
###########

#drawing the cover
def drawCover(app):
    drawW()
    drawE()
    drawL()
    drawC()
    drawO()
    drawM()
    drawE3()
    drawE2()
    drawT2()
    drawO2()
    drawT3()
    drawH()
    drawE2()
    drawESCAPE()
    drawBar()
    drawTinyMan(app)

# def passGame(app):
#     print(app.playerPosition)
#     print((app.margin + (app.cols-2) * app.cellSize) )
#     if (app.margin + (app.cols-2) * app.cellSize) < app.playerPosition[0] < \
#     (app.margin + (app.cols-1) * app.cellSize) and \
#     (app.margin + (app.rows-2) * app.cellSize) < app.playerPosition[1] < \
#     (app.margin + (app.rows-1) * app.cellSize):
#         app.gameStarted = False
#         app.passGame = True


def drawW():
    size = 900/60
    color = 'darkRed'
    drawRect(1*size,1*size,1*size,2*size,fill = color)
    drawRect(2*size,3*size,1*size,1*size,fill = color)
    drawRect(3*size,4*size,1*size,2*size,fill = color)
    drawRect(4*size,1*size,1*size,3*size,fill = color)
    drawRect(5*size,4*size,1*size,2*size,fill = color)
    drawRect(6*size,3*size,1*size,1*size,fill = color)
    drawRect(7*size,1*size,1*size,2*size,fill = color)

def drawE():
    size = 900/60
    color = 'darkRed'
    drawRect(9*size,1*size,1*size,5*size,fill = color)
    drawRect(9*size,1*size,4*size,1*size,fill = color)
    drawRect(9*size,3*size,4*size,1*size,fill = color)
    drawRect(9*size,5*size,4*size,1*size,fill = color)
    drawRect(10*size,1*size,4,5*size,fill = 'white')

def drawL():
    size = 900/60
    color = 'darkRed'
    drawRect(14*size,1*size,1*size,5*size,fill = color)
    drawRect(14*size,5*size,4*size,1*size,fill = color)

def drawC():
    size = 900/60
    color = 'darkRed'
    drawRect(19*size,1*size,4*size,1*size,fill = color)
    drawRect(19*size,1*size,1*size,5*size,fill = color)
    drawRect(19*size,5*size,4*size,1*size,fill = color)
    drawRect(20*size,1*size,4,5*size,fill = 'white')

def drawO():
    size = 900/60
    color = 'darkRed'
    drawRect(24*size,1*size,1*size,5*size,fill = color)
    drawRect(24*size,1*size,4*size,1*size,fill = color)
    drawRect(24*size,5*size,4*size,1*size,fill = color)
    drawRect(27*size,1*size,1*size,5*size,fill = color)
    drawRect(26*size-2,1*size,4,5*size,fill = 'white')

def drawM():
    size = 900/60
    color = 'darkRed'
    drawRect(29*size,3*size,1*size,3*size,fill = color)
    drawRect(30*size,1*size,1*size,2*size,fill = color)
    drawRect(31*size,3*size,1*size,2*size,fill = color)
    drawRect(32*size,1*size,1*size,2*size,fill = color)
    drawRect(33*size,3*size,1*size,3*size,fill = color)

def drawE3():
    size = 900/60
    color = 'darkRed'
    drawRect(35*size,1*size,1*size,5*size,fill = color)
    drawRect(35*size,1*size,4*size,1*size,fill = color)
    drawRect(35*size,3*size,4*size,1*size,fill = color)
    drawRect(35*size,5*size,4*size,1*size,fill = color)
    drawRect(36*size,1*size,4,5*size,fill = 'white')

def drawE2():
    size = 900/60
    color = 'darkRed'
    drawRect(35*size,1*size,1*size,5*size,fill = color)
    drawRect(35*size,1*size,4*size,1*size,fill = color)
    drawRect(35*size,3*size,4*size,1*size,fill = color)
    drawRect(35*size,5*size,4*size,1*size,fill = color)
    drawRect(36*size,1*size,4,5*size,fill = 'white')

def drawT2():
    size = 900/60
    color = 'darkRed'
    drawRect(20*size,8*size,3*size,1*size,fill = color)
    drawRect(21*size,8*size,1*size,4*size,fill = color)

def drawO2():
    size = 900/60
    color = 'darkRed'
    drawRect(24*size,8*size,3*size,1*size,fill = color)
    drawRect(24*size,8*size,1*size,4*size,fill = color)
    drawRect(26*size,8*size,1*size,4*size,fill = color)
    drawRect(24*size,11*size,3*size,1*size,fill = color)
    drawRect(25.5*size-2,8*size,4,4*size,fill = 'white')

def drawT3():
    size = 900/60
    color = 'darkRed'
    drawRect(31*size,8*size,3*size,1*size,fill = color)
    drawRect(32*size,8*size,1*size,4*size,fill = color)

def drawH():
    size = 900/60
    color = 'darkRed'
    drawRect(35*size,8*size,1*size,4*size,fill = color)
    drawRect(35*size,10*size,3*size,1*size,fill = color)
    drawRect(37*size,8*size,1*size,4*size,fill = color)

def drawE2():
    size = 900/60
    color = 'darkRed'   
    drawRect(39*size,8*size,1*size,4*size,fill = color) 
    drawRect(39*size,8*size,3*size,1*size,fill = color)
    drawRect(39*size,11*size,3*size,1*size,fill = color)
    drawRect(39*size,9.6*size,3*size,0.6*size,fill = color)
    drawRect(40*size,8*size,3,4*size,fill = 'white')

def drawESCAPE():
    size = 900/60
    color = 'fireBrick'
    #letterE
    drawRect(4*size,16*size,6*size,2*size,fill=color)
    drawRect(4*size,16*size,1*size,10*size,fill=color)
    drawRect(4*size,20*size,6*size,2*size,fill=color)
    drawRect(4*size,24*size,6*size,2*size,fill=color)
    drawRect(5*size,16*size,5,10*size,fill='white')
    #letterS
    drawRect(12*size,16*size,6*size,2*size,fill=color)
    drawRect(12*size,20*size,6*size,2*size,fill=color)
    drawRect(12*size,24*size,6*size,2*size,fill=color)
    drawRect(12*size,16*size,1*size,5*size,fill=color)
    drawRect(17*size,20*size,1*size,5*size,fill=color)
    drawRect(13*size,16*size,5,6*size,fill='white')
    drawRect(17*size-5,20*size,5,6*size,fill='white')
    #letterC
    drawRect(20*size,16*size,1*size,10*size,fill=color)
    drawRect(20*size,16*size,6*size,2*size,fill=color)
    drawRect(20*size,24*size,6*size,2*size,fill=color)
    drawRect(21*size,16*size,5,10*size,fill='white')
    #letterA
    drawRect(28*size,22*size,1*size,4*size,fill=color)
    drawRect(34*size,22*size,1*size,4*size,fill=color)
    drawRect(29*size,19*size,1*size,4*size,fill=color)
    drawRect(33*size,19*size,1*size,4*size,fill=color)
    drawRect(30*size,17*size,1*size,3*size,fill=color)
    drawRect(32*size,17*size,1*size,3*size,fill=color)
    drawRect(31*size,16*size,1*size,2*size,fill=color)
    drawRect(29*size,22*size,5*size,2*size,fill=color)
    drawRect(30*size,20*size,5,4*size,fill='white')
    drawRect(33*size-5,20*size,5,4*size,fill='white')
    #letterP
    drawRect(37*size,16*size,1*size,10*size,fill=color)
    drawRect(37*size,16*size,6*size,2*size,fill=color)
    drawRect(42*size,16*size,1*size,7*size,fill=color)
    drawRect(37*size,21*size,6*size,2*size,fill=color)
    drawRect(38*size,16*size,5,10*size,fill='white')
    #letterE
    drawRect(45*size,16*size,1*size,10*size,fill=color)
    drawRect(45*size,16*size,6*size,2*size,fill=color)
    drawRect(45*size,20*size,6*size,2*size,fill=color)
    drawRect(45*size,24*size,6*size,2*size,fill=color)
    drawRect(46*size,16*size,5,10*size,fill='white')
    #!mark
    drawRect(53*size,16*size,2*size,7*size,fill=color)
    drawRect(53*size,24*size,2*size,2*size,fill=color)

def drawBar():
    size = 900/60
    color = 'navajowhite'
    drawRect(8*size,31*size,20*size,8*size,fill=color)
    drawLabel('Start Your Trip',18*size,35*size,size=25,font='arial')

def drawTinyMan(app):
    size = 900/60
    ironColor = 'lightGray'
    drawRect(33*size,31*size,1*size,10*size,fill=ironColor)
    drawRect(35*size,31*size,1*size,10*size,fill=ironColor)
    drawRect(37*size,31*size,1*size,10*size,fill=ironColor)
    drawRect(39*size,31*size,1*size,10*size,fill=ironColor)
    drawRect(41*size,31*size,1*size,10*size,fill=ironColor)
    drawRect(43*size,31*size,1*size,10*size,fill=ironColor)
    drawRect(45*size,31*size,1*size,10*size,fill=ironColor)
    drawRect(47*size,31*size,1*size,10*size,fill=ironColor) 
    drawRect(49*size,31*size,1*size,10*size,fill=ironColor)
    drawRect(51*size,31*size,1*size,10*size,fill=ironColor)
    drawRect(53*size,31*size,1*size,10*size,fill=ironColor)
    drawRect(55*size,31*size,1*size,10*size,fill=ironColor)
    manColor = 'dimgrey'
    drawRect(43*size,31*size,3*size,3*size,fill = manColor)
    drawRect(44*size,32*size,1*size,1*size,fill = 'white')
    drawRect(44*size,34*size,1*size,4*size,fill = manColor)
    drawRect(42*size,35*size,2*size,1*size,fill = manColor)
    drawRect(45*size,35*size,2*size,1*size,fill = manColor)
    drawRect(43*size,37*size,1*size,2*size,fill = manColor)
    drawRect(45*size,37*size,1*size,2*size,fill = manColor)
    drawRect(42*size,39*size,1*size,2*size,fill = manColor)
    drawRect(46*size,39*size,1*size,2*size,fill = manColor)
    if 0 <= app.manTimer % 10 < 5:
        drawRect(41*size,33*size,1*size,2*size,fill = manColor)
        drawRect(47*size,36*size,1*size,2*size,fill = manColor)
    elif  5 <= app.manTimer % 10 < 10:
        drawRect(41*size,36*size,1*size,2*size,fill = manColor)
        drawRect(47*size,33*size,1*size,2*size,fill = manColor)


def drawraycastingUnit_3D(app):
    for angle in range(app.playerFacingAngle-30, app.playerFacingAngle+31, 1):
        if rayCastingLine(app,angle)[2] == 'V':
            (x,y) = rayCastingLine(app,angle)[0]
            (a,b,c) = (205,181,205)
            if hitWall(app,x,y)[1] == 'grey':
                k = rayCastingLine(app,angle)[1]
                fillColor = rgb(a-k,b-k,c-k)
              
        elif rayCastingLine(app,angle)[2] == 'H':
            (x,y) = rayCastingLine(app,angle)[0]
            (d,e,f) = (255,181,197)
            if hitWall(app,x,y)[1] == 'grey':
                j = rayCastingLine(app,angle)[1]
                fillColor = rgb(d-j,e-j,f-j)
        fixAngle = app.playerFacingAngle - angle
        fixRad = math.radians(fixAngle)
        pixel = 900/60
        centre = 600/2
        height = 130
        distance = rayCastingLine(app,angle)[1]
        distance = distance*math.cos(fixRad)
        wallHeight = height / distance * (20+distance)
        if wallHeight > 590:
            wallHeight = 590
        startingX = (app.playerFacingAngle+30-angle)*pixel
        drawRaycastingLine_3D(app,startingX,centre,wallHeight,pixel,fillColor)

def drawRaycastingLine_3D(app,startingX,centre,wallHeight,pixel,fillColor):
    drawRect(startingX,centre-0.5*wallHeight,pixel,wallHeight,
        fill=fillColor,border=None)
    if 0 <= app.time % 130 < 60:
        skyColor = 'skyBlue'
    elif 60 <= app.time % 130 < 70:
        skyColor = 'moccasin'
    elif 70 <= app.time % 130 < 130:
        skyColor = 'midnightBlue'
    drawRect(startingX,0,pixel,centre-0.5*wallHeight,fill=skyColor,
        border=None)
    drawRect(startingX,centre+0.5*wallHeight,pixel,600,
        fill='olive',border=None)


def drawRaycasting(app):
    for angle in range(app.playerFacingAngle-30, app.playerFacingAngle+31, 3):
        (termX,termY) = rayCastingLine(app,angle)[0]
        centreX = app.playerPosition[0]
        centreY = app.playerPosition[1]
        drawLine(centreX,centreY,termX,termY,fill='orange',lineWidth = 1)
        

def drawplayerFacingAngleLine(app):
    rad = math.radians(app.playerFacingAngle)
    startX = app.playerPosition[0]
    startY = app.playerPosition[1]
    termX = startX + 20*math.cos(rad)
    termY = startY - 20*math.sin(rad)
    drawLine(startX,startY,termX,termY,lineWidth=1)
    
def drawPlayer(app):
    centreX = app.playerPosition[0]
    centreY = app.playerPosition[1]
    drawCircle(centreX,centreY,app.playerRadius,fill = 'red',border=None)
    # drawRect(centreX-app.playerRadius,centreY-app.playerRadius,
    # 2*app.playerRadius,2*app.playerRadius,fill = 'blue',border=None)
    
def drawBoard(app):
    for col in range(app.cols):
        for row in range(app.rows):
            drawGrids(app,row,col)
            
def drawGrids(app,row,col):
    left = app.margin + col*app.cellSize
    top =app.margin + row*app.cellSize
    right=left+app.cellSize
    bottom=top+app.cellSize
    # if app.mazeHint == False:
    cellColor=app.colorList[row][col]
    # elif app.mazeHint == True:
    #     cellColor=app.hintColorList[row][col]
    drawRect(left,top,app.cellSize,app.cellSize,fill=cellColor,border='white',
    borderWidth = 0.3)
    

#Generate the set of wall
def wallGeneration(app):
    wallset = set()
    rows = app.rows
    cols = app.cols
    for i in range(rows):
        for j in range(cols):
            if app.colorList[i][j] != 'white':
                wallset.add((i,j))
    
    return wallset

def gameDimensions(app):
    row1 = 7
    col1 = 7
    row2 = 15
    col2 = 15
    cellSize = 8
    margin = 20
    # colorList = gridGeneration(app)
    # hintColorList = copy.deepcopy(colorList)
    # hintlist = mazeHint(app)
    # for (i,j) in hintlist:
    #     hintColorList[i][j] = 'green'
    if app.levelClicked1 == True:
        return([row1, col1, cellSize, margin])
    else:
        return([row2, col2, cellSize, margin])

def dFScolorListGeneration(app):
    row = app.rows
    col = app.cols
    colorList = dFSgridGeneration(app)    
    return colorList

def colorListGeneration(app):
    row = app.rows
    col = app.cols
    colorList = gridGeneration(app)    
    return colorList

def drawHintBoard(app):
    for col in range(app.cols):
        for row in range(app.rows):
            drawHintGrids(app,row,col)
            
def drawHintGrids(app,row,col):
    left = app.margin + col*app.cellSize
    top =app.margin + row*app.cellSize
    right=left+app.cellSize
    bottom=top+app.cellSize
    # if app.mazeHint == False:
    cellColor=app.hintColorList[row][col]
    # elif app.mazeHint == True:
    #     cellColor=app.hintColorList[row][col]
    drawRect(left,top,app.cellSize,app.cellSize,fill=cellColor,border='white',
    borderWidth = 0.3)

def hintColorListGeneration(app):
    hintColorList = copy.deepcopy(app.colorList)
    hintlist = mazeHint(app)
    for (i,j) in hintlist:
        hintColorList[i][j] = 'green'   
    return hintColorList

    # if app.mazeHint == True:
    #     hintlist = mazeHint(app)
    #     for (i,j) in hintlist:
    #         colorList[i][j] = 'green'
    
    # for i in range(row):
    #     colorList.append(['grey']*col)
    # for x in range(row):
    #     for y in range(col):
    #        if gridList[x][y] == '1':
    #            colorList[x][y] == 'white'
    

def drawOptionCaptions(app):
    drawRect(400,475,100,50,fill = 'RosyBrown')
    drawLabel('Lets go!',450,500,size = 20)
    drawLabel('Pick the hardness level!',450,100,font='Arial',size = 50)
    if app.levelClicked1 == True:
        levelcolor1 = 'Sienna'
    elif app.levelClicked1 == False:
        levelcolor1 = 'Burlywood'
    if app.levelClicked2 == True:
        levelcolor2 = 'Sienna'
    elif app.levelClicked2 == False:
        levelcolor2 = 'Burlywood'
    drawRect(250,175,100,50,fill = levelcolor1)
    drawRect(550,175,100,50,fill = levelcolor2)
    drawLabel('easy',300,200,size = 20)
    drawLabel('hard',600,200,size = 20)
    if app.mazeClicked1 == True:
        mazecolor1 = 'Sienna'
    elif app.mazeClicked1 == False:
        mazecolor1 = 'Burlywood'
    if app.mazeClicked2 == True:
        mazecolor2 = 'Sienna'
    elif app.mazeClicked2 == False:
        mazecolor2 = 'Burlywood'
    drawLabel('Pick the maze!',450,300,font='Arial',size = 50)
    drawRect(250,375,100,50,fill = mazecolor1)
    drawRect(550,375,100,50,fill = mazecolor2)
    drawLabel('Kruskal',300,400,size = 20)
    drawLabel('DFS',600,400,size = 20)

def drawLifestars1(app):
    if app.lifeTimer < 15:
        drawStar(30,570,20,5,fill = 'orangeRed')   
def drawLifestars2(app):
    if app.lifeTimer < 10:
        drawStar(80,570,20,5,fill = 'orangeRed')
def drawLifestars3(app):
    if app.lifeTimer < 5:
        drawStar(130,570,20,5,fill = 'orangeRed')   

def drawGameOver(app):
    
    if 0 <= app.gameOverTimer % 2 < 1:
        color = 'black'
    elif 1 <= app.gameOverTimer % 2 < 2:
        color = 'DarkRed'
    drawLabel('Time over!', 450,200,size = 60, fill = color, bold = True, \
        font = 'monospace')
    drawLabel('You are trapped in!', 450,400,size = 60, fill = color, \
        bold = True, font = 'monospace')

def drawHint_2DCaption(app):
    drawRect(800,50,50,30,border = None, fill = 'green')
    drawLabel('2D hint',825,65,size = 15)

def drawMazeHintaption(app):
    drawRect(700,50,80,30,border = None, fill = 'green')
    drawLabel('MazeHint',740,65,size = 15)

def drawPassGame(app):
    if 0 <= app.passTimer % 6 < 3:
        color1 = 'GreenYellow'
        color2 = 'Yellow'
    elif 3 <= app.passTimer % 6 < 6:
        color1 = 'LimeGreen'
        color2 = 'gold'
    drawLabel('Escape Successfully!', 450,200,size = 40, fill = color1, bold = True)
    drawLabel('Congratulation!', 450,400,size = 40, fill = color2, bold = True)

def redrawAll(app):
    print(app.lifeTimer)
    if app.gameStarted == True:
        drawraycastingUnit_3D(app)
        drawHint_2DCaption(app)
        drawMazeHintaption(app)
        drawLifestars1(app)
        drawLifestars2(app)
        drawLifestars3(app)
        if app.hint_2D == True:
            drawBoard(app)
            drawPlayer(app)
            drawRaycasting(app)
            drawplayerFacingAngleLine(app)
            if app.mazeHint == True:
                drawHintBoard(app)
                drawPlayer(app)
                drawRaycasting(app)
                drawplayerFacingAngleLine(app) 
    elif app.optionStarted == True:
        drawOptionCaptions(app)
    elif app.passGame == True:
        drawPassGame(app)
    elif app.gameOver == True:
        drawGameOver(app)
    else:
        drawCover(app)
   


def playGame():
    width = 900
    height = 600
    #print(width,height)
    # width = 500
    # height = 300
    runApp(width=width, height=height)


def main():
    playGame()
    

main()
