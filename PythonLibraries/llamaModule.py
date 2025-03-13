from auxConstants import CLIENT, CONTEXT_PROMPTS

# Send prompt to Llama
def llamaRequest(prompts): 
  completion = CLIENT.chat.completions.create(messages = prompts,
                                              model = 'llama-3.3-70b-versatile',
                                              temperature = 0.1,
                                              max_tokens = 1024,
                                              stream = True)
  response = "".join(chunk.choices[0].delta.content or '' for chunk in completion)
  return response

# Main function Llama module
def getInstructionsValues(prompt):
  prompts = CONTEXT_PROMPTS.copy()
  prompts.append({'role': 'user', 'content': prompt})
  instructionValues = llamaRequest(prompts).lower()
  return instructionValues
