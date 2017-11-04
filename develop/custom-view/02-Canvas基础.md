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
- 还可以通过Bitmap自定义一个新的canvas对象,**其中的bitmap对象必须是可以修改的，也就是isMutable()必须返回true**
 绘制完成后，可以将将生成的Bitmap在另一个需要用到Canvas的地方绘制出来Canvas.drawBitmap(...)

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
 当需要强行重绘的时候，调用invalidate()
- 在非UI线程中，如果要强行重绘的话，调用postInvalidate()
- **View的onDraw()方法必须调用super方法**
- 在onDraw()方法，调用各种Canvas.onDraw()方法，也可以调用现有view的onDraw()方法，从而绘制想要绘制的图形

## on surfaceView

- surfaceView是view的子类，其主要目的是可以在其它线程中进行图形的绘制
- 使用surfaceView的方法：继承surfaceView,并且重载SurfaceHolder.Callback方法，方便在surfaceView创建，销毁或者变化时进行对应的操作，**SurfaceHolder.Callback也是一个好的创建绘图线程的地方**
- 应当通过getHolder()得到SurfaceHolder来操作surfaceView对象，而不是直接操作surfaceView,
 比如通过SurfaceHolder.addCallback()传入SurfaceHolder.Callback对象
- **在线程中调用lockCanvas()方法，然后进行绘制，绘制结束后，调用unlockCanvasAndPost()**

## 具体绘制

### 颜色填充

- **这类颜色填充方法一般用于在绘制之前设置底色，或者在绘制之后为界面设置半透明蒙版**

```java
public void drawColor(@ColorInt int color)
public void drawColor(@ColorInt int color, @NonNull PorterDuff.Mode mode)
public void drawRGB(int r, int g, int b)
public void drawARGB(int a, int r, int g, int b)
```

### 圆

```java
public void drawCircle(float cx, float cy, float radius, @NonNull Paint paint)
```

### 椭圆

```java
public void drawOval(@NonNull RectF oval, @NonNull Paint paint)
public void drawOval(float left, float top, float right, float bottom, @NonNull Paint paint)
```

### 矩形

```java
public void drawRect(@NonNull RectF rect, @NonNull Paint paint)
public void drawRect(@NonNull Rect r, @NonNull Paint paint)
public void drawRect(float left, float top, float right, float bottom, @NonNull Paint paint)
```

### 圆角矩形

```java
public void drawRoundRect(@NonNull RectF rect, float rx, float ry, @NonNull Paint paint)
public void drawRoundRect(float left, float top, float right, float bottom, float rx, float ry,
            @NonNull Paint paint)
```

### 点

- 点的大小可以通过 paint.setStrokeWidth(width) 来设置；
- 点的形状可以通过  paint.setStrokeCap(cap) 来设置：ROUND 画出来是圆形的点，SQUARE 或 BUTT 画出来是方形的点

```java
public void drawPoint(float x, float y, @NonNull Paint paint)

// 数组中2个构成一个点的坐标
// 跳过pts前offset个数字，然后共count个绘制，也就绘制count/2个点
public void drawPoints(@Size(multiple = 2) float[] pts, int offset, int count,
            @NonNull Paint paint)
public void drawPoints(@Size(multiple = 2) @NonNull float[] pts, @NonNull Paint paint)
```

```java
float[] points = {0, 0, 50, 50, 50, 100, 100, 50, 100, 100, 150, 50, 150, 100};
// 绘制四个点：(50, 50) (50, 100) (100, 50) (100, 100)
canvas.drawPoints(points, 2 /* 跳过两个数，即前两个 0 */,
          8 /* 一共绘制 8 个数（4 个点）*/, paint);
```

### 线

```java
public void drawLine(float startX, float startY, float stopX, float stopY,@NonNull Paint paint)
public void drawLines(@Size(multiple = 4) @NonNull float[] pts, int offset, int count,
            @NonNull Paint paint)
public void drawLines(@Size(multiple = 4) @NonNull float[] pts, @NonNull Paint paint)
```

### 弧形／扇形

```java
public void drawArc(float left, float top, float right, float bottom, float startAngle,
            float sweepAngle, boolean useCenter, @NonNull Paint paint)
public void drawArc(@NonNull RectF oval, float startAngle, float sweepAngle, boolean useCenter,
            @NonNull Paint paint)
```

- drawArc() 是使用一个椭圆来描述弧形的,left, top, right, bottom 描述的是这个弧形所在的椭圆；
- startAngle 是弧形的起始角度（x 轴的正向，即正右的方向，是 0 度的位置；顺时针为正角度，逆时针为负角度)
- sweepAngle 是弧形划过的角度
- **useCenter 表示是否连接到圆心，如果不连接到圆心，就是弧形，如果连接到圆心，就是扇形。**
