# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
This is an example dag for an Amazon EMR on EKS Spark job.
"""
import os
from datetime import timedelta

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.utils.dates import days_ago


with DAG(
    dag_id='spark_application_eks_pi_job',
    dagrun_timeout=timedelta(hours=2),
    start_date=days_ago(1),
    schedule_interval="@once",
    tags=["spark_application", "example"],
) as dag:


    # [START SparkKubernetesOperator]
        SparkKubernetesOperator(
        task_id='spark_pi_submit',
        namespace="spark-operator",
        kubernetes_conn_id="eks_poc_cluster",
        application_file="/opt/airflow/dags/repo/dags/sparkApplications/SparkPi.yaml", #officially know bug
        do_xcom_push=True,
        dag=dag
        )

    # [END SparkKubernetesOperator]