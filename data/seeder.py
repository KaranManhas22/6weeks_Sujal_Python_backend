import sys
import os
import random
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv

# Add the parent directory to Python path so we can import config/models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db import get_db
from models.user_model import hash_password
from data.users import users

load_dotenv()
db = get_db()

def import_data():
    try:
        # Clear collections
        db.properties.delete_many({})
        db.users.delete_many({})
        
        # Hash user passwords before inserting
        hashed_users = []
        for u in users:
            user_copy = u.copy()
            user_copy["password"] = hash_password(u["password"])
            user_copy["avatar"] = ""
            user_copy["phone"] = ""
            user_copy["savedProperties"] = []
            user_copy["createdAt"] = datetime.utcnow()
            user_copy["updatedAt"] = datetime.utcnow()
            hashed_users.append(user_copy)
            
        inserted_users = db.users.insert_many(hashed_users)
        
        # Find seller user
        seller_user = db.users.find_one({"role": "Seller"})
        if not seller_user:
            raise Exception("Seller user not found in seeded users")
        
        seller_id = seller_user["_id"]
        
        cities = ['New York, NY', 'Los Angeles, CA', 'Austin, TX', 'Miami, FL', 'Seattle, WA', 'Chicago, IL']
        types = ['House', 'Apartment', 'Condo', 'Townhouse', 'Penthouse']
        titles = ['Modern Luxury', 'Cozy Downtown', 'Spacious Family Home', 'Renovated Classic', 'Minimalist Haven', 'Beachfront Property', 'Skyline Penthouse', 'High-Rise Oasis']
        amenities_list = ['Pool', 'Gym', 'Garage', 'Garden', 'Balcony', 'Security', 'Smart Home']
        
        # Real high-quality images from Unsplash
        house_images = [
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1512915922686-57c11dde9b6b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1513584684374-8bab748fbf90?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1502005229762-fc1b2d812ca5?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&q=80"
        ]
        
        apartment_images = [
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1502672090847-032d766e04d4?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1567496898669-ee935f5f647a?auto=format&fit=crop&w=800&q=80"
        ]
        
        penthouse_images = [
            "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1582407947304-fd86f028f716?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1515263487990-61b07816b324?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=800&q=80"
        ]
        
        sample_properties = []
        for i in range(1, 31):
            city_state = random.choice(cities).split(', ')
            city = city_state[0]
            state = city_state[1]
            
            random.shuffle(amenities_list)
            selected_amenities = amenities_list[:3]
            
            lat = 34.0522 + (random.random() * 0.1)
            lng = -118.2437 - (random.random() * 0.1)
            
            prop_type = random.choice(types)
            
            # Select realistic title prefix
            if prop_type == "Penthouse":
                title_prefix = random.choice(['Skyline Penthouse', 'High-Rise Oasis', 'Luxury Penthouse', 'Exclusive Penthouse Suite'])
                selected_imgs = random.sample(penthouse_images, min(2, len(penthouse_images)))
            elif prop_type in ["House", "Townhouse"]:
                title_prefix = random.choice(['Modern Luxury', 'Spacious Family Home', 'Renovated Classic', 'Beachfront Property'])
                selected_imgs = random.sample(house_images, min(2, len(house_images)))
            else: # Apartment, Condo
                title_prefix = random.choice(['Cozy Downtown', 'Minimalist Haven', 'Modern Apartment', 'Urban Retreat'])
                selected_imgs = random.sample(apartment_images, min(2, len(apartment_images)))
            
            prop = {
                "title": f"{title_prefix} in {city}",
                "description": f"This is a beautiful and realistic sample property number {i}. It features stunning architecture and modern amenities.",
                "price": random.randint(300000, 2000000),
                "address": f"{1000 + i} Main St, {city}",
                "location": {
                    "city": city,
                    "state": state,
                    "zipCode": f"9000{i % 9}",
                    "coordinates": { "lat": lat, "lng": lng }
                },
                "propertyType": prop_type,
                "status": "For Sale",
                "bedrooms": float(random.randint(1, 4)),
                "bathrooms": float(random.randint(1, 3)),
                "area": float(random.randint(800, 4000)),
                "parkingSpaces": random.randint(0, 2),
                "yearBuilt": random.randint(2000, 2024),
                "isFurnished": random.random() > 0.5,
                "amenities": selected_amenities,
                "features": {
                    "newConstruction": random.random() > 0.7,
                    "readyToMove": True
                },
                "images": selected_imgs,
                "seller": seller_id,
                "approvalStatus": "Approved",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            sample_properties.append(prop)
            
        db.properties.insert_many(sample_properties)
        print("Data Imported!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def destroy_data():
    try:
        db.properties.delete_many({})
        db.users.delete_many({})
        print("Data Destroyed!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-d":
        destroy_data()
    else:
        import_data()
