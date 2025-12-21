-- Database Schema for Household Management System
-- PostgreSQL Database

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS lich_su_bien_dong CASCADE;
DROP TABLE IF EXISTS yeu_cau CASCADE;
DROP TABLE IF EXISTS tam_tru CASCADE;
DROP TABLE IF EXISTS tam_vang CASCADE;
DROP TABLE IF EXISTS chung_minh_thu CASCADE;
DROP TABLE IF EXISTS nhan_khau CASCADE;
DROP TABLE IF EXISTS ho_khau CASCADE;

-- Table 1: ho_khau (Household Management)
CREATE TABLE ho_khau (
    id SERIAL PRIMARY KEY,
    ma_ho_khau VARCHAR(50) UNIQUE NOT NULL,
    id_chu_ho INTEGER,  -- Will be FK to nhan_khau, set after nhan_khau is created
    so_nha VARCHAR(100),
    duong_pho VARCHAR(200),
    phuong_xa VARCHAR(200),
    quan_huyen VARCHAR(200),
    ngay_tao DATE DEFAULT CURRENT_DATE,
    trang_thai VARCHAR(50) DEFAULT 'Thường trú',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: nhan_khau (Citizen Management)
CREATE TABLE nhan_khau (
    id SERIAL PRIMARY KEY,
    ma_nhan_khau VARCHAR(50) UNIQUE,
    ho_ten VARCHAR(200) NOT NULL,
    bi_danh VARCHAR(200),
    ngay_sinh DATE,
    gioi_tinh VARCHAR(10),
    noi_sinh VARCHAR(300),
    nguyen_quan VARCHAR(300),
    dan_toc VARCHAR(100),
    ton_giao VARCHAR(100),
    quoc_tich VARCHAR(100) DEFAULT 'Việt Nam',
    nghe_nghiep VARCHAR(200),
    noi_lam_viec VARCHAR(300),
    id_ho_khau INTEGER,
    quan_he_voi_chu_ho VARCHAR(100),
    ngay_dk_thuong_tru DATE,
    dia_chi_truoc_khi_chuyen TEXT,
    ghi_chu TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_ho_khau) REFERENCES ho_khau(id) ON DELETE SET NULL
);

-- Add FK constraint for chu_ho in ho_khau table
ALTER TABLE ho_khau
ADD CONSTRAINT fk_chu_ho
FOREIGN KEY (id_chu_ho) REFERENCES nhan_khau(id) ON DELETE SET NULL;

-- Table 3: chung_minh_thu (ID Card/Citizen ID)
CREATE TABLE chung_minh_thu (
    id SERIAL PRIMARY KEY,
    id_nhan_khau INTEGER NOT NULL,
    so_cmt VARCHAR(50) UNIQUE NOT NULL,
    ngay_cap DATE,
    noi_cap VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_nhan_khau) REFERENCES nhan_khau(id) ON DELETE CASCADE
);

-- Table 4: tam_vang (Temporary Absence)
CREATE TABLE tam_vang (
    id SERIAL PRIMARY KEY,
    id_nhan_khau INTEGER NOT NULL,
    ma_giay_tam_vang VARCHAR(50) UNIQUE,
    noi_den TEXT NOT NULL,
    tu_ngay DATE NOT NULL,
    den_ngay DATE NOT NULL,
    ly_do TEXT,
    trang_thai VARCHAR(50) DEFAULT 'Đang hiệu lực',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_nhan_khau) REFERENCES nhan_khau(id) ON DELETE CASCADE
);

-- Table 5: tam_tru (Temporary Residence)
CREATE TABLE tam_tru (
    id SERIAL PRIMARY KEY,
    id_nhan_khau INTEGER NOT NULL,
    ma_giay_tam_tru VARCHAR(50) UNIQUE,
    so_dien_thoai VARCHAR(20),
    tu_ngay DATE NOT NULL,
    den_ngay DATE NOT NULL,
    ly_do TEXT,
    trang_thai VARCHAR(50) DEFAULT 'Đang hiệu lực',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_nhan_khau) REFERENCES nhan_khau(id) ON DELETE CASCADE
);

-- Table 6: lich_su_bien_dong (Change History)
CREATE TABLE lich_su_bien_dong (
    id SERIAL PRIMARY KEY,
    id_ho_khau INTEGER,
    id_nhan_khau INTEGER,
    loai_thay_doi VARCHAR(100) NOT NULL,
    noi_dung TEXT NOT NULL,
    ngay_thay_doi DATE DEFAULT CURRENT_DATE,
    nguoi_thuc_hien VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_ho_khau) REFERENCES ho_khau(id) ON DELETE SET NULL,
    FOREIGN KEY (id_nhan_khau) REFERENCES nhan_khau(id) ON DELETE SET NULL
);

-- Table 7: Update nguoidung table
-- Check if table exists, if not create it
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'nguoidung') THEN
        CREATE TABLE nguoidung (
            id SERIAL PRIMARY KEY,
            cccd VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(200) NOT NULL,
            sdt VARCHAR(20),
            ngaysinh DATE,
            gioitinh VARCHAR(10),
            dantoc VARCHAR(100),
            vaitro VARCHAR(50) DEFAULT 'NguoiDan',
            user_name VARCHAR(100) UNIQUE NOT NULL,
            matkhau VARCHAR(255) NOT NULL,
            baomatthongtin BOOLEAN DEFAULT true,
            avatar VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    END IF;
END
$$;

-- Add id_nhan_khau to nguoidung if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'nguoidung' AND column_name = 'id_nhan_khau'
    ) THEN
        ALTER TABLE nguoidung ADD COLUMN id_nhan_khau INTEGER;
        ALTER TABLE nguoidung ADD CONSTRAINT fk_nguoidung_nhankhau 
        FOREIGN KEY (id_nhan_khau) REFERENCES nhan_khau(id) ON DELETE SET NULL;
    END IF;
END
$$;

-- Table 8: yeu_cau (Requests for approval workflow)
CREATE TABLE yeu_cau (
    id SERIAL PRIMARY KEY,
    loai_yeu_cau VARCHAR(100) NOT NULL, -- 'tam_vang', 'tam_tru', 'tach_ho', 'sinh_con', 'tu_vong', 'sua_thong_tin'
    id_nguoi_gui INTEGER NOT NULL,
    noi_dung JSONB NOT NULL, -- Store request data as JSON
    trang_thai VARCHAR(50) DEFAULT 'Chờ duyệt', -- 'Chờ duyệt', 'Đã duyệt', 'Từ chối'
    ly_do_tu_choi TEXT,
    nguoi_duyet INTEGER,
    ngay_gui DATE DEFAULT CURRENT_DATE,
    ngay_xu_ly DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_nguoi_gui) REFERENCES nguoidung(id) ON DELETE CASCADE,
    FOREIGN KEY (nguoi_duyet) REFERENCES nguoidung(id) ON DELETE SET NULL
);

-- Create indexes for better performance
CREATE INDEX idx_nhan_khau_ho_khau ON nhan_khau(id_ho_khau);
CREATE INDEX idx_nhan_khau_ngay_sinh ON nhan_khau(ngay_sinh);
CREATE INDEX idx_nhan_khau_gioi_tinh ON nhan_khau(gioi_tinh);
CREATE INDEX idx_tam_vang_nhan_khau ON tam_vang(id_nhan_khau);
CREATE INDEX idx_tam_tru_nhan_khau ON tam_tru(id_nhan_khau);
CREATE INDEX idx_yeu_cau_trang_thai ON yeu_cau(trang_thai);
CREATE INDEX idx_yeu_cau_loai ON yeu_cau(loai_yeu_cau);
CREATE INDEX idx_lich_su_ho_khau ON lich_su_bien_dong(id_ho_khau);
CREATE INDEX idx_lich_su_nhan_khau ON lich_su_bien_dong(id_nhan_khau);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ho_khau_updated_at BEFORE UPDATE ON ho_khau
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_nhan_khau_updated_at BEFORE UPDATE ON nhan_khau
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chung_minh_thu_updated_at BEFORE UPDATE ON chung_minh_thu
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tam_vang_updated_at BEFORE UPDATE ON tam_vang
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tam_tru_updated_at BEFORE UPDATE ON tam_tru
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_nguoidung_updated_at BEFORE UPDATE ON nguoidung
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_yeu_cau_updated_at BEFORE UPDATE ON yeu_cau
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
-- Sample household
INSERT INTO ho_khau (ma_ho_khau, so_nha, duong_pho, phuong_xa, quan_huyen, ngay_tao, trang_thai)
VALUES 
    ('HK001', '123', 'Nguyễn Văn Linh', 'Phường 1', 'Quận 7', '2020-01-15', 'Thường trú'),
    ('HK002', '456', 'Lê Lợi', 'Phường 2', 'Quận 1', '2019-05-20', 'Thường trú');

-- Sample citizens
INSERT INTO nhan_khau (ma_nhan_khau, ho_ten, ngay_sinh, gioi_tinh, noi_sinh, nguyen_quan, dan_toc, ton_giao, quoc_tich, nghe_nghiep, id_ho_khau, quan_he_voi_chu_ho, ngay_dk_thuong_tru)
VALUES 
    ('NK001', 'Nguyễn Văn An', '1980-05-15', 'Nam', 'TP HCM', 'Bình Định', 'Kinh', 'Không', 'Việt Nam', 'Kỹ sư', 1, 'Chủ hộ', '2020-01-15'),
    ('NK002', 'Trần Thị Bình', '1985-08-20', 'Nữ', 'TP HCM', 'Long An', 'Kinh', 'Phật giáo', 'Việt Nam', 'Giáo viên', 1, 'Vợ', '2020-01-15'),
    ('NK003', 'Nguyễn Văn Cường', '2010-03-10', 'Nam', 'TP HCM', 'TP HCM', 'Kinh', 'Không', 'Việt Nam', 'Học sinh', 1, 'Con', '2020-01-15'),
    ('NK004', 'Lê Văn Dũng', '1975-12-01', 'Nam', 'Hà Nội', 'Hà Nội', 'Kinh', 'Công giáo', 'Việt Nam', 'Bác sĩ', 2, 'Chủ hộ', '2019-05-20');

-- Update chu_ho in ho_khau
UPDATE ho_khau SET id_chu_ho = 1 WHERE id = 1;
UPDATE ho_khau SET id_chu_ho = 4 WHERE id = 2;

-- Sample ID cards
INSERT INTO chung_minh_thu (id_nhan_khau, so_cmt, ngay_cap, noi_cap)
VALUES 
    (1, '079080001234', '2015-01-10', 'Công an TP HCM'),
    (2, '079085005678', '2015-01-10', 'Công an TP HCM'),
    (4, '001075009999', '2014-06-15', 'Công an Hà Nội');

-- Sample change history
INSERT INTO lich_su_bien_dong (id_ho_khau, id_nhan_khau, loai_thay_doi, noi_dung, ngay_thay_doi, nguoi_thuc_hien)
VALUES 
    (1, 3, 'Sinh con', 'Bổ sung thành viên Nguyễn Văn Cường vào hộ khẩu', '2010-03-10', 'Tổ trưởng'),
    (1, NULL, 'Thành lập hộ', 'Thành lập hộ khẩu HK001', '2020-01-15', 'Tổ trưởng');

COMMENT ON TABLE ho_khau IS 'Quản lý thông tin sổ hộ khẩu';
COMMENT ON TABLE nhan_khau IS 'Quản lý thông tin nhân khẩu (công dân)';
COMMENT ON TABLE chung_minh_thu IS 'Quản lý giấy tờ tùy thân (CMND/CCCD)';
COMMENT ON TABLE tam_vang IS 'Quản lý giấy tạm vắng';
COMMENT ON TABLE tam_tru IS 'Quản lý giấy tạm trú';
COMMENT ON TABLE lich_su_bien_dong IS 'Lịch sử thay đổi của hộ khẩu và nhân khẩu';
COMMENT ON TABLE yeu_cau IS 'Quản lý yêu cầu từ người dân (workflow phê duyệt)';
