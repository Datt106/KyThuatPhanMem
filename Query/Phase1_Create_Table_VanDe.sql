-- =====================================================
-- PHASE 1.1: TẠO BẢNG VANDE (VẤN ĐỀ TỔNG HỢP)
-- =====================================================
-- Mục đích: Quản lý các vấn đề/sự việc được tổng hợp từ nhiều phản ánh
-- Quan hệ: 1 vande -> nhiều phananh (1-n)
-- =====================================================

BEGIN;

-- Tạo bảng vande
CREATE TABLE IF NOT EXISTS public.vande (
    mavande SERIAL PRIMARY KEY,
    tenvande VARCHAR(255) NOT NULL,
    phanloai VARCHAR(100) DEFAULT 'Khac',
    trangthai VARCHAR(50) DEFAULT 'Moi',
    ketqua TEXT,
    ngaytao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ngaycapnhat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cccd_canbo_xuly CHAR(12),
    
    -- Ràng buộc: Phân loại vấn đề
    CONSTRAINT vande_phanloai_check CHECK (
        phanloai IN ('HaTang', 'MoiTruong', 'AnNinh', 'GiaoThong', 'YTe', 'GiaoDuc', 'VanHoa', 'Khac')
    ),
    
    -- Ràng buộc: Trạng thái xử lý
    CONSTRAINT vande_trangthai_check CHECK (
        trangthai IN ('Moi', 'DangXuLy', 'DaGiaiQuyet', 'KhongGiaiQuyet')
    ),
    
    -- Khoá ngoại: Cán bộ xử lý
    CONSTRAINT vande_cccd_canbo_fkey FOREIGN KEY (cccd_canbo_xuly)
        REFERENCES public.nguoidung(cccd)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Tạo index để tối ưu query
CREATE INDEX IF NOT EXISTS idx_vande_trangthai ON public.vande(trangthai);
CREATE INDEX IF NOT EXISTS idx_vande_phanloai ON public.vande(phanloai);
CREATE INDEX IF NOT EXISTS idx_vande_ngaytao ON public.vande(ngaytao DESC);
CREATE INDEX IF NOT EXISTS idx_vande_canbo ON public.vande(cccd_canbo_xuly);

-- Comment mô tả bảng
COMMENT ON TABLE public.vande IS 'Lưu thông tin vấn đề/sự việc được tổng hợp từ nhiều phản ánh của người dân';
COMMENT ON COLUMN public.vande.mavande IS 'Mã vấn đề (Primary Key)';
COMMENT ON COLUMN public.vande.tenvande IS 'Tên vấn đề (VD: Mất nước khu vực 7, Đường bị hỏng...)';
COMMENT ON COLUMN public.vande.phanloai IS 'Phân loại: HaTang, MoiTruong, AnNinh, GiaoThong, YTe, GiaoDuc, VanHoa, Khac';
COMMENT ON COLUMN public.vande.trangthai IS 'Trạng thái: Moi, DangXuLy, DaGiaiQuyet, KhongGiaiQuyet';
COMMENT ON COLUMN public.vande.ketqua IS 'Kết quả giải quyết vấn đề';
COMMENT ON COLUMN public.vande.ngaytao IS 'Thời điểm tạo vấn đề';
COMMENT ON COLUMN public.vande.ngaycapnhat IS 'Thời điểm cập nhật cuối cùng';
COMMENT ON COLUMN public.vande.cccd_canbo_xuly IS 'CCCD cán bộ được phân công xử lý';

COMMIT;

-- =====================================================
-- THÔNG BÁO HOÀN THÀNH
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE '✓ Đã tạo bảng vande thành công';
    RAISE NOTICE '✓ Đã tạo 4 indexes cho performance';
    RAISE NOTICE '✓ Đã thêm constraints và comments';
END $$;
