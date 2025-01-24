import React from "react";
import styles from "../styles/ProcessingResultsPage.module.css"; // Page-specific CSS
import Header from "../components/Header";

const ProcessingResultsPage = () => {
  return (
    <div className={styles.processingResultsPage}>
      <Header />

      <main className={styles.mainContent}>
        {/* Left Section: Processing Status */}
        <div className={styles.leftSection}>
          <h1 className={styles.pageTitle}>Processing your Dataset</h1>
          <div className={styles.statusItem}>
            <span className={styles.iconCheck}>&#10004;</span>
            <span>Loaded the Dataset</span>
          </div>
          <div className={styles.statusItem}>
            <div className={styles.iconSpinner}></div>
            <span>Created Mappings</span>
          </div>
          <div className={styles.statusItem}>
            <div className={styles.iconSpinner}></div>
            <span>Checking Data Integrity</span>
          </div>
          <div className={styles.statusItem}>
            <div className={styles.iconSpinner}></div>
            <span>Running Tests</span>
          </div>
          <div className={styles.statusItem}>
            <div className={styles.iconSpinner}></div>
            <span>Creating list of Antibiotics</span>
          </div>
          <div className={styles.statusItem}>
            <div className={styles.iconSpinner}></div>
            <span>Generating Scorecards</span>
          </div>

        </div>

        {/* Right Section: View Results */}
        <div className={styles.rightSection}>
          <h2 className={styles.resultsTitle}>View Results</h2>
          <button className={styles.resultButton}>Isolation Burden Analysis</button>
          <button className={styles.resultButton}>Resistance Analysis</button>
          <button className={styles.resultButton}>Scorecards</button>
        </div>
      </main>
    </div>
  );
};

export default ProcessingResultsPage;
