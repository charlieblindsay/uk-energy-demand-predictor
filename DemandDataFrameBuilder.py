import pandas as pd


class DemandDataFrameBuilder:
    def __init__(self):
        pass

    def build(
        self,
        historical_df_with_demand_data,
        future_df_without_demand_data,
        future_predicted_demand
    ):
        historical_df_copy = historical_df_with_demand_data.copy()
        historical_df_copy['datetime'] = pd.to_datetime(
            historical_df_copy[['year', 'month', 'day', 'hour']]
        )

        future_df_copy = future_df_without_demand_data.copy()
        future_df_copy['datetime'] = pd.to_datetime(
            future_df_copy[['year', 'month', 'day', 'hour']]
        )

        historical_part = pd.DataFrame(
            {
                'datetime': historical_df_copy['datetime'],
                'demand': historical_df_copy['ND'],
                'predicted': False
            }
        )

        future_part = pd.DataFrame(
            {
                'datetime': future_df_copy['datetime'],
                'demand': future_predicted_demand,
                'predicted': True
            }
        )

        return pd.concat([historical_part, future_part], ignore_index=True).set_index('datetime')
