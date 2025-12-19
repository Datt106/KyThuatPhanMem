import { useState, useEffect } from "react";
import "./phananh.css";
import Navbar from "../../components/Navbar";

export default function PhanAnhPage() {
  const [showForm, setShowForm] = useState(false);
  const [phanAnhs, setPhanAnhs] = useState([]);
  const [form, setForm] = useState({
    loaiPhanAnh: "",
    maDiaChi: "",
    moTa: "",
    file: null,
  });
  const [filter, setFilter] = useState({
    trangThai: "",
    loaiPhanAnh: "",
    tuNgay: "",
    denNgay: "",
  });

  const user = JSON.parse(localStorage.getItem("user"));
  const CCCD = user?.cccd;

  useEffect(() => {
    if (!CCCD) return;
    fetch("http://localhost:5000/api/phan-anh/me", {
      headers: { cccd: CCCD },
    })
      .then((res) => res.json())
      .then((data) => setPhanAnhs(data))
      .catch((err) => console.error(err));
  }, [CCCD]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("loaiPhanAnh", form.loaiPhanAnh);
    formData.append("maDiaChi", form.maDiaChi);
    formData.append("moTa", form.moTa);
    if (form.file) formData.append("file", form.file);

    await fetch("http://localhost:5000/api/phan-anh", {
      method: "POST",
      body: formData,
      headers: { cccd: CCCD },
    });

    setShowForm(false);
    fetch("http://localhost:5000/api/phan-anh/me", {
      headers: { cccd: CCCD },
    })
      .then((res) => res.json())
      .then((data) => setPhanAnhs(data));
  };

  const filteredPhanAnhs = phanAnhs.filter((pa) => {
    if (filter.trangThai && pa.trangthaiphananh !== filter.trangThai) return false;
    if (filter.loaiPhanAnh && pa.loaiphananh !== filter.loaiPhanAnh) return false;
    const paTime = new Date(pa.thoigian);
    if (filter.tuNgay && paTime < new Date(filter.tuNgay)) return false;
    if (filter.denNgay && paTime > new Date(filter.denNgay)) return false;
    return true;
  });

  return (
    <div className="phananh-container">
      <Navbar />

      <div className="header-row">
        <h1>Phản ánh của tôi</h1>
        <button className="btn-create" onClick={() => setShowForm(!showForm)}>
          + Tạo phản ánh mới
        </button>
      </div>

      {showForm && (
        <form className="phananh-form" onSubmit={handleSubmit}>
          <div className="row">
            <label>
              Loại phản ánh
              <select name="loaiPhanAnh" required onChange={handleChange} defaultValue="">
                <option value="" disabled>Chọn loại phản ánh</option>
                <option value="an_ninh_trat_tu">An ninh, trật tự</option>
                <option value="moi_truong">Môi trường</option>
                <option value="ha_tang_tien_ich">Hạ tầng, tiện ích công cộng</option>
                <option value="quan_ly_hanh_chinh">Quản lý hành chính</option>
                <option value="van_hoa_xa_hoi">Văn hóa – xã hội</option>
                <option value="chinh_sach_phap_luat">Chính sách và pháp luật</option>
              </select>
            </label>

            <label>
              Địa chỉ
              <input type="text" name="maDiaChi" required placeholder="Nhập địa chỉ" onChange={handleChange} />
            </label>
          </div>

          <label>
            Mô tả
            <textarea name="moTa" rows="4" placeholder="Mô tả nội dung phản ánh" onChange={handleChange} />
          </label>

          <label>
            Tệp đính kèm
            <input type="file" onChange={(e) => setForm({ ...form, file: e.target.files[0] })} />
          </label>

          <button type="submit" className="btn-submit">Gửi phản ánh</button>
        </form>
      )}

      {/* Bộ lọc nằm ngang */}
      <div className="phananh-filters" >
        <select value={filter.trangThai} onChange={(e) => setFilter({ ...filter, trangThai: e.target.value })}>
          <option value="">--Trạng thái--</option>
          <option value="ChuaXuLy">Chưa xử lí</option>
          <option value="ChuaXuLy">Đang xử lí</option>
          <option value="DaXuLy">Đã xử lí</option>
        </select>

        <select value={filter.loaiPhanAnh} onChange={(e) => setFilter({ ...filter, loaiPhanAnh: e.target.value })}>
          <option value="">--Loại phản ánh--</option>
          <option value="an_ninh_trat_tu">An ninh, trật tự</option>
          <option value="moi_truong">Môi trường</option>
          <option value="ha_tang_tien_ich">Hạ tầng, tiện ích</option>
          <option value="quan_ly_hanh_chinh">Quản lý hành chính</option>
          <option value="van_hoa_xa_hoi">Văn hóa – xã hội</option>
          <option value="chinh_sach_phap_luat">Chính sách – pháp luật</option>
        </select>

        <input type="date" value={filter.tuNgay} onChange={(e) => setFilter({ ...filter, tuNgay: e.target.value })} />
        <input type="date" value={filter.denNgay} onChange={(e) => setFilter({ ...filter, denNgay: e.target.value })} />
      </div>

      {/* Bảng phản ánh */}
      <div className="phananh-list" >
        <div className="phananh-header" >
          <div>Loại phản ánh</div>
          <div>Mô tả</div>
          <div>Thời gian</div>
          <div>Trạng thái</div>
        </div>

        {filteredPhanAnhs.map((pa) => (
          <div key={pa.maphananh} className="phananh-item" style={{ display: "grid", gridTemplateColumns: "2fr 2.5fr 2fr 1fr", gap: "10px", padding: "10px", borderBottom: "1px solid #eee", alignItems: "center" }}>
            <div>{pa.loaiphananh}</div>
            <div>{pa.mota}</div>
            <div>{new Date(pa.thoigian).toLocaleString()}</div>
            <div className={`status ${pa.trangthaiphananh}`}>
            {pa.trangthaiphananh === "ChuaXuLy"
            ? "Chưa xử lí"
            : pa.trangthaiphananh === "DangXuLy"
            ? "Đang xử lí"
            : "Đã xử lí"}
            </div>

          </div>
        ))}
      </div>
    </div>
  );
}
