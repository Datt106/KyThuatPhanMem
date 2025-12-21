import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000/api",
  headers:  {
    "Content-Type":  "application/json"
  }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Management Dashboard Service
export const managementDashboardService = {
  getStats:  () => api.get("/thong-ke/tong-quan"),
  getPendingRequests: () => api.get("/yeu-cau? trang_thai=Chờ duyệt"),
};

// Household Management Service
export const managementHouseholdService = {
  getAll: (params) => api.get("/ho-khau", { params }),
  getById: (id) => api.get(`/ho-khau/${id}`),
  create: (data) => api.post("/ho-khau", data),
  update: (id, data) => api.put(`/ho-khau/${id}`, data),
  delete: (id) => api.delete(`/ho-khau/${id}`),
  getMembers: (id) => api.get(`/ho-khau/${id}/thanh-vien`),
  addMember: (id, data) => api.post(`/ho-khau/${id}/thanh-vien`, data),
  removeMember: (householdId, memberId) => api.delete(`/ho-khau/${householdId}/thanh-vien/${memberId}`),
};

// Resident Management Service
export const managementResidentService = {
  getAll: (params) => api.get("/nhan-khau", { params }),
  getById: (id) => api.get(`/nhan-khau/${id}`),
  create: (data) => api.post("/nhan-khau", data),
  update: (id, data) => api.put(`/nhan-khau/${id}`, data),
  delete: (id) => api.delete(`/nhan-khau/${id}`),
  search: (keyword) => api.get(`/nhan-khau/tim-kiem?q=${keyword}`),
};

// Temporary Absence Service
export const managementTemporaryAbsenceService = {
  getAll: (params) => api.get("/tam-vang", { params }),
  getById: (id) => api.get(`/tam-vang/${id}`),
  create: (data) => api.post("/tam-vang", data),
  update: (id, data) => api.put(`/tam-vang/${id}`, data),
  delete: (id) => api.delete(`/tam-vang/${id}`),
  approve: (id) => api.post(`/tam-vang/${id}/duyet`),
  reject: (id, reason) => api.post(`/tam-vang/${id}/tu-choi`, { reason }),
};

// Temporary Residence Service
export const managementTemporaryResidenceService = {
  getAll:  (params) => api.get("/tam-tru", { params }),
  getById: (id) => api.get(`/tam-tru/${id}`),
  create: (data) => api.post("/tam-tru", data),
  update: (id, data) => api.put(`/tam-tru/${id}`, data),
  delete: (id) => api.delete(`/tam-tru/${id}`),
  approve: (id) => api.post(`/tam-tru/${id}/duyet`),
  reject: (id, reason) => api.post(`/tam-tru/${id}/tu-choi`, { reason }),
};

// Statistics Service
export const managementStatisticsService = {
  getOverview: () => api.get("/thong-ke/tong-quan"),
  getChangeHistory: (params) => api.get("/thong-ke/lich-su-bien-dong", { params }),
  getFilteredStats: (params) => api.get("/thong-ke/thong-ke/loc", { params }),
  exportReport: (type) => api.get(`/thong-ke/bao-cao/${type}`, { responseType: 'blob' }),
};

export default api;