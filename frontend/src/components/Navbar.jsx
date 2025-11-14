import React from "react";
import "./Navbar.css";
export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-logo">KHU DÂN PHỐ TỔ</div>
      <ul className="navbar-links">
        <li><a href="/home" className="active">Trang chính</a></li>
        <li><a href="/phan-anh">Phản ánh</a></li>
        <li><a href="/thong-bao">Thông báo</a></li>
        <li><a href="/ho-so">Hồ sơ</a></li>
      </ul>
    </nav>
  );
}
