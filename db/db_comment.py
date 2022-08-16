from fastapi import HTTPException, status
from sqlalchemy.orm.session import Session
from routers.schemas import CommentBase, UserAuth
from db.models import DbComment, DbUser
from datetime import datetime
from sqlalchemy import desc


def create(db: Session, request: CommentBase, current_user: UserAuth):
   new_comment = DbComment(
      text = request.text,
      user_id = current_user.id,
      post_id = request.post_id,
      timestamp = datetime.now()
   )
   db.add(new_comment)
   db.commit()
   db.refresh(new_comment)
   user = db.query(DbUser).filter(DbUser.id == current_user.id).first()

   return {
      "id": new_comment.id,
      "text": new_comment.text,
      "user": {
        "username": user.username,
        "avatar_url": user.avatar_url
      },
      "timestamp": new_comment.timestamp
   }
   #return new_comment

def get_all(db: Session, post_id: int):
   return db.query(DbComment).filter(DbComment.post_id == post_id).order_by(desc(DbComment.id)).all()

def update(id: int, db: Session, request: CommentBase, current_user: UserAuth):
   comment = db.query(DbComment).filter(DbComment.id==id).first()
   if not comment:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment with id {id} not found")
   if request.text:
      comment.text = request.text
   db.commit()
   return comment

def delete(id: int, db: Session, current_user: UserAuth):
   comment = db.query(DbComment).filter(DbComment.id==id).first()
   if not comment:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment with id {id} not found")
   db.delete(comment)
   db.commit()
   return "Comment deleted successfully!"