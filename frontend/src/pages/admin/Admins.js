import React, { useState, useEffect, useContext } from 'react';
import { AuthContext, API } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import Layout from '@/components/Layout';
import { toast } from 'sonner';
import axios from 'axios';
import { UserPlus, Shield, Trash2, Eye, EyeOff } from 'lucide-react';

export default function AdminsManagement() {
  const { token, user } = useContext(AuthContext);
  const [admins, setAdmins] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    can_create_admins: false,
    can_manage_doctors: true,
    can_manage_patients: true,
    can_view_stats: true
  });

  const currentUserPermissions = user?.admin_permissions || {};

  useEffect(() => {
    fetchAdmins();
  }, []);

  const fetchAdmins = async () => {
    try {
      const response = await axios.get(`${API}/admin/admins`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAdmins(response.data);
    } catch (error) {
      console.error('Error fetching admins:', error);
      toast.error('Không thể tải danh sách admin');
    }
  };

  const handleCreateAdmin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post(`${API}/admin/create-admin`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Tạo tài khoản admin thành công!');
      setShowCreateForm(false);
      setFormData({
        email: '',
        password: '',
        full_name: '',
        can_create_admins: false,
        can_manage_doctors: true,
        can_manage_patients: true,
        can_view_stats: true
      });
      fetchAdmins();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Không thể tạo admin');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAdmin = async (adminId, adminEmail) => {
    if (!window.confirm(`Bạn có chắc muốn xóa admin ${adminEmail}?`)) return;

    try {
      await axios.delete(`${API}/admin/delete-admin/${adminId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Đã xóa admin thành công');
      fetchAdmins();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Không thể xóa admin');
    }
  };

  const handleUpdatePermissions = async (adminId, permissions) => {
    try {
      await axios.put(
        `${API}/admin/update-permissions`,
        { admin_id: adminId, permissions },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Cập nhật quyền thành công');
      fetchAdmins();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Không thể cập nhật quyền');
    }
  };

  const canCreateAdmins = currentUserPermissions.can_create_admins === true;

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Quản lý Admin</h1>
              <p className="text-gray-600 mt-1">Quản lý tài khoản và phân quyền admin</p>
            </div>
            {canCreateAdmins && (
              <Button
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-gradient-to-r from-teal-500 to-cyan-500"
              >
                <UserPlus className="w-4 h-4 mr-2" />
                Tạo Admin Mới
              </Button>
            )}
          </div>

          {/* Create Admin Form */}
          {showCreateForm && canCreateAdmins && (
            <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
              <h2 className="text-xl font-bold mb-4">Tạo tài khoản Admin mới</h2>
              <form onSubmit={handleCreateAdmin} className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="full_name">Họ và tên</Label>
                    <Input
                      id="full_name"
                      type="text"
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      required
                      className="mt-2"
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      required
                      className="mt-2"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="password">Mật khẩu</Label>
                  <div className="relative mt-2">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      required
                      className="pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <div>
                  <Label className="mb-3 block">Phân quyền</Label>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="can_create_admins"
                        checked={formData.can_create_admins}
                        onCheckedChange={(checked) => setFormData({ ...formData, can_create_admins: checked })}
                      />
                      <label htmlFor="can_create_admins" className="text-sm cursor-pointer">
                        Tạo và quản lý admin khác
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="can_manage_doctors"
                        checked={formData.can_manage_doctors}
                        onCheckedChange={(checked) => setFormData({ ...formData, can_manage_doctors: checked })}
                      />
                      <label htmlFor="can_manage_doctors" className="text-sm cursor-pointer">
                        Quản lý bác sĩ
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="can_manage_patients"
                        checked={formData.can_manage_patients}
                        onCheckedChange={(checked) => setFormData({ ...formData, can_manage_patients: checked })}
                      />
                      <label htmlFor="can_manage_patients" className="text-sm cursor-pointer">
                        Quản lý bệnh nhân
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="can_view_stats"
                        checked={formData.can_view_stats}
                        onCheckedChange={(checked) => setFormData({ ...formData, can_view_stats: checked })}
                      />
                      <label htmlFor="can_view_stats" className="text-sm cursor-pointer">
                        Xem thống kê
                      </label>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button type="submit" disabled={loading} className="bg-gradient-to-r from-teal-500 to-cyan-500">
                    {loading ? 'Đang tạo...' : 'Tạo Admin'}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setShowCreateForm(false)}>
                    Hủy
                  </Button>
                </div>
              </form>
            </div>
          )}

          {/* Admin List */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-xl font-bold mb-4">Danh sách Admin</h2>
            <div className="space-y-4">
              {admins.map((admin) => (
                <AdminCard
                  key={admin.id}
                  admin={admin}
                  currentUserId={user?.id}
                  canCreateAdmins={canCreateAdmins}
                  onDelete={handleDeleteAdmin}
                  onUpdatePermissions={handleUpdatePermissions}
                />
              ))}
              {admins.length === 0 && (
                <p className="text-center text-gray-500 py-8">Chưa có admin nào khác</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

function AdminCard({ admin, currentUserId, canCreateAdmins, onDelete, onUpdatePermissions }) {
  const [showPermissions, setShowPermissions] = useState(false);
  const [permissions, setPermissions] = useState(admin.admin_permissions || {});
  const isCurrentUser = admin.id === currentUserId;

  const handleSavePermissions = () => {
    onUpdatePermissions(admin.id, permissions);
    setShowPermissions(false);
  };

  return (
    <div className="border rounded-xl p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-lg">
            {admin.full_name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">
              {admin.full_name}
              {isCurrentUser && <span className="ml-2 text-xs bg-teal-100 text-teal-700 px-2 py-1 rounded">Bạn</span>}
            </h3>
            <p className="text-sm text-gray-600">{admin.email}</p>
            <p className="text-xs text-gray-500 mt-1">
              Tạo: {new Date(admin.created_at).toLocaleDateString('vi-VN')}
            </p>
          </div>
        </div>
        
        <div className="flex gap-2">
          {canCreateAdmins && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => setShowPermissions(!showPermissions)}
            >
              <Shield className="w-4 h-4 mr-1" />
              Phân quyền
            </Button>
          )}
          {!isCurrentUser && canCreateAdmins && (
            <Button
              size="sm"
              variant="outline"
              className="text-red-600 hover:text-red-700"
              onClick={() => onDelete(admin.id, admin.email)}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>

      {showPermissions && canCreateAdmins && (
        <div className="mt-4 pt-4 border-t space-y-3">
          <h4 className="font-semibold text-sm">Chỉnh sửa phân quyền</h4>
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Checkbox
                id={`perm_create_${admin.id}`}
                checked={permissions.can_create_admins || false}
                onCheckedChange={(checked) => setPermissions({ ...permissions, can_create_admins: checked })}
              />
              <label htmlFor={`perm_create_${admin.id}`} className="text-sm cursor-pointer">
                Tạo và quản lý admin khác
              </label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id={`perm_doctors_${admin.id}`}
                checked={permissions.can_manage_doctors !== false}
                onCheckedChange={(checked) => setPermissions({ ...permissions, can_manage_doctors: checked })}
              />
              <label htmlFor={`perm_doctors_${admin.id}`} className="text-sm cursor-pointer">
                Quản lý bác sĩ
              </label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id={`perm_patients_${admin.id}`}
                checked={permissions.can_manage_patients !== false}
                onCheckedChange={(checked) => setPermissions({ ...permissions, can_manage_patients: checked })}
              />
              <label htmlFor={`perm_patients_${admin.id}`} className="text-sm cursor-pointer">
                Quản lý bệnh nhân
              </label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id={`perm_stats_${admin.id}`}
                checked={permissions.can_view_stats !== false}
                onCheckedChange={(checked) => setPermissions({ ...permissions, can_view_stats: checked })}
              />
              <label htmlFor={`perm_stats_${admin.id}`} className="text-sm cursor-pointer">
                Xem thống kê
              </label>
            </div>
          </div>
          <div className="flex gap-2 mt-3">
            <Button size="sm" onClick={handleSavePermissions} className="bg-gradient-to-r from-teal-500 to-cyan-500">
              Lưu
            </Button>
            <Button size="sm" variant="outline" onClick={() => setShowPermissions(false)}>
              Hủy
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
