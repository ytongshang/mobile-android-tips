# SurfaceView GLSurfaceView SurfaceTexture TextureView

-   [Android 5.0(Lollipop)中的 SurfaceTexture，TextureView, SurfaceView 和 GLSurfaceView](https://blog.csdn.net/jinzhuojun/article/details/44062175)
-   [视频画面帧的展示控件 SurfaceView 及 TextureView 对比](https://www.jianshu.com/p/b9a1e66e95ea)

## SurfaceView

-   虽然在 App 端它仍在 View hierachy 中，但在 Server 端（WMS 和 SF）中，它与宿主窗口是分离的。在 wms 有自己的 WindowState, 在 surfaceFlinger 有自己的 layer
-   整个 Surface 的渲染可以放到单独线程去做，渲染时可以有自己的 GL context
-   双缓冲
-   Surface 不在 View hierachy 中，它的显示也不受 View 的属性控制，所以不能进行平移，缩放等变换
-   setZOrderOnTop，设置 surfaceView 的 window 是否在原先 window 的最上面
-   setZOrderMediaOverlay，设置 surfaceView 是否放置在另一个 surfaceView 上面，常见的比如 SurfaceView 的弹幕需要设置这个属性

## GLSurfaceView

-   继承 SurfaceView
-   它可以看作是 SurfaceView 的一种典型使用模式。
-   **在 SurfaceView 的基础上，它加入了 EGL 的管理，并自带了渲染线程**
-   另外它定义了用户需要实现的 Render 接口，提供了用 Strategy pattern 更改具体 Render 行为的灵活性。作为 GLSurfaceView 的 Client，只需要将实现了渲染函数的 Renderer 的实现类设置给 GLSurfaceView 即可

## TextureView

-   和 SurfaceView 不同，它不会在 WMS 中单独创建窗口，而是作为 View hierachy 中的一个普通 View，因此可以和其它普通 View 一样进行移动，旋转，缩放，动画等变化
-   TextureView 必须在硬件加速的窗口中
-   由于失效(invalidation)和缓冲的特性，TextureView 相比较于 SurfaceView 增加了额外 1~3 帧的延迟显示画面更新
-   TextureView 总是使用 GL 合成，而 SurfaceView 可以使用硬件 overlay 后端，可以占用更少的内存带宽，消耗更少的能量
-   TextureView 的内部缓冲队列导致比 SurfaceView 使用更多的内存
