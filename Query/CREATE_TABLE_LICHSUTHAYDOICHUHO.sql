-- ================================================
-- CREATE TABLE: lichsuthaydoichuho
-- Mục đích: Lưu lịch sử thay đổi chủ hộ
-- Ngày tạo: 2025-12-21
-- ================================================

BEGIN;

CREATE TABLE IF NOT EXISTS public.lichsuthaydoichuho (
    id SERIAL PRIMARY KEY,
    mahokhau INTEGER NOT NULL,
    cccd_cu CHAR(12) NOT NULL,
    cccd_moi CHAR(12) NOT NULL,
    ngaythaydoi DATE NOT NULL DEFAULT CURRENT_DATE,
    lydothaydoi VARCHAR(200),
    noidung TEXT,
    nguoithuchien VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_lichsu_mahokhau 
        FOREIGN KEY (mahokhau) REFERENCES public.hokhau(mahokhau) ON DELETE CASCADE,
    CONSTRAINT fk_lichsu_cccd_cu 
        FOREIGN KEY (cccd_cu) REFERENCES public.nguoidung(cccd),
    CONSTRAINT fk_lichsu_cccd_moi 
        FOREIGN KEY (cccd_moi) REFERENCES public.nguoidung(cccd)
);

-- Tạo index để tăng tốc độ truy vấn
CREATE INDEX IF NOT EXISTS idx_lichsuthaydoichuho_mahokhau 
    ON public.lichsuthaydoichuho(mahokhau);

CREATE INDEX IF NOT EXISTS idx_lichsuthaydoichuho_ngaythaydoi 
    ON public.lichsuthaydoichuho(ngaythaydoi DESC);

-- Thêm comment
COMMENT ON TABLE public.lichsuthaydoichuho 
    IS 'Lưu lịch sử thay đổi chủ hộ của các hộ khẩu';

COMMENT ON COLUMN public.lichsuthaydoichuho.cccd_cu 
    IS 'CCCD của chủ hộ cũ';

COMMENT ON COLUMN public.lichsuthaydoichuho.cccd_moi 
    IS 'CCCD của chủ hộ mới';

COMMENT ON COLUMN public.lichsuthaydoichuho.lydothaydoi 
    IS 'Lý do thay đổi: Qua đời, Chuyển đi, Yêu cầu đổi, v.v.';

COMMIT;

-- Kiểm tra kết quả
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'lichsuthaydoichuho'
    AND table_schema = 'public'
ORDER BY ordinal_position;
