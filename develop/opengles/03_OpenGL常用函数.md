# OpenGL常用函数

## glVertexAttribPointer

```java
void glVertexAttribPointer( GLuint index, GLint size, GLenum type,GLboolean normalized, GLsizei stride,const GLvoid * pointer);
```

- **index**:指定要修改的顶点属性的索引值
- **size**,指定每个顶点属性的组件数量。必须为1、2、3或者4。初始值为4。（如position是由3个（x,y,z）组成，而颜色是4个（r,g,b,a））
- **type**,指定数组中每个组件的数据类型。可用的符号常量有GL_BYTE, GL_UNSIGNED_BYTE, GL_SHORT,GL_UNSIGNED_SHORT, GL_FIXED, 和 GL_FLOAT，初始值为GL_FLOAT。
- **normalized**,指定当被访问时，固定点数据值是否应该被归一化（GL_TRUE）或者直接转换为固定点值（GL_FALSE)，这个参
- **stride**,指定连续顶点属性之间的偏移量。如果为0，那么顶点属性会被理解为：它们是紧密排列在一起的。初始值为0。
- **pointer**,指定第一个组件在数组的第一个顶点属性中的偏移量。该数组与GL_ARRAY_BUFFER绑定，储存于缓冲区中。初始值为0；

## glDrawArrays(GLenum mode, GLint first, GLsizei count)

- 第一个参数表示绘制mode

mode                  | 描述
----------------------|------------------------------------------------------------------
int GL_POINTS         | 将传入的顶点坐标作为单独的点绘制
int GL_LINES          | 将传入的坐标作为单独线条绘制，ABCDEFG六个顶点，绘制AB、CD、EF三条线
int GL_LINE_STRIP     | 将传入的顶点作为折线绘制，ABCD四个顶点，绘制AB、BC、CD三条线
int GL_LINE_LOOP      | 将传入的顶点作为闭合折线绘制，ABCD四个顶点，绘制AB、BC、CD、DA四条线。

- **GL_TRIANGLES**：每三个顶点绘制一个三角形。第一个三角形使用顶点v0,v1,v2,第二个使用v3,v4,v5,以此类推。如果顶点的个数n不是3的倍数，那么最后的1个或者2个顶点会被忽略
- **GL_TRIANGLE_STRIP**：假设起始点的坐标序列号是0，新增的点依次往后增加，那么转换的算法如下：
    - 当所有点数量小于或者等于2时，无法构成三角条带
    - 点号从0开始，(点号n)是偶数时，构成的三角形是 [ n, n+1, n+2]
    - 点号从0开始，(点号n)是奇数时，构成的三角形是 [n, n+2, n+1]
- **GL_TRIANGLE_FAN**：将传入的顶点作为扇面绘制，ABCDEF绘制ABC、ACD、ADE、AEF四个三角形

- first，从数组缓存中的哪一位开始绘制，一般为0。
- count，数组中顶点的数量

## glDrawElements(GLenum mode,GLsizei count,GLenum type,const GLvoid * indices)

```java
    /**
     * @param mode Specifies what kind of primitives to render. Symbolic constants GL_POINTS,              GL_LINE_STRIP, GL_LINE_LOOP, GL_LINES, GL_TRIANGLE_STRIP, GL_TRIANGLE_FAN,              and GL_TRIANGLES are accepted.
     * @param count Specifies the number of elements to be rendered
     * @param type Specifies the type of the values in indices.
     * @param indices Specifies a pointer to the location where the indices are stored.
     */
    public static native void glDrawElements(
        int mode,
        int count,
        int type,
        java.nio.Buffer indices
    );
```

```java
private byte[] mIndices = {
    0, 1, 2, 3, 4,
};

mIndiceBuffer = (ByteBuffer) ByteBuffer.allocateDirect(mIndices.length).put(mIndices).position(0);

GLES20.glDrawElements(
    GLES20.GL_TRIANGLE_STRIP,
    mIndices.length,
    GLES20.GL_UNSIGNED_BYTE,
    mIndiceBuffer
);
```

- count表示从indices中数组中取出多少个索引
