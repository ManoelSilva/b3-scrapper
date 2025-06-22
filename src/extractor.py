from datetime import datetime, timezone
import io
import os
import json

import boto3

from scrapper import B3Scrapper


class B3Extractor:
    def __init__(self):
        self._scrapper = B3Scrapper()

    def extract(self) -> dict:
        try:
            df = self._scrapper.scrape()
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': f'Erro ao obter dados da B3: {str(e)}'})}

        now = datetime.now(timezone.utc)
        date_str = now.strftime('%Y-%m-%d')
        filename = f'b3_{date_str}.parquet'
        buffer = io.BytesIO()
        df.to_parquet(path=buffer, index=False, engine='pyarrow')
        buffer.seek(0)

        s3 = boto3.client('s3')
        bucket = os.environ['BUCKET_NAME']
        s3.put_object(Bucket=bucket, Key=f'date={date_str}/{filename}', Body=buffer.getvalue())

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data saved successfully', 'filename': filename})
        }
