args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 8) {
  stop("Usage: Rscript cluster_model_final.R ",
       "<organism> <antibiotic> <source> <start_year> <end_year> ",
       "<dataset_path> <cluster_attribute> <time_attribute>")
}

organism          <- args[1]
antibiotic        <- args[2]
source_input      <- args[3]
start_year        <- as.integer(args[4])
end_year          <- as.integer(args[5])
dataset_path      <- args[6]
cluster_attribute <- args[7]
time_attribute    <- args[8]
baseline_attribute <- 'India'

cat(organism, antibiotic, source_input, start_year, end_year, dataset_path, cluster_attribute, time_attribute, "\n")

library(dplyr)
library(lubridate)
library(lmtest)
library(sandwich)
library(stats)
library(zoo)
set.seed(123)

# Read dataset
antibiotic_data <- read.csv(dataset_path)

# Moving average function
moving_avg <- function(x, n) {
  rollmean(x, k = n, fill = "extend", align = "center")
}

# Preprocessing
read_and_filter_data <- function(organism, antibiotic_data, source) {
  df <- antibiotic_data %>%
    mutate(gender = tools::toTitleCase(Gender),
           country = tools::toTitleCase(Country)) %>%
    filter(Species == organism,
           Source == source,
           Year >= start_year & Year <= end_year)
  return(df)
}

df <- read_and_filter_data(organism, antibiotic_data, source_input)
cat("Antibiotic:", antibiotic, "\n")

# Yearly aggregation
yearly_data <- df %>%
  filter(.data[[antibiotic]] %in% c("Resistant", "Intermediate", "Susceptible")) %>%
  group_by(.data[[cluster_attribute]], .data[[time_attribute]]) %>%
  summarize(
    total_samples = n(),
    resistant_samples = sum(.data[[antibiotic]] == "Resistant", na.rm = TRUE),
    resistance_percentage = (resistant_samples / total_samples) * 100,
    .groups = "drop"
  )

# Global data
global_data <- df %>%
  filter(.data[[antibiotic]] %in% c("Resistant", "Intermediate", "Susceptible")) %>%
  group_by(.data[[time_attribute]]) %>%
  summarize(
    total_samples = n(),
    resistant_samples = sum(.data[[antibiotic]] == "Resistant", na.rm = TRUE),
    resistance_percentage = (resistant_samples / total_samples) * 100,
    .groups = "drop"
  ) %>%
  mutate(!!cluster_attribute := "Global")

# Combine and clean
yearly_data_new <- rbind(yearly_data, global_data) %>%
  filter(!is.na(resistance_percentage))

data_decomp <- yearly_data_new[, c("resistance_percentage", time_attribute, cluster_attribute)]

# Determine countries with full data across years
country_data_points <- data_decomp %>%
  group_by(.data[[cluster_attribute]]) %>%
  summarize(DataPoints = n_distinct(.data[[time_attribute]]), .groups = "drop")

valid_countries <- country_data_points %>%
  filter(DataPoints == (end_year - start_year + 1)) %>%
  pull(.data[[cluster_attribute]])

data_decomp_final <- data_decomp %>%
  filter(.data[[cluster_attribute]] %in% valid_countries)

# Add trend
decomposed_data <- data_decomp_final %>%
  group_by(.data[[cluster_attribute]]) %>%
  arrange(.data[[time_attribute]]) %>%
  mutate(trend = moving_avg(resistance_percentage, n = 3)) %>%
  ungroup()

# Subset for specified time range
subset_data <- decomposed_data %>%
  filter(.data[[time_attribute]] %in% start_year:end_year) %>%
  mutate(seq_num = .data[[time_attribute]] - start_year)

# Factor setup
subset_data[[cluster_attribute]] <- as.factor(subset_data[[cluster_attribute]])

if (nrow(subset_data) == 0 || length(levels(subset_data[[cluster_attribute]])) == 0) {
  cat("No data available for this subset. Skipping.\n")
  quit("no", 0)
}

if ("Global" %in% levels(subset_data[[cluster_attribute]])) {
  subset_data[[cluster_attribute]] <- relevel(subset_data[[cluster_attribute]], ref = "Global")
  baseline_label <- "Global"
} else if (baseline_attribute %in% levels(subset_data[[cluster_attribute]])) {
  subset_data[[cluster_attribute]] <- relevel(subset_data[[cluster_attribute]], ref = baseline_attribute)
  baseline_label <- baseline_attribute
} else {
  fallback <- levels(subset_data[[cluster_attribute]])[1]
  subset_data[[cluster_attribute]] <- relevel(subset_data[[cluster_attribute]], ref = fallback)
  baseline_label <- fallback
}

# Skip check
if (nlevels(subset_data[[cluster_attribute]]) <= 2 ||
    all(subset_data$trend == subset_data$trend[1])) {
  warning("Insufficient variability or cluster levels. Skipping.")
  quit("no", 0)
}

# Linear model
lm_formula <- as.formula(paste("trend ~ seq_num * factor(", cluster_attribute, ")", sep=""))
model <- lm(lm_formula, data = subset_data)
model_summary <- summary(model)

# Robust SE
robust_se <- coeftest(model,
                      vcov = vcovHAC(model, type = "HC",
                                     cluster = cluster_attribute,
                                     group = decomposed_data[[cluster_attribute]]))

if (any(is.nan(coef(model)))) {
  warning("Model coefficients contain NaN. Skipping.")
  quit("no", 0)
}

# Extract coefficients
coefficients <- model_summary$coefficients
intercepts <- numeric()
slopes <- numeric()
names_vec <- character()

global_intercept <- coefficients["(Intercept)", "Estimate"]
global_slope     <- coefficients["seq_num", "Estimate"]

names_vec <- c(names_vec, baseline_label)
intercepts <- c(intercepts, global_intercept)
slopes     <- c(slopes, global_slope)

for (nm in rownames(coefficients)) {
  if (grepl(paste0("^factor\\(", cluster_attribute, "\\)"), nm) && !grepl("seq_num:factor", nm)) {
    country_name <- sub(paste0("^factor\\(", cluster_attribute, "\\)"), "", nm)
    country_name <- sub("^:", "", country_name)
    intercept <- coefficients[nm, "Estimate"]
    slope_name <- paste0("seq_num:", nm)
    slope <- if (slope_name %in% rownames(coefficients)) {
      coefficients[slope_name, "Estimate"]
    } else 0
    names_vec <- c(names_vec, country_name)
    intercepts <- c(intercepts, intercept)
    slopes     <- c(slopes, slope)
  }
}

# Save output
directory_path <- file.path("Time series data", organism, source_input, antibiotic)
if (!dir.exists(directory_path)) {
  dir.create(directory_path, recursive = TRUE)
  message(paste("Directory created:", directory_path))
}

result_df <- data.frame(Cluster = names_vec, intercept = intercepts, slope = slopes)
csv_path <- file.path(directory_path, paste0(organism, "_", antibiotic, "_", start_year, "_", end_year, ".csv"))
if (nrow(result_df) == 0) {
  cat("No valid results to save for:", csv_path, "\n")
} else {
  write.csv(result_df, csv_path, row.names = FALSE)
  cat("Saved coefficients to:", csv_path, "\n")
}