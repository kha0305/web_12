import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Users, UserCheck, UserPlus, Calendar, ClipboardCheck, TrendingUp } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export default function DepartmentHeadDashboard() {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/api/department-head/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, title, value, subtitle, color, onClick }) => (
    <div 
      className={`bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm mb-1">{title}</p>
          <h3 className="text-3xl font-bold text-gray-800">{value}</h3>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
      </div>
    </div>
  );

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
          <h1 className="text-3xl font-bold text-gray-800">{t('departmentHeadDashboard')}</h1>
          <p className="text-gray-600 mt-1">{t('welcomeBack')}</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard
          icon={Users}
          title={t('totalDoctors')}
          value={stats?.total_doctors || 0}
          subtitle={`${stats?.approved_doctors || 0} ${t('approved')}`}
          color="bg-blue-500"
          onClick={() => navigate('/department-head/doctors')}
        />
        
        <StatCard
          icon={UserCheck}
          title={t('approvedDoctors')}
          value={stats?.approved_doctors || 0}
          subtitle={`${stats?.pending_doctors || 0} ${t('pending')}`}
          color="bg-green-500"
          onClick={() => navigate('/department-head/doctors')}
        />
        
        <StatCard
          icon={UserPlus}
          title={t('totalPatients')}
          value={stats?.total_patients || 0}
          color="bg-purple-500"
          onClick={() => navigate('/department-head/patients')}
        />
        
        <StatCard
          icon={Calendar}
          title={t('totalAppointments')}
          value={stats?.total_appointments || 0}
          color="bg-orange-500"
        />
        
        <StatCard
          icon={ClipboardCheck}
          title={t('completedAppointments')}
          value={stats?.completed_appointments || 0}
          color="bg-teal-500"
        />
        
        <StatCard
          icon={TrendingUp}
          title={t('successRate')}
          value={stats?.total_appointments > 0 
            ? `${Math.round((stats?.completed_appointments / stats?.total_appointments) * 100)}%`
            : '0%'}
          color="bg-indigo-500"
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">{t('quickActions')}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/department-head/create-accounts')}
            className="flex items-center justify-center space-x-2 bg-blue-500 hover:bg-blue-600 text-white py-3 px-6 rounded-lg transition-colors"
          >
            <UserPlus className="w-5 h-5" />
            <span>{t('createAccount')}</span>
          </button>
          
          <button
            onClick={() => navigate('/department-head/doctors')}
            className="flex items-center justify-center space-x-2 bg-green-500 hover:bg-green-600 text-white py-3 px-6 rounded-lg transition-colors"
          >
            <Users className="w-5 h-5" />
            <span>{t('manageDoctors')}</span>
          </button>
          
          <button
            onClick={() => navigate('/department-head/patients')}
            className="flex items-center justify-center space-x-2 bg-purple-500 hover:bg-purple-600 text-white py-3 px-6 rounded-lg transition-colors"
          >
            <Users className="w-5 h-5" />
            <span>{t('managePatients')}</span>
          </button>
        </div>
      </div>

      {/* Info Card */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">{t('departmentHeadInfo')}</h3>
            <p className="mt-2 text-sm text-blue-700">
              {t('departmentHeadInfoText')}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
