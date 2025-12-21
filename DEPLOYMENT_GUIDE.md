# Hướng Dẫn Triển Khai Hệ Thống Quản Lý Hộ Khẩu

## Yêu cầu hệ thống

- Node.js 16+ 
- PostgreSQL 12+
- npm hoặc yarn

## Bước 1: Cài đặt Database

### 1.1 Tạo Database

```bash
# Kết nối PostgreSQL
psql -U postgres

# Tạo database
CREATE DATABASE QuanLiPhanAnh;

# Thoát psql
\q
```

### 1.2 Chạy Schema

```bash
# Kết nối vào database vừa tạo
psql -U postgres -d QuanLiPhanAnh

# Chạy file schema
\i backend/database/schema.sql

# Kiểm tra các bảng đã được tạo
\dt

# Thoát
\q
```

Bạn sẽ thấy các bảng sau:
- ho_khau
- nhan_khau
- chung_minh_thu
- tam_vang
- tam_tru
- lich_su_bien_dong
- nguoidung
- yeu_cau

## Bước 2: Cấu hình Backend

### 2.1 Cài đặt Dependencies

```bash
cd backend
npm install
```

### 2.2 Cấu hình Environment Variables

File `.env` đã có sẵn với cấu hình mặc định:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=admin
DB_NAME=QuanLiPhanAnh
JWT_SECRET=my_secret_key
REACT_APP_API_URL=http://localhost:5000
```

**Lưu ý**: Thay đổi `DB_PASSWORD` theo mật khẩu PostgreSQL của bạn.

### 2.3 Chạy Backend

```bash
# Development mode (tự động reload khi có thay đổi)
npm run dev

# Production mode
npm start
```

Server sẽ chạy tại: `http://localhost:5000`

### 2.4 Kiểm tra Backend

Mở browser và truy cập: `http://localhost:5000/test`

Bạn sẽ thấy: "Server is running!"

## Bước 3: Cấu hình Frontend

### 3.1 Cài đặt Dependencies

```bash
cd frontend
npm install
```

### 3.2 Cấu hình Environment Variables (nếu cần)

Tạo file `.env` trong thư mục frontend:

```env
VITE_API_URL=http://localhost:5000
```

### 3.3 Chạy Frontend

```bash
npm run dev
```

App sẽ chạy tại: `http://localhost:5173`

## Bước 4: Đăng nhập và Sử dụng

### 4.1 Tạo tài khoản Admin

Có 2 cách:

**Cách 1: Qua giao diện đăng ký**
- Truy cập: `http://localhost:5173/register`
- Điền thông tin và đăng ký
- Sau đó cập nhật role trong database:

```sql
UPDATE nguoidung SET vaitro = 'CanBo' WHERE cccd = 'YOUR_CCCD';
```

**Cách 2: Tạo trực tiếp trong database**

```sql
INSERT INTO nguoidung (cccd, name, sdt, ngaysinh, gioitinh, dantoc, vaitro, user_name, matkhau)
VALUES ('123456789', 'Admin User', '0123456789', '1990-01-01', 'Nam', 'Kinh', 'CanBo', 'admin', '123456');
```

### 4.2 Liên kết User với Nhân Khẩu (Optional)

Để sử dụng tính năng dashboard người dân, cần liên kết user với nhân khẩu:

```sql
-- Tìm ID của người dùng
SELECT id FROM nguoidung WHERE cccd = 'YOUR_CCCD';

-- Tìm ID nhân khẩu phù hợp (hoặc tạo mới)
SELECT id FROM nhan_khau WHERE ho_ten = 'TÊN CỦA BẠN';

-- Liên kết
UPDATE nguoidung SET id_nhan_khau = <ID_NHAN_KHAU> WHERE id = <ID_USER>;
```

### 4.3 Đăng nhập

**Người dân:**
- URL: `http://localhost:5173/login`
- Đăng nhập -> Chuyển đến `/dashboard`

**Quản lý (CanBo):**
- URL: `http://localhost:5173/login`
- Đăng nhập -> Chuyển đến `/admin/dashboard`

## Bước 5: Sử dụng hệ thống

### 5.1 Chức năng Người Dân

**Trang Dashboard** (`/dashboard`)
- Xem thông tin hộ khẩu
- Xem lịch sử yêu cầu
- Quick actions: Khai báo tạm vắng, tạm trú, tách hộ, sinh con

**Sổ Hộ Khẩu** (`/ho-khau-cua-toi`)
- Xem danh sách thành viên
- Xem chi tiết từng thành viên
- Thông tin CMND/CCCD

### 5.2 Chức năng Quản Lý

**Admin Dashboard** (`/admin/dashboard`)
- Thống kê tổng quan
- Yêu cầu chờ duyệt
- Biểu đồ phân bố dân số
- Quick links đến các trang quản lý

**Quản lý Hộ Khẩu** (API sẵn sàng, UI chưa có)
- Endpoint: `/api/ho-khau`
- CRUD operations
- Tách hộ

**Quản lý Nhân Khẩu** (API sẵn sàng, UI chưa có)
- Endpoint: `/api/nhan-khau`
- CRUD operations
- Khai sinh, khai tử

**Xử lý Yêu cầu** (API sẵn sàng, UI chưa có)
- Endpoint: `/api/yeu-cau`
- Duyệt/Từ chối yêu cầu

## API Endpoints

### Authentication
```
POST /api/auth/register - Đăng ký
POST /api/auth/login    - Đăng nhập
```

### Hộ Khẩu
```
GET    /api/ho-khau           - Danh sách
GET    /api/ho-khau/:id       - Chi tiết
POST   /api/ho-khau           - Tạo mới
PUT    /api/ho-khau/:id       - Cập nhật
DELETE /api/ho-khau/:id       - Xóa
POST   /api/ho-khau/:id/tach-ho - Tách hộ
```

### Nhân Khẩu
```
GET  /api/nhan-khau                    - Danh sách
GET  /api/nhan-khau/:id                - Chi tiết
POST /api/nhan-khau                    - Tạo mới
PUT  /api/nhan-khau/:id                - Cập nhật
POST /api/nhan-khau/:id/khai-tu        - Khai tử
POST /api/nhan-khau/:id/chuyen-di      - Chuyển đi
GET  /api/nhan-khau/thong-ke/tong-hop  - Thống kê
```

### Tạm Vắng
```
GET    /api/tam-vang     - Danh sách
GET    /api/tam-vang/:id - Chi tiết
POST   /api/tam-vang     - Đăng ký
PUT    /api/tam-vang/:id - Cập nhật
DELETE /api/tam-vang/:id - Xóa
```

### Tạm Trú
```
GET    /api/tam-tru                    - Danh sách
GET    /api/tam-tru/:id                - Chi tiết
POST   /api/tam-tru                    - Đăng ký
PUT    /api/tam-tru/:id                - Cập nhật
DELETE /api/tam-tru/:id                - Xóa
GET    /api/tam-tru/thong-ke/tong-hop  - Thống kê
```

### Yêu Cầu
```
GET    /api/yeu-cau                    - Danh sách
GET    /api/yeu-cau/:id                - Chi tiết
POST   /api/yeu-cau                    - Tạo mới
POST   /api/yeu-cau/:id/duyet          - Duyệt
POST   /api/yeu-cau/:id/tu-choi        - Từ chối
DELETE /api/yeu-cau/:id                - Xóa
GET    /api/yeu-cau/thong-ke/cho-duyet - Số chờ duyệt
```

### Thống Kê
```
GET /api/thong-ke/tong-quan           - Tổng quan (admin)
GET /api/thong-ke/nguoi-dan/:id       - Cá nhân
GET /api/thong-ke/lich-su-bien-dong   - Lịch sử
GET /api/thong-ke/loc                 - Thống kê theo filter
```

## Troubleshooting

### Lỗi kết nối Database

```
Error: connect ECONNREFUSED 127.0.0.1:5432
```

**Giải pháp:**
- Kiểm tra PostgreSQL đã chạy: `sudo service postgresql status`
- Kiểm tra port: `sudo netstat -plunt | grep postgres`
- Kiểm tra credentials trong `.env`

### Lỗi CORS

```
Access to fetch at 'http://localhost:5000' has been blocked by CORS policy
```

**Giải pháp:**
- Backend đã cấu hình CORS cho `http://localhost:5173`
- Nếu frontend chạy ở port khác, cập nhật trong `backend/server.js`

### Frontend không kết nối được API

**Giải pháp:**
- Kiểm tra backend đang chạy
- Kiểm tra URL trong code: `http://localhost:5000`
- Mở DevTools -> Network để xem lỗi cụ thể

### Token hết hạn

```
Token không hợp lệ
```

**Giải pháp:**
- Đăng xuất và đăng nhập lại
- Token có thời hạn 7 ngày

## Dữ liệu mẫu

Database schema đã bao gồm dữ liệu mẫu:
- 2 hộ khẩu
- 4 nhân khẩu
- Chủ hộ và quan hệ gia đình
- Lịch sử biến động

Để thêm dữ liệu mẫu khác, bạn có thể:
1. Sử dụng API endpoints
2. Thêm trực tiếp vào database qua SQL

## Bảo mật

### Trong môi trường Production

1. **Thay đổi JWT_SECRET:**
```env
JWT_SECRET=your_very_long_and_random_secret_key_here
```

2. **Sử dụng HTTPS**

3. **Cấu hình CORS chính xác:**
```javascript
app.use(cors({
  origin: "https://your-production-domain.com",
  credentials: true
}));
```

4. **Bật bcrypt cho password:**
Uncomment dòng này trong `authController.js`:
```javascript
const isMatch = await bcrypt.compare(matkhau, user.matkhau);
```

5. **Giới hạn request rate**

6. **Sử dụng environment variables**

## Tài liệu tham khảo

- [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) - Chi tiết implementation
- Database schema: `backend/database/schema.sql`
- API routes: `backend/src/routes/`
- Frontend components: `frontend/src/pages/`

## Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Console logs (browser DevTools)
2. Server logs (terminal chạy backend)
3. Database logs
4. Network tab trong DevTools

## Tính năng đang phát triển

- [ ] Các trang quản lý admin
- [ ] Form khai báo cho người dân
- [ ] Xuất Excel
- [ ] Charts/Graphs
- [ ] Email notifications
- [ ] File upload cho ảnh CMND
- [ ] Print sổ hộ khẩu
- [ ] Mobile responsive hoàn thiện
