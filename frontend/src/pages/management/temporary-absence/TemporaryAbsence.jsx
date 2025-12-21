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
} from "@mui/material";
import {
  Search as SearchIcon,
  Add as AddIcon,
  Visibility as VisibilityIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Refresh as RefreshIcon,
  ExitToApp as ExitIcon,
} from "@mui/icons-material";
import Navbar from "../../../components/Navbar";
import { managementTemporaryAbsenceService } from "../../../services/api";

export default function TemporaryAbsence() {
  const navigate = useNavigate();
  const [absences, setAbsences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState("");
  const [totalCount, setTotalCount] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedAbsence, setSelectedAbsence] = useState(null);
  const [filterStatus, setFilterStatus] = useState("all");

  useEffect(() => {
    fetchAbsences();
  }, [page, rowsPerPage, searchTerm, filterStatus]);

  const fetchAbsences = async () => {
    try {
      setLoading(true);
      const response = await managementTemporaryAbsenceService.getAll({
        page: page + 1,
        limit: rowsPerPage,
        search: searchTerm,
        status: filterStatus !== "all" ? filterStatus : undefined,
      });
      setAbsences(response.data.absences || []);
      setTotalCount(response.data.total || 0);
    } catch (error) {
      console.error("Error fetching absences:", error);
      // Mock data
      const mockData = Array.from({ length: 50 }, (_, i) => ({
        id: i + 1,
        ma_giay: `TV${String(i + 1).padStart(6, "0")}`,
        ho_ten: `Nguyễn Văn ${String. fromCharCode(65 + (i % 26))}`,
        cccd: `0${String(100000000 + i).slice(1)}`,
        so_ho_khau: `HK${String(i + 1).padStart(6, "0")}`,
        tu_ngay: new Date(2025, 0, 1 + i).toISOString(),
        den_ngay: new Date(2025, 2, 1 + i).toISOString(),
        noi_den: `TP.  ${["Hà Nội", "TP. HCM", "Đà Nẵng", "Hải Phòng"][i % 4]}`,
        ly_do: "Công tác",
        trang_thai: ["Chờ duyệt", "Đã duyệt", "Từ chối"][i % 3],
        ngay_tao: new Date(2024, 11, 1 + i).toISOString(),
      }));
      setAbsences(mockData. slice(page * rowsPerPage, (page + 1) * rowsPerPage));
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

  const handleViewDetails = (absence) => {
    setSelectedAbsence(absence);
    setOpenDialog(true);
  };

  const handleApprove = async (id) => {
    if (window.confirm("Bạn có chắc chắn muốn duyệt đơn này?")) {
      try {
        await managementTemporaryAbsenceService.approve(id);
        fetchAbsences();
      } catch (error) {
        console.error("Error approving absence:", error);
        alert("Có lỗi xảy ra khi duyệt đơn");
      }
    }
  };

  const handleReject = async (id) => {
        const reason = prompt("Nhập lý do từ chối:");
    if (reason) {
      try {
        await managementTemporaryAbsenceService.reject(id, reason);
        fetchAbsences();
      } catch (error) {
        console.error("Error rejecting absence:", error);
        alert("Có lỗi xảy ra khi từ chối đơn");
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "Đã duyệt":
        return "success";
      case "Từ chối":
        return "error";
      case "Chờ duyệt":
        return "warning";
      default: 
        return "default";
    }
  };

  return (
    <Box sx={{ bgcolor: "background.default", minHeight: "100vh" }}>
      <Navbar />
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Quản lý tạm vắng
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Danh sách và quản lý giấy tạm vắng
          </Typography>
        </Box>

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card sx={{ bgcolor: "primary.light", color: "white" }}>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                  <ExitIcon sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {totalCount}
                    </Typography>
                    <Typography variant="body2">Tổng số đơn</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ bgcolor: "warning.light", color: "white" }}>
              <CardContent>
                <Box sx={{ display:  "flex", alignItems: "center", gap: 2 }}>
                  <ExitIcon sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {absences.filter((a) => a.trang_thai === "Chờ duyệt").length}
                    </Typography>
                    <Typography variant="body2">Chờ duyệt</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ bgcolor: "success.light", color: "white" }}>
              <CardContent>
                <Box sx={{ display:  "flex", alignItems: "center", gap: 2 }}>
                  <CheckIcon sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {absences.filter((a) => a.trang_thai === "Đã duyệt").length}
                    </Typography>
                    <Typography variant="body2">Đã duyệt</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ bgcolor: "error.light", color: "white" }}>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", gap:  2 }}>
                  <CloseIcon sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {absences.filter((a) => a.trang_thai === "Từ chối").length}
                    </Typography>
                    <Typography variant="body2">Từ chối</Typography>
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
                placeholder="Tìm kiếm theo mã giấy, họ tên, CCCD..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
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
                label="Trạng thái"
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <MenuItem value="all">Tất cả</MenuItem>
                <MenuItem value="Chờ duyệt">Chờ duyệt</MenuItem>
                <MenuItem value="Đã duyệt">Đã duyệt</MenuItem>
                <MenuItem value="Từ chối">Từ chối</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={5} sx={{ display: "flex", gap: 1, justifyContent: "flex-end" }}>
              <Button variant="outlined" startIcon={<RefreshIcon />} onClick={fetchAbsences}>
                Làm mới
              </Button>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => navigate("/management/temporary-absence/create")}
              >
                Thêm đơn tạm vắng
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
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>Mã giấy</TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>Họ và tên</TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>CCCD</TableCell>
                <TableCell sx={{ color: "white", fontWeight:  "bold" }}>Từ ngày</TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>Đến ngày</TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>Nơi đến</TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }} align="center">
                  Trạng thái
                </TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }} align="center">
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
              ) : absences.length === 0 ?  (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    Không có dữ liệu
                  </TableCell>
                </TableRow>
              ) : (
                absences.map((absence, index) => (
                  <TableRow key={absence.id} hover sx={{ "&:hover": { bgcolor: "action.hover" } }}>
                    <TableCell>{page * rowsPerPage + index + 1}</TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium" color="primary">
                        {absence.ma_giay}
                      </Typography>
                    </TableCell>
                    <TableCell>{absence.ho_ten}</TableCell>
                    <TableCell>{absence.cccd}</TableCell>
                    <TableCell>
                      {new Date(absence.tu_ngay).toLocaleDateString("vi-VN")}
                    </TableCell>
                    <TableCell>
                      {new Date(absence.den_ngay).toLocaleDateString("vi-VN")}
                    </TableCell>
                    <TableCell>{absence.noi_den}</TableCell>
                    <TableCell align="center">
                      <Chip
                        label={absence.trang_thai}
                        size="small"
                        color={getStatusColor(absence.trang_thai)}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Tooltip title="Xem chi tiết">
                        <IconButton
                          size="small"
                          color="info"
                          onClick={() => handleViewDetails(absence)}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      {absence.trang_thai === "Chờ duyệt" && (
                        <>
                          <Tooltip title="Duyệt">
                            <IconButton
                              size="small"
                              color="success"
                              onClick={() => handleApprove(absence.id)}
                            >
                              <CheckIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Từ chối">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleReject(absence.id)}
                            >
                              <CloseIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </>
                      )}
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
              Chi tiết giấy tạm vắng
            </Typography>
          </DialogTitle>
          <DialogContent dividers>
            {selectedAbsence && (
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Mã giấy
                  </Typography>
                  <Typography variant="body1" fontWeight="medium" color="primary">
                    {selectedAbsence.ma_giay}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text. secondary">
                    Trạng thái
                  </Typography>
                  <Chip
                    label={selectedAbsence.trang_thai}
                    size="small"
                    color={getStatusColor(selectedAbsence.trang_thai)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Họ và tên
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {selectedAbsence.ho_ten}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    CCCD
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {selectedAbsence.cccd}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Số hộ khẩu
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {selectedAbsence. so_ho_khau}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Nơi đến
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {selectedAbsence.noi_den}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Từ ngày
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {new Date(selectedAbsence.tu_ngay).toLocaleDateString("vi-VN")}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Đến ngày
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {new Date(selectedAbsence.den_ngay).toLocaleDateString("vi-VN")}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Lý do
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {selectedAbsence. ly_do}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Ngày tạo
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {new Date(selectedAbsence.ngay_tao).toLocaleString("vi-VN")}
                  </Typography>
                </Grid>
              </Grid>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Đóng</Button>
            {selectedAbsence?. trang_thai === "Chờ duyệt" && (
              <>
                <Button
                  variant="outlined"
                  color="error"
                  onClick={() => {
                    setOpenDialog(false);
                    handleReject(selectedAbsence. id);
                  }}
                >
                  Từ chối
                </Button>
                <Button
                  variant="contained"
                  color="success"
                  onClick={() => {
                    setOpenDialog(false);
                    handleApprove(selectedAbsence.id);
                  }}
                >
                  Duyệt
                </Button>
              </>
            )}
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}