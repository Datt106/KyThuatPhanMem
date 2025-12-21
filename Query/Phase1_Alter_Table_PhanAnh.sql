-- =====================================================
-- PHASE 1.2: CẬP NHẬT BẢNG PHANANH
-- =====================================================
-- Mục đích: Thêm liên kết đến vande và timestamp tracking
-- =====================================================

BEGIN;

-- Kiểm tra và thêm cột mavande (Foreign Key)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'phananh' 
        AND column_name = 'mavande'
    ) THEN
        ALTER TABLE public.phananh
            ADD COLUMN mavande INTEGER;
        
        RAISE NOTICE '✓ Đã thêm cột mavande';
    ELSE
        RAISE NOTICE '⚠ Cột mavande đã tồn tại';
    END IF;
END $$;

-- Kiểm tra và thêm cột thoigiantao
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'phananh' 
        AND column_name = 'thoigiantao'
    ) THEN
        ALTER TABLE public.phananh
            ADD COLUMN thoigiantao TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        
        -- Cập nhật giá trị mặc định cho các bản ghi cũ
        UPDATE public.phananh 
        SET thoigiantao = CURRENT_TIMESTAMP 
        WHERE thoigiantao IS NULL;
        
        RAISE NOTICE '✓ Đã thêm cột thoigiantao';
    ELSE
        RAISE NOTICE '⚠ Cột thoigiantao đã tồn tại';
    END IF;
END $$;

-- Kiểm tra và thêm cột thoigianxuly
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'phananh' 
        AND column_name = 'thoigianxuly'
    ) THEN
        ALTER TABLE public.phananh
            ADD COLUMN thoigianxuly TIMESTAMP;
        
        RAISE NOTICE '✓ Đã thêm cột thoigianxuly';
    ELSE
        RAISE NOTICE '⚠ Cột thoigianxuly đã tồn tại';
    END IF;
END $$;

-- Thêm Foreign Key constraint cho mavande
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'phananh_mavande_fkey'
    ) THEN
        ALTER TABLE public.phananh
            ADD CONSTRAINT phananh_mavande_fkey FOREIGN KEY (mavande)
                REFERENCES public.vande(mavande)
                ON DELETE SET NULL
                ON UPDATE CASCADE;
        
        RAISE NOTICE '✓ Đã thêm Foreign Key constraint cho mavande';
    ELSE
        RAISE NOTICE '⚠ Foreign Key constraint đã tồn tại';
    END IF;
END $$;

-- Tạo indexes để tối ưu query
CREATE INDEX IF NOT EXISTS idx_phananh_mavande ON public.phananh(mavande);
CREATE INDEX IF NOT EXISTS idx_phananh_thoigiantao ON public.phananh(thoigiantao DESC);
CREATE INDEX IF NOT EXISTS idx_phananh_is_public ON public.phananh(is_public);
CREATE INDEX IF NOT EXISTS idx_phananh_trangthai ON public.phananh(trangthaiphananh);

-- Composite index cho News Feed query
CREATE INDEX IF NOT EXISTS idx_phananh_newsfeed 
    ON public.phananh(is_public, thoigiantao DESC) 
    WHERE is_public = true;

-- Composite index cho phản ánh hot (nhiều tương tác)
CREATE INDEX IF NOT EXISTS idx_phananh_hot 
    ON public.phananh(is_public, like_count DESC, comment_count DESC) 
    WHERE is_public = true;

-- Comment mô tả các cột mới
COMMENT ON COLUMN public.phananh.mavande IS 'Mã vấn đề mà phản ánh này thuộc về (FK -> vande.mavande)';
COMMENT ON COLUMN public.phananh.thoigiantao IS 'Thời điểm tạo phản ánh';
COMMENT ON COLUMN public.phananh.thoigianxuly IS 'Thời điểm xử lý/cập nhật trạng thái';

COMMIT;

-- =====================================================
-- THÔNG BÁO HOÀN THÀNH
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE '═══════════════════════════════════════════════';
    RAISE NOTICE '✓ Hoàn thành cập nhật bảng phananh';
    RAISE NOTICE '✓ Đã thêm: mavande, thoigiantao, thoigianxuly';
    RAISE NOTICE '✓ Đã tạo 6 indexes cho performance optimization';
    RAISE NOTICE '═══════════════════════════════════════════════';
END $$;
