const express = require("express");
const router = express.Router();
const pool = require("../config/db");
const authMiddleware = require("../middlewares/authMiddleware");

// Get all citizens with filters
router.get("/", authMiddleware, async (req, res) => {
  try {
    const { gioi_tinh, do_tuoi_min, do_tuoi_max, id_ho_khau, search } = req.query;
    
    let query = `
      SELECT 
        nk.*,
        hk.ma_ho_khau,
        hk.so_nha || ', ' || hk.duong_pho || ', ' || hk.phuong_xa || ', ' || hk.quan_huyen as dia_chi,
        cmt.so_cmt,
        cmt.ngay_cap as ngay_cap_cmt,
        cmt.noi_cap as noi_cap_cmt,
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, nk.ngay_sinh)) as tuoi
      FROM nhan_khau nk
      LEFT JOIN ho_khau hk ON nk.id_ho_khau = hk.id
      LEFT JOIN chung_minh_thu cmt ON nk.id = cmt.id_nhan_khau
      WHERE 1=1
    `;
    
    const params = [];
    let paramCount = 1;

    if (gioi_tinh) {
      query += ` AND nk.gioi_tinh = $${paramCount}`;
      params.push(gioi_tinh);
      paramCount++;
    }

    if (do_tuoi_min) {
      query += ` AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, nk.ngay_sinh)) >= $${paramCount}`;
      params.push(do_tuoi_min);
      paramCount++;
    }

    if (do_tuoi_max) {
      query += ` AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, nk.ngay_sinh)) <= $${paramCount}`;
      params.push(do_tuoi_max);
      paramCount++;
    }

    if (id_ho_khau) {
      query += ` AND nk.id_ho_khau = $${paramCount}`;
      params.push(id_ho_khau);
      paramCount++;
    }

    if (search) {
      query += ` AND (nk.ho_ten ILIKE $${paramCount} OR nk.ma_nhan_khau ILIKE $${paramCount} OR cmt.so_cmt ILIKE $${paramCount})`;
      params.push(`%${search}%`);
      paramCount++;
    }

    query += ` ORDER BY nk.created_at DESC`;

    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (error) {
    console.error("Error fetching citizens:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get citizen by ID
router.get("/:id", authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pool.query(`
      SELECT 
        nk.*,
        hk.ma_ho_khau,
        hk.so_nha || ', ' || hk.duong_pho || ', ' || hk.phuong_xa || ', ' || hk.quan_huyen as dia_chi,
        cmt.so_cmt,
        cmt.ngay_cap as ngay_cap_cmt,
        cmt.noi_cap as noi_cap_cmt,
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, nk.ngay_sinh)) as tuoi
      FROM nhan_khau nk
      LEFT JOIN ho_khau hk ON nk.id_ho_khau = hk.id
      LEFT JOIN chung_minh_thu cmt ON nk.id = cmt.id_nhan_khau
      WHERE nk.id = $1
    `, [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy nhân khẩu" });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error("Error fetching citizen:", error);
    res.status(500).json({ error: error.message });
  }
});

// Create new citizen (birth)
router.post("/", authMiddleware, async (req, res) => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const {
      ma_nhan_khau,
      ho_ten,
      bi_danh,
      ngay_sinh,
      gioi_tinh,
      noi_sinh,
      nguyen_quan,
      dan_toc,
      ton_giao,
      quoc_tich,
      nghe_nghiep,
      noi_lam_viec,
      id_ho_khau,
      quan_he_voi_chu_ho,
      dia_chi_truoc_khi_chuyen,
      ghi_chu,
      so_cmt,
      ngay_cap,
      noi_cap
    } = req.body;

    // Create citizen
    const result = await client.query(`
      INSERT INTO nhan_khau (
        ma_nhan_khau, ho_ten, bi_danh, ngay_sinh, gioi_tinh, noi_sinh, nguyen_quan,
        dan_toc, ton_giao, quoc_tich, nghe_nghiep, noi_lam_viec,
        id_ho_khau, quan_he_voi_chu_ho, ngay_dk_thuong_tru, dia_chi_truoc_khi_chuyen, ghi_chu
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, CURRENT_DATE, $15, $16)
      RETURNING *
    `, [
      ma_nhan_khau, ho_ten, bi_danh, ngay_sinh, gioi_tinh, noi_sinh, nguyen_quan,
      dan_toc, ton_giao, quoc_tich, nghe_nghiep, noi_lam_viec,
      id_ho_khau, quan_he_voi_chu_ho, dia_chi_truoc_khi_chuyen, ghi_chu
    ]);

    const citizenId = result.rows[0].id;

    // Add ID card if provided
    if (so_cmt) {
      await client.query(`
        INSERT INTO chung_minh_thu (id_nhan_khau, so_cmt, ngay_cap, noi_cap)
        VALUES ($1, $2, $3, $4)
      `, [citizenId, so_cmt, ngay_cap, noi_cap]);
    }

    // Log the change
    const loaiThayDoi = ghi_chu && ghi_chu.includes('Mới sinh') ? 'Sinh con' : 'Thêm nhân khẩu';
    await client.query(`
      INSERT INTO lich_su_bien_dong (id_ho_khau, id_nhan_khau, loai_thay_doi, noi_dung, nguoi_thuc_hien)
      VALUES ($1, $2, $3, $4, $5)
    `, [id_ho_khau, citizenId, loaiThayDoi, `Thêm nhân khẩu ${ho_ten}`, req.user.name]);

    await client.query('COMMIT');
    res.status(201).json(result.rows[0]);
  } catch (error) {
    await client.query('ROLLBACK');
    console.error("Error creating citizen:", error);
    res.status(500).json({ error: error.message });
  } finally {
    client.release();
  }
});

// Update citizen
router.put("/:id", authMiddleware, async (req, res) => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const { id } = req.params;
    const {
      ho_ten,
      bi_danh,
      ngay_sinh,
      gioi_tinh,
      noi_sinh,
      nguyen_quan,
      dan_toc,
      ton_giao,
      quoc_tich,
      nghe_nghiep,
      noi_lam_viec,
      quan_he_voi_chu_ho,
      dia_chi_truoc_khi_chuyen,
      ghi_chu,
      so_cmt,
      ngay_cap,
      noi_cap
    } = req.body;

    const result = await client.query(`
      UPDATE nhan_khau
      SET ho_ten = $1, bi_danh = $2, ngay_sinh = $3, gioi_tinh = $4, noi_sinh = $5,
          nguyen_quan = $6, dan_toc = $7, ton_giao = $8, quoc_tich = $9,
          nghe_nghiep = $10, noi_lam_viec = $11, quan_he_voi_chu_ho = $12,
          dia_chi_truoc_khi_chuyen = $13, ghi_chu = $14
      WHERE id = $15
      RETURNING *
    `, [
      ho_ten, bi_danh, ngay_sinh, gioi_tinh, noi_sinh, nguyen_quan,
      dan_toc, ton_giao, quoc_tich, nghe_nghiep, noi_lam_viec,
      quan_he_voi_chu_ho, dia_chi_truoc_khi_chuyen, ghi_chu, id
    ]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy nhân khẩu" });
    }

    // Update ID card if provided
    if (so_cmt) {
      const cmtCheck = await client.query('SELECT id FROM chung_minh_thu WHERE id_nhan_khau = $1', [id]);
      
      if (cmtCheck.rows.length > 0) {
        await client.query(`
          UPDATE chung_minh_thu
          SET so_cmt = $1, ngay_cap = $2, noi_cap = $3
          WHERE id_nhan_khau = $4
        `, [so_cmt, ngay_cap, noi_cap, id]);
      } else {
        await client.query(`
          INSERT INTO chung_minh_thu (id_nhan_khau, so_cmt, ngay_cap, noi_cap)
          VALUES ($1, $2, $3, $4)
        `, [id, so_cmt, ngay_cap, noi_cap]);
      }
    }

    await client.query('COMMIT');
    res.json(result.rows[0]);
  } catch (error) {
    await client.query('ROLLBACK');
    console.error("Error updating citizen:", error);
    res.status(500).json({ error: error.message });
  } finally {
    client.release();
  }
});

// Mark citizen as deceased
router.post("/:id/khai-tu", authMiddleware, async (req, res) => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const { id } = req.params;
    const { ngay_mat, ly_do } = req.body;

    const result = await client.query(`
      UPDATE nhan_khau
      SET ghi_chu = $1
      WHERE id = $2
      RETURNING *
    `, [`Đã qua đời ngày ${ngay_mat}. ${ly_do || ''}`, id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy nhân khẩu" });
    }

    // Log the change
    await client.query(`
      INSERT INTO lich_su_bien_dong (id_ho_khau, id_nhan_khau, loai_thay_doi, noi_dung, nguoi_thuc_hien)
      VALUES ($1, $2, 'Qua đời', $3, $4)
    `, [result.rows[0].id_ho_khau, id, `${result.rows[0].ho_ten} qua đời ngày ${ngay_mat}`, req.user.name]);

    await client.query('COMMIT');
    res.json({ message: "Khai tử thành công", citizen: result.rows[0] });
  } catch (error) {
    await client.query('ROLLBACK');
    console.error("Error marking citizen as deceased:", error);
    res.status(500).json({ error: error.message });
  } finally {
    client.release();
  }
});

// Mark citizen as moved away
router.post("/:id/chuyen-di", authMiddleware, async (req, res) => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const { id } = req.params;
    const { noi_chuyen_den, ngay_chuyen } = req.body;

    const citizen = await client.query('SELECT * FROM nhan_khau WHERE id = $1', [id]);
    if (citizen.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy nhân khẩu" });
    }

    const result = await client.query(`
      UPDATE nhan_khau
      SET id_ho_khau = NULL, ghi_chu = $1, dia_chi_truoc_khi_chuyen = $2
      WHERE id = $3
      RETURNING *
    `, [`Đã chuyển đi ${noi_chuyen_den} ngày ${ngay_chuyen}`, 
        citizen.rows[0].id_ho_khau, id]);

    // Log the change
    await client.query(`
      INSERT INTO lich_su_bien_dong (id_ho_khau, id_nhan_khau, loai_thay_doi, noi_dung, nguoi_thuc_hien)
      VALUES ($1, $2, 'Chuyển đi', $3, $4)
    `, [citizen.rows[0].id_ho_khau, id, `${citizen.rows[0].ho_ten} chuyển đi ${noi_chuyen_den}`, req.user.name]);

    await client.query('COMMIT');
    res.json({ message: "Đã ghi nhận chuyển đi", citizen: result.rows[0] });
  } catch (error) {
    await client.query('ROLLBACK');
    console.error("Error marking citizen as moved:", error);
    res.status(500).json({ error: error.message });
  } finally {
    client.release();
  }
});

// Get citizen statistics
router.get("/thong-ke/tong-hop", authMiddleware, async (req, res) => {
  try {
    const { gioi_tinh, do_tuoi_min, do_tuoi_max } = req.query;

    // Total citizens
    const totalResult = await pool.query('SELECT COUNT(*) as total FROM nhan_khau WHERE id_ho_khau IS NOT NULL');

    // By gender
    const genderResult = await pool.query(`
      SELECT gioi_tinh, COUNT(*) as count
      FROM nhan_khau
      WHERE id_ho_khau IS NOT NULL AND gioi_tinh IS NOT NULL
      GROUP BY gioi_tinh
    `);

    // By age groups
    const ageGroupResult = await pool.query(`
      SELECT 
        CASE
          WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, ngay_sinh)) < 6 THEN 'Mầm non'
          WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, ngay_sinh)) BETWEEN 6 AND 10 THEN 'Tiểu học'
          WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, ngay_sinh)) BETWEEN 11 AND 14 THEN 'THCS'
          WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, ngay_sinh)) BETWEEN 15 AND 17 THEN 'THPT'
          WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, ngay_sinh)) BETWEEN 18 AND 59 THEN 'Lao động'
          ELSE 'Nghỉ hưu'
        END as nhom_tuoi,
        COUNT(*) as count
      FROM nhan_khau
      WHERE id_ho_khau IS NOT NULL AND ngay_sinh IS NOT NULL
      GROUP BY nhom_tuoi
      ORDER BY 
        CASE nhom_tuoi
          WHEN 'Mầm non' THEN 1
          WHEN 'Tiểu học' THEN 2
          WHEN 'THCS' THEN 3
          WHEN 'THPT' THEN 4
          WHEN 'Lao động' THEN 5
          ELSE 6
        END
    `);

    res.json({
      tong_so: parseInt(totalResult.rows[0].total),
      theo_gioi_tinh: genderResult.rows,
      theo_nhom_tuoi: ageGroupResult.rows
    });
  } catch (error) {
    console.error("Error fetching statistics:", error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
