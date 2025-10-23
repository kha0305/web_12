import React, { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";

// Pages
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import ForgotPasswordPage from "@/pages/ForgotPasswordPage";

// Patient Pages
import PatientDashboard from "@/pages/patient/Dashboard";
import SearchDoctors from "@/pages/patient/SearchDoctors";
import PatientAppointments from "@/pages/patient/Appointments";
import PatientChat from "@/pages/patient/Chat";

// Doctor Pages
import DoctorDashboard from "@/pages/doctor/Dashboard";
import DoctorProfile from "@/pages/doctor/Profile";
import DoctorSchedule from "@/pages/doctor/Schedule";
import DoctorAppointments from "@/pages/doctor/Appointments";
import DoctorChat from "@/pages/doctor/Chat";

// Admin Pages
import AdminDashboard from "@/pages/admin/Dashboard";
import AdminDoctors from "@/pages/admin/Doctors";
import AdminPatients from "@/pages/admin/Patients";
import AdminStats from "@/pages/admin/Stats";
import AdminsManagement from "@/pages/admin/Admins";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// Auth Context
export const AuthContext = React.createContext();

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error("Failed to fetch user", error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = (newToken, userData) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />

            {/* Patient Routes */}
            <Route path="/patient/dashboard" element={user?.role === "patient" ? <PatientDashboard /> : <Navigate to="/login" />} />
            <Route path="/patient/search-doctors" element={user?.role === "patient" ? <SearchDoctors /> : <Navigate to="/login" />} />
            <Route path="/patient/appointments" element={user?.role === "patient" ? <PatientAppointments /> : <Navigate to="/login" />} />
            <Route path="/patient/chat/:appointmentId" element={user?.role === "patient" ? <PatientChat /> : <Navigate to="/login" />} />

            {/* Doctor Routes */}
            <Route path="/doctor/dashboard" element={user?.role === "doctor" ? <DoctorDashboard /> : <Navigate to="/login" />} />
            <Route path="/doctor/profile" element={user?.role === "doctor" ? <DoctorProfile /> : <Navigate to="/login" />} />
            <Route path="/doctor/schedule" element={user?.role === "doctor" ? <DoctorSchedule /> : <Navigate to="/login" />} />
            <Route path="/doctor/appointments" element={user?.role === "doctor" ? <DoctorAppointments /> : <Navigate to="/login" />} />
            <Route path="/doctor/chat/:appointmentId" element={user?.role === "doctor" ? <DoctorChat /> : <Navigate to="/login" />} />

            {/* Admin Routes */}
            <Route path="/admin/dashboard" element={user?.role === "admin" ? <AdminDashboard /> : <Navigate to="/login" />} />
            <Route path="/admin/doctors" element={user?.role === "admin" ? <AdminDoctors /> : <Navigate to="/login" />} />
            <Route path="/admin/patients" element={user?.role === "admin" ? <AdminPatients /> : <Navigate to="/login" />} />
            <Route path="/admin/stats" element={user?.role === "admin" ? <AdminStats /> : <Navigate to="/login" />} />
            <Route path="/admin/admins" element={user?.role === "admin" ? <AdminsManagement /> : <Navigate to="/login" />} />
          </Routes>
        </BrowserRouter>
        <Toaster position="top-right" />
      </div>
    </AuthContext.Provider>
  );
}

export default App;
