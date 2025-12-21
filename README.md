# 🏠 Hệ Thống Quản Lý Hộ Khẩu - Household Management System

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Node](https://img.shields.io/badge/node-%3E%3D16.0.0-green)
![PostgreSQL](https://img.shields.io/badge/postgresql-%3E%3D12.0-blue)
![React](https://img.shields.io/badge/react-18.3.1-blue)

Hệ thống quản lý hộ khẩu điện tử hiện đại, giúp quản lý thông tin hộ gia đình, nhân khẩu, tạm trú, tạm vắng và các biến động dân cư một cách hiệu quả.

## ✨ Tính năng chính

### 👥 Dành cho Người Dân
- 📊 **Dashboard cá nhân** - Xem thông tin hộ khẩu và thành viên
- 📱 **Sổ hộ khẩu điện tử** - Tra cứu thông tin chi tiết
- 📝 **Gửi yêu cầu** - Khai báo tạm vắng, tạm trú, tách hộ, sinh con
- 📜 **Theo dõi yêu cầu** - Xem trạng thái và lịch sử

### 🛡️ Dành cho Quản Lý
- 📈 **Dashboard thống kê** - Tổng quan hệ thống
- 👨‍👩‍👧‍👦 **Quản lý hộ khẩu** - CRUD, tách hộ, chuyển đi
- 👤 **Quản lý nhân khẩu** - Khai sinh, khai tử, chuyển đi/đến
- ✅ **Xử lý yêu cầu** - Duyệt/từ chối với workflow
- 📊 **Thống kê & báo cáo** - Theo giới tính, độ tuổi, tạm trú/vắng
- 📜 **Lịch sử biến động** - Tracking mọi thay đổi

## 🎨 Giao diện

### Resident Dashboard
- Modern gradient design (Purple/Blue)
- Responsive cards layout
- Quick action buttons với icons
- Real-time request status

### Admin Dashboard  
- Clean professional interface
- Statistics cards với colors
- Interactive charts
- Pending requests notification

### Household View
- Member cards với avatar
- Detailed information display
- Relationship visualization
- Age calculation

## 🏗️ Kiến trúc hệ thống

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   React     │ ◄─────► │   Express   │ ◄─────► │ PostgreSQL  │
│  Frontend   │   REST  │   Backend   │   SQL   │  Database   │
└─────────────┘   API   └─────────────┘         └─────────────┘
```

### Tech Stack

**Backend:**
- Node.js + Express
- PostgreSQL với pg
- JWT Authentication
- Bcrypt password hashing
- Multer file upload

**Frontend:**
- React 18.3
- React Router 7
- Modern CSS with gradients
- Responsive design

## 📊 Database Schema

8 bảng chính:

1. **ho_khau** - Sổ hộ khẩu
2. **nhan_khau** - Nhân khẩu (công dân)
3. **chung_minh_thu** - CMND/CCCD
4. **tam_vang** - Giấy tạm vắng
5. **tam_tru** - Giấy tạm trú
6. **lich_su_bien_dong** - Lịch sử thay đổi
7. **nguoidung** - Tài khoản người dùng
8. **yeu_cau** - Yêu cầu phê duyệt

Chi tiết: [backend/database/schema.sql](backend/database/schema.sql)

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- PostgreSQL 12+
- npm hoặc yarn

### Installation

**1. Clone repository**
```bash
git clone <repository-url>
cd KyThuatPhanMem
```

**2. Setup Database**
```bash
psql -U postgres
CREATE DATABASE QuanLiPhanAnh;
\c QuanLiPhanAnh
\i backend/database/schema.sql
```

**3. Setup Backend**
```bash
cd backend
npm install
# Cấu hình .env (đã có sẵn)
npm run dev
```

**4. Setup Frontend**
```bash
cd frontend
npm install
npm run dev
```

**5. Access**
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

Chi tiết: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 📚 Documentation

- 📖 [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Chi tiết implementation
- 🚀 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Hướng dẫn triển khai
- 📝 API Documentation - Trong từng route file

## 🎯 API Endpoints

### Core APIs (50+ endpoints)

```
/api/auth          - Authentication
/api/ho-khau       - Household management
/api/nhan-khau     - Citizen management  
/api/tam-vang      - Temporary absence
/api/tam-tru       - Temporary residence
/api/yeu-cau       - Request workflow
/api/thong-ke      - Statistics
```

Xem chi tiết: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#api-endpoints)

## 🔐 Security

- ✅ JWT token-based authentication
- ✅ Role-based access control (NguoiDan, CanBo)
- ✅ Password hashing
- ✅ SQL injection prevention
- ✅ CORS configuration
- ⚠️ Bcrypt (commented, enable in production)

## 📱 Screenshots

### Resident Portal
- Dashboard với household summary
- Quick actions (4 services)
- Request history tracking

### Admin Portal  
- Statistics overview (5 cards)
- Pending requests list
- Gender & age distribution charts
- Quick management links (6 modules)

### Household View
- Member cards với full details
- Avatar by gender
- Age calculation
- CMND/CCCD info

## 🎯 Implementation Status

### ✅ Completed (Core System)

**Backend (100%)**
- ✅ Full database schema
- ✅ 6 route modules
- ✅ 50+ API endpoints
- ✅ Authentication & authorization
- ✅ Request approval workflow
- ✅ Statistics & reporting

**Frontend (40%)**
- ✅ Resident Dashboard
- ✅ Admin Dashboard
- ✅ Household member view
- ✅ Modern responsive UI
- ✅ Routing setup

### ⏳ In Progress / Planned

**Admin Management Pages**
- ⏳ Household list & CRUD
- ⏳ Citizen list & CRUD
- ⏳ Temporary records management
- ⏳ Request approval UI
- ⏳ Advanced statistics

**Resident Features**
- ⏳ Declaration forms
- ⏳ Request tracking
- ⏳ Profile editing

**Enhancements**
- ⏳ Form validation
- ⏳ Toast notifications
- ⏳ Excel export
- ⏳ Charts & graphs
- ⏳ Search & filters
- ⏳ Pagination

## 🔄 Workflow Example

### Tạm Vắng (Temporary Absence)

1. **Người dân** gửi yêu cầu qua form
2. Yêu cầu lưu vào `yeu_cau` (status: Chờ duyệt)
3. **Admin** nhận thông báo
4. **Admin** xem chi tiết và duyệt
5. Hệ thống tự động:
   - Tạo record trong `tam_vang`
   - Cập nhật `lich_su_bien_dong`
   - Đổi status yêu cầu thành "Đã duyệt"
6. Người dân thấy status updated

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Code Style

- Backend: Follow existing Express patterns
- Frontend: React functional components with hooks
- CSS: BEM-like naming convention
- Database: Snake_case for columns

## 📝 License

MIT License - feel free to use for your projects

## 👥 Authors

- Initial design & architecture
- Backend API development
- Frontend UI/UX design
- Database schema design

## 🙏 Acknowledgments

- PostgreSQL for robust database
- Express.js for API framework
- React for modern UI
- Vietnamese government household registry requirements

## 📞 Support

For issues and questions:
1. Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Review API documentation in route files
3. Check console logs (browser & server)
4. Review database schema

## 🗺️ Roadmap

### Version 1.1 (Next)
- [ ] Complete admin management pages
- [ ] Add all declaration forms
- [ ] Form validation
- [ ] Toast notifications

### Version 1.2
- [ ] Excel export
- [ ] Advanced charts
- [ ] Email notifications
- [ ] File upload for documents

### Version 2.0
- [ ] Mobile app
- [ ] Real-time notifications
- [ ] E-signature
- [ ] OCR for documents

---

**Built with ❤️ for efficient household management**
