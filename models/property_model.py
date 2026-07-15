from pydantic import BaseModel
from typing import List, Optional

class Coordinates(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None

class Location(BaseModel):
    city: str
    state: str
    zipCode: Optional[str] = None
    coordinates: Optional[Coordinates] = None

class Features(BaseModel):
    newConstruction: bool = False
    readyToMove: bool = False

class PropertyCreate(BaseModel):
    title: str
    description: str
    price: float
    address: str
    location: Location
    propertyType: str
    status: str = "For Sale"
    bedrooms: float
    bathrooms: float
    area: float
    parkingSpaces: int = 0
    yearBuilt: Optional[int] = None
    isFurnished: bool = False
    amenities: List[str] = []
    features: Features = Features()
    images: List[str] = []
