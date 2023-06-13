import os
import pyaudio
import pymorphy2
import pyttsx3
import requests
import translators as ts
import vosk
from random import choice


def get_currency_dict() -> dict:
    return requests.get(
        'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/rub.json',
        timeout=10
    ).json()


def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if record.AcceptWaveform(data) and len(data) > 0:
            answer = json.loads(record.Result())
            if answer['text']:
                yield answer['text']


def speak(say):
    tts.say(say)
    tts.runAndWait()


if __name__ == '__main__':
    morph = pymorphy2.MorphAnalyzer(lang='ru')
    tts = pyttsx3.init('sapi5')
    voices = tts.getProperty('voices')
    tts.setProperty('voices', 'ru')
    tts.setProperty('voice', next(filter(lambda voice: 'ru' in voice.name.lower(), voices)).id)
    model = vosk.Model(next(filter(lambda file_folder: 'ru' in file_folder, os.listdir())))
    record = vosk.KaldiRecognizer(model, 16000)
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    speak('День добрый')
    for text in listen():
        print(text)
        text = morph.parse(text)[0].normal_form
        if text == 'доллар':
            speak(f'Доллар стоит {1 / get_currency_dict()["rub"]["usd"]:.2f} рублей')
        elif text == 'евро':
            speak(f'Евро стоит {1 / get_currency_dict()["rub"]["usd"]:.2f} рублей')
        elif text == 'сохранить':
            data = get_currency_dict()
            with open(f'currency_{data["date"]}.csv', 'w', encoding='utf-8') as f:
                f.write('name,price\n')
                for key in data["rub"]:
                    f.write(f'{key},{data["rub"][key]}\n')
            speak('Файл сохранен')
        elif text == 'случайный':
            data = get_currency_dict()["rub"]
            key = choice(data.keys())
            if data[key] < 1.000001:
                speak(f'{key} стоит {1 / data[key]:.2f} рублей')
            else:
                speak(f'Рубль стоит {data[key]:2.f} {key}')
        elif text == 'стоп':
            speak('Всего доброго')
            break
        else:
            speak('Жду команды')
