- TODO: Add data dictionary
- TODO: Complete write-up
- TODO: Add docstrings
- TODO: Push to remote branch

# Udacity Data Engineering Nanodegree - Capstone Project

## Setup Instructions

### First Time Setup



```bash
# Set airflow home directory
export AIRFLOW_HOME=$(pwd)/airflow
```

```bash
# Install required python packages
pip install -r requirements.txt
```

```bash
# initialize the airflow database
airflow initdb
```

```bash
# start the web server on default port
airflow webserver -p 8080
```

```bash
# start the airflow scheduler
airflow scheduler
```


### Airflow Connections Setup
#### AWS Credentials
- Conn Id: `aws_credentials`
- Conn Type: `Amazon Web Services`
- Login: `<Your AWS Access key ID>`
- Password: `<Your AWS Secret access key>`

#### FX Rates API
- Conn Id: `fx_rates_api`
- Conn Type: `HTTP`
- Host: `https://api.ratesapi.io`

#### Redshift Credentials
- Conn Id: `redshift`
- Conn Type: `Postgres`
- Host: `<Your Redshift cluster endpoint>`
- Schema: `dev`
- Login: `<Your Redshift username>`
- Password: `<Your Redshift password>`
- Port: `5439`

### Airflow Variables Setup
#### s3_data_lake_bucket
- Key: `s3_data_lake_bucket`
- Value: `<Your S3 bucket name>`

#### s3_data_lake_region
- Key: `s3_data_lake_region`
- Value: `<Your S3 bucket region>`

## Project Scope and Data Gathering

In this project I wanted to simulate a real-world situation I often encounter in the workplace, where daily transactions needs to be enriched with data pulled from multiple sources to anable analysis. To simulate this situation, I have used the following datasets:

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

### FX Rates Tables
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


## Explore and Assess the Data

### No Currency Fields in Transactions table
To apply the correct exchange rate to a record in the Transactions table, we need 3 pieces of information:

#### Base Currency
From the information provided with the dataset, we know the online retailer only processes transactions in GBP currency, so we don't need to worry about deriving a base currency.

#### Exchange Currency
The exchange currency is a little trickier, this will need to be derived from the [country] column which states the country the goods were sold to. Luckily, the country names present in the transactions table can easily be mapped to existing ISO country code tables freely found online, so from the country name I can derive the currency.

Upon inspecting the ISO country code table I found that all of the country names in the [entity] column are UPPERCASE, while those in the transactions table are not. This is easily solved in the INSERT statement which loads the transaction records, I'll convert the country names to UPPERCASE at this point to match the country code table. 

#### Exchange Date
I initially thought this would be a simple matter of relating the exchange rate information to the transactions on [invoice_date] to retrieve the currect exchange rate. However, I soon discovered that exchange rate data is not available on weekends, if you call the API with a weekend date, it will return the exchange rate for the previous Friday.

I played around with the idea of using logic in the SQL to add an [fx_date] column which returns the previous Friday if the [invoice_date] falls on a weekend. This works, but introuduces issues with task dependendies; the previous Friday's run will have to complete before the weekend dates can be run.

To eliminate the dependency problem I decided to exclude the date from table join. The reasoning behind this is that each ETL operation is self-contained and isolated to a single invoice date, the exchange rate API will return the appropriate exchange rate for that date. Now that I don't need to rely on anything outside of the current run of the ETL process, I can have many operations running in parallel.

### Non-null values in "empty" cells
The transactions table is not clean and there are whitespace and other such non-null values in cells which should be null. To get around this, I will use the COPY OPTIONS parameter when copying the data from S3 to Redshift. This parameter lets you specify how non-null values will be handled, in this case they will be replaced will NULL when the data is copied.

### Long Decimal Values
The exchange rates returned by the API are long decimal numbers, I intially encountered a problem where these values were being truncated to fewer decimal places. To remedy this, I've declared the scale and precision of these NUMERIC columns in the table definition.


## Step 3: Define the Data Model
Map out the conceptual data model and explain why you chose that model
List the steps necessary to pipeline the data into the chosen data model
Include the data dictionary you did in project_03


## Run ETL to Model the Data
The ETL process has been designed to be modular and self-contained, ie a run on a particular date does not rely on the state of a run on another date. This is to ensure that I can have many ETL operations running in parallel, adding more workers as the size and complexity of my data grows.

Each `run` executes over a single date and is comprised of the following operations:

### Extract
1. The ratesapi.io API is called to retrieve the currency exchange rate data for the date of operation.
2. The currency exchange rate data is saved to the S3 data lake.
3. The country, currency and transaction data for the date of operation is copied from S3 to staging tables in Redshift.

### Ingest
The staged data is modelled into dimension and fact tables and loaded from the transient staging tables to permanent ones.

### Data Checks
Data quality checks are performed on the dimension and fact tables to ensure records are present. If no records exist in S3 for the date of operation, then the checks are skipped. To enable this, I've used Airflow's `xcom` feature to pass status variables between tasks in the operation.

### Cleanup
If the data checks pass, the staging tables are dropped and operation terminated.


## Project Summary

### Project Goal
The goal of this project is to sequentially read date-partitioned transactional data from a data store, enrich it with currency exchange rates and store the enriched records in a data warehouse. The resulting data warehouse schema will be modelled to enable end-users to analyse transactions over time in base and customer currency.

### Choice of Technologies
#### Airflow
Airflow was chosen because it allows you to create complex, interdependent data pipelines in a concise manner. This software includes pre-build hooks and operators which make working with other cloud-based services easy, additionally, its rich github community provides a wealth of solutions to common problems.

With the Airflow UI, it is easy to inspect the status of running jobs, or the code which triggered an error in a failed job along with its stack trace. Your data pipelines are represented visually in the Graph View of the UI; this view will update as you make changes to your code, essentially giving you a live view of the structure which is invaluable when composing tasks. 

#### AWS Redshift and S3
AWS Redshift and S3 were chosen due to the seamless data transfer between them, the excellent APIs which make working with these resources straightforward and how well Airflow integrates them. The pre-built AWS operators and hooks Airflow ships with made connecting to these services quick and straightforward, which allowed me to concentrate on building and iterating the ETL process right away.

### Update Frequency
The transactions data has been partitioned to suit the grain of the currency exchange rate data; a single date. This means that each Airflow job will only deal with data for a specific date and can operate independently, enabling parallel processing. As the data is partitioned to single days, I propose the update frequency matches this.

### Scaling Scenarios

Include a description of how you would approach the problem differently under the following scenarios:
    If the data was increased by 100x.
    If the pipelines were run on a daily basis by 7am.
    If the database needed to be accessed by 100+ people.

### Example Queries
What queries will you want to run?
