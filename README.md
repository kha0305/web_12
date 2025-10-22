# MediSchedule - Hệ thống Đặt lịch Khám bệnh

Hệ thống quản lý đặt lịch khám bệnh trực tuyến với 3 vai trò: Bệnh nhân, Bác sĩ và Admin.

## Tính năng

### 👤 Bệnh nhân
- Đăng ký / Đăng nhập / Quên mật khẩu
- Tìm kiếm bác sĩ theo chuyên khoa
- Đặt lịch khám (trực tiếp hoặc tư vấn online)
- Xem lại lịch sử đặt lịch
- Chat với bác sĩ (cho lịch tư vấn online)

### 👨‍⚕️ Bác sĩ
- Đăng nhập quản lý tài khoản
- Cập nhật thông tin chuyên khoa, khung giờ rảnh
- Xác nhận hoặc hủy lịch hẹn
- Chat với bệnh nhân

### 🛠️ Admin
- Quản lý danh sách bác sĩ, bệnh nhân
- Duyệt tài khoản bác sĩ mới
- Thống kê số lượng đặt lịch, lượt tư vấn, người dùng
- Quản lý chuyên khoa

## Công nghệ sử dụng

### Backend
- FastAPI (Python)
- MongoDB
- JWT Authentication
- Bcrypt (Password hashing)

### Frontend
- React 19
- Tailwind CSS
- Shadcn UI Components
- React Router v7
- Axios

## Tài khoản mẫu

### Admin
- Email: `admin@medischedule.com`
- Password: `admin123`

### Tạo tài khoản mới
Bạn có thể đăng ký tài khoản Bệnh nhân hoặc Bác sĩ từ trang đăng ký.

## Hướng dẫn sử dụng

### Dành cho Bệnh nhân
1. Đăng ký tài khoản với vai trò "Bệnh nhân"
2. Đăng nhập vào hệ thống
3. Tìm kiếm bác sĩ theo chuyên khoa
4. Chọn bác sĩ và đặt lịch khám
5. Theo dõi trạng thái lịch hẹn
6. Chat với bác sĩ (nếu chọn tư vấn online)

### Dành cho Bác sĩ
1. Đăng ký tài khoản với vai trò "Bác sĩ"
2. Đăng nhập và hoàn thiện hồ sơ
3. Cập nhật chuyên khoa, kinh nghiệm, phí tư vấn
4. Thiết lập lịch làm việc
5. Chờ admin duyệt tài khoản
6. Quản lý lịch hẹn (xác nhận/hủy/hoàn thành)
7. Chat với bệnh nhân

### Dành cho Admin
1. Đăng nhập với tài khoản admin
2. Duyệt tài khoản bác sĩ mới
3. Quản lý danh sách bệnh nhân
4. Xem thống kê hệ thống
5. Quản lý chuyên khoa

## Chuyên khoa có sẵn
- Nội khoa
- Ngoại khoa
- Tim mạch
- Da liễu
- Tai mũi họng
- Mắt
- Nhi khoa
- Sản phụ khoa

## 📁 Project Structure

```
/app
├── frontend/         # React application
│   ├── src/
│   │   ├── pages/   # Patient, Doctor, Admin pages
│   │   └── components/
├── backend/          # FastAPI application
│   ├── server.py    # Main API
│   ├── init_data.py # Initialize specialties
│   └── create_admin.py # Create admin account
└── README.md
```
# web_12
