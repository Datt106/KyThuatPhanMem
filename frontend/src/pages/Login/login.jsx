import { useState } from "react";
import InputField from "../../components/InputField";
import Button from "../../components/Button";
import { loginUser } from "../../services/authservice";
import { FaLock, FaEye, FaEyeSlash } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import "./login.css"; // CSS riêng cho trang đăng nhập

export default function LoginPage() {
  const navigate = useNavigate();
  const [cccd, setCccd] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const userdata = {cccd, matkhau: password};
      const res = await loginUser(userdata);
      navigate("/");
    } catch (err) {
      setError("Lỗi kết nối đến server");
    }
  };

  return (
    <div className="login-container">
    <img src="/assets/drum.png" alt="Rotating logo" className="rotating-corner-image" />
      <form onSubmit={handleLogin} className ="login-form">
        <h2>Đăng nhập</h2>
       <div className="input-group">
        <label className="input-label">CCCD</label>
        <input
          type="text"
          placeholder="Nhập CCCD..."
          value={cccd}
          onChange={(e) => setCccd(e.target.value)}
          className="input-field"
          />
        </div>
        <div className="input-group">
        <label className="input-label">Mật Khẩu:</label> 
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Mật khẩu"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="password-input"
          />
          <span
            className="toggle-password"
            onClick={() => setShowPassword(!showPassword)}
          >
          </span>
        </div>
        <Button text="Đăng nhập" type="submit" />
        <p className="register-link">
          Chưa có tài khoản?{" "}
          <a href="/register">Đăng ký ngay</a>
        </p>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
}
