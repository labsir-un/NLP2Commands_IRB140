from mappingModule import instructions2CommandsValues, setUpCommands, socketMessage
from llamaModule import getInstructionsValues
from whisperModule import getTranscription
import keyboard
import socket

def createClientSocket(ip):
  socketClient = socket.socket()
  socketClient.connect((ip, 8000))
  print(f"Conexión a servidor {ip} fue: {socketClient.recv(1024)}")
  return socketClient

def systemInput():
    while True:
      voiceCommand = ''
      while not voiceCommand.lower().__contains__('robot despierta'):
          # 2 seconds for the voice command enabler
          commandTranscription = getTranscription(2, 'Esperando comando de voz...')
          print(commandTranscription)
          voiceCommand = commandTranscription.lower()
      print('<<<<<<<<<<<<<<<<<ENTER PARA DETENER RECEPCIÓN DE ORDENES>>>>>>>>>>>>>>>>>')
      transcription = getTranscription(0, 'Recibiendo ordenes...').lower()
      print(transcription, '\n')
      InstructionsValues = getInstructionsValues(transcription)
      print(InstructionsValues, '\n')
      print('<<<<<<<<<<<<<<<<<VALIDACIÓN HUMANA>>>>>>>>>>>>>>>>>')
      print('<CUALQUIER TECLA PARA REINICIAR>')
      print('<ENTER PARA VALIDAR>', '\n')
      keyPressed = keyboard.read_key()
      if keyPressed == 'enter':
          commandsValues = instructions2CommandsValues(InstructionsValues)
          commands = setUpCommands(commandsValues)
          return commands


def main ():
  # Simulated controller ip "127.0.0.1" | Real robot controller ip "192.168.125.1"
  clientSocket = createClientSocket("127.0.0.1")

  while True:
    commands = systemInput()
    print(commands, '\n')
    for command in commands:
        message = socketMessage(command)
        print(message, '\n')
        clientSocket.send(message.encode())
        caseValidation = int(clientSocket.recv(1024).strip())
        if caseValidation == 1:
          print('Command successful finished!!!!', '\n')
        else:
          print("ERROR!!!, Point unreachable or the action could break the end effector", '\n')

if __name__ == '__main__':
    main()
    