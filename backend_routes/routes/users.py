from fastapi import FastAPI,Depends,status,HTTPException,APIRouter
from ..schema import CreateUserIn,CreateUserOut,UpdatePswd,ForgotPasswordIn,UpdatePswd,VerifyAccountOTP
import random
import string
from datetime import datetime, timedelta, timezone


from email.mime.text import MIMEText

from sqlalchemy.orm import Session

from .. import models,database,utils

from dotenv import load_dotenv

OTP_EXPIRE_MINUTES = 5

load_dotenv()

router = APIRouter(
    tags=["Users"]
)

@router.post("/users", status_code=status.HTTP_200_OK)
async def create_user(user: CreateUserIn, db: Session = Depends(database.get_db)):
    existing_user = db.query(models.Users).filter(models.Users.email_id == user.email_id).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'User with email_id : {user.email_id} already exists')

    hashed_password = utils.hash(user.password)
    otp = ''.join(random.choices(string.digits, k=6))

    # A fresh signup attempt always replaces any earlier unverified attempt
    db.query(models.PendingUser).filter(models.PendingUser.email_id == user.email_id).delete()

    db.add(models.PendingUser(
        email_id=user.email_id,
        password=hashed_password,
        otp_hash=utils.hash(otp),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)
    ))
    db.commit()

    utils.send_otp_email(user.email_id, otp)

    return {"message": "OTP sent to your registered email. Verify to complete registration."}


@router.post("/users/verify-account", response_model=CreateUserOut, status_code=status.HTTP_201_CREATED)
def verify_account(request: VerifyAccountOTP, db: Session = Depends(database.get_db)):
    pending = (
        db.query(models.PendingUser)
        .filter(models.PendingUser.email_id == request.email_id)
        .first()
    )

    if not pending:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='No pending registration found, please sign up again')

    if pending.expires_at < datetime.now(timezone.utc):
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='OTP has expired, please sign up again')

    if not utils.verify(request.otp, pending.otp_hash):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Invalid OTP')

    # Safety net in case an account was somehow created between signup and verification
    existing_user = db.query(models.Users).filter(models.Users.email_id == pending.email_id).first()
    if existing_user:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User already exists')

    new_user = models.Users(email_id=pending.email_id, password=pending.password)
    db.add(new_user)
    db.delete(pending)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/users/resend-otp", status_code=status.HTTP_200_OK)
def resend_registration_otp(request: ForgotPasswordIn, db: Session = Depends(database.get_db)):
    pending = db.query(models.PendingUser).filter(models.PendingUser.email_id == request.email_id).first()
    if not pending:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No pending registration found, please sign up again')

    otp = ''.join(random.choices(string.digits, k=6))
    pending.otp_hash = utils.hash(otp)
    pending.expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)
    db.commit()

    utils.send_otp_email(request.email_id, otp)

    return {"message": "OTP sent to your registered email"}

@router.post("/users/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(request: ForgotPasswordIn, db: Session = Depends(database.get_db)):
    db_user = db.query(models.Users).filter(models.Users.email_id == request.email_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'email_id : {request.email_id} does not exist, please SignUp'
        )

    otp = ''.join(random.choices(string.digits, k=6))

    db.add(models.PasswordResetOTP(
        email_id=request.email_id,
        otp_hash=utils.hash(otp),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)
    ))
    db.commit()

    utils.send_otp_email(request.email_id, otp)

    return {"message": "OTP sent to your registered email"}


@router.post("/users/update-password", status_code=status.HTTP_200_OK)
def update_password(user: UpdatePswd, db: Session = Depends(database.get_db)):
    db_user = db.query(models.Users).filter(models.Users.email_id == user.email_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'email_id : {user.email_id} does not exist, please SignUp'
        )

    otp_record = (
        db.query(models.PasswordResetOTP).filter(
            models.PasswordResetOTP.email_id == user.email_id,
            models.PasswordResetOTP.is_used == False,
        )
        .order_by(models.PasswordResetOTP.created_at.desc())
        .first()
    )

    if not otp_record:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='No OTP request found, please request a new OTP')

    if otp_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='OTP has expired, please request a new one')

    if not utils.verify(user.otp, otp_record.otp_hash):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Invalid OTP')

    db_user.password = utils.hash(user.new_password)
    db.delete(otp_record)
    db.commit()

    return {"message": "Password updated successfully"}