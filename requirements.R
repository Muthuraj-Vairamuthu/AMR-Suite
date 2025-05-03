required_packages <- c(
  "dplyr",
  "tidyr",
  "stringi",
  "ggplot2",
  "purrr",
  "lubridate",
  "lmtest",
  "sandwich",
  "stats",    # base R package, included for completeness
  "zoo"
)

# Install and load each package
for (pkg in required_packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    message(paste("Installing missing package:", pkg))
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
  suppressPackageStartupMessages(library(pkg, character.only = TRUE))
}