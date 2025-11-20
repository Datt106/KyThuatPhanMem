import API from "./api";

// Hàm đăng ký
export const registerUser = async (userData) => {
  try {
    const res = await API.post("/auth/register", userData);
    return res.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

// Hàm đăng nhập
export const loginUser = async (userData) => {
  try {
    const res = await API.post("/auth/login", userData);
    return res.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};
