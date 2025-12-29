# Hướng dẫn: Chức năng Lịch sử Biến động Nhân khẩu

## Tổng quan
Chức năng lịch sử biến động nhân khẩu giúp theo dõi tất cả các thay đổi về thành viên trong hộ khẩu, bao gồm:
- Người rời khỏi hộ (chuyển đi, qua đời, tách hộ...)
- Lịch sử thay đổi chủ hộ
- Thông tin chi tiết về lý do và thời gian biến động

## Cấu trúc Database

### 1. Bảng `thanhvienhokhau`
Lưu thông tin thành viên hiện tại và lịch sử:

```sql
- mahokhau (PK)
- cccd (PK)
- quanhechuho
- ngaybatdau
- ngayketthuc          -- NULL = còn ở hộ, có giá trị = đã rời khỏi
- lydochuyen           -- Lý do: "Chuyển đi", "Qua đời", "Tách hộ"...
- noichuyenden         -- Địa chỉ chuyển đến (nếu có)
- ghichu               -- Ghi chú thêm
```

### 2. Bảng `lichsuthaydoichuho`
Lưu lịch sử thay đổi chủ hộ:

```sql
- malichsu (PK, SERIAL)
- mahokhau (FK → hokhau)
- cccd_cu (FK → nguoidung)     -- Chủ hộ cũ
- cccd_moi (FK → nguoidung)    -- Chủ hộ mới
- ngaythaydoi
- lydothaydoi
- noidung
- nguoithuchien (FK → nguoidung)
```

## Truy cập chức năng

1. **Từ danh sách hộ khẩu**: Click vào "Chi tiết" → Nút "Lịch sử"
2. **Từ chi tiết hộ khẩu**: Click nút "Lịch sử" ở góc trên bên phải

URL: `/hokhau/<mahokhau>/lich-su`

## Các thành phần hiển thị

### 1. Thông tin hộ khẩu
- Mã hộ khẩu
- Địa chỉ
- Ngày cấp
- Số thành viên hiện tại

### 2. Thành viên hiện tại
Danh sách những người đang sinh sống tại hộ:
- CCCD
- Họ tên
- Ngày sinh
- Giới tính
- Quan hệ với chủ hộ
- Ngày bắt đầu sinh sống

### 3. Lịch sử thay đổi chủ hộ
Timeline các lần đổi chủ hộ (nếu có):
- Ngày thay đổi
- Chủ hộ cũ → Chủ hộ mới
- Lý do thay đổi
- Nội dung chi tiết
- Người thực hiện

### 4. Lịch sử người đã rời khỏi hộ
Timeline các biến động (sắp xếp theo ngày kết thúc):
- Thông tin cá nhân (CCCD, họ tên, ngày sinh)
- Ngày bắt đầu - Ngày kết thúc
- Quan hệ với chủ hộ
- Lý do chuyển đi
- Nơi chuyển đến
- Ghi chú

## Cách ghi nhận biến động

### A. Chuyển thành viên đi nơi khác
Route: `/thanhvien/chuyen-di/<mahokhau>/<cccd>`

1. Vào chi tiết hộ khẩu
2. Click "Chuyển đi" ở hàng thành viên cần chuyển
3. Điền thông tin:
   - Ngày chuyển đi
   - Lý do (Chuyển công tác, Kết hôn, Du học...)
   - Nơi chuyển đến
   - Ghi chú (nếu có)
4. Hệ thống tự động:
   - Set `ngayketthuc` = ngày chuyển đi
   - Lưu `lydochuyen`, `noichuyenden`, `ghichu`
   - Cập nhật số lượng thành viên

### B. Thay đổi chủ hộ
Route: `/hokhau/doi-chu-ho/<mahokhau>`

1. Vào chi tiết hộ khẩu
2. Click nút "Đổi chủ hộ"
3. Chọn chủ hộ mới từ danh sách thành viên
4. Điền thông tin:
   - Ngày thay đổi
   - Lý do (Qua đời, Chuyển đi, Tự nguyện...)
   - Nội dung chi tiết
5. Hệ thống tự động:
   - Đổi `quanhechuho` của chủ hộ cũ → "Thành viên"
   - Đổi `quanhechuho` của người mới → "Chủ hộ"
   - Lưu vào bảng `lichsuthaydoichuho`

### C. Tách hộ
Route: `/hokhau/tach-ho/<mahokhau>`

1. Vào chi tiết hộ khẩu
2. Click nút "Tách hộ"
3. Chọn các thành viên sẽ tách ra
4. Chỉ định chủ hộ mới
5. Nhập địa chỉ hộ mới
6. Hệ thống tự động:
   - Tạo hộ khẩu mới
   - Set `ngayketthuc` cho các thành viên trong hộ cũ
   - Set `lydochuyen` = "Tách hộ"
   - Chuyển các thành viên sang hộ mới

## Truy vấn quan trọng

### Lấy thành viên hiện tại
```sql
SELECT n.cccd, n.name, n.ngaysinh, n.gioitinh, tv.quanhechuho, tv.ngaybatdau
FROM thanhvienhokhau tv
JOIN nguoidung n ON tv.cccd = n.cccd
WHERE tv.mahokhau = ? AND tv.ngayketthuc IS NULL
ORDER BY 
    CASE WHEN tv.quanhechuho = 'Chủ hộ' THEN 0 ELSE 1 END,
    tv.ngaybatdau;
```

### Lấy lịch sử người đã rời khỏi hộ
```sql
SELECT 
    n.cccd, n.name, n.ngaysinh,
    tv.quanhechuho, tv.ngaybatdau, tv.ngayketthuc,
    tv.lydochuyen, tv.noichuyenden, tv.ghichu
FROM thanhvienhokhau tv
JOIN nguoidung n ON tv.cccd = n.cccd
WHERE tv.mahokhau = ? AND tv.ngayketthuc IS NOT NULL
ORDER BY tv.ngayketthuc DESC;
```

### Lấy lịch sử đổi chủ hộ
```sql
SELECT 
    ls.ngaythaydoi,
    n1.name as ten_cu,
    n2.name as ten_moi,
    ls.lydothaydoi,
    ls.noidung,
    ls.nguoithuchien
FROM lichsuthaydoichuho ls
LEFT JOIN nguoidung n1 ON ls.cccd_cu = n1.cccd
LEFT JOIN nguoidung n2 ON ls.cccd_moi = n2.cccd
WHERE ls.mahokhau = ?
ORDER BY ls.ngaythaydoi DESC;
```

## Quyền truy cập

- **Cán bộ/Quản lý**: Xem đầy đủ lịch sử của tất cả hộ khẩu
- **Người dân**: Chỉ xem lịch sử của hộ khẩu mình đang sinh sống (đã được giới hạn ở route)

## Fix đã thực hiện (2025-12-29)

### 1. Sửa lỗi hiển thị giới tính
**Vấn đề**: Nữ luôn hiện N/A
**Nguyên nhân**: Template so sánh `tv[3] == 'Nam'` và `tv[3] == 'Nữ'` nhưng database lưu là `'nam'` và `'nu'` (không dấu, lowercase)
**Giải pháp**: Đổi tất cả so sánh thành `tv[3]|lower == 'nam'` và `tv[3]|lower == 'nu'`

**Files đã sửa**:
- `hokhau_detail.html`
- `hokhau_doi_chu_ho.html`
- `hokhau_lich_su.html`
- `hokhau_tach_ho.html`

### 2. Đảm bảo cấu trúc database
Tạo file `FIX_LICHSU_BIENDONG.sql` để:
- Thêm cột `lydochuyen`, `noichuyenden`, `ghichu` vào `thanhvienhokhau` (nếu chưa có)
- Tạo bảng `lichsuthaydoichuho` (nếu chưa có)
- Tạo các index tối ưu
- Thêm comments

## Lưu ý quan trọng

1. **Không xóa record**: Khi thành viên rời khỏi hộ, KHÔNG xóa record mà chỉ set `ngayketthuc` để giữ lịch sử
2. **Kiểm tra NULL**: Luôn filter `WHERE ngayketthuc IS NULL` khi lấy thành viên hiện tại
3. **Cascade delete**: Khi xóa hộ khẩu, tất cả lịch sử sẽ bị xóa theo (ON DELETE CASCADE)
4. **Giới tính**: Database lưu 'nam'/'nu' (không dấu), template hiển thị 'Nam'/'Nữ' (có dấu)

## Kiểm tra hoạt động

Chạy query sau để xem dữ liệu:

```sql
-- Xem hộ khẩu có lịch sử biến động
SELECT 
    h.mahokhau,
    COUNT(CASE WHEN tv.ngayketthuc IS NULL THEN 1 END) as hien_tai,
    COUNT(CASE WHEN tv.ngayketthuc IS NOT NULL THEN 1 END) as da_roi
FROM hokhau h
LEFT JOIN thanhvienhokhau tv ON h.mahokhau = tv.mahokhau
GROUP BY h.mahokhau
HAVING COUNT(CASE WHEN tv.ngayketthuc IS NOT NULL THEN 1 END) > 0;
```
