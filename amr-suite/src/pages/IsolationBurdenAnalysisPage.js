import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "../styles/AnalysisPage.module.css"; // Shared styles
import Header from "../components/Header";
import isolationImage from "../assets/image.png";
const IsolationBurdenAnalysisPage = () => {
  const navigate = useNavigate();

  return (
    <div className={styles.analysisPage}>
      <Header />
      <main className={styles.mainContent}>
        <div className={styles.leftSection}>
          <button className={styles.backButton} onClick={() => navigate("/processing")}>
            &#8592;
          </button>
          <h1>Isolation Burden Analysis</h1>
          <div className={styles.formGroup}>
            <label>Choose Attribute: <span className={styles.required}>*</span></label>
            <select className={styles.formInput}>
              <option>Choose Column</option>
            </select>
          </div>
          <div className={styles.formGroup}>
            <label>Choose Source: <span className={styles.required}>*</span></label>
            <select className={styles.formInput}>
              <option>Choose Column</option>
            </select>
          </div>
          <button className={styles.generateButton}>Generate</button>
        </div>
        <div className={styles.rightSection}>
          <img src={isolationImage} alt="Placeholder" className={styles.chartImage} />
        </div>
      </main>
    </div>
  );
};

export default IsolationBurdenAnalysisPage;
