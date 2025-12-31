-- Script sửa lỗi constraint cho loại địa chỉ Tạm vắng
-- Chạy script này trong pgAdmin 4

BEGIN;

-- 1. Xóa constraint kiểm tra cũ (nếu có)
ALTER TABLE public.diachinguoidung 
DROP CONSTRAINT IF EXISTS diachinguoidung_loaidiachi_check;

-- 2. Thêm constraint mới bao gồm 'TamVang'
ALTER TABLE public.diachinguoidung
ADD CONSTRAINT diachinguoidung_loaidiachi_check 
CHECK (loaidiachi IN ('ThuongTru', 'TamTru', 'NoiLamViec', 'TamVang', 'CuTru'));

-- Note: Đã thêm 'CuTru' phòng trường hợp dữ liệu cũ dùng từ này (dựa trên code app.py line 1820)
-- "WHERE dcnd.loaidiachi = 'CuTru'" --> Code đang dùng 'CuTru' thay vì 'ThuongTru'?

COMMIT;
