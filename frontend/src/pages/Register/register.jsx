import React, { useState } from "react";
import InputField from "../../components/InputField";
import Button from "../../components/button";
import { registerUser } from "../../services/register";
import "./register.css";

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    CCCD: "",
    Name: "",
    SDT: "",
    NgaySinh: "",
    GioiTinh: "",
    DanToc: "",
    VaiTro: "NguoiDan",
    User_Name: "",
    MatKhau: "",
  });
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await registerUser(formData);
      if (res.success) {
        setMessage("Đăng ký thành công! Hãy đăng nhập.");
      } else {
        setMessage(res.message || "Đăng ký thất bại!");
      }
    } catch (err) {
      setMessage("Lỗi kết nối tới server");
    }
  };

  return (
    <div className="register-container">
      <form onSubmit={handleSubmit} className="register-form">
        <h2>Đăng ký tài khoản</h2>
        <InputField name="CCCD" placeholder="CCCD" value={formData.CCCD} onChange={handleChange} />
        <InputField name="Name" placeholder="Họ và tên" value={formData.Name} onChange={handleChange} />
        <InputField name="SDT" placeholder="Số điện thoại" value={formData.SDT} onChange={handleChange} />
        <InputField name="NgaySinh" type="date" value={formData.NgaySinh} onChange={handleChange} />
        <InputField name="GioiTinh" placeholder="Giới tính" value={formData.GioiTinh} onChange={handleChange} />
        <InputField name="DanToc" placeholder="Dân tộc" value={formData.DanToc} onChange={handleChange} />
        <InputField name="User_Name" placeholder="Tên đăng nhập" value={formData.User_Name} onChange={handleChange} />
        <InputField name="MatKhau" type="password" placeholder="Mật khẩu" value={formData.MatKhau} onChange={handleChange} />
        <Button text="Đăng ký" type="submit" />
        {message && <p className="message">{message}</p>}
      </form>
    </div>
  );
}
