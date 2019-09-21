# Dog-Cat Classifier

Dog and cat image classifier with deep learning.

<br/>

## Example:
| <img src="code/test_dog.jpg?raw=true" width="200">|<img src="code/test_cat.jpg?raw=true" width="200">|
|:-:|:-:|
|Dog: 0.92035621<br/>Cat: 0.04618423|Cat: 0.90135497<br/>Dog: 0.09642436|

[http://sz.mofangdegisn.cn](http://sz.mofangdegisn.cn)

## Test Picture

[dot-cat picture](https://github.com/ardamavi/Dog-Cat-Classifier/tree/master/Data/Train_Data)

## 部署到函数计算

**Reference:** [开发函数计算的正确姿势——tensorflow serving](https://yq.aliyun.com/articles/702739)

#### 1. clone 该工程

```bash
git clone https://github.com/awesome-fc/cat-dog-classify.git
```

复制 `.env_example` 文件为 `.env`, 并且修改 `.env` 中的信息为自己的信息

#### 2. 安装最新版本的 fun
[fun 安装手册](https://github.com/alibaba/funcraft/blob/master/docs/usage/installation-zh.md)

#### 3. fun 安装依赖包
执行 `fun install`, fun 会根据 Funfile 中定义的逻辑安装相关的依赖包

```bash
root@66fb3ad27a4c: ls .fun/nas/auto-default/classify
model  python
```

根据 Funfile 的定义, 将第三方库下载到 `.fun/nas/auto-default/classify/python` 目录下
本地 model 目录移到 `.fun/nas/auto-default/model` 目录下

#### 4. 将下载的依赖的代码包上传到 nas

``` bash
fun nas init
fun nas info
fun nas sync
fun nas ls nas://classify:/mnt/auto/
```

依次执行这些命令，就将本地中的 .fun/nas/auto-default 中的第三方代码包和模型文件传到 nas 中, 依次看下这几个命令的做了什么事情:

- fun nas init : 初始化nas, 基于您的 .env 中的信息获取(已有满足条件的nas)或创建一个同region可用的nas
- fun nas info : 可以查看本地 nas 的目录位置, 对于此工程 `$(pwd)/.fun/nas/auto-default/classify`
- fun nas sync : 将本地nas中的内容（.fun/nas/auto-default/classify）上传到 nas 中的 classify 目录
- fun nas ls nas://classify:/mnt/auto/ : 查看我们是否已经正确将文件上传到了 NAS

> 这些步骤成功执行后，对于函数计算执行环境来说， 此时 `/mnt/auto/` 中内容就是 nas 中的 `classify` 目录中的内容， 即本地中的 `.fun/nas/auto-default/classify` 的内容

#### 5. fun deploy 部署函数到指定的region

修改 template.yml LogConfig 中的 Project, 任意取一个不会重复的名字即可， 然后执行

```bash
fun deploy
```

> 注: template.yml 注释的部分为自定义域名的配置, 如果想在 fun deploy 中完成这个部署工作:
  - 先去[域名解析](dc.console.aliyun.com), 如在示例中, 将域名 `sz.mofangdegisn.cn` 解析到 `123456.cn-hangzhou.fc.aliyuncs.com`, 对应的accountId 和 region 修改成自己实际的

  - 去掉 template.yml 中的注释, 修改成自己的域名

  - 执行 `fun deploy`

## TODO
...