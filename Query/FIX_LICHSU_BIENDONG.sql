-- ================================================
-- FIX: Lịch sử biến động nhân khẩu
-- Mục đích: Đảm bảo các bảng và cột cần thiết đã tồn tại
-- Ngày: 2025-12-29
-- ================================================

BEGIN;

-- 1. Kiểm tra và thêm các cột vào bảng thanhvienhokhau (nếu chưa có)
ALTER TABLE public.thanhvienhokhau 
ADD COLUMN IF NOT EXISTS lydochuyen VARCHAR(100);

ALTER TABLE public.thanhvienhokhau 
ADD COLUMN IF NOT EXISTS noichuyenden TEXT;

ALTER TABLE public.thanhvienhokhau 
ADD COLUMN IF NOT EXISTS ghichu TEXT;

-- 2. Tạo bảng lichsuthaydoichuho (nếu chưa có)
CREATE TABLE IF NOT EXISTS public.lichsuthaydoichuho (
    malichsu SERIAL PRIMARY KEY,
    mahokhau INTEGER NOT NULL,
    cccd_cu CHAR(12),
    cccd_moi CHAR(12) NOT NULL,
    ngaythaydoi DATE DEFAULT CURRENT_DATE,
    lydothaydoi VARCHAR(100),
    noidung TEXT,
    nguoithuchien CHAR(12),
    CONSTRAINT fk_lichsuthaydoichuho_hokhau 
        FOREIGN KEY (mahokhau) REFERENCES hokhau(mahokhau) ON DELETE CASCADE,
    CONSTRAINT fk_lichsuthaydoichuho_chuho_cu 
        FOREIGN KEY (cccd_cu) REFERENCES nguoidung(cccd) ON DELETE SET NULL,
    CONSTRAINT fk_lichsuthaydoichuho_chuho_moi 
        FOREIGN KEY (cccd_moi) REFERENCES nguoidung(cccd) ON DELETE CASCADE,
    CONSTRAINT fk_lichsuthaydoichuho_nguoithuchien 
        FOREIGN KEY (nguoithuchien) REFERENCES nguoidung(cccd) ON DELETE SET NULL
);

-- 3. Tạo index để tối ưu truy vấn
CREATE INDEX IF NOT EXISTS idx_lichsuthaydoichuho_mahokhau 
    ON public.lichsuthaydoichuho(mahokhau);

CREATE INDEX IF NOT EXISTS idx_lichsuthaydoichuho_ngaythaydoi 
    ON public.lichsuthaydoichuho(ngaythaydoi DESC);

CREATE INDEX IF NOT EXISTS idx_thanhvienhokhau_ngayketthuc
    ON public.thanhvienhokhau(ngayketthuc) 
    WHERE ngayketthuc IS NOT NULL;

-- 4. Thêm comments
COMMENT ON TABLE public.lichsuthaydoichuho 
IS 'Lưu lịch sử thay đổi chủ hộ';

COMMENT ON COLUMN public.thanhvienhokhau.lydochuyen 
IS 'Lý do kết thúc sinh sống tại hộ: Chuyển đi, Qua đời, Tách hộ, v.v.';

COMMENT ON COLUMN public.thanhvienhokhau.noichuyenden 
IS 'Địa chỉ nơi chuyển đến (nếu có)';

COMMENT ON COLUMN public.thanhvienhokhau.ghichu 
IS 'Ghi chú thêm về biến động nhân khẩu';

COMMIT;

-- 5. Kiểm tra kết quả
SELECT 
    'thanhvienhokhau' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'thanhvienhokhau'
    AND table_schema = 'public'
    AND column_name IN ('lydochuyen', 'noichuyenden', 'ghichu', 'ngayketthuc')
ORDER BY column_name;

SELECT 
    'lichsuthaydoichuho' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'lichsuthaydoichuho'
    AND table_schema = 'public'
ORDER BY ordinal_position;
