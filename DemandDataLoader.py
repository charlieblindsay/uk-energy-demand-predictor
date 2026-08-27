import pandas as pd
import csv
from datetime import datetime

import requests
from io import StringIO


class DemandDataLoader:
	def __init__(self):
		pass

	def parse_settlement_date(self, date_str):
		for fmt in ('%Y-%m-%d', '%d-%b-%Y'):
			try:
				return datetime.strptime(date_str, fmt)
			except ValueError:
				continue
		raise ValueError(f"Unrecognized date format: {date_str}")

	def get_historical_demand_data_df(self, years):
		all_data = []
		current_year = datetime.now().strftime("%Y")

		year_url_lookup = {
			"2026": "8a4a771c-3929-4e56-93ad-cdf13219dea5",
			"2025": "b2bde559-3455-4021-b179-dfe60c0337b0",
			"2024": "f6d02c0f-957b-48cb-82ee-09003f2ba759"
		}

		for year in years:
			url_code = year_url_lookup[year]

			if year == current_year:
				url = f"https://api.neso.energy/dataset/8f2fe0af-871c-488d-8bad-960426f24601/resource/{url_code}/download/demanddataupdate_{year}.csv"
			else:
				url = f"https://api.neso.energy/dataset/8f2fe0af-871c-488d-8bad-960426f24601/resource/{url_code}/download/demanddata_{year}.csv"

			query_parameters = {"download_format": "csv"}

			response = requests.get(url, params=query_parameters)

			year_data = list(csv.DictReader(StringIO(response.text)))
			all_data.extend(year_data)

		df = pd.DataFrame(all_data)

		df['SETTLEMENT_PERIOD'] = df['SETTLEMENT_PERIOD'].apply(func=lambda x:int(x))
		df = df[df['SETTLEMENT_PERIOD'] % 2 == 0]

		df['_parsed_date'] = df['SETTLEMENT_DATE'].apply(self.parse_settlement_date)

		df['year'] = df['_parsed_date'].apply(lambda d: d.year)
		df['month'] = df['_parsed_date'].apply(lambda d: d.month)
		df['day'] = df['_parsed_date'].apply(lambda d: d.day)
		df = df.drop(columns=['_parsed_date'])

		df['hour'] = df['SETTLEMENT_PERIOD'].apply(func=lambda x:int(x / 2 - 1))

		df['ND'] = df['ND'].apply(func=lambda x: float(x))

		columns = ['year', 'month', 'day', 'hour', 'ND']

		return df[columns]
