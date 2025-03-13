from auxConstants import CLIENT, CONTEXT_PROMPTS
import streamlit as st

def get_response(prompts):
  completion = CLIENT.chat.completions.create(model = 'llama-3.3-70b-versatile',
                                              msg = prompts,
                                              temperature = 0.01,
                                              max_tokens = 1024,
                                              stream = True)
  response = "".join(chunk.choices[0].delta.content or '' for chunk in completion)
  return response

def chat():
  st.title('Chat con Llama 3.3')
  st.write("Bienvenidos al chat con IA! Escribe 'exit' para terminar la conversación.")
  if 'prompts' not in st.session_state:
    st.session_state['prompts'] = CONTEXT_PROMPTS

  def submit():
    user_input = st.session_state.user_input
    if user_input.lower() == 'exit':
      st.write('Gracias por chatear! ¡Adios!')
      st.stop()
    
    st.session_state['prompts'].append({'role': 'user', 'content': user_input})
    
    with st.spinner("Obteniendo respuesta..."):
      ai_response = get_response(st.session_state['prompts'])
      st.session_state['prompts'].append({'role': 'assistant', 'content': ai_response})
      print(st.session_state['prompts'])
    
    st.session_state.user_input = ''

  for prompt in st.session_state['prompts']:
    role = 'Tú' if prompt['role'] == 'user' else 'Bot'
    st.write(f"**{role}:** {prompt['content']}")
  
  with st.form(key = 'chat_form', clear_on_submit = True):
    st.text_input("Tú:", key = 'user_input')
    submit_button = st.form_submit_button(label = 'Enviar', on_click = submit)

if __name__ == "__main__":
  chat()
