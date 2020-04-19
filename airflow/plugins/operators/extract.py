from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.S3_hook import S3Hook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class ExtractOperator(BaseOperator):

    ui_color = '#358140'
    template_fields = ('s3_key', 'table', )

    @apply_defaults
    def __init__(self,
                 schema,
                 table,
                 create_sql,
                 s3_bucket,
                 s3_key,
                 s3_region,
                 copy_options,
                 autocommit=True,
                 redshift_conn_id='redshift',
                 aws_conn_id='aws_credentials',
                 *args,
                 **kwargs):

        super(ExtractOperator, self).__init__(*args, **kwargs)
        self.schema = schema
        self.table = table
        self.create_sql = create_sql
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.s3_region = s3_region
        self.redshift_conn_id = redshift_conn_id
        self.aws_conn_id = aws_conn_id
        self.copy_options = copy_options
        self.autocommit = autocommit

    def execute(self, context):
        self.aws_hook = AwsHook(self.aws_conn_id)
        self.redshift_hook = PostgresHook(self.redshift_conn_id)
        self.s3_hook = S3Hook(self.aws_conn_id)

        credentials = self.aws_hook.get_credentials()
        s3_key = f's3://{self.s3_bucket}/{self.s3_key.format(**context)}'
        copy_options = '\n\t\t\t'.join(self.copy_options)

        create_sql = self.create_sql.format(
            schema=self.schema,
            table=self.table
        )
        copy_sql = (
            """
            COPY {schema}.{table}
            FROM '{s3_key}'
            REGION '{s3_region}'
            ACCESS_KEY_ID '{access_key_id}'
            SECRET_ACCESS_KEY '{secret_access_key}'
            {copy_options};
            """
        ).format(
            schema=self.schema,
            table=self.table,
            s3_bucket=self.s3_bucket,
            s3_key=s3_key,
            s3_region=self.s3_region,
            access_key_id=credentials.access_key,
            secret_access_key=credentials.secret_key,
            copy_options=copy_options,
        )

        if self.s3_hook.check_for_key(key=s3_key):
            self.has_rows = True
            self.log.info(f'Creating table: {self.schema}.{self.table}')
            self.redshift_hook.run(create_sql, self.autocommit)

            self.log.info(f'Copying data from {s3_key} to Redshift')
            self.redshift_hook.run(copy_sql, self.autocommit)
            self.log.info("COPY command complete...")
        else:
            self.has_rows = False
            self.log.info(f'S3 key: {s3_key} does not exist')

        return self.has_rows
