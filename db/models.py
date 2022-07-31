from sqlalchemy.sql.schema import ForeignKey
from .database import Base
from sqlalchemy import ARRAY, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.ext.mutable import MutableList


class DbUser(Base):
   __tablename__ = "users"
   id = Column(Integer, primary_key=True, index=True)
   username = Column(String, unique=True)
   full_name = Column(String, nullable=True)
   email = Column(String, unique=True)
   password = Column(String)
   bio = Column(String, nullable=True)
   avatar_url = Column(String, default="")
   subscribers = Column(Integer, default=0)
   items = relationship('DbPost', back_populates='user')
   items2 = relationship('DbComment', back_populates='user')
   items3 = relationship('DbFollow', back_populates='user')   

class DbPost(Base):
   __tablename__ = "post"
   id = Column(Integer, primary_key=True, index=True)
   image_url = Column(String) 
   #image_url_type = Column(String)
   caption = Column(String)
   timestamp = Column(DateTime)
   user_id = Column(Integer, ForeignKey('users.id'))
   likes = Column(Integer, default=0)
   liked_users = Column(MutableList.as_mutable(ARRAY(Integer)))
   user = relationship('DbUser', back_populates='items')
   comments = relationship('DbComment', back_populates='post')

class DbComment(Base):
   __tablename__ = "comments"
   id = Column(Integer, primary_key=True, index=True)
   text = Column(String)
   user = relationship('DbUser', back_populates='items2')
   timestamp = Column(DateTime)
   post_id = Column(Integer, ForeignKey("post.id"))
   user_id = Column(Integer, ForeignKey("users.id"))
   
   post = relationship("DbPost", back_populates="comments")

class DbFollow(Base):
   __tablename__ = "subscription"
   id = Column(Integer, primary_key=True, index=True)
   user_id = Column(Integer, ForeignKey("users.id"))
   subscribed = Column(Integer)
   user = relationship('DbUser', back_populates='items3')

class PostLikes(Base):
   __tablename__ = "PostLikes"
   id = Column(Integer, primary_key=True, index=True)
   user_id = Column(Integer)
   post_id = Column(Integer)