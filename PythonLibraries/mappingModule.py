from auxConstants import PICK_POSE_QUATERNION, RPY_ORIENTATIONS, AXES_INDEX, COMMANDS_INDEX
from auxConstants import OBJECTS, OBJECTS_POSITION, PARAMETERS_LENGTHS
from scipy.spatial.transform import Rotation
import numpy as np
import ast

lastTarget = 'none'

# There are two types move command, linear movement and joint movement
def moveInstructions(customValue):
    # It could be -10x or [1,2,3]
    if len(customValue) > 4:
        # Convert string to NumPy array, x10 due to ABB controller works with millimeters
        npArray = np.array(ast.literal_eval(customValue))*10
        # 0 in last position means moveJ
        moveCommand = npArray.tolist() + [0]
        return moveCommand
    # 1 in last position  means moveL
    moveCommand = [0, 0, 0, 1]
    axis = AXES_INDEX[customValue[-1]]
    moveCommand[axis] = int(customValue[:-1])*10
    return moveCommand

# Create the commands array from instructions string
def instructions2CommandsValues(transcription):
    wholeArray = transcription.split(', ')
    actionsList, targetsList, valuesList  = [], [], []
    for index in range(int(len(wholeArray)/3)):
        initialIndex = index * 3
        command = COMMANDS_INDEX[wholeArray[initialIndex]]
        actionsList.append(command)
        targetsList.append(wholeArray[initialIndex + 1])
        rawValue = wholeArray[initialIndex + 2]

        # Only movement instructions have considerable differences
        if command == 1:
            valuesList.append(moveInstructions(rawValue))
        else:
            valuesList.append(int(rawValue))
    return actionsList, targetsList, valuesList

# Predefine orientations according to position
def getOrientation(coordinates):
    x, y, z = coordinates

    if z <= 500:
        vectorRPY = RPY_ORIENTATIONS[0]
    elif z >= 800:
        vectorRPY = RPY_ORIENTATIONS[1]
    elif -400 < y < 400:
        vectorRPY = RPY_ORIENTATIONS[2] if x > 0.0 else RPY_ORIENTATIONS[3]
    elif y < 0.0:
        vectorRPY = RPY_ORIENTATIONS[4] if x > 0.0 else RPY_ORIENTATIONS[7]
    else:
        vectorRPY = RPY_ORIENTATIONS[5] if x > 0.0 else RPY_ORIENTATIONS[6]

    quaternion = Rotation.from_euler('xyz', vectorRPY).as_quat()

    # Robot controller reads quaternion like this -> w, x, x, z
    quaternion_wxyz = [quaternion[3], *quaternion[:3]]

    return np.round(quaternion_wxyz, 9).tolist()

# Transform command to socket format, it must be string
def socketMessage(command):
  stringCommand = ''
  for parameter, length in zip(command, PARAMETERS_LENGTHS):
    signAux = ''
    if parameter < 0:
        length = length - 1
        signAux = '-'
    # Float 0.0 -> 0
    if parameter == 0:
       parameter = 0
    stringParameter = signAux + str(abs(parameter)).rjust(length, '0')
    stringCommand = stringCommand + stringParameter
  return stringCommand

# Before send commands to robot controller, those need a last setting up
def setUpCommands(commandsValues):
    actions, targets, values = commandsValues
    global lastTarget
    commands = []

    # If the initial target is none, it doesn't mean that robot must drop the current taken object
    # It means robot have to do the instruction itself without target in memory

    for currentAction, currentTarget, currentValue in zip(actions, targets, values):
        # Does he already have something?  Previous drop or pick
        if lastTarget != currentTarget and currentTarget != 'none':

            # Previous drop
            if  lastTarget != 'none' and (currentAction or currentValue):
                dropCommand = [*OBJECTS_POSITION[OBJECTS.index(lastTarget)], *PICK_POSE_QUATERNION, 0, 0]
                commands.append(dropCommand)
                lastTarget = 'none'

            # Previous pick
            if currentAction and lastTarget != currentTarget:
                pickCommand = [*OBJECTS_POSITION[OBJECTS.index(currentTarget)], *PICK_POSE_QUATERNION, 0, 1]
                commands.append(pickCommand)
                lastTarget = currentTarget

        # Rotate sixth joint or draw routines in RobotStudio
        command = [0.0] * 7 + [currentAction, currentValue]

         # Direct pick command, if is already picked skip pick command
        if not currentAction and not (currentValue and lastTarget == currentTarget):
            lastTarget = currentTarget
            if not currentValue:
                lastTarget = 'none'

                # Absolute drop
                currentValue = 2

            command = [*OBJECTS_POSITION[OBJECTS.index(currentTarget)], *PICK_POSE_QUATERNION, currentAction, currentValue]

        # Movement command
        if currentAction == 1:
            position = currentValue[:3]
            command = [*position, *getOrientation(position), currentAction, currentValue[3]]

        commands.append(command)
    return commands
