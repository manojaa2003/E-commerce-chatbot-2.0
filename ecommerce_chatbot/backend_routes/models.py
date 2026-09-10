from .database import Base
from sqlalchemy import Column,Integer,String,Boolean,text,ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key = True,nullable = False)
    email_id = Column(String,nullable = False,unique=True)
    password = Column(String,nullable = False)
    created_at = Column(TIMESTAMP(timezone=True),nullable = False, server_default = text('now()'))

class PendingUser(Base):
    __tablename__ = "pending_users"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, nullable=False, index=True)
    password = Column(String, nullable=False)   # already hashed
    otp_hash = Column(String, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class PasswordResetOTP(Base):
    __tablename__ = "password_reset_otps"

    id = Column(Integer, primary_key=True, nullable=False)
    email_id = Column(String, nullable=False, index=True)
    otp_hash = Column(String, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    is_used = Column(Boolean, nullable=False, server_default=text('false'))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))