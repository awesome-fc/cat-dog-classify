# Dog-Cat Classifier

Dog and cat image classifier with deep learning.

## Example:
| <img src="test_dog.jpg?raw=true" width="170">|<img src="test_cat.jpg?raw=true" width="200">|
|:-:|:-:|
|Dog: 0.9634414<br/>Cat: 0.01574309|Cat: 0.9599058<br/>Dog: 0.0357831|

[http://sz.mofangdegisn.cn](http://sz.mofangdegisn.cn)

## Test Picture
[dog.jpg](https://raw.githubusercontent.com/awesome-fc/cat-dog-classify/master/test_dog.jpg)  |  [cat.jpg](https://raw.githubusercontent.com/awesome-fc/cat-dog-classify/master/test_cat.jpg)

## 基于Serverless Devs的函数计算部署

#### 准备工作

[免费开通函数计算](https://statistics.functioncompute.com/?title=ServerlessAI&theme=ServerlessAI&author=rsong&src=article&url=http://fc.console.aliyun.com) ，按量付费，函数计算有很大的免费额度。

[免费开通文件存储服务NAS](https://nas.console.aliyun.com/)， 按量付费

#### 1. clone 该工程

```bash
git clone https://github.com/awesome-fc/cat-dog-classify.git
```

#### 2. 安装最新版本的 Serverless Devs

[s 安装手册](https://www.serverless-devs.com/docs/install)

#### 3. s 安装依赖包

如果开发机器没有安装docker，请先安装[docker](https://www.docker.com/products/docker-desktop)以拉取函数计算环境的镜像

执行 `s build --use-docker`, s 工具会根据 `requirements.txt` 进行相关的依赖包的安装,
将第三方库下载到 `.s/build/artifacts/cat-dog/classify/.s/python` 目录下

从这里我们看出， 函数计算引用的代码包解压之后已经超过 100M 代码包限制, 解决方案是 NAS，
我们将大体积的依赖和相对较大的模型参数文件放入 NAS，从而达到减少代码包体积的目的。

#### 4. 将下载的依赖的代码包上传到 nas

``` bash
s nas upload -r .s/build/artifacts/cat-dog/classify/.s/python nas:///mnt/auto/python
s nas upload -r model nas:///mnt/auto/model
s nas command ls nas:///mnt/auto/
```

依次执行这些命令，就将本地的第三方代码包和模型文件传到 nas 中，同时，我们仍需要手动删去本地依赖。

#### 5. 部署函数到指定的region

```bash
s deploy
```

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