import pandas as pd
import csv

import requests
from io import StringIO


class DemandDataLoader:
	def __init__(self):
		pass

	def get_historical_demand_data_df(self, years):
		all_data = []
		for year in years:
			# TODO: Handle the case where a year is not present:
			url = f"https://api.neso.energy/dataset/8f2fe0af-871c-488d-8bad-960426f24601/resource/8a4a771c-3929-4e56-93ad-cdf13219dea5/download/demanddataupdate_{year}.csv"

			query_parameters = {"download_format": "csv"}

			response = requests.get(url, params=query_parameters)

			year_data = list(csv.DictReader(StringIO(response.text)))
			all_data.extend(year_data)

		df = pd.DataFrame(all_data)

		df['SETTLEMENT_PERIOD'] = df['SETTLEMENT_PERIOD'].apply(func=lambda x:int(x))
		df = df[df['SETTLEMENT_PERIOD'] % 2 == 0]

		df['year'] = df['SETTLEMENT_DATE'].apply(func=lambda x:int(x.split('-')[0]))
		df['month'] = df['SETTLEMENT_DATE'].apply(func=lambda x:int(x.split('-')[1]))
		df['day'] = df['SETTLEMENT_DATE'].apply(func=lambda x:int(x.split('-')[2]))
		df['hour'] = df['SETTLEMENT_PERIOD'].apply(func=lambda x:int(x / 2 - 1))

		df['ND'] = df['ND'].apply(func=lambda x: float(x))

		columns = ['year', 'month', 'day', 'hour', 'ND']

		return df[columns]
