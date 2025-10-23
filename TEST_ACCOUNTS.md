# 🔐 TEST ACCOUNTS - MediSchedule System

File này chứa tất cả tài khoản test đã được tạo sẵn trong hệ thống MediSchedule. Sử dụng các tài khoản này để test đầy đủ các tính năng.

---

## 📋 TÓM TẮT NHANH

| Vai trò | Số lượng | Trạng thái |
|---------|----------|------------|
| 👑 Admin (Root) | 1 | Full permissions |
| 👔 Trưởng khoa | 1 | Limited permissions |
| 👨‍⚕️ Bác sĩ | 3 | Approved & Active |
| 👤 Bệnh nhân | 3 | Active |

---

## 👑 ADMIN ACCOUNTS

### Root Admin (Full Permissions)

```yaml
Vai trò: Admin (Root)
Email: admin@medischedule.com
Password: admin123

Quyền hạn:
  ✅ can_create_admins: true
  ✅ can_manage_doctors: true
  ✅ can_manage_patients: true
  ✅ can_view_stats: true
  ✅ can_manage_specialties: true

Mô tả:
  - Tài khoản admin gốc với toàn quyền
  - Có thể tạo admin khác
  - Quản lý toàn bộ hệ thống
  - Truy cập tất cả tính năng admin

Tính năng có thể test:
  ✓ Tạo tài khoản Admin mới với phân quyền tùy chỉnh
  ✓ Quản lý danh sách Admin (xem/sửa/xóa)
  ✓ Tạo tài khoản Patient/Doctor/Department Head
  ✓ Phê duyệt/từ chối bác sĩ mới
  ✓ Quản lý chuyên khoa (thêm/sửa/xóa)
  ✓ Xem thống kê toàn hệ thống
  ✓ Quản lý tất cả người dùng
```

### Cách tạo Admin mới (từ Root Admin):

```
1. Login với admin@medischedule.com / admin123
2. Vào sidebar → "Quản lý Admin"
3. Click "Tạo Admin Mới"
4. Nhập thông tin:
   - Email: newadmin@test.com
   - Password: admin123
   - Họ tên: Quản trị viên mới
5. Chọn quyền:
   ☐ Có thể tạo Admin khác
   ☑ Quản lý bác sĩ
   ☑ Quản lý bệnh nhân
   ☑ Xem thống kê
   ☐ Quản lý chuyên khoa
6. Click "Tạo Admin"
```

---

## 👔 DEPARTMENT HEAD ACCOUNT

### Trưởng khoa

```yaml
Vai trò: Trưởng khoa (Department Head)
Email: departmenthead@test.com
Password: dept123
Họ tên: Trưởng khoa Nguyễn Văn G
SĐT: 0907890123

Quyền hạn:
  ✅ can_manage_doctors: true
  ✅ can_manage_patients: true
  ✅ can_manage_appointments: true
  ✅ can_view_stats: true
  ❌ can_manage_specialties: false
  ❌ can_create_admins: false

Mô tả:
  - Quản lý bác sĩ trong khoa
  - Phê duyệt bác sĩ mới tham gia khoa
  - Xem thống kê khoa
  - KHÔNG thể tạo Admin
  - KHÔNG thể quản lý chuyên khoa

Tính năng có thể test:
  ✓ Xem danh sách bác sĩ trong khoa
  ✓ Phê duyệt/từ chối bác sĩ mới
  ✓ Thêm bác sĩ vào khoa
  ✓ Xóa bác sĩ khỏi khoa
  ✓ Xem thống kê bệnh nhân
  ✗ Không thấy menu "Quản lý Admin"
  ✗ Không thể tạo chuyên khoa mới
```

---

## 👨‍⚕️ DOCTOR ACCOUNTS

### 1. Bác sĩ Tim mạch - Phạm Minh D

```yaml
Vai trò: Bác sĩ (Doctor)
Email: doctor1@test.com
Password: doctor123

Thông tin cá nhân:
  Họ tên: BS. Phạm Minh D
  SĐT: 0904567890
  Chuyên khoa: Tim mạch (Cardiology)
  
Thông tin nghề nghiệp:
  Kinh nghiệm: 15 năm
  Học vấn: Chưa cập nhật
  Bio: "Bác sĩ chuyên khoa Tim mạch với 15 năm kinh nghiệm"
  Phí tư vấn: 300,000 VNĐ
  Trạng thái: Approved (Đã phê duyệt)

Lịch làm việc mẫu:
  Thứ 2-6: 08:00 - 12:00, 14:00 - 17:00
  Thứ 7: 08:00 - 12:00
  Chủ nhật: Nghỉ

Tính năng có thể test:
  ✓ Cập nhật profile (bio, học vấn, phí tư vấn)
  ✓ Thiết lập lịch làm việc
  ✓ Xem danh sách lịch hẹn
  ✓ Xác nhận/từ chối lịch hẹn mới
  ✓ Đánh dấu hoàn thành lịch hẹn
  ✓ Chat với bệnh nhân (lịch tư vấn online)
  ✓ Xem danh sách bệnh nhân đã khám
```

### 2. Bác sĩ Nhi khoa - Hoàng Thị E

```yaml
Vai trò: Bác sĩ (Doctor)
Email: doctor2@test.com
Password: doctor123

Thông tin cá nhân:
  Họ tên: BS. Hoàng Thị E
  SĐT: 0905678901
  Chuyên khoa: Nhi khoa (Pediatrics)
  
Thông tin nghề nghiệp:
  Kinh nghiệm: 10 năm
  Bio: "Bác sĩ chuyên khoa Nhi với 10 năm kinh nghiệm"
  Phí tư vấn: 250,000 VNĐ
  Trạng thái: Approved (Đã phê duyệt)

Đặc điểm:
  - Chuyên trị trẻ em dưới 16 tuổi
  - Phù hợp test đặt lịch cho trẻ
  - Phí thấp hơn (250k)
```

### 3. Bác sĩ Nội khoa - Võ Văn F

```yaml
Vai trò: Bác sĩ (Doctor)
Email: doctor3@test.com
Password: doctor123

Thông tin cá nhân:
  Họ tên: BS. Võ Văn F
  SĐT: 0906789012
  Chuyên khoa: Nội khoa (Internal Medicine)
  
Thông tin nghề nghiệp:
  Kinh nghiệm: 12 năm
  Bio: "Bác sĩ chuyên khoa Nội với 12 năm kinh nghiệm"
  Phí tư vấn: 280,000 VNĐ
  Trạng thái: Approved (Đã phê duyệt)

Đặc điểm:
  - Chuyên khoa phổ thông
  - Phù hợp test đa dạng triệu chứng
```

---

## 👤 PATIENT ACCOUNTS

### 1. Bệnh nhân Nguyễn Văn A

```yaml
Vai trò: Bệnh nhân (Patient)
Email: patient1@test.com
Password: patient123

Thông tin cá nhân:
  Họ tên: Nguyễn Văn A
  SĐT: 0901234567
  Ngày sinh: 15/01/1990 (35 tuổi)
  Địa chỉ: 123 Lê Lợi, Q1, TP.HCM

Tính năng có thể test:
  ✓ Tìm kiếm bác sĩ theo chuyên khoa
  ✓ Đặt lịch khám (trực tiếp)
  ✓ Đặt lịch tư vấn online
  ✓ Xem lịch sử đặt lịch
  ✓ Hủy lịch hẹn (nếu chưa xác nhận)
  ✓ Chat với bác sĩ
  ✓ Xem chi tiết bác sĩ
```

### 2. Bệnh nhân Trần Thị B

```yaml
Vai trò: Bệnh nhân (Patient)
Email: patient2@test.com
Password: patient123

Thông tin cá nhân:
  Họ tên: Trần Thị B
  SĐT: 0902345678
  Ngày sinh: 20/05/1985 (39 tuổi)
  Địa chỉ: 456 Nguyễn Huệ, Q1, TP.HCM

Đặc điểm:
  - Nữ giới, tuổi trung niên
  - Phù hợp test đặt lịch Sản phụ khoa
```

### 3. Bệnh nhân Lê Văn C

```yaml
Vai trò: Bệnh nhân (Patient)
Email: patient3@test.com
Password: patient123

Thông tin cá nhân:
  Họ tên: Lê Văn C
  SĐT: 0903456789
  Ngày sinh: 10/08/1995 (29 tuổi)
  Địa chỉ: 789 Hai Bà Trưng, Q3, TP.HCM

Đặc điểm:
  - Nam giới, trẻ tuổi
  - Phù hợp test đa dạng chuyên khoa
```

---

## 🧪 TESTING SCENARIOS

### Scenario 1: Patient đặt lịch và chat với Doctor

```
1. Login Patient (patient1@test.com / patient123)
2. Tìm bác sĩ chuyên khoa "Tim mạch"
3. Chọn BS. Phạm Minh D
4. Đặt lịch:
   - Loại: Tư vấn online
   - Ngày: Ngày mai
   - Giờ: 09:00
   - Lý do: Đau ngực, khó thở
5. Logout Patient

6. Login Doctor (doctor1@test.com / doctor123)
7. Vào "Lịch hẹn của tôi"
8. Xác nhận lịch hẹn từ Nguyễn Văn A
9. Vào chi tiết lịch hẹn
10. Bắt đầu chat: "Xin chào, bạn có triệu chứng gì?"
11. Logout Doctor

12. Login lại Patient1
13. Vào chi tiết lịch hẹn
14. Chat với bác sĩ: "Tôi hay bị đau ngực khi vận động"
15. Kiểm tra real-time chat
```

### Scenario 2: Admin tạo Admin mới và phân quyền

```
1. Login Root Admin (admin@medischedule.com / admin123)
2. Vào "Quản lý Admin"
3. Tạo Admin mới:
   - Email: subadmin@test.com
   - Password: admin123
   - Họ tên: Sub Admin
   - Quyền: Chỉ "Quản lý bác sĩ" và "Xem thống kê"
4. Logout Root Admin

5. Login Sub Admin (subadmin@test.com / admin123)
6. Kiểm tra:
   ✓ Có thể vào "Quản lý bác sĩ"
   ✓ Có thể xem "Thống kê"
   ✗ KHÔNG thấy "Quản lý Admin"
   ✗ KHÔNG thể tạo chuyên khoa
```

### Scenario 3: Department Head phê duyệt bác sĩ mới

```
1. Tạo tài khoản bác sĩ mới:
   - Đăng ký với role "Doctor"
   - Email: newdoctor@test.com
   - Password: doctor123
   - Chuyên khoa: Nội khoa

2. Login Department Head (departmenthead@test.com / dept123)
3. Vào "Quản lý bác sĩ"
4. Thấy bác sĩ mới với status "Pending"
5. Click "Approve" hoặc "Reject"
6. Kiểm tra bác sĩ đã được phê duyệt
```

### Scenario 4: Test đa ngôn ngữ (Vi/En)

```
1. Login bất kỳ tài khoản nào
2. Click icon 🌐 ở sidebar
3. Chọn "Tiếng Việt" → Kiểm tra UI hiển thị tiếng Việt
4. Chọn "English" → Kiểm tra UI hiển thị tiếng Anh
5. Reload trang → Ngôn ngữ vẫn được giữ (localStorage)
```

### Scenario 5: Admin tạo tài khoản người dùng

```
1. Login Admin (admin@medischedule.com / admin123)
2. Vào "Tạo tài khoản"
3. Test tạo Patient:
   - Chọn role: Patient
   - Điền thông tin đầy đủ
   - Submit
4. Test tạo Doctor:
   - Chọn role: Doctor
   - Điền thông tin + chuyên khoa
   - Submit
5. Test tạo Department Head:
   - Chọn role: Department Head
   - Chọn quyền hạn
   - Submit
6. Kiểm tra tài khoản mới có login được không
```

---

## 📊 CHUYÊN KHOA CÓ SẴN

Các chuyên khoa đã được khởi tạo sẵn trong hệ thống:

1. **Nội khoa** (Internal Medicine)
2. **Ngoại khoa** (Surgery)
3. **Nhi khoa** (Pediatrics)
4. **Sản phụ khoa** (Obstetrics & Gynecology)
5. **Tim mạch** (Cardiology)
6. **Thần kinh** (Neurology)
7. **Da liễu** (Dermatology)
8. **Tai mũi họng** (ENT)

---

## 🔧 SCRIPTS HỮU ÍCH

### Tạo lại dữ liệu mẫu

```bash
cd /app/backend
python create_sample_data.py
```

Script này sẽ:
- ✅ Tạo 8 chuyên khoa
- ✅ Tạo 3 bác sĩ (đã approved)
- ✅ Tạo 3 bệnh nhân
- ✅ Tạo 1 trưởng khoa
- ℹ️ Admin phải tạo bằng script riêng

### Tạo Root Admin

```bash
cd /app/backend
python create_admin.py
```

Tạo tài khoản admin@medischedule.com với full permissions.

### Khởi tạo chuyên khoa

```bash
cd /app/backend
python init_data.py
```

Tạo 8 chuyên khoa mặc định.

---

## 🚨 LƯU Ý QUAN TRỌNG

### Mật khẩu
- ⚠️ **TẤT CẢ TÀI KHOẢN TEST** đều dùng password đơn giản
- 🔒 **KHÔNG dùng cho production**
- 🔐 Đổi password sau khi deploy

### Quyền hạn Admin
- Root Admin có `can_create_admins = true`
- Admin khác mặc định `can_create_admins = false`
- Department Head KHÔNG phải Admin, không có quyền tạo admin

### Trạng thái Bác sĩ
- Tất cả bác sĩ test đều có status `approved`
- Bác sĩ mới đăng ký sẽ có status `pending`
- Cần Admin/Department Head phê duyệt

### Email Validation
- Hệ thống chấp nhận email domain `@test.com`
- Email phải unique
- Format chuẩn: `username@domain.com`

---

## 📞 SUPPORT

Nếu gặp vấn đề với tài khoản test:
1. Kiểm tra tài khoản có tồn tại: Login thử
2. Chạy lại `create_sample_data.py`
3. Check MongoDB: `db.users.find({email: "email@test.com"})`
4. Check logs: `/var/log/supervisor/backend.err.log`

---

## ✅ CHECKLIST TEST ĐẦY ĐỦ

### Authentication
- [ ] Login Admin
- [ ] Login Doctor
- [ ] Login Patient
- [ ] Login Department Head
- [ ] Logout
- [ ] Token expiry handling

### Patient Features
- [ ] Tìm bác sĩ
- [ ] Lọc theo chuyên khoa
- [ ] Xem chi tiết bác sĩ
- [ ] Đặt lịch trực tiếp
- [ ] Đặt lịch online
- [ ] Hủy lịch hẹn
- [ ] Chat với bác sĩ
- [ ] Xem lịch sử

### Doctor Features
- [ ] Cập nhật profile
- [ ] Cập nhật lịch làm việc
- [ ] Xác nhận lịch hẹn
- [ ] Từ chối lịch hẹn
- [ ] Hoàn thành lịch hẹn
- [ ] Chat với bệnh nhân

### Admin Features
- [ ] Tạo Patient account
- [ ] Tạo Doctor account
- [ ] Tạo Department Head account
- [ ] Tạo Admin account (nếu có quyền)
- [ ] Xem danh sách admin
- [ ] Sửa quyền admin
- [ ] Xóa admin
- [ ] Phê duyệt bác sĩ
- [ ] Quản lý chuyên khoa
- [ ] Xem thống kê

### Department Head Features
- [ ] Xem bác sĩ trong khoa
- [ ] Phê duyệt bác sĩ
- [ ] Thêm bác sĩ
- [ ] Xóa bác sĩ
- [ ] Xem thống kê

### System Features
- [ ] Đổi ngôn ngữ VI/EN
- [ ] Responsive design
- [ ] Real-time chat
- [ ] Error handling
- [ ] Loading states

---

**Last Updated**: 2025-01-20  
**Total Test Accounts**: 8  
**Status**: ✅ All accounts verified and working

---

**Happy Testing! 🧪🎉**
