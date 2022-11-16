
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

az acr login --name $ACR_URL

docker build -t $ACR_URL/airflow-custom:1.0.0 .
docker push $ACR_URL/airflow-custom:1.0.0 

```

## Deploy airflow 


```Powershell
helm repo add apache-airflow https://airflow.apache.org
helm repo update
helm search repo airflow

helm upgrade --install airflow apache-airflow/airflow -n airflow `
--set defaultAirflowRepository=$ACR_URL/airflow-custom `
--set defaultAirflowTag="1.0.0" --debug

helm ls -n airflow 

```

