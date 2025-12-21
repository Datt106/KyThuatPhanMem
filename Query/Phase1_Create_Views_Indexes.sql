-- =====================================================
-- PHASE 1.4: TẠO VIEW VÀ INDEX TỐI ƯU
-- =====================================================
-- Mục đích: 
-- - Tạo View tổng hợp để query dễ dàng hơn
-- - Tạo indexes bổ sung cho performance
-- =====================================================

BEGIN;

-- =====================================================
-- VIEW 1: VIEW_PHANANH_FULL
-- =====================================================
-- Mục đích: Join đầy đủ thông tin phản ánh với người dùng, địa chỉ, vấn đề
CREATE OR REPLACE VIEW public.view_phananh_full AS
SELECT 
    -- Thông tin phản ánh
    p.maphananh,
    p.tieude,
    p.mota,
    p.loaiphananh,
    p.trangthaiphananh,
    p.is_public,
    p.allow_comment,
    p.like_count,
    p.comment_count,
    p.view_count,
    p.thoigiantao,
    p.thoigianxuly,
    
    -- Thông tin người tạo phản ánh
    p.cccd,
    n.name AS nguoi_tao,
    n.sdt AS sdt_nguoi_tao,
    n.vaitro AS vaitro_nguoi_tao,
    
    -- Thông tin địa chỉ phản ánh
    p.madiachi,
    d.tinh,
    d.xaphuong,
    d.chitiet AS diachi_chitiet,
    
    -- Thông tin vấn đề (nếu đã gộp)
    p.mavande,
    v.tenvande,
    v.phanloai AS phanloai_vande,
    v.trangthai AS trangthai_vande,
    v.ketqua AS ketqua_vande,
    
    -- Thông tin cán bộ xử lý
    v.cccd_canbo_xuly,
    nc.name AS ten_canbo_xuly,
    
    -- Thông tin tệp đính kèm
    p.matepdinhkem,
    t.duongdan AS duongdan_tepdinhkem

FROM public.phananh p
LEFT JOIN public.nguoidung n ON p.cccd = n.cccd
LEFT JOIN public.diachi d ON p.madiachi = d.madiachi
LEFT JOIN public.vande v ON p.mavande = v.mavande
LEFT JOIN public.nguoidung nc ON v.cccd_canbo_xuly = nc.cccd
LEFT JOIN public.tepdinhkem t ON p.matepdinhkem = t.matepdinhkem;

COMMENT ON VIEW public.view_phananh_full IS 'View tổng hợp thông tin đầy đủ của phản ánh (join nguoidung, diachi, vande, canbo)';


-- =====================================================
-- VIEW 2: VIEW_VANDE_SUMMARY
-- =====================================================
-- Mục đích: Thống kê tổng quan về vấn đề
CREATE OR REPLACE VIEW public.view_vande_summary AS
SELECT 
    v.mavande,
    v.tenvande,
    v.phanloai,
    v.trangthai,
    v.ketqua,
    v.ngaytao,
    v.ngaycapnhat,
    
    -- Thông tin cán bộ xử lý
    v.cccd_canbo_xuly,
    n.name AS ten_canbo_xuly,
    n.sdt AS sdt_canbo,
    
    -- Thống kê phản ánh
    COUNT(p.maphananh) AS so_luong_phananh,
    COUNT(DISTINCT p.cccd) AS so_nguoi_phananh,
    
    -- Thống kê tương tác
    COALESCE(SUM(p.like_count), 0) AS tong_like,
    COALESCE(SUM(p.comment_count), 0) AS tong_comment,
    COALESCE(SUM(p.view_count), 0) AS tong_view,
    
    -- Thời gian xử lý
    CASE 
        WHEN v.trangthai = 'DaGiaiQuyet' THEN 
            EXTRACT(EPOCH FROM (v.ngaycapnhat - v.ngaytao)) / 86400  -- Số ngày xử lý
        ELSE NULL
    END AS so_ngay_xu_ly

FROM public.vande v
LEFT JOIN public.nguoidung n ON v.cccd_canbo_xuly = n.cccd
LEFT JOIN public.phananh p ON v.mavande = p.mavande
GROUP BY v.mavande, v.tenvande, v.phanloai, v.trangthai, v.ketqua, 
         v.ngaytao, v.ngaycapnhat, v.cccd_canbo_xuly, n.name, n.sdt;

COMMENT ON VIEW public.view_vande_summary IS 'View tổng hợp thống kê về vấn đề (số phản ánh, tương tác, thời gian xử lý)';


-- =====================================================
-- VIEW 3: VIEW_NEWSFEED
-- =====================================================
-- Mục đích: View cho News Feed (phản ánh công khai)
CREATE OR REPLACE VIEW public.view_newsfeed AS
SELECT 
    p.maphananh,
    p.tieude,
    p.mota,
    p.loaiphananh,
    p.like_count,
    p.comment_count,
    p.view_count,
    p.thoigiantao,
    
    -- Thông tin người đăng
    p.cccd,
    n.name AS nguoi_dang,
    n.avatar_url,
    
    -- Địa chỉ
    d.xaphuong,
    d.chitiet AS diachi,
    
    -- Vấn đề
    v.tenvande,
    v.trangthai AS trangthai_vande,
    
    -- Tệp đính kèm
    t.duongdan AS hinh_anh,
    
    -- Điểm "hot" (để sắp xếp)
    (p.like_count * 2 + p.comment_count * 3 + p.view_count * 0.1) AS hot_score

FROM public.phananh p
INNER JOIN public.nguoidung n ON p.cccd = n.cccd
LEFT JOIN public.diachi d ON p.madiachi = d.madiachi
LEFT JOIN public.vande v ON p.mavande = v.mavande
LEFT JOIN public.tepdinhkem t ON p.matepdinhkem = t.matepdinhkem
WHERE p.is_public = TRUE;

COMMENT ON VIEW public.view_newsfeed IS 'View cho News Feed - chỉ phản ánh công khai với hot score';


-- =====================================================
-- VIEW 4: VIEW_THONGBAO_CHUA_DOC
-- =====================================================
-- Mục đích: Thông báo chưa đọc của người dùng
CREATE OR REPLACE VIEW public.view_thongbao_chua_doc AS
SELECT 
    tn.mathongbao_nguoidung,
    tn.cccd,
    tn.noidung,
    tn.loai,
    tn.thoigian,
    tn.mavande,
    tn.maphananh,
    
    -- Thông tin vấn đề (nếu có)
    v.tenvande,
    
    -- Thông tin phản ánh (nếu có)
    p.tieude AS tieude_phananh

FROM public.thongbao_nguoidung tn
LEFT JOIN public.vande v ON tn.mavande = v.mavande
LEFT JOIN public.phananh p ON tn.maphananh = p.maphananh
WHERE tn.trangthai_doc = FALSE;

COMMENT ON VIEW public.view_thongbao_chua_doc IS 'View thông báo chưa đọc của người dùng';


-- =====================================================
-- INDEXES BỔ SUNG
-- =====================================================

-- Index cho box chat và tin nhắn
CREATE INDEX IF NOT EXISTS idx_boxchat_maphananh_cccd 
    ON public.boxchat(maphananh, cccd_nguoidan);

CREATE INDEX IF NOT EXISTS idx_tinnhan_thoigiangui 
    ON public.tinnhan(thoigiangui DESC);

-- Index cho bình luận
CREATE INDEX IF NOT EXISTS idx_binhluan_maphananh_thoigian 
    ON public.binhluan(maphananh, thoigian DESC);

CREATE INDEX IF NOT EXISTS idx_binhluan_parent_id 
    ON public.binhluan(parent_id) 
    WHERE parent_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_binhluan_is_hidden 
    ON public.binhluan(is_hidden, maphananh) 
    WHERE is_hidden = FALSE;

-- Index cho like_post
CREATE INDEX IF NOT EXISTS idx_like_post_cccd 
    ON public.like_post(cccd);

CREATE INDEX IF NOT EXISTS idx_like_post_thoigian 
    ON public.like_post(thoigian DESC);

-- Index cho thống kê theo thời gian
CREATE INDEX IF NOT EXISTS idx_phananh_created_date 
    ON public.phananh(DATE(thoigiantao));

CREATE INDEX IF NOT EXISTS idx_vande_created_date 
    ON public.vande(DATE(ngaytao));

-- Partial index cho phản ánh chưa gộp vào vấn đề
CREATE INDEX IF NOT EXISTS idx_phananh_chua_gop 
    ON public.phananh(thoigiantao DESC) 
    WHERE mavande IS NULL;

COMMIT;

-- =====================================================
-- THÔNG BÁO HOÀN THÀNH
-- =====================================================
DO $$
DECLARE
    view_count INTEGER;
    index_count INTEGER;
BEGIN
    -- Đếm số views đã tạo
    SELECT COUNT(*) INTO view_count
    FROM information_schema.views
    WHERE table_schema = 'public'
    AND table_name LIKE 'view_%';
    
    -- Đếm số indexes
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'public'
    AND indexname LIKE 'idx_%';
    
    RAISE NOTICE '═══════════════════════════════════════════════';
    RAISE NOTICE '✓ Đã tạo 4 views tổng hợp:';
    RAISE NOTICE '  - view_phananh_full (thông tin đầy đủ)';
    RAISE NOTICE '  - view_vande_summary (thống kê vấn đề)';
    RAISE NOTICE '  - view_newsfeed (news feed công khai)';
    RAISE NOTICE '  - view_thongbao_chua_doc (thông báo chưa đọc)';
    RAISE NOTICE '✓ Đã tạo 9 indexes bổ sung cho performance';
    RAISE NOTICE '✓ Tổng số views hiện có: %', view_count;
    RAISE NOTICE '✓ Tổng số indexes hiện có: %', index_count;
    RAISE NOTICE '═══════════════════════════════════════════════';
END $$;
