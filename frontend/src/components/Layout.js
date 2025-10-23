import React, { useContext } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Calendar, Users, Clock, Home, User, BarChart, FileText, MessageSquare, Settings, Shield, UserPlus } from 'lucide-react';
import { AuthContext } from '@/App';
import LanguageToggle from '@/components/LanguageToggle';

export default function Layout({ children }) {
  const location = useLocation();
  const role = location.pathname.split('/')[1];
  const { user } = useContext(AuthContext);
  const { t } = useLanguage();

  const patientLinks = [
    { path: '/patient/dashboard', icon: Home, label: t('home') },
    { path: '/patient/search-doctors', icon: Users, label: t('findDoctor') },
    { path: '/patient/appointments', icon: Calendar, label: t('appointments') }
  ];

  const doctorLinks = [
    { path: '/doctor/dashboard', icon: Home, label: t('home') },
    { path: '/doctor/appointments', icon: Calendar, label: t('appointments') },
    { path: '/doctor/profile', icon: User, label: t('profile') },
    { path: '/doctor/schedule', icon: Clock, label: t('schedule') }
  ];

  let adminLinks = [
    { path: '/admin/dashboard', icon: Home, label: t('home') },
    { path: '/admin/create-accounts', icon: UserPlus, label: t('createAccounts') },
    { path: '/admin/doctors', icon: Users, label: t('doctors') },
    { path: '/admin/patients', icon: FileText, label: t('patients') },
    { path: '/admin/stats', icon: BarChart, label: t('stats') }
  ];

  // Add Admins management link if user has permission
  if (role === 'admin' && user?.admin_permissions?.can_create_admins) {
    adminLinks.push({ path: '/admin/admins', icon: Shield, label: t('admins') });
  }

  const links = role === 'patient' ? patientLinks : role === 'doctor' ? doctorLinks : role === 'admin' ? adminLinks : [];

  if (links.length === 0) {
    return <>{children}</>;
  }

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-xl fixed h-full z-10 flex flex-col">
        <div className="p-6 flex-1">
          <Link to="/" className="flex items-center gap-2 mb-8">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-gray-800">MediSchedule</span>
          </Link>

          <nav className="space-y-2">
            {links.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  data-testid={`nav-${link.path.split('/').pop()}`}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-teal-500 to-cyan-500 text-white shadow-lg'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{link.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>
        
        {/* Language Toggle at bottom of sidebar */}
        <div className="p-6 border-t">
          <LanguageToggle />
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 flex-1">
        {children}
      </main>
    </div>
  );
}
