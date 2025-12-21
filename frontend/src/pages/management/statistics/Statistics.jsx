import { useEffect, useState } from "react";
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  MenuItem,
  TextField,
  Divider,
  CircularProgress,
  Alert,
} from "@mui/material";
import {
  Download as DownloadIcon,
  People as PeopleIcon,
  Home as HomeIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
} from "@mui/icons-material";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import Navbar from "../../../components/Navbar";
import { managementStatisticsService } from "../../../services/api";

const COLORS = ["#03A9F4", "#0277BD", "#4CAF50", "#FF9800", "#F44336", "#9C27B0"];

export default function Statistics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reportType, setReportType] = useState("overview");

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await managementStatisticsService.getOverview();
      const data = response.data;

      const transformedStats = {
        tong_ho_khau: data.tong_ho_khau || 0,
        tong_nhan_khau:  data.tong_nhan_khau || 0,
        yeu_cau_cho_duyet: data.yeu_cau_cho_duyet || 0,
        tam_vang_hieu_luc: data.tam_vang_hieu_luc || 0,
        tam_tru_hieu_luc: data.tam_tru_hieu_luc || 0,
        phan_bo_gioi_tinh: data.phan_bo_gioi_tinh || [],
        phan_bo_do_tuoi: data.phan_bo_do_tuoi || [],
        bien_dong_gan_day: data.bien_dong_gan_day || [],
      };

      console.log("Statistics data:", transformedStats);
      setStats(transformedStats);
    } catch (error) {
      console.error("Error fetching statistics:", error);
      setError("Không thể tải dữ liệu thống kê. Vui lòng thử lại sau.");
    } finally {
      setLoading(false);
    }
  };

  const handleExportReport = async () => {
    try {
      const response = await managementStatisticsService.exportReport(reportType);
      const url = window.URL.createObjectURL(new Blob([response. data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `bao-cao-${reportType}-${new Date().getTime()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Error exporting report:", error);
      alert("Tính năng xuất báo cáo đang được phát triển");
    }
  };

  if (loading) {
    return (
      <Box sx={{ bgcolor: "background.default", minHeight: "100vh" }}>
        <Navbar />
        <Container sx={{ mt: 8, textAlign: "center" }}>
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 3 }}>
            Đang tải dữ liệu thống kê...
          </Typography>
        </Container>
      </Box>
    );
  }

  return (
    <Box sx={{ bgcolor: "background.default", minHeight: "100vh" }}>
      <Navbar />
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4, display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 2 }}>
          <Box>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Thống kê & Báo cáo
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Phân tích và báo cáo dữ liệu hộ khẩu
            </Typography>
          </Box>
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={fetchStatistics}
              disabled={loading}
            >
              Làm mới
            </Button>
            <TextField
              select
              size="small"
              label="Loại báo cáo"
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              sx={{ minWidth: 200 }}
            >
              <MenuItem value="overview">Tổng quan</MenuItem>
              <MenuItem value="household">Hộ khẩu</MenuItem>
              <MenuItem value="resident">Nhân khẩu</MenuItem>
              <MenuItem value="temporary">Tạm vắng/Tạm trú</MenuItem>
            </TextField>
            <Button 
              variant="contained" 
              startIcon={<DownloadIcon />} 
              onClick={handleExportReport}
            >
              Xuất báo cáo
            </Button>
          </Box>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError("")}>
            {error}
          </Alert>
        )}

        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: "primary.main", color: "white", height: "100%" }}>
              <CardContent>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                      Tổng hộ khẩu
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {stats?.tong_ho_khau?. toLocaleString("vi-VN") || 0}
                    </Typography>
                  </Box>
                  <HomeIcon sx={{ fontSize: 48, opacity: 0.8 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: "success.main", color: "white", height: "100%" }}>
              <CardContent>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                      Tổng nhân khẩu
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {stats?. tong_nhan_khau?.toLocaleString("vi-VN") || 0}
                    </Typography>
                  </Box>
                  <PeopleIcon sx={{ fontSize: 48, opacity: 0.8 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: "warning.main", color: "white", height: "100%" }}>
              <CardContent>
                <Box sx={{ display:  "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity:  0.9, mb: 1 }}>
                      Tạm vắng hiệu lực
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {stats?.tam_vang_hieu_luc?.toLocaleString("vi-VN") || 0}
                    </Typography>
                  </Box>
                  <TrendingUpIcon sx={{ fontSize:  48, opacity: 0.8 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor:  "info.main", color: "white", height: "100%" }}>
              <CardContent>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                      Tạm trú hiệu lực
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {stats?.tam_tru_hieu_luc?.toLocaleString("vi-VN") || 0}
                    </Typography>
                  </Box>
                  <AssessmentIcon sx={{ fontSize: 48, opacity: 0.8 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Charts Row 1 - Gender and Age Distribution */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {/* Gender Distribution */}
        <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
            📊 Phân bố theo giới tính
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {stats?.phan_bo_gioi_tinh && stats.phan_bo_gioi_tinh.length > 0 ? (
            <ResponsiveContainer width="100%" height={350}>
                <BarChart data={stats.phan_bo_gioi_tinh}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                    dataKey="gioi_tinh"
                    interval={0}
                    style={{ fontSize: "12px" }}
                />
                <YAxis />
                <Tooltip
                    formatter={(value) => [
                    `${Number(value).toLocaleString("vi-VN")} người`,
                    "Số lượng",
                    ]}
                />
                <Legend />
                <Bar
                    dataKey="count"
                    fill="#4CAF50"
                    name="Số lượng"
                />
                </BarChart>
            </ResponsiveContainer>
            ) : (
            <Box sx={{ textAlign: "center", py: 8 }}>
                <Typography color="text.secondary">
                Không có dữ liệu
                </Typography>
            </Box>
            )}
        </Paper>
        </Grid>


          {/* Age Distribution */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                📈 Phân bố theo độ tuổi
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {stats?.phan_bo_do_tuoi && stats.phan_bo_do_tuoi.length > 0 ? (
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={stats.phan_bo_do_tuoi}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="nhom_tuoi" 
                      angle={-15}
                      textAnchor="end"
                      height={100}
                      interval={0}
                      style={{ fontSize: '11px' }}
                    />
                    <YAxis />
                    <Tooltip 
                      formatter={(value) => [`${value.toLocaleString("vi-VN")} người`, "Số lượng"]}
                    />
                    <Legend />
                    <Bar dataKey="count" fill="#03A9F4" name="Số lượng" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ textAlign: "center", py:  8 }}>
                  <Typography color="text.secondary">Không có dữ liệu</Typography>
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>

        {/* Recent Changes */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12}>
            <Paper sx={{ p:  3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                📋 Biến động gần đây (30 ngày qua)
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {stats?.bien_dong_gan_day && stats.bien_dong_gan_day.length > 0 ? (
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={stats.bien_dong_gan_day}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="loai_thay_doi" />
                    <YAxis />
                    <Tooltip 
                      formatter={(value) => [`${value.toLocaleString("vi-VN")} lần`, "Số lượng"]}
                    />
                    <Legend />
                    <Bar dataKey="count" fill="#4CAF50" name="Số lượng" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ textAlign: "center", py:  8 }}>
                  <Typography color="text.secondary">
                    Không có biến động nào trong 30 ngày qua
                  </Typography>
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>

        {/* Summary Statistics Table */}
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p:  3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                📑 Tổng hợp số liệu
              </Typography>
              <Divider sx={{ mb: 3 }} />
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={4}>
                  <Box sx={{ p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Trung bình nhân khẩu/hộ
                    </Typography>
                    <Typography variant="h5" fontWeight="bold" color="primary. main">
                      {stats?. tong_ho_khau && stats?. tong_ho_khau > 0
                        ? (stats.tong_nhan_khau / stats.tong_ho_khau).toFixed(2)
                        : 0}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Box sx={{ p: 2, bgcolor:  "grey.100", borderRadius: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Tỷ lệ nam
                    </Typography>
                    <Typography variant="h5" fontWeight="bold" color="info.main">
                      {stats?.phan_bo_gioi_tinh && stats?. tong_nhan_khau > 0
                        ? (
                            ((stats.phan_bo_gioi_tinh.find((g) => g.gioi_tinh === "Nam")?.count || 0) /
                              stats.tong_nhan_khau) *
                            100
                          ).toFixed(1)
                        : 0}
                      %
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Box sx={{ p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Tỷ lệ nữ
                    </Typography>
                    <Typography variant="h5" fontWeight="bold" color="secondary.main">
                      {stats?.phan_bo_gioi_tinh && stats?.tong_nhan_khau > 0
                        ? (
                            ((stats.phan_bo_gioi_tinh. find((g) => g.gioi_tinh === "Nữ")?.count || 0) /
                              stats.tong_nhan_khau) *
                            100
                          ).toFixed(1)
                        : 0}
                      %
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Box sx={{ p:  2, bgcolor: "grey. 100", borderRadius: 1 }}>
                    <Typography variant="body2" color="text. secondary">
                      Yêu cầu chờ duyệt
                    </Typography>
                    <Typography variant="h5" fontWeight="bold" color="warning.main">
                      {stats?.yeu_cau_cho_duyet?. toLocaleString("vi-VN") || 0}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Box sx={{ p:  2, bgcolor: "grey. 100", borderRadius: 1 }}>
                    <Typography variant="body2" color="text. secondary">
                      Tổng tạm vắng & tạm trú
                    </Typography>
                    <Typography variant="h5" fontWeight="bold" color="success.main">
                      {((stats?.tam_vang_hieu_luc || 0) + (stats?.tam_tru_hieu_luc || 0)).toLocaleString(
                        "vi-VN"
                      )}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Box sx={{ p:  2, bgcolor: "grey. 100", borderRadius: 1 }}>
                    <Typography variant="body2" color="text. secondary">
                      Cập nhật lần cuối
                    </Typography>
                    <Typography variant="h6" fontWeight="bold" color="text.primary">
                      {new Date().toLocaleString("vi-VN")}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}