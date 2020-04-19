from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.S3_hook import S3Hook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class StageToRedshiftOperator(BaseOperator):

    ui_color = '#358140'
    template_fields = ('s3_key', )

    @apply_defaults
    def __init__(self,
                 schema,
                 table,
                 s3_bucket,
                 s3_key,
                 s3_region,
                 copy_options,
                 autocommit=True,
                 redshift_conn_id='redshift',
                 aws_conn_id='aws_credentials',
                 *args,
                 **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.table = table
        self.schema = schema
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.s3_region = s3_region
        self.redshift_conn_id = redshift_conn_id
        self.aws_conn_id = aws_conn_id
        self.copy_options = copy_options
        self.autocommit = autocommit

    def execute(self, context):
        self.aws_hook = AwsHook('aws_credentials')
        self.redshift_hook = PostgresHook('redshift')
        self.s3_hook = S3Hook('aws_credentials')
        credentials = self.aws_hook.get_credentials()
        s3_key = f's3://{self.s3_bucket}/{self.s3_key.format(**context)}'
        copy_options = '\n\t\t\t'.join(self.copy_options)

        copy_query = (
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

        self.log.info(
            f'Truncating Redshift table: {self.schema}.{self.table}'
        )
        self.redshift_hook.run(
            f'TRUNCATE TABLE {self.schema}.{self.table}'
        )
        self.log.info("TRUNCATE command complete...")

        if self.s3_hook.check_for_key(key=s3_key):
            self.log.info(
                f'Copying data from {s3_key} to {self.schema}.{self.table}'
            )
            self.redshift_hook.run(copy_query, self.autocommit)
            self.has_rows = True
            self.log.info("COPY command complete...")
        else:
            self.has_rows = False
            self.log.info(f'S3 key: {s3_key} does not exist')

        return self.has_rows
