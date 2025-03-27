args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 8) {
  stop("Usage: Rscript cluster_model_final.R ",
       "<organism> <antibiotic> <source> <start_year> <end_year> ",
       "<dataset_path> <cluster_attribute> <time_attribute>")
}

organism          <- args[1]  # e.g., "Escherichia coli"
antibiotic        <- args[2]  # e.g., "Amikacin_I"
source_input      <- args[3]  # e.g., "Urine"
start_year        <- as.integer(args[4]) # e.g., 2014
end_year          <- as.integer(args[5]) # e.g., 2022
dataset_path      <- args[6]  # e.g., "../CSV_Files/Data_part1.csv"
cluster_attribute <- args[7]  # e.g., "MyLocationCol"
time_attribute    <- args[8]  # e.g., "SampleYear"

cat(organism, antibiotic, source_input, start_year, end_year, dataset_path, cluster_attribute, time_attribute, "\n")

library(dplyr)
library(lubridate)
library(lmtest)
library(sandwich)
library(stats)
library(zoo)
set.seed(123)

antibiotic_data <- read.csv(dataset_path)


# Function to calculate moving average
moving_avg <- function(x, n) {
  rollmean(x, k = n, fill = "extend", align = "center")
}

# Function to read and preprocess dataset 
read_and_filter_data <- function(organism, antibiotic_data, source) {

  df <- antibiotic_data %>% 
    mutate(gender = tools::toTitleCase(Gender),
           country = tools::toTitleCase(Country))
  
  df <- df %>% filter(Species == organism)
  df <- df %>% filter(Source == source)
  df <- df %>% filter(Year >= start_year & Year <= end_year)
  return(df)
}

cat("Antibiotic:", antibiotic, "\n")
df <- read_and_filter_data(organism, antibiotic_data, source_input)
subset_data <- df[, c(time_attribute, cluster_attribute, antibiotic)]

# Calculate the resistance percentage for each country, each year
yearly_data <- df %>%
  filter(.data[[antibiotic]] %in% c("Resistant", "Intermediate", "Susceptible")) %>%
  group_by(.data[[cluster_attribute]], .data[[time_attribute]]) %>%
  summarize(
    total_samples = n(),
    resistant_samples = sum(.data[[antibiotic]] == "Resistant", na.rm = TRUE),
    resistance_percentage = (resistant_samples / total_samples) * 100,
    .groups = "drop"
  )

# Calculate global-level data
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

yearly_data_new <- rbind(yearly_data, global_data)

yearly_data_new <- yearly_data_new %>% filter(!is.na(resistance_percentage))

cat("Unique clusters:", unique(yearly_data_new[[cluster_attribute]]), "\n")

data_decomp <- yearly_data_new[, c("resistance_percentage", time_attribute, cluster_attribute)]

# Identify start and end year and calculate the total number of data points
start_year <- min(data_decomp$Year)
end_year <- max(data_decomp$Year)
total_years <- end_year - start_year + 1


# Count the number of data points (years) for each country
country_data_points <- data_decomp %>%
  group_by(.data[[cluster_attribute]]) %>%
  summarize(DataPoints = n_distinct(.data[[time_attribute]]), .groups = "drop")

valid_countries <- country_data_points %>%
  filter(DataPoints == total_years) %>%
  pull(.data[[cluster_attribute]])

data_decomp_final <- data_decomp %>%
  filter(.data[[cluster_attribute]] %in% valid_countries)

decomposed_data <- data_decomp_final %>%
  group_by(.data[[cluster_attribute]]) %>%
  arrange(.data[[time_attribute]]) %>%
  mutate(trend = moving_avg(resistance_percentage, n = 3)) %>%
  ungroup()


# Number of years in each subset
subset_years <- 4

# Create a list to store the models
models <- list()

for (start in seq(start_year, end_year - subset_years + 1)) {
  # Define the subset range
  subset_range <- start:(start + subset_years - 1)

  # Subset the data using the dynamic time column
  subset_data <- decomposed_data %>%
    filter(.data[[time_attribute]] %in% subset_range)

  # Calculate the sequence number using the dynamic time column
  subset_data <- subset_data %>%
    mutate(seq_num = .data[[time_attribute]] - start - 1)

  # Ensure seq_num is an integer
  subset_data$seq_num <- as.integer(subset_data$seq_num)

  # Convert the dynamic cluster column to a factor
  subset_data[[cluster_attribute]] <- as.factor(subset_data[[cluster_attribute]])

  # If "Global" is present among the factor levels, make it the reference level
  if ("Global" %in% levels(subset_data[[cluster_attribute]])) {
    subset_data[[cluster_attribute]] <- relevel(subset_data[[cluster_attribute]], ref = "Global")
  }
  cat("Unique clusters:", unique(subset_data[[cluster_attribute]]), "\n")
  cat("Unique seq_num values:", unique(subset_data$seq_num), "\n")
  cat("Levels of cluster factor:", levels(as.factor(subset_data[[cluster_attribute]])), "\n")
  cat("Number of cluster levels:", nlevels(as.factor(subset_data[[cluster_attribute]])), "\n")
  print(subset_data)

  # Determine the number of levels using the dynamic cluster column
  cluster_levels <- nlevels(as.factor(subset_data[[cluster_attribute]]))
  if (cluster_levels <= 2) {
    warning("Very small subset. Skipping subset.")
    next
  }

  if (all(subset_data$trend == subset_data$trend[1])) {
    warning("trend has no variability. Skipping subset.")
    next
  }

  # Build the linear model formula dynamically:
  lm_formula <- as.formula(paste("trend ~ seq_num * factor(", cluster_attribute, ")", sep=""))

  # Fit the linear model using the dynamic formula
  model <- lm(lm_formula, data = subset_data)
  model_summary <- summary(model)
  cat("Linear model fitted\n")
  print(model_summary)

  # Calculate total number of parameters using dynamic cluster levels
  num_predictors <- nlevels(as.factor(subset_data[[cluster_attribute]])) + 1
  num_interactions <- nlevels(as.factor(subset_data[[cluster_attribute]]))
  total_parameters <- num_predictors + num_interactions

  if (nrow(subset_data) <= total_parameters) {
    warning(sprintf("Skipping subset: %d rows and %d parameters.", nrow(subset_data), total_parameters))
    next
  }

  # Compute robust standard errors dynamically.
  # Note: We pass the dynamic cluster_attribute name to the vcov function.
  robust_se <- coeftest(model, 
                        vcov = vcovHAC(model, type = "HC", 
                                      cluster = cluster_attribute, 
                                      group = decomposed_data[[cluster_attribute]]))

  if (any(is.nan(coef(model)))) {
    warning("Model coefficients contain NaN. Skipping this subset.")
    next
  }

  cat("Robust SE fitted\n")
  print(robust_se)

  # Store the model in the list with a name like "2014-2017"
  models[[paste(start, start + subset_years - 1, sep = "-")]] <- model

  # Build a filename dynamically
  filename <- paste(organism, antibiotic, start, start + subset_years - 1, sep = "_")
  model_summary <- summary(model)
  cat(paste(start, start + subset_years - 1), "\n")
  cat("Debug 2\n")
  print(model_summary)

  # Extract coefficients from the model summary dynamically
  coefficients <- model_summary$coefficients

  # Initialize vectors for intercepts, slopes, and names (clusters)
  intercepts <- numeric()
  slopes <- numeric()
  names_vec <- character()

  # Extract the global (reference) intercept and slope
  global_intercept <- coefficients["(Intercept)", "Estimate"]
  global_slope     <- coefficients["seq_num", "Estimate"]

  names_vec <- c(names_vec, "Global")
  intercepts <- c(intercepts, global_intercept)
  slopes     <- c(slopes, global_slope)

  # Extract cluster-specific adjustments dynamically
  for (nm in rownames(coefficients)) {
    # Look for rows corresponding to cluster factors; e.g., "factor(Country)XYZ"
    if (grepl(paste0("^factor\\(", cluster_attribute, "\\)"), nm) && !grepl("seq_num:factor", nm)) {
      # Remove the prefix to obtain the cluster name
      country_name <- sub(paste0("^factor\\(", cluster_attribute, "\\)"), "", nm)
      country_name <- sub("^:", "", country_name)
      names_vec <- c(names_vec, country_name)
      intercept <- coefficients[nm, "Estimate"]
      slope_name <- paste0("seq_num:", nm)
      slope <- if (slope_name %in% rownames(coefficients)) {
        coefficients[slope_name, "Estimate"]
      } else 0
      intercepts <- c(intercepts, intercept)
      slopes     <- c(slopes, slope)
    }
  }

  # Create a dynamic output directory path
  directory_path <- file.path("Time series data", organism, source_input, antibiotic)
  if (!dir.exists(directory_path)) {
    dir.create(directory_path, recursive = TRUE)
    message(paste("Directory created:", directory_path))
  } else {
    message(paste("Directory already exists:", directory_path))
  }

  # Create a data frame with dynamic column name for clusters
  result_df <- data.frame(Cluster = names_vec, intercept = intercepts, slope = slopes)

  # Save the result to a CSV file
  csv_path <- file.path(directory_path, paste0(filename, ".csv"))
  write.csv(result_df, csv_path, row.names = FALSE)
  cat("Saved coefficients to:", csv_path, "\n")
}