-- ================================================
-- TRIGGER 1: Cập nhật ngày kết thúc địa chỉ cũ
-- ================================================
CREATE OR REPLACE FUNCTION fn_cap_nhat_ket_thuc_dia_chi_cu()
RETURNS TRIGGER AS $$
BEGIN
    -- Nếu người dân đã có địa chỉ cùng loại chưa kết thúc
    UPDATE DiaChiNguoiDung
    SET ThoiDiemKetThuc = CURRENT_DATE
    WHERE CCCD = NEW.CCCD
      AND LoaiDiaChi = NEW.LoaiDiaChi
      AND ThoiDiemKetThuc IS NULL;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cap_nhat_ket_thuc_dia_chi_cu
BEFORE INSERT ON DiaChiNguoiDung
FOR EACH ROW
EXECUTE FUNCTION fn_cap_nhat_ket_thuc_dia_chi_cu();

COMMENT ON TRIGGER trg_cap_nhat_ket_thuc_dia_chi_cu ON DiaChiNguoiDung IS
'Tự động cập nhật ngày kết thúc địa chỉ cũ cùng loại khi người dân thay đổi nơi cư trú/tạm trú/tạm vắng/nơi làm việc.';

-- ================================================
-- TRIGGER 2A: Tự tạo BoxChat khi có phản ánh mới
-- ================================================
CREATE OR REPLACE FUNCTION fn_tao_box_chat_khi_them_phan_anh()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO BoxChat (MaPhanAnh, CCCD_NguoiDan)
    VALUES (NEW.MaPhanAnh, NEW.CCCD);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tao_box_chat_khi_them_phan_anh
AFTER INSERT ON PhanAnh
FOR EACH ROW
EXECUTE FUNCTION fn_tao_box_chat_khi_them_phan_anh();

COMMENT ON TRIGGER trg_tao_box_chat_khi_them_phan_anh ON PhanAnh IS
'Tự động tạo box chat mới cho phản ánh vừa được thêm.';

-- ================================================
-- TRIGGER 2B: Cập nhật trạng thái phản ánh khi cán bộ gửi tin nhắn
-- ================================================
CREATE OR REPLACE FUNCTION fn_cap_nhat_trang_thai_phan_anh()
RETURNS TRIGGER AS $$
DECLARE
    ma_phan_anh INT;
BEGIN
    -- Lấy mã phản ánh từ box chat
    SELECT MaPhanAnh INTO ma_phan_anh
    FROM BoxChat
    WHERE MaBoxChat = NEW.MaBoxChat;

    -- Nếu người gửi là cán bộ → đổi trạng thái phản ánh
    IF EXISTS (
        SELECT 1 FROM NguoiDung
        WHERE CCCD = NEW.NguoiGui AND VaiTro = 'CanBo'
    ) THEN
        UPDATE PhanAnh
        SET TrangThaiPhanAnh = 'DangXuLy'
        WHERE MaPhanAnh = ma_phan_anh;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cap_nhat_trang_thai_phan_anh
AFTER INSERT ON TinNhan
FOR EACH ROW
EXECUTE FUNCTION fn_cap_nhat_trang_thai_phan_anh();

COMMENT ON TRIGGER trg_cap_nhat_trang_thai_phan_anh ON TinNhan IS
'Tự động cập nhật phản ánh sang "Đang xử lý" khi cán bộ gửi tin nhắn.';

-- ================================================
-- TRIGGER 3: Xóa hộ khẩu khi không còn thành viên
-- ================================================
CREATE OR REPLACE FUNCTION fn_xoa_ho_khau_khi_khong_con_thanh_vien()
RETURNS TRIGGER AS $$
BEGIN
    -- Nếu hộ khẩu không còn thành viên nào
    IF NOT EXISTS (
        SELECT 1 FROM ThanhVienHoKhau WHERE MaHoKhau = OLD.MaHoKhau
    ) THEN
        DELETE FROM HoKhau WHERE MaHoKhau = OLD.MaHoKhau;
    END IF;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_xoa_ho_khau_khi_khong_con_thanh_vien
AFTER DELETE ON ThanhVienHoKhau
FOR EACH ROW
EXECUTE FUNCTION fn_xoa_ho_khau_khi_khong_con_thanh_vien();

COMMENT ON TRIGGER trg_xoa_ho_khau_khi_khong_con_thanh_vien ON ThanhVienHoKhau IS
'Tự động xóa sổ hộ khẩu khi không còn thành viên nào.';

-- ================================================
-- TRIGGER 4: Ẩn thông tin người dân khi phản ánh chưa được xử lý
-- ================================================
CREATE OR REPLACE FUNCTION fn_an_thong_tin_nguoi_dan()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.TrangThaiPhanAnh = 'ChuaXuLy' THEN
        UPDATE NguoiDung
        SET BaoMatThongTin = TRUE
        WHERE CCCD = NEW.CCCD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_an_thong_tin_nguoi_dan
AFTER INSERT OR UPDATE ON PhanAnh
FOR EACH ROW
EXECUTE FUNCTION fn_an_thong_tin_nguoi_dan();

COMMENT ON TRIGGER trg_an_thong_tin_nguoi_dan ON PhanAnh IS
'Tự động ẩn thông tin người dân khi phản ánh chưa được xử lý.';
