-- Bảng lưu đơn đăng ký tài khoản của người dân
-- Workflow: Người dân điền form -> Cán bộ duyệt -> Tạo tài khoản -> Người dân đến lấy mật khẩu

CREATE TABLE IF NOT EXISTS DonDangKy (
    madondangky SERIAL PRIMARY KEY,
    cccd VARCHAR(12) NOT NULL UNIQUE,
    hoten VARCHAR(100) NOT NULL,
    ngaysinh DATE NOT NULL,
    gioitinh VARCHAR(10) NOT NULL,
    sdt VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    
    -- Loại đăng ký
    loaidangky VARCHAR(20) NOT NULL CHECK (loaidangky IN ('TamTru', 'CuTru')),
    
    -- Địa chỉ đăng ký
    tinh VARCHAR(50) NOT NULL,
    xaphuong VARCHAR(50) NOT NULL,
    diachi_chitiet TEXT NOT NULL,
    
    -- Thông tin bổ sung
    quoctich VARCHAR(50) DEFAULT 'Việt Nam',
    dantoc VARCHAR(30),
    
    -- Trạng thái đơn
    trangthai VARCHAR(20) NOT NULL DEFAULT 'ChoDuyet' 
        CHECK (trangthai IN ('ChoDuyet', 'DaDuyet', 'TuChoi')),
    
    -- Thông tin duyệt
    nguoiduyet_cccd VARCHAR(12),
    ngayduyet TIMESTAMP,
    lydotuchoi TEXT,
    
    -- Mật khẩu được tạo khi duyệt
    matkhau_tam VARCHAR(20), -- Mật khẩu tạm để người dân đến lấy
    matkhau_daxacnhan BOOLEAN DEFAULT FALSE, -- Đánh dấu đã giao mật khẩu cho người dân
    nguoixacnhan_cccd VARCHAR(12), -- Cán bộ xác nhận đã giao mật khẩu
    ngayxacnhan TIMESTAMP, -- Ngày giao mật khẩu
    
    -- Metadata
    ngaytao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ghichu TEXT,
    
    -- Foreign key
    CONSTRAINT fk_nguoiduyet FOREIGN KEY (nguoiduyet_cccd) REFERENCES nguoidung(cccd),
    CONSTRAINT fk_nguoixacnhan FOREIGN KEY (nguoixacnhan_cccd) REFERENCES nguoidung(cccd)
);

-- Index để tìm kiếm nhanh
CREATE INDEX idx_dondangky_trangthai ON DonDangKy(trangthai);
CREATE INDEX idx_dondangky_cccd ON DonDangKy(cccd);
CREATE INDEX idx_dondangky_ngaytao ON DonDangKy(ngaytao DESC);

-- Comment
COMMENT ON TABLE DonDangKy IS 'Lưu đơn đăng ký tài khoản của người dân, chờ cán bộ duyệt';
COMMENT ON COLUMN DonDangKy.loaidangky IS 'TamTru: Tạm trú, CuTru: Cư trú thường xuyên';
COMMENT ON COLUMN DonDangKy.trangthai IS 'ChoDuyet: Chờ duyệt, DaDuyet: Đã duyệt, TuChoi: Từ chối';
COMMENT ON COLUMN DonDangKy.matkhau_tam IS 'Mật khẩu tạm thời được tạo khi duyệt, người dân đến lấy';
COMMENT ON COLUMN DonDangKy.matkhau_daxacnhan IS 'TRUE khi cán bộ đã giao mật khẩu cho người dân';
