-- ================================================
-- FIX: Sửa lỗi hiển thị thành viên và tự động đánh dấu hộ trống
-- Ngày: 2025-12-29
-- ================================================

-- GIẢI THÍCH CÁC SỬA ĐỔI ĐÃ THỰC HIỆN:

-- 1. SỬA LỖI: Hiển thị cả người đã chuyển đi trong danh sách thành viên
--    - VẤN ĐỀ: Query không có điều kiện ngayketthuc IS NULL
--    - GIẢI PHÁP: Thêm điều kiện WHERE tv.ngayketthuc IS NULL vào tất cả query lấy thành viên hiện tại

-- 2. TÍNH NĂNG MỚI: Tự động đánh dấu hộ khẩu trống
--    - KHI: Thành viên cuối cùng rời khỏi hộ (chuyển đi, qua đời...)
--    - HÀNH ĐỘNG: Tự động thêm tag "[HỘ TRỐNG - Không còn thành viên]" vào cột ghichu
--    - LỢI ÍCH: Giữ lại dữ liệu hộ khẩu để tra cứu lịch sử, không bị mất dữ liệu

-- ================================================
-- TÙY CHỌN: Thêm cột trangthai vào bảng hokhau (nếu muốn quản lý chính thức hơn)
-- ================================================

BEGIN;

-- Thêm cột trangthai (nếu chưa có)
ALTER TABLE public.hokhau 
ADD COLUMN IF NOT EXISTS trangthai VARCHAR(20) DEFAULT 'Hoạt động';

COMMENT ON COLUMN public.hokhau.trangthai 
IS 'Trạng thái hộ khẩu: Hoạt động, Trống, Đã giải thể';

-- Tạo index để tìm kiếm nhanh
CREATE INDEX IF NOT EXISTS idx_hokhau_trangthai 
ON public.hokhau(trangthai);

COMMIT;

-- ================================================
-- CẬP NHẬT TỰ ĐỘNG TRẠNG THÁI (nếu dùng cột trangthai)
-- ================================================

-- Đánh dấu các hộ trống (không còn thành viên)
UPDATE hokhau h
SET trangthai = 'Trống'
WHERE NOT EXISTS (
    SELECT 1 FROM thanhvienhokhau tv 
    WHERE tv.mahokhau = h.mahokhau 
    AND tv.ngayketthuc IS NULL
)
AND trangthai != 'Trống';

-- Đánh dấu các hộ hoạt động (có thành viên)
UPDATE hokhau h
SET trangthai = 'Hoạt động'
WHERE EXISTS (
    SELECT 1 FROM thanhvienhokhau tv 
    WHERE tv.mahokhau = h.mahokhau 
    AND tv.ngayketthuc IS NULL
)
AND trangthai != 'Hoạt động';

-- ================================================
-- VIEW: Tổng hợp thông tin hộ khẩu
-- ================================================

CREATE OR REPLACE VIEW v_hokhau_summary AS
SELECT 
    h.mahokhau,
    h.ngaycap,
    h.ghichu,
    h.trangthai,
    d.tinh,
    d.xaphuong,
    d.chitiet as diachi,
    COUNT(CASE WHEN tv.ngayketthuc IS NULL THEN 1 END) as so_thanh_vien_hien_tai,
    COUNT(CASE WHEN tv.ngayketthuc IS NOT NULL THEN 1 END) as so_thanh_vien_da_roi,
    MAX(CASE WHEN tv.quanhechuho = 'Chủ hộ' AND tv.ngayketthuc IS NULL 
        THEN n.name END) as ten_chu_ho,
    MAX(CASE WHEN tv.quanhechuho = 'Chủ hộ' AND tv.ngayketthuc IS NULL 
        THEN tv.cccd END) as cccd_chu_ho
FROM hokhau h
LEFT JOIN diachi d ON h.madiachi = d.madiachi
LEFT JOIN thanhvienhokhau tv ON h.mahokhau = tv.mahokhau
LEFT JOIN nguoidung n ON tv.cccd = n.cccd
GROUP BY h.mahokhau, h.ngaycap, h.ghichu, h.trangthai, d.tinh, d.xaphuong, d.chitiet;

COMMENT ON VIEW v_hokhau_summary 
IS 'Tổng hợp thông tin hộ khẩu với số lượng thành viên hiện tại và đã rời';

-- ================================================
-- TRIGGER: Tự động cập nhật trạng thái khi thành viên thay đổi (TÙY CHỌN)
-- ================================================

CREATE OR REPLACE FUNCTION update_hokhau_trangthai()
RETURNS TRIGGER AS $$
BEGIN
    -- Kiểm tra số thành viên còn lại
    IF NOT EXISTS (
        SELECT 1 FROM thanhvienhokhau 
        WHERE mahokhau = COALESCE(NEW.mahokhau, OLD.mahokhau)
        AND ngayketthuc IS NULL
    ) THEN
        -- Không còn thành viên -> Đánh dấu Trống
        UPDATE hokhau 
        SET trangthai = 'Trống'
        WHERE mahokhau = COALESCE(NEW.mahokhau, OLD.mahokhau);
    ELSE
        -- Còn thành viên -> Đánh dấu Hoạt động
        UPDATE hokhau 
        SET trangthai = 'Hoạt động'
        WHERE mahokhau = COALESCE(NEW.mahokhau, OLD.mahokhau)
        AND trangthai != 'Hoạt động';
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Gắn trigger vào bảng thanhvienhokhau
DROP TRIGGER IF EXISTS trigger_update_hokhau_trangthai ON thanhvienhokhau;
CREATE TRIGGER trigger_update_hokhau_trangthai
AFTER INSERT OR UPDATE OR DELETE ON thanhvienhokhau
FOR EACH ROW
EXECUTE FUNCTION update_hokhau_trangthai();

-- ================================================
-- QUERY KIỂM TRA
-- ================================================

-- 1. Xem các hộ trống
SELECT 
    h.mahokhau,
    d.chitiet || ', ' || d.xaphuong as diachi,
    h.trangthai,
    h.ghichu,
    COUNT(tv.cccd) FILTER (WHERE tv.ngayketthuc IS NULL) as thanh_vien_hien_tai,
    COUNT(tv.cccd) FILTER (WHERE tv.ngayketthuc IS NOT NULL) as da_roi_khoi_ho
FROM hokhau h
LEFT JOIN diachi d ON h.madiachi = d.madiachi
LEFT JOIN thanhvienhokhau tv ON h.mahokhau = tv.mahokhau
GROUP BY h.mahokhau, d.chitiet, d.xaphuong, h.trangthai, h.ghichu
HAVING COUNT(tv.cccd) FILTER (WHERE tv.ngayketthuc IS NULL) = 0
ORDER BY h.mahokhau;

-- 2. Thống kê theo trạng thái
SELECT 
    trangthai,
    COUNT(*) as so_luong
FROM hokhau
GROUP BY trangthai
ORDER BY trangthai;

-- 3. Xem chi tiết hộ 19620 (ví dụ test)
SELECT 
    h.mahokhau,
    h.trangthai,
    h.ghichu,
    tv.cccd,
    n.name,
    tv.quanhechuho,
    tv.ngaybatdau,
    tv.ngayketthuc,
    tv.lydochuyen,
    tv.noichuyenden
FROM hokhau h
LEFT JOIN thanhvienhokhau tv ON h.mahokhau = tv.mahokhau
LEFT JOIN nguoidung n ON tv.cccd = n.cccd
WHERE h.mahokhau = 19620
ORDER BY tv.ngayketthuc IS NULL DESC, tv.ngaybatdau;
