import streamlit as st
from CloudStorage import CloudStorage
from JobExecutionViewer import JobExecutionViewer
from DemandDataViewer import DemandDataViewer
from config import REGION, DATA_JOB_NAME


def main():
    df = CloudStorage().load_data()

    viewer = DemandDataViewer(df=df)

    st.write(f'Training data range: {viewer.min_historical_date} - {viewer.max_historical_date}')

    job_execution_viewer = JobExecutionViewer(
        region=REGION,
        job_name=DATA_JOB_NAME)

    latest_execution = job_execution_viewer.get_latest_execution()

    if latest_execution:
        st.write("Last time data was refreshed and model was retrained on new data:", latest_execution)

    start_date = st.date_input(
        label='start_date',
        min_value=viewer.min_date,
        max_value=viewer.max_date
    )
    end_date = st.date_input(
        label='end_date',
        min_value=viewer.min_date,
        max_value=viewer.max_date
    )

    chart_df = viewer.get_df_actual_filtered_vs_predicted(
        start_date=start_date,
        end_date=end_date
    )

    st.line_chart(
        chart_df,
        color=["#0000FF", "#00AA00"]
    )


if __name__ == '__main__':
    main()
