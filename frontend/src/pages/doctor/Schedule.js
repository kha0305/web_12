import React, { useContext, useEffect, useState } from 'react';
import { AuthContext, API } from '@/App';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import Layout from '@/components/Layout';
import { Plus, Trash2, Clock } from 'lucide-react';

export default function DoctorSchedule() {
  const { user, token } = useContext(AuthContext);
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchSchedule();
  }, []);

  const fetchSchedule = async () => {
    try {
      const response = await axios.get(`${API}/doctors/${user.id}`);
      setSlots(response.data.available_slots || []);
    } catch (error) {
      toast.error('Không thể tải lịch làm việc');
    } finally {
      setLoading(false);
    }
  };

  const addSlot = () => {
    setSlots([...slots, { day: 'monday', start_time: '09:00', end_time: '17:00' }]);
  };

  const removeSlot = (index) => {
    setSlots(slots.filter((_, i) => i !== index));
  };

  const updateSlot = (index, field, value) => {
    const newSlots = [...slots];
    newSlots[index][field] = value;
    setSlots(newSlots);
  };

  const handleSave = async () => {
    setSaving(true);

    try {
      await axios.put(`${API}/doctors/schedule`, { available_slots: slots }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Cập nhật lịch làm việc thành công!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Cập nhật thất bại');
    } finally {
      setSaving(false);
    }
  };

  const dayNames = {
    monday: 'Thứ 2',
    tuesday: 'Thứ 3',
    wednesday: 'Thứ 4',
    thursday: 'Thứ 5',
    friday: 'Thứ 6',
    saturday: 'Thứ 7',
    sunday: 'Chủ nhật'
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
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Lịch làm việc</h1>
            <Button data-testid="add-slot-btn" onClick={addSlot} className="bg-gradient-to-r from-teal-500 to-cyan-500">
              <Plus className="w-4 h-4 mr-2" />
              Thêm khung giờ
            </Button>
          </div>

          <div className="bg-white rounded-3xl shadow-xl p-8">
            {slots.length === 0 ? (
              <div className="text-center py-12">
                <Clock className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 mb-4">Chưa có lịch làm việc</p>
                <Button data-testid="add-first-slot-btn" onClick={addSlot} className="bg-gradient-to-r from-teal-500 to-cyan-500">
                  Thêm khung giờ đầu tiên
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                {slots.map((slot, index) => (
                  <div key={index} className="border border-gray-200 rounded-xl p-6">
                    <div className="grid md:grid-cols-4 gap-4">
                      <div>
                        <Label>Ngày</Label>
                        <Select value={slot.day} onValueChange={(v) => updateSlot(index, 'day', v)}>
                          <SelectTrigger data-testid={`day-select-${index}`} className="mt-2">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {Object.entries(dayNames).map(([key, value]) => (
                              <SelectItem key={key} value={key}>{value}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label>Giờ bắt đầu</Label>
                        <Input
                          data-testid={`start-time-${index}`}
                          type="time"
                          value={slot.start_time}
                          onChange={(e) => updateSlot(index, 'start_time', e.target.value)}
                          className="mt-2"
                        />
                      </div>

                      <div>
                        <Label>Giờ kết thúc</Label>
                        <Input
                          data-testid={`end-time-${index}`}
                          type="time"
                          value={slot.end_time}
                          onChange={(e) => updateSlot(index, 'end_time', e.target.value)}
                          className="mt-2"
                        />
                      </div>

                      <div className="flex items-end">
                        <Button
                          data-testid={`delete-slot-${index}`}
                          type="button"
                          variant="outline"
                          onClick={() => removeSlot(index)}
                          className="w-full border-red-300 text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Xóa
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}

                <Button data-testid="save-schedule-btn" onClick={handleSave} disabled={saving} className="w-full bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-600 hover:to-cyan-600">
                  {saving ? 'Đang lưu...' : 'Lưu lịch làm việc'}
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
