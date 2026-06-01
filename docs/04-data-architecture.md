# Domain Model

## Product

- product_id
- product_name
- category

## Store

- store_id
- store_name
- region

## Sale

- sale_id
- product_id
- store_id
- date
- quantity

## Inventory

- inventory_id
- product_id
- current_stock

## Forecast

- forecast_id
- product_id
- forecast_date
- predicted_quantity

## Model

- model_id
- version
- metrics

## Experiment

- experiment_id
- parameters
- metrics
