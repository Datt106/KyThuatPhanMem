# Phản Ánh Detail Template - Data Structure Mapping

## Route: `/phananh/<int:maphananh>`
**File:** `app.py` (lines 2110-2215)

## Template: `phananh_detail.html`

### 1. Phananh Tuple (24 fields from main query)

```python
phananh[0]  = p.maphananh          # ID phản ánh
phananh[1]  = p.cccd               # CCCD người tạo
phananh[2]  = n.name               # Tên người tạo (nguoi_tao)
phananh[3]  = n.sdt                # SĐT người tạo
phananh[4]  = p.tieude             # Tiêu đề phản ánh
phananh[5]  = p.mota               # Mô tả/nội dung chi tiết
phananh[6]  = p.loaiphananh        # Loại phản ánh
phananh[7]  = p.trangthaiphananh   # Trạng thái (Mới, Đang xử lý, Đã xử lý, Đã từ chối)
phananh[8]  = p.is_public          # Công khai (True/False)
phananh[9]  = p.allow_comment      # Cho phép bình luận (True/False)
phananh[10] = p.like_count         # Số lượng likes
phananh[11] = p.comment_count      # Số lượng comments
phananh[12] = p.view_count         # Số lượng views
phananh[13] = p.thoigiantao        # Thời gian tạo (datetime)
phananh[14] = p.thoigianxuly       # Thời gian xử lý (datetime hoặc NULL)
phananh[15] = p.mavande            # Mã vấn đề (int hoặc NULL)
phananh[16] = v.tenvande           # Tên vấn đề (string hoặc NULL)
phananh[17] = v.phanloai           # Phân loại vấn đề
phananh[18] = v.trangthai          # Trạng thái vấn đề
phananh[19] = v.ketqua             # Kết quả xử lý vấn đề
phananh[20] = d.tinh               # Tỉnh/Thành phố
phananh[21] = d.xaphuong           # Xã/Phường
phananh[22] = d.chitiet            # Địa chỉ chi tiết
phananh[23] = t.duongdan           # Đường dẫn hình ảnh (comma-separated)
```

### 2. Comments List (8 fields per comment)

```python
comment[0] = b.id                  # ID bình luận
comment[1] = b.cccd_nguoidung      # CCCD người bình luận
comment[2] = n.name                # Tên người bình luận
comment[3] = n.avatar_url          # Avatar URL
comment[4] = b.noidung             # Nội dung bình luận
comment[5] = b.thoigian            # Thời gian bình luận (datetime)
comment[6] = b.parent_id           # ID comment cha (int hoặc NULL)
comment[7] = b.is_hidden           # Ẩn hay không (True/False)
```

### 3. Additional Variables

```python
user_liked     # Boolean - Người dùng hiện tại đã like chưa
nguoidung_name # String - Tên người tạo phản ánh (phananh[2])
vande_name     # String hoặc None - Tên vấn đề (phananh[16])
boxchat_id     # Int hoặc None - ID boxchat nếu có
```

## Template Features

### Display Sections
1. **Header Card**: Tiêu đề, trạng thái, người tạo, thời gian
2. **Content**: Mô tả, địa chỉ, hình ảnh đính kèm
3. **Engagement**: Like/Comment/View counts với action buttons
4. **Actions**: Edit/Delete (owner), Update Status (CanBo/QuanLy)
5. **Comments**: Danh sách bình luận với nested replies
6. **Sidebar**: 
   - Link vấn đề (nếu có)
   - Thông tin xử lý
   - Link chat box (nếu có)

### Role-Based Permissions
- **Owner (phananh[1] == session.user.cccd)**: Edit, Delete
- **CanBo/QuanLy**: Update status, Hide comments
- **All users**: View, Like (if public), Comment (if allowed)

### Related Routes Used
- `phananh_like` (POST) - Thêm like
- `phananh_unlike` (POST) - Bỏ like
- `phananh_edit` (GET/POST) - Chỉnh sửa phản ánh
- `phananh_delete` (POST) - Xóa phản ánh
- `comment_add` (POST) - Thêm bình luận/reply
- `comment_hide` (POST) - Ẩn bình luận
- `vande_detail` (GET) - Chi tiết vấn đề
- `chat_detail` (GET) - Mở chat box

## JavaScript Functions
- `showReplyForm(commentId)` - Hiển thị form trả lời
- `hideReplyForm(commentId)` - Ẩn form trả lời

## Query Optimizations
- LEFT JOINs for optional data (vande, diachi, tepdinhkem)
- Single query for phananh with all related info
- Separate query for comments with nguoidung names
- Filters hidden comments in query (is_hidden = FALSE)
- Orders comments DESC by time

## Status Badges
- **Mới**: `bg-secondary` (gray)
- **Đang xử lý**: `bg-warning` (yellow)
- **Đã xử lý**: `bg-success` (green)
- **Đã từ chối**: `bg-danger` (red)

## Privacy Rules
- Public phản ánh: Anyone can view, like, comment (if allowed)
- Private phản ánh: Only owner + CanBo/QuanLy can view
- Auto-increment view count on page load
