# Activity的事件分发

## dispatchTouchEvent

### dispatchTouchEvent() 源码

  ```java
  public boolean dispatchTouchEvent(MotionEvent ev) {
        if (ev.getAction() == MotionEvent.ACTION_DOWN) {
            onUserInteraction();
        }
        if (getWindow().superDispatchTouchEvent(ev)) {
            return true;
        }
        return onTouchEvent(ev);
    }
  ```

- 首先会触发Activity的dispatchTouchEvent方法。

- 接着会调用getWindow().superDispatchTouchEvent(ev),通过调用到Activity所属Window的superDispatchTouchEvent，进而调用到Window(PhoneWindow)的DecorView的superDispatchTouchEvent，因为DecorView是继承于Framelayout的，进一步的又调用到ViewGroup的dispatchTouchEvent()。

- 事件的分发顺序，先分发给它所包含的View(setContentView())，只有它所属View对事件不感兴趣的话，即返回false,才会分发给Activity

## onUserInteraction() 与onUserLeaveHint()

- onUserLeaveHint 当用户的操作使一个activity准备进入后台时，此 方法会像activity的生命周期的一部分一样被调用。
 例如，当用户按下 Home键， Activity#onUserLeaveHint()将会被回调。
- **但是当来电导致来电activity自动占据前台，Activity#onUserLeaveHint()将不会被回调**。

- onUserLeaveHint() 用户手动离开当前activity，会调用该方法，比如用户主动切换任务，短按home进入桌面等。系统自动切换activity不会调用此方法，如来电，灭屏等。

- onUserInteraction() activity在分发各种事件的时候会调用该方法，注意：启动另一个activity,Activity#onUserInteraction()会被调用两次，一次是activity捕获到事件，
 另一次是调用Activity#onUserLeaveHint()之前会调用Activity#onUserInteraction()。

## onTouchEvent

- activity的onTouchEvent

  ```java
  public boolean onTouchEvent(MotionEvent event) {
        if (mWindow.shouldCloseOnTouch(this, event)) {
            finish();
            return true;
        }

        return false;
    }
  ```

  ```java
    /** @hide */
    public boolean shouldCloseOnTouch(Context context, MotionEvent event) {
        if (mCloseOnTouchOutside && event.getAction() == MotionEvent.ACTION_DOWN
                && isOutOfBounds(context, event) && peekDecorView() != null) {
            return true;
        }
        return false;
    }
  ```

- 如果Activity设置了setFinishOnTouchOutside(true),并且ACTION_DOWN事件在DectorView的范围的外部，触摸事件可以finish掉Activity,相当于Dialog的setCanceledOnTouchOutside，主要用于Dialog形式的Activity

```java
 public void setFinishOnTouchOutside(boolean finish) {
    mWindow.setCloseOnTouchOutside(finish);
 }
```


