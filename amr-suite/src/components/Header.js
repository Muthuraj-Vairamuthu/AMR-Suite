import React from "react";
import { AppBar, Toolbar, Typography, Box } from "@mui/material";

const Header = () => {
  return (
    <AppBar position="static" style={{ backgroundColor: "#1c1c28", padding: "0 16px" }}>
      <Toolbar style={{ display: "flex", justifyContent: "space-between" }}>
        <Box display="flex" alignItems="center">
          <Box component="img" src="/assets/logo.png" alt="Logo" height="40px" />
          <Typography variant="h6" style={{ marginLeft: "16px" }}>
            AMRSuite
          </Typography>
        </Box>
        <Typography variant="h6">Home</Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
