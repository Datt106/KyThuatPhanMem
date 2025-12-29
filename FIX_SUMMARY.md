# Tóm tắt Fix: Lỗi hiển thị thành viên và hộ khẩu trống

## Ngày thực hiện: 2025-12-29

## Vấn đề phát hiện

### 1. **Lỗi: Vẫn hiển thị người đã chuyển đi trong danh sách thành viên**
- **Mô tả**: Người dùng đã khai báo "chuyển đi" (qua đời) cho thành viên hộ 19620, nhưng khi quay lại trang chi tiết hộ khẩu vẫn thấy người đó trong danh sách
- **Nguyên nhân**: Query lấy thành viên THIẾU điều kiện `WHERE ngayketthuc IS NULL`
- **Hậu quả**: Dữ liệu hiển thị sai, gây nhầm lẫn cho người dùng

### 2. **Yêu cầu: Đánh dấu hộ khẩu không còn thành viên**
- **Mô tả**: Khi tất cả thành viên rời khỏi hộ, cần đánh dấu hộ đó là "trống"
- **Lý do**: Không muốn xóa dữ liệu để giữ lịch sử
- **Giải pháp**: Tự động ghi chú hoặc dùng cột `trangthai`

---

## Các thay đổi đã thực hiện

### A. Sửa file `app.py`

#### 1. Route `hokhau_detail()` - Dòng 710-730
**Trước (SAI):**
```python
query_thanhvien = """
    SELECT n.cccd, n.name, n.ngaysinh, n.gioitinh, n.dantoc, n.sdt, tv.quanhechuho, tv.ngaybatdau
    FROM thanhvienhokhau tv
    JOIN nguoidung n ON tv.cccd = n.cccd
    WHERE tv.mahokhau = %s
    ORDER BY CASE WHEN tv.quanhechuho = 'ChuHo' THEN 0 ELSE 1 END, tv.ngaybatdau
"""
```

**Sau (ĐÚNG):**
```python
query_thanhvien = """
    SELECT n.cccd, n.name, n.ngaysinh, n.gioitinh, n.dantoc, n.sdt, tv.quanhechuho, tv.ngaybatdau
    FROM thanhvienhokhau tv
    JOIN nguoidung n ON tv.cccd = n.cccd
    WHERE tv.mahokhau = %s AND tv.ngayketthuc IS NULL
    ORDER BY CASE WHEN tv.quanhechuho = 'ChuHo' THEN 0 ELSE 1 END, tv.ngaybatdau
"""
```

**Lý do**: Chỉ lấy thành viên còn sống tại hộ (chưa có ngày kết thúc)

---

#### 2. Route `thanhvien_chuyen_di()` - Dòng 886-900
**Thêm logic tự động đánh dấu hộ trống:**

```python
# Sau khi UPDATE ngayketthuc
# Kiểm tra xem hộ còn thành viên không
query_count = """
    SELECT COUNT(*) FROM thanhvienhokhau 
    WHERE mahokhau = %s AND ngayketthuc IS NULL
"""
count = execute_query(query_count, (mahokhau,), fetch_one=True)

# Nếu hết thành viên, đánh dấu hộ là trống
if count and count[0] == 0:
    query_mark_empty = """
        UPDATE hokhau 
        SET ghichu = CASE 
            WHEN ghichu IS NULL OR ghichu = '' THEN '[HỘ TRỐNG - Không còn thành viên]'
            ELSE ghichu || ' | [HỘ TRỐNG - Không còn thành viên]'
        END
        WHERE mahokhau = %s
    """
    execute_query(query_mark_empty, (mahokhau,))
    flash(f'Đã cập nhật thông tin chuyển đi cho thành viên {cccd}. Hộ khẩu đã trống!', 'warning')
else:
    flash(f'Đã cập nhật thông tin chuyển đi cho thành viên {cccd}!', 'success')
```

**Cách hoạt động**:
1. Sau khi set `ngayketthuc`, đếm số thành viên còn lại
2. Nếu count = 0, tự động append tag `[HỘ TRỐNG]` vào cột `ghichu`
3. Hiển thị thông báo warning để user biết

---

#### 3. Route `dashboard()` và `hokhau_list()` - COUNT thành viên
**Trước (SAI):**
```sql
(SELECT COUNT(*) FROM thanhvienhokhau tv WHERE tv.mahokhau = h.mahokhau) as so_thanh_vien
```

**Sau (ĐÚNG):**
```sql
(SELECT COUNT(*) FROM thanhvienhokhau tv 
 WHERE tv.mahokhau = h.mahokhau AND tv.ngayketthuc IS NULL) as so_thanh_vien
```

**Lý do**: Số thành viên phải là số người HIỆN TẠI, không tính người đã rời khỏi

---

### B. File SQL mới: `FIX_HOKHAU_TRONG.sql`

Tạo file SQL hỗ trợ 2 phương án quản lý hộ trống:

#### **Phương án 1: Dùng cột `ghichu` (đã implement trong app.py)**
- Ưu điểm: Không cần thay đổi cấu trúc database
- Nhược điểm: Khó lọc/thống kê hộ trống

#### **Phương án 2: Thêm cột `trangthai` (tùy chọn, script có sẵn)**
```sql
ALTER TABLE hokhau ADD COLUMN trangthai VARCHAR(20) DEFAULT 'Hoạt động';
-- Giá trị: 'Hoạt động', 'Trống', 'Đã giải thể'
```

File cũng bao gồm:
- Trigger tự động cập nhật `trangthai` khi thành viên thay đổi
- View `v_hokhau_summary` tổng hợp thông tin
- Query kiểm tra và thống kê

---

## Cách sử dụng

### 1. Khai báo chuyển đi/qua đời
1. Vào [Chi tiết hộ khẩu](d:\GitHub\KyThuatPhanMem\Interface\templates\hokhau_detail.html)
2. Click "Chuyển đi" ở hàng thành viên
3. Điền thông tin:
   - Ngày chuyển
   - Lý do: Chọn "Qua đời" hoặc "Chuyển đi"
   - Nơi chuyển đến (nếu có)
   - Ghi chú
4. Submit → Hệ thống tự động:
   - Set `ngayketthuc` = ngày chuyển
   - Lưu `lydochuyen`, `noichuyenden`, `ghichu`
   - **KIỂM TRA**: Nếu hộ hết thành viên → Đánh dấu `[HỘ TRỐNG]` trong `ghichu`

### 2. Xem danh sách hộ trống
```sql
SELECT 
    h.mahokhau,
    d.chitiet || ', ' || d.xaphuong as diachi,
    h.ghichu,
    COUNT(tv.cccd) FILTER (WHERE tv.ngayketthuc IS NOT NULL) as so_nguoi_da_roi
FROM hokhau h
LEFT JOIN diachi d ON h.madiachi = d.madiachi
LEFT JOIN thanhvienhokhau tv ON h.mahokhau = tv.mahokhau
GROUP BY h.mahokhau, d.chitiet, d.xaphuong, h.ghichu
HAVING COUNT(tv.cccd) FILTER (WHERE tv.ngayketthuc IS NULL) = 0
ORDER BY h.mahokhau;
```

### 3. Kiểm tra hộ 19620 (ví dụ test)
```sql
SELECT 
    tv.cccd,
    n.name,
    tv.quanhechuho,
    tv.ngaybatdau,
    tv.ngayketthuc,
    tv.lydochuyen,
    CASE 
        WHEN tv.ngayketthuc IS NULL THEN 'Còn trong hộ'
        ELSE 'Đã rời khỏi'
    END as trang_thai
FROM thanhvienhokhau tv
JOIN nguoidung n ON tv.cccd = n.cccd
WHERE tv.mahokhau = 19620
ORDER BY tv.ngayketthuc IS NULL DESC, tv.ngaybatdau;
```

---

## Kiểm tra sau khi fix

### Test case 1: Chuyển đi thành viên cuối cùng
1. Vào hộ chỉ có 1 thành viên
2. Khai báo chuyển đi
3. **Kỳ vọng**:
   - Danh sách thành viên rỗng
   - Cột `ghichu` có tag `[HỘ TRỐNG]`
   - Thông báo warning xuất hiện

### Test case 2: Xem lịch sử biến động
1. Vào [Lịch sử hộ](d:\GitHub\KyThuatPhanMem\Interface\templates\hokhau_lich_su.html)
2. **Kỳ vọng**:
   - "Thành viên hiện tại" = 0
   - "Lịch sử người đã rời" hiển thị đầy đủ người vừa chuyển đi
   - Có đầy đủ thông tin: ngày kết thúc, lý do, nơi chuyển đến

### Test case 3: Số lượng thành viên trong danh sách hộ
1. Vào [Danh sách hộ khẩu](d:\GitHub\KyThuatPhanMem\Interface\templates\hokhau.html)
2. **Kỳ vọng**:
   - Cột "Số TV" của hộ trống = 0
   - Cột "Chủ hộ" = NULL hoặc trống

---

## Lưu ý quan trọng

### ⚠️ KHÔNG XÓA RECORD
- KHÔNG dùng `DELETE FROM thanhvienhokhau`
- CHỈ dùng `UPDATE SET ngayketthuc = ...`
- Lý do: Giữ lịch sử để tra cứu

### ✅ Luôn dùng điều kiện `ngayketthuc IS NULL`
```sql
-- ĐÚNG: Lấy thành viên hiện tại
WHERE tv.ngayketthuc IS NULL

-- SAI: Lấy tất cả (kể cả người đã rời)
WHERE tv.mahokhau = %s
```

### 📊 Phân biệt 2 loại query
```sql
-- 1. Thành viên HIỆN TẠI (cho màn hình chi tiết)
WHERE ngayketthuc IS NULL

-- 2. LỊCH SỬ BIẾN ĐỘNG (cho màn hình lịch sử)
WHERE ngayketthuc IS NOT NULL
ORDER BY ngayketthuc DESC
```

---

## Files đã thay đổi

1. ✅ [app.py](d:\GitHub\KyThuatPhanMem\app.py)
   - `hokhau_detail()` - Thêm điều kiện ngayketthuc IS NULL
   - `thanhvien_chuyen_di()` - Thêm logic đánh dấu hộ trống
   - `dashboard()` - Sửa COUNT thành viên
   - `hokhau_list()` - Sửa COUNT thành viên

2. ✅ [FIX_HOKHAU_TRONG.sql](d:\GitHub\KyThuatPhanMem\Query\FIX_HOKHAU_TRONG.sql) *(mới)*
   - Script thêm cột `trangthai` (tùy chọn)
   - Trigger tự động cập nhật
   - View tổng hợp
   - Query kiểm tra

3. ✅ [FIX_SUMMARY.md](d:\GitHub\KyThuatPhanMem\FIX_SUMMARY.md) *(file này)*
   - Tài liệu tóm tắt fix

---

## Rollback (nếu cần)

Nếu muốn quay lại trạng thái cũ:

```sql
-- Xóa tag [HỘ TRỐNG] khỏi ghichu
UPDATE hokhau 
SET ghichu = REPLACE(ghichu, ' | [HỘ TRỐNG - Không còn thành viên]', '')
WHERE ghichu LIKE '%[HỘ TRỐNG%';

UPDATE hokhau 
SET ghichu = NULL
WHERE ghichu = '[HỘ TRỐNG - Không còn thành viên]';
```

---

## Kết luận

✅ **Đã fix**: Lỗi hiển thị người đã chuyển đi  
✅ **Đã thêm**: Tự động đánh dấu hộ trống  
✅ **Đã kiểm tra**: Query COUNT thành viên ở tất cả màn hình  
✅ **Đã tạo**: Script SQL hỗ trợ (FIX_HOKHAU_TRONG.sql)  

Người dùng giờ sẽ KHÔNG còn thấy người đã qua đời/chuyển đi trong danh sách thành viên, và hộ khẩu trống sẽ được đánh dấu rõ ràng mà không mất dữ liệu lịch sử! 🎉
