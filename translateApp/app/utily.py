import openai
from sqlalchemy.orm import Session
from crud import update_translation_task
from dotenv import load_dotenv
from groq import Groq

import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPEN_API_KEY")

client = Groq(
    api_key = OPENAI_API_KEY,
)

def perform_translation(task:int, text: str, languages: list, db:Session):
    translations = {}
    for lang in languages:
        try:
            chat_completion = client.chat.completions.create(
                        messages = [
                            {
                            "role": "system",
                            "content": f"You are a helpful assistant that translate text to the language: {lang}"
                            },
                            {
                                "role":"user",
                                "content": text
                            }
                        ],
                        models = "llama3-8b-8192",
                    )

            translated_text = chat_completion.choices[0].message.content.strip()
            translations[lang] = translated_text
        except Exception as e:
            print(f"Error translating to {lang}: {e}")
            translations[lang] = f"Error: {e}"
        update_translation_task(db, task, translations)
