import os
import json
import requests
import sqlite3
from setup_db import add_idea, get_ideas, delete_idea
from web_app import enviar_email
import dotenv
import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

# Load environment variables from a .env file
dotenv.load_dotenv()

# Define the endpoint for the audio transcription API
url = 'https://api.openai.com/v1/audio/transcriptions'

# API Key from OpenAI
api_key = os.getenv('OPENAI_KEY')

openai.api_key = api_key

# Directory to save audio files
audio_directory = 'audio_transcricao'

# Create the directory if it doesn't exist
if not os.path.exists(audio_directory):
    os.makedirs(audio_directory)

# Function to show the main menu
def show_menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Diga sua ideia", callback_data='diga_ideia')],
        [InlineKeyboardButton("Suas ideias", callback_data='suas_ideias')],
        [InlineKeyboardButton("Apague ideias", callback_data='apague_ideias')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text('Escolha uma opção:', reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text('Escolha uma opção:', reply_markup=reply_markup)

# Function to capture a new idea
def diga_ideia(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Envie sua ideia:")
    context.user_data['awaiting_idea'] = True
    context.user_data['awaiting_day_time'] = False  # Reset any previous day/time awaiting status

def get_completion(prompt, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def salvar_ideia(update: Update, context: CallbackContext) -> None:
    if 'awaiting_day_time' in context.user_data and context.user_data['awaiting_day_time']:
        if update.message and update.message.text:
            data_hora = update.message.text.strip()
            update.message.reply_text(f'Data e hora recebidas: {data_hora}')
            context.user_data['awaiting_day_time'] = False
            ask_for_more(update, context)
        else:
            update.message.reply_text("Por favor, envie a data e hora no formato correto.")
        return

    if 'awaiting_idea' in context.user_data and context.user_data['awaiting_idea']:
        if update.message.voice:
            context.user_data['awaiting_idea'] = False  # Marque como concluída a captura da ideia
            file_id = update.message.voice.file_id
            new_file = context.bot.get_file(file_id)
            file_path = os.path.join(audio_directory, f"{file_id}.ogg")
            new_file.download(file_path)
            update.message.reply_text('Seu arquivo de áudio foi salvo!')

            headers = {
                'Authorization': f'Bearer {api_key}'
            }
            files = {
                'file': (file_id, open(file_path, 'rb'), 'audio/ogg')
            }
            data = {
                'model': 'whisper-1'
            }

            try:
                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    transcription = response.json()
                    transcribed_text = transcription.get('text', '')

                    prompt = f"""
                    Ajude na construção e fomentação da ideia: "{transcribed_text}", além disso ela deve responder os seguintes questionamentos e retornar no formato JSON:
                    {{
                        "descricao": "Por favor, descreva a ideia em detalhes. Certifique-se de que a descrição tenha no mínimo 100 palavras.",
                        "impacto": "Se essa ideia for aplicada, qual será o impacto gerado? Detalhe os possíveis resultados e efeitos dessa implementação.",
                        "recursos": "Quais são os recursos necessários para implementar essa ideia? Responda de forma detalhada, sem usar tópicos ou listas.",
                        "beneficios": "Quais são os benefícios que essa ideia pode trazer? Descreva-os de forma contínua e sem listar em tópicos.",
                        "resumo": "Com base nas informações fornecidas nas seções anteriores, incluindo a descrição da ideia e as respostas detalhadas, crie um resumo completo de pelo menos 300 palavras.",
                        "titulo": "Com base em todas as informações fornecidas, sugira um título adequado que resuma a ideia e seu impacto com no máximo 8 palavras."
                    }}
                    """
                    response = get_completion(prompt)
                    try:
                        response_json = json.loads(response)
                        titulo = response_json.get("titulo")
                        descricao = response_json.get("descricao")
                        impacto = response_json.get("impacto")
                        recursos = response_json.get("recursos")
                        beneficios = response_json.get("beneficios")
                        resumo = response_json.get("resumo")
                        
                        user_id = update.message.from_user.id
                        ideia_id = add_idea(user_id=user_id, idea=transcribed_text, audio_file=file_path, transcription=transcribed_text, titulo=titulo, descricao=descricao, impacto=impacto, recursos=recursos, beneficios=beneficios, observacao=None, resumo=resumo, data_inicio=None, data_implementacao=None, visibilidade=None)

                        with open('transcription.json', 'w', encoding='utf-8') as json_file:
                            json.dump(transcription, json_file, ensure_ascii=False, indent=4)
                        print("Transcrição salva com sucesso em transcription.json")
                    except Exception as e:
                        print(f"Erro ao separar os campos: {e}")

                    context.user_data['ultima_ideia_id'] = ideia_id  # Salvar o ID da ideia para referência posterior
                    perguntar_visibilidade(update, context)
                else:
                    print(f"Erro na transcrição: {response.status_code}")
                    print(response.text)
            except Exception as e:
                print(f"Erro ao tentar fazer a solicitação: {e}")
            
            finally:
                files['file'][1].close()

        elif update.message.text:
            context.user_data['awaiting_idea'] = False  # Marque como concluída a captura da ideia
            idea = update.message.text.strip()

            prompt = f"""
            Ajude na construção e fomentação da ideia: "{idea}", além disso ela deve responder os seguintes questionamentos e retornar no formato JSON:
            {{
                "descricao": "Por favor, descreva a ideia em detalhes. Certifique-se de que a descrição tenha no mínimo 100 palavras.",
                "impacto": "Se essa ideia for aplicada, qual será o impacto gerado? Detalhe os possíveis resultados e efeitos dessa implementação.",
                "recursos": "Quais são os recursos necessários para implementar essa ideia? Responda de forma detalhada, sem usar tópicos ou listas.",
                "beneficios": "Quais são os benefícios que essa ideia pode trazer? Descreva-os de forma contínua e sem listar em tópicos.",
                "resumo": "Com base nas informações fornecidas nas seções anteriores, incluindo a descrição da ideia e as respostas detalhadas, crie um resumo completo de pelo menos 300 palavras.",
                "titulo": "Com base em todas as informações fornecidas, sugira um título adequado que resuma a ideia e seu impacto com no máximo 8 palavras."
            }}
            """
            response = get_completion(prompt)
            try:
                response_json = json.loads(response)
                titulo = response_json.get("titulo")
                descricao = response_json.get("descricao")
                impacto = response_json.get("impacto")
                recursos = response_json.get("recursos")
                beneficios = response_json.get("beneficios")
                resumo = response_json.get("resumo")

                user_id = update.message.from_user.id
                ideia_id = add_idea(user_id=user_id, idea=idea, audio_file=None, transcription=None, titulo=titulo, descricao=descricao, impacto=impacto, recursos=recursos, beneficios=beneficios, observacao=None, resumo=resumo, data_inicio=None, data_implementacao=None, visibilidade=None)
                update.message.reply_text('Sua ideia foi salva!')
                
                context.user_data['ultima_ideia_id'] = ideia_id  # Salvar o ID da ideia para referência posterior
                perguntar_visibilidade(update, context)
            except Exception as e:
                print(f"Erro ao separar os campos: {e}")

    else:
        show_menu(update, context)

# Function to ask for visibility
def perguntar_visibilidade(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Público", callback_data='Público')],
        [InlineKeyboardButton("Privado", callback_data='Privado')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text('Você deseja que essa ideia seja pública ou privada?', reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text('Você deseja que essa ideia seja pública ou privada?', reply_markup=reply_markup)

# Function to set visibility
def definir_visibilidade(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    visibilidade = query.data  # 'publica' ou 'privada'
    ideia_id = context.user_data.get('ultima_ideia_id')

    if ideia_id:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE ideas SET visibilidade=? WHERE id=?", (visibilidade, ideia_id))
        conn.commit()
        conn.close()

        query.edit_message_text(f"A visibilidade da ideia foi definida como: {visibilidade}.")
        
        # Agora, perguntar sobre a data e hora
        keyboard = [
            [InlineKeyboardButton("Sim", callback_data='definir_dia_hora')],
            [InlineKeyboardButton("Não", callback_data='skip_day_time')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Deseja definir um dia e hora para esta ideia?', reply_markup=reply_markup)
        context.user_data['awaiting_day_time'] = True

# Function to display saved ideas
def suas_ideias(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    ideas = get_ideas(user_id)
    
    message = ""
    if ideas:
        for idea in ideas:
            idea_text = idea[1] if idea[1] else idea[2][:50]
            message += f"Ideia: {idea_text}\n"
            message += "\n"
    else:
        message = "Você não tem ideias salvas."
    
    keyboard = [
        [InlineKeyboardButton("Sim", callback_data='show_menu')],
        [InlineKeyboardButton("Não", callback_data='end')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=message.strip())
    query.message.reply_text('Deseja fazer mais alguma operação?', reply_markup=reply_markup)

# Function to delete ideas
def apague_ideias(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    ideas = get_ideas(user_id)
    
    if ideas:
        keyboard = []
        for idea in ideas:
            idea_text = idea[1] if idea[1] else idea[2][:50]
            button_text = f"Excluir: {idea_text}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f'excluir_ideia_{idea[0]}')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Escolha a ideia que deseja excluir:", reply_markup=reply_markup)
    else:
        query.edit_message_text(text="Você não tem ideias salvas.")
        ask_for_more(query, context)

# Function to delete a specific idea
def excluir_ideia(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    try:
        idea_id = int(query.data.split('_')[-1])
        
        delete_idea(idea_id)  # Usando uma função de exclusão no setup_db.py para deletar a ideia

        query.edit_message_text(text="Ideia excluída com sucesso!")
    except ValueError as e:
        query.edit_message_text(text="Erro ao excluir a ideia. Tente novamente.")
        print(f"Erro ao excluir a ideia: {e}")

    ask_for_more(query, context)

# Function to ask for more operations
def ask_for_more(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Sim", callback_data='show_menu')],
        [InlineKeyboardButton("Não", callback_data='end')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text('Você quer realizar outra operação?', reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text('Você quer realizar outra operação?', reply_markup=reply_markup)

# Function to set day and time
def definir_dia_hora(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Por favor, digite o dia e a hora (formato: DD/MM/YYYY HH:MM):")
    context.user_data['awaiting_day_time'] = True

# Function to handle button clicks
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query.data == 'diga_ideia':
        diga_ideia(update, context)
    elif query.data == 'suas_ideias':
        suas_ideias(update, context)
    elif query.data == 'apague_ideias':
        apague_ideias(update, context)
    elif query.data.startswith('excluir_ideia_'):
        excluir_ideia(update, context)
    elif query.data == 'show_menu':
        show_menu(update, context)
    elif query.data == 'end':
        query.edit_message_text(text="Obrigado por usar o bot! Até mais!")
    elif query.data == 'definir_dia_hora':
        definir_dia_hora(update, context)
    elif query.data == 'skip_day_time':
        ask_for_more(query, context)
    elif query.data in ['Público', 'Privado']:
        definir_visibilidade(update, context)

# Main function
def main() -> None:
    updater = Updater(os.getenv('TELEGRAM_BOT_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("start", show_menu))
    dispatcher.add_handler(MessageHandler(Filters.voice | Filters.text, salvar_ideia))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, lambda update, context: show_menu(update, context)))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
