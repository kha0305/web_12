import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { UserPlus, User, Stethoscope } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export default function CreateAccounts() {
  const { t } = useLanguage();
  const [selectedRole, setSelectedRole] = useState('patient');
  const [specialties, setSpecialties] = useState([]);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    phone: '',
    date_of_birth: '',
    address: '',
    // Doctor specific
    specialty_id: '',
    bio: '',
    experience_years: '',
    consultation_fee: ''
  });

  useEffect(() => {
    fetchSpecialties();
  }, []);

  const fetchSpecialties = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/specialties`);
      setSpecialties(response.data);
    } catch (error) {
      console.error('Error fetching specialties:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
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
        payload.bio = formData.bio || '';
        payload.experience_years = parseInt(formData.experience_years) || 0;
        payload.consultation_fee = parseFloat(formData.consultation_fee) || 0;
      }

      await axios.post(
        `${API_BASE_URL}/api/department-head/create-user`,
        payload,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success(t('accountCreatedSuccess'));
      
      // Reset form
      setFormData({
        email: '',
        password: '',
        full_name: '',
        phone: '',
        date_of_birth: '',
        address: '',
        specialty_id: '',
        bio: '',
        experience_years: '',
        consultation_fee: ''
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || t('accountCreatedError'));
    }
  };

  const RoleCard = ({ icon: Icon, title, role, selected, onClick }) => (
    <div
      onClick={onClick}
      className={`flex flex-col items-center p-6 border-2 rounded-lg cursor-pointer transition-all ${
        selected
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-200 hover:border-gray-300'
      }`}
    >
      <Icon className={`w-12 h-12 ${selected ? 'text-blue-500' : 'text-gray-400'}`} />
      <span className={`mt-2 font-semibold ${selected ? 'text-blue-700' : 'text-gray-600'}`}>
        {title}
      </span>
    </div>
  );

  const getRoleName = (role) => {
    const names = {
      patient: t('patient'),
      doctor: t('doctor')
    };
    return names[role] || role;
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6">
        {/* Header */}
        <div className="border-b pb-4 mb-6">
          <h2 className="text-2xl font-bold text-gray-800">{t('createNewAccount')}</h2>
          <p className="text-gray-600 mt-1">{t('createAccountSubtitle')}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Role Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              {t('selectRole')} <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-2 gap-4">
              <RoleCard
                icon={User}
                title={t('patient')}
                role="patient"
                selected={selectedRole === 'patient'}
                onClick={() => setSelectedRole('patient')}
              />
              <RoleCard
                icon={Stethoscope}
                title={t('doctor')}
                role="doctor"
                selected={selectedRole === 'doctor'}
                onClick={() => setSelectedRole('doctor')}
              />
            </div>
          </div>

          {/* Account Info */}
          <div className="border-t pt-6">
            <h3 className="font-semibold text-gray-700 mb-4">{t('accountInfo')}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('email')} <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="email@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('password')} <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  minLength={6}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('fullName')} <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('phone')}
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('dateOfBirth')}
                </label>
                <input
                  type="date"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('address')}
                </label>
                <input
                  type="text"
                  name="address"
                  value={formData.address}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Doctor Specific Fields */}
          {selectedRole === 'doctor' && (
            <div className="border-t pt-6">
              <h3 className="font-semibold text-gray-700 mb-4">{t('doctorInfo')}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('specialty')} <span className="text-red-500">*</span>
                  </label>
                  <select
                    name="specialty_id"
                    value={formData.specialty_id}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">{t('selectSpecialty')}</option>
                    {specialties.map(spec => (
                      <option key={spec.id} value={spec.id}>{spec.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('experienceYears')}
                  </label>
                  <input
                    type="number"
                    name="experience_years"
                    value={formData.experience_years}
                    onChange={handleInputChange}
                    min="0"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('consultationFee')}
                  </label>
                  <input
                    type="number"
                    name="consultation_fee"
                    value={formData.consultation_fee}
                    onChange={handleInputChange}
                    min="0"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('bio')}
                  </label>
                  <textarea
                    name="bio"
                    value={formData.bio}
                    onChange={handleInputChange}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder={t('bioPlaceholder')}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={() => setFormData({
                email: '',
                password: '',
                full_name: '',
                phone: '',
                date_of_birth: '',
                address: '',
                specialty_id: '',
                bio: '',
                experience_years: '',
                consultation_fee: ''
              })}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              {t('reset')}
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
            >
              <UserPlus className="w-5 h-5" />
              <span>{t('createAccount')}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
