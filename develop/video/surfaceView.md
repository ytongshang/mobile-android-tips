# SurfaceView GLSurfaceView  SurfaceTexture TextureView

## SurfaceView

- 在wms有自己的WindowState, 在surfaceFlinger有自己的layer
- 虽然在App端它仍在View hierachy中，但在Server端（WMS和SF）中，它与宿主窗口是分离的。这样的好处是对这个Surface的渲染可以放到单独线程去做，渲染时可以有自己的GL context
- Surface不在View hierachy中，它的显示也不受View的属性控制，所以不能进行平移，缩放等变换
- setZOrderOnTop，设置surfaceView的window是否在原先window的最上面
- setZOrderMediaOverlay，设置surfaceView是否放置在另一个surfaceView上面，常见的比如SurfaceView的弹幕需要设置这个属性

## GLSurfaceView

- 继承SurfaceView
- 它可以看作是SurfaceView的一种典型使用模式。
- **在SurfaceView的基础上，它加入了EGL的管理，并自带了渲染线程**
- 另外它定义了用户需要实现的Render接口，提供了用Strategy pattern更改具体Render行为的灵活性。作为GLSurfaceView的Client，只需要将实现了渲染函数的Renderer的实现类设置给GLSurfaceView即可
