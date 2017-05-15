# Drawable

## getIntrinsicWidth 与 getIntrinsicHeight

- 对于Drawable来说，getIntrinsicWidth和getIntrinsicHeight默认返回-1
- **对于BitmapDrawable来说，会返回bitmap在当前density下的的像素大小.**
 比如一张90×90的png图片放到drawable-hdpi文件夹下，那么它在dpi为320的手机上，getIntrinsicWidth和getIntrinsicHeight两个函数返回的是(320/240*100 + 0.5) =120

## ConstantState 与 mute

### ConstantState

- 每个 Drawable 类对象类都关联有一个 ConstantState 类对象，这是为了保存 Drawable 类对象的一些恒定不变的数据，如果从同一个 res 中创建的 Drawable 类对象，为了节约内存，它们会共享同一个 ConstantState 类对象。比如一个 ColorDrawable 类对象，它会关联一个 ColorState 类对象，color 的颜色值是保存在 ColorState 类对象中的。如果修改 ColorDrawable 的颜色值，会修改到 ColorState 的值，会导致和 ColorState 关联的所有的 ColorDrawable 的颜色都改变。

### Drawable mutate()

- 让当前drawable关联一个新的ConstantState对象，新的ConstantState对象是原先ConstantState的
 复制，这样修改当前drawable的属性，比如Alpha,不会对其它的来自同一资源的drawable产生影响
- **返回的仍然是当前的drawable,只是ConstantState发生了变化**

```java
//BitmapDrawable.java

@Override
public Drawable mutate() {
    if (!mMutated && super.mutate() == this) {
        mBitmapState = new BitmapState(mBitmapState);
        mMutated = true;
    }
    return this;
}
```

### 复制一个drawable

```java
Drawable drawable = ContextCompact.getDrawable(mContext, R.drawable.icon);

Drawable clone1 = drawable.getConstantState().newDrawable();

Drawable clone2 = (Drawable) drawable.mutate();
```

- **clone1是一个新的drawable**,它与drawable共享相同的ConstantState,只要一个地方修改了ConstantState,两者的都会发生变化
- **drawable与clone2是同一个drawalbe**,但是两者不会共享ConstantState


## Drawable.Callback

```java
/**
* Implement this interface if you want to create an animated drawable that
* extends {@link android.graphics.drawable.Drawable Drawable}.
* Upon retrieving a drawable, use
* {@link Drawable#setCallback(android.graphics.drawable.Drawable.Callback)}
* to supply your implementation of the interface to the drawable; it uses
* this interface to schedule and execute animation changes.
*/
public interface Callback {
    /**
    * Called when the drawable needs to be redrawn.  A view at this point
    * should invalidate itself (or at least the part of itself where the
    * drawable appears).
    *
    * @param who The drawable that is requesting the update.
    */
    void invalidateDrawable(@NonNull Drawable who);

    /**
    * A Drawable can call this to schedule the next frame of its
    * animation.  An implementation can generally simply call
    * {@link android.os.Handler#postAtTime(Runnable, Object, long)} with
    * the parameters <var>(what, who, when)</var> to perform the
    * scheduling.
    *
    * @param who The drawable being scheduled.
    * @param what The action to execute.
    * @param when The time (in milliseconds) to run.  The timebase is
    *             {@link android.os.SystemClock#uptimeMillis}
    */
    void scheduleDrawable(@NonNull Drawable who, @NonNull Runnable what, long when);

    /**
    * A Drawable can call this to unschedule an action previously
    * scheduled with {@link #scheduleDrawable}.  An implementation can
    * generally simply call
    * {@link android.os.Handler#removeCallbacks(Runnable, Object)} with
    * the parameters <var>(what, who)</var> to unschedule the drawable.
    *
    * @param who The drawable being unscheduled.
    * @param what The action being unscheduled.
    */
    void unscheduleDrawable(@NonNull Drawable who, @NonNull Runnable what);
    }
```

- 当我们实现一个有动画的drawable的时候，通过实现Drawable.Callback来实现drawable的多次绘制
 比如GifDrawable

```java
drawable = GifDrawable.createFromResource(context.getResources(),
    mEmojisMap.get(matcher.group()).mDrawableId);
if (null != callback) {
    drawable.setCallback(callback);
}

// Drawable.Callback
private DraweeTextView mContent;

@Override
public void scheduleDrawable(Drawable who, Runnable what, long when) {
    if (null != mContent) {
        mContent.postDelayed(what, when);
    }
}

@Override
public void unscheduleDrawable(Drawable who, Runnable what) {
    if (null != mContent) {
        mContent.removeCallbacks(what);
    }
}

@Override
protected void setupBaseListeners() {
    super.setupBaseListeners();
    mContent.setOnLongClickListener(this);
}
```

## setLevel

- **level的值的范围是0~10000**
- setLevel的值会回调它的onLevelChange，从而可能会导致Drawable的重绘
- setLevel的值与LevelDrawable选取哪一项有关
- setLevel的值与ClipDrawable的裁剪区域有关，并且level越大，裁剪区域越小
- setLevel的值与ScaleDrawble最终的大小有关，一般情况下，对于ScaleDrawable我们会设置level为1,这样
 当我们在xml中指定scaleWidth为a时，最终实际的大小为原大小的(1-a)
