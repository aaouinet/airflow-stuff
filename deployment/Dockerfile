FROM apache/airflow:2.4.3
COPY requirements.txt .
RUN pip install -r requirements.txt 
RUN curl -Lo aws-iam-authenticator https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v0.5.9/aws-iam-authenticator_0.5.9_linux_amd64 &&\
    chmod +x ./aws-iam-authenticator &&\
    mkdir -p $HOME/bin && cp ./aws-iam-authenticator $HOME/bin/aws-iam-authenticator && export PATH=$PATH:$HOME/bin 


