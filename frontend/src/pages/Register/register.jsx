import React, { useState } from "react";
import InputField from "../../components/InputField";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import Button from "../../components/Button";
import { registerUser } from "../../services/register";
import "./register.css";
import Select from "react-select";
const genderOptions = [
  { value: "Nam", label: "Nam" },
  { value: "Nữ", label: "Nữ" },
];

const ethnicOptions = [
  { value: "Kinh", label: "Kinh" },
  { value: "Tày", label: "Tày" },
  { value: "Thái", label: "Thái" },
  { value: "Hoa", label: "Hoa" },
  { value: "Khơ-me", label: "Khơ-me" },
];
export default function RegisterPage() {
  const [formData, setFormData] = useState({
    CCCD: "",
    Name: "",
    SDT: "",
    NgaySinh: "",
    GioiTinh: null,
    DanToc: null,
    VaiTro: "NguoiDan",
    User_Name: "",
    MatKhau: "",
  });
  const [message, setMessage] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleGenderChange = (selectedOption) => {
    setFormData({ ...formData, GioiTinh: selectedOption });
  };

  const handleEthnicChange = (selectedOption) => {
    setFormData({ ...formData, DanToc: selectedOption });
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
      <form className="register-form" onSubmit={handleSubmit}>
        <h2>Đăng ký tài khoản</h2>
        <div className="form-columns">
          <div className="column">
            <div className="input-group">
              <label className="input-label">CCCD<span className="required">*</span>:</label>
              <input
                type="text"
                name="CCCD"
                placeholder="Nhập CCCD"
                value={formData.CCCD}
                onChange={handleChange}
                className="input-field"
                required
              />
            </div>
            <div className="input-group">
              <label className="input-label">Họ và tên<span className="required">*</span>:</label>
              <input
                type="text"
                name="Name"
                placeholder="Nhập họ và tên"
                value={formData.Name}
                onChange={handleChange}
                className="input-field"
                required
              />
            </div>
            <div className="input-group">
              <label className="input-label">Ngày sinh<span className="required">*</span>:</label>
              <input
                type="date"
                name="NgaySinh"
                value={formData.NgaySinh}
                onChange={handleChange}
                className="input-field"
              />
            </div>
            <div className="input-group">
              <label className="input-label">Giới tính<span className="required">*</span>:</label>
              <Select
                options={genderOptions}
                value={formData.GioiTinh}
                onChange={handleGenderChange}
                placeholder="Chọn giới tính"
                isClearable
                required
              />
            </div>
          </div>
          <div className="column">
            <div className="input-group">
              <label className="input-label">Số điện thoại<span className="required">*</span>:</label>
              <input
                type="text"
                name="SDT"
                placeholder="Nhập số điện thoại"
                value={formData.SDT}
                onChange={handleChange}
                className="input-field"
                required
              />
            </div>
            <div className="input-group">
              <label className="input-label">Dân tộc<span className="required">*</span>:</label>
              <Select
                options={ethnicOptions}
                value={formData.DanToc}
                onChange={handleEthnicChange}
                placeholder="Chọn dân tộc"
                isClearable
                isSearchable
                required
              />
            </div>
            <div className="input-group">
              <label className="input-label">Tên đăng nhập<span className="required">*</span>:</label>
              <input
                type="text"
                name="User_Name"
                placeholder="Nhập tên đăng nhập"
                value={formData.User_Name}
                onChange={handleChange}
                className="input-field"
                required
              />
            </div>
            <div className="input-group">
              <label className="input-label">Mật khẩu<span className="required">*</span>:</label>
              <div className="password-wrapper">
                <input
                  type={showPassword ? "text" : "password"}
                  name="MatKhau"
                  placeholder="Nhập mật khẩu"
                  value={formData.MatKhau}
                  onChange={handleChange}
                  className="input-field"
                  required
                />
                <span
                  className="toggle-password"
                  onClick={() => setShowPassword(!showPassword)}
                >
                </span>
              </div>
            </div>
          </div>
        </div>

        <Button text="Đăng ký" type="submit" />
        {message && <p className="message">{message}</p>}
      </form>
    </div>
  );
}
