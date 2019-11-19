# Dog-Cat Classifier

Dog and cat image classifier with deep learning.

## Example:
| <img src="test_dog.jpg?raw=true" width="170">|<img src="test_cat.jpg?raw=true" width="200">|
|:-:|:-:|
|Dog: 0.9634414<br/>Cat: 0.01574309|Cat: 0.9599058<br/>Dog: 0.0357831|

[http://sz.mofangdegisn.cn](http://sz.mofangdegisn.cn)

## Test Picture
[dog.jpg](https://raw.githubusercontent.com/awesome-fc/cat-dog-classify/master/test_dog.jpg)  |  [cat.jpg](https://raw.githubusercontent.com/awesome-fc/cat-dog-classify/master/test_cat.jpg)

## 部署到函数计算

**Reference:**
- [开发函数计算的正确姿势——tensorflow serving](https://yq.aliyun.com/articles/702739)

- [开发函数计算的正确姿势 —— Fun 自动化 NAS 配置](https://yq.aliyun.com/articles/712693)

- [开发函数计算的正确姿势 —— 使用 Fun NAS 管理 NAS 资源](https://yq.aliyun.com/articles/712700)

#### 准备工作

[免费开通函数计算](http://statistics.cn-shanghai.1221968287646227.cname-test.fc.aliyun-inc.com/?title=ServerlessAI&theme=ServerlessAI&author=rsong&type=click&url=http://fc.console.aliyun.com) ，按量付费，函数计算有很大的免费额度。

[免费开通文件存储服务NAS](https://nas.console.aliyun.com/)， 按量付费

#### 1. clone 该工程

```bash
git clone https://github.com/awesome-fc/cat-dog-classify.git
```

复制 `.env_example` 文件为 `.env`, 并且修改 `.env` 中的信息为自己的信息

#### 2. 安装最新版本的 fun
[fun 安装手册](https://github.com/alibaba/funcraft/blob/master/docs/usage/installation-zh.md)

#### 3. fun 安装依赖包
执行 `fun install -v`, fun 会根据 Funfile 中定义的逻辑安装相关的依赖包

```bash
root@66fb3ad27a4c: ls .fun/nas/auto-default/classify
model  python
root@66fb3ad27a4c: du -sm .fun
697     .fun
```

根据 Funfile 的定义, 将第三方库下载到 `.fun/nas/auto-default/classify/python` 目录下
本地 model 目录移到 `.fun/nas/auto-default/model` 目录下

从这里我们看出， 函数计算引用的代码包解压之后已经达到了 670 M, 远超过 50M 代码包限制, 解决方案是 NAS
详情可以参考: [挂载NAS访问](https://help.aliyun.com/document_detail/87401.html), 幸运的是 fun 工具一键解决了 nas 的配置和文件上传问题.

#### 4. 将下载的依赖的代码包上传到 nas

``` bash
fun nas sync
fun nas ls nas:///mnt/auto/
```

依次执行这些命令，就将本地中的 .fun/nas/auto-default 中的第三方代码包和模型文件传到 nas 中, 依次看下这几个命令的做了什么事情:

- fun nas sync : 将本地nas中的内容（.fun/nas/auto-default/classify）上传到 nas 中的 classify 目录
- fun nas ls nas:///mnt/auto/ : 查看我们是否已经正确将文件上传到了 NAS

> 这些步骤成功执行后，对于函数计算执行环境来说， 此时 `/mnt/auto/` 中内容就是 nas 中的 `classify` 目录中的内容， 即本地中的 `.fun/nas/auto-default/classify` 的内容

#### 5. fun deploy 部署函数到指定的region

修改 template.yml LogConfig 中的 Project, 任意取一个不会重复的名字即可，有两处需要同时一起修改，然后执行

```bash
fun deploy
```

> 注: template.yml 注释的部分为自定义域名的配置, 如果想在 fun deploy 中完成这个部署工作:
  - 先去[域名解析](https://dc.console.aliyun.com), 如在示例中, 将域名 `sz.mofangdegisn.cn` 解析到 `123456.cn-hangzhou.fc.aliyuncs.com`, 对应的域名、accountId 和 region 修改成自己的

  - 去掉 template.yml 中的注释, 修改成自己的域名

  - 执行 `fun deploy`

[Fun操作视频教学示例](https://fc-hz-demo.oss-cn-hangzhou.aliyuncs.com/video/fun.mp4)

## 使用预留消除冷启动毛刺

[预留操作视频教学示例](https://fc-hz-demo.oss-cn-hangzhou.aliyuncs.com/video/provision.mp4)

函数计算具有动态伸缩的特性， 根据并发请求量，自动弹性扩容出执行环境来执行环境，在这个典型的深度学习示例中，import keras 消耗的时间很长 ， 在我们设置的 1 G 规格的函数中， 并发访问的时候时间10s左右， 有时甚至20s+

> 注：一般加载模型时间长, 本示例中模型较小, 但是也可以体现深度学习使用场景的中 init 过程时间很长

```
start = time.time()
from keras.models import model_from_json
print("import keras time = ", time.time()-start)
```

因此这个会不可避免出现函数调用毛刺情况出现(冷启动时间10s+), 以下函数计算执行环境进行公网压测的一个压测报告:

**函数计算设置预留:**

- 在 [FC 控制台](https://fc.console.aliyun.com)，发布版本，并且基于该版本创建别名 `prod`

- 设置预留，基于 `prod` 预留 10 个实例
  <img src="pressureTest/fc1.jpg?raw=true" width="800">

- 将该函数的 http trigger 和 自定义域名的设置执行 `prod` 版本
  <img src="pressureTest/fc4.jpg?raw=true" width="800">
  <img src="pressureTest/fc5.jpg?raw=true" width="800">


**压测参数:**

<img src="pressureTest/PT0.jpg?raw=true" width="800">
<img src="pressureTest/PT1.jpg?raw=true" width="800">

**压测结果:**

<img src="pressureTest/PT2.jpg?raw=true" width="800">
<img src="pressureTest/PT3.jpg?raw=true" width="800">

**函数执行详情:**
<img src="pressureTest/fc2.jpg?raw=true" width="800">
<img src="pressureTest/fc3.jpg?raw=true" width="800">

从上面图中我们可以看出，当函数执行的请求到来时，优先被调度到预留的实例中被执行， 这个时候是没有冷启动的，所以请求是没有毛刺的， 后面随着测试的压力不断增大(峰值TPS 达到 1184), 预留的实例不能满足调用函数的请求， 这个时候函数计算就自动进行按需扩容实例供函数执行，此时的调用就有冷启动的过程， 从上面我们可以看出， 函数的最大 latency 时间甚至达到了 32s，如果这个 web API是延时敏感的，这个 latency 是不可接受的。

### 结论
1. 函数计算具有自动伸缩扩容能力
2. 预留模式很好地解决了冷启动中的毛刺问题
3. 开发简单易上手，只需要关注具体的代码逻辑， Fun 工具助您一键式部署运用
4. 函数计算具有很好监控设施, 您可以可视化观察您函数运行情况， 执行时间、内存、调用次数等信息