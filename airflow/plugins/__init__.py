from airflow.plugins_manager import AirflowPlugin

import operators
import helpers


class UdacityPlugin(AirflowPlugin):
    name = "udacity_plugin"
    operators = [
        operators.DropTableOperator,
        operators.ExtractOperator,
        operators.FXRateOperator,
        operators.HasRowsOperator,
        operators.IngestOperator,
        operators.LoadTableOperator,
        operators.StageToRedshiftOperator,
    ]
    helpers = [
        helpers.CreateSQL,
        helpers.InsertSQL,
    ]
