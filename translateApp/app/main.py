from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
import schemas, crud, database
import models
from database import get_db, engine, SessionLocal
from utily import perform_translation
from typing import List
import uuid


models.Base.metadata.create_all(bind=engine)
app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

#-----------------------------------------------#

@app.get('/index', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request":request})

# @app.post("/translate", response_model=schemas.TaskResponse)
# def translate(request: schemas.TranslationRequest, db: Session = Depends(get_db)):
#     task = crud.create__translation_task(db, request.text, request.languages)

@app.post("/translate", response_model=schemas.TaskResponse)
def get_translate(request: schemas.TranslationRequest, backgroud_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task = crud.create__translation_task(db, request.text, request.languages)
    backgroud_tasks.add_task(perform_translation, task.id, request.text, request.languages, db)
    return {"task_id":{task.id}}

@app.get("/translate/{task_id}", response_model=schemas.TranslationStatus)
def get_translate(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_translation_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return {"task_id":task.id, "status":task.status, "translation":task.translations}

@app.get("/translate/content/{task_id}")
def get_translate_content(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_translation_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task