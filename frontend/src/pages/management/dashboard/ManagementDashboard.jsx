import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  IconButton,
} from "@mui/material";
import {
  Home as HomeIcon,
  People as PeopleIcon,
  HourglassEmpty as HourglassIcon,
  Description as DescriptionIcon,
  Apartment as ApartmentIcon,
  PersonAdd as PersonAddIcon,
  ExitToApp as ExitIcon,
  Assessment as AssessmentIcon,
  History as HistoryIcon,
  ArrowForward as ArrowForwardIcon,
} from "@mui/icons-material";
import Navbar from "../../../components/Navbar";
import { managementDashboardService } from "../../../services/api";

export default function ManagementDashboard() {
  const [stats, setStats] = useState(null);
  const [pendingRequests, setPendingRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    // Fetch dashboard statistics
    Promise.all([
      managementDashboardService.getStats(),
      managementDashboardService.getPendingRequests(),
    ])
      .then(([statsResponse, requestsResponse]) => {
        setStats(statsResponse.data);
        setPendingRequests(requestsResponse.data.slice(0, 5));
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        // Mock data for development
        setStats({
          tong_ho_khau: 1250,
          tong_nhan_khau: 4800,
          yeu_cau_cho_duyet: 23,
          tam_vang_hieu_luc: 145,
          tam_tru_hieu_luc: 89,
          phan_bo_gioi_tinh: [
            { gioi_tinh: "Nam", count: 2400 },
            { gioi_tinh: "Nữ", count: 2300 },
            { gioi_tinh: "Khác", count: 100 },
          ],
          phan_bo_do_tuoi: [
            { nhom_tuoi: "0-17", count: 960 },
            { nhom_tuoi: "18-35", count: 1680 },
            { nhom_tuoi: "36-60", count: 1440 },
            { nhom_tuoi: "60+", count: 720 },
          ],
        });
        setPendingRequests([]);
        setLoading(false);
      });
  }, [navigate]);

  const statCards = [
    {
      title: "Tổng số hộ khẩu",
      value: stats?.tong_ho_khau || 0,
      icon: <HomeIcon sx={{ fontSize: 40 }} />,
      color: "primary.main",
      bgColor: "primary.light",
    },
    {
      title: "Tổng số nhân khẩu",
      value: stats?.tong_nhan_khau || 0,
      icon: <PeopleIcon sx={{ fontSize: 40 }} />,
      color: "success.main",
      bgColor: "success.light",
    },
    {
      title: "Yêu cầu chờ duyệt",
      value: stats?.yeu_cau_cho_duyet || 0,
      icon: <HourglassIcon sx={{ fontSize: 40 }} />,
      color: "warning.main",
      bgColor: "warning.light",
    },
    {
      title: "Giấy tạm vắng hiệu lực",
      value: stats?.tam_vang_hieu_luc || 0,
      icon: <DescriptionIcon sx={{ fontSize: 40 }} />,
      color: "info.main",
      bgColor: "info.light",
    },
    {
      title: "Giấy tạm trú hiệu lực",
      value: stats?.tam_tru_hieu_luc || 0,
      icon: <ApartmentIcon sx={{ fontSize: 40 }} />,
      color: "secondary.main",
      bgColor: "secondary.light",
    },
  ];

  const quickLinks = [
    {
      title: "Quản lý hộ khẩu",
      icon: <HomeIcon sx={{ fontSize: 48 }} />,
      path: "/management/household-management",
      color: "primary.main",
    },
    {
      title: "Quản lý nhân khẩu",
      icon: <PeopleIcon sx={{ fontSize: 48 }} />,
      path: "/management/resident-management",
      color: "success.main",
    },
    {
      title: "Quản lý tạm vắng",
      icon: <ExitIcon sx={{ fontSize: 48 }} />,
      path: "/management/temporary-absence",
      color: "warning.main",
    },
    {
      title: "Quản lý tạm trú",
      icon: <PersonAddIcon sx={{ fontSize: 48 }} />,
      path: "/management/temporary-residence",
      color: "info.main",
    },
    {
      title: "Thống kê báo cáo",
      icon: <AssessmentIcon sx={{ fontSize: 48 }} />,
      path: "/management/statistics",
      color: "secondary.main",
    },
    {
      title: "Lịch sử biến động",
      icon: <HistoryIcon sx={{ fontSize: 48 }} />,
      path: "/management/change-history",
      color: "error.main",
    },
  ];

  if (loading) {
    return (
      <Box>
        <Navbar />
        <Container sx={{ mt: 4, textAlign: "center" }}>
          <Typography variant="h6">Đang tải...</Typography>
        </Container>
      </Box>
    );
  }

  return (
    <Box sx={{ bgcolor: "background.default", minHeight: "100vh" }}>
      <Navbar />

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Bảng điều khiển quản trị
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Tổng quan hệ thống quản lý hộ khẩu
          </Typography>
        </Box>

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {statCards.map((card, index) => (
            <Grid item xs={12} sm={6} md={4} lg={2.4} key={index}>
              <Card
                sx={{
                  height: "100%",
                  background: `linear-gradient(135deg, ${card.bgColor}15 0%, ${card.bgColor}30 100%)`,
                  border: `1px solid ${card.color}30`,
                  transition: "transform 0.2s, box-shadow 0.2s",
                  "&:hover": {
                    transform: "translateY(-4px)",
                    boxShadow: 4,
                  },
                }}
              >
                <CardContent>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      mb: 2,
                    }}
                  >
                    <Box
                      sx={{
                        color: card.color,
                        bgcolor: "white",
                        borderRadius: 2,
                        p: 1,
                        display: "flex",
                      }}
                    >
                      {card.icon}
                    </Box>
                  </Box>
                  <Typography variant="h4" fontWeight="bold" gutterBottom>
                    {card.value.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {card.title}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Charts Section */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: "100%" }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                📊 Phân bố theo giới tính
              </Typography>
              <Box sx={{ mt: 3 }}>
                {stats?.phan_bo_gioi_tinh?.map((item, index) => (
                  <Box key={item.gioi_tinh} sx={{ mb: 2 }}>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 0.5,
                      }}
                    >
                      <Typography variant="body2" fontWeight="medium">
                        {item.gioi_tinh}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {item.count.toLocaleString()} (
                        {((item.count / stats.tong_nhan_khau) * 100).toFixed(1)}
                        %)
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        height: 8,
                        bgcolor: "grey.200",
                        borderRadius: 1,
                        overflow: "hidden",
                      }}
                    >
                      <Box
                        sx={{
                          height: "100%",
                          width: `${(item.count / stats.tong_nhan_khau) * 100}%`,
                          bgcolor:
                            item.gioi_tinh === "Nam"
                              ? "primary.main"
                              : item.gioi_tinh === "Nữ"
                              ? "secondary.main"
                              : "info.main",
                          transition: "width 0.5s ease",
                        }}
                      />
                    </Box>
                  </Box>
                ))}
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: "100%" }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                📈 Phân bố theo độ tuổi
              </Typography>
              <Box sx={{ mt: 3 }}>
                {stats?.phan_bo_do_tuoi?.map((item, index) => (
                  <Box key={index} sx={{ mb: 2 }}>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 0.5,
                      }}
                    >
                      <Typography variant="body2" fontWeight="medium">
                        {item.nhom_tuoi} tuổi
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {item.count.toLocaleString()} (
                        {((item.count / stats.tong_nhan_khau) * 100).toFixed(1)}
                        %)
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        height: 8,
                        bgcolor: "grey.200",
                        borderRadius: 1,
                        overflow: "hidden",
                      }}
                    >
                      <Box
                        sx={{
                          height: "100%",
                          width: `${(item.count / stats.tong_nhan_khau) * 100}%`,
                          bgcolor: `hsl(${index * 60}, 70%, 60%)`,
                          transition: "width 0.5s ease",
                        }}
                      />
                    </Box>
                  </Box>
                ))}
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* Quick Links */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" fontWeight="bold" gutterBottom>
            Quản lý
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {quickLinks.map((link, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card
                  sx={{
                    cursor: "pointer",
                    transition: "all 0.2s",
                    "&:hover": {
                      transform: "translateY(-4px)",
                      boxShadow: 4,
                      bgcolor: `${link.color}10`,
                    },
                  }}
                  onClick={() => navigate(link.path)}
                >
                  <CardContent>
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 2,
                      }}
                    >
                      <Box sx={{ color: link.color }}>{link.icon}</Box>
                      <Typography variant="h6" fontWeight="medium">
                        {link.title}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Container>
    </Box>
  );
}