from google.cloud import run_v2
import google.auth


class JobExecutionViewer:
    def __init__(self, region, job_name):
        self.region = region
        self.job_name = job_name

        self.client = run_v2.ExecutionsClient()

        _, self.project_id = google.auth.default()

    def _get_parent(self):
        return (
            f"projects/{self.project_id}"
            f"/locations/{self.region}"
            f"/jobs/{self.job_name}"
        )

    def get_latest_execution(self):
        parent = self._get_parent()
        executions = self.client.list_executions(parent=parent)
        latest_execution = next(iter(executions), None)

        return latest_execution.completion_time if latest_execution else None
