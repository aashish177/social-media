from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from random import randint
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

# while True:
try:
    conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='Roundrock#1378', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print ("Database connection successful!")
    
except Exception as error:
    print('Connection to database failed :(')
    print('Error: ', error)

my_posts = [{"title": "Title of post 1", "content": "Content of post 1", "id": 1},
            {"title": "Title of post 2", "content": "Content of post 2", "id": 2}]

def find_post(id):
    for post in my_posts:
        if post["id"] == int(id):
            return post

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == int(id):
            return i

@app.get("/")
def root():
    return {"Hello! Welcome to my API"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts """)
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"Data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()

    # post_dict = post.dict()
    # post_dict["id"] = randint(1, 1000000)
    # my_posts.append(post_dict)
    # conn.commit()
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data":new_post}

@app.get("/posts/{id}")
def get_post(id:int, Response: Response, db: Session = Depends(get_db)):
    # post = find_post(id)
    # cursor.execute("""SELECT * FROM posts WHERE id=%s""", (str(id)))
    # post = cursor.fetchone()
    
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    return {"post detail" : post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id)))
    # deleted_post = cursor.fetchone()
    # index = find_index_post(id)
    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} does not exist")
    # my_posts.pop(index)
    post.delete(synchronize_session=False)
    db.commit()

@app.put("/posts/{id}")
def update_post(id:int, updated_post: Post, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    # index = find_index_post(id)
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    post = post_query.first()

    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"post with id {id} does not exist")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    
    # post_dict = post.dict()
    # post_dict["id"] = id
    # my_posts[index] = post_dict

    return {"message: ": "Post updated successfully", "data":post}