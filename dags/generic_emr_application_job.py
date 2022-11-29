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
from datetime import timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.providers.amazon.aws.operators.emr import EmrContainerOperator
from airflow.utils.dates import days_ago
from custom_operator.custom_kubernetees_sensor import CustomSparkKubernetesSensor
from airflow.operators.python_operator import PythonOperator
import yaml
import sys

# [emr release vs spark version]
spark_version="3.3.0"
emr_release = {
  "3.3.0": "emr-6.8.0-latest",
  "3.2.1": "emr-6.7.0-latest",
  "3.2.0": "emr-6.6.0-latest",
  "3.1.2": "emr-6.5.0-latest"
}

# [START howto_operator_emr_eks_config]
JOB_DRIVER_ARG = {
    "sparkSubmitJobDriver": {   
      "entryPoint": "local:///usr/lib/spark/examples/jars/spark-examples.jar",
      "sparkSubmitParameters": "--class org.apache.spark.examples.SparkPi"
    }
}

CONFIGURATION_OVERRIDES_ARG = {
      "applicationConfiguration": [
        {
          "classification": "spark-defaults", 
          "properties": {
            "spark.kubernetes.container.image": "318897785936.dkr.ecr.eu-west-1.amazonaws.com/spark:3.3.1-test",
            "spark.driver.core": "1",
            "spark.driver.memory": "512m",
            "spark.executor.cores": "1",
            "spark.executor.memory": "512m",
            "spark.executor.instances": "1",
            "spark.executor.defaultJavaOptions": "-verbose:gc -XX:+UseParallelGC -XX:InitiatingHeapOccupancyPercent=70"  }
        }
      ], 
      "monitoringConfiguration": {
        "s3MonitoringConfiguration": {
          "logUri": "s3://emr-on-eks-nvme-318897785936-eu-west-1/logs/airflow"
        }
      }
}
# 
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


dag = DAG(
    dag_id='spark_emr_generic_job',
    dagrun_timeout=timedelta(hours=2),
    start_date=days_ago(1),
    schedule_interval="@once",
    tags=["emr_containers", "example"],
    params={
        "cluster": "iy2lb99tr6pd1fepo2xxiyyau",
        "spark_version": "3.3.1",
        "namespace": "emr",
        "image": "318897785936.dkr.ecr.eu-west-1.amazonaws.com/spark:3.3.1-test"
    },
    catchup=False
)

    # An example of how to get the cluster id and arn from an Airflow connection
    # VIRTUAL_CLUSTER_ID = '{{ conn.emr_eks.extra_dejson["virtual_cluster_id"] }}'
    # JOB_ROLE_ARN = '{{ conn.emr_eks.extra_dejson["job_role_arn"] }}'


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

   
# spark emr generic job
run_emr_job = EmrContainerOperator(
    task_id="spark_job_submit",
    virtual_cluster_id='{{ conn.aws_default.extra_dejson["virtual_cluster_id"] }}',
    execution_role_arn='{{ conn.aws_default.extra_dejson["job_role_arn"] }}',
    release_label=emr_release[spark_version],
    job_driver=JOB_DRIVER_ARG,
    configuration_overrides=CONFIGURATION_OVERRIDES_ARG,
    name="spark_sample",
)
# spark kubernetes monitoring job
monitor_spark_job = CustomSparkKubernetesSensor(
    task_id='spark_pi_monitor',
    namespace="{{ params.namespace }}",
    kubernetes_conn_id="{{ params.cluster }}",
    application_name="{{ task_instance.xcom_pull(task_ids='spark_job_submit')['metadata']['name'] }}",
    dag=dag,
)

check_dag_input >> run_emr_job >> monitor_spark_job


    # [END howto_operator_emr_eks_jobrun]

