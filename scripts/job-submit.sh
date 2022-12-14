#!/bin/bash

#
# a simple way to run spark on k8s airflow dags
# 

cluster_type="[aks | eks | emr]"
cluster_id="cluster_id";
spark_version="[3.3.1 | 3.2.1 | 3.1.2]";
configuration_file="application_config.json";


function usage()
{
    echo "simple job submit script"
    echo ""
    echo "./job-submit.sh"
    echo "\t-h --help"
    echo "\t-t --cluster_type=${cluster_type}";
    echo "\t-c --cluster_id=${cluster_id}";
    echo "\t-v --spark_version=${spark_version}";
    echo "\t-f --configuration_file=${configuration_file}";
    echo ""
}

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        -h | --help)
            usage
            exit
            ;;
        -t | --cluster_type)
            cluster_type=$VALUE
            ;;
        -c | --cluster_id)
            cluster_id=$VALUE
            ;;
        -v | --spark_version)
            spark_version=$VALUE
            ;;
        -f | --configuration_file)
            configuration_file=$VALUE
            ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
    shift
done

echo "##############################################"
echo "Running spark job wit following configuration:"
echo "##############################################"
echo "cluster type : ${cluster_type} ";
echo "cluster id : ${cluster_id} ";
echo "spark version : ${spark_version}";
echo "configuration file: ${configuration_file} ";



# render a template configuration file
# expand variables + preserve formatting
render_template() {
  eval "echo \"$(cat $1 | sed  's/"/\\""/g')\""
}


# run airflow spark k8s dag
run_spark_k8s_dag() {
 rendred_configuration_file=$1
 curl -X POST \
   http://localhost:8080/api/v1/dags/spark_generic_job/dagRuns  \
   -H 'Cache-Control: no-cache'  \
   -H 'Content-Type: application/json'  \
   --user $airflowuser:$airflowpassword   \
   -d  @${rendred_configuration_file}
}


# run airflow spark emr dag
run_spark_emr_dag() {
 rendred_configuration_file=$1
 curl -X POST \
   http://localhost:8080/api/v1/dags/spark_emr_generic_job/dagRuns  \
   -H 'Cache-Control: no-cache'  \
   -H 'Content-Type: application/json'  \
   --user $airflowuser:$airflowpassword   \
   -d  @${rendred_configuration_file}
}


# main

case ${cluster_type} in
    "aks" )
        container_repo="airflowjarvis.azurecr.io"
        render_template application_config.json > rendred_application_config.json
        run_spark_k8s_dag rendred_application_config.json        
        ;;
    "eks" )
        container_repo="318897785936.dkr.ecr.eu-west-1.amazonaws.com"
        render_template application_config.json > rendred_application_config.json
        run_spark_k8s_dag rendred_application_config.json        
        ;;
    "emr" )
        render_template application_config.json > rendred_application_config.json
        run_spark_emr_dag rendred_application_config.json        
        ;;
esac









