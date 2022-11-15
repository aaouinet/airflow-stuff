
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

