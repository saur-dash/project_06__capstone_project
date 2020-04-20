# Data Dictionary

### Transactions Table
- Source: http://archive.ics.uci.edu/ml/datasets/Online+Retail+II
- Name: `fact_transaction`
- Dist key: `date_id`
- Sort key: `date_id`

| Field Name          | Data Type       | Description                                       |
|---------------------|-----------------|---------------------------------------------------|
| `id (PK)`           | BIGINT          | Primary key                                       |
| `country_id (FK)`   | BIGINT          | Foreign key relating to dim_country               |
| `customer_id`       | VARCHAR         | Unique customer identifier                        |
| `date_id (FK)`      | BIGINT          | Foreign key relating to dim_date                  |
| `fx_rate_id (FK)`   | BIGINT          | Foreign key relating to dim_fx_rate               |
| `invoice_id`        | VARCHAR         | Identifier relating items in an order             |
| `invoice_date`      | TIMESTAMP       | The creation date of the record                   |
| `stock_code`        | VARCHAR         | Identifier for items on sale                      |
| `description`       | VARCHAR         | Item description                                  |
| `quantity`          | INT             | Number of items ordered                           |
| `price`             | NUMERIC         | Item price per unit                               |
| `extracted_at`      | TIMESTAMP       | The timestamp when the record was loaded          |

### Countries Table
- Source: https://www.currency-iso.org
- Name: `dim_country`
- Dist style: `ALL`
- Sort key: `entity`

| Field Name          | Data Type       | Description                                       |
|---------------------|-----------------|---------------------------------------------------|
| `id (PK)`           | BIGINT          | Primary key                                       |
| `entity`            | VARCHAR         | The ISO name of the country                       |
| `currency`          | VARCHAR         | The ISO name of the currency                      |
| `alpha_code`        | VARCHAR         | The 3-character alpha currency code (eg: "GBP")   |
| `numeric_code`      | SMALLINT        | The 3-character numeric currency code (eg: 826)   |
| `minor_unit`        | SMALLINT        | The currency exponent                             |
| `extracted_at`      | TIMESTAMP       | The timestamp when the record was loaded          |

### Date Table
- Source: http://archive.ics.uci.edu/ml/datasets/Online+Retail+II
- Name: `dim_date`
- Dist key: `date_time`
- Sort key: `date_time`

| Field Name          | Data Type       | Description                                       |
|---------------------|-----------------|---------------------------------------------------|
| `id (PK)`           | BIGINT          | Primary key                                       |
| `date_time`         | TIMESTAMP       | Date in YYYY-MM-DD HH:MM:SS format                |
| `date`              | DATE            | Date in YYYY-MM-DD format                         |
| `hour`              | SMALLINT        | Numeric hour of the day                           |
| `day`               | SMALLINT        | Numeric day of the month                          |
| `week`              | SMALLINT        | Numeric week of the year                          |
| `month`             | SMALLINT        | Numeric month of the year                         |
| `year`              | SMALLINT        | Numeric year in YYYY format                       |
| `week_day`          | SMALLINT        | Numeric day of the week                           |
| `extracted_at`      | TIMESTAMP       | The timestamp when the record was loaded          |

### FX Rates Table
- Source: https://ratesapi.io
- Name: `dim_fx_rate`
- Dist key: `date`
- Sort key: `date`

| Field Name          | Data Type       | Description                                       |
|---------------------|-----------------|---------------------------------------------------|
| `id (PK)`           | BIGINT          | Primary key                                       |
| `exchange`          | TIMESTAMP       | The exchange currency                             |
| `base`              | NUMERIC         | The base currency                                 |
| `rates`             | NUMERIC         | The decimal currency exchange rate                |
| `date`              | NUMERIC         | The date of the currency exchange                 |
| `file_date`         | NUMERIC         | The The date passed to the fx rate API            |
| `extracted_at`      | TIMESTAMP       | The timestamp when the record was loaded          |
