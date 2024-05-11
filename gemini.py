import google.generativeai as genai
import pyttsx3
import os
from PIL import ImageGrab, Image
from io import BytesIO
import time
import speech_recognition as sr
import random
import requests

# Função para reproduzir um texto usando TTS
def play_audio(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 250)  # ajuste a velocidade da fala conforme necessário
    engine.setProperty('voice', 'brazil')  # selecione a voz conforme necessário
    engine.say(text)
    engine.runAndWait()
    
# Crie um objeto de reconhecimento de voz
r = sr.Recognizer()

while "gemini_api_key" not in os.environ:
    play_audio("Insira sua chave da API do Jieminái.")
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
    system_instruction="Você é um chatbot!((Não utilize simbolos ou emojis de forma alguma!)). Só informe o que tiver certeza. Se for pedido para ver a tela do computador, envie somente o texto 'tkscreenshot' e nada mais, lembre-se que você tem acesso a tela do computador, para isso envie somente o texto 'tkscreenshot' e nada mais. Se for uma pergunta, pergunte ao final se pode ajudar com algo mais. Se o usuário informar que não precisa mais de ajuda, pergunte antes se ele quer que encerre o chat, caso ele responder sim envie o texto ((fecharchat))")
# Carregando modelo pro-vision
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
play_audio("Olá, como vai você? Meu nome é Jieminái, sou um modelo Lhama multimodal! Me faça uma pergunta ou converse comigo pelo Microfone! Ficarei feliz em te ajudar! Também posso transcrever e verificar imagens na tela do seu computador se me pedir! Apenas lembrissí de esperar eu terminar de falar para me perguntar novamente. No que posso te ajudar hoje?")


print("Diga algo no Microfone!")

# Função principal em loop
def chat_with_audio():
    while True:
        try:
            # Utilizando o Microfone no device padrão para ouvir o áudio
            with sr.Microphone() as source:
                audio = r.listen(source)
                # Enviando o áudio para a API gratuíta do Google para transcrição
                texto_transcrito = r.recognize_google(audio, language="pt-BR")
                
                # 3 textos de resposta após o usuário informar sua pergunta, para que ele saiba que foi escutado.
                textos_resposta = ["Entendi, já lhe ouvi. Aguarde um momento, por favor, que já lhe responderei.", "Entendi seu pedido, peço apenas um momento e já te respondo.", "Consegui te ouvir, Em um instante lhe respondo."]
                play_audio(random.choice(textos_resposta))
                
                # Request para o Gemini feita com base no áudio transcrito da pessoa.
                response = chat.send_message(texto_transcrito)
                
                # Texto informado ao Gemini nas instruções para ser enviado caso o usuário não precisar mais de ajuda e quiser encerrar o chat.
                if 'fecharchat' in response.text:
                    print("Encerrando o chat...")
                    play_audio("Estarei encerrando nosso chat, se precisar de ajuda novamente é só me abrir!")
                    break
                
                # If que realiza o screenshot da tela se informado pelo usuário e envia ao modelo Pro-Vision, para que ele consiga ler ou identificar o que está na tela do usuário.
                if 'tkscreenshot' in response.text:
                    play_audio("Só um momento, estou verificando a sua tela")
                    screenshot = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
                    stream = BytesIO()
                    screenshot.save(stream, format="PNG")
                    stream.seek(0)
                    img = Image.open(stream)
                    response = model_vision.generate_content([texto_transcrito, img], stream=True)
                    response.resolve()
                    
                    # Removendo asteríscos e jogo da velha do resultado, para que o TTS não precise dizer.
                    texto_limpo = response.text.replace("#", "")
                    texto_limpo = response.text.replace("*", "")
                    print("Resposta do bot:", texto_limpo)
                    play_audio(response.text)
                    play_audio("Posso ajudar em algo mais?")
                    
                # Else caso não seja necessário utilizar o modelo Pro-Vision
                else:
                    print("Resposta do bot:", response.text)
                    texto_final = response.text
                    # Removendo asteríscos e jogo da velha do resultado, para que o TTS não precise dizer.
                    texto_limpo = response.text.replace("#", "")
                    texto_limpo = response.text.replace("*", "")
                    
                    # Audio com o resultado final é mandado para o TTS sintetizar.
                    play_audio(texto_limpo)
        # Handling de erros
        except sr.UnknownValueError:
            play_audio("Desculpe, não consegui entender o que disse ou você não disse nada, poderia repetir?")
        except sr.RequestError as e:
            play_audio("Desculpe, parece que não consegui atender sua requisição, poderia tentar novamente?")

chat_with_audio()