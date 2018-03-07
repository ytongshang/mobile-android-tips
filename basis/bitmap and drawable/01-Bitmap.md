# Bitmap详解

* [BitmapOptions](#bitmapoptions)
  * [BitmapOptions参数](#bitmapoptions参数)
  * [inBitmap](#inbitmap)
* [BitmapFactory](#bitmapfactory)
  * [解析方法](#解析方法)
  * [decodeResource](#decoderesource)
  * [setDensityFromOptions](#setdensityfromoptions)
  * [inDensity与inTargetDensity的应用](#indensity与intargetdensity的应用)
* [Bitmap对图像进行操作](#bitmap对图像进行操作)
  * [Bitmap裁剪, 缩放，旋转，移动](#bitmap裁剪-缩放旋转移动)
    * [裁剪](#裁剪)
    * [缩放，旋转，移动](#缩放旋转移动)
    * [注意](#注意)
  * [Bitmap其它常用函数](#bitmap其它常用函数)

## 1. BitmapOptions

### 1.1. BitmapOptions参数

| Header One | Header Two |
| :--- | :--- |
| inBitmap | 在解析Bitmap时重用该Bitmap，不过必须等大的Bitmap而且inMutable须为true |
| inMutable | 解析出的Bitmap是否可变，想通过Bitmap.setPixels修该bitmap，必须设为true,默认为false |
| inJustDecodeBounds | 为true仅返回Bitmap的宽高等属性 |
| inSampleSize | 表示Bitmap的压缩比例，如：inSampleSize=4，将返回一个是原始图的1/16大小的Bitmap |
| inPreferredConfig | Bitmap.Config.ARGB\_8888等 |
| inDither | 是否开启抖动，默认为false |
| inPremultiplied | 默认为true，如果想能过Canvas绘制直接绘制bitmap,必须设置为true |
| inDensity | Bitmap解析时的像素密度 |
| inTargetDensity | Bitmap最终的像素密度 |
| inScreenDensity | 当前屏幕的像素密度 |
| inScaled | 是否支持缩放，默认为true，当设置了这个，Bitmap将会以inTargetDensity的值进行缩放 |
| inPreferQualityOverSpeed | 设为true时，优先保证Bitmap质量其次是解码速度 |
| outWidth | 返回的Bitmap的宽，注意是经过scale的 |
| outHeight | 返回的Bitmap的高，注意是经过scale的 |
| inTempStorage | 解码时的临时空间，建议16\*1024，默认为16k |
| outMimeType | bitmap的mimeType,不设置或者解析出错时，该值为null |
| mCancel | 解析bitmap是否被取消掉了，可以通过requestCancelDecode\(\)取消bitmap的解析 |

### 1.2. inBitmap

* 假如设置了Options.inBitmap的这个字段，在解码Bitmap的时候，系统会去重用inBitmap设置的Bitmap，减少内存的分配和释放，提高了应用的性能
* **设置的inBitmap必须inMutable为true**
* 在Android 4.4之前，BitmapFactory.Options.inBitmap设置的Bitmap必须和我们需要解码的Bitmap的大小完全一致才行，
  **也就是宽高要一样，并且inSampleSize也必须为1**
* 在Android4.4以后，BitmapFactory.Options.inBitmap设置的Bitmap的getAllocationByteCount必须要大于等于能解码的Bitmap的getByteCount

[Managing Bitmap Memory](https://developer.android.com/topic/performance/graphics/manage-memory.html)

```java
// ImageCache
Set<SoftReference<Bitmap>> mReusableBitmaps;
private LruCache<String, BitmapDrawable> mMemoryCache;

// If you're running on Honeycomb or newer, create a
// synchronized HashSet of references to reusable bitmaps.
if (Utils.hasHoneycomb()) {
    mReusableBitmaps =
            Collections.synchronizedSet(new HashSet<SoftReference<Bitmap>>());
}

mMemoryCache = new LruCache<String, BitmapDrawable>(mCacheParams.memCacheSize) {

    // Notify the removed entry that is no longer being cached.
    @Override
    protected void entryRemoved(boolean evicted, String key,
            BitmapDrawable oldValue, BitmapDrawable newValue) {
        if (RecyclingBitmapDrawable.class.isInstance(oldValue)) {
            // The removed entry is a recycling drawable, so notify it
            // that it has been removed from the memory cache.
            ((RecyclingBitmapDrawable) oldValue).setIsCached(false);
        } else {
            // The removed entry is a standard BitmapDrawable.
            if (Utils.hasHoneycomb()) {
                // We're running on Honeycomb or later, so add the bitmap
                // to a SoftReference set for possible use with inBitmap later.
                mReusableBitmaps.add
                        (new SoftReference<Bitmap>(oldValue.getBitmap()));
            }
        }
    }
....
}

public static Bitmap decodeSampledBitmapFromFile(String filename,
        int reqWidth, int reqHeight, ImageCache cache) {

    final BitmapFactory.Options options = new BitmapFactory.Options();
    options.inJustDecodeBounds = true;
    ...
    BitmapFactory.decodeFile(filename, options);
    ...

    // If we're running on Honeycomb or newer, try to use inBitmap.
    if (Utils.hasHoneycomb()) {
        addInBitmapOptions(options, cache);
    }
     options.inJustDecodeBounds = false;
    ...
    return BitmapFactory.decodeFile(filename, options);
}

private static void addInBitmapOptions(BitmapFactory.Options options,
        ImageCache cache) {
    // inBitmap only works with mutable bitmaps, so force the decoder to
    // return mutable bitmaps.
    options.inMutable = true;

    if (cache != null) {
        // Try to find a bitmap to use for inBitmap.
        Bitmap inBitmap = cache.getBitmapFromReusableSet(options);

        if (inBitmap != null) {
            // If a suitable bitmap has been found, set it as the value of
            // inBitmap.
            options.inBitmap = inBitmap;
        }
    }
}

// This method iterates through the reusable bitmaps, looking for one
// to use for inBitmap:
protected Bitmap getBitmapFromReusableSet(BitmapFactory.Options options) {

    Bitmap bitmap = null;

    if (mReusableBitmaps != null && !mReusableBitmaps.isEmpty()) {
        synchronized (mReusableBitmaps) {
            final Iterator<SoftReference<Bitmap>> iterator = mReusableBitmaps.iterator();
            Bitmap item;

            while (iterator.hasNext()) {
                item = iterator.next().get();

                if (null != item && item.isMutable()) {
                    // Check to see it the item can be used for inBitmap.
                    if (canUseForInBitmap(item, options)) {
                        bitmap = item;

                        // Remove from reusable set so it can't be used again.
                        iterator.remove();
                        break;
                    }
                } else {
                    // Remove from the set if the reference has been cleared.
                    iterator.remove();
                }
            }
        }
    }
    return bitmap;
}

static boolean canUseForInBitmap( Bitmap candidate, BitmapFactory.Options targetOptions) {

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
        // From Android 4.4 (KitKat) onward we can re-use if the byte size of
        // the new bitmap is smaller than the reusable bitmap candidate
        // allocation byte count.
        int width = targetOptions.outWidth / targetOptions.inSampleSize;
        int height = targetOptions.outHeight / targetOptions.inSampleSize;
        int byteCount = width * height * getBytesPerPixel(candidate.getConfig());
        return byteCount <= candidate.getAllocationByteCount();
    }

    // On earlier versions, the dimensions must match exactly and the inSampleSize must be 1
    return candidate.getWidth() == targetOptions.outWidth
            && candidate.getHeight() == targetOptions.outHeight
            && targetOptions.inSampleSize == 1;
}

/**
 * A helper function to return the byte usage per pixel of a bitmap based on its configuration.
 */
static int getBytesPerPixel(Config config) {
    if (config == Config.ARGB_8888) {
        return 4;
    } else if (config == Config.RGB_565) {
        return 2;
    } else if (config == Config.ARGB_4444) {
        return 2;
    } else if (config == Config.ALPHA_8) {
        return 1;
    }
    return 1;
}
```

## 2. BitmapFactory

### 2.1. 解析方法

```java
Bitmap decodeFile(...)
Bitmap decodeResource(...)
Bitmap decodeByteArray(...)
Bitmap decodeStream(...)
Bitmap decodeFileDescriptor(...)
```

* 其中decodeFile与decodeResource最后都间接调用了decodeStream来解析bitmap

* 每一个方法都被重载为可以传递一个BitmapOptions的参数，这样可以根据BitmapOptions来返回对应的bitmap

### 2.2. decodeResource

* decodeResouce会间接调用decodeResourceStream

```java
public static Bitmap decodeResource(Resources res, int id, Options opts) {
    Bitmap bm = null;
    InputStream is = null;

    try {
        final TypedValue value = new TypedValue();
        is = res.openRawResource(id, value);

        bm = decodeResourceStream(res, value, is, null, opts);
    } catch (Exception e) {
        /*  do nothing.
            If the exception happened on open, bm will be null.
            If it happened on close, bm is still valid.
        */
    } finally {
        try {
            if (is != null) is.close();
        } catch (IOException e) {
                // Ignore
        }
    }

    if (bm == null && opts != null && opts.inBitmap != null) {
        throw new IllegalArgumentException("Problem decoding into existing bitmap");
    }

    return bm;
}
```

* decodeResourceStream与decodeStream最大的区别在于decodeResource如果没有BitmapFactory.Options时，会自动生成一个BitmapFactory.Options
* **其中Options的inDensity会因为图片资源的存放位置在读取时获得**，比如图片存放在xhdpi，那么它的inDensity会是320,但是从asset中读取的是没有inDensity的，所以它会使用默认的DENSITY\_DEFAULT，也就是160dpi
* 如果没有设置Options的inTargetDensity,那么inTargetDensity会是当前屏幕的density

```java
public static Bitmap decodeResourceStream(Resources res, TypedValue value,
            InputStream is, Rect pad, Options opts) {

    if (opts == null) {
        opts = new Options();
    }

    if (opts.inDensity == 0 && value != null) {
        final int density = value.density;
        if (density == TypedValue.DENSITY_DEFAULT) {
            opts.inDensity = DisplayMetrics.DENSITY_DEFAULT;
        } else if (density != TypedValue.DENSITY_NONE) {
            opts.inDensity = density;
        }
    }

    if (opts.inTargetDensity == 0 && res != null) {
        opts.inTargetDensity = res.getDisplayMetrics().densityDpi;
    }

    return decodeStream(is, pad, opts);
}
```

```java
public static Bitmap decodeStream(InputStream is, Rect outPadding, Options opts) {
        // we don't throw in this case, thus allowing the caller to only check
        // the cache, and not force the image to be decoded.
    if (is == null) {
        return null;
    }

    Bitmap bm = null;

    Trace.traceBegin(Trace.TRACE_TAG_GRAPHICS, "decodeBitmap");
    try {
        if (is instanceof AssetManager.AssetInputStream) {
            final long asset = ((AssetManager.AssetInputStream) is).getNativeAsset();
            bm = nativeDecodeAsset(asset, outPadding, opts);
        } else {
            bm = decodeStreamInternal(is, outPadding, opts);
        }

        if (bm == null && opts != null && opts.inBitmap != null) {
            throw new IllegalArgumentException("Problem decoding into existing bitmap");
        }

        setDensityFromOptions(bm, opts);
    } finally {
        Trace.traceEnd(Trace.TRACE_TAG_GRAPHICS);
    }

    return bm;
}
```

### 2.3. setDensityFromOptions

* 图片解析完成后，只要解析传入的BitmapFactory.Options不为空，就会对图片可能做scale

```java
private static void setDensityFromOptions(Bitmap outputBitmap, Options opts) {
    if (outputBitmap == null || opts == null) return;

    final int density = opts.inDensity;
    // inDensity不为0, 也就是设置了inDensity
    if (density != 0) {
        outputBitmap.setDensity(density);
        final int targetDensity = opts.inTargetDensity;
        // 如果没有设置target或者inDensity==inTargetDensity或inDensity_ == inScreenDensity相同也不会缩放
        // 一般情况下我们都只会设置inTargetDensity
        if (targetDensity == 0 || density == targetDensity || density == opts.inScreenDensity) {
            return;
        }

        byte[] np = outputBitmap.getNinePatchChunk();
        final boolean isNinePatch = np != null && NinePatch.isNinePatchChunk(np);
        // .9图一定会做缩放，
        // inScaled为true才会做缩放，当然inScaled的值的的默认值就是为true
        if (opts.inScaled || isNinePatch) {
            outputBitmap.setDensity(targetDensity);
        }
    } else if (opts.inBitmap != null) {
        // bitmap was reused, ensure density is reset
        outputBitmap.setDensity(Bitmap.getDefaultDensity());
    }
}
```

### 2.4. inDensity与inTargetDensity的应用

* 比如从文件中生成.9图,使用了开源库NinePatchDrawable

```java
try {
    BitmapFactory.Options options = new BitmapFactory.Options();
    options.inDensity = DisplayMetrics.DENSITY_MEDIUM;
    Bitmap bitmap = BitmapFactory.decodeFile(bgLocal, options);
    NinePatchDrawable drawable1 = BitmapType.getNinePatchDrawable(mResources, bitmap, null);
    drawable1.setTargetDensity(mResources.getDisplayMetrics().densityDpi);
    drawable = drawable1;
} catch (Exception e) {
    drawable = null;
}
if (drawable == null) {
    drawable = mResources.getDrawable(bgDefault);
}
```

## 3. Bitmap对图像进行操作

### 3.1. Bitmap裁剪, 缩放，旋转，移动

```java
Bitmap.createBitmap(Bitmap source, int x, int y, int width, int height,Matrix m, boolean filter);

Bitmap.createBitmap(Bitmap source, int x, int y, int width, int height) {
    return createBitmap(source, x, y, width, height, null, false);
}

Bitmap createScaledBitmap(Bitmap src, int dstWidth,int dstHeight, boolean filter)
```

#### 3.1.1. 裁剪

* x,y分别代表裁剪时，x轴和y轴的第一个像素，width，height分别表示裁剪后的图像的宽度和高度。
* 注意：x+width要小于等于source的宽度，y+height要小于等于source的高度。

#### 3.1.2. 缩放，旋转，移动

* m是一个Matrix（矩阵）对象，可以进行缩放，旋转，移动等动作
* filter为true时表示source会被过滤，仅仅当m操作不仅包含移动操作，还包含别的操作时才适用

```java
// 定义矩阵对象
 Matrix matrix = new Matrix();
// 缩放图像
matrix.postScale(0.8f, 0.9f);
// 向左旋转（逆时针旋转）45度，参数为正则向右旋转（顺时针旋转）
matrix.postRotate(-45);
//移动图像
//matrix.postTranslate(100,80);
Bitmap bitmap = Bitmap.createBitmap(source, 0, 0, source.getWidth(), source.getHeight(),   matrix, true);
```

#### 3.1.3. 注意

* 这里的矩阵变换，并不是对bitmap的颜色进行矩阵变换，如果对bitmap的颜色
  进行矩阵变化，是通过Paint来实现的

  ```java
  Canvas c = new Canvas(bitmap);
  Paint paint = new Paint();
  ColorMatrix cm = new ColorMatrix();
  cm.setSaturation(0);
  ColorMatrixColorFilter f = new ColorMatrixColorFilter(cm);
  paint.setColorFilter(f);
  c.drawBitmap(bitmap, 0, 0, paint);
  ```

## 4. Bitmap其它使用技能

### 4.1. 部分函数

```java
// 将位图的压缩到指定的OutputStream，可以理解成将Bitmap保存到文件中！
public boolean compress (Bitmap.CompressFormat format, int quality, OutputStream stream)

// 回收位图占用的内存空间，把位图标记为Dead
void recycle()

// 判断位图是否recycled
boolean isRecycled()

// 获取位图的宽度
int getWidth()

// 获取位图的高度
int getHeight()

// 图片是否可修改，如果想用setPixel修改bitmap，这个必须返回true
boolean isMutable()

// 获取指定密度转换后的图像的宽度
int getScaledWidth(Canvas canvas)

// 获取指定密度转换后的图像的高度
int getScaledHeight(Canvas canvas)
```

### 4.2. Bitmap的大小

* 如果bitmap设置了inDensity并且也设置了inTargetDensity,那么这个bitmap的大小就应当是
 **内存 = width *height *nTargetDensity/inDensity*TargetDensity/inDensity*一个像素所占的内存**

* decodeResource方法会默认使用资源所处文件夹对应密度和手机系统密度进行缩放之外

* 别的解码方法默认都不会。此时Bitmap默认占用的内存 = width*height*一个像素所占的内存

### 4.3. getByteCount()

* 在API12加入的，代表存储Bitmap的色素需要的最少内存
* **在API19以后，看bitmap占用了多大的内存空间，应当调用getAllocationByteCount()**

```java
public final int getByteCount() {
    // int result permits bitmaps up to 46,340 x 46,340
    return getRowBytes() * getHeight();
}
```

### 4.4. getAllocationByteCount()

* 在API19加入的，代表在内存中为Bitmap分配的内存大小。
* 一般情况下，getByteCount与getAllocationByteCount大小是一致的，
* 在以下情况下两者会不一样
  * 解析Bitmap时设置了inBitmap来解析更小的bitmap
  * 调用了reconfigure\(int, int, Config\)
  * 调用了setWidth\(int\)
  * setHeight\(int\)
  * setConfig\(Bitmap.Config\)}

```java
public final int getAllocationByteCount() {
    if (mBuffer == null) {
        //mBuffer代表存储Bitmap像素数据的字节数组。
        return getByteCount();
    }
    return mBuffer.length;
}
```