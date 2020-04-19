# Data Dictionary

### Transactions Table
This is a dataset from the UCI Machine Learning Repository which contains transactions from an online retail business.

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
This is a list of the world's countries by name along with their ISO currency code information and will be used as a static mapping table.

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
Need some text here to describe the date table...

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
This free API serves current and historical currency exchange rate data from the European Central Bank. We will keep a record of these rates in the S3 data lake.

- Source: https://ratesapi.io
- Name: `dim_fx_rate`
- Dist key: `date`
- Sort key: `date`

| Field Name          | Data Type       | Description                                       |
|---------------------|-----------------|---------------------------------------------------|
| `id (PK)`           | BIGINT          | Primary key                                       |
| `date`              | TIMESTAMP       | The date of the currency exchange                 |
| `hkd`               | VARCHAR         | The decimal currency exchange rate                |
| `(alpha codes...)`  | VARCHAR         | The decimal currency exchange rate                |
| `hkd`               | NUMERIC         | The decimal currency exchange rate                |
| `idr`               | NUMERIC         | The decimal currency exchange rate                |
| `php`               | NUMERIC         | The decimal currency exchange rate                |
| `lvl`               | NUMERIC         | The decimal currency exchange rate                |
| `inr`               | NUMERIC         | The decimal currency exchange rate                |
| `chf`               | NUMERIC         | The decimal currency exchange rate                |
| `mxn`               | NUMERIC         | The decimal currency exchange rate                |
| `sgd`               | NUMERIC         | The decimal currency exchange rate                |
| `czk`               | NUMERIC         | The decimal currency exchange rate                |
| `thb`               | NUMERIC         | The decimal currency exchange rate                |
| `bgn`               | NUMERIC         | The decimal currency exchange rate                |
| `eur`               | NUMERIC         | The decimal currency exchange rate                |
| `myr`               | NUMERIC         | The decimal currency exchange rate                |
| `nok`               | NUMERIC         | The decimal currency exchange rate                |
| `cny`               | NUMERIC         | The decimal currency exchange rate                |
| `hrk`               | NUMERIC         | The decimal currency exchange rate                |
| `pln`               | NUMERIC         | The decimal currency exchange rate                |
| `ltl`               | NUMERIC         | The decimal currency exchange rate                |
| `try`               | NUMERIC         | The decimal currency exchange rate                |
| `zar`               | NUMERIC         | The decimal currency exchange rate                |
| `cad`               | NUMERIC         | The decimal currency exchange rate                |
| `brl`               | NUMERIC         | The decimal currency exchange rate                |
| `ron`               | NUMERIC         | The decimal currency exchange rate                |
| `dkk`               | NUMERIC         | The decimal currency exchange rate                |
| `nzd`               | NUMERIC         | The decimal currency exchange rate                |
| `eek`               | NUMERIC         | The decimal currency exchange rate                |
| `jpy`               | NUMERIC         | The decimal currency exchange rate                |
| `rub`               | NUMERIC         | The decimal currency exchange rate                |
| `krw`               | NUMERIC         | The decimal currency exchange rate                |
| `usd`               | NUMERIC         | The decimal currency exchange rate                |
| `aud`               | NUMERIC         | The decimal currency exchange rate                |
| `huf`               | NUMERIC         | The decimal currency exchange rate                |
| `sek`               | NUMERIC         | The decimal currency exchange rate                |
| `extracted_at`      | TIMESTAMP       | The timestamp when the record was loaded          |
