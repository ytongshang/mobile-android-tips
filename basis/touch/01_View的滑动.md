# View的滑动

## scrollTo和scrollBy

- 关于View提供的与坐标息息相关的另一组常用的重要方法就是滚动或者滑动相关的

函数                   | 具体描述
----------------------------- | :--------------------------------------------------------------------
offsetLeftAndRight(int offset) | 水平方向挪动View，offset为正则x轴正向移动，移动的是整个View，getLeft()会变的，自定义View很有用。
offsetTopAndBottom(int offset) | 垂直方向挪动View，offset为正则y轴正向移动，移动的是整个View，getTop()会变的，自定义View很有用
scrollTo(int x, int y)         | 将View中内容（不是整个View）滑动到相应的位置，参考坐标原点为ParentView左上角，x，y为正则向xy轴反方向移动，反之同理。
scrollBy(int x, int y)         | 将View中的内容相对于当前位置滑动x, y,x，y为正则向xy轴反方向移动，反之同理。
setScrollX(int value)          | 实质为scrollTo()，只是只改变Y轴滑动
setScrollY(int value)          | 实质为scrollTo()，只是只改变X轴滑动
getScrollX()/getScrollY()      | 获取当前滑动位置偏移量

- 改变View在屏幕中的位置可以使用offsetLeftAndRight()和offsetTopAndBottom()方法，他会导致getLeft()等值改变。

```java
public void scrollTo(int x, int y) {
    if (mScrollX != x || mScrollY != y) {
        int oldX = mScrollX;
        int oldY = mScrollY;
        mScrollX = x;
        mScrollY = y;
        invalidateParentCaches();
        onScrollChanged(mScrollX, mScrollY, oldX, oldY);
        if (!awakenScrollBars()) {
            postInvalidateOnAnimation();
        }
    }
}

public void scrollBy(int x, int y) {
    scrollTo(mScrollX + x, mScrollY + y);
}

```

- **scrollTo和scrollBy都是将view的内容进行滑动，view本身的位置没有变化**
- **scrollTo()方法是让View相对于初始的位置滚动某段距离**，由于View的初始位置是不变的，因此只要scrollTo的参数不变，不管我们调用多少次scrollTo滚动到的都将是同一个位置。
- **scrollBy()方法则是让View相对于当前的位置滚动某段距离**，scrollBy的参数不变，每调用一次scrollBy View的内容位置都进行了变动
- mScrollX为View的左边缘与View内容左边缘在水平方向上的距离，**并且由左向右滑动，mScrollX为负值，反之为正**
- mScrollY为View的上边缘与View内容上边缘在竖直方向上的距离，**并且由上向下滑动，mScrollY为负值，反之为正**

## 使用动画

- 通过动画让一个View平移，从而实现滑动效果
- 使用属性动画，可以修改View的实际位置，从而可以正确的响应触摸事件
- **使用View动画由于是对View的影像做操作，平移结束后，触摸事件响应是不正确的**
- **兼容3.0以下的nineoldanimations在3.0以下实际上也是采用View动画**

## 改变布局参数

- **通过修改View的margin参数并且请求View重绘，从而实现View的滑动**
- 另一种方式在View的旁边放置一个空的View,通过修改空View的大小，从而实现View的滑动

```java
MarginLayoutParams params = (MarginLayoutParams)mButton1.getLayoutParams();
params.leftMargin += 100;
mButton1.requestLayout();
//或者调用mButton1.setLayoutParams(params);
```

## 弹性滑动

- View调用ScrollTo/ScrollBy方法进行滑动时，其过程是瞬时完成的
- 如果要实现滑动的过渡效果，可以使用Scroller结合View的computeScroll配合完成

```java

Scroller scroller = new Scroller()

```