from fastapi import FastAPI,HTTPException, Depends
from database import SessionLocal, Account, Post, Comment
from schemas import CreateAccount, CreatePost, CreateComment
from sqlalchemy.exc import IntegrityError
from auth import hash_password

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
app = FastAPI()

@app.get("/accounts")
def get_account(db= Depends(get_db)):
    account = db.query(Account).all()
    return account

@app.post("/accounts")
def create_account(account:CreateAccount, db = Depends(get_db)):
    new_account = Account(name = account.name, 
                          email = account.email,
                          hashed_password = hash_password(account.hashed_password),
                          role = account.role)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


@app.get("/posts")
def get_posts(db = Depends(get_db)):
    posts = db.query(Post).all()    
    return posts
@app.post("/posts")
def create_post(post: CreatePost, db = Depends(get_db)):
    new_post = Post(title = post.title, content = post.content, account_id = post.author_id)
    db.add(new_post)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=404, detail="Account not found")
    db.refresh(new_post)
    return new_post
    

@app.get("/comments")
def get_comment(db = Depends(get_db)):
    comments = db.query(Comment).all()    
    return comments
@app.post("/comments")
def create_comment(comment: CreateComment, db = Depends(get_db)):
    new_comment = Comment(content = comment.content, post_id=comment.post_id, user_id = comment.user_id)
    db.add(new_comment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=404, detail="Post not found")
    db.refresh(new_comment)
    return new_comment

