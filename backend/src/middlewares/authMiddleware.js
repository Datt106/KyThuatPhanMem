const jwt = require('jsonwebtoken');

const authenticateToken = (req, res, next) => {
  // Lấy token từ header Authorization: Bearer <token>
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; 

  if (!token) return res.status(401).json({ message: 'Token không tồn tại' });

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ message: 'Token không hợp lệ' });
    
    req.user = user; // gắn thông tin user vào request
    next();
  });
};

module.exports = authenticateToken;
