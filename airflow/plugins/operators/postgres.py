from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class HasRowsOperator(BaseOperator):

    ui_color = '#358140'

    @apply_defaults
    def __init__(self,
                 schema,
                 table,
                 date_filter,
                 has_rows,
                 redshift_conn_id='redshift',
                 *args,
                 **kwargs):

        super(HasRowsOperator, self).__init__(*args, **kwargs)
        self.schema = schema
        self.table = table
        self.filter = date_filter
        self.has_rows = has_rows
        self.redshift_conn_id = redshift_conn_id

    def execute(self, context):
        redshift_hook = PostgresHook(self.redshift_conn_id)

        if self.has_rows == 'True':
            self.log.info(
                f'Checking table {self.schema}.{self.table} data quality'
            )

            records = redshift_hook.get_records(
                f"""
                SELECT COUNT(*) FROM {self.schema}.{self.table}
                WHERE extracted_at = '{self.date_filter}';
                """
            )
            num_records = records[0][0]

            if len(records) < 1 or len(records[0]) < 1:
                raise ValueError(
                    f'Data quality check failed: '
                    f'{self.schema}.{self.table} returned no results'
                )

            if num_records < 1:
                raise ValueError(
                    f'Data quality check failed: '
                    f'{self.schema}.{self.table} contained {num_records} rows'
                )

            self.log.info(
                f'Data quality check passed: '
                f'{self.schema}.{self.table} contained {num_records} records'
            )
        else:
            self.log.info('Source has no records, skipping data checks')

        return self.has_rows


class LoadTableOperator(BaseOperator):

    ui_color = '#076D9F'
    template_fields = ('sql', )

    @apply_defaults
    def __init__(self,
                 schema,
                 table,
                 sql,
                 truncate=False,
                 redshift_conn_id='redshift',
                 *args,
                 **kwargs):

        super(LoadTableOperator, self).__init__(*args, **kwargs)
        self.schema = schema
        self.table = table
        self.sql = sql
        self.truncate = truncate
        self.redshift_conn_id = redshift_conn_id

    def execute(self, context):
        redshift_hook = PostgresHook(self.redshift_conn_id)
        formatted_sql = self.sql.format(schema=self.schema, table=self.table)

        if self.truncate:
            self.log.info(
                'Truncating Redshift table: {self.schema}.{self.table}'
            )
            redshift_hook.run(f'TRUNCATE TABLE {self.schema}.{self.table}')

        self.log.info(
            f'Copying data to Redshift table {self.schema}.{self.table}'
        )
        redshift_hook.run(formatted_sql)
