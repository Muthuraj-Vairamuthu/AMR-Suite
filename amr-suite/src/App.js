import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import DatasetMappingPage from "./pages/DatasetMappingPage";
import ProcessingPage from "./pages/ProcessingPage";
import IsolationBurdenAnalysisPage from "./pages/IsolationBurdenAnalysisPage";
import ResistanceAnalysisPage from "./pages/ResistanceAnalysisPage";
import ScorecardsPage from "./pages/ScorecardsPage";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<DatasetMappingPage />} />
        <Route path="/processing" element={<ProcessingPage />} />
        <Route path="/isolation-burden" element={<IsolationBurdenAnalysisPage />} />
        <Route path="/resistance-analysis" element={<ResistanceAnalysisPage />} />
        <Route path="/scorecards" element={<ScorecardsPage />} />
      </Routes>
    </Router>
  );
};

export default App;
