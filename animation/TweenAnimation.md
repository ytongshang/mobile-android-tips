# 总体

- alpha,rotate,scale, translate

- Animation属性详解

Header One              | Header Two                    | Header Two
:---------------------- | :---------------------------- | :--------------------------------------
android:detachWallpaper | setDetachWallpaper(boolean)   | 是否在壁纸上运行
android:duration        | setDuration(long)             | 动画持续时间，毫秒为单位
android:fillAfter       | setFillAfter(boolean)         | 控件动画结束时是否保持动画最后的状态
android:fillBefore      | setFillBefore(boolean)        | 控件动画结束时是否还原到开始动画前的状态
android:fillEnabled     | setFillEnabled(boolean)       | 与android:fillBefore效果相同
android:interpolator    | setInterpolator(Interpolator) | 设定插值器（指定的动画效果，譬如回弹等)
android:repeatCount     | setRepeatCount(int)           | 重复次数
android:repeatMode      | android:repeatMode            | 重复类型有两个值，reverse表示倒序回放，restart表示从头播放
android:startOffset     | setStartOffset(long)          | 调用start函数之后等待开始运行的时间，单位为毫秒
android:zAdjustment     | setZAdjustment(int)           | 表示被设置动画的内容运行时在Z轴上的位置（top/bottom/normal)

- alpha

Header One        | Header Two                           | Header Two
:---------------- | :----------------------------------- | :--------------------------------
android:fromAlpha | AlphaAnimation(float fromAlpha, ...) | 动画开始的透明度（0.0到1.0，0.0是全透明，1.0是不透明）
android:toAlpha   | AlphaAnimation(..., float toAlpha)   | 动画结束的透明度，同上

- rotate

Header One          | Header Two                                 | Header Two
:------------------ | :----------------------------------------- | :---------------------------------------------------------------------------------------------------------------------
android:fromDegrees | RotateAnimation(float fromDegrees, ...)    | 旋转开始角度，正代表顺时针度数，负代表逆时针度数
android:toDegrees   | RotateAnimation(..., float toDegrees, ...) | 旋转结束角度，正代表顺时针度数，负代表逆时针度数
android:pivotX      | RotateAnimation(..., float pivotX, ...)    | 缩放起点X坐标（数值、百分数、百分数p，譬如50表示以当前View左上角坐标加50px为初始点、50%表示以当前View的左上角加上当前View宽高的50%做为初始点、50%p表示以当前View的左上角加上父控件宽高的50%做为初始点）
android:pivotY      | RotateAnimation(..., float pivotY)         | 缩放起点Y坐标，同上规律

- scale

Header One         | Header Two                             | Header Two
:----------------- | :------------------------------------- | :----------------------------------------------------------------------------------------------------------------------
android:fromXScale | ScaleAnimation(float fromX, ...)       | 初始X轴缩放比例，1.0表示无变化
android:toXScale   | ScaleAnimation(..., float toX, ...)    | 结束X轴缩放比例
android:fromYScale | ScaleAnimation(..., float fromY, ...)  | 初始Y轴缩放比例
android:toYScale   | ScaleAnimation(..., float toY, ...)    | 结束Y轴缩放比例
android:pivotX     | ScaleAnimation(..., float pivotX, ...) | 缩放起点X轴坐标（数值、百分数、百分数p，譬如50表示以当前View左上角坐标加50px为初始点、50%表示以当前View的左上角加上当前View宽高的50%做为初始点、50%p表示以当前View的左上角加上父控件宽高的50%做为初始点）
android:pivotY     | ScaleAnimation(..., float pivotY)      | 同上

- translate

Header One         | Header Two                                     | Header Two
:----------------- | :--------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------
android:fromXDelta | TranslateAnimation(float fromXDelta, ...)      | 起始点X轴坐标（数值、百分数、百分数p，譬如50表示以当前View左上角坐标加50px为初始点、50%表示以当前View的左上角加上当前View宽高的50%做为初始点、50%p表示以当前View的左上角加上父控件宽高的50%做为初始点）
android:fromYDelta | TranslateAnimation(..., float fromYDelta, ...) | 起始点Y轴从标，同上规律
android:toXDelta   | TranslateAnimation(..., float toXDelta, ...)   | 结束点X轴坐标，同上规律
android:toYDelta   | TranslateAnimation(..., float toYDelta)        | 结束点Y轴坐标，同上规律

- animationSet

  - 当我们对set标签使用Animation的属性时会对该标签下的所有子控件都产生影响

## 使用

- animation 常用方法

Header One                                       | Header Two
:----------------------------------------------- | :-----------------
reset()                                          | 重置Animation的初始化
cancel()                                         | 取消Animation动画
start()                                          | 开始Animation动画
setAnimationListener(AnimationListener listener) | 给当前Animation设置动画监听
hasStarted()                                     | 判断当前Animation是否开始
hasEnded()                                       | 判断当前Animation是否结束

- view 类用方法

Header One                          | Header Two
:---------------------------------- | :----------------------
startAnimation(Animation animation) | 对当前View开始设置的Animation动画
clearAnimation()                    | 取消当View在执行的Animation动画

## xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android"
    android:interpolator="@[package:]anim/interpolator_resource"
    android:shareInterpolator=["true" | "false"] >
    <alpha
        android:fromAlpha="float"
        android:toAlpha="float" />
    <scale
        android:fromXScale="float"
        android:toXScale="float"
        android:fromYScale="float"
        android:toYScale="float"
        android:pivotX="float"
        android:pivotY="float" />
    <translate
        android:fromXDelta="float"
        android:toXDelta="float"
        android:fromYDelta="float"
        android:toYDelta="float" />
    <rotate
        android:fromDegrees="float"
        android:toDegrees="float"
        android:pivotX="float"
        android:pivotY="float" />
    <set>
        ...
    </set>
</set>
```

```java
ImageView spaceshipImage = (ImageView) findViewById(R.id.spaceshipImage);
Animation hyperspaceJumpAnimation = AnimationUtils.loadAnimation(this, R.anim.hyperspace_jump);
spaceshipImage.startAnimation(hyperspaceJumpAnimation);
```

## 动画插值器

Header One                       | Header Two                                       | Header Two
:------------------------------- | :----------------------------------------------- | :-------------------------
AccelerateDecelerateInterpolator | @android:anim/accelerate_decelerate_interpolator | 动画始末速率较慢，中间加速
AccelerateInterpolator           | @android:anim/accelerate_interpolator            | 动画开始速率较慢，之后慢慢加速
AnticipateInterpolator           | @android:anim/anticipate_interpolator            | 开始的时候从后向前甩
AnticipateOvershootInterpolator  | @android:anim/anticipate_overshoot_interpolator  | 类似上面AnticipateInterpolator
BounceInterpolator               | @android:anim/bounce_interpolator                | 动画结束时弹起
CycleInterpolator                | @android:anim/cycle_interpolator                 | 循环播放速率改变为正弦曲线
DecelerateInterpolator           | @android:anim/decelerate_interpolator            | 动画开始快然后慢
LinearInterpolator               | @android:anim/linear_interpolator                | 动画匀速改变
OvershootInterpolator            | @android:anim/overshoot_interpolator             | 向前弹出一定值之后回到原来位置
PathInterpolator                 |                                                  | 新增，定义路径坐标后按照路径坐标来跑。

## 注意

- 补间动画执行之后并未改变View的真实布局属性值。切记这一点，譬如我们在Activity中有一个Button在屏幕上方，我们设置了平移动画移动到屏幕下方然后保持动画最后执行状态呆在屏幕下方，这时如果点击屏幕下方动画执行之后的Button是没有任何反应的，而点击原来屏幕上方没有Button的地方却响应的是点击Button的事件
