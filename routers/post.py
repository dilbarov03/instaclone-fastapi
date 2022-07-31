from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from fastapi.responses import StreamingResponse
from auth.oauth2 import get_current_user
from .schemas import PostBase, PostDisplay
from db.database import get_db
from db import db_post
from typing import List
from routers.schemas import UserAuth
import random
import string
import shutil
import cloudinary
import cloudinary.uploader


router = APIRouter(
   prefix = '/post',
   tags = ['post']
)

image_url_types = ['absolute', 'relative']

@router.get('/all', response_model=List[PostDisplay])
def get_all(db: Session = Depends(get_db)):
   return db_post.get_all(db)

@router.get('/some', response_model=List[PostDisplay])
def get_some(num: int, db: Session = Depends(get_db)):
   return db_post.get_some(num, db)

@router.get('/{id}', response_model=PostDisplay)
def get_post_by_id(id: int, db: Session = Depends(get_db)):
   return db_post.get_id(db, id)

@router.patch('/{id}', response_model=PostDisplay)
def update_post(request: PostBase,id: int, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
   return db_post.change_post(request, id, db, current_user)


@router.post('/', response_model=PostDisplay)
def create(request: PostBase, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
   return db_post.create(db, request, current_user)

@router.post('/image')
def upload_image(file: UploadFile = File(...), current_user: UserAuth = Depends(get_current_user)):
   result = cloudinary.uploader.upload(file.file)
   url = result.get("url")

   return {'path': url}

@router.post('/{id}/like', response_model=PostDisplay)
def like(id: int, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
   return db_post.like_post(id, db, current_user)


@router.delete('/delete/{id}')
def delete_post(id: int, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
   return db_post.delete(db, id, current_user.id)