import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../../components/Navbar";
import "./AdminDashboard.css";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [pendingRequests, setPendingRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    // if (!token || user.vaitro !== "CanBo") {
    //   navigate("/login");
    //   return;
    // }

    // Fetch dashboard statistics
    Promise.all([
      fetch("http://localhost:5000/api/thong-ke/tong-quan", {
        headers: { Authorization: `Bearer ${token}` },
      }).then((res) => res.json()),
      fetch("http://localhost:5000/api/yeu-cau?trang_thai=Chờ duyệt", {
        headers: { Authorization: `Bearer ${token}` },
      }).then((res) => res.json()),
    ])
      .then(([statsData, requestsData]) => {
        setStats(statsData);
        setPendingRequests(requestsData.slice(0, 5));
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [navigate]);

  if (loading) {
    return (
      <div className="admin-dashboard">
        <Navbar />
        <div className="loading">Đang tải...</div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <Navbar />
      
      <div className="admin-content">
        <div className="admin-header">
          <h1>Bảng điều khiển quản trị</h1>
          <p className="subtitle">Tổng quan hệ thống quản lý hộ khẩu</p>
        </div>

        {/* Statistics Cards */}
        <div className="stats-grid">
          <div className="stat-card primary">
            <div className="stat-icon">🏠</div>
            <div className="stat-details">
              <h3>{stats?.tong_ho_khau || 0}</h3>
              <p>Tổng số hộ khẩu</p>
            </div>
          </div>

          <div className="stat-card success">
            <div className="stat-icon">👥</div>
            <div className="stat-details">
              <h3>{stats?.tong_nhan_khau || 0}</h3>
              <p>Tổng số nhân khẩu</p>
            </div>
          </div>

          <div className="stat-card warning">
            <div className="stat-icon">⏳</div>
            <div className="stat-details">
              <h3>{stats?.yeu_cau_cho_duyet || 0}</h3>
              <p>Yêu cầu chờ duyệt</p>
            </div>
          </div>

          <div className="stat-card info">
            <div className="stat-icon">📄</div>
            <div className="stat-details">
              <h3>{stats?.tam_vang_hieu_luc || 0}</h3>
              <p>Giấy tạm vắng hiệu lực</p>
            </div>
          </div>

          <div className="stat-card secondary">
            <div className="stat-icon">🏘️</div>
            <div className="stat-details">
              <h3>{stats?.tam_tru_hieu_luc || 0}</h3>
              <p>Giấy tạm trú hiệu lực</p>
            </div>
          </div>
        </div>

        {/* Pending Requests Section */}
        {pendingRequests.length > 0 && (
          <div className="pending-section">
            <div className="section-header">
              <h2>🔔 Yêu cầu cần xử lý</h2>
              <button 
                className="view-all-link"
                onClick={() => navigate("/admin/yeu-cau")}
              >
                Xem tất cả →
              </button>
            </div>
            <div className="pending-list">
              {pendingRequests.map((req) => (
                <div 
                  key={req.id} 
                  className="pending-item"
                  onClick={() => navigate(`/admin/yeu-cau/${req.id}`)}
                >
                  <div className="pending-icon">
                    {getRequestIcon(req.loai_yeu_cau)}
                  </div>
                  <div className="pending-details">
                    <h4>{req.ten_nguoi_gui}</h4>
                    <p>{getRequestTypeLabel(req.loai_yeu_cau)}</p>
                    <span className="time-ago">{getTimeAgo(req.created_at)}</span>
                  </div>
                  <div className="pending-action">
                    <button className="btn-primary-small">Xem chi tiết</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Charts Section */}
        <div className="charts-section">
          <div className="chart-card">
            <h3>Phân bố theo giới tính</h3>
            <div className="chart-content">
              {stats?.phan_bo_gioi_tinh?.map((item) => (
                <div key={item.gioi_tinh} className="chart-bar">
                  <span className="bar-label">{item.gioi_tinh}</span>
                  <div className="bar-container">
                    <div 
                      className="bar-fill"
                      style={{ 
                        width: `${(item.count / stats.tong_nhan_khau) * 100}%`,
                        background: item.gioi_tinh === 'Nam' ? '#667eea' : '#f093fb'
                      }}
                    ></div>
                  </div>
                  <span className="bar-value">{item.count}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="chart-card">
            <h3>Phân bố theo độ tuổi</h3>
            <div className="chart-content">
              {stats?.phan_bo_do_tuoi?.map((item, index) => (
                <div key={index} className="chart-bar">
                  <span className="bar-label">{item.nhom_tuoi}</span>
                  <div className="bar-container">
                    <div 
                      className="bar-fill"
                      style={{ 
                        width: `${(item.count / stats.tong_nhan_khau) * 100}%`,
                        background: `hsl(${index * 60}, 70%, 60%)`
                      }}
                    ></div>
                  </div>
                  <span className="bar-value">{item.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Links */}
        <div className="quick-links-section">
          <h2>Quản lý</h2>
          <div className="quick-links-grid">
            <div className="quick-link-card" onClick={() => navigate("/admin/ho-khau")}>
              <div className="link-icon">🏠</div>
              <h3>Quản lý hộ khẩu</h3>
            </div>
            <div className="quick-link-card" onClick={() => navigate("/admin/nhan-khau")}>
              <div className="link-icon">👤</div>
              <h3>Quản lý nhân khẩu</h3>
            </div>
            <div className="quick-link-card" onClick={() => navigate("/admin/tam-vang")}>
              <div className="link-icon">📄</div>
              <h3>Quản lý tạm vắng</h3>
            </div>
            <div className="quick-link-card" onClick={() => navigate("/admin/tam-tru")}>
              <div className="link-icon">🏘️</div>
              <h3>Quản lý tạm trú</h3>
            </div>
            <div className="quick-link-card" onClick={() => navigate("/admin/thong-ke")}>
              <div className="link-icon">📊</div>
              <h3>Thống kê báo cáo</h3>
            </div>
            <div className="quick-link-card" onClick={() => navigate("/admin/lich-su")}>
              <div className="link-icon">📜</div>
              <h3>Lịch sử biến động</h3>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function getRequestTypeLabel(type) {
  const labels = {
    tam_vang: "Đăng ký tạm vắng",
    tam_tru: "Đăng ký tạm trú",
    tach_ho: "Yêu cầu tách hộ",
    sinh_con: "Khai sinh",
    tu_vong: "Khai tử",
    sua_thong_tin: "Sửa thông tin nhân khẩu"
  };
  return labels[type] || type;
}

function getRequestIcon(type) {
  const icons = {
    tam_vang: "📄",
    tam_tru: "🏘️",
    tach_ho: "✂️",
    sinh_con: "👶",
    tu_vong: "🕯️",
    sua_thong_tin: "✏️"
  };
  return icons[type] || "📋";
}

function getTimeAgo(timestamp) {
  const now = new Date();
  const created = new Date(timestamp);
  const diff = Math.floor((now - created) / 1000); // seconds

  if (diff < 60) return "Vừa xong";
  if (diff < 3600) return `${Math.floor(diff / 60)} phút trước`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} giờ trước`;
  return `${Math.floor(diff / 86400)} ngày trước`;
}
