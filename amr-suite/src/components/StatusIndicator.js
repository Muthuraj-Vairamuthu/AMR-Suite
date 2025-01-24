import React from "react";
import { Box, Typography } from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import HourglassEmptyIcon from "@mui/icons-material/HourglassEmpty";

const StatusIndicator = ({ label, completed }) => {
  return (
    <Box display="flex" alignItems="center" marginBottom="8px">
      {completed ? (
        <CheckCircleIcon style={{ color: "#4caf50", marginRight: "8px" }} />
      ) : (
        <HourglassEmptyIcon style={{ color: "#00bcd4", marginRight: "8px" }} />
      )}
      <Typography>{label}</Typography>
    </Box>
  );
};

export default StatusIndicator;
