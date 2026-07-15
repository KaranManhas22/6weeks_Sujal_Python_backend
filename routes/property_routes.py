from fastapi import APIRouter, Depends, Query
from models.property_model import PropertyCreate
from controllers.property_controller import get_properties_controller, get_property_by_id_controller, create_property_controller
from middleware.auth_middleware import protect

router = APIRouter()

@router.get("")
@router.get("/")
def get_properties(keyword: str = Query(None), pageNumber: int = Query(1)):
    return get_properties_controller(keyword, pageNumber)

@router.post("", status_code=201)
@router.post("/", status_code=201)
def create_property(property_data: PropertyCreate, current_user: dict = Depends(protect)):
    return create_property_controller(property_data, current_user)

@router.get("/{id}")
def get_property_by_id(id: str):
    return get_property_by_id_controller(id)
