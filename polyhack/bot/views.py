# therapy_bot_project/bot/views.py
import os
import random
import requests
import pyttsx3
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.templatetags.static import static
from django.http import HttpRequest

class TherapyBot:
    def __init__(self):
        self.speaker = pyttsx3.init()
        self.speaker.setProperty('rate', 150)
    
    def get_chat_response(self, message):
        API_URL = "https://api.openai.com/v1/chat/completions"
        API_KEY = os.getenv('OPENAI_API_KEY')  


        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are an empathetic AI therapist. Respond with compassion, insight, and emotional support. Be concise and caring."},
                {"role": "user", "content": message}
            ]
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as error:
            print(f"Error in get_chat_response: {error}")
            return None

    def text_to_speech(self, text):
        try:
            audio_dir = settings.AUDIO_ROOT
            os.makedirs(audio_dir, exist_ok=True)
            audio_path = os.path.join(audio_dir, f'speech_{random.randint(1, 10000)}.mp3')
            
            self.speaker.setProperty('rate', 150)
            self.speaker.setProperty('volume', 1.0)
            
            self.speaker.save_to_file(text, audio_path)
            self.speaker.runAndWait()
            
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                return os.path.basename(audio_path)
            else:
                return None
        
        except Exception as e:
            print(f"TTS Error: {e}")
            return None

bot = TherapyBot()

def home(request):
    return render(request, 'bot.html')

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if user_message:
                # Use the TherapyBot to generate a response
                response_text = bot.get_chat_response(user_message)
                
                # Generate audio for the response
                audio_filename = bot.text_to_speech(response_text)
                
                # Construct the audio URL
                audio_url = f'/audio/{audio_filename}' if audio_filename else None

                return JsonResponse({
                    'response': response_text,
                    'audio_url': audio_url
                })
            else:
                return JsonResponse({'error': 'No message provided'}, status=400)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def serve_audio(request, filename):
    audio_path = os.path.join(settings.AUDIO_ROOT, filename)
    if os.path.exists(audio_path):
        with open(audio_path, 'rb') as file:
            response = JsonResponse({'audio_file': file.read().decode('latin-1')})
            response['Content-Type'] = 'audio/mpeg'
            return response
    return JsonResponse({'error': 'File not found'}, status=404)