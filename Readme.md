
<!-- markdownlint-configure-file {
  "MD013": {
    "code_blocks": false,
    "tables": false
  },
  "MD033": false,
  "MD041": false
} -->

<div align="left">

# spark airflow jobs samples

This repository give some airflow dags and scripts to submit generic spark (through templates) on following compute services:
- spark on aks (kubernetes on azure)
- spark on eks (kubernetes on aws)
- spark on emr/eks (aws emr containers on kubernetes)

•[Test using airflow on Kubernetes ](#test-using-airflow-on-kubernetes ) 

•[local airflow tests on windows](#local-airflow-tests-on-windows)

</div>


# Test using airflow on Kubernetes 

## create namespace

```Powershell

kubectl create namespace airflow
kubectl get namespaces
```
## Build custom airflow image


```Powershell
helm show values apache-airflow/airflow > values.yaml

enable git sync configutation : 
  gitSync:
    enabled: true

    # git repo clone url
    # ssh examples ssh://git@github.com/apache/airflow.git
    # git@github.com:apache/airflow.git
    # https example: https://github.com/apache/airflow.git
    repo: <this repo.git>
    branch: main
    rev: HEAD
    depth: 1
    # the number of consecutive failures allowed before aborting
    maxFailures: 0
    # subpath within the repo where dags are located
    # should be "" if dags are at repo root
    subPath: "dags"


cd deployment
$ACR_URL="<ecr repo>.azurecr.io"
az acr login --name $ACR_URL

docker build -t $ACR_URL/airflow-custom:1.0.0 .
docker push $ACR_URL/airflow-custom:1.0.0 

```

## Deploy airflow on kubernetes


```Powershell
helm repo add apache-airflow https://airflow.apache.org
helm repo update
helm search repo airflow

helm upgrade --install airflow apache-airflow/airflow -n airflow `
--set defaultAirflowRepository=$ACR_URL/airflow-custom `
--set defaultAirflowTag="1.0.0" --debug

helm ls -n airflow 

```

## test spark dags


```Powershell

kubectl port-forward  svc/airflow-webserver 8085:8080 -n airflow

# access the UI on localhost:8080
# run dags from UI or through airflow API using dag conf
# example :
http://localhost:8080/api/v1/dags/spark_generic_job/dagRuns
  {
        "cluster": "eks_poc_cluster",
        "spark_version": "3.3.1",
        "namespace": "spark",
        "image": "<account id>.dkr.ecr.eu-west-1.amazonaws.com/spark:3.3.1-test"
    }
```


# local airflow tests on windows

## Deploy airflow on local wsl/ubuntu
```Powershell
#Open Microsoft Store, search for Ubuntu, install it then restart
# Open cmd and type wsl
wsl
# Update everything: 
sudo apt update && sudo apt upgrade
#Install pip3 like this
sudo apt-get install software-properties-common
sudo apt-add-repository universe
sudo apt-get update
sudo apt-get install python3-pip
# Install Airflow: 
pip3 install apache-airflow 

# Run sudo nano /etc/wsl.conf, insert the block below, save and exit with ctrl+s ctrl+x

[automount]
root = /
options = "metadata"

# update .bashrc, insert the line below, save and exit with ctrl+s ctrl+x
nano ~/.bashrc
export AWS_ACCESS_KEY_ID=< aws key>
export AWS_SECRET_ACCESS_KEY=<aws secret>
export AIRFLOW_HOME=/c/Users/<user>/airflow
export airflowuser=<airflow user>
export airflowpassword=<airflow passwd>

# create admin user 
airflow users create \
    --username abdel \
    --firstname Peter \
    --lastname Parker \
    --role Admin \
    --email spiderman@superhero.org

# install requirements
pip3 install -r deployment/requirements.txt

# check whether AIRFLOW_HOME was set correctly 
env | grep AIRFLOW_HOME 
# initialize database in AIRFLOW_HOME 
airflow initdb 
# initialize scheduler 
airflow scheduler 
# use the second cmd window to run 
airflow webserver 
# access the UI on localhost:8080 in your browser

```
## Run airflow tests

```Powershell

# acess local ubuntu
wsl
cd <this repo>

#  spark on aks job submit example
./job-submit.sh --cluster_type="aks" --cluster_id="aks_poc_cluster" --spark_version="3.3.1"  --configuration_file="job_config.json"

#  spark on eks job submit example
./job-submit.sh --cluster_type="eks" --cluster_id="eks_poc_cluster" --spark_version="3.3.1"  --configuration_file="job_config.json"

#  spark on emr/eks job submit example
./job-submit.sh --cluster_type="emr" --cluster_id="eks_poc_cluster" --spark_version="3.3.1"  --configuration_file="job_config.json"
https://06d450f2e2d24342b7f5b16522145547.svc.dynamics.com/EvtMgmt/api/v2.0/checkin/stream?sessionRegistrationId=SR%20H6AU24NQ4XVPEWULZ8RXHEGCME&redirectUri=https%3A%2F%2Fteams.microsoft.com%2Fl%2Fmeetup-join%2F19%253ameeting_MGJhZGE0NGMtMGQ2MS00YzdmLTljYTUtYWFjZTQwZTc2NzY0%2540thread.v2%2F0%3Fcontext%3D%257b%2522Tid%2522%253a%252272f988bf-86f1-41af-91ab-2d7cd011db47%2522%252c%2522Oid%2522%253a%2522c5825cfd-a05b-4288-8c3d-cec2cf365dd6%2522%257d
```
