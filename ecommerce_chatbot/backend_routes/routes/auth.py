from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from .. import schema,database,models,utils,Oauth2

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login",status_code=status.HTTP_200_OK)
def UserLogin(user_credentials : OAuth2PasswordRequestForm = Depends(),db : Session = Depends(database.get_db)):

    user = db.query(models.Users).filter(models.Users.email_id == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Invalid credentials')

    if not utils.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid credentials')

    token = Oauth2.create_access_token(data={"user_id" : user.id})

    return {"access_token" : token,"token_type" : "Bearer"}

@router.delete("/delete_user")
def Delete_user(current_user: schema.TokenData = Depends(Oauth2.get_current_user),db : Session = Depends(database.get_db)):
    user = db.query(models.Users).filter(models.Users.id == current_user.id ).first()

    if not user :
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,detail=f"Not Authorized to perform this action")
    
    db.delete(user)
    db.commit()
    return HTTPException(status_code=status.HTTP_204_NO_CONTENT,detail=f"user:{current_user.id} deleted successfully")