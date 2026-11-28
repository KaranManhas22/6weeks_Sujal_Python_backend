from fastapi import APIRouter, Depends, Query
from models.property_model import PropertyCreate
from controllers.property_controller import get_properties_controller, get_property_by_id_controller, create_property_controller
from middleware.auth_middleware import protect
from models.inquiry_model import InquiryCreate
from controllers.inquiry_controller import create_inquiry_controller, get_my_inquiries_controller
from controllers.property_controller import get_my_properties_controller, get_pending_properties_controller, approve_property_controller

router = APIRouter()

@router.get("")
@router.get("/")
def get_properties(keyword: str = Query(None, max_length=100), pageNumber: int = Query(1, ge=1)):
    return get_properties_controller(keyword, pageNumber)

@router.post("", status_code=201)
@router.post("/", status_code=201)
def create_property(property_data: PropertyCreate, current_user: dict = Depends(protect)):
    return create_property_controller(property_data, current_user)

@router.get("/mine")
def get_my_properties(current_user: dict = Depends(protect)):
    return get_my_properties_controller(current_user)

@router.get("/mine/inquiries")
def get_my_inquiries(current_user: dict = Depends(protect)):
    return get_my_inquiries_controller(current_user)

@router.get("/pending")
def get_pending_properties(current_user: dict = Depends(protect)):
    return get_pending_properties_controller(current_user)

@router.patch("/{id}/approve")
def approve_property(id: str, current_user: dict = Depends(protect)):
    return approve_property_controller(id, current_user)

@router.post("/{id}/inquiries", status_code=201)
def create_inquiry(id: str, inquiry: InquiryCreate):
    return create_inquiry_controller(id, inquiry)

@router.get("/{id}")
def get_property_by_id(id: str):
    return get_property_by_id_controller(id)
