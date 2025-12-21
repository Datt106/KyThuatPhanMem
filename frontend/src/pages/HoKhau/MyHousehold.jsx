import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../../components/Navbar";
import "./HoKhau.css";

export default function MyHousehold() {
  const [household, setHousehold] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    // if (!user) {
    //   navigate("/login");
    //   return;
    // }

    // First get user's household ID
    fetch(`http://localhost:5000/api/thong-ke/nguoi-dan/${user.id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.co_ho_khau && data.ho_khau) {
          // Get full household details
          return fetch(`http://localhost:5000/api/ho-khau/${data.ho_khau.id}`, {
            headers: { Authorization: `Bearer ${token}` },
          });
        } else {
          setLoading(false);
          return null;
        }
      })
      .then((res) => res ? res.json() : null)
      .then((householdData) => {
        setHousehold(householdData);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [navigate]);

  const calculateAge = (birthDate) => {
    if (!birthDate) return "N/A";
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("vi-VN");
  };

  if (loading) {
    return (
      <div className="household-page">
        <Navbar />
        <div className="loading">Đang tải...</div>
      </div>
    );
  }

  if (!household) {
    return (
      <div className="household-page">
        <Navbar />
        <div className="no-data">
          <h2>Chưa có thông tin hộ khẩu</h2>
          <p>Vui lòng liên hệ tổ trưởng để được đăng ký</p>
        </div>
      </div>
    );
  }

  return (
    <div className="household-page">
      <Navbar />
      
      <div className="household-content">
        <div className="household-header">
          <h1>Sổ Hộ Khẩu Điện Tử</h1>
          <button className="btn-back" onClick={() => navigate("/dashboard")}>
            ← Quay lại
          </button>
        </div>

        {/* Household Info Card */}
        <div className="household-info-card">
          <div className="info-header">
            <h2>Thông tin hộ khẩu</h2>
            <span className="status-badge">{household.trang_thai}</span>
          </div>
          <div className="info-grid">
            <div className="info-item">
              <span className="label">Mã hộ khẩu:</span>
              <span className="value">{household.ma_ho_khau}</span>
            </div>
            <div className="info-item">
              <span className="label">Chủ hộ:</span>
              <span className="value">{household.ten_chu_ho}</span>
            </div>
            <div className="info-item">
              <span className="label">Địa chỉ:</span>
              <span className="value">
                {household.so_nha}, {household.duong_pho}, {household.phuong_xa}, {household.quan_huyen}
              </span>
            </div>
            <div className="info-item">
              <span className="label">Ngày lập sổ:</span>
              <span className="value">{formatDate(household.ngay_tao)}</span>
            </div>
          </div>
        </div>

        {/* Members List */}
        <div className="members-section">
          <h2>Thành viên hộ khẩu ({household.thanh_vien?.length || 0} người)</h2>
          
          <div className="members-grid">
            {household.thanh_vien?.map((member) => (
              <div key={member.id} className="member-card">
                <div className="member-avatar">
                  {member.gioi_tinh === 'Nam' ? '👨' : '👩'}
                </div>
                <div className="member-info">
                  <h3>{member.ho_ten}</h3>
                  <p className="relationship">{member.quan_he_voi_chu_ho}</p>
                  
                  <div className="member-details">
                    <div className="detail-row">
                      <span className="detail-label">Ngày sinh:</span>
                      <span className="detail-value">{formatDate(member.ngay_sinh)}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Tuổi:</span>
                      <span className="detail-value">{calculateAge(member.ngay_sinh)} tuổi</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Giới tính:</span>
                      <span className="detail-value">{member.gioi_tinh}</span>
                    </div>
                    {member.so_cmt && (
                      <div className="detail-row">
                        <span className="detail-label">CMND/CCCD:</span>
                        <span className="detail-value">{member.so_cmt}</span>
                      </div>
                    )}
                    <div className="detail-row">
                      <span className="detail-label">Dân tộc:</span>
                      <span className="detail-value">{member.dan_toc || "N/A"}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Nghề nghiệp:</span>
                      <span className="detail-value">{member.nghe_nghiep || "N/A"}</span>
                    </div>
                    {member.ghi_chu && (
                      <div className="detail-row">
                        <span className="detail-label">Ghi chú:</span>
                        <span className="detail-value note">{member.ghi_chu}</span>
                      </div>
                    )}
                  </div>

                  <div className="member-actions">
                    <button 
                      className="btn-view"
                      onClick={() => alert("Chi tiết thành viên (chưa triển khai)")}
                    >
                      Xem chi tiết
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
