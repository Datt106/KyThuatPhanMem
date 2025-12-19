const express = require("express");
const router = express.Router();
const pool = require("../config/db");
const multer = require("multer");
const path = require("path");
const fs = require("fs");

// Tạo folder uploads/phananh nếu chưa tồn tại
const uploadDir = path.join(__dirname, "..", "uploads", "phananh");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// Cấu hình multer
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
    cb(null, uniqueSuffix + path.extname(file.originalname)); // giữ extension
  },
});

const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 }, // giới hạn 5MB
  fileFilter: (req, file, cb) => {
    const allowedTypes = ["image/jpeg", "image/png", "image/gif"];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error("Chỉ cho phép JPG, PNG, GIF"));
    }
  },
});

router.get("/me", async (req, res) => {
  try {
    const CCCD = req.headers.cccd;
    const result = await pool.query(
      `SELECT maphananh, loaiphananh, mota, trangthaiphananh, thoigian
       FROM phananh
       WHERE CCCD = $1
       ORDER BY maphananh DESC`,
      [CCCD]
    );

    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post("/", upload.single("file"), async (req, res) => {
  try {
    const CCCD = req.headers.cccd;
    const { loaiPhanAnh, maDiaChi, moTa } = req.body;

    let maTep = null;

    if (req.file) {
      const filePath = `/uploads/phananh/${req.file.filename}`;

      const tep = await pool.query(
        `INSERT INTO tepdinhkem (duongdan)
         VALUES ($1)
         RETURNING matepdinhkem`,
        [filePath]
      );
      maTep = tep.rows[0].matepdinhkem;
    }

    const newPhanAnh = await pool.query(
      `INSERT INTO phananh (cccd, diachi, loaiphananh, mota, matepdinhkem)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING maphananh`,
      [CCCD, maDiaChi, loaiPhanAnh, moTa, maTep]
    );
    console.log(newPhanAnh);
    res.status(201).json({
      message: "Tạo phản ánh thành công",
      maPhanAnh: newPhanAnh.rows[0].maphananh,
      file: req.file ? filePath : null,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
