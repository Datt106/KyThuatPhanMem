const express = require("express");
const router = express.Router();
const pool = require("../db");
const multer = require("multer");
const path = require("path");

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, "uploads/"),
  filename: (req, file, cb) =>
    cb(null, Date.now() + path.extname(file.originalname)),
});
const upload = multer({ storage });

router.get("/", async (req, res) => {
  try {
    const result = await pool.query(
      "SELECT * FROM ThongTin ORDER BY ngay_dang DESC"
    );
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Server error" });
  }
});
router.post("/", upload.single("hinhanh"), async (req, res) => {
  const { tieude, noidung, loai_tin, nguoi_dang } = req.body;
  const hinhanh = req.file ? req.file.filename : null;

  try {
    const result = await pool.query(
      `INSERT INTO ThongTin (tieude, noidung, hinhanh, loai_tin, nguoi_dang)
       VALUES ($1,$2,$3,$4,$5) RETURNING *`,
      [tieude, noidung, hinhanh, loai_tin, nguoi_dang]
    );
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Server error" });
  }
});
module.exports = router;
