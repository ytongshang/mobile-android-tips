# 属性动画

## 属性动画基本属性

- Duration：动画的持续时间；

- TimeInterpolation：定义动画变化速率的接口，所有插值器都必须实现此接口，如线性、非线性插值器；

- TypeEvaluator：用于定义属性值计算方式的接口，有int、float、color类型，根据属性的起始、结束值和插值一起计算出当前时间的属性值；

```java
public void setEvaluator(TypeEvaluator value) {
    if (value != null && mValues != null && mValues.length > 0) {
        mValues[0].setEvaluator(value);
    }
}

public interface TypeEvaluator<T> {

    /**
     * This function returns the result of linearly interpolating the start and end values, with
     * <code>fraction</code> representing the proportion between the start and end values. The
     * calculation is a simple parametric calculation: <code>result = x0 + t * (x1 - x0)</code>,
     * where <code>x0</code> is <code>startValue</code>, <code>x1</code> is <code>endValue</code>,
     * and <code>t</code> is <code>fraction</code>.
     *
     * @param fraction   The fraction from the starting to the ending values
     * @param startValue The start value.
     * @param endValue   The end value.
     * @return A linear interpolation between the start and end values, given the
     *         <code>fraction</code> parameter.
     */
    public T evaluate(float fraction, T startValue, T endValue);

}
```

- Animation sets：动画集合，即可以同时对一个对象应用多个动画，这些动画可以同时播放也可以对不同动画设置不同的延迟；

- Frame refreash delay：多少时间刷新一次，即每隔多少时间计算一次属性值，默认为10ms，最终刷新时间还受系统进程调度与硬件的影响；

```java
public static long getFrameDelay() {
    return Choreographer.getFrameDelay();
}

/**
* The amount of time, in milliseconds, between each frame of the animation. This is a
* requested time that the animation will attempt to honor, but the actual delay between
* frames may be different, depending on system load and capabilities. This is a static
* function because the same delay will be applied to all animations, since they are all
* run off of a single timing loop.
*
* The frame delay may be ignored when the animation system uses an external timing
* source, such as the display refresh rate (vsync), to govern animations.
*
* @param frameDelay the requested time between frames, in milliseconds
*/
public static void setFrameDelay(long frameDelay) {
    Choreographer.setFrameDelay(frameDelay);
}
```

- Repeat Country and behavoir：重复次数与方式，如播放3次、5次、无限循环，可以让此动画一直重复，或播放完时向反向播放；

```java
public void setRepeatCount(int value) {
    mRepeatCount = value;
}

public void setRepeatMode(int value) {
    mRepeatMode = value;
}

/**
* When the animation reaches the end and <code>repeatCount</code> is INFINITE
* or a positive value, the animation restarts from the beginning.
*/
public static final int RESTART = 1;
/**
* When the animation reaches the end and <code>repeatCount</code> is INFINITE
* or a positive value, the animation reverses direction on every iteration.
*/
public static final int REVERSE = 2;
/**
* This value used used with the {@link #setRepeatCount(int)} property to repeat
* the animation indefinitely.
*/
public static final int INFINITE = -1;
```

## xml使用属性动画

### xml

```xml
<set
  android:ordering=["together" | "sequentially"]>

    <objectAnimator
        android:propertyName="string"
        android:duration="int"
        android:valueFrom="float | int | color"
        android:valueTo="float | int | color"
        android:startOffset="int"
        android:repeatCount="int"
        android:repeatMode=["repeat" | "reverse"]
        android:valueType=["intType" | "floatType"]/>

    <animator
        android:duration="int"
        android:valueFrom="float | int | color"
        android:valueTo="float | int | color"
        android:startOffset="int"
        android:repeatCount="int"
        android:repeatMode=["repeat" | "reverse"]
        android:valueType=["intType" | "floatType"]/>

    <set>
        ...
    </set>
</set>
```

### Animator xml 属性

| column0              | column1                                                                                                                              |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| android:propertyName | String类型，必须要设置的节点属性，代表要执行动画的属性，辟如你可以指定了一个View的”alpha” ，必须通过调用loadAnimator()方法加载你的XML动画资源，然后调用setTarget()应用到具备这个属性的目标对象上（譬如TextView）。 |
| android:valueTo      | float、int或者color类型，必须要设置的节点属性，表明动画结束的点；如果是颜色的话，由6位十六进制的数字表示。                                                                         |
| android:duration     | 动画的时长，int类型，以毫秒为单位，默认为300毫秒。                                                                                                         |
| android:startOffset  | 动画延迟的时间，从调用start方法后开始计算，int型，毫秒为单位。                                                                                                  |
| android:repeatCount  | 一个动画的重复次数，int型，”-1“表示无限循环，”1“表示动画在第一次执行完成后重复执行一次，也就是两次，默认为0，不重复执行。                                                                   |
| android:repeatMode   | 重复模式：int型，当一个动画执行完的时候应该如何处理。该值必须是正数或者是-1，“reverse”会使得按照动画向相反的方向执行，可实现类似钟摆效果。“repeat”会使得动画每次都从头开始循环。                                  |
| android:valueType    | 关键参数，如果该value是一个颜色，那么就不需要指定，因为动画框架会自动的处理颜色值。有intType和floatType（默认）两种：分别说明动画值为int和float型。                                             |

### 使用xml中定义的animator

```java
AnimatorSet set = (AnimatorSet) AnimatorInflater.loadAnimator(myContext,R.animtor.property_animator);
set.setTarget(myObject);
set.start();
```

## ValueAnimator

- ValueAnimator只是动画计算管理驱动，设置了作用目标，但没有设置属性，需要通过updateListener里设置属性才会生效

```java
ValueAnimator animator = ValueAnimator.ofFloat(0, mContentHeight);  //定义动画
animator.setTarget(view);   //设置作用目标
animator.setDuration(5000).start();
animator.addUpdateListener(new AnimatorUpdateListener() {
    @Override
    public void onAnimationUpdate(ValueAnimator animation){
        float value = (float) animation.getAnimatedValue();
        view.setXXX(value);  //必须通过这里设置属性值才有效
        view.mXXX = value;  //不需要setXXX属性方法
    }

});
```

## ObjectAnimator

- ObjectAnimator：继承自ValueAnimator，允许你指定要进行动画的对象以及该对象的一个属性
- ObjectAnimator的动画原理是不停的调用setXXX方法更新属性值，所有使用ObjectAnimator更新属性时的前提是Object必须声明有getXXX和setXXX方法

```java
ObjectAnimator mObjectAnimator= ObjectAnimator.ofInt(view, "customerDefineAnyThingName", 0,  1).setDuration(2000);
mObjectAnimator.addUpdateListener(new ValueAnimator.AnimatorUpdateListener() {
    @Override
    public void onAnimationUpdate(ValueAnimator animation) {
        //int value = animation.getAnimatedValue();  可以获取当前属性值
        //view.postInvalidate();  可以主动刷新
        //view.setXXX(value);
        //view.setXXX(value);
        //......可以批量修改属性
    }
});
```

## PropertyValuesHolder

- PropertyValuesHolder：多属性动画同时工作管理类。有时候我们需要同时修改多个属性，那就可以用到此类

```java
PropertyValuesHolder a1 = PropertyValuesHolder.ofFloat("alpha", 0f, 1f);
PropertyValuesHolder a2 = PropertyValuesHolder.ofFloat("translationY", 0, viewWidth);
ObjectAnimator.ofPropertyValuesHolder(view, a1, a2).setDuration(1000).start();
```

## AnimatorSet

- AnimationSet：动画集合，提供把多个动画组合成一个组合的机制，并可设置动画的时序关系，如同时播放、顺序播放或延迟播放

```java
ObjectAnimator a1 = ObjectAnimator.ofFloat(view, "alpha", 1.0f, 0f);
ObjectAnimator a2 = ObjectAnimator.ofFloat(view, "translationY", 0f, viewWidth);
AnimatorSet animSet = new AnimatorSet();
animSet.setDuration(5000);
animSet.setInterpolator(new LinearInterpolator());
//animSet.playTogether(a1, a2, ...); //两个动画同时执行
animSet.play(a1).after(a2); //先后执行
animSet.start();
```

## ViewPropertyAnimator动画

- ViewPropertyAnimator提供了一种非常方便的方法为View的部分属性设置动画（切记，是部分属性），它可以直接使用一个Animator对象设置多个属性的动画；在多属性设置动画时，
 它比 上面的ObjectAnimator更加牛逼、高效，因为他会管理多个属性的invalidate方法统一调运触发，而不像上面分别调用，所以还会有一些性能优化。如下就是一个例子：

```java
myView.animate().x(0f).y(100f).start();
```

## TimeInterpolator 与 Interpolator

```java
// Animation.java
public void setInterpolator(Interpolator i);

// Animator.java
public abstract void setInterpolator(TimeInterpolator value);

public interface Interpolator extends TimeInterpolator {
    // A new interface, TimeInterpolator, was introduced for the new android.animation
    // package. This older Interpolator interface extends TimeInterpolator so that users of
    // the new Animator-based animations can use either the old Interpolator implementations or
    // new classes that implement TimeInterpolator directly.
}

public interface TimeInterpolator {
    /**
     * Maps a value representing the elapsed fraction of an animation to a value that represents
     * the interpolated fraction. This interpolated value is then multiplied by the change in
     * value of an animation to derive the animated value at the current elapsed animation time.
     *
     * @param input A value between 0 and 1.0 indicating our current point
     *        in the animation where 0 represents the start and 1.0 represents
     *        the end
     * @return The interpolation value. This value can be more than 1.0 for
     *         interpolators which overshoot their targets, or less than 0 for
     *         interpolators that undershoot their targets.
     */
    float getInterpolation(float input);
}
```

## Animator相关的listener

```java
// Animator中定义的
public static interface AnimatorListener {
     void onAnimationStart(Animator animation);
     void onAnimationEnd(Animator animation);
     void onAnimationCancel(Animator animation);
     void onAnimationRepeat(Animator animation);
}

public static interface AnimatorPauseListener {
    void onAnimationPause(Animator animation);
    void onAnimationResume(Animator animation);
}

// 为了方便还有一个AnimatorListenerAdapter,这样方便只用重写其中的部分方法
public abstract class AnimatorListenerAdapter implements Animator.AnimatorListener,
        Animator.AnimatorPauseListener  {
//...
}

// ValueAnimator中定义的,主要用处在于使用使用可能要自定义的ValueAnimator
public static interface AnimatorUpdateListener {
    void onAnimationUpdate(ValueAnimator animation);
}

ObjectAnimator mObjectAnimator= ObjectAnimator.ofInt(view, "customerDefineAnyThingName", 0,  1).setDuration(2000);
mObjectAnimator.addUpdateListener(new ValueAnimator.AnimatorUpdateListener() {
    @Override
    public void onAnimationUpdate(ValueAnimator animation) {
        //int value = animation.getAnimatedValue();  可以获取当前属性值
        //view.postInvalidate();  可以主动刷新
        //view.setXXX(value);
        //view.setXXX(value);
        //......可以批量修改属性
    }
});
```

## 对任意属性做动画

- 对于有UI
