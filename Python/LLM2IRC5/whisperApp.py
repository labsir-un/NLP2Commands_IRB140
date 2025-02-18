import os
import tempfile
import wave
import pyaudio
from groq import Groq
import keyboard

client = Groq(api_key = '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')

def recordAudio(secondRecording, msg):
  chunk = 1024
  frequency = 16000
  p = pyaudio.PyAudio()
  stream = p.open(format = pyaudio.paInt16, channels = 1, rate = frequency, input = True, frames_per_buffer = chunk,)
  frames = []
  print(msg)
  if secondRecording:
    for _ in range(0, int(frequency/chunk * secondRecording)):
      data = stream.read(chunk)
      frames.append(data)
  else:
    print('<<<<<<<<<<<<<<<<<ENTER PARA DETENER RECEPCIÓN DE ORDENES>>>>>>>>>>>>>>>>>')
    while True:
      data = stream.read(chunk)
      frames.append(data)
      if keyboard.is_pressed('enter'): break
  stream.stop_stream()
  stream.close()
  p.terminate()
  # Save and send basename
  with tempfile.NamedTemporaryFile(suffix = '.wav', delete = False) as audioTemp:
    wf = wave.open(audioTemp.name, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    wf.setframerate(frequency)
    wf.writeframes(b"".join(frames))
    wf.close()
  return audioTemp.name
  
def getTranscription(fileName):
  try:
    with open(fileName, 'rb') as file:
      transcription = client.audio.transcriptions.create(
        file = (os.path.basename(fileName), file.read()),
        model = 'whisper-large-v3',
        prompt = 'Ordenes a robot ABB-irb140',
        response_format = 'text',
        language = 'es',)
    return transcription
  except Exception as e:
    print(f'There is an error: {str(e)}')
    return None
