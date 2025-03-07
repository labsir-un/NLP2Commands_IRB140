import socket
#Es necesario validar al pose en casos de move 1
from commandMapping import getArrayCommands, setUpCommands, NL2Array

lengths = [4, 4, 4, 12, 12, 12, 12, 1, 4]
# X, Y, Z, qw, q1, q2, q3, action, value

def socketMsg(command):
  stringCommand = ''
  for value, length in zip(command, lengths):
    aux = ''
    if value < 0:
        value = -value
        length = length - 1
        aux = '-'
    if value == 0:
       value = 0
    value = aux + str(value).rjust(length, '0')
    stringCommand = stringCommand + value
  return stringCommand

def main ():
  mySocket = socket.socket()
  # mySocket.connect(("127.0.0.1", 8000)) #Simulation
  mySocket.connect(("192.168.125.1", 8000)) #Real Robot
  ans = mySocket.recv(1024)
  print(ans)

  while True:
    rawCommands = getArrayCommands()
    # test = 'draw, none, 0, draw, none, 10, draw, none, 11, draw, none, 12, draw, none, 13, draw, none, 14, draw, none, 15, draw, none, 16, draw, none, 17, draw, none, 18, draw, none, 19, draw, none, 20, draw, none, 30, draw, none, 40, draw, none, 50, draw, none, 60, draw, none, 70, draw, none, 80, draw, none, 90'
    # rawCommands = NL2Array(test)
    commands = setUpCommands(rawCommands)
    print(commands)
    for command in commands:
        msg = socketMsg(command)
        mySocket.send(msg.encode())
        print(command)        
        print(msg)
        allGood = int(mySocket.recv(1024).strip())
        if allGood == 1: print('Command successful finished!!!!')
        elif allGood == 2: print("ERROR!!!, That action would break end effector")
        else: print("ERROR!!!, The arm can't reach that point")

if __name__ == '__main__':
    main()
