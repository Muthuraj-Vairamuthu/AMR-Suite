import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import DatasetMappingPage from "./pages/DatasetMappingPage";
import ProcessingPage from "./pages/ProcessingPage";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<DatasetMappingPage />} />
        <Route path="/processing" element={<ProcessingPage />} />
      </Routes>
    </Router>
  );
};

export default App;
