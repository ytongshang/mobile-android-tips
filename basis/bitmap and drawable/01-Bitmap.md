# Bitmap详解

## BitmapOptions

- BitmapOptions参数

Header One                       | Header Two
:------------------------------- | :-----------------------------------------------
inBitmap | 在解析Bitmap时重用该Bitmap，不过必须等大的Bitmap而且inMutable须为true
inMutable | 解析出的Bitmap是否可变，想通过Bitmap.setPixels修该bitmap，必须设为true,默认为false
inJustDecodeBounds | 为true仅返回Bitmap的宽高等属性
inSampleSize | 表示Bitmap的压缩比例，如：inSampleSize=4，将返回一个是原始图的1/16大小的Bitmap
inPreferredConfig | Bitmap.Config.ARGB_8888等
inDither | 是否开启抖动，默认为false
inPremultiplied | 默认为true，如果想能过Canvas绘制直接绘制bitmap,必须设置为true
inDensity | Bitmap解析时的像素密度
inTargetDensity | Bitmap最终的像素密度
inScreenDensity | 当前屏幕的像素密度
inScaled | 是否支持缩放，默认为true，当设置了这个，Bitmap将会以inTargetDensity的值进行缩放
inPreferQualityOverSpeed | 设为true时，优先保证Bitmap质量其次是解码速度
outWidth | 返回的Bitmap的宽，注意是经过scale的
outHeight | 返回的Bitmap的高，注意是经过scale的
inTempStorage | 解码时的临时空间，建议16*1024，默认为16k
outMimeType | bitmap的mimeType,不设置或者解析出错时，该值为null
mCancel | 解析bitmap是否被取消掉了，可以通过requestCancelDecode()取消bitmap的解析

## BitmapFactory

### 解析方法

```java
Bitmap decodeFile(...)
Bitmap decodeResource(...)
Bitmap decodeByteArray(...)
Bitmap decodeStream(...)
Bitmap decodeFileDescriptor(...)
```

- 其中decodeFile与decodeResource最后都间接调用了decodeStream来解析bitmap

- 每一个方法都被重载为可以传递一个BitmapOptions的参数，这样可以根据BitmapOptions来返回对应的bitmap

### decodeResource

- decodeResouce会间接调用decodeResourceStream

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

- decodeResourceStream与decodeStream最大的区别在于decodeResource如果没有BitmapFactory.Options时，会自动生成一个BitmapFactory.Options
- **其中Options的inDensity会因为图片资源的存放位置在读取时获得**，比如图片存放在xhdpi，那么它的inDensity会是320,但是从asset中读取的是没有inDensity的，所以它会使用默认的DENSITY_DEFAULT，也就是160dpi
- 如果没有设置Options的inTargetDensity,那么inTargetDensity会是当前屏幕的density

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

### setDensityFromOptions

- 图片解析完成后，只要解析传入的BitmapFactory.Options不为空，就会对图片可能做scale

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

### inDensity与inTargetDensity的应用

- 比如从文件中生成.9图,使用了开源库NinePatchDrawable

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


