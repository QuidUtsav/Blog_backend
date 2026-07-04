from fastapi import FastAPI,HTTPException, Depends
from database import SessionLocal, Account, Post, Comment
from schemas import CreateAccount, CreatePost, CreateComment, AccountResponse,LoginRequest
from sqlalchemy.exc import IntegrityError
from auth import hash_password,verify_password,create_access_token
from auth import get_current_account
from fastapi.security import OAuth2PasswordRequestForm
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
app = FastAPI()

@app.get("/accounts",response_model=list[AccountResponse])
def get_account(db= Depends(get_db)):
    account = db.query(Account).all()
    return account

@app.post("/accounts", response_model= AccountResponse)
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
def create_post(post: CreatePost, db = Depends(get_db), current_acc = Depends(get_current_account)):
    if current_acc.role !="author":
        raise HTTPException(status_code=403 , detail="only authors can create post.")
    
    new_post = Post(title = post.title, content = post.content, author_id = current_acc.id)
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
def create_comment(comment: CreateComment, db = Depends(get_db), curent_acc = Depends(get_current_account)):
    if (curent_acc.role != "user" and curent_acc.role != "author"):
        raise HTTPException(status_code=403, detail="You need to login to comment.")
    new_comment = Comment(content = comment.content, post_id=comment.post_id, user_id = curent_acc.id)
    db.add(new_comment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=404, detail="Post not found")
    db.refresh(new_comment)
    return new_comment

@app.post("/login")
def login(form_data :OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    account = db.query(Account).filter(Account.email == form_data.username).first()
    
    if account is None:
        raise HTTPException(status_code=404, detail="account not found")
    
    else:
        if verify_password(form_data.password, account.hashed_password):
            token = create_access_token({"sub": str(account.id)})
            return {"access_token": token, "token_type": "bearer", "account_type":account.role}
        else:
            raise HTTPException(status_code=401, detail="password incorrect.")
        
@app.put("/posts/{post_id}")
def update_post(post_id:int, updated_post: CreatePost, db =Depends(get_db), current_acc = Depends(get_current_account)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post not found.")
    
    if post.author_id !=current_acc.id:
        raise HTTPException(status_code=403, detail="you can only edit your own posts.")
    
    post.title = updated_post.title
    post.content=updated_post.content
    db.commit()
    db.refresh(post)
    return post
    
@app.delete("/posts/{post_id}")
def delete_post(post_id:int , db=Depends(get_db), current_account=Depends(get_current_account)):
    post = db.query(Post).filter(post_id==Post.id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="no post found")
    if post.author_id != current_account.id:
        raise HTTPException(status_code=403, detail="you can only delete you own post")
    db.delete(post)
    db.commit()
    return "post deleted successfully"

@app.delete("/comments/{comment_id}")
def delete_comment(comment_id:int, db=Depends(get_db),current_acc = Depends(get_current_account)):
    comment = db.query(Comment).filter(Comment.id==comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404 , detail="comment not found")
    if current_acc.id != comment.user_id:
        raise HTTPException(status_code=403, detail="you can only delete comment you wrote")
    db.delete(comment)
    db.commit()
    return "comment successfully deleted"

@app.put("/comments/{comment_id}")
def edit_comment(comment_id:int, edited_comment:CreateComment, db = Depends(get_db),current_account = Depends(get_current_account)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="no comment found.")
    if comment.user_id != current_account.id:
        raise HTTPException(status_code=403, detail="you can only edit your own comment")
    comment.content = edited_comment.content
    db.commit()
    db.refresh(comment)
    
    return comment
    