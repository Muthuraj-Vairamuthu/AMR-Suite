# 📥 Command line arguments
args <- commandArgs(trailingOnly = TRUE)

input_path <- args[1]
output_prefix <- args[2]  # without extension
n_total <- as.numeric(args[3])
anonymize <- as.logical(args[4])
generate_plots <- as.logical(args[5])

output_csv <- paste0(output_prefix, ".csv")
output_pdf <- paste0(output_prefix, ".pdf")

library(dplyr)
library(tidyr)
library(stringi)
library(ggplot2)
library(purrr)

# 🧬 Load Data
original_data <- read.csv(input_path)

if (anonymize) {
  study_map <- setNames(LETTERS[1:length(unique(original_data$Study))], unique(original_data$Study))
  original_data$Study <- study_map[original_data$Study]

  country_map <- setNames(paste0("Z", seq_along(unique(original_data$Country))), unique(original_data$Country))
  original_data$Country <- country_map[original_data$Country]

  state_map <- setNames(paste0("Y", seq_along(unique(original_data$State))), unique(original_data$State))
  original_data$State <- state_map[original_data$State]
}

# 🎯 Proportional Allocation
group_counts <- original_data %>%
  count(Country, Year) %>%
  mutate(prop = n / sum(n)) %>%
  mutate(n_synthetic = round(prop * n_total))

meta_columns <- c("Isolate.Id", "Study", "Species", "Family", "Country", "State", "Gender", "Age.Group", "Speciality", "Year")
interpretation_columns <- grep("_I$", colnames(original_data), value = TRUE)
categorical_cols <- names(which(sapply(original_data, function(x) is.character(x) || is.factor(x))))
numeric_cols <- setdiff(names(which(sapply(original_data, is.numeric))), "Year")

generate_synthetic_group <- function(df, n_samples = 20) {
  synthetic_cols <- list()
  for (col in names(df)) {
    if (col %in% meta_columns) {
      synthetic_cols[[col]] <- rep(df[[col]][1], n_samples)
    } else if (col %in% numeric_cols) {
      mean_val <- mean(df[[col]], na.rm = TRUE)
      sd_val <- sd(df[[col]], na.rm = TRUE)
      if (is.na(sd_val) || sd_val == 0) sd_val <- 1
      synthetic_cols[[col]] <- rnorm(n_samples, mean_val, sd_val)
    } else if (col %in% categorical_cols) {
      freqs <- table(df[[col]])
      synthetic_cols[[col]] <- sample(names(freqs), n_samples, replace = TRUE, prob = freqs)
    } else {
      synthetic_cols[[col]] <- rep(NA, n_samples)
    }
  }
  as.data.frame(synthetic_cols)
}

synthetic_list <- list()
for (i in 1:nrow(group_counts)) {
  group_data <- original_data %>% filter(Country == group_counts$Country[i], Year == group_counts$Year[i])
  n_to_sample <- group_counts$n_synthetic[i]
  if (nrow(group_data) > 0 && n_to_sample > 0) {
    synthetic_list[[length(synthetic_list) + 1]] <- generate_synthetic_group(group_data, n_to_sample)
  }
}
synthetic_data <- bind_rows(synthetic_list)
write.csv(synthetic_data, output_csv, row.names = FALSE)

# 📊 Plots
if (generate_plots) {
  # Create output folder if it doesn't exist
  output_dir <- dirname(output_prefix)
  dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

  # --- Open PDF device
  pdf(output_pdf, height = 12, width = 8)

  # Plot 1: Species Distribution
  p1 <- ggplot(synthetic_data, aes(x = Species)) +
    geom_bar(fill = "steelblue") +
    coord_flip() + theme_minimal() +
    labs(title = "Species Distribution", x = "Species", y = "Count")
  print(p1)

  # Also save as PNG
  ggsave(filename = file.path(output_dir, "species_distribution.png"),
         plot = p1, width = 8, height = 6, dpi = 150)

  # Plot 2: S/I/R Distribution
  resistance_columns <- grep("_I$", colnames(synthetic_data), value = TRUE)

  if (length(resistance_columns) > 0) {
    synthetic_long <- synthetic_data %>%
      select(Species, all_of(resistance_columns)) %>%
      pivot_longer(cols = -Species, names_to = "Antibiotic", values_to = "Response") %>%
      filter(Response %in% c("Susceptible", "Intermediate", "Resistant"))

    synthetic_long$Response <- recode(synthetic_long$Response,
                                      "Susceptible" = "S",
                                      "Intermediate" = "I",
                                      "Resistant" = "R")

    proportions_data <- synthetic_long %>%
      group_by(Species, Response) %>%
      summarise(count = n(), .groups = 'drop') %>%
      group_by(Species) %>%
      mutate(proportion = count / sum(count)) %>%
      ungroup()

    p2 <- ggplot(proportions_data, aes(x = Species, y = proportion, fill = Response)) +
      geom_bar(stat = "identity", position = "fill") +
      coord_flip() + theme_minimal() +
      scale_fill_manual(values = c("S" = "seagreen", "I" = "gold", "R" = "firebrick")) +
      labs(title = "Aggregated S/I/R per Species", x = "Species", y = "Proportion", fill = "Response")
    
    print(p2)

    # Also save as PNG
    ggsave(filename = file.path(output_dir, "sir_distribution.png"),
           plot = p2, width = 8, height = 6, dpi = 150)
  }

  dev.off()
}