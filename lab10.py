import requests
import pyttsx3
import pyaudio
from vosk import Model, KaldiRecognizer
import json
from datetime import datetime


class VoiceAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        self.model = Model("vosk-model-small-ru-0.22")
        self.recognizer = KaldiRecognizer(self.model, 16000)

        self.mic = pyaudio.PyAudio()
        self.stream = self.mic.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8192
        )

        self.current_user = None

    def speak(self, text):
        print(f"Ассистент: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        print("Слушаю...")
        while True:
            data = self.stream.read(4096, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                command = result.get('text', '').lower()
                if command:
                    print(f"Вы сказали: {command}")
                    return command

    def get_random_user(self):
        response = requests.get("https://randomuser.me/api/")
        if response.status_code == 200:
            self.current_user = response.json()['results'][0]
            return True
        return False

    def process_command(self, command):
        if not self.current_user and command not in ["создать", "выход"]:
            self.speak("Сначала создайте пользователя командой 'создать'")
            return

        if "создать" in command:
            if self.get_random_user():
                self.speak("Пользователь создан")
            else:
                self.speak("Ошибка при создании пользователя")

        elif "имя" in command:
            name = self.current_user['name']
            self.speak(f"{name['title']} {name['first']} {name['last']}")

        elif "страна" in command:
            self.speak(self.current_user['location']['country'])

        elif "анкета" in command:
            user = self.current_user
            profile = f"""
            Имя: {user['name']['first']} {user['name']['last']}
            Пол: {user['gender']}
            Возраст: {user['dob']['age']} лет
            Страна: {user['location']['country']}
            Email: {user['email']}
            Телефон: {user['phone']}
            """
            self.speak(profile)

        elif "сохранить" in command:
            self.save_user_photo()

        elif "выход" in command:
            self.speak("До свидания!")
            exit()

        else:
            self.speak("Не распознана команда, ошибка в запросе")

    def save_user_photo(self):
        if not self.current_user:
            return

        photo_url = self.current_user['picture']['large']
        response = requests.get(photo_url)

        if response.status_code == 200:
            filename = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            with open(filename, 'wb') as f:
                f.write(response.content)
            self.speak(f"Фото сохранено как {filename}")
        else:
            self.speak("Ошибка при сохранении фото")

    def run(self):
        self.speak("Голосовой ассистент запущен. Скажите 'создать' для начала.")
        while True:
            try:
                command = self.listen()
                self.process_command(command)
            except Exception as e:
                print(f"Ошибка: {e}")
                self.speak("Произошла ошибка, попробуйте еще раз")


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()
