from fastapi import APIRouter, Depends
from models.user_model import UserRegister, UserLogin
from controllers.auth_controller import register_user_controller, login_user_controller, get_user_profile_controller
from middleware.auth_middleware import protect

router = APIRouter()

@router.post("/register", status_code=201)
def register(user_data: UserRegister):
    return register_user_controller(user_data)

@router.post("/login")
def login(login_data: UserLogin):
    return login_user_controller(login_data)

@router.get("/profile")
def get_profile(current_user: dict = Depends(protect)):
    return get_user_profile_controller(current_user)
