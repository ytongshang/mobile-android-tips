# Fresco

## 解码器

-   Android 8.0 及以上使用系统的，bitmap 数据保存在 native
-   Android 5.0~Android8.0 使用系统的，bitmap 数据保存在 java 堆好
-   Android 4.4 也保存在了 java 堆上，但是使用了 pool 减少内存的分配
-   Android 2.3-Android 4.4 Bitmap 缓存位于匿名共享内存,Android 中操作匿名共享内存对应的类是 MemoryFile，将 bitmap 的数据拷贝到 memoryFile 中，然后用 file descriptor 解析图片

```java
// com.facebook.imagepipeline.platform.PlatformDecoderFactory.java
public static PlatformDecoder buildPlatformDecoder(
      PoolFactory poolFactory, boolean gingerbreadDecoderEnabled) {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
      int maxNumThreads = poolFactory.getFlexByteArrayPoolMaxNumThreads();
      return new OreoDecoder(
          poolFactory.getBitmapPool(), maxNumThreads, new Pools.SynchronizedPool<>(maxNumThreads));
    } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
      int maxNumThreads = poolFactory.getFlexByteArrayPoolMaxNumThreads();
      return new ArtDecoder(
          poolFactory.getBitmapPool(), maxNumThreads, new Pools.SynchronizedPool<>(maxNumThreads));
    } else {
      if (gingerbreadDecoderEnabled && Build.VERSION.SDK_INT < Build.VERSION_CODES.KITKAT) {
        return new GingerbreadPurgeableDecoder();
      } else {
        return new KitKatPurgeableDecoder(poolFactory.getFlexByteArrayPool());
      }
    }
  }
```
