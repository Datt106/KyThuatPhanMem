import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../../components/Navbar";
import "./dashboard.css";

export default function ResidentDashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    // if (!user) {
    //   navigate("/login");
    //   return;
    // }

    // Fetch dashboard data
    fetch(`http://localhost:5000/api/thong-ke/nguoi-dan/${user.id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
      })
      .then((data) => {
        setDashboardData(data);
        setLoading(false);
      })
      .catch(() => {
        // localStorage.removeItem("token");
        navigate("/login");
      });
  }, [navigate]);

  const handleQuickAction = (action) => {
    navigate(`/${action}`);
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <Navbar />
        <div className="loading">Đang tải...</div>
      </div>
    );
  }

  if (!dashboardData || !dashboardData.co_ho_khau) {
    return (
      <div className="dashboard-container">
        <Navbar />
        <div className="no-household">
          <h2>Chưa có thông tin hộ khẩu</h2>
          <p>Vui lòng liên hệ tổ trưởng để được đăng ký hộ khẩu</p>
        </div>
      </div>
    );
  }

  const { ho_khau, thanh_vien, yeu_cau_gan_day } = dashboardData;

  return (
    <div className="dashboard-container">
      <Navbar />
      
      <div className="dashboard-content">
        <div className="welcome-section">
          <h1>Xin chào, {JSON.parse(localStorage.getItem("user") || "{}").name}</h1>
          <p className="subtitle">Quản lý hộ khẩu của bạn một cách dễ dàng</p>
        </div>

        {/* Household Summary Card */}
        <div className="household-summary-card">
          <div className="card-header">
            <h2>Hộ khẩu của tôi</h2>
            <span className="status-badge">Thường trú</span>
          </div>
          <div className="household-info">
            <div className="info-row">
              <span className="label">Mã hộ khẩu:</span>
              <span className="value">{ho_khau.ma_ho_khau}</span>
            </div>
            <div className="info-row">
              <span className="label">Chủ hộ:</span>
              <span className="value">{ho_khau.ten_chu_ho}</span>
            </div>
            <div className="info-row">
              <span className="label">Địa chỉ:</span>
              <span className="value">
                {ho_khau.so_nha}, {ho_khau.duong_pho}, {ho_khau.phuong_xa}, {ho_khau.quan_huyen}
              </span>
            </div>
            <div className="info-row">
              <span className="label">Số thành viên:</span>
              <span className="value">{ho_khau.so_thanh_vien} người</span>
            </div>
          </div>
          <button 
            className="view-details-btn"
            onClick={() => navigate("/ho-khau-cua-toi")}
          >
            Xem chi tiết →
          </button>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions-section">
          <h2>Dịch vụ</h2>
          <div className="quick-actions-grid">
            <div className="action-card" onClick={() => handleQuickAction("khai-bao-tam-vang")}>
              <div className="action-icon">📄</div>
              <h3>Khai báo tạm vắng</h3>
              <p>Đăng ký khi đi xa dài ngày</p>
            </div>
            
            <div className="action-card" onClick={() => handleQuickAction("khai-bao-tam-tru")}>
              <div className="action-icon">🏠</div>
              <h3>Khai báo tạm trú</h3>
              <p>Đăng ký cho người ở nhờ</p>
            </div>
            
            <div className="action-card" onClick={() => handleQuickAction("yeu-cau-tach-ho")}>
              <div className="action-icon">✂️</div>
              <h3>Yêu cầu tách hộ</h3>
              <p>Tách thành hộ khẩu riêng</p>
            </div>
            
            <div className="action-card" onClick={() => handleQuickAction("khai-bao-sinh")}>
              <div className="action-icon">👶</div>
              <h3>Khai báo sinh</h3>
              <p>Đăng ký thành viên mới</p>
            </div>
          </div>
        </div>

        {/* Recent Requests */}
        {yeu_cau_gan_day && yeu_cau_gan_day.length > 0 && (
          <div className="recent-requests-section">
            <h2>Lịch sử yêu cầu</h2>
            <div className="requests-list">
              {yeu_cau_gan_day.map((req) => (
                <div key={req.id} className="request-item">
                  <div className="request-info">
                    <span className="request-type">{getRequestTypeLabel(req.loai_yeu_cau)}</span>
                    <span className="request-date">{formatDate(req.ngay_gui)}</span>
                  </div>
                  <span className={`request-status status-${req.trang_thai.toLowerCase().replace(' ', '-')}`}>
                    {req.trang_thai}
                  </span>
                </div>
              ))}
            </div>
            <button 
              className="view-all-btn"
              onClick={() => navigate("/yeu-cau-cua-toi")}
            >
              Xem tất cả
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function getRequestTypeLabel(type) {
  const labels = {
    tam_vang: "Tạm vắng",
    tam_tru: "Tạm trú",
    tach_ho: "Tách hộ",
    sinh_con: "Khai sinh",
    tu_vong: "Khai tử",
    sua_thong_tin: "Sửa thông tin"
  };
  return labels[type] || type;
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("vi-VN");
}
