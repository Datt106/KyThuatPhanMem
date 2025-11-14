import api from "./api"
export async function registerUser(userData) {
  const res = await api.post(`/register`, userData);
  return res.data;
}

export async function login(email, password) {
  const res = await api.post(`/login`, { email, password });
  return res.data;
}