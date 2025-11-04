import React from "react";
import Navbar from "../../components/Navbar";
import "./HomePage.css";

export default function HomePage() {
  return (
    <div className="home-page">
      <Navbar />
      <div className="home-content">
        <h1>Chào mừng bạn đến với Hệ thống phản ánh</h1>
        <p>Chọn một mục trong thanh điều hướng để bắt đầu.</p>
      </div>
    </div>
  );
}
