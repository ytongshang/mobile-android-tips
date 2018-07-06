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
#version version_number
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

- GLSL中包含C等其它语言大部分的默认基础数据类型：void, bool,int、float
- 数组，但是只支持1维数组,float foo[3]
- 结构体与C语言一样,struct type-name{}
- 两种容器类型，向量与矩阵
- sampler2D 2D纹理
- samplerCube  盒纹理 cube mapped texture

## 浮点精度

- 与顶点着色器不同的是，**在片元着色器中使用浮点型时，必须指定浮点类型的精度**，否则编译会报错。精度有三种，分别为
    - lowp：低精度。8位。
    - mediump：中精度。10位。
    - highp：高精度。16位。

- 不仅仅是float可以制定精度，其他（除了bool相关）类型也同样可以，但是int、采样器类型并不一定要求指定精度。加精度的定义如下：

```glsl
uniform lowp float a=1.0;
varying mediump vec4 c;
```

### 向量

- 向量是一个可以包含有1、2、3或者4个分量的容器
- 分量存储的类型可以bool,int,float中的一种
- GLSL中的向量表示竖向量，所以与矩阵相乘进行变换时，矩阵在前，向量在后（与DirectX正好相反）

类型  | 含义
------|-------------------------------
vecn  | 包含n个float分量的默认向量
bvecn | 包含n个bool分量的向量
ivecn | 包含n个int分量的向量

- 一个向量的分量可以通过vec.x这种方式获取，这里x是指这个向量的第一个分量。可以分别使用.x、.y、.z和.w来获取它们的第1、2、3、4个分量。
- GLSL也允许你对颜色使用rgba，或是对纹理坐标使用stpq访问相同的分量。

```glsl
vec2 someVec;
vec4 differentVec = someVec.xyxx;
vec3 anotherVec = differentVec.zyw;
vec4 otherVec = someVec.xxxx + anotherVec.yxzy;

vec2 vect = vec2(0.5, 0.7);
vec4 result = vec4(vect, 0.0, 0.0);
vec4 otherResult = vec4(result.xyz, 1.0);
```

## 类型转换

- **GLSL的类型转换与C不同。在GLSL中类型不可以自动提升**，比如float a=1;就是一种错误的写法，必须严格的写成float a=1.0，也不可以强制转换，即float a=(float)1;也是错误的写法，
- **可以用内置函数来进行转换**，如float a=float(1);还有float a=float(true);（true为1.0，false为0.0）等，值得注意的是，低精度的int不能转换为低精度的float。。

## 变量限定符

修饰符    | 说明
----------|----------------------------------------------------------------------------------------------
none      | (默认的可省略)本地变量,可读可写,函数的输入参数既是这种类型
const     | 声明变量或函数的参数为只读类型
attribute | 只能存在于vertex shader中,一般用于保存顶点或法线数据,它可以在数据缓冲区中读取数据
uniform   | 在运行时shader无法改变uniform变量, 一般用来放置程序传递给shader的变换矩阵，材质，光照参数等等.
varying   | 主要负责在vertex 和 fragment 之间传递变量

## Attribute

- 当我们谈论到顶点着色器的时候，每个输入变量也叫顶点属性(Vertex Attribute)。
- 我们能声明的顶点属性是有上限的，它一般由硬件来决定。OpenGL确保至少有16个包含4分量的顶点属性可用，但是有些硬件或许允许更多的顶点属性,可以通过以下方法查明
- **attribute变量是只能在vertex shader中使用的变量**。一般用attribute变量来表示一些顶点的数据，如：顶点坐标，法线，纹理坐标，顶点颜色等,**不能在fragment shader中声明attribute变量，也不能被fragment shader中使用**
- glGetAttribLocation获得vertex shader中attribute变量的index, 使用glVertexAttribPointer为每个attribute
 变量赋值

```glsl
attribute vec4 vPosition;
uniform mat4 vMatrix;
varying  vec4 vColor;
attribute vec4 aColor;
void main() {
  gl_Position = vMatrix*vPosition;
  vColor=aColor;
}
```

- 也可以通过代码获得它的顶点属性的position值

```java
public int getAttributeLocation(String name) {
    int location = GLES20.glGetAttribLocation(mProgram, name);
    if (location == -1) {
        Logger.d(TAG, "Attribute :" + name + " not found");
    }
    return location;
}

int index = getAttributeLocation(program, "aPos");
```

## varying变量

- varying变量是vertex和fragment shader之间做数据传递用的。
- **一般vertex shader修改varying变量的值，然后fragment shader使用该varying变量的值。因此varying变量在vertex和fragment shader二者之间的声明必须是一致的**

## Uniform

- Uniform是一种从CPU中的应用向GPU中的着色器发送数据的方式。
- 首先，**uniform是全局的(Global)**。全局意味着uniform变量必须在每个着色器程序对象中都是独一无二的，而且**它可以被着色器程序的任意着色器在任意阶段访问**。
- 第二，**无论你把uniform值设置成什么，uniform会一直保存它们的数据，直到它们被重置或更新**
- **如果你声明了一个uniform却在GLSL代码中没用过，编译器会静默移除这个变量，导致最后编译出的版本中并不会包含它，这可能导致几个非常麻烦的错误，记住这点！**

### 使用Uniform

- 在glsl代码中定义uniform
- 通过glGetUniformLocation获得Uniform的地址
- 通过glUniform4f等其它方法设置它的值】
- 在着色器程序的任意着色器器使用uniform
- 因为OpenGL在其核心是一个C库，所以它**不支持类型重载**，在函数参数不同的时候就要为其定义新的函数；glUniform是一个典型例子。这个函数有一个特定的后缀，标识设定的uniform的类型。可能的后缀有：

后缀 | 含义
-----|--------------------------------------
f    | 函数需要一个float作为它的值
i    | 函数需要一个int作为它的值
ui   | 函数需要一个unsigned int作为它的值
3f   | 函数需要3个float作为它的值
fv   | 函数需要一个float向量/数组作为它的值

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

## 顶点着色器的内建变量

### 输入变量：

- **gl_Position**：顶点坐标
- **gl_PointSize**：点的大小，没有赋值则为默认值1，通常设置绘图为点绘制才有意义。

## 片元着色器的内建变量

### 输入变量

- **gl_FragCoord**：当前片元相对窗口位置所处的坐标。
- **gl_FragFacing**：bool型，表示是否为属于光栅化生成此片元的对应图元的正面。

### 输出变量

- **gl_FragColor**：当前片元颜色
- **gl_FragData**：vec4类型的数组。向其写入的信息，供渲染管线的后继过程使用。