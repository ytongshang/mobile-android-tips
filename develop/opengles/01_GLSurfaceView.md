# OpenGLES

## GLSurfaceView

### 设定OpenGL的版本

```java
if (GLUtils.hasGLES20(this)) {
    mSurfaceView.setEGLContextClientVersion(2);
} else {
    // 不支持opengles 2.0
}

public static boolean hasGLES20(Context context) {
    ActivityManager am = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
    ConfigurationInfo info = am.getDeviceConfigurationInfo();
    return info.reqGlEsVersion >= 0x20000;
}
```

### onResume与onPause

- 必须要设置了GLSurfaceView.Renderer才能调用
- **onResume**一般在Activity的**onStart**中调用
- **onPause**一般在Activity的**onStop**中调用

## GLSurfaceView.Renderer

- Renderer是被GLSurfaceView调用的。
- Renderer的方法是运行在一个单独线程rendering thread的，而非main thread。
- 默认情况下，GLSurfaceView会以display的refresh rate不停的进行render，但是我们也可以将其配置成触发刷新，用到的api  是GLSurfaceView.setRenderMode(RENDERMODE_WHEN_DIRTY)

```java
public interface Renderer {
    void onSurfaceCreated(GL10 gl, EGLConfig config);

    void onSurfaceChanged(GL10 gl, int width, int height);

    void onDrawFrame(GL10 gl);
}
```

### onSurfaceCreated

- 当SurfaceView创建或重新创建时会调用，当OpenGl的上下文丢失，重新开始渲染时会调用
- 当OpenGl的上下文丢失时，我们不需要调用glDelete去删除OpenGL相关的资源
- 一般在这个方法设置一些绘制时不常变化的参数，比如：背景色，是否打开 z-buffer等

### onSurfaceChanged

- 在Surface的大小变化时调用
- 一般在这里设置ViewPort
- 如果Camera是固定的话，也可以在这里设置Projection

### onDrawFrame

- 定义了实际的绘图操作