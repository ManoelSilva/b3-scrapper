import os

import requests
import pandas as pd
from base64_decoder import Base64Decoder


class B3Scrapper:
    def __init__(self):
        self.base_url = os.environ['B3_API_URL']
        self.payload = '{"language":"pt-br","index":"IBOV","segment":"1"}'

    def scrape(self) -> pd.DataFrame:
        uri = Base64Decoder.encode_base64(self.payload)
        url = f'{self.base_url}{uri}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        results = data.get('results', [])
        if not results:
            raise ValueError('No results found in B3 response')
        df = pd.DataFrame(results)
        return df
