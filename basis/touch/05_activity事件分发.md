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

- 如果Activity设置了setFinishOnTouchOutside(true),并且ACTION_DOWN事件在DectorView的范围的外部，触摸事件可以finish掉Activity,相当于Dialog的setCanceledOnTouchOutside，主要用于Dialog形式的Activity

```java
 public void setFinishOnTouchOutside(boolean finish) {
    mWindow.setCloseOnTouchOutside(finish);
 }
```


