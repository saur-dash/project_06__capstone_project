import json
import pandas as pd

from airflow.hooks.S3_hook import S3Hook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class FXRateOperator(BaseOperator):

    ui_color = '#358140'
    template_fields = ('data', 's3_key', 'file_date', )

    @apply_defaults
    def __init__(self,
                 data,
                 s3_bucket,
                 s3_key,
                 file_date,
                 *args,
                 **kwargs):

        super(FXRateOperator, self).__init__(*args, **kwargs)
        self.data = data
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.s3_hook = S3Hook('aws_credentials')
        self.file_date = file_date

    def execute(self, context):
        data = json.loads(self.data)
        s3_key = f's3://{self.s3_bucket}/{self.s3_key.format(**context)}'
        self.log.info(f'Data retrieved: {data}')
        self.log.info(f'Copying to S3 key: {s3_key}')

        df = pd.DataFrame(data)
        df.index.rename('exchange', inplace=True)
        df.insert(len(df.columns), 'file_date', self.file_date)

        data = df.to_csv(
            index=True,
            header=True,
            sep=',',
            encoding='utf-8’',
        )

        self.s3_hook.load_string(data,
                                 s3_key,
                                 replace=True,
                                 encrypt=False,
                                 encoding='utf-8')
