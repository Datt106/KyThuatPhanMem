const express = require("express");
const cors = require("cors");
require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors({
  origin: "http://localhost:5173", // FE host
  credentials: true               // nếu có dùng cookie/token
}));
app.use(express.json());
app.use("/uploads", express.static("uploads"));

const userRoutes = require("./src/routes/user");
const homeRoutes = require("./src/routes/home");
const authRoutes = require("./src/routes/auth");
const profileRoutes = require("./src/routes/profile");
const phananhRoutes = require("./src/routes/phananh");

app.use("/home", homeRoutes);
app.use("/api/users", userRoutes);
app.use("/api/auth", authRoutes);
app.use("/api/profile", profileRoutes);
app.use("/api/phan-anh",phananhRoutes);
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

app.get('/test', (req, res) => res.send('Server is running!'));
