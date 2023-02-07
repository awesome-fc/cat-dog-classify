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

#### 2. 安装最新版本的 Serverless Devs 并完成配置

1. 针对 Mac/Linux 用户， 直接使用如下命令安装即可：
    ```
    $ curl -o- -L http://cli.so/install.sh | bash
    ```
    > 更多请参考 [s 安装手册](https://docs.serverless-devs.com/serverless-devs/install)

2. [s 配置](https://docs.serverless-devs.com/serverless-devs/quick_start#%E5%AF%86%E9%92%A5%E9%85%8D%E7%BD%AE)

#### 3. s 安装依赖

- 如果开发机器没有安装docker，请先安装[docker](https://www.docker.com/products/docker-desktop)以拉取函数计算环境的镜像

- 根据代码导入的包，构建 Python 依赖安装文件 `requirements.txt`

- 执行 `s build --use-docker` （s 工具自动进行相关的依赖包的安装,
将第三方库下载到 `.s/build/artifacts/cat-dog/classify/.s/python` 目录下）

从这里我们看出， 函数计算引用的代码包解压之后已经超过 100M 代码包限制, 解决方案是 NAS，
我们将大体积的依赖和相对较大的模型参数文件放入 NAS，从而达到减少代码包体积的目的。

#### 4. 将下载的依赖的代码包上传到 NAS

- 由于我们使用了 `auto` 的 NAS 配置，在上传文件前我们需要先初始化 NAS

```bash
s nas init
```

- 分别将依赖和模型上传到 NAS，并查看 NAS 远程目录：

``` bash
s nas upload -r .s/build/artifacts/cat-dog/classify/.s/python/ /mnt/auto/python
s nas upload -r src/model/ /mnt/auto/model
s nas command ls /mnt/auto/
```

#### 5. 部署函数到指定的region

```bash
s deploy
```

之后就可以使用部署产生的自定义域名的 url 在浏览器中访问：

![](https://img.alicdn.com/imgextra/i2/O1CN01oMwtse1CjAdnZnHEV_!!6000000000116-2-tps-980-54.png)

## 使用预留消除冷启动毛刺

[预留操作视频教学示例](https://fc-hz-demo.oss-cn-hangzhou.aliyuncs.com/video/provision.mp4)

函数计算具有动态伸缩的特性， 根据并发请求量，自动弹性扩容出执行环境来执行环境。在这个典型的深度学习示例中，加载依赖和模型参数消耗的时间很长 ， 在我们设置的 1 G 规格的函数中， 并发访问的时候时间10s左右， 有时甚至20s+

> 注：一般加载模型时间长, 本示例中模型较小, 但是也可以体现深度学习使用场景的中初始化过程时间很长

因此这个会不可避免出现函数调用毛刺情况出现(冷启动时间10s+)，在这种情况下，我们使用**设置预留**的方式来避免冷启动。利用 s 工具中，只需要简单地执行：

```bash
s provision put --target 10 --qualifier LATEST
```

 以下函数计算执行环境进行公网压测的一个压测报告:

**压测参数:**

<img src="pressureTest/PT0.jpg?raw=true" width="800">
<img src="pressureTest/PT1.jpg?raw=true" width="800">

**压测结果:**

<img src="pressureTest/PT2.jpg?raw=true" width="800">
<img src="pressureTest/PT3.jpg?raw=true" width="800">

**函数执行详情:**
<img src="pressureTest/fc2.jpg?raw=true" width="800">
<img src="pressureTest/fc3.jpg?raw=true" width="800">

从上面图中我们可以看出，当函数执行的请求到来时，优先被调度到预留的实例中被执行， 这个时候是没有冷启动的，所以请求是没有毛刺的， 后面随着测试的压力不断增大(峰值TPS 达到 1184), 预留的实例不能满足调用函数的请求， 这个时候函数计算就自动进行按需扩容实例供函数执行，此时的调用就有冷启动的过程， 从上面我们可以看出， 函数的最大 latency 时间甚至达到了 32s，如果这个 web API 是延时敏感的，这个 latency 是不可接受的。

### 结论
1. 函数计算具有自动伸缩扩容能力
2. 预留模式很好地解决了冷启动中的毛刺问题
3. 开发简单易上手，只需要关注具体的代码逻辑， s 工具助您一键式部署运用
4. 函数计算具有很好监控设施, 您可以可视化观察您函数运行情况， 执行时间、内存、调用次数等信息
