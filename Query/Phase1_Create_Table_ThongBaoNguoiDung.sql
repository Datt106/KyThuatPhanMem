-- =====================================================
-- PHASE 1.3: TẠO BẢNG THONGBAO_NGUOIDUNG
-- =====================================================
-- Mục đích: Quản lý thông báo cá nhân cho từng người dùng
-- Khác với bảng thongbao (thông báo chung), bảng này lưu:
-- - Thông báo riêng cho từng người
-- - Trạng thái đã đọc/chưa đọc
-- - Thông báo tự động từ hệ thống (cập nhật vấn đề, chat...)
-- =====================================================

BEGIN;

-- Tạo bảng thongbao_nguoidung
CREATE TABLE IF NOT EXISTS public.thongbao_nguoidung (
    mathongbao_nguoidung SERIAL PRIMARY KEY,
    cccd CHAR(12) NOT NULL,
    mathongbao INTEGER,
    noidung TEXT NOT NULL,
    loai VARCHAR(50) DEFAULT 'General',
    trangthai_doc BOOLEAN DEFAULT FALSE,
    thoigian TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mavande INTEGER,
    maphananh INTEGER,
    
    -- Ràng buộc: Loại thông báo
    CONSTRAINT thongbao_nguoidung_loai_check CHECK (
        loai IN ('General', 'PhanAnh', 'VanDe', 'Chat', 'System', 'LichSu')
    ),
    
    -- Khoá ngoại: Người nhận thông báo
    CONSTRAINT thongbao_nguoidung_cccd_fkey FOREIGN KEY (cccd)
        REFERENCES public.nguoidung(cccd)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    -- Khoá ngoại: Liên kết đến thông báo chung (nếu có)
    CONSTRAINT thongbao_nguoidung_mathongbao_fkey FOREIGN KEY (mathongbao)
        REFERENCES public.thongbao(mathongbao)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    
    -- Khoá ngoại: Liên kết đến vấn đề (nếu có)
    CONSTRAINT thongbao_nguoidung_mavande_fkey FOREIGN KEY (mavande)
        REFERENCES public.vande(mavande)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    -- Khoá ngoại: Liên kết đến phản ánh (nếu có)
    CONSTRAINT thongbao_nguoidung_maphananh_fkey FOREIGN KEY (maphananh)
        REFERENCES public.phananh(maphananh)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Tạo indexes để tối ưu query
CREATE INDEX IF NOT EXISTS idx_thongbao_nguoidung_cccd 
    ON public.thongbao_nguoidung(cccd, thoigian DESC);

CREATE INDEX IF NOT EXISTS idx_thongbao_nguoidung_chua_doc 
    ON public.thongbao_nguoidung(cccd, trangthai_doc) 
    WHERE trangthai_doc = FALSE;

CREATE INDEX IF NOT EXISTS idx_thongbao_nguoidung_loai 
    ON public.thongbao_nguoidung(loai);

CREATE INDEX IF NOT EXISTS idx_thongbao_nguoidung_thoigian 
    ON public.thongbao_nguoidung(thoigian DESC);

CREATE INDEX IF NOT EXISTS idx_thongbao_nguoidung_mavande 
    ON public.thongbao_nguoidung(mavande);

CREATE INDEX IF NOT EXISTS idx_thongbao_nguoidung_maphananh 
    ON public.thongbao_nguoidung(maphananh);

-- Comment mô tả bảng và cột
COMMENT ON TABLE public.thongbao_nguoidung IS 'Lưu thông báo cá nhân cho từng người dùng với trạng thái đã đọc';
COMMENT ON COLUMN public.thongbao_nguoidung.mathongbao_nguoidung IS 'Mã thông báo người dùng (Primary Key)';
COMMENT ON COLUMN public.thongbao_nguoidung.cccd IS 'CCCD người nhận thông báo';
COMMENT ON COLUMN public.thongbao_nguoidung.mathongbao IS 'Mã thông báo chung (nếu liên kết từ bảng thongbao)';
COMMENT ON COLUMN public.thongbao_nguoidung.noidung IS 'Nội dung thông báo';
COMMENT ON COLUMN public.thongbao_nguoidung.loai IS 'Loại: General, PhanAnh, VanDe, Chat, System, LichSu';
COMMENT ON COLUMN public.thongbao_nguoidung.trangthai_doc IS 'Trạng thái đã đọc (TRUE/FALSE)';
COMMENT ON COLUMN public.thongbao_nguoidung.thoigian IS 'Thời điểm tạo thông báo';
COMMENT ON COLUMN public.thongbao_nguoidung.mavande IS 'Liên kết đến vấn đề (nếu thông báo về vấn đề)';
COMMENT ON COLUMN public.thongbao_nguoidung.maphananh IS 'Liên kết đến phản ánh (nếu thông báo về phản ánh)';

COMMIT;

-- =====================================================
-- THÔNG BÁO HOÀN THÀNH
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE '✓ Đã tạo bảng thongbao_nguoidung thành công';
    RAISE NOTICE '✓ Đã tạo 6 indexes cho performance';
    RAISE NOTICE '✓ Đã thêm 4 foreign keys và constraints';
    RAISE NOTICE '✓ Support các loại: General, PhanAnh, VanDe, Chat, System, LichSu';
END $$;
