import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./profile.css";
import Navbar from "../../components/Navbar";

export default function ProfilePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      navigate("/home"); 
      return;
    }

    fetch("http://localhost:5000/api/profile", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
      })
      .then((json) => {
        setData(json);
        setLoading(false);
      })
      .catch(() => {
        // localStorage.removeItem("token");
        navigate("/home");
      });
  }, []);
  const formatDate = (date) => {
  if (!date) return "";
  return new Date(date).toLocaleDateString("vi-VN");
};

  if (loading) return <p>Đang tải dữ liệu...</p>;
  if (!data) return <p>Không có dữ liệu</p>;

  return (
  <div className="profile-container">
    <Navbar />
    <h1 className="profile-title">Hồ sơ cá nhân</h1>
    <div className="profile-card profile-top">
    <img
    src={`http://localhost:5000/uploads/avatar/${data.avatar || "default.png"}`|| "/default.png"}
    className="profile-avatar"
  />
  </div>
    <div className="profile-card">
      <h2 className="section-title">Thông tin cá nhân</h2>
      <div className="info-grid">
        <p><span>CCCD:</span> {data.cccd}</p>
        <p><span>Họ tên:</span> {data.name}</p>
        <p><span>Ngày sinh:</span> {formatDate(data.ngaysinh)}</p>
        <p><span>Giới tính:</span> {data.gioitinh}</p>
        <p><span>Dân tộc:</span> {data.dantoc}</p>
        <p><span>SĐT:</span> {data.sdt}</p>
      </div>
    </div>

    {data.ho_khau && (
      <div className="profile-card">
        <h2 className="section-title">Hộ khẩu</h2>
        <p><span>Mã hộ khẩu:</span> {data.ho_khau.ma_ho_khau}</p>
        <p><span>Quan hệ chủ hộ:</span> {data.ho_khau.quan_he}</p>
      </div>
    )}

    {data.dia_chi?.length > 0 && (
      <div className="profile-card">
        <h2 className="section-title">Địa chỉ</h2>
        {data.dia_chi.map((dc, i) => (
          <div key={i} className="address-item">
            <p className="address-type">{dc.loai_dia_chi}</p>
            <p className="address-desc">{dc.mo_ta}</p>
          </div>
        ))}
      </div>
    )}
  </div>
);
}
