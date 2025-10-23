import React, { useContext, useEffect, useState } from 'react';
import { AuthContext, API } from '@/App';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import Layout from '@/components/Layout';
import { Search, CheckCircle, XCircle, Clock, Trash2 } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';

export default function AdminDoctors() {
  const { token } = useContext(AuthContext);
  const { t } = useLanguage();
  const [doctors, setDoctors] = useState([]);
  const [filteredDoctors, setFilteredDoctors] = useState([]);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDoctors();
  }, []);

  useEffect(() => {
    filterDoctors();
  }, [statusFilter, searchQuery, doctors]);

  const fetchDoctors = async () => {
    try {
      const response = await axios.get(`${API}/admin/doctors`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDoctors(response.data);
      setFilteredDoctors(response.data);
    } catch (error) {
      toast.error('Không thể tải danh sách bác sĩ');
    } finally {
      setLoading(false);
    }
  };

  const filterDoctors = () => {
    let filtered = doctors;

    if (statusFilter !== 'all') {
      filtered = filtered.filter(d => d.status === statusFilter);
    }

    if (searchQuery) {
      filtered = filtered.filter(d => 
        d.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.specialty_name?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredDoctors(filtered);
  };

  const handleApprove = async (doctorId, status) => {
    try {
      await axios.put(`${API}/admin/doctors/${doctorId}/approve?status=${status}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success(status === 'approved' ? 'Duyệt bác sĩ thành công' : 'Đã từ chối bác sĩ');
      fetchDoctors();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Cập nhật thất bại');
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Quản lý bác sĩ</h1>

          {/* Filters */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <Input
                    data-testid="search-input"
                    placeholder="Tìm theo tên, email hoặc chuyên khoa..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <div>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger data-testid="status-filter">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Tất cả trạng thái</SelectItem>
                    <SelectItem value="pending">Chờ duyệt</SelectItem>
                    <SelectItem value="approved">Đã duyệt</SelectItem>
                    <SelectItem value="rejected">Đã từ chối</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Doctors List */}
          {loading ? (
            <p className="text-center text-gray-500">Đang tải...</p>
          ) : filteredDoctors.length === 0 ? (
            <div className="bg-white rounded-2xl p-12 text-center">
              <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Không tìm thấy bác sĩ phù hợp</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredDoctors.map(doctor => (
                <DoctorCard key={doctor.user_id} doctor={doctor} onApprove={handleApprove} />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

function DoctorCard({ doctor, onApprove }) {
  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    approved: 'bg-green-100 text-green-800 border-green-200',
    rejected: 'bg-red-100 text-red-800 border-red-200'
  };

  const statusText = {
    pending: 'Chờ duyệt',
    approved: 'Đã duyệt',
    rejected: 'Đã từ chối'
  };

  const statusIcons = {
    pending: <Clock className="w-4 h-4" />,
    approved: <CheckCircle className="w-4 h-4" />,
    rejected: <XCircle className="w-4 h-4" />
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex justify-between items-start">
        <div className="flex gap-4 flex-1">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center text-white text-2xl font-bold flex-shrink-0">
            {doctor.full_name?.charAt(0) || 'D'}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="font-bold text-xl text-gray-900">{doctor.full_name || 'Bác sĩ'}</h3>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold border flex items-center gap-1 ${statusColors[doctor.status]}`}>
                {statusIcons[doctor.status]}
                {statusText[doctor.status]}
              </span>
            </div>
            <p className="text-gray-600 mb-2">{doctor.email}</p>
            {doctor.specialty_name && (
              <p className="text-teal-600 font-semibold mb-2">Chuyên khoa: {doctor.specialty_name}</p>
            )}
            {doctor.bio && (
              <p className="text-gray-600 text-sm mb-2 line-clamp-2">{doctor.bio}</p>
            )}
            <div className="flex gap-4 text-sm text-gray-600">
              {doctor.experience_years > 0 && (
                <span>{doctor.experience_years} năm kinh nghiệm</span>
              )}
              {doctor.consultation_fee > 0 && (
                <span>Phí: {doctor.consultation_fee.toLocaleString()} VNĐ</span>
              )}
            </div>
          </div>
        </div>
        
        {doctor.status === 'pending' && (
          <div className="flex gap-2">
            <Button 
              data-testid={`approve-${doctor.user_id}`}
              onClick={() => onApprove(doctor.user_id, 'approved')} 
              className="bg-green-600 hover:bg-green-700"
              size="sm"
            >
              <CheckCircle className="w-4 h-4 mr-1" />
              Duyệt
            </Button>
            <Button 
              data-testid={`reject-${doctor.user_id}`}
              onClick={() => onApprove(doctor.user_id, 'rejected')} 
              variant="outline"
              className="border-red-300 text-red-600 hover:bg-red-50"
              size="sm"
            >
              <XCircle className="w-4 h-4 mr-1" />
              Từ chối
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
