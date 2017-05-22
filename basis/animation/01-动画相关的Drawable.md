# Animation

- [AnimationDrawable](#animationdrawable)
    - [使用AnimationDrawable](#使用animationdrawable)
    - [start()调用时机](#start调用时机)
    - [oom解决办法](#oom解决办法)
- [RotateDrawable](#rotatedrawable)
- [AnimatedRotateDrawable](#animatedrotatedrawable)
- [RippleDrawable](#rippledrawable)
    - [Ripple With Color Mask（用颜色作为Mask的Ripple）](#ripple-with-color-mask用颜色作为mask的ripple)
    - [Ripple With Picture Mask(用图片作为Mask的Ripple)](#ripple-with-picture-mask用图片作为mask的ripple)
    - [Ripple With Shape Mask(用设定形状作为Mask的Ripple)](#ripple-with-shape-mask用设定形状作为mask的ripple)
    - [Ripple With Selector(搭配selector作为Ripple)](#ripple-with-selector搭配selector作为ripple)
    - [Ripple With No Mask（没有边界的Ripple）](#ripple-with-no-mask没有边界的ripple)
- [AnimatedListStateDrawable](#animatedliststatedrawable)


## AnimationDrawable

### 使用AnimationDrawable

- 首先 **animationDrawable 它是一个Drawable**

- 使用

```xml
<animation-list xmlns:android="http://schemas.android.com/apk/res/android"
    android:oneshot="true">
    <item android:drawable="@drawable/rocket_thrust1" android:duration="200" />
    <item android:drawable="@drawable/rocket_thrust2" android:duration="200" />
    <item android:drawable="@drawable/rocket_thrust3" android:duration="200" />
</animation-list>
```

```java
ImageView rocketImage = (ImageView) findViewById(R.id.rocket_image);
rocketImage.setBackgroundResource(R.drawable.rocket_thrust);

rocketAnimation = (AnimationDrawable) rocketImage.getBackground();
rocketAnimation.start();
```

### start()调用时机

- 如果是在activity中，不能在onCreate（）中播放动画，因为些时，animationDrawable还没有附加到window中
- 如果一开始就要播放动画，则播放在代码应当写在onWindowFocusChanged()中
- 使用post方法也可以

### oom解决办法

- 如果帧动画的帧数非常多，很可能会出现OOM,可以使用view的setBackground与post相接合的方式来解决

```java
public class KeyFrameAnimation {

    private ImageView mImageView;

    private int[] mFrames;

    private int[] mDurations;

    private int mSameDuration;

    private int mCurrentFrame;

    private boolean mIsStopped;

    private boolean mIsOneShot;

    private boolean mIsSameDuration;

    private Runnable mAction;

    private FrameAnimationListener mListener;

    public KeyFrameAnimation(@NonNull ImageView imageView, @NonNull int[] frames, @NonNull int[] durations) {
        init(imageView, frames);
        mIsSameDuration = false;
        mDurations = durations;
    }

    public KeyFrameAnimation(@NonNull ImageView imageView, @NonNull int[] frames, int duration) {
        init(imageView, frames);
        mIsSameDuration = true;
        mSameDuration = duration;
    }

    private void init(ImageView imageView, int[] frames) {
        mImageView = imageView;
        mFrames = frames;
        mCurrentFrame = 0;
        mIsOneShot = true;
    }

    public int getTotalDuration() {
        if (mFrames != null && mFrames.length > 0) {
            if (mIsSameDuration) {
                return mSameDuration * mFrames.length;
            } else if (mDurations != null) {
                int total = 0;
                for (int duration : mDurations) {
                    total += duration;
                }
                return total;
            }
        }

        return 0;
    }

    public void startPlay() {
        if (mImageView == null || mFrames == null || mFrames.length == 0) {
            return;
        }
        mImageView.removeCallbacks(mAction);
        mCurrentFrame = 0;
        mImageView.setBackgroundResource(mFrames[mCurrentFrame]);
        if (mListener != null) {
            mListener.onStart();
            mListener.onFrame(mCurrentFrame);
        }
        mAction = new Runnable() {
            @Override
            public void run() {
                if (mIsStopped) {
                    return;
                }
                mCurrentFrame++;
                if (mCurrentFrame >= mFrames.length) {
                    return;
                }
                if (mImageView != null) {
                    mImageView.setBackgroundResource(mFrames[mCurrentFrame]);
                }
                if (mListener != null) {
                    mListener.onFrame(mCurrentFrame);
                }
                if (mCurrentFrame == mFrames.length - 1) {
                    if (mIsOneShot) {
                        if (mListener != null) {
                            mListener.onEnd();
                        }
                    } else {
                        startPlay();
                    }
                }
            }
        };
        mImageView.postDelayed(mAction, mIsSameDuration ? mSameDuration : mDurations[mCurrentFrame]);
    }

    public void stopPlay() {
        mIsStopped = true;
        if (mImageView != null) {
            mImageView.removeCallbacks(mAction);
            mAction = null;
        }
    }

    public void setFrameAnimationListener(FrameAnimationListener listener) {
        mListener = listener;
    }

    public void setIsOneShot(boolean isOneShot) {
        mIsOneShot = isOneShot;
    }


}
```

## RotateDrawable

```xml
<?xml version="1.0" encoding="utf-8"?>
<rotate
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/drawable_resource"
    android:visible=["true" | "false"]
    android:fromDegrees="integer"
    android:toDegrees="integer"
    android:pivotX="float"
    android:pivotY="float"/>
```

- 表示相对于pivotX与pivotY进行旋转，角度从fromDegree转到toDegree，**旋转是通过setLevel来实现的**

```java
// RotateDrawable.java
@Override
protected boolean onLevelChange(int level) {
    super.onLevelChange(level);
    // MAX_LEVEL为10000
    final float value = level / (float) MAX_LEVEL;

    // 是一个线性插值
    final float degrees = MathUtils.lerp(mState.mFromDegrees, mState.mToDegrees, value);
    mState.mCurrentDegrees = degrees;

    invalidateSelf();
    return true;
}

@Override
public void draw(Canvas canvas) {
    final Drawable d = getDrawable();
    final Rect bounds = d.getBounds();
    final int w = bounds.right - bounds.left;
    final int h = bounds.bottom - bounds.top;
    final RotateState st = mState;
    final float px = st.mPivotXRel ? (w * st.mPivotX) : st.mPivotX;
    final float py = st.mPivotYRel ? (h * st.mPivotY) : st.mPivotY;

    final int saveCount = canvas.save();
    canvas.rotate(st.mCurrentDegrees, px + bounds.left, py + bounds.top);
    d.draw(canvas);
    canvas.restoreToCount(saveCount);
}

// MathUtils.java
public static float lerp(float start, float stop, float amount) {
    return start + (stop - start) * amount;
}

```

## AnimatedRotateDrawable

- 代表一个可以绕着指定的旋转中心进行旋转的drawable

- **AnimatedRotateDrawale类被标记为@hide的，不能通过代码使用，只能通过xml使用**

```xml
<?xml version="1.0" encoding="utf-8"?>
<animated-rotate xmlns:android="http://schemas.android.com/apk/res/android"
    android:pivotX="50%"
    android:pivotY="50%"
    android:drawable="@drawable/fifth">
</animated-rotate>
```

```java
<TextView
    android:layout_centerInParent="true"
    android:gravity="center"
    android:background="@drawable/animated_rotate_drawable"
    android:id="@+id/tv"
    android:layout_width="200dp"
    android:layout_height="200dp"/>
```

## RippleDrawable

- 主要是在按下时提供一个涟漪效果的视觉反馈
- 它本身继承于LayerDrawable

### Ripple With Color Mask（用颜色作为Mask的Ripple）

- 如果在ripple内部增加一个item子项，并且子项的id为@android:id/mask,drawable属性为引用的颜色(color) ，**则水波效果会限定在drawable对应的RippleDrawable本身矩形区域内部。**

```xml
<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android"
        android:color="#FF0000" >

    <item android:id="@android:id/mask"
         android:drawable="@android:color/white" />
</ripple>
```

- **item本身drawable的颜色是什么颜色并没有用，只是相当于新增了一个遮罩层，并且也不会绘制出来**

- 如果要设置一个已经存在的layer为mask,可以通过设置setId(int index, android.R.id.mask);

```java
// LayerDrawable.java
public void setId(int index, int id) {
    mLayerState.mChildren[index].mId = id;
}
```

- 如果要动态替换一个已经存在的mask,可以通过setDrawableByLayerId(android.R.id.mask, drawable).

```java
// LayerDrawable.java
 public boolean setDrawableByLayerId(int id, Drawable drawable) {
    final int index = findIndexByLayerId(id);
    if (index < 0) {
        return false;
    }

    setDrawable(index, drawable);
    return true;
}
```

### Ripple With Picture Mask(用图片作为Mask的Ripple)

- 如果在一个ripple标签中，添加一个item，其id为@android:id/mask，drawable属性为引用的图片(png,jpg)，则水波效果会限定在图片drawable中非透明部分对应的区域内部。

### Ripple With Shape Mask(用设定形状作为Mask的Ripple)

- 如果在一个ripple标签中，添加一个item，其id为@android:id/mask，drawable属性为引用的形状(shape) ，则水波效果会限定在shape对应的区域内部。

### Ripple With Selector(搭配selector作为Ripple)

- 如果在一个ripple标签中，添加一个item，在item的内部写上selector标签，那么这个RippleDrawable在按下的时候，同时具有水波效果和selector指定的图层

```xml
<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android"
    android:color="#FF0000" >
    <item>
        <selector>
            <item
                android:drawable="@drawable/icon_folder_i"
                android:state_pressed="true">
            </item>
            <item
                android:drawable="@drawable/icon_folder_r"
                android:state_pressed="false">
            </item>
        </selector>
    </item>

</ripple>
```

### Ripple With No Mask（没有边界的Ripple）

```xml
<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android"
    android:color="#FF0000" >
</ripple>
```

- ripple标签生成一个RippleDrawable,**如果没有指定mask layer， 也没有指定child layer,在按下时，涟漪效果是没有边界的，可能会超出drawable本身的范围**


## AnimatedListStateDrawable


