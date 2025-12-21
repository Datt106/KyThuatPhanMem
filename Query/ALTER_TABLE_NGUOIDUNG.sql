-- ================================================
-- MIGRATION: Bổ sung thông tin chi tiết cho bảng NguoiDung
-- Ngày tạo: 21/12/2025
-- Mục đích: Thêm các trường thông tin chi tiết theo yêu cầu quản lý nhân khẩu
-- ================================================

\c QuanLyPhanAnh;

BEGIN;

-- Thêm các cột mới vào bảng nguoidung
ALTER TABLE public.nguoidung
    ADD COLUMN IF NOT EXISTS bidanh VARCHAR(50),
    ADD COLUMN IF NOT EXISTS noisinh VARCHAR(100),
    ADD COLUMN IF NOT EXISTS nguyenquan VARCHAR(200),
    ADD COLUMN IF NOT EXISTS noilamviec VARCHAR(200),
    ADD COLUMN IF NOT EXISTS ngaycapcccd DATE,
    ADD COLUMN IF NOT EXISTS noicapcccd VARCHAR(100),
    ADD COLUMN IF NOT EXISTS ngaydangkythuongtru DATE,
    ADD COLUMN IF NOT EXISTS diachitruoc TEXT;

-- Thêm comment cho các cột mới
COMMENT ON COLUMN public.nguoidung.bidanh IS 'Bí danh của người dùng (nếu có)';
COMMENT ON COLUMN public.nguoidung.noisinh IS 'Nơi sinh của người dùng';
COMMENT ON COLUMN public.nguoidung.nguyenquan IS 'Nguyên quán của người dùng';
COMMENT ON COLUMN public.nguoidung.noilamviec IS 'Nơi làm việc hiện tại';
COMMENT ON COLUMN public.nguoidung.ngaycapcccd IS 'Ngày cấp CCCD';
COMMENT ON COLUMN public.nguoidung.noicapcccd IS 'Nơi cấp CCCD';
COMMENT ON COLUMN public.nguoidung.ngaydangkythuongtru IS 'Ngày đăng ký thường trú tại địa chỉ hiện tại';
COMMENT ON COLUMN public.nguoidung.diachitruoc IS 'Địa chỉ nơi thường trú trước khi chuyển đến (hoặc "Mới sinh" nếu sinh ra tại đây)';

COMMIT;

-- ================================================
-- KIỂM TRA KẾT QUẢ
-- ================================================
-- Chạy query sau để xem cấu trúc bảng mới:
-- SELECT column_name, data_type, character_maximum_length, column_default, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'nguoidung'
-- ORDER BY ordinal_position;
