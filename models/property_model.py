from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class Coordinates(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None

class Location(BaseModel):
    city: str = Field(min_length=1)
    state: str = Field(min_length=1)
    zipCode: Optional[str] = None
    coordinates: Optional[Coordinates] = None

class Features(BaseModel):
    newConstruction: bool = False
    readyToMove: bool = False

class PropertyCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    price: float = Field(gt=0, allow_inf_nan=False)
    address: str = Field(min_length=1)
    location: Location
    propertyType: Literal["House", "Apartment", "Condo", "Townhouse", "Penthouse", "Land", "Commercial"]
    status: Literal["For Sale", "For Rent", "Pending", "Sold"] = "For Sale"
    bedrooms: float = Field(ge=0, allow_inf_nan=False)
    bathrooms: float = Field(ge=0, allow_inf_nan=False)
    area: float = Field(gt=0, allow_inf_nan=False)
    parkingSpaces: int = Field(default=0, ge=0)
    yearBuilt: Optional[int] = None
    isFurnished: bool = False
    amenities: List[str] = Field(default_factory=list)
    features: Features = Field(default_factory=Features)
    images: List[str] = Field(default_factory=list)
