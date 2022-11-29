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
from airflow.providers.cncf.kubernetes.sensors.spark_kubernetes import SparkKubernetesSensor
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow.configuration import conf
from custom_operator.custom_spark_kubernetes import CustomSparkKubernetesOperator
from custom_operator.custom_kubernetees_sensor import CustomSparkKubernetesSensor

import json
import yaml


# Get values from dag run configuration
# cluster="{{dag_run.conf['cluster']}}"
# namespace="{{dag_run.conf['namespace']}}"
# image="{{dag_run.conf['image']}}"

# get dags home (to do: get from dag_run context)
dags_home =  Variable.get("dags_home")


# check dag inputs:
# - cluster and image : should not be empty
def check_dag_input(job_config):
    """
    Check dag inputs.
    :param cluster_id: cluster_id object
    :param image: image object
    :param namespace: namespace object
    :return: check status 
    """
    
    print(job_config)
    job_configuration = yaml.safe_load(job_config)
    print(type(yaml.safe_load(job_config)))
    print(job_configuration)

    cluster = job_configuration["cluster"]
    namespace = job_configuration["namespace"]
    image = job_configuration["image"] 
    print (cluster)
    print(namespace)
    try:
       if(len(cluster) == 0 or len(namespace) == 0):
            raise Exception('cluster and namespace should not be empty')
    except:
        print("failed to check dag input") 
        print('cluster and namespace should not be empty')
        sys.exit(1)
    finally:
        print("input checked")
        # set cluster var 
        Variable.set("cluster", cluster ) 
        return job_configuration
       

# [START SparkKubernetesOperator_DAG]
dag = DAG(
    dag_id='spark_generic_job',
    dagrun_timeout=timedelta(hours=2),
    start_date=days_ago(1),
    schedule_interval="@once",
    tags=["spark_application", "example"],
    params={
        "cluster": "iy2lb99tr6pd1fepo2xxiyyau",
        "spark_version": "3.3.1",
        "namespace": "spark",
        "image": "318897785936.dkr.ecr.eu-west-1.amazonaws.com/spark:3.3.1-test"
    },
    catchup=False
) 


# Step 1
check_dag_input = PythonOperator(
    task_id='check_dag_input',
    python_callable=check_dag_input,
    do_xcom_push=True,
    op_kwargs={
        "job_config": "{{ dag_run.conf }}"
    },
    dag=dag
)

   
# spark kubernetes generic job
run_saprk_job = CustomSparkKubernetesOperator(
    task_id='spark_job_submit',
    namespace="{{ params.namespace }}",
    kubernetes_conn_id="{{ params.cluster }}",
    application_file=open(str(dags_home)+"/sparkApplications/SparkJobTemplate.yaml").read(), #known bug
    do_xcom_push=True,
    params={
        "job_configuration": "{{ dag_run.conf }}"
    },
    dag=dag
)

# spark kubernetes monitoring job
monitor_spark_job = CustomSparkKubernetesSensor(
    task_id='spark_pi_monitor',
    namespace="{{ params.namespace }}",
    kubernetes_conn_id="{{ params.cluster }}",
    application_name="{{ task_instance.xcom_pull(task_ids='spark_job_submit')['metadata']['name'] }}",
    dag=dag,
)

check_dag_input >> run_saprk_job >> monitor_spark_job

# [END SparkKubernetesOperator_DAG]



