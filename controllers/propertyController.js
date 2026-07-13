import Property from '../models/Property.js';

// @desc    Fetch all properties
// @route   GET /api/properties
// @access  Public
export const getProperties = async (req, res) => {
  try {
    const pageSize = 12;
    const page = Number(req.query.pageNumber) || 1;

    const keyword = req.query.keyword
      ? {
          title: {
            $regex: req.query.keyword,
            $options: 'i',
          },
        }
      : {};

    const count = await Property.countDocuments({ ...keyword, approvalStatus: 'Approved' });
    const properties = await Property.find({ ...keyword, approvalStatus: 'Approved' })
      .limit(pageSize)
      .skip(pageSize * (page - 1));

    res.json({ properties, page, pages: Math.ceil(count / pageSize) });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// @desc    Fetch single property
// @route   GET /api/properties/:id
// @access  Public
export const getPropertyById = async (req, res) => {
  try {
    const property = await Property.findById(req.params.id).populate('seller', 'name email avatar phone');
    if (property) {
      res.json(property);
    } else {
      res.status(404).json({ message: 'Property not found' });
    }
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// @desc    Create a property
// @route   POST /api/properties
// @access  Private/Seller
export const createProperty = async (req, res) => {
  try {
    if (req.user.role !== 'Seller' && req.user.role !== 'Admin') {
      return res.status(401).json({ message: 'Not authorized to create properties' });
    }

    const property = new Property({
      ...req.body,
      seller: req.user._id,
      approvalStatus: req.user.role === 'Admin' ? 'Approved' : 'Pending',
    });

    const createdProperty = await property.save();
    res.status(201).json(createdProperty);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};
