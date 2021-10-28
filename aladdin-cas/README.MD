# pandora 代码结构
```shell
├── docs #文档目录
├── Jenkinsfile #jenkins自动构建脚本
├── scripts#脚本目录
│   ├── centos#构建centos系统运行时依赖的文件
│   ├── docker_package#构建docker镜像依赖的文件
│   └── helm#使用helm部署的脚本
├── src #源码目录
│   ├── analysis_package#分析算法模块
│   ├── conf#配置文件
│   ├── handler#http请求处理
│   ├── model#保存机器训练模型以及依赖的文件
│   ├── predata#预处理数据
│   ├── prework#预处理代码
└── unit_test#单元测试模块
```



# 代码下载

- 安装git

- 从pandora项目主仓库fork一个个人仓库

- 使用git工具将代码下载到本地


#  构建

由于公司网络隔离，pandora依赖的第三方模块安装速度很慢，个别模块需要翻墙才能安装。因此以centos7.4为基础创建一个pandora-base镜像，该镜像中安装了pandora开发、测试、构建等各环节中依赖的所有第三方环境。因此目前pandora暂时只支持在pandora-base生成的容器内部进行构建与测试。

## 本地容器内部构建

- 安装docker-ce

- 使用docker构建一个pandora-base镜像。

- 使用pandora-base镜像创建一个容器，并将pandora代码目录挂载到容器。

- 进入容器，切换到pandora源码目录，执行构建脚本。

  ```shell
  yum -y install docker-ce
  cd scripts/docker_package && sh build.sh base
  docker run -it --rm  -v /root/pandora:/root/pandora pandora-base /bin/bash
  cd /root/pandora/src && sh package.sh
  ```

## jenkins构建

- jenkins多分支构建配置。
- 将开发的代码合并到主仓库的相应分支，自动触发构建，生成相应的pandora小包。
- 手动触发大包构建，将pandora小包打入AnyShare大包中。

# 开发

## 开发流程

- 根据需求编号，在主仓库上创建相应的Feature分支。
- 将本地的develop分支push到个人仓库的develop分支上。
- 将个人仓库develop分支的代码merge到主仓库的Feature分支上。

## 添加接口

- 在analysis_package进行功能模块的开发。
- 在handler目录下编写相应的接口处理类，进行接口的参数检查，并调用具体的功能模块。
- 将接口处理类注册到相应的src/server.py的url上。

# 测试

测试用例保存在docs/Test_Case目录下,测试代码保存在unit_test目录下。开发或修改代码后请执行以下过程：

- 根据代码改动，添加相应测试用例。
- 根据测试用例编写相应的接口测试代码。
- 使用pandora-base镜像创建测试容器，并将pandora目录挂在到容器的/root/pandora目录
- 进入容器并切换到/root/pandora目录。
- 通过源码启动pandora服务（如果不是接口测试，则跳过此步骤）。
- 执行相应的测试脚本。

# 集成到AnyShare集群

构建Feature分支的大包：

- 为AnyShareConfig、pandora、UpgradeScripts6.0项目添加feature分支。
- 修改AnyShareConfig，将pandora.service文件添加到 service_script目录，将pandora服务信息添加到conf/default_service.yaml文件中。
- 修改UpgradeScript6分支，将pandora的升级脚本添加到正确的目录，目录规则：[to_version]/[from_version]/static/pandora。
- 在各项目的Feature分支上开发完毕后，代码更新的gitlab的主仓库，自动触发jenkins构建各个项目的小包。
- 网页上登陆jenkins：http://192.168.137.90:8080/view/_Server_ST/job/I_P_AS_Server_CentOS7_Feature/build?delay=0sec。配置构建参数将project参数配置为:Feature-[feature分支名]，执行build开始构建AnyShare大包。
- 构建完成后，将生成对应的大包，并自动上传到ftp服务器上：ftp://asftp.eisoo.com/FTP/Feature/