import React, { useContext, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext, API } from '@/App';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { Search, MapPin, Star, Calendar } from 'lucide-react';
import Layout from '@/components/Layout';

export default function SearchDoctors() {
  const { token } = useContext(AuthContext);
  const [specialties, setSpecialties] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [filteredDoctors, setFilteredDoctors] = useState([]);
  const [selectedSpecialty, setSelectedSpecialty] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [showBooking, setShowBooking] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    filterDoctors();
  }, [selectedSpecialty, searchQuery, doctors]);

  const fetchData = async () => {
    try {
      const [specialtiesRes, doctorsRes] = await Promise.all([
        axios.get(`${API}/specialties`),
        axios.get(`${API}/doctors`)
      ]);
      setSpecialties(specialtiesRes.data);
      setDoctors(doctorsRes.data);
      setFilteredDoctors(doctorsRes.data);
    } catch (error) {
      toast.error('Không thể tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const filterDoctors = () => {
    let filtered = doctors;

    if (selectedSpecialty !== 'all') {
      filtered = filtered.filter(d => d.specialty_id === selectedSpecialty);
    }

    if (searchQuery) {
      filtered = filtered.filter(d => 
        d.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.specialty_name?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredDoctors(filtered);
  };

  const handleBookAppointment = (doctor) => {
    setSelectedDoctor(doctor);
    setShowBooking(true);
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Tìm kiếm bác sĩ</h1>

          {/* Filters */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label>Tìm kiếm</Label>
                <div className="relative mt-2">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <Input
                    data-testid="search-input"
                    placeholder="Tìm theo tên bác sĩ hoặc chuyên khoa..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <div>
                <Label>Chuyên khoa</Label>
                <Select value={selectedSpecialty} onValueChange={setSelectedSpecialty}>
                  <SelectTrigger data-testid="specialty-filter" className="mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Tất cả chuyên khoa</SelectItem>
                    {specialties.map(s => (
                      <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Doctors Grid */}
          {loading ? (
            <p className="text-center text-gray-500">Đang tải...</p>
          ) : filteredDoctors.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-2xl">
              <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Không tìm thấy bác sĩ phù hợp</p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredDoctors.map(doctor => (
                <DoctorCard key={doctor.user_id} doctor={doctor} onBook={handleBookAppointment} />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Booking Dialog */}
      {showBooking && selectedDoctor && (
        <BookingDialog
          doctor={selectedDoctor}
          open={showBooking}
          onClose={() => {
            setShowBooking(false);
            setSelectedDoctor(null);
          }}
          token={token}
        />
      )}
    </Layout>
  );
}

function DoctorCard({ doctor, onBook }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all p-6">
      <div className="flex items-start gap-4 mb-4">
        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center text-white text-2xl font-bold">
          {doctor.full_name?.charAt(0) || 'D'}
        </div>
        <div className="flex-1">
          <h3 className="font-bold text-lg text-gray-900">{doctor.full_name || 'Bác sĩ'}</h3>
          <p className="text-teal-600 text-sm">{doctor.specialty_name || 'Chuyên khoa'}</p>
        </div>
      </div>
      
      {doctor.bio && (
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">{doctor.bio}</p>
      )}
      
      <div className="space-y-2 mb-4">
        {doctor.experience_years > 0 && (
          <p className="text-sm text-gray-600">
            <Star className="w-4 h-4 inline mr-2 text-yellow-500" />
            {doctor.experience_years} năm kinh nghiệm
          </p>
        )}
        {doctor.consultation_fee > 0 && (
          <p className="text-sm text-gray-600">
            <MapPin className="w-4 h-4 inline mr-2" />
            Phí tư vấn: {doctor.consultation_fee.toLocaleString()} VNĐ
          </p>
        )}
      </div>
      
      <Button 
        data-testid={`book-doctor-${doctor.user_id}`}
        onClick={() => onBook(doctor)} 
        className="w-full bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-600 hover:to-cyan-600"
      >
        Đặt lịch khám
      </Button>
    </div>
  );
}

function BookingDialog({ doctor, open, onClose, token }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    appointment_type: 'in_person',
    appointment_date: '',
    appointment_time: '',
    symptoms: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post(`${API}/appointments`, {
        ...formData,
        doctor_id: doctor.user_id
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Đặt lịch thành công!');
      onClose();
      navigate('/patient/appointments');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Đặt lịch thất bại');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Đặt lịch với {doctor.full_name}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Loại hình khám</Label>
            <Select value={formData.appointment_type} onValueChange={(v) => setFormData({ ...formData, appointment_type: v })}>
              <SelectTrigger data-testid="appointment-type-select" className="mt-2">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="in_person">Khám trực tiếp</SelectItem>
                <SelectItem value="online">Tư vấn online</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Ngày khám</Label>
            <Input
              data-testid="appointment-date-input"
              type="date"
              value={formData.appointment_date}
              onChange={(e) => setFormData({ ...formData, appointment_date: e.target.value })}
              required
              className="mt-2"
              min={new Date().toISOString().split('T')[0]}
            />
          </div>

          <div>
            <Label>Giờ khám</Label>
            <Input
              data-testid="appointment-time-input"
              type="time"
              value={formData.appointment_time}
              onChange={(e) => setFormData({ ...formData, appointment_time: e.target.value })}
              required
              className="mt-2"
            />
          </div>

          <div>
            <Label>Triệu chứng</Label>
            <Textarea
              data-testid="symptoms-input"
              value={formData.symptoms}
              onChange={(e) => setFormData({ ...formData, symptoms: e.target.value })}
              placeholder="Mô tả triệu chứng của bạn..."
              className="mt-2"
              rows={3}
            />
          </div>

          <div className="flex gap-3">
            <Button data-testid="cancel-booking-btn" type="button" variant="outline" onClick={onClose} className="flex-1">
              Hủy
            </Button>
            <Button data-testid="confirm-booking-btn" type="submit" disabled={loading} className="flex-1 bg-gradient-to-r from-teal-500 to-cyan-500">
              {loading ? 'Đang xử lý...' : 'Xác nhận'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
