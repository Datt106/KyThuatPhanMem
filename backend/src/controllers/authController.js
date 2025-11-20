const pool = require("../config/db");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");

// Hàm đăng ký
exports.register = async (req, res) => {
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
  } = req.body;

  try {
    // kiểm tra user_name hoặc cccd đã tồn tại chưa
    const existingUser = await pool.query(
      "SELECT * FROM nguoidung WHERE user_name = $1 OR cccd = $2",
      [user_name, cccd]
    );

    if (existingUser.rows.length > 0) {
      const exists = existingUser.rows[0];
      if (exists.user_name === user_name) {
        return res.status(400).json({ message: "Tên đăng nhập đã tồn tại" });
      }
      if (exists.cccd === cccd) {
        return res.status(400).json({ message: "CCCD đã tồn tại" });
      }
    }

    // hash mật khẩu
    const hashedPass = await bcrypt.hash(matkhau, 10);

    // insert DB và trả về user vừa tạo
    const allowedRoles = ['NguoiDan', 'CanBo'];
    const vaitroValue = allowedRoles.includes(vaitro) ? vaitro : 'NguoiDan'; // mặc định 'NguoiDan'

    const newUser = await pool.query(
      `INSERT INTO nguoidung 
      (cccd, name, sdt, ngaysinh, gioitinh, dantoc, vaitro, user_name, matkhau, baomatthongtin)
      VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
      RETURNING cccd, name, sdt, ngaysinh, gioitinh, dantoc, vaitro, user_name, baomatthongtin`,
      [
        cccd,
        name,
        sdt,
        ngaysinh,
        gioitinh,
        dantoc,
        vaitroValue,
        user_name,
        hashedPass,
        true
      ]
    );

    res.status(201).json({ message: "Đăng ký thành công", user: newUser.rows[0] });
  } catch (err) {
    console.log(err);
    res.status(500).json({ message: "Đăng ký không thành công" });
  }
};

// Hàm đăng nhập
exports.login = async (req, res) => {
  const { cccd, matkhau } = req.body;

  try {
    // tìm user theo cccd
    const userFind = await pool.query(
      "SELECT * FROM nguoidung WHERE cccd = $1",
      [cccd]
    );

    if (userFind.rows.length === 0) {
      return res.status(400).json({ message: "CCCD không tồn tại" });
    }

    const user = userFind.rows[0];

    // check password
    const isMatch = await bcrypt.compare(matkhau, user.matkhau);
    if (!isMatch) {
      return res.status(400).json({ message: "Sai mật khẩu" });
    }

    // tạo JWT token để trả về  
    const token = jwt.sign(
      {
        cccd: user.cccd,
        vaitro: user.vaitro,
        name: user.name
      },
      process.env.JWT_SECRET,
      { expiresIn: "7d" }
    );

    res.json({
      message: "Đăng nhập thành công",
      token: token,
      user: {
        cccd: user.cccd,
        name: user.name,
        vaitro: user.vaitro,
        sdt: user.sdt,
        gioitinh: user.gioitinh,
        dantoc: user.dantoc
      }
    });

  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Lỗi server" });
  }
};
