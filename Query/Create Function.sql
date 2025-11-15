-- ========================================================
--  CÁC FUNCTION THỐNG KÊ DÂN CƯ / LÀM VIỆC
-- (Dựa trên cấu trúc bảng DiaChi và DiaChiNguoiDung hiện tại)
-- ========================================================

-- 1️ Thống kê số người thường trú ở một phường/xã
CREATE OR REPLACE FUNCTION thong_ke_thuong_tru_phuong(ten_xa_phuong VARCHAR)
RETURNS INT AS $$
DECLARE
    so_luong INT;
BEGIN
    SELECT COUNT(*) INTO so_luong
    FROM DiaChiNguoiDung dcnd
    JOIN DiaChi dc ON dcnd.MaDiaChi = dc.MaDiaChi
    WHERE dcnd.LoaiDiaChi = 'CuTru'
      AND dc.XaPhuong = ten_xa_phuong
      AND dcnd.ThoiDiemKetThuc IS NULL;
    RETURN so_luong;
END;
$$ LANGUAGE plpgsql;


-- 2️ Thống kê số người thường trú ở một tỉnh
CREATE OR REPLACE FUNCTION thong_ke_thuong_tru_tinh(ten_tinh VARCHAR)
RETURNS INT AS $$
DECLARE
    so_luong INT;
BEGIN
    SELECT COUNT(*) INTO so_luong
    FROM DiaChiNguoiDung dcnd
    JOIN DiaChi dc ON dcnd.MaDiaChi = dc.MaDiaChi
    WHERE dcnd.LoaiDiaChi = 'CuTru'
      AND dc.Tinh = ten_tinh
      AND dcnd.ThoiDiemKetThuc IS NULL;
    RETURN so_luong;
END;
$$ LANGUAGE plpgsql;


-- 3️ Thống kê số người tạm trú ở một phường/xã
CREATE OR REPLACE FUNCTION thong_ke_tam_tru_phuong(ten_xa_phuong VARCHAR)
RETURNS INT AS $$
DECLARE
    so_luong INT;
BEGIN
    SELECT COUNT(*) INTO so_luong
    FROM DiaChiNguoiDung dcnd
    JOIN DiaChi dc ON dcnd.MaDiaChi = dc.MaDiaChi
    WHERE dcnd.LoaiDiaChi = 'TamTru'
      AND dc.XaPhuong = ten_xa_phuong
      AND dcnd.ThoiDiemKetThuc IS NULL;
    RETURN so_luong;
END;
$$ LANGUAGE plpgsql;


-- 4️ Thống kê số người tạm trú ở một tỉnh
CREATE OR REPLACE FUNCTION thong_ke_tam_tru_tinh(ten_tinh VARCHAR)
RETURNS INT AS $$
DECLARE
    so_luong INT;
BEGIN
    SELECT COUNT(*) INTO so_luong
    FROM DiaChiNguoiDung dcnd
    JOIN DiaChi dc ON dcnd.MaDiaChi = dc.MaDiaChi
    WHERE dcnd.LoaiDiaChi = 'TamTru'
      AND dc.Tinh = ten_tinh
      AND dcnd.ThoiDiemKetThuc IS NULL;
    RETURN so_luong;
END;
$$ LANGUAGE plpgsql;


-- 5️ Thống kê số người làm việc ở một phường/xã
CREATE OR REPLACE FUNCTION thong_ke_lam_viec_phuong(ten_xa_phuong VARCHAR)
RETURNS INT AS $$
DECLARE
    so_luong INT;
BEGIN
    SELECT COUNT(*) INTO so_luong
    FROM DiaChiNguoiDung dcnd
    JOIN DiaChi dc ON dcnd.MaDiaChi = dc.MaDiaChi
    WHERE dcnd.LoaiDiaChi = 'NoiLamViec'
      AND dc.XaPhuong = ten_xa_phuong
      AND dcnd.ThoiDiemKetThuc IS NULL;
    RETURN so_luong;
END;
$$ LANGUAGE plpgsql;


-- 6️ Thống kê số người làm việc ở một tỉnh
CREATE OR REPLACE FUNCTION thong_ke_lam_viec_tinh(ten_tinh VARCHAR)
RETURNS INT AS $$
DECLARE
    so_luong INT;
BEGIN
    SELECT COUNT(*) INTO so_luong
    FROM DiaChiNguoiDung dcnd
    JOIN DiaChi dc ON dcnd.MaDiaChi = dc.MaDiaChi
    WHERE dcnd.LoaiDiaChi = 'NoiLamViec'
      AND dc.Tinh = ten_tinh
      AND dcnd.ThoiDiemKetThuc IS NULL;
    RETURN so_luong;
END;
$$ LANGUAGE plpgsql;


-- 7️ Thống kê tổng hợp (theo tỉnh) - trả về đầy đủ loại địa chỉ
CREATE OR REPLACE FUNCTION thong_ke_tong_hop_tinh(ten_tinh VARCHAR)
RETURNS TABLE (
    Tinh VARCHAR,
    SoCuTru INT,
    SoTamTru INT,
    SoNoiLamViec INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ten_tinh AS Tinh,
        (SELECT COUNT(*) FROM DiaChiNguoiDung dcnd JOIN DiaChi dc ON dc.MaDiaChi = dcnd.MaDiaChi
         WHERE dc.Tinh = ten_tinh AND dcnd.LoaiDiaChi = 'CuTru' AND dcnd.ThoiDiemKetThuc IS NULL),
        (SELECT COUNT(*) FROM DiaChiNguoiDung dcnd JOIN DiaChi dc ON dc.MaDiaChi = dcnd.MaDiaChi
         WHERE dc.Tinh = ten_tinh AND dcnd.LoaiDiaChi = 'TamTru' AND dcnd.ThoiDiemKetThuc IS NULL),
        (SELECT COUNT(*) FROM DiaChiNguoiDung dcnd JOIN DiaChi dc ON dc.MaDiaChi = dcnd.MaDiaChi
         WHERE dc.Tinh = ten_tinh AND dcnd.LoaiDiaChi = 'NoiLamViec' AND dcnd.ThoiDiemKetThuc IS NULL);
END;
$$ LANGUAGE plpgsql;
