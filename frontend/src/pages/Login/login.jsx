import { useState } from "react";
import InputField from "../components/InputField";
import Button from "../components/button";
import { login } from "../services/authservice";
import { FaLock, FaEye, FaEyeSlash } from "react-icons/fa";
import "./login.css"; 

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await login(email, password);
      if (res.success) {
        window.location.href = "/home";
      } else {
        setError(res.message || "Sai tài khoản hoặc mật khẩu");
      }
    } catch (err) {
      setError("Lỗi kết nối đến server");
    }
  };

  return (
    <div className="login-container">
      <div className="rotating-background">
    <img src="/assets/drum.png" alt="Rotating logo" className="rotating-image" />
    </div>
      <form onSubmit={handleLogin} clasName ="login-form">
        <h2>Đăng nhập</h2>
        <InputField
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <div className="password-wrapper">
          <FaLock className="lock-icon" /> 
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
            {showPassword ? <FaEyeSlash /> : <FaEye />}
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
