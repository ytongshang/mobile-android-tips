# Canvas操作

- **所有的画布操作都只影响后续的绘制，对之前已经绘制过的内容没有影响**

## Canvas坐标系

- Canvas坐标系指的是Canvas本身的坐标系，Canvas坐标系有且只有一个，且是唯一不变的
- 其坐标原点在View的左上角，从坐标原点向右为x轴的正半轴，从坐标原点向下为y轴的正半轴。

## 绘图坐标系

- **Canvas的drawXXX方法中传入的各种坐标指的都是绘图坐标系中的坐标**，而非Canvas坐标系中的坐标。
- 默认情况下，绘图坐标系与Canvas坐标系完全重合，即初始状况下，绘图坐标系的坐标原点也在View的左上角，从原点向右为x轴正半轴，从原点向下为y轴正半轴。
- 但不同于Canvas坐标系，绘图坐标系并不是一成不变的，可以通过调用Canvas的translate方法平移坐标系，可以通过Canvas的rotate方法旋转坐标系，还可以通过Canvas的scale方法缩放坐标系.
- 需要注意的是，**translate、rotate、scale的操作都是基于当前绘图坐标系的，而不是基于Canvas坐标系**
- **一旦通过以上方法对坐标系进行了操作之后，当前绘图坐标系就变化了，以后绘图都是基于更新的绘图坐标系了**。也就是说，真正对我们绘图有用的是绘图坐标系而非Canvas坐标系。

## Translate

```java
public void translate(float dx, float dy) {
    native_translate(mNativeCanvasWrapper, dx, dy);
}
```

- float dx：**水平方向平移的距离，正数指向正方向（向右）平移的量，负数为向负方向（向左）平移的量**
- flaot dy：**垂直方向平移的距离，正数指向正方向（向下）平移的量，负数为向负方向（向上）平移的量**

## Rotate

```java
public void rotate(float degrees) {
    native_rotate(mNativeCanvasWrapper, degrees);
}

public final void rotate(float degrees, float px, float py) {
    translate(px, py);
    rotate(degrees);
    translate(-px, -py);
}
```

- 第一个构造函数直接输入旋转的度数，**正数是顺时针旋转，负数指逆时针旋转，它的旋转中心点是原点（0，0）**
- 第二个构造函数除了度数以外，还可以指定旋转的中心点坐标（px,py）

## Scale

```java
public void scale(float sx, float sy) {
    native_scale(mNativeCanvasWrapper, sx, sy);
}

public final void scale(float sx, float sy, float px, float py) {
    translate(px, py);
    scale(sx, sy);
    translate(-px, -py);
}
```

- 这两个方法中前两个参数是相同的分别为x轴和y轴的缩放比例。而第二种方法比前一种多了两个参数，用来控制缩放中心位置的

- 缩放比例(sx,sy)取值范围详解

取值范围(n) | 说明
------------|--------------------------------------------
[-∞, -1)    | 先根据缩放中心放大n倍，再根据中心轴进行翻转
-1          | 根据缩放中心轴进行翻转
(-1, 0)     | 先根据缩放中心缩小到n，再根据中心轴进行翻转
0           | 不会显示，若sx为0，则宽度为0，不会显示，sy同理
(0, 1)      | 根据缩放中心缩小到n
1           | 没有变化
(1, +∞)     | 根据缩放中心放大n倍

- **当scale的值为负值时，会让canvas坐标轴反向**

## Skew(斜切)

```java
public void skew(float sx, float sy) {
    native_skew(mNativeCanvasWrapper, sx, sy);
}
```

- float sx:将画布在x方向上倾斜相应的角度，sx倾斜角度的tan值，
- float sy:将画布在y轴方向上倾斜相应的角度，sy为倾斜角度的tan值.

## 裁剪画布

- 裁剪画布是利用Clip系列函数，通过与Rect、Path、Region取交、并、差等集合运算来获得最新的画布形状。
- **除了调用Save、Restore函数以外，这个操作是不可逆的，一但Canvas画布被裁剪，就不能再被恢复！**

```java
boolean clipPath(Path path)
boolean clipPath(Path path, Region.Op op)
boolean clipRect(Rect rect, Region.Op op)
boolean clipRect(RectF rect, Region.Op op)
boolean clipRect(int left, int top, int right, int bottom)
boolean clipRect(float left, float top, float right, float bottom)
boolean clipRect(RectF rect)
boolean clipRect(float left, float top, float right, float bottom, Region.Op op)
boolean clipRect(Rect rect)
boolean clipRegion(Region region)
boolean clipRegion(Region region, Region.Op op)
```

## Save与Restore

- 所有对画布的操作都是不可逆的，这会造成很多麻烦，比如，我们为了实现一些效果不得不对画布进行操作，但操作完了，画布状态也改变了，
 这会严重影响到后面的画图操作。通过save与Restore对画布的大小和状态（旋转角度、扭曲等）进行实时保存和恢复就最好了

### 保存的信息SaveFlags

名称                       | 简介
---------------------------|-------------------------------------------------
ALL_SAVE_FLAG              | 默认，保存全部状态
CLIP_SAVE_FLAG             | 保存剪辑区
CLIP_TO_LAYER_SAVE_FLAG    | 剪裁区作为图层保存
FULL_COLOR_LAYER_SAVE_FLAG | 保存图层的全部色彩通道
HAS_ALPHA_LAYER_SAVE_FLAG  | 保存图层的alpha(不透明度)通道
MATRIX_SAVE_FLAG           | 保存Matrix信息( translate, rotate, scale, skew)

### save

```java
public int save(@Saveflags int saveFlags) {
    return native_save(mNativeCanvasWrapper, saveFlags);
}

public int save() {
    return native_save(mNativeCanvasWrapper, MATRIX_SAVE_FLAG | CLIP_SAVE_FLAG);
}
```

### restore

- getSaveCount 获取保存的次数，即状态栈中保存状态的数量
- restore 状态回滚，就是从栈顶取出一个状态然后根据内容进行恢复
- restoreToCount,弹出指定位置以及以上所有状态，并根据指定位置状态进行恢复

```java
int count = canvas.save();
// more calls potentially to save()
canvas.restoreToCount(count);
// now the canvas is back in the same state it was before the initial
// call to save().
```

## SaveLayerXXX

- 我们之前讲解的绘制操作和画布操作都是在默认图层上进行的。
- 在通常情况下，使用默认图层就可满足需求，但是如果需要绘制比较复杂的内容，
 如地图则分图层绘制比较好一些。
- **通过saveLayerXXX来保存一个图层**
- saveLayerXxx方法会让你花费更多的时间去渲染图像(图层多了相互之间叠加会导致计算量成倍增长)，使用前请谨慎，如果可能，尽量避免使用
- 使用saveLayerXxx方法，也会将图层状态也放入状态栈中，**同样使用restore方法进行恢复**