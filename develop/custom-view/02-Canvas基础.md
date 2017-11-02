# Canvas基础

[Android中Canvas绘图基础详解](http://blog.csdn.net/iispring/article/details/49770651)

- [draw 2d graphics](#draw-2d-graphics)
- [获得Canvas方法](#获得canvas方法)
- [在View中绘制](#在view中绘制)
- [on surfaceView](#on-surfaceview)
- [坐标系](#坐标系)
    - [Canvas坐标系](#canvas坐标系)
    - [绘图坐标系](#绘图坐标系)

## draw 2d graphics

- 对于不需要经常动态改变的或者不是太在意性能的2d图形绘制，一般在一个view对象中绘制,重写onDraw方法
- 对于需要经常重绘的图形，一般直接通过Canvas对象绘制，一种是直接调用对应对象的draw法，比如Bitmap的draw方法，
 另一种方法是调用Canvas对应的draw方法

## 获得Canvas方法

- 重写View的onDraw()方法，canvas对象会被作为参数传进来
- 通过SurfaceHolder.lockCanvas()获得canvas对象
- 还可以通过Bitmap自定义一个新的canvas对象,绘制完成后，可以将将生成的Bitmap在另一个需要用到Canvas的地方绘制出来
 Canvas.drawBitmap(...)

```java
Bitmap b = Bitmap.createBitmap(100, 100, Bitmap.Config.ARGB_8888);
Canvas c = new Canvas(b);
// 完成绘制

// 在另一处绘制的地方，比如View.onDraw,SufaceView中
public void onDraw(Canvas canvas) {
    //调用前面生成的bitmap的draw方法
    canvas.drawBitmap(b);
}
```

## 在View中绘制

- 当不是大量的图形绘制，或者需要考虑性能时，使用Canvas的好的方法是继承view对象，然后重写onDraw()，
- 当需要强行重绘的时候，调用invalidate()
- 在onDraw()方法，调用各种Canvas.onDraw()方法，也可以调用现有view的onDraw()方法，从而绘制想要绘制的图形
- 在非UI线程中，如果要强行重绘的话，调用postInvalidate()

## on surfaceView

- surfaceView是view的子类，其主要目的是可以在其它线程中进行图形的绘制
- 使用surfaceView的方法：继承surfaceView,并且重载SurfaceHolder.Callback方法，方便在surfaceView创建，销毁或者变化时进行对应的操作，
 SurfaceHolder.Callback也是一个好的创建绘图线程的地方
- 应当通过getHolder()得到SurfaceHolder来操作surfaceView对象，而不是直接操作surfaceView,
 比如通过SurfaceHolder.addCallback()传入SurfaceHolder.Callback对象
- 在第二线程中调用lockCanvas()方法，然后进行绘制，绘制结束后，调用unlockCanvasAndPost()
