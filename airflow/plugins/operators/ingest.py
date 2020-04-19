from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class IngestOperator(BaseOperator):

    ui_color = '#076D9F'
    template_fields = ('has_rows', 'insert_sql', )

    @apply_defaults
    def __init__(self,
                 schema,
                 table,
                 create_sql,
                 insert_sql,
                 has_rows,
                 truncate=False,
                 autocommit=True,
                 redshift_conn_id='redshift',
                 *args,
                 **kwargs):

        super(IngestOperator, self).__init__(*args, **kwargs)
        self.schema = schema
        self.table = table
        self.create_sql = create_sql
        self.insert_sql = insert_sql
        self.has_rows = has_rows
        self.truncate = truncate
        self.autocommit = autocommit
        self.redshift_conn_id = redshift_conn_id

    def execute(self, context):
        self.redshift_hook = PostgresHook(self.redshift_conn_id)

        self.redshift_hook.run(self.create_sql, self.autocommit)

        if self.has_rows == 'True':
            if self.truncate:
                self.log.info(f'Truncating table: {self.schema}.{self.table}')
                self.redshift_hook.run(
                    f'TRUNCATE TABLE {self.schema}.{self.table}',
                    self.autocommit,
                )

            self.log.info(
                f'Loading data to Redshift table: {self.schema}.{self.table}'
            )
            self.redshift_hook.run(self.insert_sql, self.autocommit)

        return self.has_rows
