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
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  People as PeopleIcon,
  Home as HomeIcon,
  Refresh as RefreshIcon,
} from "@mui/icons-material";
import Navbar from "../../../components/Navbar";
import { managementHouseholdService } from "../../../services/api";

export default function HouseholdList() {
  const navigate = useNavigate();

  const [households, setHouseholds] = useState([]);
  const [loading, setLoading] = useState(true);

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");

  const [openDialog, setOpenDialog] = useState(false);
  const [selectedHousehold, setSelectedHousehold] = useState(null);

  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    fetchHouseholds();
  }, [page, rowsPerPage, searchTerm, filterStatus]);

  const fetchHouseholds = async () => {
    try {
      setLoading(true);

      const res = await managementHouseholdService.getAll({
        search: searchTerm,
        status: filterStatus !== "all" ? filterStatus : undefined,
      });

      // ✅ BACKEND TRẢ ARRAY TRỰC TIẾP
      setHouseholds(res.data);
      setTotalCount(res.data.length);
    } catch (err) {
      console.error("Fetch households error:", err);
      setHouseholds([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (_, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (e) => {
    setRowsPerPage(parseInt(e.target.value, 10));
    setPage(0);
  };

  const handleViewDetails = (household) => {
    setSelectedHousehold(household);
    setOpenDialog(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Bạn có chắc chắn muốn xóa hộ khẩu này?")) return;
    try {
      await managementHouseholdService.delete(id);
      fetchHouseholds();
    } catch (err) {
      alert("Xóa thất bại");
    }
  };

  // ✅ paginate frontend
  const pagedHouseholds = households.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  return (
    <Box sx={{ minHeight: "100vh" }}>
      <Navbar />
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" fontWeight="bold">
          Quản lý hộ khẩu
        </Typography>

        {/* STATS */}
        <Grid container spacing={3} sx={{ my: 3 }}>
          <Grid item md={4}>
            <Card>
              <CardContent>
                <HomeIcon /> Tổng số hộ khẩu: {totalCount}
              </CardContent>
            </Card>
          </Grid>
          <Grid item md={4}>
            <Card>
              <CardContent>
                <PeopleIcon /> Tổng nhân khẩu:{" "}
                {households.reduce((s, h) => s + (h.so_thanh_vien || 0), 0)}
              </CardContent>
            </Card>
          </Grid>
          <Grid item md={4}>
            <Card>
              <CardContent>
                TB nhân khẩu/hộ:{" "}
                {totalCount
                  ? (
                      households.reduce(
                        (s, h) => s + (h.so_thanh_vien || 0),
                        0
                      ) / totalCount
                    ).toFixed(1)
                  : 0}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* TOOLBAR */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2}>
            <Grid item md={4}>
              <TextField
                fullWidth
                size="small"
                placeholder="Tìm kiếm..."
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

            <Grid item md={3}>
              <TextField
                fullWidth
                select
                size="small"
                label="Trạng thái"
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <MenuItem value="all">Tất cả</MenuItem>
                <MenuItem value="active">Hoạt động</MenuItem>
                <MenuItem value="inactive">Không hoạt động</MenuItem>
              </TextField>
            </Grid>

            <Grid
              item
              md={5}
              sx={{ display: "flex", justifyContent: "flex-end", gap: 1 }}
            >
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={fetchHouseholds}
              >
                Làm mới
              </Button>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() =>
                  navigate("/management/household-management/create")
                }
              >
                Thêm hộ khẩu
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* TABLE */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>STT</TableCell>
                <TableCell>Số hộ khẩu</TableCell>
                <TableCell>Chủ hộ</TableCell>
                <TableCell>Địa chỉ</TableCell>
                <TableCell align="center">Số thành viên</TableCell>
                <TableCell>Ngày tạo</TableCell>
                <TableCell align="center">Thao tác</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    Đang tải...
                  </TableCell>
                </TableRow>
              ) : pagedHouseholds.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    Không có dữ liệu
                  </TableCell>
                </TableRow>
              ) : (
                pagedHouseholds.map((h, i) => (
                  <TableRow key={h.id}>
                    <TableCell>{page * rowsPerPage + i + 1}</TableCell>
                    <TableCell>{h.ma_ho_khau}</TableCell>
                    <TableCell>{h.ten_chu_ho}</TableCell>
                    <TableCell>{h.dia_chi}</TableCell>
                    <TableCell align="center">{h.so_thanh_vien}</TableCell>
                    <TableCell>
                      {new Date(h.created_at).toLocaleDateString("vi-VN")}
                    </TableCell>
                    <TableCell align="center">
                      <IconButton onClick={() => handleViewDetails(h)}>
                        <VisibilityIcon />
                      </IconButton>
                      <IconButton
                        onClick={() =>
                          navigate(
                            `/management/household-management/edit/${h.id}`
                          )
                        }
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton onClick={() => handleDelete(h.id)}>
                        <DeleteIcon />
                      </IconButton>
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
          />
        </TableContainer>
      </Container>
    </Box>
  );
}
