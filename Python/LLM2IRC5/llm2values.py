from llmApp import getNLValues
from whisperApp import getTranscription, recordAudio
import keyboard
import ast
import numpy as np

actions = {'pick': 0, 'move': 1, 'rotate': 2, 'draw': 3}
cartesianAux = {'x': 0, 'y': 1, 'z': 2}

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
    