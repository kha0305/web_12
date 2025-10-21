import React, { useContext, useEffect, useState } from 'react';
import { AuthContext, API } from '@/App';
import axios from 'axios';
import { toast } from 'sonner';
import Layout from '@/components/Layout';
import { Users, Calendar, CheckCircle, XCircle, Clock, TrendingUp } from 'lucide-react';

export default function AdminStats() {
  const { token } = useContext(AuthContext);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/admin/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      toast.error('Không thể tải thống kê');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 p-6 flex items-center justify-center">
          <p className="text-gray-500">Đang tải...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Thống kê hệ thống</h1>

          {/* User Stats */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Người dùng</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <StatCard
                icon={<Users className="w-8 h-8" />}
                title="Bệnh nhân"
                value={stats.total_patients}
                color="from-blue-500 to-indigo-500"
                testId="patients-stat"
              />
              <StatCard
                icon={<Users className="w-8 h-8" />}
                title="Bác sĩ"
                value={stats.total_doctors}
                color="from-teal-500 to-cyan-500"
                testId="doctors-stat"
              />
              <StatCard
                icon={<Calendar className="w-8 h-8" />}
                title="Tổng lịch hẹn"
                value={stats.total_appointments}
                color="from-purple-500 to-pink-500"
                testId="total-appointments-stat"
              />
            </div>
          </div>

          {/* Appointment Stats */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Trạng thái lịch hẹn</h2>
            <div className="grid md:grid-cols-4 gap-6">
              <StatCard
                icon={<Clock className="w-6 h-6" />}
                title="Chờ xác nhận"
                value={stats.pending_appointments}
                color="from-yellow-500 to-orange-500"
                testId="pending-appointments-stat"
              />
              <StatCard
                icon={<CheckCircle className="w-6 h-6" />}
                title="Đã xác nhận"
                value={stats.confirmed_appointments}
                color="from-green-500 to-emerald-500"
                testId="confirmed-appointments-stat"
              />
              <StatCard
                icon={<CheckCircle className="w-6 h-6" />}
                title="Hoàn thành"
                value={stats.completed_appointments}
                color="from-blue-500 to-cyan-500"
                testId="completed-appointments-stat"
              />
              <StatCard
                icon={<XCircle className="w-6 h-6" />}
                title="Đã hủy"
                value={stats.cancelled_appointments}
                color="from-red-500 to-pink-500"
                testId="cancelled-appointments-stat"
              />
            </div>
          </div>

          {/* Consultation Type Stats */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Loại hình tư vấn</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <StatCard
                icon={<TrendingUp className="w-8 h-8" />}
                title="Tư vấn online"
                value={stats.online_consultations}
                color="from-teal-500 to-cyan-500"
                testId="online-consultations-stat"
              />
              <StatCard
                icon={<Users className="w-8 h-8" />}
                title="Khám trực tiếp"
                value={stats.in_person_consultations}
                color="from-purple-500 to-pink-500"
                testId="in-person-consultations-stat"
              />
            </div>
          </div>

          {/* Doctor Approval Stats */}
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-4">Trạng thái duyệt bác sĩ</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <StatCard
                icon={<Clock className="w-8 h-8" />}
                title="Chờ duyệt"
                value={stats.pending_doctors}
                color="from-yellow-500 to-orange-500"
                testId="pending-doctors-stat"
              />
              <StatCard
                icon={<CheckCircle className="w-8 h-8" />}
                title="Đã duyệt"
                value={stats.approved_doctors}
                color="from-green-500 to-emerald-500"
                testId="approved-doctors-stat"
              />
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

function StatCard({ icon, title, value, color, testId }) {
  return (
    <div data-testid={testId} className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all">
      <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center text-white mb-4`}>
        {icon}
      </div>
      <p className="text-gray-600 text-sm mb-1">{title}</p>
      <p className="text-4xl font-bold text-gray-900">{value || 0}</p>
    </div>
  );
}
