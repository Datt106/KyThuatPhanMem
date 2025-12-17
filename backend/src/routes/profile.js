const express = require("express");
const router = express.Router();
const authMiddleware = require("../middlewares/authMiddleware");
const pool = require("../config/db");

router.get("/", authMiddleware, async (req, res) => {
  try {
    const cccd = req.user.cccd;

    const query = `
      SELECT 
        nd.cccd,
        nd.name,
        nd.sdt,
        nd.ngaysinh,
        nd.gioitinh,
        nd.dantoc,
        nd.vaitro,
        nd.baomatthongtin
      FROM nguoidung nd
      WHERE nd.cccd = $1
    `;

    const { rows } = await pool.query(query, [cccd]);

    if (rows.length === 0)
      return res.status(404).json({ message: "Không tìm thấy người dùng" });

    res.json(rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Lỗi server" });
  }
});

module.exports = router;
