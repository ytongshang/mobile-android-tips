# GLSL

## 参考资料

- [GLSL](https://learnopengl-cn.github.io/01%20Getting%20started/05%20Shaders/)
- [GLSL 中文手册](https://github.com/wshxbqq/GLSL-Card)

## 简介

- 着色器是使用一种叫GLSL的类C语言写成的
- GLSL是为图形计算量身定制的，它包含一些针对向量和矩阵操作的有用特性。
- 着色器的开头总是要声明版本，接着是输入和输出变量、uniform和main函数。
- 每个着色器的入口点都是main函数，在这个函数中我们处理所有的输入变量，并将结果输出到输出变量中

```glsl
// 典型的着色器代码结构
#version version_number es
in type in_variable_name;
in type in_variable_name;

out type out_variable_name;

uniform type uniform_name;

int main()
{
  // 处理输入并进行一些图形操作
  ...
  // 输出处理过的结果到输出变量
  out_variable_name = weird_stuff_we_processed;
}
```

## 数据类型

- 基础数据类型：void, bool,int,uint,float
- 数组，但是只支持1维数组,float foo[3]
- 结构体与C语言一样,struct type-name{}
- 两种容器类型，向量与矩阵
- sampler2D 2D纹理
- samplerCube  盒纹理 cube mapped texture

## 浮点精度

- 精度限定符可以用于指定任何基于浮点数或者整数的变量的精度
    - lowp：低精度。
    - mediump：中精度。
    - highp：高精度。

```glsl
highp vec4 position;
mediump float specularExp;
```

- 默认精度，如果变量声明时没有使用精度限定符，它将拥有该类型的默认精度，**默认精度限定符在顶点或者片段着色器的开头用如下语法指定**

```glsl
precision highp float;
precision mediump int;
```

- **顶点着色器中，如果没有指定默认精度，则int 和float的默认精度都为highp,片段着色器中，每个着色器必须声明一个默认的float精度，或者为每个float变量指定精度**

### 向量与矩阵

- 向量是一个可以包含有1、2、3或者4个分量的容器
- 分量存储的类型可以bool,int,uint,float中的一种

| 类型  | 含义                       |
|-------|----------------------------|
| vecn  | 包含n个float分量的默认向量 |
| bvecn | 包含n个bool分量的向量      |
| ivecn | 包含n个int分量的向量       |
| uvecn | 包含n个uint分量的向量      |

-   {x,y,z,w}, {r,g,b,a},{s,t,p,q}读取向量的值，但不能混用
-   也可以用下标方问，[0]对应x,[1]对应y

```glsl
vec2 someVec;
vec4 differentVec = someVec.xyxx;
vec3 anotherVec = differentVec.zyw;
vec4 otherVec = someVec.xxxx + anotherVec.yxzy;

vec2 vect = vec2(0.5, 0.7);
vec4 result = vec4(vect, 0.0, 0.0);
vec4 otherResult = vec4(result.xyz, 1.0);
```

- **GLSL中的向量表示竖向量，所以与矩阵相乘进行变换时，矩阵在前，向量在后（与DirectX正好相反）**
- **openglES中矩阵以列优先顺序存储**
- **矩阵可以被看成一些向量组成，单独的列可以用数组下标[]选择，然后每个向量可以通过向量访问行为一访问**

```glsl
// 1.0被放到对象线上，下面将创建一个4*4的单位矩阵
mat4 myMat4 = mat4(1.0)
```

## 常量

- const编译期就确定的常量

| 修饰符    | 说明                                                                                           |
|-----------|------------------------------------------------------------------------------------------------|
| none      | (默认的可省略)本地变量,可读可写,函数的输入参数既是这种类型                                     |
| const     | 声明变量或函数的参数为只读类型                                                                 |
| attribute | 只能存在于vertex shader中,一般用于保存顶点或法线数据,它可以在数据缓冲区中读取数据              |
| uniform   | 在运行时shader无法改变uniform变量, 一般用来放置程序传递给shader的变换矩阵，材质，光照参数等等. |
| varying   | 主要负责在vertex 和 fragment 之间传递量                                                        |


```glsl
const float zero = 0.0
```

## Struct

- 当我们谈论到顶点着色器的时候，每个输入变量也叫顶点属性(Vertex Attribute)。
- 我们能声明的顶点属性是有上限的，它一般由硬件来决定。OpenGL确保至少有16个包含4分量的顶点属性可用，但是有些硬件或许允许更多的顶点属性,可以通过以下方法查明
- **attribute变量是只能在vertex shader中使用的变量**。一般用attribute变量来表示一些顶点的数据，如：顶点坐标，法线，纹理坐标，顶点颜色等,**不能在fragment shader中声明attribute变量，也不能被fragment shader中使用**
- glGetAttribLocation获得vertex shader中attribute变量的index, 使用glVertexAttribPointer为每个attribute变量赋值

```glsl
struct fogStruct {
    vect4 color;
    float start;
    float end;
} fogVar;
fogVar = fogStruct(
    vect4(0.0, 1.0, 0.0, 1.0),
    0.5,
    1.0
)
```

- 当我们谈论到顶点着色器的时候，每个输入变量也叫顶点属性(Vertex Attribute)。
- 我们能声明的顶点属性是有上限的，它一般由硬件来决定。OpenGL确保至少有16个包含4分量的顶点属性可用，但是有些硬件或许允许更多的顶点属性,可以通过以下方法查明

## 类型转换

- **GLSL的类型转换与C不同。在GLSL中类型不可以自动提升，可以用内置函数来进行转换**

```glsl
float a = 1;  // 错误，不能自动转换类型
float a = (float) 1; // 错误，不能强制转换
float a = float(1); // 正确，内置函数进行转换
```

## 函数

- 修饰符，定义是否可以修改形参
    - in, 按值传递，函数不能修改, 函数参数没有指定时，默认修饰符是in
    - inout，变量按照引用传递，如果该值被修改，它将在函数退出时变化
    - out, 该变量不被传入函数，但是在函数返回时将被修改
- **不允许出现递归函数，因为 GPU没有堆栈**

```glsl
vect4 myFunc(inout float myFloat,
out vect4 myVect4,
mat4 myMat4
)
```

## Uniform

- 存储应用程序通过OpenGL ES 3.0 API传入着色器的只读值
- 首先，**uniform是全局的(Global)，如果顶点着色器与片段着色器一起链接到同一个程序对象，它们会共享同一组统一变量，所以在顶点着色器与片段着色器声明同一名字的统一变量，那么它们的类型必须相同**
- 第二，**无论你把uniform值设置成什么，uniform会一直保存它们的数据，直到它们被重置或更新**
- **如果你声明了一个uniform却在GLSL代码中没用过，编译器会静默移除这个变量，导致最后编译出的版本中并不会包含它，这可能导致几个非常麻烦的错误，记住这点！**

### 使用Uniform

- 在glsl代码中定义uniform
- 通过glGetUniformLocation获得Uniform的地址
- 通过glUniform4f等其它方法设置它的值
- 在着色器程序的任意着色器器使用uniform
- 因为OpenGL在其核心是一个C库，所以它**不支持类型重载**，在函数参数不同的时候就要为其定义新的函数；glUniform是一个典型例子。这个函数有一个特定的后缀，标识设定的uniform的类型。可能的后缀有：

| 后缀 | 含义                                 |
|------|--------------------------------------|
| f    | 函数需要一个float作为它的值          |
| i    | 函数需要一个int作为它的值            |
| ui   | 函数需要一个unsigned int作为它的值   |
| 3f   | 函数需要3个float作为它的值           |
| fv   | 函数需要一个float向量/数组作为它的值 |

```glsl
precision mediump float;
uniform vec4 vColor;
void main() {
    gl_FragColor = vColor;
}
```

```java
public class Triangle {
    private static final int COORDS_PER_VERTEX = 3;

    private final float vertices[] = {
            0.0f, 0.5f, 0.0f, // top
            -0.5f, 0.0f, 0.0f, // bottom left
            0.5f, 0.0f, 0.0f  // bottom right
    };
    private final int vertexCount = vertices.length / COORDS_PER_VERTEX;

    private FloatBuffer vertexBuffer;

    private float color[] = {1.0f, 0.0f, 0.0f, 1.0f};

    private int glProgram;
    private int glPositionHandle;
    private int glColorHandle;

    private final Context context;

    public Triangle(Context c) {
        context = c;
        initData();
        initShader();
    }

    private void initData() {
        ByteBuffer vb = ByteBuffer.allocateDirect(vertices.length * 4);
        vb.order(ByteOrder.nativeOrder());
        vertexBuffer = vb.asFloatBuffer();
        vertexBuffer.put(vertices);
        vertexBuffer.position(0);
    }

    private void initShader() {
        glProgram = ShaderHelper.buildProgram(
                GLUtils.readFromAssets(context, "basic_vertex_shader.glsl"),
                GLUtils.readFromAssets(context, "basic_fragment_shader.glsl"));
        // opengles 2.0, 3.0直接用layout指定location
        glPositionHandle = GLES20.glGetAttribLocation(glProgram, "vPosition");
        // 获得uniform vColor的地址
        glColorHandle = GLES20.glGetUniformLocation(glProgram, "vColor");
    }

    public void draw() {
        // 必须先调用glUseProgram后面才能设置uniform的值
        GLES20.glUseProgram(glProgram);

        GLES20.glEnableVertexAttribArray(glPositionHandle);
        GLES20.glVertexAttribPointer(glPositionHandle, COORDS_PER_VERTEX,
                GLES20.GL_FLOAT, false,
                COORDS_PER_VERTEX * 4, vertexBuffer);
        // 设置uniform vColor的值
        GLES20.glUniform4fv(glColorHandle, 1, color, 0);
        GLES20.glDrawArrays(GLES20.GL_TRIANGLES, 0, vertexCount);
        GLES20.glDisableVertexAttribArray(glPositionHandle);
    }
}
```

## 顶点和片段着色器的输入与输出

-   顶点着色器的输入与片段着色器的输出可以指定layout限定符
-   **顶点着色器的输出与片段着色器的输入不可以指定layout限定符**
-   输入in,输出out
-   **每个顶点着色器将在一个或多个输出变量中输出需要传递给片段着色器的数据，然后，这些变量也会在片段着色器中声明为in变量**

```glsl
```

## 插值限定符

- **默认的插值行为是执行平滑着色，也就是说来是顶点的着色器输出变量在图元中线性插值，片段着色器接收线性插值之后的数值作为输入**
- 平面着色，图元中的值没有进行插值，而是将其中一个顶点视为驱动顶点，该顶点的值被用于图元中的所有片段
- centroid(centroid samping),用于强制插值发生在被渲染图元的内部，否则，在图元的边缘可能出现伪像

```glsl
// 默认行为，线性插值
// Vertex shader
smooth out vec3 v_color;
// Fragment shader
smooth in vec3 v_color;

// 指定行为，平面着色
flat out vec3 v_color;
flat in vec3 v_color;

smooth centroid out vec3 v_color;
smooth centroid in vec3 v_color
```

## 预处理

- extension
- 行为：
    - require, 必须的，不支持将抛错
    - enable，启动
    - warn，使用了则会警告
    - disable， 禁用

```glsl
#extension extension_name : behavior
#extension all: behavior

#extension GL_OES_EGL_image_external : require
```

## 不变性

-   invariant,可以用于任何可变的顶点着色器输出，避免因为精度导致的微小的偏移
-   可以用于自己定义和系统的

```glsl
#version 300 es
uniform mat4 u_viewProjMatrix;
layout(location = 0) in vec4 a_vertex;
invariant gl_position;

# pragma STDGL invariant(all)
```

## 顶点着色器的内建变量

- **gl_Position**：顶点坐标
- **gl_PointSize**：点的大小，没有赋值则为默认值1，通常设置绘图为点绘制才有意义。

## 片元着色器的内建变量

- **gl_FragCoord**：当前片元相对窗口位置所处的坐标。
- **gl_FragFacing**：bool型，表示是否为属于光栅化生成此片元的对应图元的正面。
- **gl_FragColor**：当前片元颜色
- **gl_FragData**：vec4类型的数组。向其写入的信息，供渲染管线的后继过程使用。
