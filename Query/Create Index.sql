-- ================================================================
-- 1️ BẢNG NGUOI_DUNG
-- ================================================================
-- Tìm kiếm người dùng theo username hoặc CCCD rất thường xuyên
CREATE INDEX idx_nguoidung_username ON NguoiDung (User_Name);
CREATE INDEX idx_nguoidung_vaitro ON NguoiDung (VaiTro);

-- ================================================================
-- 2️ BẢNG DIA_CHI
-- ================================================================
-- Tra cứu theo tỉnh, xã/phường
CREATE INDEX idx_diachi_tinh ON DiaChi (Tinh);
CREATE INDEX idx_diachi_xaphuong ON DiaChi (XaPhuong);

-- ================================================================
-- 3️ BẢNG DIA_CHI_NGUOI_DUNG
-- ================================================================
-- Lọc theo loại địa chỉ (Cư trú, Tạm trú, Nơi làm việc,…)
CREATE INDEX idx_diachinguoidung_loai ON DiaChiNguoiDung (LoaiDiaChi);
-- Lọc nhanh người theo CCCD hoặc địa chỉ
CREATE INDEX idx_diachinguoidung_cccd ON DiaChiNguoiDung (CCCD);
CREATE INDEX idx_diachinguoidung_madiadi ON DiaChiNguoiDung (MaDiaChi);

-- ================================================================
-- 4️ BẢNG PHAN_ANH
-- ================================================================
-- Các truy vấn phổ biến: theo người gửi, trạng thái, địa chỉ
CREATE INDEX idx_phananh_cccd ON PhanAnh (CCCD);
CREATE INDEX idx_phananh_trangthai ON PhanAnh (TrangThaiPhanAnh);
CREATE INDEX idx_phananh_madiadi ON PhanAnh (MaDiaChi);

-- ================================================================
-- 5️ BẢNG BOX_CHAT
-- ================================================================
CREATE INDEX idx_boxchat_maphananh ON BoxChat (MaPhanAnh);
CREATE INDEX idx_boxchat_canbo ON BoxChat (CCCD_CanBo);
CREATE INDEX idx_boxchat_nguoidan ON BoxChat (CCCD_NguoiDan);

-- ================================================================
-- 6️ BẢNG TIN_NHAN
-- ================================================================
-- Tăng tốc lấy tin nhắn theo box chat và thời gian
CREATE INDEX idx_tinnhan_maboxchat ON TinNhan (MaBoxChat);
CREATE INDEX idx_tinnhan_thoigiangui ON TinNhan (ThoiGianGui);

-- ================================================================
-- 7️ BẢNG HO_KHAU
-- ================================================================
-- Thường dùng để tìm theo địa chỉ hộ khẩu
CREATE INDEX idx_hokhau_madiadi ON HoKhau (MaDiaChi);

-- ================================================================
-- 8️ BẢNG THANH_VIEN_HO_KHAU
-- ================================================================
CREATE INDEX idx_thanhvienhokhau_mahokhau ON ThanhVienHoKhau (MaHoKhau);
CREATE INDEX idx_thanhvienhokhau_cccd ON ThanhVienHoKhau (CCCD);
