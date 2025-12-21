import { useState } from 'react'
import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';

import LoginPage from './pages/Login/login';
import RegisterPage from './pages/Register/register';
import HomePage from './pages/Home/home';
import ProfilePage from './pages/profile/profile';
import PhanAnhPage from './pages/Phananh/phananh';
import ResidentDashboard from './pages/Dashboard/ResidentDashboard';
import AdminDashboard from './pages/Admin/AdminDashboard';
import MyHousehold from './pages/HoKhau/MyHousehold';

import ManagementDashboard from './pages/Management/dashboard/ManagementDashboard';
import HouseholdList from './pages/Management/household-management/HouseholdList';
import HouseholdCreate from './pages/Management/household-management/HouseholdCreate';
import ResidentManagement from './pages/Management/resident-management/ResidentManagement';
import TemporaryAbsence from './pages/Management/temporary-absence/TemporaryAbsence';
import TemporaryResidence from './pages/Management/temporary-residence/TemporaryResidence';
import Statistics from './pages/Management/statistics/Statistics';

function App() {
  const [count, setCount] = useState(0)

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/home" element={<HomePage/>} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/phan-anh" element={<PhanAnhPage />} />
          <Route path="/dashboard" element={<ResidentDashboard />} />
          <Route path="/ho-khau-cua-toi" element={<MyHousehold />} />
          <Route path="/admin/dashboard" element={<AdminDashboard />} />

          {/* Routes for Management (Ban Quản lý) */}
          <Route path="/management/dashboard" element={<ManagementDashboard />} />
          <Route path="/management/household-management" element={<HouseholdList />} />
          <Route path="/management/household-management/create" element={<HouseholdCreate />} />
          <Route path="/management/resident-management" element={<ResidentManagement />} />
          <Route path="/management/temporary-absence" element={<TemporaryAbsence />} />
          <Route path="/management/temporary-residence" element={<TemporaryResidence />} />
          <Route path="/management/statistics" element={<Statistics />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
export default App