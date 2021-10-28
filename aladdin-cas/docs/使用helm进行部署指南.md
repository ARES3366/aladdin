[TOC]

# 软件需求：

​	kubernetes-suite >= 0.1.1

# 部署步骤：

​	从jenkins下载pandora包
```sh
wget http://10.2.65.5:8080/job/pandora/lastSuccessfulBuild/artifact/pandora-0.0.1-{build_number}.tar.gz
```

​	解压 pandora-{version}-{build_number}.tar.gz

```sh
tar -xzf pandora-0.0.1-111.tar.gz
```

​	进入到目录 pandora-{version}-{build_number}

```shell
cd pandora-0.0.1-111
```

​        导入pandora镜像

```sh
 docker load -i image.tar
```

​	如有必要，修改pandora部署参数

```sh
[root@localhost pandora-0.0.1-111]# vim helm/values.yaml 
```

```yaml
replicaCount: 1            #部署的副本数

image:
  repository: pandora       #镜像名称
  tag: 0.0.1                #镜像的标签  
  pullPolicy: IfNotPresent  #镜像拉取策略

resources:
  limits:
    cpu: 1            #cpu上限,0.5-1之间取值
    memory: 2000Mi    #内存使用上限：建议取2000Mi
  requests:
    cpu: 0.9          #cpu下限
    memory: 500Mi     #内存使用下限：建议取500Mi

env:
  #可以设置[NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL]
  LOGGING_LEVEL: DEBUG
  tornado:
    DEBUG: True            #是否以debug模式启动tornado服务

    MAX_BUFFER_SIZE: 200Mi #tornado服务每个客户端最大使用的内存大小
    MAX_BODY_SIZE: 500Mi   #tornado服务每个客户端最大POST的数据大小
                           #如果post的数据大于MAX_BODY_SIZE，则直接返回错误，且后台打印 ”CONTENT—LENGTH too long“ 
                           #如果post的数据大于MAX_BUFFER_SIZE，那么将会把数据存放到临时文件中，因此会影响服务的性能造成响应超时。

nameOverride: ""
fullnameOverride: ""

service:
  type: NodePort
  port: 9528         #pandora服务的端口号。
  nodePort: 32032    #映射到节点上的端口号，供调试时使用。

ingress:
  enabled: false
  annotations: {}
    # kubernetes.io/ingress.class: nginx
    # kubernetes.io/tls-acme: "true"
  hosts:
    - host: chart-example.local
      paths: []

  tls: []


```

​	创建pandora release：

```shell
helm install  helm -n release-name
```

​        查看helm release是否已经生成

```shell
[root@localhost pandora]# helm list
NAME	REVISION	UPDATED                 	STATUS  	CHART        	APP VERSION	NAMESPACE
mxx 	3       	Tue Apr 16 09:07:28 2019	DEPLOYED	pandora-0.0.1	1.0        	default  
```

​	查看 pod 是否生成

```shell
[root@localhost pandora]# kubectl get pod
NAME                           READY   STATUS    RESTARTS   AGE
grafana-74b887f6fb-6cn52       1/1     Running   0          22h
mxx-pandora-5f856b98b7-cnn7r   1/1     Running   0          4h40m
```

