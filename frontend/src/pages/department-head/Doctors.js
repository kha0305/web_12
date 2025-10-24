import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Search, CheckCircle, XCircle, Trash2, Eye } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export default function Doctors() {
  const { t } = useLanguage();
  const [doctors, setDoctors] = useState([]);
  const [filteredDoctors, setFilteredDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    fetchDoctors();
  }, []);

  useEffect(() => {
    filterDoctors();
  }, [doctors, searchTerm, statusFilter]);

  const fetchDoctors = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/api/department-head/doctors`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDoctors(response.data);
    } catch (error) {
      toast.error(t('errorFetchingDoctors'));
    } finally {
      setLoading(false);
    }
  };

  const filterDoctors = () => {
    let filtered = [...doctors];

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(doctor =>
        doctor.user_info?.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doctor.user_info?.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doctor.specialty_name?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(doctor => doctor.status === statusFilter);
    }

    setFilteredDoctors(filtered);
  };

  const handleApprove = async (doctorId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_BASE_URL}/api/department-head/approve-doctor/${doctorId}?status=approved`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success(t('doctorApprovedSuccess'));
      fetchDoctors();
    } catch (error) {
      toast.error(t('errorApprovingDoctor'));
    }
  };

  const handleReject = async (doctorId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_BASE_URL}/api/department-head/approve-doctor/${doctorId}?status=rejected`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success(t('doctorRejectedSuccess'));
      fetchDoctors();
    } catch (error) {
      toast.error(t('errorRejectingDoctor'));
    }
  };

  const handleDelete = async (doctorId) => {
    if (!window.confirm(t('confirmDeleteDoctor'))) return;

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_BASE_URL}/api/department-head/remove-doctor/${doctorId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success(t('doctorDeletedSuccess'));
      fetchDoctors();
    } catch (error) {
      toast.error(error.response?.data?.detail || t('errorDeletingDoctor'));
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      approved: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      rejected: 'bg-red-100 text-red-800'
    };
    const labels = {
      approved: t('approved'),
      pending: t('pending'),
      rejected: t('rejected')
    };
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">{t('manageDoctors')}</h1>
          <p className="text-gray-600 mt-1">{t('manageDoctorsSubtitle')}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder={t('searchDoctors')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">{t('allStatus')}</option>
            <option value="approved">{t('approved')}</option>
            <option value="pending">{t('pending')}</option>
            <option value="rejected">{t('rejected')}</option>
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <p className="text-gray-600 text-sm">{t('totalDoctors')}</p>
          <p className="text-2xl font-bold text-gray-800">{doctors.length}</p>
        </div>
        <div className="bg-green-50 rounded-lg shadow-md p-4">
          <p className="text-green-600 text-sm">{t('approved')}</p>
          <p className="text-2xl font-bold text-green-800">
            {doctors.filter(d => d.status === 'approved').length}
          </p>
        </div>
        <div className="bg-yellow-50 rounded-lg shadow-md p-4">
          <p className="text-yellow-600 text-sm">{t('pending')}</p>
          <p className="text-2xl font-bold text-yellow-800">
            {doctors.filter(d => d.status === 'pending').length}
          </p>
        </div>
      </div>

      {/* Doctors Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('doctor')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('specialty')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('experience')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('fee')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('status')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('actions')}
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredDoctors.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                    {t('noDoctorsFound')}
                  </td>
                </tr>
              ) : (
                filteredDoctors.map((doctor) => (
                  <tr key={doctor.user_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {doctor.user_info?.full_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {doctor.user_info?.email}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{doctor.specialty_name}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">
                        {doctor.experience_years} {t('years')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">
                        {doctor.consultation_fee?.toLocaleString()} VNĐ
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(doctor.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        {doctor.status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleApprove(doctor.user_id)}
                              className="text-green-600 hover:text-green-900"
                              title={t('approve')}
                            >
                              <CheckCircle className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => handleReject(doctor.user_id)}
                              className="text-red-600 hover:text-red-900"
                              title={t('reject')}
                            >
                              <XCircle className="w-5 h-5" />
                            </button>
                          </>
                        )}
                        <button
                          onClick={() => handleDelete(doctor.user_id)}
                          className="text-red-600 hover:text-red-900"
                          title={t('delete')}
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
