import mongoose from 'mongoose';
import dotenv from 'dotenv';
import bcrypt from 'bcryptjs';
import User from '../models/User.js';
import Property from '../models/Property.js';
import users from './users.js';

dotenv.config();

const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/realestate';

mongoose.connect(MONGO_URI);

const importData = async () => {
  try {
    await Property.deleteMany();
    await User.deleteMany();

    // Hash passwords for users before inserting
    const usersToInsert = await Promise.all(users.map(async (u) => {
      const salt = await bcrypt.genSalt(10);
      const hashedPassword = await bcrypt.hash(u.password, salt);
      return { ...u, password: hashedPassword };
    }));

    const createdUsers = await User.insertMany(usersToInsert);
    const sellerUser = createdUsers.find(u => u.role === 'Seller');

    const sampleProperties = [];
    const cities = ['New York, NY', 'Los Angeles, CA', 'Austin, TX', 'Miami, FL', 'Seattle, WA', 'Chicago, IL'];
    const types = ['House', 'Apartment', 'Condo', 'Townhouse'];
    const titles = ['Modern Luxury', 'Cozy Downtown', 'Spacious Family Home', 'Renovated Classic', 'Minimalist Haven', 'Beachfront Property'];
    const amenitiesList = ['Pool', 'Gym', 'Garage', 'Garden', 'Balcony', 'Security', 'Smart Home'];

    for (let i = 1; i <= 30; i++) {
      const location = cities[Math.floor(Math.random() * cities.length)].split(', ');
      
      const shuffledAmenities = amenitiesList.sort(() => 0.5 - Math.random());
      const selectedAmenities = shuffledAmenities.slice(0, 3);

      sampleProperties.push({
        title: `${titles[Math.floor(Math.random() * titles.length)]} in ${location[0]}`,
        description: `This is a beautiful and realistic sample property number ${i}. It features stunning architecture and modern amenities.`,
        price: Math.floor(Math.random() * (2000000 - 300000 + 1) + 300000),
        address: `${1000 + i} Main St, ${location[0]}`,
        location: {
          city: location[0],
          state: location[1],
          zipCode: `9000${i % 9}`,
          coordinates: { lat: 34.0522 + (Math.random() * 0.1), lng: -118.2437 - (Math.random() * 0.1) }
        },
        propertyType: types[Math.floor(Math.random() * types.length)],
        status: 'For Sale',
        bedrooms: Math.floor(Math.random() * 4) + 1,
        bathrooms: Math.floor(Math.random() * 3) + 1,
        area: Math.floor(Math.random() * (4000 - 800 + 1) + 800),
        parkingSpaces: Math.floor(Math.random() * 3),
        yearBuilt: 2000 + Math.floor(Math.random() * 24),
        isFurnished: Math.random() > 0.5,
        amenities: selectedAmenities,
        features: {
          newConstruction: Math.random() > 0.7,
          readyToMove: true
        },
        images: [
          `https://picsum.photos/seed/${i * 10}/800/600`,
          `https://picsum.photos/seed/${i * 20}/800/600`
        ],
        seller: sellerUser._id,
        approvalStatus: 'Approved'
      });
    }

    await Property.insertMany(sampleProperties);

    console.log('Data Imported!');
    process.exit();
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
};

const destroyData = async () => {
  try {
    await Property.deleteMany();
    await User.deleteMany();

    console.log('Data Destroyed!');
    process.exit();
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
};

if (process.argv[2] === '-d') {
  destroyData();
} else {
  importData();
}
