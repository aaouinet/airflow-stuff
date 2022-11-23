
## Airflow on Kubernetes (azure)
To deploy Airflow on Kuberntes, the first step is to create a namespace.

```Powershell


create deployer spn (appregistration -> spark-deployer)
az login --service-principal -u $SP_APP_ID -p $SP_APP_PW --tenant $TENANT_ID

az aks get-credentials --resource-group $myResourceGroup --name $myAKSCluster

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
    repo: https://github.com/aaouinet/airflow-stuff.git
    branch: main
    rev: HEAD
    depth: 1
    # the number of consecutive failures allowed before aborting
    maxFailures: 0
    # subpath within the repo where dags are located
    # should be "" if dags are at repo root
    subPath: "dags"


cd deployment
$ACR_URL="airflowjarvis.azurecr.io"
az acr login --name $ACR_URL

docker build -t $ACR_URL/airflow-custom:1.0.0 .
docker push $ACR_URL/airflow-custom:1.0.0 

```

## Deploy airflow pon kubernetes


```Powershell
helm repo add apache-airflow https://airflow.apache.org
helm repo update
helm search repo airflow

helm upgrade --install airflow apache-airflow/airflow -n airflow `
--set defaultAirflowRepository=$ACR_URL/airflow-custom `
--set defaultAirflowTag="1.0.0" --debug

helm ls -n airflow 

```

## local windows airflow tests
Open Microsoft Store, search for Ubuntu, install it then restart
Open cmd and type wsl
Update everything: sudo apt update && sudo apt upgrade
Install pip3 like this
sudo apt-get install software-properties-common
sudo apt-add-repository universe
sudo apt-get update
sudo apt-get install python3-pip
5. Install Airflow: pip3 install apache-airflow 

6. Run sudo nano /etc/wsl.conf, insert the block below, save and exit with ctrl+s ctrl+x

[automount]
root = /
options = "metadata"
7. Run nano ~/.bashrc, insert the line below, save and exit with ctrl+s ctrl+x

export AIRFLOW_HOME=/mnt/c/users/YOURNAME/airflowhome


# create admin user 
airflow users create \
    --username admin \
    --firstname Peter \
    --lastname Parker \
    --role Admin \
    --email spiderman@superhero.org

# install requirements
pip3 install -r airflow-stuff/deployment/requirements.txt

# check whether AIRFLOW_HOME was set correctly 
env | grep AIRFLOW_HOME 
# initialize database in AIRFLOW_HOME 
airflow initdb 
# initialize scheduler 
airflow scheduler 
# use the second cmd window to run 
airflow webserver 
# access the UI on localhost:8080 in your browser