from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session
from db.database import get_db
from db import db_comment
from db.models import DbComment
from routers.schemas import CommentBase, CommentDisplay, UserAuth
from auth.oauth2 import get_current_user

router = APIRouter(
   prefix='/comment',
   tags=['comment']
)

@router.get('/all/{post_id}')
def comments(post_id: int, db: Session = Depends(get_db)):
   return db_comment.get_all(db, post_id)

@router.patch('/{id}', response_model=CommentDisplay)
def update_comment(id: int, request: CommentBase, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
   return db_comment.update(id,db, request,  current_user)

@router.post('/')
def create(request: CommentBase, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
   return db_comment.create(db, request, current_user)

@router.delete('/{id}')
def delete_comment(id: int, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
   return db_comment.delete(id, db, current_user)