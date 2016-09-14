# Activity的事件分发

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

- onUserInteraction默认不执行任何动作，主要是在有Down事件，回调该函数，我们可以自定义其行为

- getWindow().superDispatchTouchEvent(ev),通过调用到Activity所属Window的superDispatchTouchEvent，进而调用到Window的DecorView的superDispatchTouchEvent，进一步的又调用到ViewGroup的dispatchTouchEvent()。

- 如果Activity所包含的视图拦截或者消费了该触摸事件的话，就不会再执行Activity的onTouchEvent()； 如果Activity所包含的视图没有拦截或者消费该触摸事件的话，则会执行Activity的onTouchEvent()。

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

  1. 该方法主要是针对dialog形式的activity,Activity中的onTouchEvent是Activity自身对触摸事件的处理。如果该Activity的android:windowCloseOnTouchOutside属性为true，并且当前触摸事件是ACTION_DOWN，而且该触摸事件的坐标在Activity之外，同时Activity还包含了视图的话；就会导致Activity被结束
