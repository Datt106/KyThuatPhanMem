const express = require("express");
const router = express.Router();
const pool = require("../config/db");
const authMiddleware = require("../middlewares/authMiddleware");

// Get all temporary absences
router.get("/", authMiddleware, async (req, res) => {
  try {
    const { trang_thai, id_nhan_khau } = req.query;

    let query = `
      SELECT 
        tv.*,
        nk.ho_ten,
        nk.ma_nhan_khau,
        CASE 
          WHEN tv.den_ngay < CURRENT_DATE THEN 'Hết hạn'
          ELSE 'Đang hiệu lực'
        END as tinh_trang
      FROM tam_vang tv
      JOIN nhan_khau nk ON tv.id_nhan_khau = nk.id
      WHERE 1=1
    `;

    const params = [];
    let paramCount = 1;

    if (trang_thai) {
      if (trang_thai === 'Hết hạn') {
        query += ` AND tv.den_ngay < CURRENT_DATE`;
      } else if (trang_thai === 'Đang hiệu lực') {
        query += ` AND tv.den_ngay >= CURRENT_DATE`;
      }
    }

    if (id_nhan_khau) {
      query += ` AND tv.id_nhan_khau = $${paramCount}`;
      params.push(id_nhan_khau);
      paramCount++;
    }

    query += ` ORDER BY tv.created_at DESC`;

    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (error) {
    console.error("Error fetching temporary absences:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get temporary absence by ID
router.get("/:id", authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pool.query(`
      SELECT 
        tv.*,
        nk.ho_ten,
        nk.ma_nhan_khau,
        nk.ngay_sinh,
        nk.gioi_tinh,
        CASE 
          WHEN tv.den_ngay < CURRENT_DATE THEN 'Hết hạn'
          ELSE 'Đang hiệu lực'
        END as tinh_trang
      FROM tam_vang tv
      JOIN nhan_khau nk ON tv.id_nhan_khau = nk.id
      WHERE tv.id = $1
    `, [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy giấy tạm vắng" });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error("Error fetching temporary absence:", error);
    res.status(500).json({ error: error.message });
  }
});

// Create temporary absence
router.post("/", authMiddleware, async (req, res) => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const {
      id_nhan_khau,
      ma_giay_tam_vang,
      noi_den,
      tu_ngay,
      den_ngay,
      ly_do
    } = req.body;

    // Generate ma_giay if not provided
    let maGiay = ma_giay_tam_vang;
    if (!maGiay) {
      const countResult = await client.query('SELECT COUNT(*) FROM tam_vang');
      const count = parseInt(countResult.rows[0].count) + 1;
      maGiay = `TV${new Date().getFullYear()}${String(count).padStart(5, '0')}`;
    }

    const result = await client.query(`
      INSERT INTO tam_vang (id_nhan_khau, ma_giay_tam_vang, noi_den, tu_ngay, den_ngay, ly_do, trang_thai)
      VALUES ($1, $2, $3, $4, $5, $6, 'Đang hiệu lực')
      RETURNING *
    `, [id_nhan_khau, maGiay, noi_den, tu_ngay, den_ngay, ly_do]);

    // Get citizen info
    const citizen = await client.query('SELECT ho_ten, id_ho_khau FROM nhan_khau WHERE id = $1', [id_nhan_khau]);

    // Log the change
    await client.query(`
      INSERT INTO lich_su_bien_dong (id_ho_khau, id_nhan_khau, loai_thay_doi, noi_dung, nguoi_thuc_hien)
      VALUES ($1, $2, 'Tạm vắng', $3, $4)
    `, [
      citizen.rows[0].id_ho_khau,
      id_nhan_khau,
      `${citizen.rows[0].ho_ten} tạm vắng đến ${noi_den} từ ${tu_ngay} đến ${den_ngay}`,
      req.user.name
    ]);

    await client.query('COMMIT');
    res.status(201).json(result.rows[0]);
  } catch (error) {
    await client.query('ROLLBACK');
    console.error("Error creating temporary absence:", error);
    res.status(500).json({ error: error.message });
  } finally {
    client.release();
  }
});

// Update temporary absence
router.put("/:id", authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const { noi_den, tu_ngay, den_ngay, ly_do, trang_thai } = req.body;

    const result = await pool.query(`
      UPDATE tam_vang
      SET noi_den = $1, tu_ngay = $2, den_ngay = $3, ly_do = $4, trang_thai = $5
      WHERE id = $6
      RETURNING *
    `, [noi_den, tu_ngay, den_ngay, ly_do, trang_thai, id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy giấy tạm vắng" });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error("Error updating temporary absence:", error);
    res.status(500).json({ error: error.message });
  }
});

// Delete temporary absence
router.delete("/:id", authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pool.query('DELETE FROM tam_vang WHERE id = $1 RETURNING *', [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy giấy tạm vắng" });
    }

    res.json({ message: "Xóa giấy tạm vắng thành công" });
  } catch (error) {
    console.error("Error deleting temporary absence:", error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
