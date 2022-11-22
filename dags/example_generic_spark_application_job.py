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
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


# check dag inputs:
# - cluster and image : should not be empty
def check_dag_input(cluster_id, image, namespace):
    """
    Check dag inputs.
    :param cluster_id: cluster_id object
    :param image: image object
    :param namespace: namespace object
    :return: check status 
    """

    print("cluster_id: "+cluster_id)
    print("image: "+image)
    try:
       if(len(cluster_id) == 0 or len(image) == 0):
            raise Exception('cluster_id and image should not be empty')
    except:
        print("failed to check dag input") 
        print('cluster_id and image should not be empty')
        sys.exit(1)
    finally:
        print("input checked") 
       
        

dag = DAG(
    dag_id='spark_generic_job',
    dagrun_timeout=timedelta(hours=2),
    start_date=days_ago(1),
    schedule_interval="@once",
    tags=["spark_application", "example"],
    catchup=False
) 

# Get values from dag run configuration
cluster="{{ dag_run.conf['cluster'] }}"
namespace="{{ dag_run.conf['namespace'] }}"
image="{{ dag_run.conf['image'] }}"


# Step 1
check_dag_input = PythonOperator(
    task_id='check_dag_input',
    python_callable=check_dag_input,
    op_kwargs={
        'cluster_id': cluster,
        'image': image,
        'namespace': namespace
    },
    dag=dag
)


# [START SparkKubernetesOperator]
SparkKubernetesOperator(
    task_id='spark_pi_submit',
    namespace="{{ namespace }}",
    kubernetes_conn_id="{{ cluster }}",
    application_file=open("/opt/airflow/dags/repo/dags/sparkApplications/SparkPi.yaml").read(), #known bug
    do_xcom_push=True,
    dag=dag
)

    # [END SparkKubernetesOperator]