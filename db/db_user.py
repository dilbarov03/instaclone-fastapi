from logging import Handler
from routers.schemas import UpdateProfile, UserAuth, UserBase
from sqlalchemy.orm.session import Session
from .models import DbComment, DbFollow, DbPost, DbUser
from db.hashing import Hash
from fastapi import HTTPException, status

def get_all_users(db: Session):
   users = db.query(DbUser).all()
   return users

def create_user(db: Session, request: UserBase):
   new_user = DbUser(
      username = request.username,
      email = request.email,
      password = Hash.bcrypt(request.password),
      avatar_url = request.avatar_url
   )
   db.add(new_user)
   db.commit()
   db.refresh(new_user)

   return new_user

def get_user_by_username(db: Session, username: str):
   user = db.query(DbUser).filter(DbUser.username==username).first()
   if not user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username {username} not found")
   return user

def users_posts(db: Session, username: str):
   users_id = db.query(DbUser.id).filter(DbUser.username==username).first()
   if not users_id:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username {username} not found")   
   posts = db.query(DbPost).filter(DbPost.user_id==users_id["id"]).all()
   if not posts:
      user = db.query(DbUser).filter(DbUser.username==username).first()
      return user
   return posts

def profile_info(db: Session, current_user: UserAuth):
   user = db.query(DbUser).filter(DbUser.id==current_user.id).first()
   if not user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with {id} is not found")
   return user


def change_profile(db: Session, request: UpdateProfile, current_user: UserAuth):
   user = db.query(DbUser).filter(DbUser.username==current_user.username).first()
   if request.username: 
      user.username = request.username
   if request.full_name:
      user.full_name = request.full_name
   if request.bio:
      user.bio = request.bio
   if request.email: 
      user.email = request.email
   if request.password:
      user.password = Hash.bcrypt(request.password)
   if request.avatar_url:
      user.avatar_url = request.avatar_url

   db.commit()
   return user

def subscribe(username: str, db: Session, current_user: UserAuth):
   if current_user.username!=username:
      source_user_id = db.query(DbUser.id).filter(DbUser.username==username).first()
      item = db.query(DbFollow).filter(DbFollow.subscribed==source_user_id[0]).filter(DbFollow.user_id==current_user.id).first()
      
      if item==None:
         new_subscription = DbFollow(
            user_id=current_user.id,
            subscribed=source_user_id[0]
         )
         db.add(new_subscription)
         db.commit()
         db.refresh(new_subscription)
         
         user = db.query(DbUser).filter(DbUser.id==source_user_id[0]).first()
         user.subscribers+=1
         db.commit()

         return user
         

      else:
         db.delete(item)
         db.commit()
         user = db.query(DbUser).filter(DbUser.id==source_user_id[0]).first()
         user.subscribers-=1
         db.commit()
         return user

def my_subscriptions(db: Session, current_user: UserAuth):
   subscriptions = db.query(DbFollow.subscribed).filter(DbFollow.user_id==current_user.id).all()
   output = []
   for i in subscriptions:
      user_id = i["subscribed"]
      user = db.query(DbUser).filter(DbUser.id==user_id).first()
      output.append(user)

   return output

def delete_account(db: Session, current_user: UserAuth):
   user = db.query(DbUser).filter(DbUser.id==current_user.id).first()
   comments = db.query(DbComment).filter(DbComment.user_id==user.id).all()
   if comments:
      for i in comments:
         db.delete(i)
         db.commit()

   posts = db.query(DbPost).filter(DbPost.user_id==user.id).all()
   if posts:
      for i in posts:
         db.delete(i)
         db.commit()
   
   subscriptions = db.query(DbFollow).filter(DbFollow.user_id==user.id).all()
   if subscriptions:
      for i in subscriptions:
         subscribed_user = db.query(DbUser).filter(DbUser.id==i.subscribed).first()
         subscribed_user.subscribers-=1
         db.commit()
         db.delete(i)
         db.commit()

   followed = db.query(DbFollow).filter(DbFollow.subscribed==user.id).all()
   if followed:
      for i in followed:
         db.delete(i)
         db.commit()

   db.delete(user)
   db.commit()

   return {"msg":"Account deleted successfully!"}      