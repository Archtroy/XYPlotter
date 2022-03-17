"""
gCodeConverter - convert svg file to g-code

"""
# Libraries
from gCodeConverterObjects import Shape
import turtle
import math
import time

# Functions
def get_obj_data(objData):
    """Gets data from file string and retruns dict"""
    # Make object data into list
    objData = objData.split("\"")
    objDataClean = []
    for item in objData:
        item = item.strip()
        item = item.strip("=")
        item = item.strip()
        if len(objDataClean) == 0:
            item = item.split()
            item = item[1].strip()
        objDataClean.append(item)
    objDataClean = objDataClean[:-1]
    # Make list into dict
    objDataDict = {}
    for index, item in enumerate(objDataClean):
        if index%2 == 0:
            objDataDict[item] = objDataClean[index+1]
    # Removes ID tag from data
    try:
        del objDataDict["id"]
    except KeyError as err:
        if str(err) != "'id'":
            raise KeyError(str(err))
    return objDataDict

def create_shape(shapeName, shapeDataDict, gData):
    """Creates shape objects"""
    # Note: some objects may not exist
    newShape = Shape(shapeName)
    for item in gData:
        itemAdded = newShape.add(item, gData[item])
        if itemAdded:
            print("Successfully added\t" + str(item) + "\tto " + str(shapeName))
        else:
            print("Could not find\t\t" + str(item) + "\tin " + str(shapeName))
    for item in shapeDataDict:
        itemAdded = newShape.add(item, shapeDataDict[item])
        if itemAdded:
            print("Successfully added\t" + str(item) + "\tto " + str(shapeName))
        else:
            print("Could not find\t\t" + str(item) + "\tin " + str(shapeName))
    return newShape

def draw_arc(xPos, yPos, rx, ry, sDegree, degree, res):
    """Draws arc with radius r, starting at sDegree"""
    sRad = sDegree * math.pi/180  # Start pos
    rad = degree * math.pi/180  # Move amount
    for step in range(res+1):
        x = xPos + rx * math.cos((rad/res)*step + sRad)
        y = yPos + ry * math.sin((rad/res)*step + sRad)
        addPoint("point", x, y)

def addPoint(sel, xPos=0, yPos=0):
    if sel == "point":
        pointsList.append(xPos)
        pointsList.append(yPos)
    elif sel == "up" or sel == "down":
        pointsList.append(sel)
    else:
        print("addPoint error, \"" + str(sel) + "\" not valid selection")
        raise TypeError("addPoint error, \"" + str(sel) + "\" not valid selection")

# Constants
FILE = "freeSample.svg"  # Source file for plotting
SHAPE_LIST = ["path", "rect", "circle", "ellipse"]  # not  implemented: , "line", "polyline", "polygon"]
FORMAT_SYSTAX = ["svg"]

# Variables
shapeObjList = []
gData = {}
pointsList = []

# Import svg file
with open(FILE, "r") as fileObj:
    fileText = fileObj.read()

# Split file into instructions
fileList = fileText.split("<")
fileListStrip = []
for item in fileList:
    item = item.strip()
    fileListStrip.append(item)

# Identify objects
for item in fileListStrip:
    if item != "":
        objName = item.split()[0]
        if objName in SHAPE_LIST:
            # Create shape object
            print("Creating object: " + objName)
            objDict = get_obj_data(item)
            shapeObj = create_shape(objName, objDict, gData)
            shapeObjList.append(shapeObj)
        elif objName in FORMAT_SYSTAX:
            print(objName + " format")
        elif objName == "g":
            # Creates g container
            print("Open g container")
            gData = get_obj_data(item)
        elif objName == "/g>":
            # Close g container
            print("Close g container")
            gData = {}
        elif "/" in objName:
            print("Closing: " + str(objName[1:-1]))
        else:
            print("What dis: " + str(objName))

# Point mapping
for i in shapeObjList:
    print(i)
    if i.checkShape():
        if i.shapeName == "rect":
            if i.rx == None:
                i.rx = 0
            if i.ry == None:
                i.ry = 0
            if i.rx > i.width/2:
                i.rx = i.width/2
            if i.ry > i.height/2:
                i.ry = i.height/2
            addPoint("up")
            addPoint("point", i.x+i.rx, i.y)
            addPoint("down")
            if i.rx+i.ry != 0:
                addPoint("point", i.x+i.width-i.rx, i.y)
                draw_arc(i.x+i.width-i.rx, i.y+i.ry, i.rx, i.ry, -90, 90, 25)
                addPoint("point", i.x+i.width, i.y+i.height-i.ry)
                draw_arc(i.x+i.width-i.rx, i.y+i.height-i.ry, i.rx, i.ry, 0, 90, 25)
                addPoint("point", i.x+i.rx, i.y+i.height)
                draw_arc(i.x+i.rx, i.y+i.height-i.ry, i.rx, i.ry, 90, 90, 25)
                addPoint("point", i.x, i.y+i.ry)
                draw_arc(i.x+i.rx, i.y+i.ry, i.rx, i.ry, -180, 90, 25)
            else:
                addPoint("point", i.x+i.width, i.y)
                addPoint("point", i.x+i.width, i.y+i.height)
                addPoint("point", i.x, i.y+i.height)
                addPoint("point", i.x, i.y)
            addPoint("up")
        if i.shapeName == "circle" or i.shapeName == "ellipse":
            if i.shapeName == "circle":
                i.rx = i.r
                i.ry = i.r
            addPoint("up")
            addPoint("point", i.cx+i.rx, i.cy)
            addPoint("down")
            draw_arc(i.cx, i.cy, i.rx, i.ry, 0, 360, 100)
            addPoint("up")
        if i.shapeName == "path":
            pathCommands = {"M": 2,"L": 2,"H": 1,"V": 1,"C": 6,"S": 4,"Q": 4,"T": 2,"A": 99,"Z": 0}
            pathCur = ""
            pathShape = []

            # Split path into commands
            for char in i.d:
                if char.upper() in pathCommands.keys():
                    pathCur = "".join(pathCur)
                    pathShape.append(pathCur)
                    pathCur = []
                pathCur += char
            pathCur = "".join(pathCur)
            pathShape.append(pathCur)
            pathShape = pathShape[1:]
            print(pathShape)

            # Split commands into points
            startPoint = [0, 0]
            prevPoint = [0, 0]
            prevCommandType = ""
            prevSmoothPoint = [0, 0]
            commandPointsAdj = [0, 0, 0, 0]
            for command in pathShape:
                command = command.strip()
                commandType = command[0]
                # Find points in string
                commandPoints = [""]
                commandPointsIndex = 0
                for char in command[1:]:
                    if char == "," or char == " " or char == "-":
                        commandPointsIndex += 1
                        if char == "-":
                            commandPoints.append(char)
                        else:
                            commandPoints.append("")
                    else:
                        commandPoints[commandPointsIndex] += char
                while "" in commandPoints:
                    commandPoints.remove("")
                for index, point in enumerate(commandPoints):
                    commandPoints[index] = float(point)
                # Number of commands per commands
                commandLength = pathCommands[commandType.upper()]
                commandIterations = (int( len(commandPoints) / commandLength ))
                # Relative vs absolute points
                moveRelative = False
                if commandType not in pathCommands.keys():
                    moveRelative = True
                # Pre-calculation of points
                commandPointsAdjList = []
                print("test1")
                for commandPointNum in range(len(commandPoints)):
                    # Update previous command data if new iteration
                    print("test2")
                    if commandPointNum % commandLength == 0:
                        print("new iteration")
                        print(commandType.upper())
                        if len(commandPoints) >= 2:
                            prevPoint = [commandPointsAdj[-2], commandPointsAdj[-1]]
                        elif commandType.upper() == "H":
                            prevPoint = [commandPointsAdj[0], prevPoint[1]]
                        elif commandType.upper() == "V":
                            prevPoint = [prevPoint[0], commandPointsAdj[0]]
                        elif commandType.upper() == "Z":
                            prevPoint = startPoint
                        if commandType.upper() == "M":
                            startPoint = prevPoint
                        if prevCommandType.upper() in ["C", "S", "Q", "T"]:
                            prevSmoothPoint = [moveRelative+commandPointsAdj[-4], commandPointsAdj[-3]]
                        prevCommandType = commandType
                        commandPointsAdjList.append(commandPointsAdj)
                        commandPointsAdj = []

                    commandPointsAdj.append(prevPoint[commandPointNum%2]*moveRelative + commandPoints[commandPointNum])
                
                print(commandPointsAdjList)
                print(commandPoints)


                # Plot points from commands points
                for iteration in range(commandIterations):
                    pass
                
                if commandType.upper() == "M":
                    print("Move")
                    addPoint("up")
                    addPoint("point", prevPoint[0]*moveRelative + commandPoints[0+commandLength*iteration], prevPoint[1]*moveRelative + commandPoints[1])
                    addPoint("down")
                    startPoint = [prevPoint[0]*moveRelative + commandPoints[0], prevPoint[1]*moveRelative + commandPoints[1]]
                    prevPoint = startPoint
                elif commandType.upper() == "L":
                    print("Line")
                    addPoint("point", prevPoint[0]*moveRelative + commandPoints[0], prevPoint[1]*moveRelative + commandPoints[1])
                elif commandType.upper() == "H":
                    print("Horizontal line")
                    addPoint("point", prevPoint[0]*moveRelative + commandPoints[0], prevPoint[1])
                    prevPoint = [prevPoint[0]*moveRelative + commandPoints[0], prevPoint[1]]
                elif commandType.upper() == "V":
                    print("Vertical line")
                    addPoint("point", prevPoint[0], prevPoint[1]*moveRelative + commandPoints[0])
                    prevPoint = [prevPoint[0], prevPoint[1]*moveRelative + commandPoints[0]]
                elif commandType.upper() == "C":
                    print("Curve")
                    for i in range(0, 101, 1):
                        i /= 100
                        xPoint = (((1-i)**3) * prevPoint[0]) + (3*i*((1-i)**2) * (prevPoint[0]*moveRelative+commandPoints[0])) + (3*(i**2) * (1-i) * (prevPoint[0]*moveRelative+commandPoints[2])) + (i**3 * (prevPoint[0]*moveRelative+commandPoints[4]))
                        yPoint = (((1-i)**3) * prevPoint[1]) + (3*i*((1-i)**2) * (prevPoint[1]*moveRelative+commandPoints[1])) + (3*(i**2) * (1-i) * (prevPoint[1]*moveRelative+commandPoints[3])) + (i**3 * (prevPoint[1]*moveRelative+commandPoints[5]))
                        addPoint("point", xPoint, yPoint)
                        prevSmoothPoint = [(prevPoint[0]*moveRelative+commandPoints[2]), (prevPoint[1]*moveRelative+commandPoints[3])]
                elif commandType.upper() == "S":
                    print("Smooth curve")
                    mirrorPoint = [0, 0]
                    if prevCommandType.upper() in ["C", "S"]:
                        for i in range(2):
                            mirrorPoint[i] = prevPoint[i] + (prevPoint[i] - prevSmoothPoint[i])
                    else:
                        for i in range(2):
                            mirrorPoint[i] = prevPoint[i] + commandPoints[i]
                    for i in range(0, 101, 1):
                        i /= 100
                        xPoint = (((1-i)**3) * prevPoint[0]) + (3*i*((1-i)**2) * (mirrorPoint[0])) + (3*(i**2) * (1-i) * (prevPoint[0]*moveRelative+commandPoints[0])) + (i**3 * (prevPoint[0]*moveRelative+commandPoints[2]))
                        yPoint = (((1-i)**3) * prevPoint[1]) + (3*i*((1-i)**2) * (mirrorPoint[1])) + (3*(i**2) * (1-i) * (prevPoint[1]*moveRelative+commandPoints[1])) + (i**3 * (prevPoint[1]*moveRelative+commandPoints[3]))
                        addPoint("point", xPoint, yPoint)
                    prevSmoothPoint = [(prevPoint[0]*moveRelative+commandPoints[2]), (prevPoint[1]*moveRelative+commandPoints[3])]
                elif commandType.upper() == "Q":
                    print("Quaratic curve")
                    for i in range(0, 101, 1):
                        i /= 100
                        xPoint = (((1-i)**2) * prevPoint[0]) + (2*i*(1-i) * (prevPoint[0]*moveRelative+commandPoints[0])) + (i**2 * (prevPoint[0]*moveRelative+commandPoints[2]))
                        yPoint = (((1-i)**2) * prevPoint[1]) + (2*i*(1-i) * (prevPoint[1]*moveRelative+commandPoints[1])) + (i**2 * (prevPoint[1]*moveRelative+commandPoints[3]))
                        addPoint("point", xPoint, yPoint)
                elif commandType.upper() == "T":
                    print("Smooth quadratic curve to be added #################################")
                    
                elif commandType.upper() == "A":
                    print("Arc to be added ####################################################")
                elif commandType.upper() == "Z":
                    print("Close path")
                    addPoint("point", startPoint[0], startPoint[1]) 
                    prevPoint = startPoint
                
                if len(commandPoints) >= 2:
                    prevPoint = [prevPoint[0]*moveRelative + commandPoints[-2], prevPoint[1]*moveRelative + commandPoints[-1]]
                prevCommandType = commandType

                #print(commandPoints)
                #print(prevPoint)
                #print(prevCommandType)
                #print(prevSmoothPoint)
                    
                
            print()
                
                


    else:
        print("Object invald, not drawing object: " + str(i.shapeName))

# Point reduction
# First loop: rounding
for index, item in enumerate(pointsList):
    if item != "up" and item != "down":
        pointsList[index] = round(item, 1)

# Second loop: removing duplicate point; finding max X and Y points
maxXPoint = 0
maxYPoint = 0
minXPoint = 0
minYPoint = 0
i = 0
while i < len(pointsList) - 2:
    if pointsList[i] != "up" and pointsList[i] != "down":
        if pointsList[i] > maxXPoint:
            maxXPoint = pointsList[i]
        if pointsList[i+1] > maxYPoint:
            maxYPoint = pointsList[i+1]
        if pointsList[i] < minXPoint:
            minXPoint = pointsList[i]
        if pointsList[i+1] < minYPoint:
            minYPoint = pointsList[i+1]

        if pointsList[i] == pointsList[i+2] and pointsList[i+1] == pointsList[i+3]:
            del pointsList[i:i+2]
        else:
            i += 2
    else:
        i += 1

# Turtle simulation
# Turtle settings for screen
IMAGE_SCALING = 2
screen = turtle.Screen()
canvasWidth = (maxXPoint-minXPoint)*IMAGE_SCALING
canvasHeight = (maxYPoint-minYPoint)*IMAGE_SCALING
turtle.screensize(canvasWidth, canvasHeight)
screen.setup(canvasWidth+50, canvasHeight+50)
turtle.tracer(1, 0)
t = turtle.Turtle()
t.hideturtle()
t.left(90)

# Drawing of points
i = 0
while i < len(pointsList):
    if pointsList[i] == "up":
        t.penup()
    elif pointsList[i] == "down":
        t.pendown()
    else:
        t.setpos(pointsList[i]*IMAGE_SCALING-canvasWidth/2, -pointsList[i+1]*IMAGE_SCALING+canvasHeight/2)
        i += 1
    i += 1


"""
# Curve Test

xVal = [0,0,200,200]
yVal = [0,200,0,200]
addPoint("up")
addPoint("point", 0, 0)
addPoint("down")
addPoint("point", 0,200)
addPoint("point", 0,0)
for i in range(0, 100, 1):
    i /= 100
    xPoint = (((1-i)**3) * xVal[0]) + (3*i*((1-i)**2) * xVal[1]) + (3*(i**2) * (1-i) * xVal[2]) + (i**3 * xVal[3])
    yPoint = (((1-i)**3) * yVal[0]) + (3*i*((1-i)**2) * yVal[1]) + (3*(i**2) * (1-i) * yVal[2]) + (i**3 * yVal[3])
    addPoint("point", xPoint, yPoint)
    print(str(xPoint) + ", " + str(yPoint))

addPoint("up")
"""
input()  # delay till enter