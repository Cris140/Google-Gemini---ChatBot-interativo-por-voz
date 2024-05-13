import google.generativeai as genai
import pyttsx3
import os
from PIL import ImageGrab, Image
from io import BytesIO
import time
import speech_recognition as sr
import random
import requests
import re

# Função para reproduzir um texto usando TTS
def play_audio(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 250)  # ajuste a velocidade da fala conforme necessário
    engine.setProperty('voice', 'brazil')  # selecione a voz conforme necessário
    engine.say(text)
    engine.runAndWait()
    
# Cria um objeto de reconhecimento de voz
r = sr.Recognizer()
with sr.Microphone() as source:
    play_audio("Vou calibrar o seu Microfone, fique em silêncio por um segundo para que eu possa ajustar o sinal para o volume ambiente.")
    r.adjust_for_ambient_noise(source)

while "gemini_api_key" not in os.environ:
    play_audio("Pronto, agora insira sua chave da API do jêmini.")
    api_key = input("Cole somente sua API key do Gemini obtida no AI Studio: ")
    url = f'https://generativelanguage.googleapis.com/v1/models?key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        play_audio("Perfeito, a chave está correta. Vamos iniciar nosso chat!")
        os.environ["gemini_api_key"] = api_key
        genai.configure(api_key=os.environ["gemini_api_key"])
        # Comando para limpar a tela
        os.system('cls||clear')
    else:
        play_audio("Parece que sua chave não é válida, tente novamente.")

# Carregando modelo 1.5 do Gemini
model=genai.GenerativeModel(
    model_name='models/gemini-1.5-pro-latest',
    system_instruction="Você é um chatbot!((Não utilize simbolos ou emojis de forma alguma!)). Só informe o que tiver certeza e seja breve. Se for pedido para ver a tela do computador, envie somente o texto 'tkscreenshot' e nada mais, lembre-se que você tem acesso a tela do computador, para isso envie somente o texto 'tkscreenshot' e nada mais. Se for uma pergunta, pergunte ao final 'posso ajudar com algo mais?'. Se o usuário informar que não precisa mais de ajuda, pergunte antes se ele quer que encerre o chat, caso ele responder sim envie o texto ((fecharchat))")

# Carregando modelo pro-vision para imagens
model_vision = genai.GenerativeModel('gemini-pro-vision')

# Inicializando o modo chat para que ele guarde o histórico das mensagens
chat = model.start_chat(history=[])
chat
message = ""

# Tela de Boas Vindas!
ascii_art = r'''                     
 $$$$$$\                                $$\                  $$$$$$\                          $$\           $$\ 
$$  __$$\                               $$ |                $$  __$$\                         \__|          \__|
$$ /  \__| $$$$$$\   $$$$$$\   $$$$$$\  $$ | $$$$$$\        $$ /  \__| $$$$$$\  $$$$$$\$$$$\  $$\ $$$$$$$\  $$\ 
$$ |$$$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$ |$$  __$$\       $$ |$$$$\ $$  __$$\ $$  _$$  _$$\ $$ |$$  __$$\ $$ |
$$ |\_$$ |$$ /  $$ |$$ /  $$ |$$ /  $$ |$$ |$$$$$$$$ |      $$ |\_$$ |$$$$$$$$ |$$ / $$ / $$ |$$ |$$ |  $$ |$$ |
$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |$$   ____|      $$ |  $$ |$$   ____|$$ | $$ | $$ |$$ |$$ |  $$ |$$ |
\$$$$$$  |\$$$$$$  |\$$$$$$  |\$$$$$$$ |$$ |\$$$$$$$\       \$$$$$$  |\$$$$$$$\ $$ | $$ | $$ |$$ |$$ |  $$ |$$ |
 \______/  \______/  \______/  \____$$ |\__| \_______|       \______/  \_______|\__| \__| \__|\__|\__|  \__|\__|
                              $$\   $$ |                                                                        
                              \$$$$$$  |                                                                        
                               \______/                                        
                               

Projeto de Chatbot interativo por voz utilizando Gemini, acessível a deficientes visuais.
Criado por Cristhian Reinhard (https://github.com/Cris140)
 '''
 
print(ascii_art)

# Áudio de introdução. Os erros ortográficos são para que o TTS consiga dizer corretamente.
play_audio("Olá! Sou o Jiemini, um modelo Lhama multimodal. Posso responder suas perguntas e ajudar você. Use o microfone para conversar comigo ou me peça para transcrever e verificar imagens no seu computador. Apenas espere eu terminar de falar antes de fazer outra pergunta. Para me chamar, basta dizer Jiemini e fazer sua pergunta direta. Estou aqui para ajudar!")


print("Diga algo no Microfone!")
activated = False
def chat_with_audio():
    global activated  # Declarando activated como global
    while True:
        try:
            # Inicia a captura de áudio do microfone
            with sr.Microphone() as source:  
                # Escuta o áudio do microfone
                audio = r.listen(source)
                # Transcreve o áudio em texto usando a API do Google com idioma definido para Português do Brasil
                texto_transcrito = r.recognize_google(audio, language="pt-BR")              
                
                # Verifica se a palavra "gemini" está presente no texto transcrito, ignorando maiúsculas e minúsculas
                if 'gemini' in texto_transcrito.lower():
                    # Encontra o índice da palavra "gemini" no texto transcrito
                    gemini_index = texto_transcrito.lower().index('gemini')
                    # Extrai o texto após a palavra "gemini" e remove espaços em branco
                    text_after_gemini = texto_transcrito[gemini_index + len('gemini'):].strip()
                    
                    # Verifica se há texto após a palavra "gemini"
                    if text_after_gemini:
                        try:
                            # Define o texto transcrito como o texto após "gemini"
                            texto_transcrito = text_after_gemini
                            # Ativa a flag de atividade
                            activated = True
                        # Trata o erro quando a API de reconhecimento de fala não reconhece o áudio
                        except sr.UnknownValueError:
                            play_audio("Você não disse nada ou não consegui entender o que me pediu, se precisar de mim novamente só me chamar.")
                        # Trata o erro quando há um problema na requisição à API de reconhecimento de fala
                        except sr.RequestError as e:
                            play_audio("Desculpe, parece que não consegui atender sua requisição, poderia tentar novamente?")
                    else:
                        # Ativa a flag de atividade
                        activated = True
                        # Informa ao usuário que mencionou "gemini" mas não fez nenhuma pergunta
                        play_audio("Você mencionou jiemini, mas não fez nenhuma pergunta. Como posso ajudar?")
                
                # Verifica se a flag de atividade está ativada
                if activated:
                    try:
                        # Se não houver texto após "gemini", escuta novamente o áudio do microfone
                        if not text_after_gemini:
                            audio = r.listen(source)
                            texto_transcrito = r.recognize_google(audio, language="pt-BR")
                        
                        # Define respostas possíveis para serem reproduzidas ao usuário
                        textos_resposta = ["Entendi, consegui te ouvir. Só um momento.", "Entendi seu pedido, peço apenas um momento.", "Consegui te ouvir, Em um instante lhe respondo."]
                        # Reproduz uma resposta aleatória
                        play_audio(random.choice(textos_resposta))
                        
                        # Envia o texto transcrito para o chatbot e recebe a resposta
                        response = chat.send_message(texto_transcrito)
                        
                        # Verifica se o texto da resposta indica o fechamento do chat
                        if 'fecharchat' in response.text:
                            # Informa ao usuário que o chat foi encerrado
                            play_audio("Tudo bem, se precisar de ajuda novamente é só me chamar!")    
                            print("Aguardando ser chamado novamente...")                  
                            pass
                        # Verifica se o texto da resposta indica a necessidade de capturar uma captura de tela
                        if 'tkscreenshot' in response.text:
                            # Informa ao usuário que está verificando a tela para capturar uma screenshot
                            play_audio("Só um momento, estou verificando a sua tela")
                            # Captura uma screenshot da tela
                            screenshot = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
                            stream = BytesIO()
                            screenshot.save(stream, format="PNG")
                            stream.seek(0)
                            img = Image.open(stream)
                            # Gera conteúdo com o texto transcrito e a screenshot e envia para o modelo de visão
                            response = model_vision.generate_content([texto_transcrito, img], stream=True)
                            response.resolve()
                            # Remove caracteres especiais da resposta e a reproduz
                            texto_limpo = response.text.replace("#", "")
                            texto_limpo = response.text.replace("*", "")
                            print("Resposta do bot:", texto_limpo)
                            play_audio(response.text)
                        else:                         
                            # Obtém o texto final da resposta
                            texto_final = response.text
                            # Remove caracteres especiais do texto final
                            texto_limpo = response.text.replace("#", "")
                            texto_limpo = response.text.replace("*", "")
                            # Verifica se a resposta indica o fechamento do chat
                            if '((fecharchat))' in texto_limpo:
                                pass
                            else:
                                # Imprime a resposta do chatbot
                                print("Resposta do bot:", response.text)  
                                # Reproduz o texto final da resposta
                                play_audio(texto_limpo)
                    except sr.UnknownValueError:
                        # Trata o erro quando a API de reconhecimento de fala não reconhece o áudio
                        play_audio("Você não disse nada ou não consegui entender o que me pediu, se precisar de mim novamente só me chamar.")
                    except sr.RequestError as e:
                        # Trata o erro quando há um problema na requisição à API de reconhecimento de fala
                        play_audio("Desculpe, parece que não consegui atender sua requisição, poderia tentar novamente?")
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            pass


chat_with_audio()