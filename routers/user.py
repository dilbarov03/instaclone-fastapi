from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm.session import Session
from auth.oauth2 import get_current_user
from db.database import get_db
from routers.schemas import AllUsers, PostDisplay, ProfileDisplay, UpdateProfile, UserAuth, UserBase, UserDisplay, UserPostDisplay
from db.db_user import change_profile, create_user, delete_account, get_user_by_username, my_subscriptions, subscribe, users_posts, profile_info, get_all_users
import cloudinary
import cloudinary.uploader

router = APIRouter(
   tags=['user']
)

@router.get("/profile", response_model=ProfileDisplay)
def get_profile(db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
   return profile_info(db, current_user)

@router.get("/my_subscriptions",response_model=List[AllUsers])
def get_subscriptions(db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
   return my_subscriptions(db, current_user)

@router.post("/user", response_model=UserDisplay)
def create_profile(request: UserBase, db: Session = Depends(get_db)):
   return create_user(db, request)

@router.get("/user/all", response_model=List[AllUsers])
def getting_users(db: Session = Depends(get_db)):
   return get_all_users(db)

@router.post('/user/image')
def upload_image(file: UploadFile = File(...)):
   result = cloudinary.uploader.upload(file.file)
   url = result.get("url")

   return {'path': url}

'''@router.get("/profile/{name}")
def download_img(name: str):
    res = profile_pics.get(name)
    return StreamingResponse(res.iter_chunks(1024), media_type="image/png")'''

@router.get("/{username}", response_model=UserPostDisplay)
def get_user_posts(username: str, db: Session = Depends(get_db)):
   #return users_posts(db, username)
   return get_user_by_username(db, username)

@router.patch("/update", response_model=ProfileDisplay)
def update_user(request: UpdateProfile, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
   return change_profile(db, request, current_user)
   



@router.post("/{username}/subscribe", response_model=UserDisplay)
def subscribe_to(username: str, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
   return subscribe(username, db, current_user)

@router.delete("/delete")
def delete(db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
   delete_account(db, current_user)