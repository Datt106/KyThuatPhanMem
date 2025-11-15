CREATE OR REPLACE VIEW v_ThongTinNguoiDung AS
SELECT 
    nd.CCCD,
    nd.User_Name,
    nd.SDT,
    nd.NgaySinh,
    nd.GioiTinh,
    nd.VaiTro,
    nd.BaoMatThongTin,
    dc.Tinh,
    dc.XaPhuong,
    dc.ChiTiet,
    dnd.LoaiDiaChi
FROM 
    NguoiDung nd
    LEFT JOIN DiaChiNguoiDung dnd ON nd.CCCD = dnd.CCCD
    LEFT JOIN DiaChi dc ON dnd.MaDiaChi = dc.MaDiaChi;
COMMENT ON VIEW v_ThongTinNguoiDung IS 'Gộp thông tin người dùng và các địa chỉ liên quan.';

CREATE OR REPLACE VIEW v_PhanAnhChiTiet AS
SELECT 
    pa.MaPhanAnh,
    nd.User_Name AS NguoiPhanAnh,
    dc.Tinh,
    dc.XaPhuong,
    dc.ChiTiet AS DiaChiPhanAnh,
    pa.LoaiPhanAnh,
    pa.TrangThaiPhanAnh,
    pa.MoTa,
    td.DuongDan AS TepDinhKem
FROM 
    PhanAnh pa
    LEFT JOIN NguoiDung nd ON pa.CCCD = nd.CCCD
    LEFT JOIN DiaChi dc ON pa.MaDiaChi = dc.MaDiaChi
    LEFT JOIN TepDinhKem td ON pa.MaTepDinhKem = td.MaTepDinhKem;
COMMENT ON VIEW v_PhanAnhChiTiet IS 'Hiển thị thông tin chi tiết của từng phản ánh, bao gồm người gửi, địa chỉ và tệp đính kèm.';

CREATE OR REPLACE VIEW v_PhanAnhChuaXuLy AS
SELECT *
FROM v_PhanAnhChiTiet
WHERE TrangThaiPhanAnh = 'ChuaXuLy';
COMMENT ON VIEW v_PhanAnhChuaXuLy IS 'Lọc danh sách các phản ánh chưa được xử lý.';

CREATE OR REPLACE VIEW v_TinNhanChiTiet AS
SELECT 
    tn.TinNhanID,
    bc.MaBoxChat,
    pa.MaPhanAnh,
    tn.NguoiGui,
    nd.User_Name AS TenNguoiGui,
    tn.NoiDung,
    tn.ThoiGianGui,
    tn.DaDoc,
    td.DuongDan AS TepDinhKem
FROM 
    TinNhan tn
    LEFT JOIN BoxChat bc ON tn.MaBoxChat = bc.MaBoxChat
    LEFT JOIN PhanAnh pa ON bc.MaPhanAnh = pa.MaPhanAnh
    LEFT JOIN NguoiDung nd ON tn.NguoiGui = nd.CCCD
    LEFT JOIN TepDinhKem td ON tn.MaTepDinhKem = td.MaTepDinhKem;
COMMENT ON VIEW v_TinNhanChiTiet IS 'Gộp tin nhắn với thông tin người gửi, box chat và tệp đính kèm.';

CREATE OR REPLACE VIEW v_ThongKePhanAnh AS
SELECT 
    TrangThaiPhanAnh,
    COUNT(*) AS SoLuongPhanAnh
FROM 
    PhanAnh
GROUP BY 
    TrangThaiPhanAnh;
COMMENT ON VIEW v_ThongKePhanAnh IS 'Thống kê tổng số phản ánh theo từng trạng thái (Chưa xử lý, Đang xử lý, Đã xử lý).';
