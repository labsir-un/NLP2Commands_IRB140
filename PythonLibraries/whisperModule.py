from auxConstants import CLIENT
import tempfile
import keyboard
import pyaudio
import wave
import os

# Frequency for audio and temporal file
frequency = 16000

# Temporal files, because Whisper gonna need constantly entries
def createTemporalFile(frames):
  with tempfile.NamedTemporaryFile(suffix = '.wav', delete = False) as file:
    waveFile = wave.open(file.name, 'wb')
    waveFile.setnchannels(1)
    waveFile.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    waveFile.setframerate(frequency)
    waveFile.writeframes(frames)
    waveFile.close()
  return file.name

def recordAudio(recordingSeconds, message):
  # Audio configuration
  chunk = 1024
  audioInstance = pyaudio.PyAudio()
  stream = audioInstance.open(format = pyaudio.paInt16,
                              channels = 1,
                              rate = frequency,
                              input = True,
                              frames_per_buffer = chunk)
  frames = []
  # Show audio instance message
  print(message)

  iterations = int(frequency / chunk * recordingSeconds) if recordingSeconds else None

  while iterations is None or iterations > 0:
    data = stream.read(chunk)
    frames.append(data)

    if iterations:
      iterations -= 1
    elif iterations is None and keyboard.is_pressed("enter"):
      break

  stream.stop_stream()
  stream.close()
  audioInstance.terminate()
  frames = b"".join(frames)
  return frames

# Send audio to Whisper
def whisperRequest(fileName):
  with open(fileName, 'rb') as file:
    transcription = CLIENT.audio.transcriptions.create(file = (os.path.basename(fileName), file.read()),
                                                        model = 'whisper-large-v3',
                                                        prompt = 'Ordenes a robot ABB-irb140',
                                                        response_format = 'text',
                                                        # If u want I could be in english
                                                        language = 'es')
  return transcription

# Main function Whisper module
def getTranscription(recordingSeconds, message):
  audioFrames = recordAudio(recordingSeconds, message)
  fileName = createTemporalFile(audioFrames)
  transcription = whisperRequest(fileName)
  return transcription

# Credits to Código Espinoza - Automatiza tu vida https://www.youtube.com/@CodigoEspinoza