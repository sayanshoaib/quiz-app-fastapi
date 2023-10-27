from fastapi import FastAPI, Depends, HTTPException
import db_models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List, Annotated
from api_models import QuestionBase, ChoiceBase

app = FastAPI()
db_models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/questions/{question_id")
async def get_questions(question_id: int, db: db_dependency):
    result = db.query(db_models.Questions).filter(db_models.Questions.id == question_id).first()
    if not result:
        raise HTTPException(status_code=404, detail=f"Question not found with id {question_id}")

    return result


@app.get("/choices/{question_id}")
async def get_choices(question_id: int, db: db_dependency):
    result = db.query(db_models.Choices).filter(db_models.Choices.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail=f"Question not found with id {question_id}")

    return result


@app.post("/questions/")
async def create_questions(question: QuestionBase, db: db_dependency):
    db_question = db_models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for choice in question.choices:
        db_choice = db_models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id
        )
        db.add(db_choice)

    db.commit()
