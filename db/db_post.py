from fastapi import HTTPException, status
from routers.schemas import PostBase, UpdatePostBase, UserAuth
from sqlalchemy.orm.session import Session
from db.models import DbPost, PostLikes
import datetime
from sqlalchemy import text

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

def change_post(request: UpdatePostBase, id:int, db: Session, current_user: UserAuth ):
   post = db.query(DbPost).filter(DbPost.id == id).first()
   if not post:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
   if post.user_id!=current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can post only by your account")
   if request.image_url:
      post.image_url=request.image_url
   if request.caption:
      post.caption=request.caption 

   db.commit() #save

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

def like_post(id: int, db: Session, current_user: UserAuth):
   post = db.query(DbPost).filter(DbPost.id == id).first()
   if not post:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
   
   if (post.liked_users is not None) and (current_user.id in post.liked_users):
      post.likes-=1
      post.liked_users.remove(current_user.id)
      db.commit()
   else:
      post.likes+=1 
      post.liked_users.append(current_user.id)
      db.commit()

   """liked_user = db.query(PostLikes).filter(PostLikes.post_id==post.id, PostLikes.user_id==current_user.id).first()
   if liked_user:
      post.likes -= 1
      db.delete(liked_user)
      db.commit()
   else:
      post.likes += 1
      new_like = PostLikes(post_id=post.id, user_id=current_user.id)
      db.add(new_like)
      db.commit()
      db.refresh(new_like)"""


   return post