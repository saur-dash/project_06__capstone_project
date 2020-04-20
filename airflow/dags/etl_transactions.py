from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.udacity_plugin import (
    DropTableOperator,
    ExtractOperator,
    FXRateOperator,
    HasRowsOperator,
    IngestOperator,
)

from helpers import CreateSQL, InsertSQL


default_args = {
    'owner': 'saur-dash__udacity_capstone_project',
    'start_date': datetime(2009, 12, 1),
    'end_date': datetime(2011, 12, 9),
    'depends_on_past': False,
    'catchup': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_retry': False,
}

dag_name = 'transactions_etl'

s3_data_source_bucket = 'udacity-saur-dash-capstone-project'
s3_data_source_region = 'us-west-2'

s3_data_lake_bucket = Variable.get('s3_data_lake_bucket')
s3_data_lake_region = Variable.get('s3_data_lake_region')

with DAG(dag_name,
         default_args=default_args,
         description='Extract data from S3 and load to Redshift with Airflow',
         schedule_interval='@daily',
         max_active_runs=3,
         ) as dag:

    start_operator = DummyOperator(task_id='execution_started')
    extract_completed = DummyOperator(task_id='extract_completed')
    ingest_completed = DummyOperator(task_id='ingest_completed')
    stop_operator = DummyOperator(task_id='execution_stopped')

    xcom_template = 'ti.xcom_pull(task_ids="{id}", key="return_value")'

    get_fx_rates = SimpleHttpOperator(
        task_id='get_fx_rates',
        method='GET',
        http_conn_id='fx_rates_api',
        endpoint='api/{{ ds }}?base=GBP',
        headers={'Content-Type': 'application/json'},
        xcom_push=True,
    )

    copy_fx_rates_to_s3 = FXRateOperator(
        task_id='copy_fx_rates',
        data=f"{{{{ {xcom_template.format(id='get_fx_rates')} }}}}",
        s3_bucket=s3_data_lake_bucket,
        s3_key='fx_rates/{{ execution_date.year }}/{{ ds }}__fx_rates.csv',
        file_date='{{ ds }}',
    )

    extract_country_data = ExtractOperator(
        task_id='extract_country_data',
        schema='public',
        table='staging_country__{{ ts_nodash }}',
        create_sql=CreateSQL.create_staging_country,
        s3_bucket=s3_data_source_bucket,
        s3_key='countries/country_currency.gz',
        s3_region=s3_data_source_region,
        copy_options=[
            'CSV',
            'IGNOREHEADER 1',
            "DELIMITER ','",
            'EMPTYASNULL',
            'BLANKSASNULL',
            'GZIP',
            'COMPUPDATE ON',
            ],
        xcom_push=True,
    )

    extract_fx_rate_data = ExtractOperator(
        task_id='extract_fx_rate_data',
        schema='public',
        table='staging_fx_rate__{{ ts_nodash }}',
        create_sql=CreateSQL.create_staging_fx_rate,
        s3_bucket=s3_data_lake_bucket,
        s3_key='fx_rates/{{ execution_date.year }}/{{ ds }}__fx_rates.csv',
        s3_region=s3_data_lake_region,
        copy_options=[
            'CSV',
            'IGNOREHEADER 1',
            "DELIMITER ','",
            'EMPTYASNULL',
            'BLANKSASNULL',
            'COMPUPDATE ON',
            ],
        xcom_push=True,
    )

    extract_transaction_data = ExtractOperator(
        task_id='extract_transaction_data',
        schema='public',
        table='staging_transaction__{{ ts_nodash }}',
        create_sql=CreateSQL.create_staging_transaction,
        s3_bucket=s3_data_source_bucket,
        s3_key=(
            'transactions/{{ execution_date.year }}/{{ ds }}__transactions.gz'
        ),
        s3_region=s3_data_source_region,
        copy_options=[
            'CSV',
            'IGNOREHEADER 1',
            "DELIMITER ','",
            'EMPTYASNULL',
            'BLANKSASNULL',
            'GZIP',
            'COMPUPDATE ON',
            ],
        xcom_push=True,
    )

    ingest_dim_country_table = IngestOperator(
        task_id='ingest_dim_country_table',
        schema='public',
        table='dim_country',
        create_sql=CreateSQL.create_dim_country,
        insert_sql=(
            InsertSQL.insert_dim_country.format(tstamp='{{ ts_nodash }}')
        ),
        has_rows=(
            f"{{{{ {xcom_template.format(id='extract_country_data')} }}}}"
        ),
        truncate=True,
    )

    ingest_dim_date_table = IngestOperator(
        task_id='ingest_dim_date_table',
        schema='public',
        table='dim_date',
        create_sql=CreateSQL.create_dim_date,
        insert_sql=(
            InsertSQL.insert_dim_date.format(tstamp='{{ ts_nodash }}')
        ),
        has_rows=(
            f"{{{{ {xcom_template.format(id='extract_transaction_data')} }}}}"
        ),
    )

    ingest_dim_fx_rate_table = IngestOperator(
        task_id='ingest_dim_fx_rate_table',
        schema='public',
        table='dim_fx_rate',
        create_sql=CreateSQL.create_dim_fx_rate,
        insert_sql=(
            InsertSQL.insert_dim_fx_rate.format(tstamp='{{ ts_nodash }}')
        ),
        has_rows=(
            f"{{{{ {xcom_template.format(id='extract_fx_rate_data')} }}}}"
        ),
    )

    ingest_fact_transaction_table = IngestOperator(
        task_id='ingest_fact_transaction_table',
        schema='public',
        table='fact_transaction',
        create_sql=CreateSQL.create_fact_transaction,
        insert_sql=(
            InsertSQL.insert_fact_transaction.format(tstamp='{{ ts_nodash }}')
        ),
        has_rows=(
            f"{{{{ {xcom_template.format(id='extract_transaction_data')} }}}}"
        ),
    )

    data_check_dim_country = HasRowsOperator(
        task_id='data_check_dim_country',
        schema='public',
        table='dim_country',
        date_filter='{{ ds }}',
        has_rows=(
            f"{{{{ {xcom_template.format(id='extract_country_data')} }}}}"
        ),
    )

    data_check_dim_date = HasRowsOperator(
        task_id='data_check_dim_date',
        schema='public',
        table='dim_date',
        date_filter='{{ ds }}',
        has_rows=(
            f"{{{{ {xcom_template.format(id='extract_transaction_data')} }}}}"
        ),
    )

    data_check_dim_fx_rate = HasRowsOperator(
        task_id='data_check_dim_fx_rate',
        schema='public',
        table='dim_fx_rate',
        date_filter='{{ ds }}',
        has_rows=(
            f"{{{{ {xcom_template.format(id='extract_fx_rate_data')} }}}}"
        ),
    )

    data_check_fact_transaction = HasRowsOperator(
        task_id='data_check_fact_transaction',
        schema='public',
        table='fact_transaction',
        date_filter='{{ ds }}',
        has_rows=(
            f"{{{{ {xcom_template.format(id='extract_transaction_data')} }}}}"
        ),
    )

    cleanup = DropTableOperator(
        task_id='drop_staging_tables',
        schema='public',
        tables=[
            'staging_country__{{ ts_nodash }}',
            'staging_fx_rate__{{ ts_nodash }}',
            'staging_transaction__{{ ts_nodash }}',
        ]
    )

extract_operations = [
    extract_country_data,
    extract_fx_rate_data,
    extract_transaction_data,
]

ingest_operations = [
    ingest_dim_country_table,
    ingest_dim_date_table,
    ingest_dim_fx_rate_table,
]

data_quality_checks = [
    data_check_dim_country,
    data_check_dim_date,
    data_check_dim_fx_rate,
    data_check_fact_transaction,
]

# DAG DEPENDENCIES
# call fx_rate api and save response to s3 data lake
start_operator >> get_fx_rates >> copy_fx_rates_to_s3

# extract raw data from s3 data lake
copy_fx_rates_to_s3 >> extract_operations >> extract_completed

# ingest data from staging to live tables
(extract_completed
    >> ingest_operations
    >> ingest_fact_transaction_table
    >> ingest_completed)

# run data quality checks
ingest_completed >> data_quality_checks

# drop staging tables and stop operation if data checks pass
data_quality_checks >> cleanup >> stop_operator
