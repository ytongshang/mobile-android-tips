# Canvas对绘制的辅助

## Canvas坐标系

- Canvas坐标系指的是Canvas本身的坐标系，Canvas坐标系有且只有一个，且是唯一不变的
- 其坐标原点在View的左上角，从坐标原点向右为x轴的正半轴，从坐标原点向下为y轴的正半轴。

## 绘图坐标系

- **Canvas的drawXXX方法中传入的各种坐标指的都是绘图坐标系中的坐标**，而非Canvas坐标系中的坐标。
- 默认情况下，绘图坐标系与Canvas坐标系完全重合，即初始状况下，绘图坐标系的坐标原点也在View的左上角，从原点向右为x轴正半轴，从原点向下为y轴正半轴。
- 但不同于Canvas坐标系，绘图坐标系并不是一成不变的，可以通过调用Canvas的translate方法平移坐标系，可以通过Canvas的rotate方法旋转坐标系，还可以通过Canvas的scale方法缩放坐标系.
- 需要注意的是，**translate、rotate、scale的操作都是基于当前绘图坐标系的，而不是基于Canvas坐标系**
- **一旦通过以上方法对坐标系进行了操作之后，当前绘图坐标系就变化了，以后绘图都是基于更新的绘图坐标系了**。也就是说，真正对我们绘图有用的是绘图坐标系而非Canvas坐标系。

- **所有的画布操作都只影响后续的绘制，对之前已经绘制过的内容没有影响**

## Save与Restore

- 所有对画布的操作都是不可逆的，这会造成很多麻烦，比如，我们为了实现一些效果不得不对画布进行操作，但操作完了，画布状态也改变了，这会严重影响到后面的画图操作。
- 通过save与Restore对画布的大小和状态（旋转角度、扭曲等）进行实时保存和恢复

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

## 裁剪

- 裁剪画布是利用Clip系列函数，通过与Rect、Path取交、并、差等集合运算来获得最新的画布形状。
- **其中的坐标系都是采用的是local坐标系，也就是绘图坐标系**

```java
boolean clipRect(Rect rect)
boolean clipRect(RectF rect)
boolean clipRect(int left, int top, int right, int bottom)
boolean clipRect(float left, float top, float right, float bottom)
boolean clipRect(Rect rect, Region.Op op)
boolean clipRect(RectF rect, Region.Op op)
boolean clipRect(float left, float top, float right, float bottom, Region.Op op)

boolean clipPath(Path path)
boolean clipPath(Path path, Region.Op op)
```

```java
public enum Op {
    DIFFERENCE(0),
    INTERSECT(1),
    UNION(2),
    XOR(3),
    REVERSE_DIFFERENCE(4),
    REPLACE(5);
}
```

- **如果后续需要恢复原来的canvas，使用save与restore方法**

```java
canvas.save();
canvas.clipRect(left, top, right, bottom);
canvas.drawBitmap(bitmap, x, y, paint);
canvas.restore();
```

## Canvas常见的二维变换

### 使用总结

- **使用 Canvas 来做常见的二维变换**
- **使用 Matrix 来做常见和不常见的二维变换**
- **使用 Camera 来做三维变换**
- **在Canvas中如果有多个二维变换操作，代码顺序必须与实际的二维变化操作相关**
 **也就是如果想先移动后旋转，那么代码应当是先旋转后移动**

### Translate

```java
public void translate(float dx, float dy) {
    native_translate(mNativeCanvasWrapper, dx, dy);
}
```

- float dx：**水平方向平移的距离，正数指向正方向（向右）平移的量，负数为向负方向（向左）平移的量**
- flaot dy：**垂直方向平移的距离，正数指向正方向（向下）平移的量，负数为向负方向（向上）平移的量**

### Rotate

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

### Scale

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

### Skew(斜切)

```java
public void skew(float sx, float sy) {
    native_skew(mNativeCanvasWrapper, sx, sy);
}
```

- float sx:将画布在x方向上倾斜相应的角度，sx倾斜角度的tan值，
- float sy:将画布在y轴方向上倾斜相应的角度，sy为倾斜角度的tan值.

## Matrix

- 在使用Matrix，**一般情况下我们要通过创建一个新的Matrix，或者调用现在Matrix.reset()方法将其变为单位矩阵**
- 使用Matrix的步骤
    - 创建 Matrix 对象
    - 调用 Matrix 的 pre/postTranslate/Rotate/Scale/Skew() 方法来设置几何变换；
    - 使用 Canvas.setMatrix(matrix) 或 Canvas.concat(matrix) 来把几何变换应用到 Canvas，一般情况下使用Canvas.concat(matrix)

### set pre post

- 对于四种基本变换 平移(translate)、缩放(scale)、旋转(rotate)、 错切(skew) 它们每一种都三种操作方法，分别为 设置(set)、 前乘(pre) 和 后乘 (post)。
- 而它们的基础是Concat，通过先构造出特殊矩阵然后用原始矩阵Concat特殊矩阵，达到变换的结果。

方法 | 简介
-----|---------------------------------------------------
set  | 设置，会覆盖掉之前的数值，导致之前的操作失效。
pre  | 前乘，相当于矩阵的右乘， M' = M * S (S指为特殊矩阵)
post | 后乘，相当于矩阵的左乘，M' = S * M （S指为特殊矩阵）

### setPolyToPoly

### setRectToRect

- - 简单来说就是将源矩形的内容填充到目标矩形中，然而在大多数的情况下，源矩形和目标矩形的长宽比是不一致的，到底该如何填充呢，这个填充的模式就由第三个参数 stf 来确定。

```java
```

## Camera

### 相关资料

- [Matrix Camera](http://www.gcssloop.com/customview/matrix-3d-camera)

## SaveLayerXXX

- 我们之前讲解的绘制操作和画布操作都是在默认图层上进行的。
- 在通常情况下，使用默认图层就可满足需求，但是如果需要绘制比较复杂的内容，
 如地图则分图层绘制比较好一些。
- **通过saveLayerXXX来保存一个图层**
- saveLayerXxx方法会让你花费更多的时间去渲染图像(图层多了相互之间叠加会导致计算量成倍增长)，使用前请谨慎，如果可能，尽量避免使用
- 使用saveLayerXxx方法，也会将图层状态也放入状态栈中，**同样使用restore方法进行恢复**