# MotionEvent

## 文档

- [Android Developer](https://developer.android.com/reference/android/view/MotionEvent.html#ACTION_POINTER_DOWN)

- [MotionEvent](http://www.jianshu.com/p/0c863bbde8eb)

## Pointer

- 一次触摸可能有多个触点，每一个触摸点叫作一个Pointer，每个pointer都有自己的事件类型，也有自己的横轴坐标值

- 一个MotionEvent对象中可能会存储多个pointer的相关信息，每个pointer都会有一个自己的id和index

- 一个Pointer在第一次按下时（ACTION_DOWN 或ACTION_POINTER_DOWN）指定了唯一的id,这个id在整个事件流中都有效，直到抬起（ ACTION_UP or ACTION_POINTER_UP）或者父ViewGroup截取了事件，发给子View的cancal事件（ACTION_CANCEL）

- 但在中整个事件流中，Pointer的index却不一定是相同的，总是介于0 和getPointerCount()-1 之间，可以通过 getPointerId (int pointerIndex)获取其id,也可以通过findPointerIndex(int id) 查询其index

- 由于pointer的index值在不同的MotionEvent对象中会发生变化，但是id值却不会变化。所以，当我们要记录一个触摸点的事件流时，就只需要保存其id,然后使用findPointerIndex(int)来获得其index值，然后再获得其他信息

  ```java
    private final static int INVALID_ID = -1;
    private int mActivePointerId = INVALID_ID;
    private int mSecondaryPointerId = INVALID_ID;
    private float mPrimaryLastX = -1;
    private float mPrimaryLastY = -1;
    private float mSecondaryLastX = -1;
    private float mSecondaryLastY = -1;
    public boolean onTouchEvent(MotionEvent event) {
        int action = MotionEventCompat.getActionMasked(event);

        switch (action) {
            case MotionEvent.ACTION_DOWN:
                int index = event.getActionIndex();
                mActivePointerId = event.getPointerId(index);
                mPrimaryLastX = MotionEventCompat.getX(event,index);
                mPrimaryLastY = MotionEventCompat.getY(event,index);
                break;
            case MotionEvent.ACTION_POINTER_DOWN:
                index = event.getActionIndex();
                mSecondaryPointerId = event.getPointerId(index);
                mSecondaryLastX = event.getX(index);
                mSecondaryLastY = event.getY(index);
                break;
            case MotionEvent.ACTION_MOVE:
                index = event.findPointerIndex(mActivePointerId);
                int secondaryIndex = MotionEventCompat.findPointerIndex(event,mSecondaryPointerId);
                final float x = MotionEventCompat.getX(event,index);
                final float y = MotionEventCompat.getY(event,index);
                final float secondX = MotionEventCompat.getX(event,secondaryIndex);
                final float secondY = MotionEventCompat.getY(event,secondaryIndex);
                break;
            case MotionEvent.ACTION_POINTER_UP:
                xxxxxx
                break;
            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_CANCEL:
                mActivePointerId = INVALID_ID;
                mPrimaryLastX =-1;
                mPrimaryLastY = -1;
                break;
        }
        return true;
    }
  ```

- 除了pointer的概念，MotionEvent还引入了两个事件类型

  - ACTION_POINTER_DOWN:代表用户又使用一个手指触摸到屏幕上，也就是说，在已经有一个触摸点的情况下，有新出现了一个触摸点。
  - ACTION_POINTER_UP:代表用户的一个手指离开了触摸屏，但是还有其他手指还在触摸屏上。也就是说，在多个触摸点存在的情况下，其中一个触摸点消失了。它与ACTION_UP的区别就是，它是在多个触摸点中的一个触摸点消失时（此时，还有触摸点存在，也就是说用户还有手指触摸屏幕）产生，而ACTION_UP可以说是最后一个触摸点消失时产生。

## getAction 和 getActionMasked

- 一个MotionEvent对象中可以包含多个触摸点的事件。当MotionEvent对象只包含一个触摸点的事件时，上边两个函数的结果是相同的，但是当包含多个触摸点时，二者的结果就不同啦

- getAction获得的int值是由pointer的index值和事件类型值组合而成的，而getActionWithMasked则只返回事件的类型值

## 批处理

- 为了效率，Android系统在处理ACTION_MOVE事件时会将连续的几个多触点移动事件打包到一个MotionEvent对象中。我们可以通过getX(int)和getY(int)来获得最近发生的一个触摸点事件的坐标，然后使用getHistorical(int,int)和getHistorical(int,int)来获得时间稍早的触点事件的坐标，二者是发生时间先后的关系

  ```java
  void printSamples(MotionEvent ev) {
     final int historySize = ev.getHistorySize();
     final int pointerCount = ev.getPointerCount();
     for (int h = 0; h < historySize; h++) {
         System.out.printf("At time %d:", ev.getHistoricalEventTime(h));
         for (int p = 0; p < pointerCount; p++) {
             System.out.printf("  pointer %d: (%f,%f)",
                 ev.getPointerId(p), ev.getHistoricalX(p, h), ev.getHistoricalY(p, h));
         }
     }
     System.out.printf("At time %d:", ev.getEventTime());
     for (int p = 0; p < pointerCount; p++) {
         System.out.printf("  pointer %d: (%f,%f)",
             ev.getPointerId(p), ev.getX(p), ev.getY(p));
     }
  }
  ```

## 坐标问题

- getX()是表示Widget相对于自身左上角的x坐标,而getRawX()是表示相对于屏幕左上角的x坐标值(注意:这个屏幕左上角是手机屏幕左上角,不管activity是否有titleBar或是否全屏幕),getY(),getRawY()一样的道理
