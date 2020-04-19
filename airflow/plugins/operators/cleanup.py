from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class DropTableOperator(BaseOperator):

    ui_color = '#076D9F'
    template_fields = ('tables', )

    @apply_defaults
    def __init__(self,
                 schema,
                 tables,
                 redshift_conn_id='redshift',
                 *args,
                 **kwargs):

        super(DropTableOperator, self).__init__(*args, **kwargs)
        self.schema = schema
        self.tables = tables
        self.redshift_conn_id = redshift_conn_id

    def execute(self, context):
        self.redshift_hook = PostgresHook(self.redshift_conn_id)

        for table in self.tables:
            self.log.info(f'Dropping table: {self.schema}.{table}')
            self.redshift_hook.run(
                f'DROP TABLE IF EXISTS {self.schema}.{table}'
            )
