const express = require("express");
const router = express.Router();
const pool = require("../config/db");
const authMiddleware = require("../middlewares/authMiddleware");

// Get all temporary residences
router.get("/", authMiddleware, async (req, res) => {
  try {
    const { trang_thai, search } = req.query;

    let query = `
      SELECT 
        tt.*,
        nk.ho_ten,
        nk.ma_nhan_khau,
        nk.ngay_sinh,
        nk.gioi_tinh,
        CASE 
          WHEN tt.den_ngay < CURRENT_DATE THEN 'Hết hạn'
          ELSE 'Đang hiệu lực'
        END as tinh_trang
      FROM tam_tru tt
      JOIN nhan_khau nk ON tt.id_nhan_khau = nk.id
      WHERE 1=1
    `;

    const params = [];
    let paramCount = 1;

    if (trang_thai) {
      if (trang_thai === 'Hết hạn') {
        query += ` AND tt.den_ngay < CURRENT_DATE`;
      } else if (trang_thai === 'Đang hiệu lực') {
        query += ` AND tt.den_ngay >= CURRENT_DATE`;
      }
    }

    if (search) {
      query += ` AND (nk.ho_ten ILIKE $${paramCount} OR nk.ma_nhan_khau ILIKE $${paramCount} OR tt.ma_giay_tam_tru ILIKE $${paramCount})`;
      params.push(`%${search}%`);
      paramCount++;
    }

    query += ` ORDER BY tt.created_at DESC`;

    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (error) {
    console.error("Error fetching temporary residences:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get temporary residence by ID
router.get("/:id", authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pool.query(`
      SELECT 
        tt.*,
        nk.ho_ten,
        nk.ma_nhan_khau,
        nk.ngay_sinh,
        nk.gioi_tinh,
        nk.nguyen_quan,
        CASE 
          WHEN tt.den_ngay < CURRENT_DATE THEN 'Hết hạn'
          ELSE 'Đang hiệu lực'
        END as tinh_trang
      FROM tam_tru tt
      JOIN nhan_khau nk ON tt.id_nhan_khau = nk.id
      WHERE tt.id = $1
    `, [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy giấy tạm trú" });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error("Error fetching temporary residence:", error);
    res.status(500).json({ error: error.message });
  }
});

// Create temporary residence (with citizen)
router.post("/", authMiddleware, async (req, res) => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const {
      // Citizen info
      ho_ten,
      ngay_sinh,
      gioi_tinh,
      noi_sinh,
      nguyen_quan,
      dan_toc,
      ton_giao,
      quoc_tich,
      so_cmt,
      ngay_cap,
      noi_cap,
      // Temporary residence info
      ma_giay_tam_tru,
      so_dien_thoai,
      tu_ngay,
      den_ngay,
      ly_do
    } = req.body;

    // Generate ma_nhan_khau for temporary resident
    const countResult = await client.query('SELECT COUNT(*) FROM nhan_khau');
    const count = parseInt(countResult.rows[0].count) + 1;
    const ma_nhan_khau = `TT${new Date().getFullYear()}${String(count).padStart(5, '0')}`;

    // Create citizen record (without household)
    const citizenResult = await client.query(`
      INSERT INTO nhan_khau (
        ma_nhan_khau, ho_ten, ngay_sinh, gioi_tinh, noi_sinh, nguyen_quan,
        dan_toc, ton_giao, quoc_tich, ghi_chu
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'Tạm trú')
      RETURNING *
    `, [ma_nhan_khau, ho_ten, ngay_sinh, gioi_tinh, noi_sinh, nguyen_quan, dan_toc, ton_giao, quoc_tich]);

    const citizenId = citizenResult.rows[0].id;

    // Add ID card if provided
    if (so_cmt) {
      await client.query(`
        INSERT INTO chung_minh_thu (id_nhan_khau, so_cmt, ngay_cap, noi_cap)
        VALUES ($1, $2, $3, $4)
      `, [citizenId, so_cmt, ngay_cap, noi_cap]);
    }

    // Generate ma_giay if not provided
    let maGiay = ma_giay_tam_tru;
    if (!maGiay) {
      const ttCountResult = await client.query('SELECT COUNT(*) FROM tam_tru');
      const ttCount = parseInt(ttCountResult.rows[0].count) + 1;
      maGiay = `GTT${new Date().getFullYear()}${String(ttCount).padStart(5, '0')}`;
    }

    // Create temporary residence record
    const tamTruResult = await client.query(`
      INSERT INTO tam_tru (id_nhan_khau, ma_giay_tam_tru, so_dien_thoai, tu_ngay, den_ngay, ly_do, trang_thai)
      VALUES ($1, $2, $3, $4, $5, $6, 'Đang hiệu lực')
      RETURNING *
    `, [citizenId, maGiay, so_dien_thoai, tu_ngay, den_ngay, ly_do]);

    // Log the change
    await client.query(`
      INSERT INTO lich_su_bien_dong (id_nhan_khau, loai_thay_doi, noi_dung, nguoi_thuc_hien)
      VALUES ($1, 'Tạm trú', $2, $3)
    `, [citizenId, `${ho_ten} đăng ký tạm trú từ ${tu_ngay} đến ${den_ngay}`, req.user.name]);

    await client.query('COMMIT');
    res.status(201).json({
      ...tamTruResult.rows[0],
      nhan_khau: citizenResult.rows[0]
    });
  } catch (error) {
    await client.query('ROLLBACK');
    console.error("Error creating temporary residence:", error);
    res.status(500).json({ error: error.message });
  } finally {
    client.release();
  }
});

// Update temporary residence
router.put("/:id", authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const { so_dien_thoai, tu_ngay, den_ngay, ly_do, trang_thai } = req.body;

    const result = await pool.query(`
      UPDATE tam_tru
      SET so_dien_thoai = $1, tu_ngay = $2, den_ngay = $3, ly_do = $4, trang_thai = $5
      WHERE id = $6
      RETURNING *
    `, [so_dien_thoai, tu_ngay, den_ngay, ly_do, trang_thai, id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy giấy tạm trú" });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error("Error updating temporary residence:", error);
    res.status(500).json({ error: error.message });
  }
});

// Delete temporary residence
router.delete("/:id", authMiddleware, async (req, res) => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    
    const { id } = req.params;
    
    // Get citizen ID before deleting
    const tamTruResult = await client.query('SELECT id_nhan_khau FROM tam_tru WHERE id = $1', [id]);
    if (tamTruResult.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy giấy tạm trú" });
    }

    const citizenId = tamTruResult.rows[0].id_nhan_khau;

    // Delete temporary residence
    await client.query('DELETE FROM tam_tru WHERE id = $1', [id]);

    // Delete citizen record if it's only temporary residence
    await client.query('DELETE FROM nhan_khau WHERE id = $1 AND id_ho_khau IS NULL', [citizenId]);

    await client.query('COMMIT');
    res.json({ message: "Xóa giấy tạm trú thành công" });
  } catch (error) {
    await client.query('ROLLBACK');
    console.error("Error deleting temporary residence:", error);
    res.status(500).json({ error: error.message });
  } finally {
    client.release();
  }
});

// Get statistics
router.get("/thong-ke/tong-hop", authMiddleware, async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT 
        COUNT(*) FILTER (WHERE den_ngay >= CURRENT_DATE) as dang_hieu_luc,
        COUNT(*) FILTER (WHERE den_ngay < CURRENT_DATE) as het_han,
        COUNT(*) as tong_so
      FROM tam_tru
    `);

    res.json(result.rows[0]);
  } catch (error) {
    console.error("Error fetching statistics:", error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
