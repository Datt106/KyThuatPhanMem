-- ================================================
-- ALTER TABLE: thanhvienhokhau
-- Mục đích: Thêm các cột để lưu thông tin biến động nhân khẩu
-- Ngày tạo: 2025-12-21
-- ================================================

BEGIN;

-- Thêm cột lý do chuyển (chuyển đi, qua đời, tách hộ, v.v.)
ALTER TABLE public.thanhvienhokhau 
ADD COLUMN IF NOT EXISTS lydochuyen VARCHAR(100);

COMMENT ON COLUMN public.thanhvienhokhau.lydochuyen 
IS 'Lý do kết thúc sinh sống tại hộ: Chuyển đi, Qua đời, Tách hộ, v.v.';

-- Thêm cột nơi chuyển đến
ALTER TABLE public.thanhvienhokhau 
ADD COLUMN IF NOT EXISTS noichuyenden TEXT;

COMMENT ON COLUMN public.thanhvienhokhau.noichuyenden 
IS 'Địa chỉ nơi chuyển đến (nếu có)';

-- Thêm cột ghi chú về biến động
ALTER TABLE public.thanhvienhokhau 
ADD COLUMN IF NOT EXISTS ghichu TEXT;

COMMENT ON COLUMN public.thanhvienhokhau.ghichu 
IS 'Ghi chú thêm về biến động nhân khẩu';

COMMIT;

-- Kiểm tra kết quả
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'thanhvienhokhau'
    AND table_schema = 'public'
    AND column_name IN ('lydochuyen', 'noichuyenden', 'ghichu')
ORDER BY ordinal_position;
