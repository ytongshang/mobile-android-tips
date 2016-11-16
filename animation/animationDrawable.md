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

- 注意

  - 如果是在activity中，不能在onCreate（）中播放动画，因为些时，animationDrawable还没有附加到window中
  - 如果一开始就要播放动画，则播放在代码应当写在onWindowFocusChanged()中
  - 使用post方法也可以

- 如果帧动画的帧数非常多，很可能会出现OOM,可以使用view的setBackground与post相接合的方式来解决
