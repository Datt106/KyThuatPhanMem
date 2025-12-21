INSERT INTO NguoiDung (CCCD, Name, SDT, NgaySinh, GioiTinh, DanToc, VaiTro, User_Name, MatKhau)
VALUES
('038200000001', 'Nguyen Van Hung', '0911111111', '1985-05-12', 'Nam', 'Kinh', 'QuanLy', 'ql_hung', 'pass123'),
('038200000002', 'Tran Thi Mai', '0911111112', '1988-09-20', 'Nu', 'Kinh', 'QuanLy', 'ql_mai', 'pass123'),
('038200000003', 'Le Van Minh', '0911111113', '1990-03-18', 'Nam', 'Kinh', 'QuanLy', 'ql_minh', 'pass123'),
('038200000004', 'Pham Thi Hoa', '0911111114', '1987-07-08', 'Nu', 'Kinh', 'QuanLy', 'ql_hoa', 'pass123'),
('038200000005', 'Do Van Long', '0911111115', '1983-11-25', 'Nam', 'Kinh', 'QuanLy', 'ql_long', 'pass123'),
('038200000006', 'Bui Thi Lan', '0911111116', '1992-02-05', 'Nu', 'Kinh', 'QuanLy', 'ql_lan', 'pass123'),
('038200000007', 'Hoang Van Tuan', '0911111117', '1989-01-14', 'Nam', 'Kinh', 'QuanLy', 'ql_tuan', 'pass123'),
('038200000008', 'Vo Thi Huong', '0911111118', '1991-04-22', 'Nu', 'Kinh', 'QuanLy', 'ql_huong', 'pass123'),
('038200000009', 'Trinh Van Khoa', '0911111119', '1984-10-30', 'Nam', 'Kinh', 'QuanLy', 'ql_khoa', 'pass123'),
('038200000010', 'Nguyen Thi Yen', '0911111120', '1993-06-11', 'Nu', 'Kinh', 'QuanLy', 'ql_yen', 'pass123');

INSERT INTO DiaChiNguoiDung (MaDiaChi, CCCD, LoaiDiaChi, ThoiDiemXacNhan)
VALUES
(145, '038200000001', 'NoiLamViec', CURRENT_DATE),
(387, '038200000002', 'NoiLamViec', CURRENT_DATE),
(256, '038200000003', 'NoiLamViec', CURRENT_DATE),
(499, '038200000004', 'NoiLamViec', CURRENT_DATE),
(310, '038200000005', 'NoiLamViec', CURRENT_DATE),
(122, '038200000006', 'NoiLamViec', CURRENT_DATE),
(478, '038200000007', 'NoiLamViec', CURRENT_DATE),
(201, '038200000008', 'NoiLamViec', CURRENT_DATE),
(390, '038200000009', 'NoiLamViec', CURRENT_DATE),
(415, '038200000010', 'NoiLamViec', CURRENT_DATE);
