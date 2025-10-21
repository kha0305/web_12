import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { API } from '@/App';
import { toast } from 'sonner';
import axios from 'axios';
import { Calendar, ArrowLeft } from 'lucide-react';

export default function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post(`${API}/auth/forgot-password`, { email });
      toast.success('Nếu email tồn tại, link reset mật khẩu sẽ được gửi');
      setTimeout(() => navigate('/login'), 2000);
    } catch (error) {
      toast.error('Có lỗi xảy ra');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <Button data-testid="back-to-login-btn" variant="ghost" onClick={() => navigate('/login')} className="mb-6">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Về trang đăng nhập
        </Button>
        
        <div className="bg-white rounded-3xl shadow-2xl p-8">
          <div className="flex items-center justify-center gap-2 mb-8">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center">
              <Calendar className="w-7 h-7 text-white" />
            </div>
            <span className="text-3xl font-bold text-gray-800">MediSchedule</span>
          </div>

          <h2 className="text-2xl font-bold text-center mb-4 text-gray-900">Quên mật khẩu</h2>
          <p className="text-center text-gray-600 mb-8">Nhập email của bạn để nhận link reset mật khẩu</p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                data-testid="email-input"
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="mt-2"
              />
            </div>

            <Button data-testid="submit-forgot-btn" type="submit" disabled={loading} className="w-full bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-600 hover:to-cyan-600">
              {loading ? 'Đang xử lý...' : 'Gửi link reset'}
            </Button>
          </form>

          <p className="mt-6 text-center text-gray-600">
            Nhớ lại mật khẩu?{' '}
            <Link to="/login" className="text-teal-600 hover:text-teal-700 font-semibold">
              Đăng nhập
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
