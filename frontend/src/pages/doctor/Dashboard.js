import React, { useContext, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext, API } from '@/App';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Calendar, Users, Clock, LogOut, AlertCircle } from 'lucide-react';
import Layout from '@/components/Layout';

export default function DoctorDashboard() {
  const navigate = useNavigate();
  const { user, token, logout } = useContext(AuthContext);
  const [appointments, setAppointments] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [appointmentsRes, profileRes] = await Promise.all([
        axios.get(`${API}/appointments/my`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/doctors/${user.id}`)
      ]);
      setAppointments(appointmentsRes.data.slice(0, 3));
      setProfile(profileRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const pendingCount = appointments.filter(a => a.status === 'pending').length;
  const todayCount = appointments.filter(a => a.appointment_date === new Date().toISOString().split('T')[0]).length;

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Xin chào, BS. {user?.full_name}!</h1>
              <p className="text-gray-600 mt-1">Quản lý lịch khám của bạn</p>
            </div>
            <Button data-testid="logout-btn" variant="outline" onClick={logout}>
              <LogOut className="w-4 h-4 mr-2" />
              Đăng xuất
            </Button>
          </div>

          {/* Status Warning */}
          {profile?.status === 'pending' && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-6 mb-8 flex items-start gap-4">
              <AlertCircle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-bold text-yellow-900 mb-1">Tài khoản đang chờ duyệt</h3>
                <p className="text-yellow-800">Tài khoản của bạn đang được admin xem xét. Vui lòng hoàn thiện hồ sơ để được duyệt nhanh hơn.</p>
                <Button data-testid="complete-profile-btn" onClick={() => navigate('/doctor/profile')} className="mt-3 bg-yellow-600 hover:bg-yellow-700">
                  Hoàn thiện hồ sơ
                </Button>
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <StatCard
              icon={<Clock className="w-8 h-8" />}
              title="Chờ xác nhận"
              value={pendingCount}
              color="from-yellow-500 to-orange-500"
              testId="pending-stat"
            />
            <StatCard
              icon={<Calendar className="w-8 h-8" />}
              title="Lịch hôm nay"
              value={todayCount}
              color="from-teal-500 to-cyan-500"
              testId="today-stat"
            />
            <StatCard
              icon={<Users className="w-8 h-8" />}
              title="Tổng lịch hẹn"
              value={appointments.length}
              color="from-blue-500 to-indigo-500"
              testId="total-stat"
            />
          </div>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <QuickActionCard
              icon={<Calendar className="w-8 h-8" />}
              title="Lịch hẹn"
              description="Xem và quản lý lịch hẹn"
              onClick={() => navigate('/doctor/appointments')}
              testId="appointments-card"
            />
            <QuickActionCard
              icon={<Users className="w-8 h-8" />}
              title="Hồ sơ"
              description="Cập nhật thông tin cá nhân"
              onClick={() => navigate('/doctor/profile')}
              testId="profile-card"
            />
            <QuickActionCard
              icon={<Clock className="w-8 h-8" />}
              title="Lịch làm việc"
              description="Thiết lập khung giờ rảnh"
              onClick={() => navigate('/doctor/schedule')}
              testId="schedule-card"
            />
          </div>

          {/* Recent Appointments */}
          <div className="bg-white rounded-3xl shadow-xl p-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Lịch hẹn mới nhất</h2>
              <Button data-testid="view-all-btn" variant="outline" onClick={() => navigate('/doctor/appointments')}>
                Xem tất cả
              </Button>
            </div>

            {loading ? (
              <p className="text-center text-gray-500 py-8">Đang tải...</p>
            ) : appointments.length === 0 ? (
              <div className="text-center py-12">
                <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">Chưa có lịch hẹn nào</p>
              </div>
            ) : (
              <div className="space-y-4">
                {appointments.map((apt) => (
                  <AppointmentCard key={apt.id} appointment={apt} navigate={navigate} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}

function StatCard({ icon, title, value, color, testId }) {
  return (
    <div data-testid={testId} className="bg-white rounded-2xl p-6 shadow-lg">
      <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center text-white mb-4`}>
        {icon}
      </div>
      <p className="text-gray-600 text-sm mb-1">{title}</p>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

function QuickActionCard({ icon, title, description, onClick, testId }) {
  return (
    <div
      data-testid={testId}
      onClick={onClick}
      className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all cursor-pointer hover:-translate-y-1"
    >
      <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center text-white mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-2 text-gray-900">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}

function AppointmentCard({ appointment, navigate }) {
  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    confirmed: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    completed: 'bg-blue-100 text-blue-800'
  };

  const statusText = {
    pending: 'Chờ xác nhận',
    confirmed: 'Đã xác nhận',
    cancelled: 'Đã hủy',
    completed: 'Hoàn thành'
  };

  return (
    <div className="border border-gray-200 rounded-xl p-4 hover:border-teal-300 transition-colors">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="font-bold text-lg text-gray-900">{appointment.patient_name || 'Bệnh nhân'}</h3>
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${statusColors[appointment.status]}`}>
              {statusText[appointment.status]}
            </span>
          </div>
          <p className="text-gray-600 mb-1">
            <Clock className="w-4 h-4 inline mr-2" />
            {appointment.appointment_date} - {appointment.appointment_time}
          </p>
          {appointment.symptoms && (
            <p className="text-gray-500 text-sm">Triệu chứng: {appointment.symptoms}</p>
          )}
        </div>
        <Button data-testid={`view-appointment-${appointment.id}`} size="sm" onClick={() => navigate('/doctor/appointments')} variant="outline">
          Xem chi tiết
        </Button>
      </div>
    </div>
  );
}
