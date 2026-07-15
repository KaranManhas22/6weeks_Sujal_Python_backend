import mongoose from 'mongoose';

const propertySchema = new mongoose.Schema({
  title: { type: String, required: true },
  description: { type: String, required: true },
  price: { type: Number, required: true },
  address: { type: String, required: true },
  location: {
    city: { type: String, required: true },
    state: { type: String, required: true },
    zipCode: { type: String },
    coordinates: {
      lat: { type: Number },
      lng: { type: Number }
    }
  },
  propertyType: { type: String, required: true, enum: ['House', 'Apartment', 'Condo', 'Townhouse', 'Land', 'Commercial'] },
  status: { type: String, required: true, enum: ['For Sale', 'For Rent', 'Pending', 'Sold'], default: 'For Sale' },
  bedrooms: { type: Number, required: true },
  bathrooms: { type: Number, required: true },
  area: { type: Number, required: true }, // in sq ft
  parkingSpaces: { type: Number, default: 0 },
  yearBuilt: { type: Number },
  isFurnished: { type: Boolean, default: false },
  amenities: [{ type: String }], // e.g., Garden, Swimming Pool, Gym
  features: {
    newConstruction: { type: Boolean, default: false },
    readyToMove: { type: Boolean, default: false }
  },
  images: [{ type: String }], // Array of image URLs
  seller: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  approvalStatus: { type: String, enum: ['Pending', 'Approved', 'Rejected'], default: 'Pending' }
}, { timestamps: true });

// Performance Indexes
propertySchema.index({ approvalStatus: 1 });
propertySchema.index({ title: 1 });
propertySchema.index({ seller: 1 });

const Property = mongoose.model('Property', propertySchema);
export default Property;
