import { useState } from 'react'
import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/Login/login';
import RegisterPage from './pages/Register/register';
import HomePage from './pages/Home/home';
import ProfilePage from'./pages/profile/profile';
import PhanAnhPage from './pages/Phananh/phananh';
function App() {
  const [count, setCount] = useState(0)

  return (
      <BrowserRouter>
        <Routes>
          <Route path="/home" element={<HomePage/>} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/phan-anh" element={<PhanAnhPage />} />
        </Routes>
      </BrowserRouter>
    );
}
export default App
