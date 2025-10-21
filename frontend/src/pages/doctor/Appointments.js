import React, { useContext, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext, API } from '@/App';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar, Clock, MessageSquare } from 'lucide-react';
import Layout from '@/components/Layout';
import { toast } from 'sonner';

export default function DoctorAppointments() {
  const navigate = useNavigate();
  const { token } = useContext(AuthContext);
  const [appointments, setAppointments] = useState([]);
  const [filteredAppointments, setFilteredAppointments] = useState([]);
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAppointments();
  }, []);

  useEffect(() => {
    filterAppointments();
  }, [statusFilter, appointments]);

  const fetchAppointments = async () => {
    try {
      const response = await axios.get(`${API}/appointments/my`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAppointments(response.data);
      setFilteredAppointments(response.data);
    } catch (error) {
      toast.error('Không thể tải lịch hẹn');
    } finally {
      setLoading(false);
    }
  };

  const filterAppointments = () => {
    if (statusFilter === 'all') {
      setFilteredAppointments(appointments);
    } else {
      setFilteredAppointments(appointments.filter(a => a.status === statusFilter));
    }
  };

  const handleStatusChange = async (appointmentId, newStatus) => {
    try {
      await axios.put(`${API}/appointments/${appointmentId}/status`, 
        { status: newStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Cập nhật trạng thái thành công!');
      fetchAppointments();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Cập nhật thất bại');
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 p-6">
        <div className="max-w-5xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Quản lý lịch hẹn</h1>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger data-testid="status-filter" className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tất cả</SelectItem>
                <SelectItem value="pending">Chờ xác nhận</SelectItem>
                <SelectItem value="confirmed">Đã xác nhận</SelectItem>
                <SelectItem value="completed">Hoàn thành</SelectItem>
                <SelectItem value="cancelled">Đã hủy</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {loading ? (
            <p className="text-center text-gray-500">Đang tải...</p>
          ) : filteredAppointments.length === 0 ? (
            <div className="bg-white rounded-3xl shadow-xl p-12 text-center">
              <Calendar className="w-20 h-20 text-gray-300 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Không có lịch hẹn</h2>
              <p className="text-gray-600">Không tìm thấy lịch hẹn phù hợp với bộ lọc</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredAppointments.map(apt => (
                <AppointmentCard 
                  key={apt.id} 
                  appointment={apt} 
                  onStatusChange={handleStatusChange}
                  navigate={navigate}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

function AppointmentCard({ appointment, onStatusChange, navigate }) {
  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    confirmed: 'bg-green-100 text-green-800 border-green-200',
    cancelled: 'bg-red-100 text-red-800 border-red-200',
    completed: 'bg-blue-100 text-blue-800 border-blue-200'
  };

  const statusText = {
    pending: 'Chờ xác nhận',
    confirmed: 'Đã xác nhận',
    cancelled: 'Đã hủy',
    completed: 'Hoàn thành'
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-all">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <h3 className="font-bold text-xl text-gray-900">{appointment.patient_name || 'Bệnh nhân'}</h3>
            <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${statusColors[appointment.status]}`}>
              {statusText[appointment.status]}
            </span>
          </div>
          
          <div className="space-y-2 mb-4">
            <p className="text-gray-600">
              <Calendar className="w-4 h-4 inline mr-2" />
              {appointment.appointment_date}
            </p>
            <p className="text-gray-600">
              <Clock className="w-4 h-4 inline mr-2" />
              {appointment.appointment_time}
            </p>
            <p className="text-gray-600">
              Loại: <span className="font-semibold">{appointment.appointment_type === 'online' ? 'Tư vấn online' : 'Khám trực tiếp'}</span>
            </p>
            {appointment.symptoms && (
              <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm font-semibold text-gray-700 mb-1">Triệu chứng:</p>
                <p className="text-gray-600">{appointment.symptoms}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="flex gap-3">
        {appointment.status === 'pending' && (
          <>
            <Button 
              data-testid={`confirm-${appointment.id}`}
              onClick={() => onStatusChange(appointment.id, 'confirmed')} 
              className="flex-1 bg-green-600 hover:bg-green-700"
            >
              Xác nhận
            </Button>
            <Button 
              data-testid={`cancel-${appointment.id}`}
              onClick={() => onStatusChange(appointment.id, 'cancelled')} 
              variant="outline"
              className="flex-1 border-red-300 text-red-600 hover:bg-red-50"
            >
              Hủy
            </Button>
          </>
        )}
        {appointment.status === 'confirmed' && (
          <Button 
            data-testid={`complete-${appointment.id}`}
            onClick={() => onStatusChange(appointment.id, 'completed')} 
            className="flex-1 bg-blue-600 hover:bg-blue-700"
          >
            Đánh dấu hoàn thành
          </Button>
        )}
        {appointment.appointment_type === 'online' && (appointment.status === 'confirmed' || appointment.status === 'completed') && (
          <Button 
            data-testid={`chat-${appointment.id}`}
            onClick={() => navigate(`/doctor/chat/${appointment.id}`)} 
            className="flex-1 bg-gradient-to-r from-teal-500 to-cyan-500"
          >
            <MessageSquare className="w-4 h-4 mr-2" />
            Chat
          </Button>
        )}
      </div>
    </div>
  );
}
