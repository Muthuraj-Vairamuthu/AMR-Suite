import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "../styles/AnalysisPage.module.css"; // Shared styles
import Header from "../components/Header";
import scorecardimage from "../assets/image3.png";
const ScorecardsPage = () => {
  const navigate = useNavigate();

  return (
    <div className={styles.analysisPage}>
      <Header />
      <main className={styles.mainContent}>
        <div className={styles.leftSection}>
          <button className={styles.backButton} onClick={() => navigate("/processing")}>
            &#8592;
          </button>
          <h1>Scorecards</h1>
          <div className={styles.formGroup}>
            <label>Choose Infection: <span className={styles.required}>*</span></label>
            <select className={styles.formInput}>
              <option>Choose Column</option>
            </select>
          </div>
          <div className={styles.formGroup}>
            <label>Choose Antibiotic: <span className={styles.required}>*</span></label>
            <select className={styles.formInput}>
              <option>Choose Column</option>
            </select>
          </div>
          <div className={styles.formGroup}>
            <label>Choose Sample: <span className={styles.required}>*</span></label>
            <select className={styles.formInput}>
              <option>Choose Column</option>
            </select>
          </div>
          <button className={styles.generateButton}>Generate</button>
        </div>
        <div className={styles.rightSection}>
          <img src={scorecardimage} alt="Placeholder" className={styles.chartImage} />
        </div>
      </main>
    </div>
  );
};

export default ScorecardsPage;
