#### 事件分发的相关api
```
1. Activity中的触摸事件API
public boolean dispatchTouchEvent(MotionEvent ev)；
public boolean onTouchEvent(MotionEvent ev);

2. ViewGroup中的触摸事件API
public boolean dispatchTouchEvent(MotionEvent ev)；
public boolean onTouchEvent(MotionEvent ev);
public boolean onInterceptTouchEvent(MotionEvent ev);

3. View中的触摸事件API
public boolean dispatchTouchEvent(MotionEvent ev)；
public boolean onTouchEvent(MotionEvent ev);

```
* **dispatchTouchEvent**：它是传递触摸事件的接口。
  1. Activity将触摸事件传递给ViewGroup，ViewGroup将触摸事件传递给另一个ViewGroup，以及ViewGroup将触摸事件传递给View；这些都是通过dispatchTouchEvent()来传递的。
  2. dispatchTouchEvent(), onInterceptTouchEvent(), onTouchEvent()以及onTouch()它们之间的联系，都是通过dispatchTouchEvent()体现的。它们都是在dispatchTouchEvent()中调度的.
  3. 返回值：true，表示触摸事件被消费了；false，则表示触摸事件没有被消费。


* **onTouchEvent**：它是处理触摸事件的接口。
  1. 无论是Activity, ViewGroup还是View，对触摸事件的处理，基本上都是在onTouchEvent()中进行的。因此，我们说它是处理触摸事件的接口。
  2. 返回值：返回true，表示触摸事件被它处理过了；或者，换句话说，表示它消费了触摸事件。否则，表示它没有消费该触摸事件。


* **onInterceptTouchEvent**：它是拦截触摸事件的接口。
  1. 只有ViewGroup中才有该接口。如果ViewGroup不想将触摸事件传递给它的子View，则可以在onInterceptTouchEvent中进行拦截。
  2. 返回值：true，表示ViewGroup拦截了该触摸事件；那么，该事件就不会分发给它的子View或者子ViewGroup。否则，表示ViewGroup没有拦截该事件，该事件就会分发给它的子View和子ViewGroup。
