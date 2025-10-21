import React, { useContext, useEffect, useState } from 'react';
import { AuthContext, API } from '@/App';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import Layout from '@/components/Layout';
import { User } from 'lucide-react';

export default function DoctorProfile() {
  const { user, token } = useContext(AuthContext);
  const [profile, setProfile] = useState(null);
  const [specialties, setSpecialties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    specialty_id: '',
    bio: '',
    experience_years: 0,
    consultation_fee: 0
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [profileRes, specialtiesRes] = await Promise.all([
        axios.get(`${API}/doctors/${user.id}`),
        axios.get(`${API}/specialties`)
      ]);
      setProfile(profileRes.data);
      setSpecialties(specialtiesRes.data);
      setFormData({
        specialty_id: profileRes.data.specialty_id || '',
        bio: profileRes.data.bio || '',
        experience_years: profileRes.data.experience_years || 0,
        consultation_fee: profileRes.data.consultation_fee || 0
      });
    } catch (error) {
      toast.error('Không thể tải thông tin');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      await axios.put(`${API}/doctors/profile`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Cập nhật hồ sơ thành công!');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Cập nhật thất bại');
    } finally {
      setSaving(false);
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
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Hồ sơ bác sĩ</h1>

          <div className="bg-white rounded-3xl shadow-xl p-8">
            <div className="flex items-center gap-4 mb-8 pb-8 border-b">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center text-white text-3xl font-bold">
                {user?.full_name?.charAt(0) || 'D'}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{user?.full_name}</h2>
                <p className="text-gray-600">{user?.email}</p>
                <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs font-semibold ${
                  profile.status === 'approved' ? 'bg-green-100 text-green-800' :
                  profile.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {profile.status === 'approved' ? 'Đã duyệt' : 
                   profile.status === 'pending' ? 'Chờ duyệt' : 'Đã từ chối'}
                </span>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <Label htmlFor="specialty_id">Chuyên khoa *</Label>
                <Select value={formData.specialty_id} onValueChange={(v) => setFormData({ ...formData, specialty_id: v })}>
                  <SelectTrigger data-testid="specialty-select" className="mt-2">
                    <SelectValue placeholder="Chọn chuyên khoa" />
                  </SelectTrigger>
                  <SelectContent>
                    {specialties.map(s => (
                      <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="bio">Giới thiệu</Label>
                <Textarea
                  data-testid="bio-input"
                  id="bio"
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  placeholder="Giới thiệu về bản thân, kinh nghiệm, chuyên môn..."
                  className="mt-2"
                  rows={5}
                />
              </div>

              <div>
                <Label htmlFor="experience_years">Số năm kinh nghiệm</Label>
                <Input
                  data-testid="experience-input"
                  id="experience_years"
                  type="number"
                  min="0"
                  value={formData.experience_years}
                  onChange={(e) => setFormData({ ...formData, experience_years: parseInt(e.target.value) || 0 })}
                  className="mt-2"
                />
              </div>

              <div>
                <Label htmlFor="consultation_fee">Phí tư vấn (VNĐ)</Label>
                <Input
                  data-testid="fee-input"
                  id="consultation_fee"
                  type="number"
                  min="0"
                  step="1000"
                  value={formData.consultation_fee}
                  onChange={(e) => setFormData({ ...formData, consultation_fee: parseFloat(e.target.value) || 0 })}
                  className="mt-2"
                />
              </div>

              <Button data-testid="save-profile-btn" type="submit" disabled={saving} className="w-full bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-600 hover:to-cyan-600">
                {saving ? 'Đang lưu...' : 'Lưu thay đổi'}
              </Button>
            </form>
          </div>
        </div>
      </div>
    </Layout>
  );
}
