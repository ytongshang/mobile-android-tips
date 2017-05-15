# TweenAnimation

- alpha,rotate,scale, translate

## Animation公共属性

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


- 当我们对set标签使用Animation的属性时会对该标签下的所有子动画都产生影响


## 具体动画属性

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

## android:pivotX与android:pivotY

- 缩放起点X/Y坐标
- 数值、百分数、百分数p
- 譬如50表示以当前View左上角坐标加50px为初始点
- 50%表示以当前View的左上角加上当前View宽高的50%做为初始点
- 50%p表示以当前View的左上角加上父控件宽高的50%做为初始点

## 使用

### animation 常用方法

Header One                                       | Header Two
:----------------------------------------------- | :-----------------
reset()                                          | 重置Animation的初始化
cancel()                                         | 取消Animation动画
start()                                          | 开始Animation动画
setAnimationListener(AnimationListener listener) | 给当前Animation设置动画监听
hasStarted()                                     | 判断当前Animation是否开始
hasEnded()                                       | 判断当前Animation是否结束

### view 类用方法

Header One                          | Header Two
:---------------------------------- | :----------------------
startAnimation(Animation animation) | 对当前View开始设置的Animation动画
clearAnimation()                    | 取消当View在执行的Animation动画


```java
ImageView spaceshipImage = (ImageView) findViewById(R.id.spaceshipImage);
Animation hyperspaceJumpAnimation = AnimationUtils.loadAnimation(this,R.anim.hyperspace_jump);
spaceshipImage.startAnimation(hyperspaceJumpAnimation);
```

## 动画插值器

- android:interpolator 指定动画的插值器
- android:shareInterpolator，表示animationSet中的动画是否和集合共享同一个插值器，
 如果集合不指定插值器，那么子动画就需要单独指定所需的插值器或使用默认值

### 具体的动画插值 器

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

