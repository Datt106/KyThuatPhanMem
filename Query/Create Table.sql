-- ================================================
-- TẠO DATABASE
-- ================================================
CREATE DATABASE "QuanLyPhanAnh";
\c QuanLyPhanAnh;

-- ================================================
-- 1. BẢNG NGUOI_DUNG
-- ================================================
CREATE TABLE NguoiDung (
    CCCD CHAR(12) PRIMARY KEY,
    Name VARCHAR(50),
    SDT VARCHAR(15),
    NgaySinh DATE,
    GioiTinh VARCHAR(10),
    DanToc VARCHAR(30),
    VaiTro VARCHAR(20) CHECK (VaiTro IN ('NguoiDan', 'CanBo')),
    User_Name VARCHAR(50) UNIQUE NOT NULL,
    MatKhau VARCHAR(255) NOT NULL,
    BaoMatThongTin BOOLEAN DEFAULT TRUE  -- Ẩn thông tin cho đến khi cán bộ xử lý
);
COMMENT ON TABLE NguoiDung IS 'Lưu thông tin người dùng (người dân, cán bộ).';
COMMENT ON COLUMN NguoiDung.BaoMatThongTin IS 'Ẩn thông tin người dân cho đến khi cán bộ xử lý phản ánh.';

-- ================================================
-- 2. BẢNG DIA_CHI
-- ================================================
CREATE TABLE DiaChi (
    MaDiaChi SERIAL PRIMARY KEY,
    Tinh VARCHAR(50),
    XaPhuong VARCHAR(50),
    ChiTiet VARCHAR(255)
);
COMMENT ON TABLE DiaChi IS 'Lưu thông tin địa chỉ chung (tỉnh, xã/phường, chi tiết).';

-- ================================================
-- 3. BẢNG DIA_CHI_NGUOI_DUNG
-- ================================================
CREATE TABLE DiaChiNguoiDung (
    MaDiaChi INT REFERENCES DiaChi(MaDiaChi) ON DELETE CASCADE,
    CCCD CHAR(12) REFERENCES NguoiDung(CCCD) ON DELETE CASCADE,
    LoaiDiaChi VARCHAR(20) CHECK (LoaiDiaChi IN ('CuTru', 'TamTru', 'NoiLamViec')),
    ThoiDiemXacNhan DATE,
    ThoiDiemKetThuc DATE,
    PRIMARY KEY (MaDiaChi, CCCD, LoaiDiaChi)
);
COMMENT ON TABLE DiaChiNguoiDung IS 'Xác định loại địa chỉ (cư trú, tạm trú, nơi làm việc) của từng người.';

-- ================================================
-- 4. BẢNG TEP_DINH_KEM
-- ================================================
CREATE TABLE TepDinhKem (
    MaTepDinhKem SERIAL PRIMARY KEY,
    DuongDan TEXT NOT NULL
);
COMMENT ON TABLE TepDinhKem IS 'Lưu đường dẫn đến tệp đính kèm.';

-- ================================================
-- 5. BẢNG PHAN_ANH
-- ================================================
CREATE TABLE PhanAnh (
    MaPhanAnh SERIAL PRIMARY KEY,
    CCCD CHAR(12) REFERENCES NguoiDung(CCCD) ON DELETE SET NULL,
    MaDiaChi INT REFERENCES DiaChi(MaDiaChi),
    LoaiPhanAnh VARCHAR(100),
    TrangThaiPhanAnh VARCHAR(50) DEFAULT 'ChuaXuLy' CHECK (TrangThaiPhanAnh IN ('ChuaXuLy','DangXuLy','DaXuLy')),
    MoTa TEXT,
    MaTepDinhKem INT REFERENCES TepDinhKem(MaTepDinhKem)
);
COMMENT ON TABLE PhanAnh IS 'Lưu thông tin phản ánh của người dân.';

-- ================================================
-- 6. BẢNG BOX_CHAT
-- ================================================
CREATE TABLE BoxChat (
    MaBoxChat SERIAL PRIMARY KEY,
    MaPhanAnh INT UNIQUE REFERENCES PhanAnh(MaPhanAnh) ON DELETE CASCADE,
    CCCD_CanBo CHAR(12) REFERENCES NguoiDung(CCCD) ON DELETE SET NULL,
    CCCD_NguoiDan CHAR(12) REFERENCES NguoiDung(CCCD) ON DELETE SET NULL
);
COMMENT ON TABLE BoxChat IS 'Mỗi phản ánh có 1 box chat riêng giữa người dân và cán bộ.';

-- ================================================
-- 7. BẢNG TIN_NHAN
-- ================================================
CREATE TABLE TinNhan (
    TinNhanID SERIAL PRIMARY KEY,
    MaBoxChat INT REFERENCES BoxChat(MaBoxChat) ON DELETE CASCADE,
    NguoiGui CHAR(12) REFERENCES NguoiDung(CCCD) ON DELETE SET NULL,
    NoiDung TEXT NOT NULL,
    ThoiGianGui TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    DaDoc BOOLEAN DEFAULT FALSE,
    MaTepDinhKem INT REFERENCES TepDinhKem(MaTepDinhKem)
);
COMMENT ON TABLE TinNhan IS 'Lưu tin nhắn giữa người dân và cán bộ trong từng box chat.';

-- ================================================
-- 8. BẢNG HO_KHAU
-- ================================================
CREATE TABLE HoKhau (
    MaHoKhau SERIAL PRIMARY KEY,
    MaDiaChi INT REFERENCES DiaChi(MaDiaChi) ON DELETE SET NULL,
    NgayCap DATE DEFAULT CURRENT_DATE,
    GhiChu TEXT
);
COMMENT ON TABLE HoKhau IS 'Lưu thông tin hộ khẩu, gắn với một địa chỉ cư trú.';
COMMENT ON COLUMN HoKhau.SoHoKhau IS 'Số sổ hộ khẩu duy nhất.';

-- ================================================
-- 9. BẢNG THANH_VIEN_HO_KHAU
-- ================================================
CREATE TABLE ThanhVienHoKhau (
    MaHoKhau INT REFERENCES HoKhau(MaHoKhau) ON DELETE CASCADE,
    CCCD CHAR(12) REFERENCES NguoiDung(CCCD) ON DELETE CASCADE,
    QuanHeChuHo VARCHAR(50) CHECK (
        QuanHeChuHo IN ('ChuHo', 'Vo/Chong', 'Con', 'Cha', 'Me', 'Anh/Chi/Em', 'Khac')
    ),
    NgayBatDau DATE DEFAULT CURRENT_DATE,
    NgayKetThuc DATE,  -- nếu rời hộ thì điền ngày kết thúc
    PRIMARY KEY (MaHoKhau, CCCD)
);
COMMENT ON TABLE ThanhVienHoKhau IS 'Liên kết người dân với hộ khẩu và quan hệ với chủ hộ.';
COMMENT ON COLUMN ThanhVienHoKhau.QuanHeChuHo IS 'Quan hệ của thành viên với chủ hộ.';
