library(vars)
library(tseries)
library(urca)
library(ggplot2)
library(readxl)
library(zoo)

#===========================
# Función de la Ley de Okun
#===========================

calculate_okun_coefficient <- function(unemployment, gdp_growth, potential_gdp_growth = 0.9) {
  if (length(unemployment) != length(gdp_growth)) {
    stop("Length mismatch: 'unemployment' and 'gdp_growth' must have the same length.")
  }
  
  gdp_deviation <- gdp_growth - potential_gdp_growth
  aligned_unemployment <- unemployment[-1]  # Remove the first value to match lengths
  aligned_gdp_deviation <- gdp_deviation[-1] # Remove the first value to match
  
  model <- lm(aligned_unemployment ~ aligned_gdp_deviation)
  return(list(
    model_summary = summary(model),
    okun_coefficient = coef(model)["aligned_gdp_deviation"]
  ))
}
