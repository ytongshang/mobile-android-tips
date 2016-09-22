# Activity的事件分发

## dispatchTouchEvent

- 源码

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

- 事件的分发顺序，先分发给它所包含的View(通过setContentView())，只有它所属View对事件不感兴趣的话，即返回false,才会分发给Activity

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

  - 通过检查mCloseOnTouchOutside标记，触摸事件是否为ACTION_DOWN事件，同时判断event的x、y坐标是不是超出Bounds，然后检查FrameLayout的content的id的DecorView不为空， 如果这些都满足的话，则finish掉activity,可以参考Dialog型式的Activity
