# Canvas基础

[Android中Canvas绘图基础详解](http://blog.csdn.net/iispring/article/details/49770651)

## draw 2d graphics

- 对于不需要经常动态改变的或者不是太在意性能的2d图形绘制，一般在一个view对象中绘制,重写onDraw方法
- 对于需要经常重绘的图形，一般直接通过Canvas对象绘帛，一种是直接调用对应对象的draw法，比如BitmapDraw.draw方法，
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

## 坐标系

### Canvas坐标系

- Canvas坐标系指的是Canvas本身的坐标系，Canvas坐标系有且只有一个，且是唯一不变的
- 其坐标原点在View的左上角，从坐标原点向右为x轴的正半轴，从坐标原点向下为y轴的正半轴。

### 绘图坐标系

- **Canvas的drawXXX方法中传入的各种坐标指的都是绘图坐标系中的坐标**，而非Canvas坐标系中的坐标。
- 默认情况下，绘图坐标系与Canvas坐标系完全重合，即初始状况下，绘图坐标系的坐标原点也在View的左上角，从原点向右为x轴正半轴，从原点向下为y轴正半轴。
- 但不同于Canvas坐标系，绘图坐标系并不是一成不变的，可以通过调用Canvas的translate方法平移坐标系，可以通过Canvas的rotate方法旋转坐标系，还可以通过Canvas的scale方法缩放坐标系，而且需要注意的是，**translate、rotate、scale的操作都是基于当前绘图坐标系的，而不是基于Canvas坐标系**
- **一旦通过以上方法对坐标系进行了操作之后，当前绘图坐标系就变化了，以后绘图都是基于更新的绘图坐标系了**。也就是说，真正对我们绘图有用的是绘图坐标系而非Canvas坐标系。