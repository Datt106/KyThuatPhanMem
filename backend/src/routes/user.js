const express = require("express");
const router = express.Router();
const pool = require("../config/db"); // Đảm bảo đường dẫn này đúng

router.get("/", async (req, res) => {
  try {
    console.log("Received GET request for /api/users (all)");
    const result = await pool.query("SELECT * FROM nguoidung");
    res.json(result.rows);
  } catch (error) {
    console.error("Error fetching all users:", error);
    res.status(500).json({ error: error.message });
  }
});

router.get("/:cccd", async (req, res) => {
  try {
    const { cccd } = req.params;
    console.log(`Received GET request for /api/users/${cccd}`);
    const result = await pool.query("SELECT * FROM nguoidung WHERE cccd = $1", [cccd]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "User not found" });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error(`Error fetching user with CCCD ${cccd}:`, error);
    res.status(500).json({ error: error.message });
  }
});

router.post("/", async (req, res) => {
  try {
    const { 
        cccd, 
        name, 
        sdt, 
        ngaysinh, 
        gioitinh, 
        dantoc, 
        vaitro, 
        user_name, 
        matkhau, 
        baomatthongtin 
    } = req.body;
    if (!cccd || !name || !sdt || !user_name || !matkhau) {
      return res.status(400).json({ message: "CCCD, Tên, Số điện thoại, User Name và Mật khẩu là bắt buộc." });
    }

    console.log("Received POST request for /api/users to create new user:", req.body);
    
    // Câu lệnh INSERT INTO
    const result = await pool.query(
      `INSERT INTO nguoidung (cccd, name, sdt, ngaysinh, gioitinh, dantoc, vaitro, user_name, matkhau, baomatthongtin) 
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) 
       RETURNING *`,
      [cccd, name, sdt, ngaysinh, gioitinh, dantoc, vaitro, user_name, matkhau, baomatthongtin]
    );

    res.status(201).json(result.rows[0]); // Trả về người dùng mới được tạo với status 201 (Created)
  } catch (error) {
    console.error("Error creating new user:", error);
    if (error.code === '23505') { 
        if (error.constraint === 'nguoidung_cccd_key') { // Giả sử constraint name của cccd
            return res.status(409).json({ message: "CCCD đã tồn tại." });
        }
        if (error.constraint === 'nguoidung_user_name_key') { // Giả sử constraint name của user_name
            return res.status(409).json({ message: "User Name đã tồn tại." });
        }
    }
    res.status(500).json({ error: error.message });
  }
});

// --- API PUT (Cập nhật người dùng hiện có theo CCCD) ---
router.put("/:cccd", async (req, res) => {
  try {
    const { cccd: cccd_param } = req.params; // Lấy cccd từ URL
    // Lấy các trường từ request body (chỉ những trường muốn cập nhật)
    const { 
        name, 
        sdt, 
        ngaysinh, 
        gioitinh, 
        dantoc, 
        vaitro, 
        user_name, 
        matkhau, 
        baomatthongtin 
    } = req.body;

    console.log(`Received PUT request for /api/users/${cccd_param} to update user:`, req.body);

    // Xây dựng câu lệnh SQL cập nhật động
    let query = "UPDATE nguoidung SET ";
    const values = [];
    const setClauses = [];
    let paramIndex = 1;
    if (name !== undefined) {
      setClauses.push(`name = $${paramIndex++}`);
      values.push(name);
    }
    if (sdt !== undefined) {
      setClauses.push(`sdt = $${paramIndex++}`);
      values.push(sdt);
    }
    if (ngaysinh !== undefined) {
      setClauses.push(`ngaysinh = $${paramIndex++}`);
      values.push(ngaysinh);
    }
    if (gioitinh !== undefined) {
      setClauses.push(`gioitinh = $${paramIndex++}`);
      values.push(gioitinh);
    }
    if (dantoc !== undefined) {
      setClauses.push(`dantoc = $${paramIndex++}`);
      values.push(dantoc);
    }
    if (vaitro !== undefined) {
      setClauses.push(`vaitro = $${paramIndex++}`);
      values.push(vaitro);
    }
    if (user_name !== undefined) {
      setClauses.push(`user_name = $${paramIndex++}`);
      values.push(user_name);
    }
    if (matkhau !== undefined) {
      setClauses.push(`matkhau = $${paramIndex++}`);
      values.push(matkhau);
    }
    if (baomatthongtin !== undefined) {
      setClauses.push(`baomatthongtin = $${paramIndex++}`);
      values.push(baomatthongtin);
    }

    if (setClauses.length === 0) {
      return res.status(400).json({ message: "Không có dữ liệu để cập nhật." });
    }

    query += setClauses.join(", ") + ` WHERE cccd = $${paramIndex++} RETURNING *`;
    values.push(cccd_param); // CCCD từ URL để xác định người dùng cần cập nhật

    const result = await pool.query(query, values);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "User not found" });
    }

    res.json(result.rows[0]); // Trả về người dùng đã được cập nhật
  } catch (error) {
    console.error(`Error updating user with CCCD ${cccd_param}:`, error);
    // Xử lý lỗi trùng lặp khi cập nhật (nếu user_name có UNIQUE constraint)
    if (error.code === '23505' && error.constraint === 'nguoidung_user_name_key') {
        return res.status(409).json({ message: "User Name đã tồn tại." });
    }
    res.status(500).json({ error: error.message });
  }
});

// --- API DELETE (Xóa người dùng theo CCCD) ---
router.delete("/:cccd", async (req, res) => {
  try {
    const { cccd } = req.params;
    console.log(`Received DELETE request for /api/users/${cccd}`);
    const result = await pool.query("DELETE FROM nguoidung WHERE cccd = $1 RETURNING *", [cccd]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "User not found" });
    }

    res.status(204).send(); // Trả về status 204 (No Content) khi xóa thành công
  } catch (error) {
    console.error(`Error deleting user with CCCD ${cccd}:`, error);
    res.status(500).json({ error: error.message });
  }
});


module.exports = router;