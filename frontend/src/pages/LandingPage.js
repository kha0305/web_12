import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { AuthContext } from '@/App';
import { Calendar, Users, MessageSquare, Shield } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);

  React.useEffect(() => {
    if (user) {
      if (user.role === 'patient') navigate('/patient/dashboard');
      else if (user.role === 'doctor') navigate('/doctor/dashboard');
      else if (user.role === 'admin') navigate('/admin/dashboard');
    }
  }, [user, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50">
      {/* Header */}
      <header className="absolute top-0 left-0 right-0 z-10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-gray-800">MediSchedule</span>
          </div>
          <div className="flex gap-3">
            <Button data-testid="login-btn" variant="outline" onClick={() => navigate('/login')} className="border-teal-500 text-teal-600 hover:bg-teal-50">
              Đăng nhập
            </Button>
            <Button data-testid="register-btn" onClick={() => navigate('/register')} className="bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-600 hover:to-cyan-600">
              Đăng ký
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
                Đặt lịch khám bệnh
                <span className="block mt-2 bg-gradient-to-r from-teal-500 to-cyan-500 bg-clip-text text-transparent">
                  Dễ dàng & Nhanh chóng
                </span>
              </h1>
              <p className="text-lg text-gray-600">
                Kết nối bạn với các bác sĩ chuyên khoa hàng đầu. Đặt lịch khám online hoặc trực tiếp chỉ trong vài phút.
              </p>
              <div className="flex gap-4">
                <Button data-testid="get-started-btn" size="lg" onClick={() => navigate('/register')} className="bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-600 hover:to-cyan-600 text-lg px-8">
                  Bắt đầu ngay
                </Button>
                <Button data-testid="learn-more-btn" size="lg" variant="outline" className="border-teal-500 text-teal-600 hover:bg-teal-50 text-lg px-8">
                  Tìm hiểu thêm
                </Button>
              </div>
            </div>
            <div className="relative">
              <div className="aspect-square rounded-3xl bg-gradient-to-br from-teal-100 to-cyan-100 p-8 backdrop-blur-lg">
                <img
                  src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=600&h=600&fit=crop"
                  alt="Medical professionals"
                  className="w-full h-full object-cover rounded-2xl shadow-2xl"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6 bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-16 text-gray-900">Tính năng nổi bật</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <FeatureCard
              icon={<Calendar className="w-8 h-8" />}
              title="Đặt lịch dễ dàng"
              description="Chọn thời gian phù hợp và đặt lịch khám chỉ trong vài bước đơn giản"
            />
            <FeatureCard
              icon={<Users className="w-8 h-8" />}
              title="Bác sĩ chuyên khoa"
              description="Tìm kiếm và kết nối với các bác sĩ có chuyên môn phù hợp với bạn"
            />
            <FeatureCard
              icon={<MessageSquare className="w-8 h-8" />}
              title="Tư vấn online"
              description="Chat trực tiếp với bác sĩ để được tư vấn nhanh chóng và tiện lợi"
            />
            <FeatureCard
              icon={<Shield className="w-8 h-8" />}
              title="Bảo mật thông tin"
              description="Thông tin cá nhân và y tế của bạn được bảo vệ tuyệt đối"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900">
            Sẵn sàng chăm sóc sức khỏe của bạn?
          </h2>
          <p className="text-xl text-gray-600">
            Đăng ký ngay hôm nay và trải nghiệm dịch vụ y tế hiện đại
          </p>
          <Button data-testid="cta-register-btn" size="lg" onClick={() => navigate('/register')} className="bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-600 hover:to-cyan-600 text-lg px-12">
            Đăng ký miễn phí
          </Button>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="p-6 rounded-2xl bg-white shadow-lg hover:shadow-xl transition-all hover:-translate-y-1">
      <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center text-white mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-2 text-gray-900">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
