import jwt from 'jsonwebtoken';

const generateToken = (userId) => {
  return jwt.sign({ userId }, process.env.JWT_SECRET || 'supersecretkey', {
    expiresIn: '30d',
  });
};

export default generateToken;
