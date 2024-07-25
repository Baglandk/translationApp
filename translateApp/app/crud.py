from sqlalchemy.orm import Session
import models


def create__transllation_task(db:Session, text: str, languages:list):
    task = models.TranslationTask(text=text, languages=languages)