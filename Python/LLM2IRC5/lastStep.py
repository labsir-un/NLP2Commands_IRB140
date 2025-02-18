from scipy.spatial.transform import Rotation as Rot
import numpy as np
import time

posesRPY = [[0, 0, 0], # Top 
        [0, 1.5708, 0], [-3.1416, 1.5708, 0], # Front and back
        [0.7854, 1.5708, 0], [-0.7854, 1.5708, 0], # Front right and left
        [-2.3562, 1.5708, 0], [2.3562, 1.5708, 0]] # Back left and right

zeros = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
pickPose = [0, 3.1416, 0]

elements = ['cubo rojo', 'cubo amarillo', 'rectángulo verde']
objectsPosition = [[300, 300, 230], [700, -200, 230], [-300, -400, 230]] #Red, yellow
# 10 cm up, safety choice

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

def fixCommands(arrayCommands):
    commands = []
    actions, targets, values = arrayCommands[0], arrayCommands[1], arrayCommands[2]
    previousAction = None

    global lastCommandTarget
    firstTarget = targets[0]
    noneTest = firstTarget != 'none' and lastCommandTarget != 'none'
    if firstTarget != lastCommandTarget and noneTest: #does he already have something?
        indexPosition = elements.index(lastCommandTarget)
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
                indexPrevious = elements.index(lastCommandTarget)
                positionPrevious = objectsPosition[indexPrevious]
                previousPose = poseGetter(positionPrevious)
                dropCommand = [*positionPrevious, *previousPose, 0, 0]
                lastCommandTarget = 'none'
                commands.append(dropCommand)

            if action and targetTest and lastCommandTarget != target:
                indexCurrent = elements.index(target)
                currentPosition = objectsPosition[indexCurrent]
                currentPose = poseGetter(currentPosition)
                pickCommand = [*currentPosition, *currentPose, 0, 1]
                lastCommandTarget = target
                commands.append(pickCommand)

        command = [*zeros, action, value] # Rotate joint_6 or draw routines in RobotStudio

        if not action: #If is pick action
            alreadyPicked = value and lastCommandTarget == target
            indexPosition = elements.index(target)
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
