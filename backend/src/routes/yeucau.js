const express = require("express");
const router = express.Router();
const pool = require("../config/db");
const authMiddleware = require("../middlewares/authMiddleware");

// Get all requests (with filters)
router.get("/", authMiddleware, async (req, res) => {
  try {
    const { trang_thai, loai_yeu_cau, id_nguoi_gui } = req.query;
    const userRole = req.user.vaitro;

    let query = `
      SELECT 
        yc.*,
        nd.name as ten_nguoi_gui,
        nd.cccd as cccd_nguoi_gui,
        duyet.name as ten_nguoi_duyet
      FROM yeu_cau yc
      JOIN nguoidung nd ON yc.id_nguoi_gui = nd.id
      LEFT JOIN nguoidung duyet ON yc.nguoi_duyet = duyet.id
      WHERE 1=1
    `;

    const params = [];
    let paramCount = 1;

    // If resident, only show their own requests
    if (userRole === 'NguoiDan') {
      query += ` AND yc.id_nguoi_gui = $${paramCount}`;
      params.push(req.user.id);
      paramCount++;
    }

    if (trang_thai) {
      query += ` AND yc.trang_thai = $${paramCount}`;
      params.push(trang_thai);
      paramCount++;
    }

    if (loai_yeu_cau) {
      query += ` AND yc.loai_yeu_cau = $${paramCount}`;
      params.push(loai_yeu_cau);
      paramCount++;
    }

    if (id_nguoi_gui) {
      query += ` AND yc.id_nguoi_gui = $${paramCount}`;
      params.push(id_nguoi_gui);
      paramCount++;
    }

    query += ` ORDER BY 
      CASE yc.trang_thai 
        WHEN 'Chờ duyệt' THEN 1
        WHEN 'Đã duyệt' THEN 2
        WHEN 'Từ chối' THEN 3
      END,
      yc.created_at DESC
    `;

    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (error) {
    console.error("Error fetching requests:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get request by ID
router.get("/:id", authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pool.query(`
      SELECT 
        yc.*,
        nd.name as ten_nguoi_gui,
        nd.cccd as cccd_nguoi_gui,
        nd.sdt as sdt_nguoi_gui,
        duyet.name as ten_nguoi_duyet
      FROM yeu_cau yc
      JOIN nguoidung nd ON yc.id_nguoi_gui = nd.id
      LEFT JOIN nguoidung duyet ON yc.nguoi_duyet = duyet.id
      WHERE yc.id = $1
    `, [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy yêu cầu" });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error("Error fetching request:", error);
    res.status(500).json({ error: error.message });
  }
});

// Create new request (from resident)
router.post("/", authMiddleware, async (req, res) => {
  try {
    const { loai_yeu_cau, noi_dung } = req.body;
    const id_nguoi_gui = req.user.id;

    const result = await pool.query(`
      INSERT INTO yeu_cau (loai_yeu_cau, id_nguoi_gui, noi_dung, trang_thai, ngay_gui)
      VALUES ($1, $2, $3, 'Chờ duyệt', CURRENT_DATE)
      RETURNING *
    `, [loai_yeu_cau, id_nguoi_gui, JSON.stringify(noi_dung)]);

    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error("Error creating request:", error);
    res.status(500).json({ error: error.message });
  }
});

// Approve request
router.post("/:id/duyet", authMiddleware, async (req, res) => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const { id } = req.params;
    const nguoi_duyet = req.user.id;

    // Get request details
    const requestResult = await client.query('SELECT * FROM yeu_cau WHERE id = $1', [id]);
    if (requestResult.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy yêu cầu" });
    }

    const request = requestResult.rows[0];
    if (request.trang_thai !== 'Chờ duyệt') {
      return res.status(400).json({ message: "Yêu cầu đã được xử lý" });
    }

    const noiDung = request.noi_dung;
    const loaiYeuCau = request.loai_yeu_cau;

    // Process based on request type
    switch (loaiYeuCau) {
      case 'tam_vang':
        // Create temporary absence
        await client.query(`
          INSERT INTO tam_vang (id_nhan_khau, ma_giay_tam_vang, noi_den, tu_ngay, den_ngay, ly_do, trang_thai)
          VALUES ($1, $2, $3, $4, $5, $6, 'Đang hiệu lực')
        `, [
          noiDung.id_nhan_khau,
          noiDung.ma_giay_tam_vang,
          noiDung.noi_den,
          noiDung.tu_ngay,
          noiDung.den_ngay,
          noiDung.ly_do
        ]);

        // Log change
        const nhanKhauTV = await client.query('SELECT ho_ten, id_ho_khau FROM nhan_khau WHERE id = $1', [noiDung.id_nhan_khau]);
        await client.query(`
          INSERT INTO lich_su_bien_dong (id_ho_khau, id_nhan_khau, loai_thay_doi, noi_dung, nguoi_thuc_hien)
          VALUES ($1, $2, 'Tạm vắng', $3, $4)
        `, [
          nhanKhauTV.rows[0].id_ho_khau,
          noiDung.id_nhan_khau,
          `${nhanKhauTV.rows[0].ho_ten} tạm vắng đến ${noiDung.noi_den}`,
          req.user.name
        ]);
        break;

      case 'tam_tru':
        // Create citizen and temporary residence
        const citizenResult = await client.query(`
          INSERT INTO nhan_khau (
            ma_nhan_khau, ho_ten, ngay_sinh, gioi_tinh, noi_sinh, nguyen_quan,
            dan_toc, ton_giao, quoc_tich, ghi_chu
          )
          VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'Tạm trú')
          RETURNING *
        `, [
          noiDung.ma_nhan_khau || `TT${Date.now()}`,
          noiDung.ho_ten,
          noiDung.ngay_sinh,
          noiDung.gioi_tinh,
          noiDung.noi_sinh,
          noiDung.nguyen_quan,
          noiDung.dan_toc,
          noiDung.ton_giao,
          noiDung.quoc_tich
        ]);

        if (noiDung.so_cmt) {
          await client.query(`
            INSERT INTO chung_minh_thu (id_nhan_khau, so_cmt, ngay_cap, noi_cap)
            VALUES ($1, $2, $3, $4)
          `, [citizenResult.rows[0].id, noiDung.so_cmt, noiDung.ngay_cap, noiDung.noi_cap]);
        }

        await client.query(`
          INSERT INTO tam_tru (id_nhan_khau, ma_giay_tam_tru, so_dien_thoai, tu_ngay, den_ngay, ly_do, trang_thai)
          VALUES ($1, $2, $3, $4, $5, $6, 'Đang hiệu lực')
        `, [
          citizenResult.rows[0].id,
          noiDung.ma_giay_tam_tru,
          noiDung.so_dien_thoai,
          noiDung.tu_ngay,
          noiDung.den_ngay,
          noiDung.ly_do
        ]);
        break;

      case 'tach_ho':
        // Create new household
        const newHoKhau = await client.query(`
          INSERT INTO ho_khau (ma_ho_khau, so_nha, duong_pho, phuong_xa, quan_huyen, id_chu_ho, ngay_tao, trang_thai)
          VALUES ($1, $2, $3, $4, $5, $6, CURRENT_DATE, 'Thường trú')
          RETURNING *
        `, [
          noiDung.ma_ho_khau_moi,
          noiDung.so_nha,
          noiDung.duong_pho,
          noiDung.phuong_xa,
          noiDung.quan_huyen,
          noiDung.id_chu_ho_moi
        ]);

        // Move members to new household
        for (const memberId of noiDung.danh_sach_thanh_vien) {
          await client.query(`
            UPDATE nhan_khau
            SET id_ho_khau = $1
            WHERE id = $2
          `, [newHoKhau.rows[0].id, memberId]);
        }

        // Update relation for new head
        await client.query(`
          UPDATE nhan_khau
          SET quan_he_voi_chu_ho = 'Chủ hộ'
          WHERE id = $1
        `, [noiDung.id_chu_ho_moi]);

        // Log changes
        await client.query(`
          INSERT INTO lich_su_bien_dong (id_ho_khau, loai_thay_doi, noi_dung, nguoi_thuc_hien)
          VALUES ($1, 'Tách hộ', $2, $3)
        `, [noiDung.id_ho_khau_cu, `Tách ra hộ mới ${noiDung.ma_ho_khau_moi}`, req.user.name]);
        break;

      case 'sinh_con':
        // Add new citizen
        const newCitizenResult = await client.query(`
          INSERT INTO nhan_khau (
            ma_nhan_khau, ho_ten, ngay_sinh, gioi_tinh, noi_sinh, nguyen_quan,
            dan_toc, ton_giao, quoc_tich, id_ho_khau, quan_he_voi_chu_ho, ngay_dk_thuong_tru, ghi_chu
          )
          VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, CURRENT_DATE, 'Mới sinh')
          RETURNING *
        `, [
          noiDung.ma_nhan_khau,
          noiDung.ho_ten,
          noiDung.ngay_sinh,
          noiDung.gioi_tinh,
          noiDung.noi_sinh,
          noiDung.nguyen_quan,
          noiDung.dan_toc,
          noiDung.ton_giao,
          noiDung.quoc_tich,
          noiDung.id_ho_khau,
          noiDung.quan_he_voi_chu_ho
        ]);

        await client.query(`
          INSERT INTO lich_su_bien_dong (id_ho_khau, id_nhan_khau, loai_thay_doi, noi_dung, nguoi_thuc_hien)
          VALUES ($1, $2, 'Sinh con', $3, $4)
        `, [noiDung.id_ho_khau, newCitizenResult.rows[0].id, `Sinh con ${noiDung.ho_ten}`, req.user.name]);
        break;

      case 'tu_vong':
        // Mark citizen as deceased
        await client.query(`
          UPDATE nhan_khau
          SET ghi_chu = $1
          WHERE id = $2
        `, [`Đã qua đời ngày ${noiDung.ngay_mat}. ${noiDung.ly_do || ''}`, noiDung.id_nhan_khau]);

        const nhanKhauTuVong = await client.query('SELECT ho_ten, id_ho_khau FROM nhan_khau WHERE id = $1', [noiDung.id_nhan_khau]);
        await client.query(`
          INSERT INTO lich_su_bien_dong (id_ho_khau, id_nhan_khau, loai_thay_doi, noi_dung, nguoi_thuc_hien)
          VALUES ($1, $2, 'Qua đời', $3, $4)
        `, [nhanKhauTuVong.rows[0].id_ho_khau, noiDung.id_nhan_khau, `${nhanKhauTuVong.rows[0].ho_ten} qua đời`, req.user.name]);
        break;

      case 'sua_thong_tin':
        // Update citizen information
        await client.query(`
          UPDATE nhan_khau
          SET ho_ten = $1, ngay_sinh = $2, gioi_tinh = $3, noi_sinh = $4,
              nguyen_quan = $5, dan_toc = $6, ton_giao = $7, quoc_tich = $8,
              nghe_nghiep = $9, noi_lam_viec = $10, quan_he_voi_chu_ho = $11
          WHERE id = $12
        `, [
          noiDung.ho_ten, noiDung.ngay_sinh, noiDung.gioi_tinh, noiDung.noi_sinh,
          noiDung.nguyen_quan, noiDung.dan_toc, noiDung.ton_giao, noiDung.quoc_tich,
          noiDung.nghe_nghiep, noiDung.noi_lam_viec, noiDung.quan_he_voi_chu_ho,
          noiDung.id_nhan_khau
        ]);

        if (noiDung.so_cmt) {
          const existingCMT = await client.query('SELECT id FROM chung_minh_thu WHERE id_nhan_khau = $1', [noiDung.id_nhan_khau]);
          if (existingCMT.rows.length > 0) {
            await client.query(`
              UPDATE chung_minh_thu
              SET so_cmt = $1, ngay_cap = $2, noi_cap = $3
              WHERE id_nhan_khau = $4
            `, [noiDung.so_cmt, noiDung.ngay_cap, noiDung.noi_cap, noiDung.id_nhan_khau]);
          } else {
            await client.query(`
              INSERT INTO chung_minh_thu (id_nhan_khau, so_cmt, ngay_cap, noi_cap)
              VALUES ($1, $2, $3, $4)
            `, [noiDung.id_nhan_khau, noiDung.so_cmt, noiDung.ngay_cap, noiDung.noi_cap]);
          }
        }
        break;

      default:
        return res.status(400).json({ message: "Loại yêu cầu không hợp lệ" });
    }

    // Update request status
    await client.query(`
      UPDATE yeu_cau
      SET trang_thai = 'Đã duyệt', nguoi_duyet = $1, ngay_xu_ly = CURRENT_DATE
      WHERE id = $2
    `, [nguoi_duyet, id]);

    await client.query('COMMIT');
    res.json({ message: "Duyệt yêu cầu thành công" });
  } catch (error) {
    await client.query('ROLLBACK');
    console.error("Error approving request:", error);
    res.status(500).json({ error: error.message });
  } finally {
    client.release();
  }
});

// Reject request
router.post("/:id/tu-choi", authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const { ly_do_tu_choi } = req.body;
    const nguoi_duyet = req.user.id;

    if (!ly_do_tu_choi) {
      return res.status(400).json({ message: "Vui lòng nhập lý do từ chối" });
    }

    const result = await pool.query(`
      UPDATE yeu_cau
      SET trang_thai = 'Từ chối', nguoi_duyet = $1, ngay_xu_ly = CURRENT_DATE, ly_do_tu_choi = $2
      WHERE id = $3 AND trang_thai = 'Chờ duyệt'
      RETURNING *
    `, [nguoi_duyet, ly_do_tu_choi, id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy yêu cầu hoặc yêu cầu đã được xử lý" });
    }

    res.json({ message: "Đã từ chối yêu cầu", request: result.rows[0] });
  } catch (error) {
    console.error("Error rejecting request:", error);
    res.status(500).json({ error: error.message });
  }
});

// Delete request (only pending requests by owner)
router.delete("/:id", authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    const result = await pool.query(`
      DELETE FROM yeu_cau
      WHERE id = $1 AND id_nguoi_gui = $2 AND trang_thai = 'Chờ duyệt'
      RETURNING *
    `, [id, userId]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Không tìm thấy yêu cầu hoặc không có quyền xóa" });
    }

    res.json({ message: "Xóa yêu cầu thành công" });
  } catch (error) {
    console.error("Error deleting request:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get pending requests count (for admin dashboard)
router.get("/thong-ke/cho-duyet", authMiddleware, async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT COUNT(*) as count
      FROM yeu_cau
      WHERE trang_thai = 'Chờ duyệt'
    `);

    res.json({ count: parseInt(result.rows[0].count) });
  } catch (error) {
    console.error("Error fetching pending count:", error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
