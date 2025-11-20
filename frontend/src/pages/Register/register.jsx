import React, { useState } from "react";
import InputField from "../../components/InputField";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import Button from "../../components/Button";
import { registerUser } from "../../services/authservice";
import "./register.css";
import Select from "react-select"; // dropdown chọn giới tính và dân tộc
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
    cccd: "",
    name: "",
    sdt: "",
    ngaysinh: "",
    gioitinh: null,
    dantoc: null,
    vaitro: "NguoiDan",
    user_name: "",
    matkhau: "",
  });
  const [message, setMessage] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleGenderChange = (selectedOption) => {
    setFormData({ ...formData, gioitinh: selectedOption });
  };

  const handleEthnicChange = (selectedOption) => {
    setFormData({ ...formData, dantoc: selectedOption });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        gioitinh: formData.gioitinh ? formData.gioitinh.value : null,
        dantoc: formData.dantoc ? formData.dantoc.value : null,
      };
      const res = await registerUser(submitData); // Gọi API đăng ký
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
                name="cccd"
                placeholder="Nhập CCCD"
                value={formData.cccd}
                onChange={handleChange}
                className="input-field"
                required
              />
            </div>
            <div className="input-group">
              <label className="input-label">Họ và tên<span className="required">*</span>:</label>
              <input
                type="text"
                name="name"
                placeholder="Nhập họ và tên"
                value={formData.name}
                onChange={handleChange}
                className="input-field"
                required
              />
            </div>
            <div className="input-group">
              <label className="input-label">Ngày sinh<span className="required">*</span>:</label>
              <input
                type="date"
                name="ngaysinh"
                value={formData.ngaysinh}
                onChange={handleChange}
                className="input-field"
              />
            </div>
            <div className="input-group">
              <label className="input-label">Giới tính<span className="required">*</span>:</label>
              <Select
                options={genderOptions}
                value={formData.gioitinh}
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
                name="sdt"
                placeholder="Nhập số điện thoại"
                value={formData.sdt}
                onChange={handleChange}
                className="input-field"
                required
              />
            </div>
            <div className="input-group">
              <label className="input-label">Dân tộc<span className="required">*</span>:</label>
              <Select
                options={ethnicOptions}
                value={formData.dantoc}
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
                name="user_name"
                placeholder="Nhập tên đăng nhập"
                value={formData.user_name}
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
                  name="matkhau"
                  placeholder="Nhập mật khẩu"
                  value={formData.matkhau}
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
