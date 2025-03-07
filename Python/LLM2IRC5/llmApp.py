import trainingPrompts as trainingPrompts
from groq import Groq

client = Groq(api_key = "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")

def getResponse(prompts):
  try:
    completion = client.chat.completions.create(
      # model = 'llama-3.1-8b-instant',
      model = 'llama-3.3-70b-versatile',
      messages = prompts,
      temperature = 0.1,
      max_tokens = 1024,
      stream = True)
    response = "".join(chunk.choices[0].delta.content or '' for chunk in completion)
    return response
  except Exception as e:
    print(f'There is an error: {str(e)}')
    return None

def getNLValues(prompt):
  prompts = trainingPrompts.trainedPrompts.copy()
  prompts.append({'role': 'user', 'content': prompt})
  response = getResponse(prompts)
  return response
