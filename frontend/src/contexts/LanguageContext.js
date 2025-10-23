import React, { createContext, useState, useContext, useEffect } from 'react';

const LanguageContext = createContext();

export const translations = {
  vi: {
    // Common
    login: 'Đăng nhập',
    logout: 'Đăng xuất',
    register: 'Đăng ký',
    email: 'Email',
    password: 'Mật khẩu',
    fullName: 'Họ và tên',
    phone: 'Số điện thoại',
    address: 'Địa chỉ',
    dateOfBirth: 'Ngày sinh',
    save: 'Lưu',
    cancel: 'Hủy',
    delete: 'Xóa',
    edit: 'Chỉnh sửa',
    create: 'Tạo',
    search: 'Tìm kiếm',
    loading: 'Đang tải...',
    submit: 'Gửi',
    reset: 'Đặt lại',
    back: 'Quay lại',
    next: 'Tiếp theo',
    confirm: 'Xác nhận',
    
    // Navigation
    home: 'Trang chủ',
    dashboard: 'Bảng điều khiển',
    profile: 'Hồ sơ',
    settings: 'Cài đặt',
    
    // Roles
    patient: 'Bệnh nhân',
    doctor: 'Bác sĩ',
    admin: 'Quản trị viên',
    departmentHead: 'Trưởng khoa',
    
    // Admin Dashboard
    adminDashboard: 'Bảng điều khiển Admin',
    welcomeAdmin: 'Xin chào, Admin',
    manageSystem: 'Quản lý hệ thống MediSchedule',
    createAccount: 'Tạo tài khoản',
    createAccountDesc: 'Tạo tài khoản bệnh nhân, bác sĩ, trưởng khoa',
    manageDoctors: 'Quản lý bác sĩ',
    manageDoctorsDesc: 'Duyệt và quản lý tài khoản bác sĩ',
    patientList: 'Danh sách bệnh nhân',
    patientListDesc: 'Xem danh sách bệnh nhân đăng ký',
    statistics: 'Thống kê',
    statisticsDesc: 'Xem báo cáo và thống kê hệ thống',
    manageAdmins: 'Quản lý Admin',
    manageAdminsDesc: 'Tạo và quản lý tài khoản admin',
    
    // Create Account Page
    selectAccountType: 'Chọn loại tài khoản',
    accountInfo: 'Thông tin',
    basicInfo: 'Thông tin cơ bản',
    doctorInfo: 'Thông tin bác sĩ',
    departmentHeadPermissions: 'Phân quyền trưởng khoa',
    specialty: 'Chuyên khoa',
    selectSpecialty: 'Chọn chuyên khoa',
    bio: 'Giới thiệu',
    experienceYears: 'Số năm kinh nghiệm',
    consultationFee: 'Phí khám (VNĐ)',
    permissions: 'Phân quyền',
    canManageDoctors: 'Quản lý bác sĩ',
    canManagePatients: 'Quản lý bệnh nhân',
    canManageAppointments: 'Quản lý lịch hẹn',
    canViewStats: 'Xem thống kê',
    canManageSpecialties: 'Quản lý chuyên khoa',
    canCreateAdmins: 'Tạo và quản lý admin khác',
    creating: 'Đang tạo...',
    
    // Admin Management
    adminManagement: 'Quản lý Admin',
    adminManagementDesc: 'Quản lý tài khoản và phân quyền admin',
    createNewAdmin: 'Tạo Admin Mới',
    createAdminAccount: 'Tạo tài khoản Admin mới',
    adminList: 'Danh sách Admin',
    you: 'Bạn',
    created: 'Tạo',
    editPermissions: 'Chỉnh sửa phân quyền',
    
    // Messages
    createSuccess: 'Tạo thành công!',
    createError: 'Không thể tạo',
    deleteSuccess: 'Đã xóa thành công',
    deleteError: 'Không thể xóa',
    updateSuccess: 'Cập nhật thành công',
    updateError: 'Không thể cập nhật',
    loadError: 'Không thể tải dữ liệu',
    confirmDelete: 'Bạn có chắc muốn xóa',
    
    // Login Page
    welcomeBack: 'Chào mừng trở lại',
    loginToContinue: 'Đăng nhập để tiếp tục',
    forgotPassword: 'Quên mật khẩu?',
    dontHaveAccount: 'Chưa có tài khoản?',
    registerNow: 'Đăng ký ngay',
    
    // Patient
    findDoctor: 'Tìm bác sĩ',
    appointments: 'Lịch hẹn',
    bookAppointment: 'Đặt lịch khám',
    
    // Doctor
    schedule: 'Lịch làm việc',
    myAppointments: 'Lịch hẹn của tôi',
    
    // Specialties
    cardiology: 'Tim mạch',
    pediatrics: 'Nhi khoa',
    internalMedicine: 'Nội khoa',
    surgery: 'Ngoại khoa',
    obstetrics: 'Sản phụ khoa',
    neurology: 'Thần kinh',
    dermatology: 'Da liễu',
    ent: 'Tai mũi họng',
    
    // Doctors Management
    doctorManagement: 'Quản lý bác sĩ',
    doctorList: 'Danh sách bác sĩ',
    filterByStatus: 'Lọc theo trạng thái',
    all: 'Tất cả',
    pending: 'Chờ duyệt',
    approved: 'Đã duyệt',
    rejected: 'Từ chối',
    searchDoctors: 'Tìm kiếm bác sĩ...',
    approve: 'Duyệt',
    reject: 'Từ chối',
    remove: 'Xóa',
    status: 'Trạng thái',
    experience: 'Kinh nghiệm',
    years: 'năm',
    fee: 'Phí khám',
    
    // Patients Management
    patientManagement: 'Quản lý bệnh nhân',
    searchPatients: 'Tìm kiếm bệnh nhân...',
    registeredDate: 'Ngày đăng ký',
    
    // Stats Page
    systemStatistics: 'Thống kê hệ thống',
    overview: 'Tổng quan',
    totalPatients: 'Tổng bệnh nhân',
    totalDoctors: 'Tổng bác sĩ',
    totalAppointments: 'Tổng lịch hẹn',
    appointmentsByStatus: 'Lịch hẹn theo trạng thái',
    pendingAppointments: 'Chờ xác nhận',
    confirmedAppointments: 'Đã xác nhận',
    completedAppointments: 'Đã hoàn thành',
    cancelledAppointments: 'Đã hủy',
    appointmentsByType: 'Lịch hẹn theo loại',
    onlineConsultations: 'Khám online',
    inPersonConsultations: 'Khám trực tiếp',
    doctorsByStatus: 'Bác sĩ theo trạng thái',
    pendingDoctors: 'Chờ duyệt',
    approvedDoctors: 'Đã duyệt',
    
    // Common Actions
    viewDetails: 'Xem chi tiết',
    actions: 'Hành động',
    noData: 'Không có dữ liệu',
    confirmDeleteUser: 'Bạn có chắc muốn xóa người dùng này?',
    userDeleted: 'Đã xóa người dùng',
    cannotDeleteUser: 'Không thể xóa người dùng',
    
    // Sidebar Navigation
    createAccounts: 'Tạo tài khoản',
    doctors: 'Bác sĩ',
    patients: 'Bệnh nhân',
    stats: 'Thống kê',
    admins: 'Quản lý Admin'
  },
  
  en: {
    // Common
    login: 'Login',
    logout: 'Logout',
    register: 'Register',
    email: 'Email',
    password: 'Password',
    fullName: 'Full Name',
    phone: 'Phone Number',
    address: 'Address',
    dateOfBirth: 'Date of Birth',
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    create: 'Create',
    search: 'Search',
    loading: 'Loading...',
    submit: 'Submit',
    reset: 'Reset',
    back: 'Back',
    next: 'Next',
    confirm: 'Confirm',
    
    // Navigation
    home: 'Home',
    dashboard: 'Dashboard',
    profile: 'Profile',
    settings: 'Settings',
    
    // Roles
    patient: 'Patient',
    doctor: 'Doctor',
    admin: 'Administrator',
    departmentHead: 'Department Head',
    
    // Admin Dashboard
    adminDashboard: 'Admin Dashboard',
    welcomeAdmin: 'Welcome, Admin',
    manageSystem: 'Manage MediSchedule System',
    createAccount: 'Create Account',
    createAccountDesc: 'Create patient, doctor, department head accounts',
    manageDoctors: 'Manage Doctors',
    manageDoctorsDesc: 'Review and manage doctor accounts',
    patientList: 'Patient List',
    patientListDesc: 'View registered patient list',
    statistics: 'Statistics',
    statisticsDesc: 'View system reports and statistics',
    manageAdmins: 'Manage Admins',
    manageAdminsDesc: 'Create and manage admin accounts',
    
    // Create Account Page
    selectAccountType: 'Select account type',
    accountInfo: 'Information',
    basicInfo: 'Basic Information',
    doctorInfo: 'Doctor Information',
    departmentHeadPermissions: 'Department Head Permissions',
    specialty: 'Specialty',
    selectSpecialty: 'Select specialty',
    bio: 'Biography',
    experienceYears: 'Years of Experience',
    consultationFee: 'Consultation Fee (VND)',
    permissions: 'Permissions',
    canManageDoctors: 'Manage doctors',
    canManagePatients: 'Manage patients',
    canManageAppointments: 'Manage appointments',
    canViewStats: 'View statistics',
    canManageSpecialties: 'Manage specialties',
    canCreateAdmins: 'Create and manage other admins',
    creating: 'Creating...',
    
    // Admin Management
    adminManagement: 'Admin Management',
    adminManagementDesc: 'Manage admin accounts and permissions',
    createNewAdmin: 'Create New Admin',
    createAdminAccount: 'Create new admin account',
    adminList: 'Admin List',
    you: 'You',
    created: 'Created',
    editPermissions: 'Edit Permissions',
    
    // Messages
    createSuccess: 'Created successfully!',
    createError: 'Cannot create',
    deleteSuccess: 'Deleted successfully',
    deleteError: 'Cannot delete',
    updateSuccess: 'Updated successfully',
    updateError: 'Cannot update',
    loadError: 'Cannot load data',
    confirmDelete: 'Are you sure you want to delete',
    
    // Login Page
    welcomeBack: 'Welcome Back',
    loginToContinue: 'Login to continue',
    forgotPassword: 'Forgot password?',
    dontHaveAccount: "Don't have an account?",
    registerNow: 'Register now',
    
    // Patient
    findDoctor: 'Find Doctor',
    appointments: 'Appointments',
    bookAppointment: 'Book Appointment',
    
    // Doctor
    schedule: 'Schedule',
    myAppointments: 'My Appointments',
    
    // Specialties
    cardiology: 'Cardiology',
    pediatrics: 'Pediatrics',
    internalMedicine: 'Internal Medicine',
    surgery: 'Surgery',
    obstetrics: 'Obstetrics',
    neurology: 'Neurology',
    dermatology: 'Dermatology',
    ent: 'ENT',
    
    // Doctors Management
    doctorManagement: 'Doctor Management',
    doctorList: 'Doctor List',
    filterByStatus: 'Filter by Status',
    all: 'All',
    pending: 'Pending',
    approved: 'Approved',
    rejected: 'Rejected',
    searchDoctors: 'Search doctors...',
    approve: 'Approve',
    reject: 'Reject',
    remove: 'Remove',
    status: 'Status',
    experience: 'Experience',
    years: 'years',
    fee: 'Fee',
    
    // Patients Management
    patientManagement: 'Patient Management',
    searchPatients: 'Search patients...',
    registeredDate: 'Registered Date',
    
    // Stats Page
    systemStatistics: 'System Statistics',
    overview: 'Overview',
    totalPatients: 'Total Patients',
    totalDoctors: 'Total Doctors',
    totalAppointments: 'Total Appointments',
    appointmentsByStatus: 'Appointments by Status',
    pendingAppointments: 'Pending',
    confirmedAppointments: 'Confirmed',
    completedAppointments: 'Completed',
    cancelledAppointments: 'Cancelled',
    appointmentsByType: 'Appointments by Type',
    onlineConsultations: 'Online Consultations',
    inPersonConsultations: 'In-Person Consultations',
    doctorsByStatus: 'Doctors by Status',
    pendingDoctors: 'Pending',
    approvedDoctors: 'Approved',
    
    // Common Actions
    viewDetails: 'View Details',
    actions: 'Actions',
    noData: 'No data available',
    confirmDeleteUser: 'Are you sure you want to delete this user?',
    userDeleted: 'User deleted',
    cannotDeleteUser: 'Cannot delete user',
    
    // Sidebar Navigation
    createAccounts: 'Create Accounts',
    doctors: 'Doctors',
    patients: 'Patients',
    stats: 'Statistics',
    admins: 'Manage Admins'
  }
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('language') || 'vi';
  });

  useEffect(() => {
    localStorage.setItem('language', language);
  }, [language]);

  const t = (key) => {
    return translations[language][key] || key;
  };

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'vi' ? 'en' : 'vi');
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, toggleLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};
