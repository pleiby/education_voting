# Process education data from text file to CSV
# Extracts state education rankings and attainment percentages

library(stringr)
library(dplyr)
library(readr)

# Regex patterns for data extraction (separated from code)
PATTERN_STATE_ENTRY <- "^(\\d+)\\.\\s+(?:\\(tie\\)\\s+)?(.+?)$"
PATTERN_BACHELORS <- "Share of adults 25\\+ with a bachelor's degree or higher:\\s*(\\d+\\.?\\d*)%"

# Multiple patterns for graduate/professional degrees
PATTERNS_GRAD_PROF <- c(
  "(\\d+\\.?\\d*)%\\s+of adults.*?graduate or professional degree",
  "graduate or professional degree.*?(\\d+\\.?\\d*)%",
  "at (\\d+\\.?\\d*)%.*?graduate",
  "graduate.*?degree.*?at (\\d+\\.?\\d*)%"
)

# Validation constants
MAX_REASONABLE_GRAD_SHARE <- 40


extract_comments_from_source <- function(input_file) {
  #' Extract all lines starting with # from the source file
  #' @param input_file Path to source file
  #' @return Vector of comment lines

  content <- readLines(input_file, warn = FALSE)
  comments <- content[str_starts(content, "#")]
  return(comments)
}


parse_state_data <- function(lines) {
  #' Parse state education data from text lines
  #' @param lines Vector of text lines
  #' @return List of vectors containing parsed data

  state_names <- c()
  education_ranks <- c()
  bachelors_shares <- c()
  grad_prof_shares <- c()

  current_state <- NULL
  current_rank <- NULL
  current_bachelors <- NULL
  current_grad_prof <- NULL

  for (i in seq_along(lines)) {
    line <- trimws(lines[i])

    # Check if this line starts a new state entry
    rank_match <- str_match(line, PATTERN_STATE_ENTRY)

    if (!is.na(rank_match[1])) {
      # Save previous state data if complete
      if (!is.null(current_state) && !is.null(current_rank) && !is.null(current_bachelors)) {
        state_names <- c(state_names, current_state)
        education_ranks <- c(education_ranks, current_rank)
        bachelors_shares <- c(bachelors_shares, current_bachelors)
        grad_prof_shares <- c(grad_prof_shares, ifelse(is.null(current_grad_prof), NA_real_, current_grad_prof))
      }

      # Start new state
      current_rank <- as.integer(rank_match[2])
      current_state <- trimws(rank_match[3])
      current_bachelors <- NULL
      current_grad_prof <- NULL
      next
    }

    # Look for bachelor's degree percentage
    bachelors_match <- str_match(line, PATTERN_BACHELORS)
    if (!is.na(bachelors_match[1])) {
      current_bachelors <- as.numeric(bachelors_match[2])
    }

    # Look for graduate/professional degree percentage
    if (is.null(current_grad_prof)) {
      for (pattern in PATTERNS_GRAD_PROF) {
        grad_match <- str_match(line, regex(pattern, ignore_case = TRUE))

        if (!is.na(grad_match[1])) {
          potential_value <- as.numeric(grad_match[2])
          # Sanity check
          if (potential_value < MAX_REASONABLE_GRAD_SHARE) {
            current_grad_prof <- potential_value
            break
          }
        }
      }
    }
  }

  # Don't forget the last state
  if (!is.null(current_state) && !is.null(current_rank) && !is.null(current_bachelors)) {
    state_names <- c(state_names, current_state)
    education_ranks <- c(education_ranks, current_rank)
    bachelors_shares <- c(bachelors_shares, current_bachelors)
    grad_prof_shares <- c(grad_prof_shares, ifelse(is.null(current_grad_prof), NA_real_, current_grad_prof))
  }

  return(list(
    state_names = state_names,
    education_ranks = education_ranks,
    bachelors_shares = bachelors_shares,
    grad_prof_shares = grad_prof_shares
  ))
}


parse_education_data <- function(input_file, output_file) {
  #' Parse education data from text file and save to CSV
  #'
  #' @param input_file Path to the source text file (expects # comment lines at top)
  #' @param output_file Path to save the output CSV
  #' @return A data frame with the parsed education data

  # Extract comments from source file
  source_comments <- extract_comments_from_source(input_file)

  # Read the content
  content <- readLines(input_file, warn = FALSE)

  # Parse the data
  parsed <- parse_state_data(content)

  # Create data frame
  df <- data.frame(
    StateName = parsed$state_names,
    EducationRank = parsed$education_ranks,
    BachelorsDegreeShare = parsed$bachelors_shares,
    GraduateProfessionalDegreeShare = parsed$grad_prof_shares,
    stringsAsFactors = FALSE
  )

  # IMPORTANT: Recalculate ranks based on bachelor's degree share
  # The original file had markdown auto-numbering issues (many states marked as "1.")
  # So we derive the true rank from the data: highest % = rank 1, lowest % = rank 50
  df <- df %>%
    arrange(desc(BachelorsDegreeShare)) %>%
    mutate(EducationRank = row_number()) %>%
    select(StateName, EducationRank, BachelorsDegreeShare, GraduateProfessionalDegreeShare)

  # Save to CSV with metadata comments at the top
  con <- file(output_file, open = "w")

  # Write source comments from input file
  for (comment in source_comments) {
    writeLines(comment, con)
  }

  # Add processing metadata
  writeLines(c(
    "#",
    paste0("# Processed: ", Sys.Date()),
    "# EducationRank: 1 = most educated (highest bachelor's+ %), 50 = least educated",
    "# Note: Ranks recalculated from BachelorsDegreeShare due to markdown numbering issues",
    "#"
  ), con)

  close(con)

  # Append the CSV data (with header)
  write_csv(df, output_file, append = TRUE, col_names = TRUE)

  # Print summary statistics
  cat(sprintf("Processed %d states\n", nrow(df)))
  cat(sprintf("\nData saved to: %s\n", output_file))
  cat("\nTo read this CSV (with comments):\n")
  cat(sprintf("  Python: pd.read_csv('%s', comment='#')\n", output_file))
  cat(sprintf("  R: read_csv('%s', comment = '#')\n", output_file))
  cat("\nFirst 10 rows:\n")
  print(head(df, 10))
  cat(sprintf("\nMissing graduate/professional degree data for %d states\n",
              sum(is.na(df$GraduateProfessionalDegreeShare))))

  return(df)
}


# Main execution
script_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
if (length(script_arg) > 0) {
  script_path <- normalizePath(sub("^--file=", "", script_arg[1]))
  script_dir <- dirname(script_path)
} else {
  script_dir <- getwd()
}
project_dir <- normalizePath(file.path(script_dir, ".."))
input_file <- file.path(project_dir, "data", "most_and_least_educated_US-states.txt")
output_file <- file.path(project_dir, "data", "education_data_r.csv")

df <- parse_education_data(input_file, output_file)

# Data frame is now available for further analysis
# Next step: merge with 2024 election data for correlation analysis
