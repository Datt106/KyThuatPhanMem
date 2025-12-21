import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  Divider,
  IconButton,
  Card,
  CardContent,
  CardHeader,
  Alert,
  Stepper,
  Step,
  StepLabel,
  MenuItem,
} from "@mui/material";
import {
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  PersonAdd as PersonAddIcon,
  Delete as DeleteIcon,
  NavigateNext as NextIcon,
  NavigateBefore as BackIcon,
} from "@mui/icons-material";
import Navbar from "../../../components/Navbar";
import { managementHouseholdService } from "../../../services/api";

const steps = ["Thông tin hộ khẩu", "Thông tin chủ hộ", "Thành viên khác"];

const initialHouseholdData = {
  ma_ho_khau: "",
  so_nha: "",
  duong_pho: "",
  phuong_xa: "",
  quan_huyen: "",
};

const initialCitizenData = {
  ma_nhan_khau: "",
  ho_ten: "",
  ngay_sinh: "",
  gioi_tinh: "",
  noi_sinh: "",
  nguyen_quan: "",
  dan_toc: "Kinh",
  ton_giao: "Không",
  quoc_tich: "Việt Nam",
  nghe_nghiep: "",
  noi_lam_viec: "",
  so_cmt: "",
  ngay_cap: "",
  noi_cap: "",
};

export default function HouseholdCreate() {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Form data
  const [householdData, setHouseholdData] = useState(initialHouseholdData);
  const [chuHoData, setChuHoData] = useState(initialCitizenData);
  const [thanhVien, setThanhVien] = useState([]);

  // Validation errors
  const [householdErrors, setHouseholdErrors] = useState({});
  const [chuHoErrors, setChuHoErrors] = useState({});

  // Handle household data change
  const handleHouseholdChange = (field, value) => {
    setHouseholdData((prev) => ({ ...prev, [field]: value }));
    setHouseholdErrors((prev) => ({ ...prev, [field]: "" }));
  };

  // Handle chu ho data change
  const handleChuHoChange = (field, value) => {
    setChuHoData((prev) => ({ ...prev, [field]: value }));
    setChuHoErrors((prev) => ({ ...prev, [field]: "" }));
  };

  // Handle member change
  const handleMemberChange = (index, field, value) => {
    const updated = [...thanhVien];
    updated[index] = { ...updated[index], [field]:  value };
    setThanhVien(updated);
  };

  // Add new member
  const handleAddMember = () => {
    setThanhVien([
      ...thanhVien,
      { ... initialCitizenData, quan_he_voi_chu_ho:  "" },
    ]);
  };

  // Remove member
  const handleRemoveMember = (index) => {
    setThanhVien(thanhVien.filter((_, i) => i !== index));
  };

  // Validate household form
  const validateHouseholdForm = () => {
    const errors = {};
    if (!householdData.ma_ho_khau. trim()) {
      errors.ma_ho_khau = "Vui lòng nhập mã hộ khẩu";
    }
    if (!householdData.so_nha.trim()) {
      errors.so_nha = "Vui lòng nhập số nhà";
    }
    if (!householdData.duong_pho.trim()) {
      errors.duong_pho = "Vui lòng nhập đường phố";
    }
    if (! householdData.phuong_xa.trim()) {
      errors.phuong_xa = "Vui lòng nhập phường/xã";
    }
    if (!householdData.quan_huyen.trim()) {
      errors.quan_huyen = "Vui lòng nhập quận/huyện";
    }
    setHouseholdErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Validate chu ho form
  const validateChuHoForm = () => {
    const errors = {};
    if (!chuHoData.ma_nhan_khau.trim()) {
      errors.ma_nhan_khau = "Vui lòng nhập mã nhân khẩu";
    }
    if (!chuHoData.ho_ten.trim()) {
      errors.ho_ten = "Vui lòng nhập họ tên";
    }
    if (!chuHoData.ngay_sinh) {
      errors.ngay_sinh = "Vui lòng chọn ngày sinh";
    }
    if (!chuHoData.gioi_tinh) {
      errors.gioi_tinh = "Vui lòng chọn giới tính";
    }
    if (!chuHoData.noi_sinh. trim()) {
      errors.noi_sinh = "Vui lòng nhập nơi sinh";
    }
    setChuHoErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle next step
  const handleNext = () => {
    if (activeStep === 0 && ! validateHouseholdForm()) {
      setError("Vui lòng điền đầy đủ thông tin hộ khẩu");
      return;
    }
    if (activeStep === 1 && ! validateChuHoForm()) {
      setError("Vui lòng điền đầy đủ thông tin chủ hộ");
      return;
    }
    setError("");
    setActiveStep((prev) => prev + 1);
  };

  // Handle back step
  const handleBack = () => {
    setError("");
    setActiveStep((prev) => prev - 1);
  };

  // Handle submit
  const handleSubmit = async () => {
    if (!validateHouseholdForm() || !validateChuHoForm()) {
      setError("Vui lòng kiểm tra lại thông tin");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const payload = {
        ... householdData,
        chu_ho: chuHoData,
        thanh_vien: thanhVien. filter(
          (tv) => tv.ho_ten && tv.ma_nhan_khau && tv.quan_he_voi_chu_ho
        ),
      };

      await managementHouseholdService. create(payload);
      setSuccess("Tạo hộ khẩu thành công!");
      
      setTimeout(() => {
        navigate("/management/household-management");
      }, 2000);
    } catch (error) {
      console.error("Error creating household:", error);
      setError(
        error.response?.data?.error || "Có lỗi xảy ra khi tạo hộ khẩu"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ bgcolor: "background.default", minHeight: "100vh" }}>
      <Navbar />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4, display: "flex", alignItems: "center", gap: 2 }}>
          <IconButton onClick={() => navigate("/management/household-management")}>
            <ArrowBackIcon />
          </IconButton>
          <Box>
            <Typography variant="h4" fontWeight="bold">
              Tạo hộ khẩu mới
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Nhập thông tin hộ khẩu và thành viên
            </Typography>
          </Box>
        </Box>

        {/* Stepper */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Stepper activeStep={activeStep}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </Paper>

        {/* Alerts */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError("")}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" sx={{ mb: 3 }}>
            {success}
          </Alert>
        )}

        {/* Step 0:  Household Information */}
        {activeStep === 0 && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Thông tin hộ khẩu
            </Typography>
            <Divider sx={{ mb: 3 }} />
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  required
                  label="Mã hộ khẩu"
                  value={householdData.ma_ho_khau}
                  onChange={(e) => handleHouseholdChange("ma_ho_khau", e.target.value)}
                  error={!! householdErrors.ma_ho_khau}
                  helperText={householdErrors. ma_ho_khau}
                  placeholder="VD:  HK001234"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  required
                  label="Số nhà"
                  value={householdData.so_nha}
                  onChange={(e) => handleHouseholdChange("so_nha", e. target.value)}
                  error={!!householdErrors.so_nha}
                  helperText={householdErrors. so_nha}
                  placeholder="VD: 123"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  required
                  label="Đường phố"
                  value={householdData.duong_pho}
                  onChange={(e) => handleHouseholdChange("duong_pho", e.target.value)}
                  error={!!householdErrors.duong_pho}
                  helperText={householdErrors. duong_pho}
                  placeholder="VD:  Lê Lợi"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  required
                  label="Phường/Xã"
                  value={householdData.phuong_xa}
                  onChange={(e) => handleHouseholdChange("phuong_xa", e.target.value)}
                  error={!!householdErrors.phuong_xa}
                  helperText={householdErrors.phuong_xa}
                  placeholder="VD: Phường 1"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  required
                  label="Quận/Huyện"
                  value={householdData.quan_huyen}
                  onChange={(e) => handleHouseholdChange("quan_huyen", e.target.value)}
                  error={!!householdErrors. quan_huyen}
                  helperText={householdErrors.quan_huyen}
                  placeholder="VD: Quận 1"
                />
              </Grid>
            </Grid>
          </Paper>
        )}

        {/* Step 1: Head of Household */}
        {activeStep === 1 && (
          <Paper sx={{ p:  3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Thông tin chủ hộ
            </Typography>
            <Divider sx={{ mb: 3 }} />
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  required
                  label="Mã nhân khẩu"
                  value={chuHoData.ma_nhan_khau}
                  onChange={(e) => handleChuHoChange("ma_nhan_khau", e.target.value)}
                  error={!!chuHoErrors.ma_nhan_khau}
                  helperText={chuHoErrors.ma_nhan_khau}
                  placeholder="VD: NK001234"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  required
                  label="Họ và tên"
                  value={chuHoData.ho_ten}
                  onChange={(e) => handleChuHoChange("ho_ten", e.target.value)}
                  error={!!chuHoErrors.ho_ten}
                  helperText={chuHoErrors. ho_ten}
                  placeholder="VD: Nguyễn Văn A"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  required
                  type="date"
                  label="Ngày sinh"
                  value={chuHoData.ngay_sinh}
                  onChange={(e) => handleChuHoChange("ngay_sinh", e. target.value)}
                  error={!!chuHoErrors. ngay_sinh}
                  helperText={chuHoErrors.ngay_sinh}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  required
                  select
                  label="Giới tính"
                  value={chuHoData.gioi_tinh}
                  onChange={(e) => handleChuHoChange("gioi_tinh", e.target.value)}
                  error={!!chuHoErrors.gioi_tinh}
                  helperText={chuHoErrors.gioi_tinh}
                >
                  <MenuItem value="Nam">Nam</MenuItem>
                  <MenuItem value="Nữ">Nữ</MenuItem>
                  <MenuItem value="Khác">Khác</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Dân tộc"
                  value={chuHoData.dan_toc}
                  onChange={(e) => handleChuHoChange("dan_toc", e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  required
                  label="Nơi sinh"
                  value={chuHoData.noi_sinh}
                  onChange={(e) => handleChuHoChange("noi_sinh", e.target.value)}
                  error={!!chuHoErrors.noi_sinh}
                  helperText={chuHoErrors.noi_sinh}
                  placeholder="VD:  TP.  Hồ Chí Minh"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Nguyên quán"
                  value={chuHoData.nguyen_quan}
                  onChange={(e) => handleChuHoChange("nguyen_quan", e.target.value)}
                  placeholder="VD: Hà Nội"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Tôn giáo"
                  value={chuHoData.ton_giao}
                  onChange={(e) => handleChuHoChange("ton_giao", e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Quốc tịch"
                  value={chuHoData.quoc_tich}
                  onChange={(e) => handleChuHoChange("quoc_tich", e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Nghề nghiệp"
                  value={chuHoData. nghe_nghiep}
                  onChange={(e) => handleChuHoChange("nghe_nghiep", e.target. value)}
                  placeholder="VD: Kỹ sư"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Nơi làm việc"
                  value={chuHoData.noi_lam_viec}
                  onChange={(e) => handleChuHoChange("noi_lam_viec", e. target.value)}
                  placeholder="VD: Công ty ABC"
                />
              </Grid>

              {/* ID Card Information */}
              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Thông tin CMND/CCCD (Không bắt buộc)
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Số CMND/CCCD"
                  value={chuHoData.so_cmt}
                  onChange={(e) => handleChuHoChange("so_cmt", e. target.value)}
                  placeholder="VD: 001234567890"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  type="date"
                  label="Ngày cấp"
                  value={chuHoData.ngay_cap}
                  onChange={(e) => handleChuHoChange("ngay_cap", e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Nơi cấp"
                  value={chuHoData.noi_cap}
                  onChange={(e) => handleChuHoChange("noi_cap", e.target.value)}
                  placeholder="VD:  CA TP. HCM"
                />
              </Grid>
            </Grid>
          </Paper>
        )}

        {/* Step 2: Other Members */}
        {activeStep === 2 && (
          <Box>
            <Box sx={{ mb: 2, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <Typography variant="h6" fontWeight="bold">
                Thành viên khác (Không bắt buộc)
              </Typography>
              <Button
                variant="outlined"
                startIcon={<PersonAddIcon />}
                onClick={handleAddMember}
              >
                Thêm thành viên
              </Button>
            </Box>

            {thanhVien.length === 0 ? (
              <Paper sx={{ p: 4, textAlign: "center" }}>
                <Typography color="text.secondary">
                  Chưa có thành viên nào.  Nhấn "Thêm thành viên" để thêm. 
                </Typography>
              </Paper>
            ) : (
              thanhVien.map((member, index) => (
                <Card key={index} sx={{ mb:  3 }}>
                  <CardHeader
                    title={`Thành viên ${index + 1}`}
                    action={
                      <IconButton color="error" onClick={() => handleRemoveMember(index)}>
                        <DeleteIcon />
                      </IconButton>
                    }
                  />
                  <CardContent>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          required
                          label="Mã nhân khẩu"
                          value={member.ma_nhan_khau}
                          onChange={(e) =>
                            handleMemberChange(index, "ma_nhan_khau", e.target.value)
                          }
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          required
                          label="Họ và tên"
                          value={member.ho_ten}
                          onChange={(e) =>
                            handleMemberChange(index, "ho_ten", e.target.value)
                          }
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          required
                          select
                          label="Quan hệ với chủ hộ"
                          value={member.quan_he_voi_chu_ho}
                          onChange={(e) =>
                            handleMemberChange(index, "quan_he_voi_chu_ho", e.target.value)
                          }
                          size="small"
                        >
                          <MenuItem value="Vợ/Chồng">Vợ/Chồng</MenuItem>
                          <MenuItem value="Con">Con</MenuItem>
                          <MenuItem value="Cha/Mẹ">Cha/Mẹ</MenuItem>
                          <MenuItem value="Anh/Chị/Em">Anh/Chị/Em</MenuItem>
                          <MenuItem value="Ông/Bà">Ông/Bà</MenuItem>
                          <MenuItem value="Cháu">Cháu</MenuItem>
                          <MenuItem value="Khác">Khác</MenuItem>
                        </TextField>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <TextField
                          fullWidth
                          type="date"
                          label="Ngày sinh"
                          value={member.ngay_sinh}
                          onChange={(e) =>
                            handleMemberChange(index, "ngay_sinh", e. target.value)
                          }
                          InputLabelProps={{ shrink: true }}
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <TextField
                          fullWidth
                          select
                          label="Giới tính"
                          value={member.gioi_tinh}
                          onChange={(e) =>
                            handleMemberChange(index, "gioi_tinh", e.target.value)
                          }
                          size="small"
                        >
                          <MenuItem value="Nam">Nam</MenuItem>
                          <MenuItem value="Nữ">Nữ</MenuItem>
                          <MenuItem value="Khác">Khác</MenuItem>
                        </TextField>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <TextField
                          fullWidth
                          label="Nơi sinh"
                          value={member.noi_sinh}
                          onChange={(e) =>
                            handleMemberChange(index, "noi_sinh", e.target.value)
                          }
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <TextField
                          fullWidth
                          label="Nghề nghiệp"
                          value={member.nghe_nghiep}
                          onChange={(e) =>
                            handleMemberChange(index, "nghe_nghiep", e.target.value)
                          }
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          label="Số CMND/CCCD"
                          value={member.so_cmt}
                          onChange={(e) =>
                            handleMemberChange(index, "so_cmt", e.target.value)
                          }
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          type="date"
                          label="Ngày cấp"
                          value={member.ngay_cap}
                          onChange={(e) =>
                            handleMemberChange(index, "ngay_cap", e.target.value)
                          }
                          InputLabelProps={{ shrink:  true }}
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          label="Nơi cấp"
                          value={member.noi_cap}
                          onChange={(e) =>
                            handleMemberChange(index, "noi_cap", e.target. value)
                          }
                          size="small"
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              ))
            )}
          </Box>
        )}

        {/* Navigation Buttons */}
        <Box sx={{ mt: 3, display: "flex", justifyContent: "space-between" }}>
          <Button
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate("/management/household-management")}
          >
            Hủy
          </Button>
          <Box sx={{ display: "flex", gap: 2 }}>
            {activeStep > 0 && (
              <Button
                variant="outlined"
                startIcon={<BackIcon />}
                onClick={handleBack}
                disabled={loading}
              >
                Quay lại
              </Button>
            )}
            {activeStep < steps.length - 1 ?  (
              <Button
                variant="contained"
                endIcon={<NextIcon />}
                onClick={handleNext}
              >
                Tiếp theo
              </Button>
            ) : (
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSubmit}
                disabled={loading}
              >
                {loading ? "Đang lưu..." : "Hoàn thành"}
              </Button>
            )}
          </Box>
        </Box>
      </Container>
    </Box>
  );
}