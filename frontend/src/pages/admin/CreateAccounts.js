import React, { useState, useEffect, useContext } from 'react';
import { AuthContext, API } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import Layout from '@/components/Layout';
import { toast } from 'sonner';
import axios from 'axios';
import { UserPlus, Eye, EyeOff, Users, Stethoscope, Shield } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';

export default function CreateAccounts() {
  const { token } = useContext(AuthContext);
  const { t } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [selectedRole, setSelectedRole] = useState('patient');
  const [specialties, setSpecialties] = useState([]);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    phone: '',
    date_of_birth: '',
    address: '',
    // Doctor fields
    specialty_id: '',
    bio: '',
    experience_years: 0,
    consultation_fee: 0,
    // Department head fields
    can_manage_doctors: true,
    can_manage_patients: true,
    can_manage_appointments: true,
    can_view_stats: true,
    can_manage_specialties: false
  });

  useEffect(() => {
    fetchSpecialties();
  }, []);

  const fetchSpecialties = async () => {
    try {
      const response = await axios.get(`${API}/specialties`);
      setSpecialties(response.data);
    } catch (error) {
      console.error('Error fetching specialties:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        role: selectedRole,
        phone: formData.phone || undefined,
        date_of_birth: formData.date_of_birth || undefined,
        address: formData.address || undefined
      };

      if (selectedRole === 'doctor') {
        payload.specialty_id = formData.specialty_id;
        payload.bio = formData.bio;
        payload.experience_years = parseInt(formData.experience_years) || 0;
        payload.consultation_fee = parseFloat(formData.consultation_fee) || 0;
      }

      if (selectedRole === 'department_head') {
        payload.admin_permissions = {
          can_manage_doctors: formData.can_manage_doctors,
          can_manage_patients: formData.can_manage_patients,
          can_manage_appointments: formData.can_manage_appointments,
          can_view_stats: formData.can_view_stats,
          can_manage_specialties: formData.can_manage_specialties,
          can_create_admins: false
        };
      }

      await axios.post(`${API}/admin/create-user`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success(`${t('createSuccess')} ${getRoleName(selectedRole)}!`);
      resetForm();
    } catch (error) {
      toast.error(error.response?.data?.detail || t('createError'));
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      email: '',
      password: '',
      full_name: '',
      phone: '',
      date_of_birth: '',
      address: '',
      specialty_id: '',
      bio: '',
      experience_years: 0,
      consultation_fee: 0,
      can_manage_doctors: true,
      can_manage_patients: true,
      can_manage_appointments: true,
      can_view_stats: true,
      can_manage_specialties: false
    });
  };

  const getRoleName = (role) => {
    const names = {
      patient: t('patient'),
      doctor: t('doctor'),
      department_head: t('departmentHead')
    };
    return names[role] || role;
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">{t('createAccount')}</h1>
            <p className="text-gray-600 mt-1">{t('createAccountDesc')}</p>
          </div>

          {/* Role Selection */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
            <Label className="mb-4 block text-lg font-semibold">{t('selectAccountType')}</Label>
            <div className="grid md:grid-cols-3 gap-4">
              <RoleCard
                icon={<Users className="w-8 h-8" />}
                title={t('patient')}
                role="patient"
                selected={selectedRole === 'patient'}
                onClick={() => setSelectedRole('patient')}
              />
              <RoleCard
                icon={<Stethoscope className="w-8 h-8" />}
                title={t('doctor')}
                role="doctor"
                selected={selectedRole === 'doctor'}
                onClick={() => setSelectedRole('doctor')}
              />
              <RoleCard
                icon={<Shield className="w-8 h-8" />}
                title={t('departmentHead')}
                role="department_head"
                selected={selectedRole === 'department_head'}
                onClick={() => setSelectedRole('department_head')}
              />
            </div>
          </div>

          {/* Create Account Form */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-xl font-bold mb-6">{t('accountInfo')} {getRoleName(selectedRole)}</h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Basic Information */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-700 border-b pb-2">{t('basicInfo')}</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="full_name">{t('fullName')} *</Label>
                    <Input
                      id="full_name"
                      type="text"
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      required
                      className="mt-2"
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      required
                      className="mt-2"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="password">Mật khẩu *</Label>
                  <div className="relative mt-2">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      required
                      className="pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="phone">Số điện thoại</Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="mt-2"
                    />
                  </div>
                  <div>
                    <Label htmlFor="date_of_birth">Ngày sinh</Label>
                    <Input
                      id="date_of_birth"
                      type="date"
                      value={formData.date_of_birth}
                      onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                      className="mt-2"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="address">Địa chỉ</Label>
                  <Input
                    id="address"
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    className="mt-2"
                  />
                </div>
              </div>

              {/* Doctor Specific Fields */}
              {selectedRole === 'doctor' && (
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-700 border-b pb-2">Thông tin bác sĩ</h3>
                  <div>
                    <Label htmlFor="specialty_id">Chuyên khoa *</Label>
                    <select
                      id="specialty_id"
                      value={formData.specialty_id}
                      onChange={(e) => setFormData({ ...formData, specialty_id: e.target.value })}
                      required
                      className="mt-2 w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                    >
                      <option value="">Chọn chuyên khoa</option>
                      {specialties.map((specialty) => (
                        <option key={specialty.id} value={specialty.id}>
                          {specialty.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <Label htmlFor="bio">Giới thiệu</Label>
                    <textarea
                      id="bio"
                      value={formData.bio}
                      onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                      rows={3}
                      className="mt-2 w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                    />
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="experience_years">Số năm kinh nghiệm</Label>
                      <Input
                        id="experience_years"
                        type="number"
                        min="0"
                        value={formData.experience_years}
                        onChange={(e) => setFormData({ ...formData, experience_years: e.target.value })}
                        className="mt-2"
                      />
                    </div>
                    <div>
                      <Label htmlFor="consultation_fee">Phí khám (VNĐ)</Label>
                      <Input
                        id="consultation_fee"
                        type="number"
                        min="0"
                        value={formData.consultation_fee}
                        onChange={(e) => setFormData({ ...formData, consultation_fee: e.target.value })}
                        className="mt-2"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Department Head Permissions */}
              {selectedRole === 'department_head' && (
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-700 border-b pb-2">Phân quyền trưởng khoa</h3>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="can_manage_doctors"
                        checked={formData.can_manage_doctors}
                        onCheckedChange={(checked) => setFormData({ ...formData, can_manage_doctors: checked })}
                      />
                      <label htmlFor="can_manage_doctors" className="text-sm cursor-pointer">
                        Quản lý bác sĩ
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="can_manage_patients"
                        checked={formData.can_manage_patients}
                        onCheckedChange={(checked) => setFormData({ ...formData, can_manage_patients: checked })}
                      />
                      <label htmlFor="can_manage_patients" className="text-sm cursor-pointer">
                        Quản lý bệnh nhân
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="can_manage_appointments"
                        checked={formData.can_manage_appointments}
                        onCheckedChange={(checked) => setFormData({ ...formData, can_manage_appointments: checked })}
                      />
                      <label htmlFor="can_manage_appointments" className="text-sm cursor-pointer">
                        Quản lý lịch hẹn
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="can_view_stats"
                        checked={formData.can_view_stats}
                        onCheckedChange={(checked) => setFormData({ ...formData, can_view_stats: checked })}
                      />
                      <label htmlFor="can_view_stats" className="text-sm cursor-pointer">
                        Xem thống kê
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="can_manage_specialties"
                        checked={formData.can_manage_specialties}
                        onCheckedChange={(checked) => setFormData({ ...formData, can_manage_specialties: checked })}
                      />
                      <label htmlFor="can_manage_specialties" className="text-sm cursor-pointer">
                        Quản lý chuyên khoa
                      </label>
                    </div>
                  </div>
                </div>
              )}

              <div className="flex gap-3 pt-4">
                <Button 
                  type="submit" 
                  disabled={loading} 
                  className="bg-gradient-to-r from-teal-500 to-cyan-500"
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  {loading ? 'Đang tạo...' : 'Tạo tài khoản'}
                </Button>
                <Button type="button" variant="outline" onClick={resetForm}>
                  Đặt lại
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Layout>
  );
}

function RoleCard({ icon, title, role, selected, onClick }) {
  return (
    <div
      onClick={onClick}
      className={`p-6 rounded-xl border-2 cursor-pointer transition-all ${
        selected
          ? 'border-teal-500 bg-teal-50 shadow-lg'
          : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
      }`}
    >
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-3 ${
        selected
          ? 'bg-gradient-to-br from-teal-500 to-cyan-500 text-white'
          : 'bg-gray-100 text-gray-600'
      }`}>
        {icon}
      </div>
      <h3 className={`font-semibold ${selected ? 'text-teal-700' : 'text-gray-900'}`}>
        {title}
      </h3>
    </div>
  );
}
