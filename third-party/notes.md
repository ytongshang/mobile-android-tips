# tips

- [android:screenOrientation](#androidscreenorientation)
- [Fragment的显示与否监听](#fragment的显示与否监听)
- [View的生命周期](#view的生命周期)
    - [onAttachedToWindow与onDetachedFromWindow](#onattachedtowindow与ondetachedfromwindow)
    - [onStartTemporaryDetach与onFinishTemporaryDetach](#onstarttemporarydetach与onfinishtemporarydetach)

## android:screenOrientation

- "unspecified", 默认值. 由系统选择显示方向. 在不同的设备可能会有所不同..
- "landscape" 横向
- "portrait" 纵向
- "user" 用户当前的首选方向
- **"behind"** 与在活动堆栈下的活动相同方向
- "sensor" 根据物理方向传感器确定方向. 取决于用户手持的方向, 当用户转动设备, 它跟随改变
- "nosensor" 不经物理方向传感器确定方向. 该传感器被忽略, 所以当用户转动设备, 显示不会跟随改变. 除了这个区别，系统选择使用相同的政策取向对于"未指定"设置. 系统根据"未指定"("unspecified")设定选择相同显示方向.

## Fragment的显示与否监听

- 当Fragment配合ViewPager使用时，使用setUserVisibleHint()判断Fragment是显示还是隐藏。
- 当Fragment配合FragmentTransition使用时，使用onHiddenChanged()来判断Fragment是显示还是隐藏，但是第一次显示要在onResume()里判断.

## View的生命周期

### onAttachedToWindow与onDetachedFromWindow

```java
protected void onAttachedToWindow()
protected void onDetachedFromWindow()
```

- onAttachedToWindow与onDetachedFromWindow分别会在View add到WindowManager，从windowManager remove后回调
- 一般我们会在onAttachedToWindow初始化一些操作，比如动画等，在onDetachedFromWindow中取消一些动作，比如mHandler发送的消息

### onStartTemporaryDetach与onFinishTemporaryDetach

```java
/**
* This is called when a container is going to temporarily detach a child, with
* {@link ViewGroup#detachViewFromParent(View) ViewGroup.detachViewFromParent}.
* It will either be followed by {@link #onFinishTemporaryDetach()} or
* {@link #onDetachedFromWindow()} when the container is done.
*/
public void onStartTemporaryDetach() {
    removeUnsetPressCallback();
    mPrivateFlags |= PFLAG_CANCEL_NEXT_UP_EVENT;
}

/**
* Called after {@link #onStartTemporaryDetach} when the container is done
* changing the view.
*/
public void onFinishTemporaryDetach() {
}
```

- **当父布局ViewGroup调用detachViewFromParent(View child)，会回调onStartTemporaryDetach**
- **当调用onStartTemporaryDetach后，接着一定会回调onFinishTemporaryDetach或者回调onDetchedFromWindow**
- detach的childView再次调用attachViewToParent(View, int, ViewGroup.LayoutParams) add到parent上，会回调onFinishTemporaryDetach，**此时childView实际上是attached的**
- detach的childView再次调用removeDetachedView(View, boolean)，会回调onDetchedFromWindow，**此时childView是detched的**

### 属性动画 cancel 与end

- 属性动画进行过程中，如果动画正在进行中，**调用cancel与end，也会调用onAnimationEnd**,如果仅仅想取消动画，不再回调onAnimationEnd,应当将listener取消掉

```java
if (mNextAnimator != null) {
    mNextAnimator.removeAllListeners();
    mNextAnimator.cancel();
    mNextAnimator = null;
}
```

#### Animator.cancel

- cancel只会处理那些正在运行或者等待开始运行的动画，具体的处理逻辑是这样的：
    - 若未调用过AnimatorListener.onAnimationStart，则调用
    - 调用AnimatorListener.onAnimationCancel
    - 调用Animator.endAnimation：
        - 把该动画从AnimationHandler的所有列表中清除
        - 调用AnimatorListener.onAnimationEnd
        - 复位动画所有状态：如mPlayingState = STOPPED、mRunning=false、mStarted = false等等
- 从上面的逻辑不难发现，cancel对回调的处理是比较完整的，但是cancel被调用之后，动画的动画值会停留在当前帧而不会继续进行计算。

#### Animator.end

- end相对于cancel来说有两个区别：一个是会处理所有动画；另一个是会计算最末一帧动画值。其具体的处理逻辑如下所示：
    - 若动画尚未开始：调用Animatior.startAnimation让动画处于正常运行状态
    - 计算最后一帧动画的动画值：animateValue(mPlayingBackwards ? 0f : 1f)
    - 结束动画：调用endAnimation
- 这两种处理都会导致动画的非正常结束，需要注意的是cancel会保留当前的动画值，而end会计算最末帧的动画值。
