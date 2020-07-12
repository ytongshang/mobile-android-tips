# APK瘦身

## APK打包的流程

- ![apk打包流程](./../../image-resources/performance/apk打包流程.jpg)

- AAPT(Android Asset Packaging Tool)工具会打包应用中的资源文件，如AndroidManifest.xml、layout布局中的xml等，并将xml文件编译为二进制形式，当然assets文件夹中的文件不会被编译，图片及raw文件夹中的资源也会保持原来的形态，需要注意的是raw文件夹中的资源也会生成资源id。AAPT编译完成之后会生成R.java文件。
- AIDL工具会将所有的aidl接口转化为java接口。
- 所有的java代码，包括R.java与aidl文件都会被Java编译器编译成.class文件。
- Dex工具会将上述产生的.class文件及第三库及其他.class文件编译成.dex文件（dex文件是Dalvik虚拟机可以执行的格式），dex文件最终会被打包进APK文件。
- ApkBuilder工具会将编译过的资源及未编译过的资源（如图片等）以及.dex文件打包成APK文件。
- 生成APK文件后，需要对其签名才可安装到设备，平时测试时会使用debug keystore，当正式发布应用时必须使用release版的keystore对应用进行签名。
- 如果对APK正式签名，还需要使用zipalign工具对APK进行对齐操作，好处是可以减少运行应用时消耗的 RAM 容量

## 瘦身

- [使用 APK Analyzer 分析你的 APK](https://www.cnblogs.com/yuezhusust/p/6905065.html)
- [Android APK 瘦身 - JOOX Music项目实战](https://zhuanlan.zhihu.com/p/26772897?utm_medium=social&utm_source=weibo)
- [Android性能优化之APK瘦身详解(瘦身73%)](https://www.jianshu.com/p/fee82949ff84)
- Android Stuido使用Analyze app，查看各部分的大小

### 资源

- lint查找没使用的资源，assets确定没有用不上的文件
- aapt会对png进行优化，但是在此之前还可以使用其他工具如tinypng对图片进行进一步的压缩预处理，
- jpeg,png,webp的选择
    - 不需要alpha的转换为jpeg
    - webp优选，解码与png速度差不多，大小小很多
    - 转webp时，png先转jpeg,然后转webp，否则可能有alpha通道
- 尽量不要使用帧动画，使用svga,lottie
- 有选择性的提供hdpi，xhdpi，xxhdpi的图片资源。建议优先提供xhdpi的图片，对于mdpi，ldpi与xxxhdpi根据需要提供有差异的部分即可
- 是否图片资源可以用代码替换
- 是否可以替换成网络资源
- gradle开启shrinkResources
- 资源混淆，微信开源的资源混淆

### so

- native code的部分，现在大部分应当只用支持armabi-v7a
- 抽取出一个精简的第三方库,比如简减的ffmpeg
- 非必须的so可以放到服务器下载，动态加载

### chasses.dex

- 尽量减少第三方库的引用
    - 保持良好的编程习惯，不要重复或者不用的代码，谨慎添加libs，移除使用不到的libs
    - 做sdk的时候，是否可以使用宿主的公共类，比如播放器，针对接口编程，采用现在的基础模块实现
    - 是否引入了相同的功能库，比如图片加载库，特别是引用第三方库的时候
    - 减少第三方的SDK升级或JAR更换来减小APK大小
    - 第三方的JAR包时，你只想用它一丢丢功能，而且这部分功能的实现代码只有一点点，将我们需要的代码部分提取出来，并重新生成jar再导入我们的工程中
- 避免重复造轮子，基础组件的沉淀
- 混淆

### 插件化

## 进阶

### 资源相关

- [包体积优化（下）：资源优化的进阶实践](https://time.geekbang.org/column/article/81483)

#### 资源混淆

- resources.arsc。因为资源索引文件 resources.arsc 需要记录资源文件的名称与路径，使用混淆后的短路径 res/s/a，可以减少整个文件的大小
- metadata 签名文件。签名文件 MF 与 SF都需要记录所有文件的路径以及它们的哈希值，使用短路径可以减少这两个文件的大小

#### 资源压缩

- 更高的压缩率。虽然我们使用的还是 Zip 算法，但是利用了 7-Zip 的大字典优化，APK 的整体压缩率可以提升 3% 左右
- 压缩更多的文件。Android 编译过程中，下面这些格式的文件会指定不压缩；在 AndResGuard 中，我们支持针对 resources.arsc、PNG、JPG 以及 GIF 等文件的强制压缩