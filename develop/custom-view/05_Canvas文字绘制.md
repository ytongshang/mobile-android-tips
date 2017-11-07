# Canvas的文字绘制

## Paint.FontMetrics

[FontMetrics](https://stackoverflow.com/questions/27631736/meaning-of-top-ascent-baseline-descent-bottom-and-leading-in-androids-font)

```java
public static class FontMetrics {
    /**
    * The maximum distance above the baseline for the tallest glyph in
    * the font at a given text size.
    */
    public float   top;
    /**
    * The recommended distance above the baseline for singled spaced text.
    */
    public float   ascent;
    /**
    * The recommended distance below the baseline for singled spaced text.
    */
    public float   descent;
    /**
    * The maximum distance below the baseline for the lowest glyph in
    * the font at a given text size.
    */
    public float   bottom;
    /**
    * The recommended additional space to add between lines of text.
    */
    public float   leading;
}
```

![FontMetrics](./../../image-resources/customview/canvas/FontMetrics.jpg)

- **BaseLine**：基准线
- **ascent / descent**: 上图中绿色和橙色的线，它们的作用是限制普通字符的顶部和底部范围.
 普通的字符，上不会高过 ascent ，下不会低过 descent ，例如上图中大部分的字形都显示在  ascent 和 descent 两条线的范围内。具体到 Android 的绘制中， **ascent** 的值是图中绿线和  baseline 的相对位移，**它的值为负（因为它在 baseline 的上方）**； **descent** 的值是图中橙线和  baseline 相对位移，**值为正（因为它在 baseline 的下方）**
- **top / bottom**: 上图中蓝色和红色的线，**它们的作用是限制所有字形（ glyph ）的顶部和底部范围**。
 除了普通字符，有些字形的显示范围是会超过 ascent 和 descent 的，而 top 和 bottom 则限制的是所有字形的显示范围，包括这些特殊字形。例如上图的第二行文字里，就有两个泰文的字形分别超过了 ascent 和 descent 的限制，但它们都在 top 和 bottom 两条线的范围内。具体到 Android 的绘制中， top 的值是图中蓝线和 baseline 的相对位移，它的值为负（因为它在 baseline 的上方）；  bottom 的值是图中红线和 baseline 相对位移，值为正（因为它在 baseline 的下方）。
- **leading**: 这个词在上图中没有标记出来，因为它并不是指的某条线和 baseline 的相对位移。  **leading 指的是行的额外间距，即对于上下相邻的两行，上行的 bottom 线和下行的 top 线的距离**，也就是上图中第一行的红线和第二行的蓝线的距离
- **因为坐标系的关系，baseline向下为正，向右为正，所以bottom与top之间的距离应当为bottom-top**

## drawText

- 将文字从位置(x,y)开始绘制，**其中x并不是第一个字符左侧的坐标，而是第一个字符左侧稍稍偏左的位置**，字符的左右两边会留出一部分空隙，用于文字之间的间隔，以及文字和边框的间隔
- **而y是文字的基准线的坐标，并不是字符上面／下面的坐标**

```java
// 第一类
public void drawText(@NonNull char[] text, int index, int count, float x, float y,@NonNull Paint paint)
public void drawText(@NonNull CharSequence text, int start, int end, float x, float y,@NonNull Paint paint)
public void drawText(@NonNull String text, int start, int end, float x, float y, @NonNull Paint paint)
public void drawText(@NonNull String text, float x, float y, @NonNull Paint paint)

//第二类
//text：要绘制的文字
//start：从那个字开始绘制
//end：绘制到哪个字结束
//contextStart：上下文的起始位置。contextStart 需要小于等于 start
//contextEnd：上下文的结束位置。contextEnd 需要大于等于 end
//x：文字左边的坐标
//y：文字的基线坐标
//isRtl：是否是 RTL（Right-To-Left，从右向左）
public void drawTextRun(@NonNull CharSequence text, int start, int end, int contextStart,
            int contextEnd, float x, float y, boolean isRtl, @NonNull Paint paint)
public void drawTextRun(@NonNull char[] text, int index, int count, int contextIndex,
            int contextCount, float x, float y, boolean isRtl, @NonNull Paint paint)

// 第三类
public void drawTextOnPath (String text, Path path, float hOffset, float vOffset, Paint paint)
public void drawTextOnPath (char[] text, int index, int count, Path path, float hOffset, float vOffset, Paint paint)

// 第四类
@Deprecated
public void drawPosText(@NonNull String text, @NonNull @Size(multiple=2) float[] pos, @NonNull Paint paint)

@Deprecated
public void drawPosText(@NonNull char[] text, int index, int count,
            @NonNull @Size(multiple=2) float[] pos,@NonNull Paint paint)

```

### 第一类

- 第一类可以指定了文本开始的位置，可以截取文本中部分内容进行绘制

### 第二类

- 文字在不同上下文可能有不同的显示方式
- RTL的支持

### 第三类

- 与 Path相关
- **drawTextOnPath() 使用的 Path ，拐弯处全用圆角，别用尖角**，也就是说Paint.setPathEffect(CornorPathEffect effect)

### 第四类

- **必须指定每一个字符的位置，来绘制文本**
- 不建议使用，标记为Deprecated

序号 | 反对理由
-----|-------------------------------------------------
1    | 必须指定所有字符位置，否则直接crash掉，反人类设计
2    | 性能不佳，在大量使用的时候可能导致卡顿
3    | 不支持emoji等特殊字符，不支持字形组合与分解

- 绘制文字时，文字的位置由Canvas确定，但是文字的大小，字体等由Paint确定

标题 | 相关方法                  | 备注
-----|---------------------------|-----------------------------------------------------
色彩 | setColor setARGB setAlpha | 设置颜色，透明度
大小 | setTextSize               | 设置文本字体大小
字体 | setTypeface               | 设置或清除字体样式
样式 | setStyle                  | 填充(FILL),描边(STROKE),填充加描边(FILL_AND_STROKE)
对齐 | setTextAlign              | 左对齐(LEFT),居中对齐(CENTER),右对齐(RIGHT)
测量 | measureText               | 测量文本大小(注意，请在设置完文本各项参数后调用)
