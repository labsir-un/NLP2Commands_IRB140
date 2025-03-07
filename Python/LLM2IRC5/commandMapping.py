from whisperApp import getTranscription, recordAudio
from scipy.spatial.transform import Rotation as Rot
from llmApp import getNLValues
import numpy as np
import keyboard
import ast

actions = {'pick': 0, 'move': 1, 'rotate': 2, 'draw': 3}
cartesianAux = {'x': 0, 'y': 1, 'z': 2}

posesRPY = [[0, 0, 0], # Top 
        [0, 1.5708, 0], [-3.1416, 1.5708, 0], # Front and back
        [0.7854, 1.5708, 0], [-0.7854, 1.5708, 0], # Front right and left
        [-2.3562, 1.5708, 0], [2.3562, 1.5708, 0]] # Back left and right

pickPose = [0, 3.1416, 0]

zeros = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

objects = ['cubo rojo', 'cubo amarillo', 'rectángulo verde']
objectsPosition = [[300, 300, 230], [700, -200, 230], [-300, -400, 230]] #Red, yellow
# 10 cm up, safety choice

def customCartesian(customValue):
  lengthCustomValue = len(customValue)
  if lengthCustomValue > 4:
    npArray = np.array(ast.literal_eval(customValue))*10
    npArray = npArray.tolist()
    npArray.append(0) #Is moveJ
    return npArray
  cartesianValue = [0, 0, 0, 1] #Is moveL
  axisPosition = lengthCustomValue - 1
  axis = cartesianAux[customValue[axisPosition:]]
  cartesianValue[axis] = int(customValue[:axisPosition])*10
  
  return cartesianValue

actionFunctions = {
  0: lambda v: int(v),
  1: lambda v: customCartesian(v),
  2: lambda v: int(v),
  3: int
}

def NL2Array(transcription):
  transcription = transcription.lower()
  fullArray = transcription.split(', ')
  amountCommands = int(len(fullArray)/3)

  actionsList, targetsList, valuesList  = [], [], []

  for index in range(amountCommands):
      actionsList.append(fullArray[index*3])  
      targetsList.append(fullArray[index*3 + 1])
      valuesList.append(fullArray[index*3 + 2])

  actionsList = [actions[action] for action in actionsList]

  auxList = []
  for action, value in zip(actionsList, valuesList):
    auxList.append(actionFunctions.get(action, lambda v: None)(value))
  
  return [actionsList, targetsList, auxList]

def getArrayCommands():
  while True:
    command = ''
    while not command.lower().__contains__('robot despierta'):
      commandTranscription = getTranscription(recordAudio(2, 'Esperando comando de voz...'))
      print(commandTranscription)
      command = commandTranscription.lower()
    transcription = getTranscription(recordAudio(0, 'Recibiendo ordenes...')).lower()
    print(transcription)
    NLValues = getNLValues(transcription)
    print(NLValues)
    print('<<<<<<<<<<<<<<<<<VALIDACIÓN HUMANA>>>>>>>>>>>>>>>>>')
    print('<CUALQUIER TECLA PARA REINICIAR>')
    print('<ENTER PARA VALIDAR>')
    keyPressed = keyboard.read_key()
    if keyPressed == 'enter':
      arrayValues = NL2Array(NLValues)
      return arrayValues

def poseGetter(coor):
    x, y, z = coor[0], coor[1], coor[2]
    vectorRPY = posesRPY[6]
    if z <= 500:
        vectorRPY = pickPose
    elif z >= 800:
        vectorRPY = posesRPY[0]
    elif y < 400 and y > -400 and x > 0.0:
        vectorRPY = posesRPY[1]
    elif y < 400 and y > -400 and x < 0.0:
        vectorRPY = posesRPY[2]
    elif y < 0.0 and x > 0.0:
        vectorRPY = posesRPY[3]
    elif y > 0.0 and x > 0.0:
        vectorRPY = posesRPY[4]
    elif y > 0.0:
        vectorRPY = posesRPY[5]
    cuaternion = Rot.from_euler('xyz', vectorRPY).as_quat()
    qwFirst = [cuaternion[3], *cuaternion[:3]]
    return np.round(qwFirst, 9).tolist()

lastCommandTarget = 'none'

def setUpCommands(arrayCommands):
    commands = []
    actions, targets, values = arrayCommands[0], arrayCommands[1], arrayCommands[2]
    previousAction = None

    global lastCommandTarget
    firstTarget = targets[0]
    noneTest = firstTarget != 'none' and lastCommandTarget != 'none'
    if firstTarget != lastCommandTarget and noneTest: #does he already have something?
        indexPosition = objects.index(lastCommandTarget)
        objectPosition = objectsPosition[indexPosition]
        pose = poseGetter(objectPosition)
        dropCommand = [*objectPosition, *pose, 0, 0]
        commands.append(dropCommand)
        lastCommandTarget = 'none'

    for action, target, value in zip(actions, targets, values):
        alreadyPicked = False
        if lastCommandTarget != target: # Previous drop or pick
            targetTest = target != 'none'
            dropTest = previousAction or (not action and value and previousAction)
            if targetTest and dropTest: #If there was something
                indexPrevious = objects.index(lastCommandTarget)
                positionPrevious = objectsPosition[indexPrevious]
                previousPose = poseGetter(positionPrevious)
                dropCommand = [*positionPrevious, *previousPose, 0, 0]
                lastCommandTarget = 'none'
                commands.append(dropCommand)

            if action and targetTest and lastCommandTarget != target:
                indexCurrent = objects.index(target)
                currentPosition = objectsPosition[indexCurrent]
                currentPose = poseGetter(currentPosition)
                pickCommand = [*currentPosition, *currentPose, 0, 1]
                lastCommandTarget = target
                commands.append(pickCommand)

        command = [*zeros, action, value] # Rotate joint_6 or draw routines in RobotStudio

        if not action: #If is pick action
            alreadyPicked = value and lastCommandTarget == target
            indexPosition = objects.index(target)
            objectPosition = objectsPosition[indexPosition]
            pose = poseGetter(objectPosition)
            lastCommandTarget = target
            if not value:
                lastCommandTarget = 'none'
                value = 2
            command = [*objectPosition, *pose, action, value]

        if action == 1: # Move command
            typeMove = value[3] # 0 -> MoveJ [X, Y, Z] 1 -> MoveL Offs(.., x, y, z), ...
            pose = poseGetter(value)
            command = [*value[:3], *pose, action, typeMove]

        previousAction = action
        if not alreadyPicked:
            commands.append(command)
    return commands
