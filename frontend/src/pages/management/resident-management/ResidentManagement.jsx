import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Button,
  TextField,
  InputAdornment,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  MenuItem,
  Card,
  CardContent,
  Tooltip,
  Avatar,
} from "@mui/material";
import {
  Search as SearchIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  People as PeopleIcon,
  Male as MaleIcon,
  Female as FemaleIcon,
  Refresh as RefreshIcon,
} from "@mui/icons-material";
import Navbar from "../../../components/Navbar";
import { managementResidentService } from "../../../services/api";

export default function ResidentManagement() {
  const navigate = useNavigate();
  const [residents, setResidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState("");
  const [totalCount, setTotalCount] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedResident, setSelectedResident] = useState(null);
  const [filterGender, setFilterGender] = useState("all");

  useEffect(() => {
    fetchResidents();
  }, [page, rowsPerPage, searchTerm, filterGender]);

  const fetchResidents = async () => {
    try {
      setLoading(true);
      const response = await managementResidentService.getAll({
        page: page + 1,
        limit: rowsPerPage,
        search: searchTerm,
        gender: filterGender !== "all" ? filterGender :  undefined,
      });
      setResidents(response.data.residents || []);
      setTotalCount(response.data.total || 0);
    } catch (error) {
      console.error("Error fetching residents:", error);
      // Mock data
      const mockData = Array.from({ length: 100 }, (_, i) => ({
        id: i + 1,
        ho_ten: `Nguyễn Văn ${String.fromCharCode(65 + (i % 26))}`,
        cccd:  `0${String(100000000 + i).slice(1)}`,
        ngay_sinh: new Date(1950 + (i % 70), i % 12, (i % 28) + 1).toISOString(),
        gioi_tinh: i % 2 === 0 ? "Nam" : "Nữ",
        dia_chi: `${i + 1} Đường Lê Lợi, Phường ${(i % 10) + 1}`,
        so_ho_khau: `HK${String(i + 1).padStart(6, "0")}`,
        quan_he_chu_ho: i % 4 === 0 ? "Chủ hộ" : ["Vợ/Chồng", "Con", "Cha/Mẹ"][i % 3],
      }));
      setResidents(mockData. slice(page * rowsPerPage, (page + 1) * rowsPerPage));
      setTotalCount(mockData. length);
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleViewDetails = (resident) => {
    setSelectedResident(resident);
    setOpenDialog(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bạn có chắc chắn muốn xóa nhân khẩu này?")) {
      try {
        await managementResidentService.delete(id);
        fetchResidents();
      } catch (error) {
        console.error("Error deleting resident:", error);
        alert("Có lỗi xảy ra khi xóa nhân khẩu");
      }
    }
  };

  const calculateAge = (birthDate) => {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  return (
    <Box sx={{ bgcolor: "background.default", minHeight: "100vh" }}>
      <Navbar />
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Quản lý nhân khẩu
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Danh sách và quản lý thông tin nhân khẩu
          </Typography>
        </Box>

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card sx={{ bgcolor: "primary.light", color: "white" }}>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                  <PeopleIcon sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {totalCount}
                    </Typography>
                    <Typography variant="body2">Tổng nhân khẩu</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ bgcolor: "info.light", color: "white" }}>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                  <MaleIcon sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {residents.filter((r) => r.gioi_tinh === "Nam").length}
                    </Typography>
                    <Typography variant="body2">Nam giới</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ bgcolor: "secondary.light", color: "white" }}>
              <CardContent>
                <Box sx={{ display:  "flex", alignItems: "center", gap: 2 }}>
                  <FemaleIcon sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {residents.filter((r) => r.gioi_tinh === "Nữ").length}
                    </Typography>
                    <Typography variant="body2">Nữ giới</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Toolbar */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                placeholder="Tìm kiếm theo họ tên, CCCD..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target. value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                select
                size="small"
                label="Giới tính"
                value={filterGender}
                onChange={(e) => setFilterGender(e.target.value)}
              >
                <MenuItem value="all">Tất cả</MenuItem>
                <MenuItem value="Nam">Nam</MenuItem>
                <MenuItem value="Nữ">Nữ</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={5} sx={{ display: "flex", gap: 1, justifyContent:  "flex-end" }}>
              <Button variant="outlined" startIcon={<RefreshIcon />} onClick={fetchResidents}>
                Làm mới
              </Button>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => navigate("/management/resident-management/create")}
              >
                Thêm nhân khẩu
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Table */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: "primary.main" }}>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>STT</TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>Họ và tên</TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>CCCD</TableCell>
                <TableCell sx={{ color: "white", fontWeight:  "bold" }}>Ngày sinh</TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }} align="center">
                  Tuổi
                </TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }} align="center">
                  Giới tính
                </TableCell>
                <TableCell sx={{ color: "white", fontWeight:  "bold" }}>Số hộ khẩu</TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>Quan hệ chủ hộ</TableCell>
                <TableCell sx={{ color: "white", fontWeight:  "bold" }} align="center">
                  Thao tác
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    Đang tải...
                  </TableCell>
                </TableRow>
              ) : residents.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    Không có dữ liệu
                  </TableCell>
                </TableRow>
              ) : (
                residents.map((resident, index) => (
                  <TableRow key={resident.id} hover sx={{ "&:hover": { bgcolor: "action.hover" } }}>
                    <TableCell>{page * rowsPerPage + index + 1}</TableCell>
                    <TableCell>
                      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: "primary.main" }}>
                          {resident.ho_ten. charAt(0)}
                        </Avatar>
                        <Typography variant="body2" fontWeight="medium">
                          {resident.ho_ten}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{resident.cccd}</TableCell>
                    <TableCell>
                      {new Date(resident.ngay_sinh).toLocaleDateString("vi-VN")}
                    </TableCell>
                    <TableCell align="center">{calculateAge(resident.ngay_sinh)}</TableCell>
                    <TableCell align="center">
                      <Chip
                        icon={resident.gioi_tinh === "Nam" ? <MaleIcon /> : <FemaleIcon />}
                        label={resident.gioi_tinh}
                        size="small"
                        color={resident.gioi_tinh === "Nam" ? "info" : "secondary"}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="primary" fontWeight="medium">
                        {resident.so_ho_khau}
                      </Typography>
                    </TableCell>
                    <TableCell>{resident.quan_he_chu_ho}</TableCell>
                    <TableCell align="center">
                      <Tooltip title="Xem chi tiết">
                        <IconButton
                          size="small"
                          color="info"
                          onClick={() => handleViewDetails(resident)}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Chỉnh sửa">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() =>
                            navigate(`/management/resident-management/edit/${resident.id}`)
                          }
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Xóa">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDelete(resident.id)}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
          <TablePagination
            component="div"
            count={totalCount}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            labelRowsPerPage="Số hàng mỗi trang:"
            labelDisplayedRows={({ from, to, count }) => `${from}-${to} trong ${count}`}
          />
        </TableContainer>

        {/* Detail Dialog */}
        <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
          <DialogTitle>
            <Typography variant="h6" fontWeight="bold">
              Chi tiết nhân khẩu
            </Typography>
          </DialogTitle>
          <DialogContent dividers>
            {selectedResident && (
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Họ và tên
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {selectedResident.ho_ten}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    CCCD
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {selectedResident.cccd}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Ngày sinh
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {new Date(selectedResident.ngay_sinh).toLocaleDateString("vi-VN")}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Giới tính
                  </Typography>
                  <Chip
                    icon={selectedResident.gioi_tinh === "Nam" ? <MaleIcon /> : <FemaleIcon />}
                    label={selectedResident.gioi_tinh}
                    size="small"
                    color={selectedResident.gioi_tinh === "Nam" ? "info" : "secondary"}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Địa chỉ
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {selectedResident.dia_chi}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Số hộ khẩu
                  </Typography>
                  <Typography variant="body1" fontWeight="medium" color="primary">
                    {selectedResident.so_ho_khau}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Quan hệ với chủ hộ
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {selectedResident.quan_he_chu_ho}
                  </Typography>
                </Grid>
              </Grid>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Đóng</Button>
            <Button
              variant="contained"
              onClick={() => {
                setOpenDialog(false);
                navigate(`/management/resident-management/edit/${selectedResident.id}`);
              }}
            >
              Chỉnh sửa
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}