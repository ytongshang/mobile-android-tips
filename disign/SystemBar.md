# Status Bar

## SystemUiVisibility

- System ui,**指status bar以及navigation bar等window decration**
- View类提供了setSystemUiVisibility和getSystemUiVisibility方法，
 这两个方法实现了对system bar的动态设置显示或隐藏的操作

## SYSTEM UI FLAG

### View.SYSTEM_UI_FLAG_VISIBLE

- 显示状态栏,Activity不全屏显示，默认行为

### View.SYSTEM_UI_FLAG_LOW_PROFILE

- status bar和navigation bar并不会消失，只会变“暗”，变得不太引人注意
- 常见在阅读器以及图片浏览时会通过设置这个标识位，让navigation bar上的按钮变成“小的很暗”的圆点

### View.SYSTEM_UI_FLAG_HIDE_NAVIGATION(针对Navigation bar)

- 隐藏Navigation bar,一般和**View.SYSTEM_UI_FLAG_FULLSCREEN**一起用
- 因为Navigaton bar十分重要，如果与Navigation bar有任何交互的话，navigation bar会马上显示出来，
 并且**SYSTEM_UI_FLAG_HIDE_NAVIGATION**和**View.SYSTEM_UI_FLAG_FULLSCREEN**都会被清除掉

### View.SYSTEM_UI_FLAG_FULLSCREEN(针对Status bar)

- Activity全屏显示，隐藏掉status bar
- 当用户点击对应的区域时，status bar，标识位**View.SYSTEM_UI_FLAG_FULLSCREEN**会被清除掉，如果要再次隐藏，需要再次设置
- 在视觉效果上，**效果与WindowManager.LayoutParams.FLAG_FULLSCREEN**一样，
 但是如果设置了WindowManager.LayoutParams的话，除非调用**window.clearFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN)**，
 否则activity会一直是全屏效果，如果不清除，即使切换到不同的activity，也会是全屏的
- 当我们使用了**ActionBar（Window#FEATURE_ACTION_BAR）**，并且设置了**Window#FEATURE_ACTION_BAR_OVERLAY**，
 那么当我们设置**View.SYSTEM_UI_FLAG_FULLSCREEN**隐藏status bar时,也会让action bar隐藏掉，在md设计中
 如果status bar 隐藏掉了，那么action bar也应当隐藏掉
- **Window#FEATURE_ACTION_BAR_OVERLAY**,在Overlay模式中，Activity的布局占据了所有可能的空间，
 好像Action Bar不存在一样，系统会在布局的上方绘制Aciton Bar。虽然这会遮盖住上方的一些布局，
 但是当Action Bar显示或者隐藏的时候，系统就不需要重新改变布局区域的大小，常见的情况就是比如一个列表可以滑到
 半透明的action bar的下面

### View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN and View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION(针对Content布局)

- 当我们隐藏显示status bar和navigation bar因为整个局部的大小发生了变化，重绘时可能会造成“视觉”上的跳跃，
 此时应当**避免调用View.SYSTEM_UI_FLAG_HIDE_NAVIGATION, View.SYSTEM_UI_FLAG_FULLSCREEN**，
 而**选择调用View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN，View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION**
- View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN,即使status是可见的，布局整个大小也好像status bar不可见一样
- View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION,即使navigation是可见的，布局整个大小也好像navigation bar不可见一样
- 因而使用这两个flag时，当status bar，navigation bar可见时，可能会有部分的content view的ui被遮挡住，
- 如果**想要不被遮挡住，可以给那个layout设置属性android:fitsSystemWindows为true**,含义是考虑到window decration,即使设置了
 hide status bar和hide navigation bar,layout也会为window decrations留出空间

### View.SYSTEM_UI_FLAG_LAYOUT_STABLE

- 主要用来维持一个稳定的布局

### View.SYSTEM_UI_FLAG_IMMERSIVE and SYSTEM_UI_FLAG_IMMERSIVE_STICKY（沉浸模式）

- 必须和**View.SYSTEM_UI_FLAG_HIDE_NAVIGATION,View.SYSTEM_UI_FLAG_FULLSCREEN**中的一个或两个一起使用才有效果，
 不过一般情况下，都是和上面两个一起使用，因为想要达到沉浸模式，一般status 和navigation bar要都要隐藏
- 一般情况下，当我们设置了**View.SYSTEM_UI_FLAG_HIDE_NAVIGATION**后，可以暂时隐藏navigation bar，但是当我们与window
 有任何的交互时，**View.SYSTEM_UI_FLAG_HIDE_NAVIGATION**会被清除掉，同时navigation bar会显示出来，并且以后也会一直显示，
 如果要再次隐藏，必须再次设置**View.SYSTEM_UI_FLAG_HIDE_NAVIGATION**
- 如果设置了**View.SYSTEM_UI_FLAG_IMMERSIVE**后，一般的操作status 和navigation bar都不会显示出来，
 用户可以通过在状态栏与导航栏原来区域的边缘向内滑动让系统栏重新显示（这种操作当然也清除了对应的的隐藏的flag），并且也会触发
 **View.OnSystemUiVisibilityChangeListener**
- 如果你想让系统栏在一段时间后自动隐藏的话，你应该使用**View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY**标签
- 设置**View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY**处理沉浸模式下，用户会向内滑动以展示系统栏，半透明的系统栏会临时的进行显示，
 一段时间后自动隐藏。滑动的操作并不会清空任何标签，也不会触发系统UI可见性的监听器，因为暂时显示的导航栏并不被认为是一种可见的状态


## 沉浸模式

### 沉浸模式选择

- **SYSTEM_UI_FLAG_IMMERSIVE**与**SYSTEM_UI_FLAG_IMMERSIVE_STICKY**都提供了沉浸式的体验
- 如果你在写一款图书浏览器、新闻杂志阅读器，请将IMMERSIVE与SYSTEM_UI_FLAG_FULLSCREEN,
 SYSTEM_UI_FLAG_HIDE_NAVIGATION一起使用。因为用户可能会经常访问Action Bar和一些UI控件，
 又不希望在翻页的时候有其他的东西进行干扰。IMMERSIVE在该种情况下就是个很好的选择。
- 如果你在打造一款真正的沉浸式应用，而且你希望屏幕边缘的区域也可以与用户进行交互，
 并且他们也不会经常访问系统UI。这个时候就要将IMMERSIVE_STICKY和SYSTEM_UI_FLAG_FULLSCREEN，
 SYSTEM_UI_FLAG_HIDE_NAVIGATION两个标签一起使用。比如做一款游戏或者绘图应用就很合适。
- 如果你在打造一款视频播放器，并且需要少量的用户交互操作。你可能就需要之前版本的一些方法了
 （从Android 4.0开始,对于这种应用，简单的使用SYSTEM_UI_FLAG_FULLSCREEN与,
 SYSTEM_UI_FLAG_HIDE_NAVIGATION就足够了，不需要使用immersive标签。


### 使用非STICKY的沉浸模式

- 当你使用SYSTEM_UI_FLAG_IMMERSIVE标签的时候，
 它是**基于(SYSTEM_UI_FLAG_HIDE_NAVIGATION和SYSTEM_UI_FLAG_FULLSCREEN)来隐藏系统栏的**。当用户向内滑动，系统栏重新显示并保持可见。
 基于**(如SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION和SYSTEM_UI_FLAG_LAYOUT_STABLE)**来防止系统栏隐藏时内容区域大小发生变化。
 同时也需要确保**Action Bar和其他系统UI控件同时进行隐藏（Window#FEATURE_ACTION_BAR_OVERLAY）**

- 下面这段代码展示了如何在不改变内容区域大小的情况下，隐藏与显示状态栏和导航栏。

```java
// This snippet hides the system bars.
private void hideSystemUI() {
    // Set the IMMERSIVE flag.
    // Set the content to appear under the system bars so that the content
    // doesn't resize when the system bars hide and show.
    mDecorView.setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION // hide nav bar
            | View.SYSTEM_UI_FLAG_FULLSCREEN // hide status bar
            | View.SYSTEM_UI_FLAG_IMMERSIVE);
}
```

```java
// This snippet shows the system bars. It does this by removing all the flags
// except for the ones that make the content appear under the system bars.
private void showSystemUI() {
    mDecorView.setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN);
}
```

- 你可能同时也希望在如下的几种情况下使用IMMERSIVE标签来提供更好的用户体验：
 1. 注册一个监听器来监听系统UI的变化。
 2. 实现onWindowFocusChanged()函数。如果窗口获取了焦点，你可能需要对系统栏进行隐藏。
  如果窗口失去了焦点，比如说弹出了一个对话框或菜单，你可能需要取消那些将要在Handler.postDelayed()或其他地方的隐藏操作。
 3. 实现一个GestureDetector，它监听了onSingleTapUp(MotionEvent)事件。
 可以使用户点击内容区域来切换系统栏的显示状态。单纯的点击监听可能不是最好的解决方案，
 因为当用户在屏幕上拖动手指的时候（假设点击的内容占据了整个屏幕），这个事件也会被触发。

### STICKY沉浸模式

- 当使用了SYSTEM_UI_FLAG_IMMERSIVE_STICKY标签的时候，向内滑动的操作会让系统栏临时显示，
 并处于半透明的状态。此时没有标签会被清除，系统UI可见性监听器也不会被触发。如果用户没有进行操作，系统栏会在一段时间内自动隐藏。

- 下面是一段实现代码。一旦窗口获取了焦点，只要简单的设置IMMERSIVE_STICKY与上面讨论过的其他标签即可。

```java
@Override
public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
    if (hasFocus) {
        decorView.setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);}
}
```

- 如果你想实现IMMERSIVE_STICKY的自动隐藏效果，同时也需要展示你自己的UI控件。
 你只需要使用IMMERSIVE与Handler.postDelayed()或其他类似的东西，让它几秒后重新进入沉浸模式即可。