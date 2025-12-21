const express = require("express");
const router = express.Router();
const pool = require("../config/db");
const authMiddleware = require("../middlewares/authMiddleware");

// Get all households
router.get("/", authMiddleware, async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT 
        hk.*,
        nk.ho_ten as ten_chu_ho,
        (SELECT COUNT(*) FROM nhan_khau WHERE id_ho_khau = hk.id) as so_thanh_vien
      FROM ho_khau hk
      LEFT JOIN nhan_khau nk ON hk.id_chu_ho = nk.id
      ORDER BY hk.created_at DESC
    `);
    res.json(result.rows);
  } catch (error) {
    console.error("Error fetching households:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get household by ID
router.get("/:id", authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    
    // Get household info
    const hoKhauResult = await pool.query(`
      SELECT 
        hk.*,
        nk.ho_ten as ten_chu_ho
      FROM ho_khau hk
      LEFT JOIN nhan_khau nk ON hk.id_chu_ho = nk.id
      WHERE hk.id = $1
    `, [id]);

    if (hoKhauResult.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy hộ khẩu" });
    }

    // Get household members
    const membersResult = await pool.query(`
      SELECT 
        nk.*,
        cmt.so_cmt,
        cmt.ngay_cap as ngay_cap_cmt,
        cmt.noi_cap as noi_cap_cmt
      FROM nhan_khau nk
      LEFT JOIN chung_minh_thu cmt ON nk.id = cmt.id_nhan_khau
      WHERE nk.id_ho_khau = $1
      ORDER BY 
        CASE quan_he_voi_chu_ho 
          WHEN 'Chủ hộ' THEN 1
          WHEN 'Vợ' THEN 2
          WHEN 'Chồng' THEN 2
          ELSE 3
        END,
        nk.ngay_sinh
    `, [id]);

    res.json({
      ...hoKhauResult.rows[0],
      thanh_vien: membersResult.rows
    });
  } catch (error) {
    console.error("Error fetching household:", error);
    res.status(500).json({ error: error.message });
  }
});

// Create new household
router.post("/", authMiddleware, async (req, res) => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const { 
      ma_ho_khau, 
      so_nha, 
      duong_pho, 
      phuong_xa, 
      quan_huyen,
      chu_ho,  // Citizen data for the head of household
      thanh_vien // Array of other members
    } = req.body;

    // Create household
    const hoKhauResult = await client.query(`
      INSERT INTO ho_khau (ma_ho_khau, so_nha, duong_pho, phuong_xa, quan_huyen, ngay_tao, trang_thai)
      VALUES ($1, $2, $3, $4, $5, CURRENT_DATE, 'Thường trú')
      RETURNING *
    `, [ma_ho_khau, so_nha, duong_pho, phuong_xa, quan_huyen]);

    const hoKhauId = hoKhauResult.rows[0].id;

    // Create head of household
    const chuHoResult = await client.query(`
      INSERT INTO nhan_khau (
        ma_nhan_khau, ho_ten, ngay_sinh, gioi_tinh, noi_sinh, nguyen_quan,
        dan_toc, ton_giao, quoc_tich, nghe_nghiep, noi_lam_viec,
        id_ho_khau, quan_he_voi_chu_ho, ngay_dk_thuong_tru
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, 'Chủ hộ', CURRENT_DATE)
      RETURNING *
    `, [
      chu_ho.ma_nhan_khau, chu_ho.ho_ten, chu_ho.ngay_sinh, chu_ho.gioi_tinh,
      chu_ho.noi_sinh, chu_ho.nguyen_quan, chu_ho.dan_toc, chu_ho.ton_giao,
      chu_ho.quoc_tich, chu_ho.nghe_nghiep, chu_ho.noi_lam_viec, hoKhauId
    ]);

    const chuHoId = chuHoResult.rows[0].id;

    // Update household with head of household
    await client.query('UPDATE ho_khau SET id_chu_ho = $1 WHERE id = $2', [chuHoId, hoKhauId]);

    // Add ID card if provided
    if (chu_ho.so_cmt) {
      await client.query(`
        INSERT INTO chung_minh_thu (id_nhan_khau, so_cmt, ngay_cap, noi_cap)
        VALUES ($1, $2, $3, $4)
      `, [chuHoId, chu_ho.so_cmt, chu_ho.ngay_cap, chu_ho.noi_cap]);
    }

    // Add other members if provided
    if (thanh_vien && thanh_vien.length > 0) {
      for (const tv of thanh_vien) {
        const tvResult = await client.query(`
          INSERT INTO nhan_khau (
            ma_nhan_khau, ho_ten, ngay_sinh, gioi_tinh, noi_sinh, nguyen_quan,
            dan_toc, ton_giao, quoc_tich, nghe_nghiep, noi_lam_viec,
            id_ho_khau, quan_he_voi_chu_ho, ngay_dk_thuong_tru
          )
          VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, CURRENT_DATE)
          RETURNING *
        `, [
          tv.ma_nhan_khau, tv.ho_ten, tv.ngay_sinh, tv.gioi_tinh,
          tv.noi_sinh, tv.nguyen_quan, tv.dan_toc, tv.ton_giao,
          tv.quoc_tich, tv.nghe_nghiep, tv.noi_lam_viec, hoKhauId, tv.quan_he_voi_chu_ho
        ]);

        if (tv.so_cmt) {
          await client.query(`
            INSERT INTO chung_minh_thu (id_nhan_khau, so_cmt, ngay_cap, noi_cap)
            VALUES ($1, $2, $3, $4)
          `, [tvResult.rows[0].id, tv.so_cmt, tv.ngay_cap, tv.noi_cap]);
        }
      }
    }

    // Log the change
    await client.query(`
      INSERT INTO lich_su_bien_dong (id_ho_khau, loai_thay_doi, noi_dung, nguoi_thuc_hien)
      VALUES ($1, 'Thành lập hộ', $2, $3)
    `, [hoKhauId, `Thành lập hộ khẩu ${ma_ho_khau}`, req.user.name]);

    await client.query('COMMIT');
    res.status(201).json(hoKhauResult.rows[0]);
  } catch (error) {
    await client.query('ROLLBACK');
    console.error("Error creating household:", error);
    res.status(500).json({ error: error.message });
  } finally {
    client.release();
  }
});

// Update household
router.put("/:id", authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const { so_nha, duong_pho, phuong_xa, quan_huyen, trang_thai } = req.body;

    const result = await pool.query(`
      UPDATE ho_khau
      SET so_nha = $1, duong_pho = $2, phuong_xa = $3, quan_huyen = $4, trang_thai = $5
      WHERE id = $6
      RETURNING *
    `, [so_nha, duong_pho, phuong_xa, quan_huyen, trang_thai, id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy hộ khẩu" });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error("Error updating household:", error);
    res.status(500).json({ error: error.message });
  }
});

// Household separation (Tách hộ)
router.post("/:id/tach-ho", authMiddleware, async (req, res) => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const { id } = req.params;
    const { 
      id_chu_ho_moi, 
      danh_sach_thanh_vien, 
      ma_ho_khau_moi,
      so_nha,
      duong_pho,
      phuong_xa,
      quan_huyen
    } = req.body;

    // Get current household info
    const oldHoKhau = await client.query('SELECT * FROM ho_khau WHERE id = $1', [id]);
    if (oldHoKhau.rows.length === 0) {
      throw new Error('Hộ khẩu không tồn tại');
    }

    // Create new household
    const newHoKhau = await client.query(`
      INSERT INTO ho_khau (ma_ho_khau, so_nha, duong_pho, phuong_xa, quan_huyen, id_chu_ho, ngay_tao, trang_thai)
      VALUES ($1, $2, $3, $4, $5, $6, CURRENT_DATE, 'Thường trú')
      RETURNING *
    `, [ma_ho_khau_moi, so_nha, duong_pho, phuong_xa, quan_huyen, id_chu_ho_moi]);

    const newHoKhauId = newHoKhau.rows[0].id;

    // Move members to new household
    for (const memberId of danh_sach_thanh_vien) {
      await client.query(`
        UPDATE nhan_khau
        SET id_ho_khau = $1, ngay_dk_thuong_tru = CURRENT_DATE
        WHERE id = $2
      `, [newHoKhauId, memberId]);
    }

    // Update relation for new head of household
    await client.query(`
      UPDATE nhan_khau
      SET quan_he_voi_chu_ho = 'Chủ hộ'
      WHERE id = $1
    `, [id_chu_ho_moi]);

    // Log the change for old household
    await client.query(`
      INSERT INTO lich_su_bien_dong (id_ho_khau, loai_thay_doi, noi_dung, nguoi_thuc_hien)
      VALUES ($1, 'Tách hộ', $2, $3)
    `, [id, `Tách ra hộ khẩu mới ${ma_ho_khau_moi}`, req.user.name]);

    // Log the change for new household
    await client.query(`
      INSERT INTO lich_su_bien_dong (id_ho_khau, loai_thay_doi, noi_dung, nguoi_thuc_hien)
      VALUES ($1, 'Thành lập hộ', $2, $3)
    `, [newHoKhauId, `Tách từ hộ khẩu ${oldHoKhau.rows[0].ma_ho_khau}`, req.user.name]);

    await client.query('COMMIT');
    res.json({ message: "Tách hộ thành công", ho_khau_moi: newHoKhau.rows[0] });
  } catch (error) {
    await client.query('ROLLBACK');
    console.error("Error separating household:", error);
    res.status(500).json({ error: error.message });
  } finally {
    client.release();
  }
});

// Delete household
router.delete("/:id", authMiddleware, async (req, res) => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    
    const { id } = req.params;

    // Check if household has members
    const membersResult = await client.query('SELECT COUNT(*) FROM nhan_khau WHERE id_ho_khau = $1', [id]);
    if (parseInt(membersResult.rows[0].count) > 0) {
      return res.status(400).json({ message: "Không thể xóa hộ khẩu còn thành viên" });
    }

    await client.query('DELETE FROM ho_khau WHERE id = $1', [id]);
    
    await client.query('COMMIT');
    res.json({ message: "Xóa hộ khẩu thành công" });
  } catch (error) {
    await client.query('ROLLBACK');
    console.error("Error deleting household:", error);
    res.status(500).json({ error: error.message });
  } finally {
    client.release();
  }
});

module.exports = router;
