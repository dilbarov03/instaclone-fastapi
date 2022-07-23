from fastapi import HTTPException, status
from routers.schemas import PostBase, UserAuth
from sqlalchemy.orm.session import Session
from db.models import DbPost
import datetime

def create(db: Session, request: PostBase, current_user: UserAuth):
   new_post = DbPost(
      image_url = request.image_url, 
      caption = request.caption,
      timestamp = datetime.datetime.now(),
      user_id = current_user.id
   )
   db.add(new_post)
   db.commit()
   db.refresh(new_post)

   return new_post

def get_all(db: Session):
   return db.query(DbPost).all()

def get_some(num: int, db: Session):
   return db.query(DbPost).order_by(DbPost.id.desc()).limit(num).all()

def get_id(db: Session, id: int):
   post = db.query(DbPost).filter(DbPost.id==id).first()
   if not post:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
   return post   

def change_post(request: PostBase, id:int, db: Session, current_user: UserAuth ):
   post = db.query(DbPost).filter(DbPost.id == id).first()
   if not post:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
   #if request.creator_id!=current_user.id:
      #raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can post only by your account")
   if request.image_url:
      post.image_url=request.image_url
   if request.caption:
      post.caption=request.caption

   return post

def delete(db: Session, id: int, user_id: int):
   post = db.query(DbPost).filter(DbPost.id == id).first()
   if not post:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
   if post.user_id != user_id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Only post author can delete it!")
   db.delete(post)
   db.commit()
   return 'Post deleted successfully!'

def like_post(id: int, status: bool, db: Session, current_user: UserAuth):
   post = db.query(DbPost).filter(DbPost.id == id).first()
   if not post:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
   if status==True:
      post.likes+=1
      db.commit()
   else:
      post.likes-=1   
      db.commit()
   return post