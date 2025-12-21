const express = require("express");
const router = express.Router();
const pool = require("../config/db");
const authMiddleware = require("../middlewares/authMiddleware");

// Get dashboard statistics for admin
router.get("/tong-quan", authMiddleware, async (req, res) => {
  try {
    // Total households
    const hoKhauResult = await pool.query('SELECT COUNT(*) as count FROM ho_khau WHERE trang_thai = \'Thường trú\'');
    
    // Total citizens (excluding deceased and moved away)
    const nhanKhauResult = await pool.query(`
      SELECT COUNT(*) as count 
      FROM nhan_khau 
      WHERE id_ho_khau IS NOT NULL 
        AND (ghi_chu IS NULL OR (ghi_chu NOT LIKE '%qua đời%' AND ghi_chu NOT LIKE '%chuyển đi%'))
    `);
    
    // Pending requests
    const pendingResult = await pool.query('SELECT COUNT(*) as count FROM yeu_cau WHERE trang_thai = \'Chờ duyệt\'');
    
    // Active temporary absences
    const tamVangResult = await pool.query(`
      SELECT COUNT(*) as count 
      FROM tam_vang 
      WHERE den_ngay >= CURRENT_DATE
    `);
    
    // Active temporary residences
    const tamTruResult = await pool.query(`
      SELECT COUNT(*) as count 
      FROM tam_tru 
      WHERE den_ngay >= CURRENT_DATE
    `);
    
    // Gender distribution
    const genderResult = await pool.query(`
      SELECT 
        gioi_tinh,
        COUNT(*) as count
      FROM nhan_khau
      WHERE id_ho_khau IS NOT NULL 
        AND (ghi_chu IS NULL OR (ghi_chu NOT LIKE '%qua đời%' AND ghi_chu NOT LIKE '%chuyển đi%'))
        AND gioi_tinh IS NOT NULL
      GROUP BY gioi_tinh
    `);
    
    // Age distribution
    const ageDistResult = await pool.query(`
      SELECT
        nhom_tuoi,
        COUNT(*) AS count
      FROM (
        SELECT
          CASE
            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, ngay_sinh)) < 6 THEN 'Mầm non (< 6 tuổi)'
            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, ngay_sinh)) BETWEEN 6 AND 10 THEN 'Tiểu học (6-10 tuổi)'
            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, ngay_sinh)) BETWEEN 11 AND 14 THEN 'THCS (11-14 tuổi)'
            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, ngay_sinh)) BETWEEN 15 AND 17 THEN 'THPT (15-17 tuổi)'
            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, ngay_sinh)) BETWEEN 18 AND 59 THEN 'Lao động (18-59 tuổi)'
            ELSE 'Nghỉ hưu (≥ 60 tuổi)'
          END AS nhom_tuoi
        FROM nhan_khau
        WHERE id_ho_khau IS NOT NULL
          AND ngay_sinh IS NOT NULL
          AND (ghi_chu IS NULL OR (ghi_chu NOT LIKE '%qua đời%' AND ghi_chu NOT LIKE '%chuyển đi%'))
      ) t
      GROUP BY nhom_tuoi
      ORDER BY
        CASE nhom_tuoi
          WHEN 'Mầm non (< 6 tuổi)' THEN 1
          WHEN 'Tiểu học (6-10 tuổi)' THEN 2
          WHEN 'THCS (11-14 tuổi)' THEN 3
          WHEN 'THPT (15-17 tuổi)' THEN 4
          WHEN 'Lao động (18-59 tuổi)' THEN 5
          ELSE 6
        END;
    `);

    // Recent changes
    const recentChangesResult = await pool.query(`
      SELECT 
        loai_thay_doi,
        COUNT(*) as count
      FROM lich_su_bien_dong
      WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
      GROUP BY loai_thay_doi
    `);

    res.json({
      tong_ho_khau: parseInt(hoKhauResult.rows[0].count),
      tong_nhan_khau: parseInt(nhanKhauResult.rows[0].count),
      yeu_cau_cho_duyet: parseInt(pendingResult.rows[0].count),
      tam_vang_hieu_luc: parseInt(tamVangResult.rows[0].count),
      tam_tru_hieu_luc: parseInt(tamTruResult.rows[0].count),
      phan_bo_gioi_tinh: genderResult.rows,
      phan_bo_do_tuoi: ageDistResult.rows,
      bien_dong_gan_day: recentChangesResult.rows
    });
  } catch (error) {
    console.error("Error fetching dashboard statistics:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get resident dashboard statistics
router.get("/nguoi-dan/:id", authMiddleware, async (req, res) => {
  try {
    const { id } = req.params; // User ID
    
    // Get user's household
    const userResult = await pool.query(`
      SELECT nd.*, nk.id_ho_khau 
      FROM nguoidung nd
      LEFT JOIN nhan_khau nk ON nd.id_nhan_khau = nk.id
      WHERE nd.id = $1
    `, [id]);

    if (userResult.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy người dùng" });
    }

    const user = userResult.rows[0];
    const hoKhauId = user.id_ho_khau;

    if (!hoKhauId) {
      return res.json({
        co_ho_khau: false,
        message: "Người dùng chưa được liên kết với hộ khẩu"
      });
    }

    // Get household info
    const hoKhauResult = await pool.query(`
      SELECT 
        hk.*,
        nk.ho_ten as ten_chu_ho,
        (SELECT COUNT(*) FROM nhan_khau WHERE id_ho_khau = hk.id) as so_thanh_vien
      FROM ho_khau hk
      LEFT JOIN nhan_khau nk ON hk.id_chu_ho = nk.id
      WHERE hk.id = $1
    `, [hoKhauId]);

    // Get household members
    const membersResult = await pool.query(`
      SELECT id, ho_ten, ngay_sinh, gioi_tinh, quan_he_voi_chu_ho
      FROM nhan_khau
      WHERE id_ho_khau = $1
      ORDER BY 
        CASE quan_he_voi_chu_ho 
          WHEN 'Chủ hộ' THEN 1
          ELSE 2
        END,
        ngay_sinh
    `, [hoKhauId]);

    // Get user's pending requests
    const requestsResult = await pool.query(`
      SELECT id, loai_yeu_cau, trang_thai, ngay_gui
      FROM yeu_cau
      WHERE id_nguoi_gui = $1
      ORDER BY created_at DESC
      LIMIT 5
    `, [id]);

    res.json({
      co_ho_khau: true,
      ho_khau: hoKhauResult.rows[0],
      thanh_vien: membersResult.rows,
      yeu_cau_gan_day: requestsResult.rows
    });
  } catch (error) {
    console.error("Error fetching resident dashboard:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get change history
router.get("/lich-su-bien-dong", authMiddleware, async (req, res) => {
  try {
    const { id_ho_khau, id_nhan_khau, loai_thay_doi, tu_ngay, den_ngay } = req.query;

    let query = `
      SELECT 
        ls.*,
        hk.ma_ho_khau,
        nk.ho_ten as ten_nhan_khau
      FROM lich_su_bien_dong ls
      LEFT JOIN ho_khau hk ON ls.id_ho_khau = hk.id
      LEFT JOIN nhan_khau nk ON ls.id_nhan_khau = nk.id
      WHERE 1=1
    `;

    const params = [];
    let paramCount = 1;

    if (id_ho_khau) {
      query += ` AND ls.id_ho_khau = $${paramCount}`;
      params.push(id_ho_khau);
      paramCount++;
    }

    if (id_nhan_khau) {
      query += ` AND ls.id_nhan_khau = $${paramCount}`;
      params.push(id_nhan_khau);
      paramCount++;
    }

    if (loai_thay_doi) {
      query += ` AND ls.loai_thay_doi = $${paramCount}`;
      params.push(loai_thay_doi);
      paramCount++;
    }

    if (tu_ngay) {
      query += ` AND ls.ngay_thay_doi >= $${paramCount}`;
      params.push(tu_ngay);
      paramCount++;
    }

    if (den_ngay) {
      query += ` AND ls.ngay_thay_doi <= $${paramCount}`;
      params.push(den_ngay);
      paramCount++;
    }

    query += ` ORDER BY ls.created_at DESC LIMIT 100`;

    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (error) {
    console.error("Error fetching change history:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get statistics by filters
router.get("/thong-ke/loc", authMiddleware, async (req, res) => {
  try {
    const { 
      loai_thong_ke, // 'gioi_tinh', 'do_tuoi', 'tam_vang', 'tam_tru'
      gioi_tinh,
      do_tuoi_min,
      do_tuoi_max
    } = req.query;

    let result;

    switch (loai_thong_ke) {
      case 'gioi_tinh':
        result = await pool.query(`
          SELECT 
            nk.*,
            hk.ma_ho_khau,
            hk.so_nha || ', ' || hk.duong_pho || ', ' || hk.phuong_xa || ', ' || hk.quan_huyen as dia_chi
          FROM nhan_khau nk
          LEFT JOIN ho_khau hk ON nk.id_ho_khau = hk.id
          WHERE nk.id_ho_khau IS NOT NULL 
            AND (nk.ghi_chu IS NULL OR (nk.ghi_chu NOT LIKE '%qua đời%' AND nk.ghi_chu NOT LIKE '%chuyển đi%'))
            ${gioi_tinh ? `AND nk.gioi_tinh = '${gioi_tinh}'` : ''}
          ORDER BY nk.ho_ten
        `);
        break;

      case 'do_tuoi':
        let ageCondition = '';
        if (do_tuoi_min && do_tuoi_max) {
          ageCondition = `AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, nk.ngay_sinh)) BETWEEN ${do_tuoi_min} AND ${do_tuoi_max}`;
        } else if (do_tuoi_min) {
          ageCondition = `AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, nk.ngay_sinh)) >= ${do_tuoi_min}`;
        } else if (do_tuoi_max) {
          ageCondition = `AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, nk.ngay_sinh)) <= ${do_tuoi_max}`;
        }

        result = await pool.query(`
          SELECT 
            nk.*,
            hk.ma_ho_khau,
            hk.so_nha || ', ' || hk.duong_pho || ', ' || hk.phuong_xa || ', ' || hk.quan_huyen as dia_chi,
            EXTRACT(YEAR FROM AGE(CURRENT_DATE, nk.ngay_sinh)) as tuoi
          FROM nhan_khau nk
          LEFT JOIN ho_khau hk ON nk.id_ho_khau = hk.id
          WHERE nk.id_ho_khau IS NOT NULL 
            AND nk.ngay_sinh IS NOT NULL
            AND (nk.ghi_chu IS NULL OR (nk.ghi_chu NOT LIKE '%qua đời%' AND nk.ghi_chu NOT LIKE '%chuyển đi%'))
            ${ageCondition}
          ORDER BY nk.ngay_sinh
        `);
        break;

      case 'tam_vang':
        result = await pool.query(`
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
          ORDER BY tv.tu_ngay DESC
        `);
        break;

      case 'tam_tru':
        result = await pool.query(`
          SELECT 
            tt.*,
            nk.ho_ten,
            nk.ma_nhan_khau,
            nk.nguyen_quan,
            CASE 
              WHEN tt.den_ngay < CURRENT_DATE THEN 'Hết hạn'
              ELSE 'Đang hiệu lực'
            END as tinh_trang
          FROM tam_tru tt
          JOIN nhan_khau nk ON tt.id_nhan_khau = nk.id
          ORDER BY tt.tu_ngay DESC
        `);
        break;

      default:
        return res.status(400).json({ message: "Loại thống kê không hợp lệ" });
    }

    res.json(result.rows);
  } catch (error) {
    console.error("Error fetching filtered statistics:", error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
