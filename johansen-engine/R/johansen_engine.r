# Librerías necesarias
library(Matrix)
library(vars)
library(tseries)
library(urca)
library(ggplot2)
library(readxl)
library(zoo)

# Función personalizada del test de Johansen

johansen_test_custom <- function(data, lag, model_type, alpha) {
  # `data`: Matriz de datos (series de tiempo).
  # `lag`: Número de rezagos.
  # `model_type`: Modelo seleccionado (1-5).
  # `alpha`: Nivel de significancia del error.
  
  # Tablas de valores críticos para traza (trace test)
  critical_values <- list(
    "5%" = list(
      "2" = c(15.41, 3.76),       
      "3" = c(29.68, 15.41, 3.76)
    ),
    "1%" = list(
      "2" = c(20.04, 6.65),       
      "3" = c(35.65, 20.04, 6.65) 
    )
  )
  
  # Valores críticos según alpha
  alpha_label <- paste0(100 * alpha, "%")
  n_vars <- ncol(data)
  
  if (!as.character(n_vars) %in% names(critical_values[[alpha_label]])) {
    stop("No hay valores críticos para este número de variables.")
  }
  
  crit_vals <- critical_values[[alpha_label]][[as.character(n_vars)]]
  
  # Diferencias y lags
  diff_data <- diff(data)
  lagged_data <- embed(diff(data), lag + 1)
  lagged_differences <- lagged_data[, -(1:n_vars)]
  Y <- lagged_data[, 1:n_vars]
  
  # X según el modelo
  if (model_type == 1) {
    X <- lagged_differences
  } else if (model_type == 2) {
    X <- cbind(1, lagged_differences)
  } else if (model_type == 3) {
    X <- cbind(1, lagged_differences, seq(1, nrow(lagged_differences)))
  } else if (model_type == 4) {
    X <- cbind(1, lagged_differences, seq(1, nrow(lagged_differences)))
  } else if (model_type == 5) {
    X <- cbind(1, lagged_differences, seq(1, nrow(lagged_differences)), seq(1, nrow(lagged_differences))^2)
  } else {
    stop("Modelo no válido. Seleccione entre 1 y 5.")
  }
  
  # Ajustar regresión
  Y_residuals <- lm(Y ~ X - 1)$residuals
  Z_residuals <- lm(lagged_data[, -(1:n_vars)] ~ X - 1)$residuals
  
  # Calcular matrices
  S11 <- crossprod(Y_residuals) / nrow(Y_residuals)
  S22 <- crossprod(Z_residuals) / nrow(Z_residuals)
  S12 <- crossprod(Y_residuals, Z_residuals) / nrow(Y_residuals)
  S21 <- t(S12)
  
  # Valores propios
  eigen_values <- eigen(solve(S22) %*% S21 %*% solve(S11) %*% S12)$values
  lambda <- sort(eigen_values, decreasing = TRUE)
  
  # Estadísticos
  trace_stat <- -nrow(data) * cumsum(log(1 - lambda))
  max_stat <- -nrow(data) * log(1 - lambda)
  
  # Comparación con valores críticos
  trace_results <- trace_stat > crit_vals
  max_results <- max_stat > crit_vals
  
  # Salida
  return(list(
    lambda = lambda,
    trace_stat = trace_stat,
    max_stat = max_stat,
    trace_results = trace_results,
    max_results = max_results,
    critical_values = crit_vals,
    model_type = model_type
  ))
}
