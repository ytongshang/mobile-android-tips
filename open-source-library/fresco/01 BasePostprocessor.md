# BaseProcessor

[修改图片](https://www.fresco-cn.org/docs/modifying-image.html)

- 图片在进入后处理器(postprocessor)的图片是原图的一个完整拷贝，原来的图片不受修改的影响
- 在开始一个图片显示时，即使是反复显示同一个图片，在每次进行显示时，都需要指定后处理器。对于同一个图片，每次显示可以使用不同的后处理器
- 后处理器现在不支持 动图加载

## 图片大小变化

- 默认经过后处理器处理后的图片的大小与原图的大小相同，如果不相同，重写重写下面的方法

```java
@Override
  public CloseableReference<Bitmap> process(
      Bitmap sourceBitmap,
      PlatformBitmapFactory bitmapFactory) {
    final Bitmap.Config sourceBitmapConfig = sourceBitmap.getConfig();
    CloseableReference<Bitmap> destBitmapRef =
        bitmapFactory.createBitmapInternal(
            // 设置成我们想要的宽度，默认与原图相同
            sourceBitmap.getWidth(),
            // 设置成我们想要的高度，默认与原图相同
            sourceBitmap.getHeight(),
            sourceBitmapConfig != null ? sourceBitmapConfig : FALLBACK_BITMAP_CONFIGURATION);
    try {
      process(destBitmapRef.get(), sourceBitmap);
      return CloseableReference.cloneOrNull(destBitmapRef);
    } finally {
      CloseableReference.closeSafely(destBitmapRef);
    }
  }
```

## 图片处理

- 对图片具体处理时，我们需要重载下面两个方法中的一个

```java
  public void process(Bitmap destBitmap, Bitmap sourceBitmap) {
    internalCopyBitmap(destBitmap, sourceBitmap);
    process(destBitmap);
  }
  
  public void process(Bitmap bitmap) {
  }
```

## 处理后缓存

- 你可以选择性地缓存后处理器的输出结果。它会和原始图片一起放在缓存里。
- 如果要这样做，你的后处理器必须实现 getPostprocessorCacheKey 方法，并返回一个非空的结果。
- 为实现缓存命中，随后的请求中使用的后处理器必须是同一个类并返回同样的键。否则，它的返回结果将会覆盖之前缓存的条目

```java
  // 默认实现为null
  @Override
  @Nullable
  public CacheKey getPostprocessorCacheKey() {
    return null;
  }
```

## 多次处理图片

- 继承BaseRepeatedPostprocessor


## 处理

- 聊天的气泡效果

```java
/**
 * Created by Rancune@126.com on 2017/6/6.
 */

public class BubbleProcessor extends BasePostprocessor {
    private static final String BUBBLE_PROCESSOR = "BubbleProcessor";
    private static final int DEFAULT_SIZE = 300;

    private BubbleParams mParams;
    private int mWidth = DEFAULT_SIZE;
    private int mHeight = DEFAULT_SIZE;

    private CacheKey mCacheKey;

    private static final SparseArray<WeakReference<Bitmap>> sCache = new SparseArray<>();

    public BubbleProcessor(BubbleParams params, int width, int height) {
        mParams = params;
        mWidth = width <= 0 ? DEFAULT_SIZE : width;
        mHeight = height <= 0 ? DEFAULT_SIZE : height;
    }

    @Override
    public String getName() {
        return BUBBLE_PROCESSOR;
    }

    @Override
    public CloseableReference<Bitmap> process(Bitmap sourceBitmap, PlatformBitmapFactory bitmapFactory) {
        final Bitmap.Config sourceBitmapConfig = sourceBitmap.getConfig();
        CloseableReference<Bitmap> destBitmapRef =
                bitmapFactory.createBitmapInternal(
                        mWidth,
                        mHeight,
                        sourceBitmapConfig != null ? sourceBitmapConfig : FALLBACK_BITMAP_CONFIGURATION);
        try {
            process(destBitmapRef.get(), sourceBitmap);
            return CloseableReference.cloneOrNull(destBitmapRef);
        } finally {
            CloseableReference.closeSafely(destBitmapRef);
        }
    }

    @Override
    public void process(Bitmap destBitmap, Bitmap sourceBitmap) {
        Canvas mCanvas = new Canvas(destBitmap);
        Rect rect = new Rect(0, 0, mWidth, mHeight);
        Rect rectF;
        if (sourceBitmap.getHeight() / sourceBitmap.getWidth() > 3) {
            int top = (sourceBitmap.getHeight() - 3 * sourceBitmap.getWidth()) / 2;
            rectF = new Rect(0, top, sourceBitmap.getWidth(), top + 3 * sourceBitmap.getWidth());
        } else if (sourceBitmap.getWidth() / sourceBitmap.getHeight() > 3) {
            int left = (sourceBitmap.getWidth() - 3 * sourceBitmap.getHeight()) / 2;
            rectF = new Rect(left, 0, left + sourceBitmap.getHeight() * 3, sourceBitmap.getHeight());
        } else {
            rectF = new Rect(0, 0, sourceBitmap.getWidth(), sourceBitmap.getHeight());
        }

        // Perform the bubble
        Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        paint.setXfermode(new PorterDuffXfermode(PorterDuff.Mode.DST_IN));
        mCanvas.drawBitmap(sourceBitmap, rectF, rect, null);

        Bitmap bubble_TL = getBitmap(mParams.bubble_top_left);
        Rect src_TL = new Rect(0, 0, bubble_TL.getWidth(), bubble_TL.getHeight());
        Rect dst_TL = new Rect(0, 0, bubble_TL.getWidth(), bubble_TL.getHeight());
        mCanvas.drawBitmap(bubble_TL, src_TL, dst_TL, paint);

        Bitmap bubble_BL = getBitmap(mParams.bubble_bottom_left);
        Rect src_BL = new Rect(0, 0, bubble_BL.getWidth(), bubble_BL.getHeight());
        Rect dst_BL = new Rect(0, mHeight - bubble_BL.getHeight(), bubble_BL.getWidth(), mHeight);
        mCanvas.drawBitmap(bubble_BL, src_BL, dst_BL, paint);

        Bitmap bubble_L = getBitmap(mParams.bubble_left);
        Rect src_left = new Rect(0, 0, bubble_L.getWidth(), bubble_L.getHeight());
        Rect dst_left = new Rect(0, bubble_TL.getHeight(), bubble_L.getWidth(), mHeight - bubble_BL.getHeight());
        mCanvas.drawBitmap(bubble_L, src_left, dst_left, paint);

        Bitmap bubble_TR = getBitmap(mParams.bubble_top_right);
        Rect src_TR = new Rect(0, 0, bubble_TR.getWidth(), bubble_TR.getHeight());
        Rect dst_TR = new Rect(mWidth - bubble_TR.getWidth(), 0, mWidth, bubble_TR.getHeight());
        mCanvas.drawBitmap(bubble_TR, src_TR, dst_TR, paint);

        Bitmap bubble_BR = getBitmap(mParams.bubble_bottom_right);
        Rect src_BR = new Rect(0, 0, bubble_BR.getWidth(), bubble_BR.getHeight());
        Rect dst_BR = new Rect(mWidth - bubble_BR.getWidth(), mHeight - bubble_BR.getHeight(), mWidth, mHeight);
        mCanvas.drawBitmap(bubble_BR, src_BR, dst_BR, paint);

        Bitmap bubble_R = getBitmap(mParams.bubble_right);
        Rect src_right = new Rect(0, 0, bubble_R.getWidth(), bubble_R.getHeight());
        Rect dst_right = new Rect(mWidth - bubble_R.getWidth(), bubble_TR.getHeight(), mWidth, mHeight - bubble_BR.getHeight());
        mCanvas.drawBitmap(bubble_R, src_right, dst_right, paint);

        // Draw border
        paint.setXfermode(new PorterDuffXfermode(PorterDuff.Mode.SRC_OVER));
        Bitmap border_TL = getBitmap(mParams.border_top_left);
        Rect border_src = new Rect(0, 0, border_TL.getWidth(), border_TL.getHeight());
        Rect image_dst = new Rect(0, 0, border_TL.getWidth(), border_TL.getHeight());
        mCanvas.drawBitmap(border_TL, border_src, image_dst, paint);

        Bitmap border_BL = getBitmap(mParams.border_bottom_left);
        Rect border_src_BL = new Rect(0, 0, border_BL.getWidth(), border_BL.getHeight());
        Rect border_dst_BL = new Rect(0, mHeight - border_BL.getHeight(), border_BL.getWidth(), mHeight);
        mCanvas.drawBitmap(border_BL, border_src_BL, border_dst_BL, paint);

        Bitmap border_Line_L = getBitmap(mParams.border_left);
        Rect border_src_left = new Rect(0, 0, border_Line_L.getWidth(), border_Line_L.getHeight());
        Rect border_dst_left = new Rect(0, border_TL.getHeight(), border_Line_L.getWidth(), mHeight - border_BL.getHeight());
        mCanvas.drawBitmap(border_Line_L, border_src_left, border_dst_left, paint);

        Bitmap border_TR = getBitmap(mParams.border_top_right);
        Rect border_src_TR = new Rect(0, 0, bubble_TR.getWidth(), bubble_TR.getHeight());
        Rect border_dst_TR = new Rect(mWidth - border_TR.getWidth(), 0, mWidth, border_TR.getHeight());
        mCanvas.drawBitmap(border_TR, border_src_TR, border_dst_TR, paint);

        Bitmap border_BR = getBitmap(mParams.border_bottom_right);
        Rect border_src_BR = new Rect(0, 0, bubble_BR.getWidth(), bubble_BR.getHeight());
        Rect border_dst_BR = new Rect(mWidth - border_BR.getWidth(), mHeight - border_BR.getHeight(), mWidth, mHeight);
        mCanvas.drawBitmap(border_BR, border_src_BR, border_dst_BR, paint);

        Bitmap border_Line_R = getBitmap(mParams.border_right);
        Rect border_src_Right = new Rect(0, 0, border_Line_R.getWidth(), border_Line_R.getHeight());
        Rect border_dst_Right = new Rect(mWidth - border_Line_R.getWidth(), border_TR.getHeight(),
                mWidth, mHeight - border_BR.getHeight());
        mCanvas.drawBitmap(border_Line_R, border_src_Right, border_dst_Right, paint);

        Bitmap border_Line_TB = getBitmap(mParams.border_top);
        Rect border_src_tb = new Rect(0, 0, border_Line_TB.getWidth(), border_Line_TB.getHeight());
        Rect border_dst_top = new Rect(border_TL.getWidth(), 0, mWidth - border_TR.getWidth(),
                border_Line_TB.getHeight());
        mCanvas.drawBitmap(border_Line_TB, border_src_tb, border_dst_top, paint);

        Rect border_dst_bottom =
                new Rect(border_BL.getWidth(), mHeight - border_Line_TB.getHeight(),
                        mWidth - border_BR.getWidth(), mHeight);
        mCanvas.drawBitmap(border_Line_TB, border_src_tb, border_dst_bottom, paint);

        paint.setXfermode(null);

    }

    @Override
    public CacheKey getPostprocessorCacheKey() {
        if (mCacheKey == null) {
            final String key = String.format((Locale) null, "%s%d%d", mParams.key, mWidth, mHeight);
            mCacheKey = new SimpleCacheKey(key);
        }
        return mCacheKey;
    }

    private Bitmap getBitmap(@DrawableRes int bitmapRes) {
        if (bitmapRes <= 0) {
            return null;
        }
        synchronized (sCache) {
            WeakReference<Bitmap> reference = sCache.get(bitmapRes);
            if (reference != null && reference.get() != null) {
                return reference.get();
            } else {
                Bitmap bitmap = BitmapFactory.decodeResource(Utils.mContext.getResources(), bitmapRes);
                sCache.put(bitmapRes, new WeakReference<>(bitmap));
                return bitmap;
            }
        }
    }
}

```
