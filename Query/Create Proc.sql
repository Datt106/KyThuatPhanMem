-- ================================================================
-- THỦ TỤC: Thêm phản ánh mới của người dân
-- Tự động kiểm tra CCCD, tạo phản ánh mới và box chat tương ứng
-- ================================================================
CREATE OR REPLACE PROCEDURE sp_ThemPhanAnh(
    p_cccd CHAR(12),
    p_madiadi INT,
    p_loaiphananh VARCHAR(100),
    p_mota TEXT,
    p_matdinhkem INT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_maphananh INT;
BEGIN
    -- Kiểm tra người gửi tồn tại
    IF NOT EXISTS (SELECT 1 FROM NguoiDung WHERE CCCD = p_cccd) THEN
        RAISE EXCEPTION 'Người dùng với CCCD % không tồn tại', p_cccd;
    END IF;

    -- Thêm phản ánh mới
    INSERT INTO PhanAnh (CCCD, MaDiaChi, LoaiPhanAnh, MoTa, MaTepDinhKem, TrangThaiPhanAnh, NgayTao)
    VALUES (p_cccd, p_madiadi, p_loaiphananh, p_mota, p_matdinhkem, 'ChuaXuLy', CURRENT_TIMESTAMP)
    RETURNING MaPhanAnh INTO v_maphananh;

    -- Tạo box chat tương ứng để người dân và cán bộ trao đổi
    INSERT INTO BoxChat (MaPhanAnh)
    VALUES (v_maphananh);

    RAISE NOTICE 'Đã thêm phản ánh mã % và tạo box chat tương ứng.', v_maphananh;
END;
$$;

COMMENT ON PROCEDURE sp_ThemPhanAnh IS 'Thêm phản ánh mới, kiểm tra CCCD và tạo BoxChat tự động.';

-- Gọi thử:
-- CALL sp_ThemPhanAnh('012345678901', 1, 'Môi trường', 'Có rác thải chưa thu gom', NULL);



-- ================================================================
-- THỦ TỤC: Cập nhật trạng thái phản ánh
-- Cho phép cập nhật giữa 3 trạng thái: ChuaXuLy / DangXuLy / DaXuLy
-- ================================================================
CREATE OR REPLACE PROCEDURE sp_CapNhatTrangThaiPhanAnh(
    p_maphananh INT,
    p_trangthai VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Kiểm tra trạng thái hợp lệ
    IF p_trangthai NOT IN ('ChuaXuLy', 'DangXuLy', 'DaXuLy') THEN
        RAISE EXCEPTION 'Trạng thái không hợp lệ: %', p_trangthai;
    END IF;

    -- Cập nhật
    UPDATE PhanAnh
    SET TrangThaiPhanAnh = p_trangthai
    WHERE MaPhanAnh = p_maphananh;

    IF NOT FOUND THEN
        RAISE NOTICE 'Không tìm thấy phản ánh với mã %', p_maphananh;
    ELSE
        RAISE NOTICE 'Đã cập nhật trạng thái phản ánh % thành %', p_maphananh, p_trangthai;
    END IF;
END;
$$;

COMMENT ON PROCEDURE sp_CapNhatTrangThaiPhanAnh IS 'Cập nhật trạng thái phản ánh: Chưa xử lý / Đang xử lý / Đã xử lý.';

-- Gọi thử:
-- CALL sp_CapNhatTrangThaiPhanAnh(1, 'DangXuLy');



-- ================================================================
-- THỦ TỤC: Thêm tin nhắn vào box chat
-- Kiểm tra box tồn tại & người gửi có thật, sau đó thêm tin nhắn
-- ================================================================
CREATE OR REPLACE PROCEDURE sp_ThemTinNhan(
    p_maboxchat INT,
    p_nguoigui CHAR(12),
    p_noidung TEXT,
    p_matdinhkem INT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Kiểm tra box chat tồn tại
    IF NOT EXISTS (SELECT 1 FROM BoxChat WHERE MaBoxChat = p_maboxchat) THEN
        RAISE EXCEPTION 'Box chat % không tồn tại', p_maboxchat;
    END IF;

    -- Kiểm tra người gửi tồn tại
    IF NOT EXISTS (SELECT 1 FROM NguoiDung WHERE CCCD = p_nguoigui) THEN
        RAISE EXCEPTION 'Người gửi với CCCD % không tồn tại', p_nguoigui;
    END IF;

    -- Thêm tin nhắn
    INSERT INTO TinNhan (MaBoxChat, NguoiGui, NoiDung, MaTepDinhKem, ThoiGianGui, DaDoc)
    VALUES (p_maboxchat, p_nguoigui, p_noidung, p_matdinhkem, CURRENT_TIMESTAMP, FALSE);

    RAISE NOTICE 'Đã thêm tin nhắn mới vào box chat %', p_maboxchat;
END;
$$;

COMMENT ON PROCEDURE sp_ThemTinNhan IS 'Thêm tin nhắn mới vào BoxChat (kiểm tra tồn tại trước khi chèn).';

-- Gọi thử:
-- CALL sp_ThemTinNhan(1, '012345678901', 'Xin chào, tôi đang xử lý phản ánh này', NULL);
