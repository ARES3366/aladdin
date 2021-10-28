<!--
 * @Author: your name
 * @Date: 2020-06-10 01:06:39
 * @LastEditTime: 2020-06-10 01:06:39
 * @LastEditors: your name
 * @Description: In User Settings Edit
 * @FilePath: /aladdin-cas/scripts/helm/object-detection/readme.md
--> 
# Pandora Helm Chart

This directory contains a Kubernetes chart to deploy a object-detection

## Chart Details

This chart will do the following:

* Implement a object-detection deployment

## Installing the Chart

To install the chart, use the following:

```shell
$ helm install helm
```

## Configuration

The following table lists the configuable parameters of the
Pandora and their default values.

| Parameter | Description | Default |
|:----------|:------------|:--------|
| `image.registry` | image registry to use | `acr.aishu.cn` |
| `image.repository` | Container image to use | `ict/aladdin-cas` |
| `image.tag` | Container image tag to deploy | `switch-aladdin-M2` |
| `image.pullPolicy` | Container pull policy | `IfNotPresent` |
| `service.type` | service type | `ClusterIP` |
| `service.port` | TCP port on which the service is exposed | 9528 |
| env.LOGGING_LEVEL | log level, the value must in 'DEBUG' and 'RELEASE' | DEBUG |
| env.tornado.MAX_BUFFER_SIZE | tornado server param 'max_buffer_size',suggest 500Mi | 100Mi |
| env.tornado.MAX_BODY_SIZE | tornado server param 'max_body_size', suggest 500Mi | 100Mi |
| resources.limits.cpu | CPU upper limit, suggest 1 | unlimited |
| resources.limits.memory | memoy upper limit, suggest 5Gi | unlimited |
| resources.requests.cpu | CPU lower limit, suggest 0.5 | 0.5              |
| resources.requests.memory | memory lower limit, suggest 500Mi | 0 |

Specify each paramter using the `--set key=value[,key=value]` argument to
`helm install`.
