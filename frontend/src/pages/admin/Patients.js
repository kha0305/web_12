import React, { useContext, useEffect, useState } from 'react';
import { AuthContext, API } from '@/App';
import axios from 'axios';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import Layout from '@/components/Layout';
import { Search, Users, Trash2 } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';

export default function AdminPatients() {
  const { token } = useContext(AuthContext);
  const { t } = useLanguage();
  const [patients, setPatients] = useState([]);
  const [filteredPatients, setFilteredPatients] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPatients();
  }, []);

  useEffect(() => {
    filterPatients();
  }, [searchQuery, patients]);

  const fetchPatients = async () => {
    try {
      const response = await axios.get(`${API}/admin/patients`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPatients(response.data);
      setFilteredPatients(response.data);
    } catch (error) {
      toast.error(t('loadError'));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (patientId, patientName) => {
    if (!window.confirm(`${t('confirmDeleteUser')} ${patientName}?`)) return;

    try {
      await axios.delete(`${API}/admin/delete-user/${patientId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success(t('userDeleted'));
      fetchPatients();
    } catch (error) {
      toast.error(error.response?.data?.detail || t('cannotDeleteUser'));
    }
  };

  const filterPatients = () => {
    if (searchQuery) {
      setFilteredPatients(
        patients.filter(p => 
          p.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.email?.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
    } else {
      setFilteredPatients(patients);
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">{t('patientManagement')}</h1>

          {/* Search */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                data-testid="search-input"
                placeholder={t('searchPatients')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Patients List */}
          {loading ? (
            <p className="text-center text-gray-500">{t('loading')}</p>
          ) : filteredPatients.length === 0 ? (
            <div className="bg-white rounded-2xl p-12 text-center">
              <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">{t('noData')}</p>
            </div>
          ) : (
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-gradient-to-r from-teal-500 to-cyan-500 text-white">
                  <tr>
                    <th className="px-6 py-4 text-left font-semibold">{t('fullName')}</th>
                    <th className="px-6 py-4 text-left font-semibold">{t('email')}</th>
                    <th className="px-6 py-4 text-left font-semibold">{t('registeredDate')}</th>
                    <th className="px-6 py-4 text-left font-semibold">{t('actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredPatients.map((patient, index) => (
                    <tr key={patient.id} className={`border-b ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-teal-50 transition-colors`}>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center text-white font-bold">
                            {patient.full_name?.charAt(0) || 'P'}
                          </div>
                          <span className="font-semibold text-gray-900">{patient.full_name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-600">{patient.email}</td>
                      <td className="px-6 py-4 text-gray-600">
                        {patient.created_at ? new Date(patient.created_at).toLocaleDateString('vi-VN') : 'N/A'}
                      </td>
                      <td className="px-6 py-4">
                        <Button 
                          onClick={() => handleDelete(patient.id, patient.full_name)} 
                          variant="outline"
                          className="border-red-300 text-red-600 hover:bg-red-50"
                          size="sm"
                        >
                          <Trash2 className="w-4 h-4 mr-1" />
                          {t('remove')}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="mt-6 text-center text-gray-600">
            {t('totalPatients')}: <span className="font-bold text-teal-600">{filteredPatients.length}</span>
          </div>
        </div>
      </div>
    </Layout>
  );
}
