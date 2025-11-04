import api from "./api";

export const login = async (email, password) => {
  const res = await api.post("/login", { email, password });
  return res.data;
};

export const register = async (email, password) => {
  const res = await api.post("/register", { email, password });
  return res.data;
};
