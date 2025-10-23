import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '@/App';
import { Button } from '@/components/ui/button';
import { Users, FileText, BarChart, LogOut, Shield, UserPlus } from 'lucide-react';
import Layout from '@/components/Layout';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Xin chào, Admin {user?.full_name}!</h1>
              <p className="text-gray-600 mt-1">Quản lý hệ thống MediSchedule</p>
            </div>
            <Button data-testid="logout-btn" variant="outline" onClick={logout}>
              <LogOut className="w-4 h-4 mr-2" />
              Đăng xuất
            </Button>
          </div>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <QuickActionCard
              icon={<Users className="w-8 h-8" />}
              title="Quản lý bác sĩ"
              description="Duyệt và quản lý tài khoản bác sĩ"
              onClick={() => navigate('/admin/doctors')}
              testId="doctors-card"
            />
            <QuickActionCard
              icon={<FileText className="w-8 h-8" />}
              title="Danh sách bệnh nhân"
              description="Xem danh sách bệnh nhân đăng ký"
              onClick={() => navigate('/admin/patients')}
              testId="patients-card"
            />
            <QuickActionCard
              icon={<BarChart className="w-8 h-8" />}
              title="Thống kê"
              description="Xem báo cáo và thống kê hệ thống"
              onClick={() => navigate('/admin/stats')}
              testId="stats-card"
            />
            {user?.admin_permissions?.can_create_admins && (
              <QuickActionCard
                icon={<Shield className="w-8 h-8" />}
                title="Quản lý Admin"
                description="Tạo và quản lý tài khoản admin"
                onClick={() => navigate('/admin/admins')}
                testId="admins-card"
              />
            )}
          </div>
        </div>
      </div>
    </Layout>
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
