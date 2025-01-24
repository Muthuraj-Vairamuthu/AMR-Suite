import React from "react";
import styles from "../styles/DatasetMappingPage.module.css";
import Header from "../components/Header";
import { useNavigate } from "react-router-dom"; 

const DatasetMappingPage = () => {
    const navigate = useNavigate(); 

    const handleNext = () => {
        navigate("/processing");
  };
  return (
    <div className={styles.datasetMappingPage}>
      <Header />

      <main className={styles.mainContent}>
        <h1 className={styles.pageTitle}>Processing your Dataset</h1>

        <div className={styles.formContainer}>
          {/* Map Dataset Columns */}
          <div
            className={styles.container}
            style={{ width: "573px", height: "400px" }}
          >
            <h2 className={styles.sectionTitle}>Map Dataset Columns</h2>
            <div className={styles.formGroup}>
              <label>
                Bacterial Infection: <span className={styles.required}>*</span>
              </label>
              <select className={styles.formInput}>
                <option>Choose Column</option>
              </select>
            </div>
            <div className={styles.formGroup}>
              <label>
                Source Input: <span className={styles.required}>*</span>
              </label>
              <select className={styles.formInput}>
                <option>Choose Column</option>
              </select>
            </div>
            <div className={styles.formGroup}>
              <label>
                Antibiotic Format: <span className={styles.required}>*</span>
              </label>
              <input
                type="text"
                className={styles.formInput}
                placeholder="Column Format"
              />
            </div>
          </div>

          {/* Dataset Details */}
          <div
            className={styles.container}
            style={{ width: "573px", height: "400px" }}
          >
            <h2 className={styles.sectionTitle}>Dataset Details</h2>
            <div className={styles.formGroup}>
              <label>
                Dataset Format: <span className={styles.required}>*</span>
              </label>
              <select className={styles.formInput}>
                <option>Choose Column</option>
              </select>
            </div>
            <div className={styles.formGroup}>
              <label>
                Cluster Attribute: <span className={styles.required}>*</span>
              </label>
              <select className={styles.formInput}>
                <option>Choose Column</option>
              </select>
            </div>
            <div className={styles.formGroup}>
              <label>
                Time Stamp: <span className={styles.required}>*</span>
              </label>
              <select className={styles.formInput}>
                <option>Choose Trend</option>
              </select>
            </div>
          </div>
        </div>

        {/* Next Button */}
        <div className={styles.formFooter}>
          <button
            className={styles.nextButton}
            style={{
              width: "400px",
              height: "114px",
              borderRadius: "30px",
              marginTop: "40px",
            }}
            onClick={handleNext}
          >
            Next
          </button>
        </div>
      </main>
    </div>
  );
};

export default DatasetMappingPage;
