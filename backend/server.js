const express = require("express");
const cors = require("cors");
require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());
app.use("/uploads", express.static("uploads"));

const userRoutes = require("./src/routes/user");
const homeRoutes = require("./src/routes/home");
const authRoutes = require("./src/routes/auth");

app.use("/home", homeRoutes);
app.use("/api/users", userRoutes);
app.use("/api/auth", authRoutes);

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

app.get('/test', (req, res) => res.send('Server is running!'));
