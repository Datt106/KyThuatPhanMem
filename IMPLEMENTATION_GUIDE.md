# Hệ Thống Quản Lý Hộ Khẩu - Household Management System

## Tổng quan dự án

Hệ thống quản lý hộ khẩu điện tử được thiết kế để quản lý thông tin hộ gia đình, nhân khẩu, tạm trú, tạm vắng và các biến động dân cư.

## Cấu trúc dự án

```
KyThuatPhanMem/
├── backend/
│   ├── database/
│   │   └── schema.sql          # Database schema với sample data
│   ├── src/
│   │   ├── config/
│   │   │   └── db.js           # Database connection
│   │   ├── controllers/
│   │   │   └── authController.js
│   │   ├── middlewares/
│   │   │   └── authMiddleware.js
│   │   └── routes/
│   │       ├── hokhau.js       # Household management APIs
│   │       ├── nhankhau.js     # Citizen management APIs
│   │       ├── tamvang.js      # Temporary absence APIs
│   │       ├── tamtru.js       # Temporary residence APIs
│   │       ├── yeucau.js       # Request approval workflow APIs
│   │       ├── thongke.js      # Statistics and reports APIs
│   │       ├── auth.js         # Authentication
│   │       ├── user.js         # User management
│   │       ├── profile.js      # User profile
│   │       ├── home.js         # Home/News
│   │       └── phananh.js      # Feedback
│   └── server.js               # Express server
│
└── frontend/
    └── src/
        ├── pages/
        │   ├── Dashboard/
        │   │   ├── ResidentDashboard.jsx    # Trang chủ người dân
        │   │   └── dashboard.css
        │   ├── Admin/
        │   │   ├── AdminDashboard.jsx       # Trang chủ quản lý
        │   │   └── AdminDashboard.css
        │   ├── Login/
        │   ├── Register/
        │   ├── Home/
        │   ├── Profile/
        │   └── Phananh/
        ├── components/
        │   ├── Navbar.jsx
        │   ├── Button.jsx
        │   └── InputField.jsx
        └── App.jsx
```

## Database Schema

### Các bảng chính

1. **ho_khau** - Quản lý sổ hộ khẩu
2. **nhan_khau** - Quản lý nhân khẩu (công dân)
3. **chung_minh_thu** - Giấy tờ tùy thân (CMND/CCCD)
4. **tam_vang** - Quản lý tạm vắng
5. **tam_tru** - Quản lý tạm trú
6. **lich_su_bien_dong** - Lịch sử thay đổi
7. **nguoidung** - Tài khoản người dùng
8. **yeu_cau** - Yêu cầu phê duyệt

### Cài đặt Database

```bash
# Kết nối PostgreSQL
psql -U postgres

# Tạo database
CREATE DATABASE QuanLiPhanAnh;

# Chạy schema
\c QuanLiPhanAnh
\i backend/database/schema.sql
```

## Backend APIs

### Authentication APIs (`/api/auth`)
- `POST /api/auth/register` - Đăng ký tài khoản
- `POST /api/auth/login` - Đăng nhập

### Household APIs (`/api/ho-khau`)
- `GET /api/ho-khau` - Danh sách hộ khẩu
- `GET /api/ho-khau/:id` - Chi tiết hộ khẩu
- `POST /api/ho-khau` - Tạo hộ khẩu mới
- `PUT /api/ho-khau/:id` - Cập nhật hộ khẩu
- `POST /api/ho-khau/:id/tach-ho` - Tách hộ
- `DELETE /api/ho-khau/:id` - Xóa hộ khẩu

### Citizen APIs (`/api/nhan-khau`)
- `GET /api/nhan-khau` - Danh sách nhân khẩu (có filter)
- `GET /api/nhan-khau/:id` - Chi tiết nhân khẩu
- `POST /api/nhan-khau` - Thêm nhân khẩu mới
- `PUT /api/nhan-khau/:id` - Cập nhật nhân khẩu
- `POST /api/nhan-khau/:id/khai-tu` - Khai tử
- `POST /api/nhan-khau/:id/chuyen-di` - Đánh dấu chuyển đi
- `GET /api/nhan-khau/thong-ke/tong-hop` - Thống kê nhân khẩu

### Temporary Absence APIs (`/api/tam-vang`)
- `GET /api/tam-vang` - Danh sách tạm vắng
- `GET /api/tam-vang/:id` - Chi tiết tạm vắng
- `POST /api/tam-vang` - Đăng ký tạm vắng
- `PUT /api/tam-vang/:id` - Cập nhật tạm vắng
- `DELETE /api/tam-vang/:id` - Xóa tạm vắng

### Temporary Residence APIs (`/api/tam-tru`)
- `GET /api/tam-tru` - Danh sách tạm trú
- `GET /api/tam-tru/:id` - Chi tiết tạm trú
- `POST /api/tam-tru` - Đăng ký tạm trú
- `PUT /api/tam-tru/:id` - Cập nhật tạm trú
- `DELETE /api/tam-tru/:id` - Xóa tạm trú
- `GET /api/tam-tru/thong-ke/tong-hop` - Thống kê tạm trú

### Request Approval APIs (`/api/yeu-cau`)
- `GET /api/yeu-cau` - Danh sách yêu cầu
- `GET /api/yeu-cau/:id` - Chi tiết yêu cầu
- `POST /api/yeu-cau` - Tạo yêu cầu mới
- `POST /api/yeu-cau/:id/duyet` - Duyệt yêu cầu
- `POST /api/yeu-cau/:id/tu-choi` - Từ chối yêu cầu
- `DELETE /api/yeu-cau/:id` - Xóa yêu cầu
- `GET /api/yeu-cau/thong-ke/cho-duyet` - Số yêu cầu chờ duyệt

### Statistics APIs (`/api/thong-ke`)
- `GET /api/thong-ke/tong-quan` - Thống kê tổng quan (admin)
- `GET /api/thong-ke/nguoi-dan/:id` - Thống kê cá nhân (resident)
- `GET /api/thong-ke/lich-su-bien-dong` - Lịch sử biến động
- `GET /api/thong-ke/loc` - Thống kê theo filter

## Frontend Pages

### Đã hoàn thành

#### Resident Portal
- ✅ `ResidentDashboard` - Trang chủ người dân
  - Hiển thị thông tin hộ khẩu
  - Quick actions (tạm vắng, tạm trú, tách hộ, khai sinh)
  - Lịch sử yêu cầu

#### Admin Portal
- ✅ `AdminDashboard` - Trang chủ quản lý
  - Thống kê tổng quan
  - Yêu cầu chờ duyệt
  - Biểu đồ phân bố giới tính, độ tuổi
  - Quick links đến các trang quản lý

### Cần hoàn thiện

#### Resident Portal (Còn thiếu)
- ⏳ Trang sổ hộ khẩu điện tử
- ⏳ Form khai báo tạm vắng
- ⏳ Form khai báo tạm trú
- ⏳ Form yêu cầu tách hộ
- ⏳ Form khai sinh
- ⏳ Trang theo dõi yêu cầu

#### Admin Portal (Còn thiếu)
- ⏳ Trang quản lý hộ khẩu (danh sách, thêm, sửa, xóa)
- ⏳ Trang chi tiết hộ khẩu
- ⏳ Trang quản lý nhân khẩu (danh sách, thêm, sửa)
- ⏳ Trang chi tiết nhân khẩu
- ⏳ Trang quản lý tạm vắng
- ⏳ Trang quản lý tạm trú
- ⏳ Trang xử lý yêu cầu (approve/reject)
- ⏳ Trang thống kê báo cáo
- ⏳ Trang lịch sử biến động

## Cài đặt và chạy dự án

### Backend

```bash
cd backend
npm install
npm run dev
```

Server chạy tại: `http://localhost:5000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App chạy tại: `http://localhost:5173`

## Workflow Phê Duyệt

Hệ thống sử dụng workflow phê duyệt cho các yêu cầu từ người dân:

1. **Người dân** gửi yêu cầu (tạm vắng, tạm trú, tách hộ, v.v.)
2. Yêu cầu được lưu vào bảng `yeu_cau` với trạng thái "Chờ duyệt"
3. **Quản lý** xem danh sách yêu cầu chờ duyệt
4. **Quản lý** duyệt hoặc từ chối:
   - **Duyệt**: Dữ liệu được chuyển vào bảng chính (tam_vang, tam_tru, v.v.)
   - **Từ chối**: Yêu cầu bị từ chối với lý do
5. Người dân xem được trạng thái yêu cầu

## Các loại yêu cầu hỗ trợ

- `tam_vang` - Đăng ký tạm vắng
- `tam_tru` - Đăng ký tạm trú
- `tach_ho` - Yêu cầu tách hộ
- `sinh_con` - Khai sinh
- `tu_vong` - Khai tử
- `sua_thong_tin` - Sửa thông tin nhân khẩu

## Tính năng chính

### Quản lý Hộ Khẩu
- Thêm, sửa, xóa hộ khẩu
- Xem danh sách thành viên
- Tách hộ khẩu
- Chuyển đi

### Quản lý Nhân Khẩu
- Thêm nhân khẩu mới (sinh con)
- Cập nhật thông tin
- Khai tử
- Đánh dấu chuyển đi
- Quản lý CMND/CCCD

### Tạm Vắng/Tạm Trú
- Đăng ký giấy tạm vắng
- Đăng ký giấy tạm trú
- Theo dõi tình trạng (hiệu lực/hết hạn)

### Thống Kê
- Tổng số hộ khẩu, nhân khẩu
- Phân bố theo giới tính
- Phân bố theo độ tuổi
- Tạm vắng/tạm trú hiệu lực
- Lịch sử biến động

## Security

- JWT authentication
- Role-based access control (NguoiDan, CanBo)
- Password hashing với bcrypt
- SQL injection prevention với parameterized queries

## Ghi chú kỹ thuật

### Database
- PostgreSQL 12+
- Sử dụng JSONB để lưu nội dung yêu cầu
- Triggers để tự động cập nhật `updated_at`
- Indexes để tối ưu query

### Backend
- Node.js + Express
- JWT cho authentication
- CORS enabled
- File upload với Multer

### Frontend
- React 18
- React Router v7
- CSS modules
- Responsive design

## Đóng góp

Để hoàn thiện dự án, cần phát triển thêm:

1. **Frontend Pages** - Các trang quản lý còn thiếu
2. **Form Validation** - Validation cho tất cả forms
3. **Error Handling** - Xử lý lỗi toàn diện
4. **Loading States** - Loading indicators
5. **Toast Notifications** - Thông báo người dùng
6. **Export Excel** - Xuất báo cáo
7. **Charts** - Biểu đồ thống kê
8. **Search & Filters** - Tìm kiếm và lọc nâng cao
9. **Pagination** - Phân trang cho danh sách
10. **Tests** - Unit tests và integration tests

## License

MIT
