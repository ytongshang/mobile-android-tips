# GLSL

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

- GLSL中包含C等其它语言大部分的默认基础数据类型：int、float、double、uint和bool
- 两种容器类型，Vector与Matrix

### 向量

- 向量是一个可以包含有1、2、3或者4个分量的容器
- 分量的类型可以是前面默认基础类型的任意一个

类型  | 含义
------|-------------------------------
vecn  | 包含n个float分量的默认向量
bvecn | 包含n个bool分量的向量
ivecn | 包含n个int分量的向量
uvecn | 包含n个unsigned int分量的向量
dvecn | 包含n个double分量的向量

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

## 输入与输出

- 每个着色器都有输入和输出，这样才能进行数据交流和传递。GLSL定义了in和out关键字专门来实现这个目的
- 每个着色器使用这两个关键字设定输入和输出，只要一个输出变量与下一个着色器阶段的输入匹配，它就会传递下去。但在顶点和片段着色器中会有点不同
- 在下面的例子中，在顶点着色器中声明了一个vertexColor变量作为vec4输出，并在片段着色器中声明了一个类似的vertexColor。
 **由于它们名字相同且类型相同，片段着色器中的vertexColor就和顶点着色器中的vertexColor链接了**

```glsl
#version 330 core
layout (location = 0) in vec3 aPos; // Vertex

out vec4 vertexColor; // 为片段着色器指定一个颜色输出

void main()
{
    gl_Position = vec4(aPos, 1.0); // 注意我们如何把一个vec3作为vec4的构造器的参数
    vertexColor = vec4(0.5, 0.0, 0.0, 1.0); // 把输出变量设置为暗红色
}
```

```glsl
#version 330 core
out vec4 FragColor;

in vec4 vertexColor; // 从顶点着色器传来的输入变量（名称相同、类型相同）

void main()
{
    FragColor = vertexColor;
}
```

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

### glVertexAttribPointer

```java
void glVertexAttribPointer( GLuint index, GLint size, GLenum type,GLboolean normalized, GLsizei stride,const GLvoid * pointer);
```

- **index**:指定要修改的顶点属性的索引值
- **size**,指定每个顶点属性的组件数量。必须为1、2、3或者4。初始值为4。（如position是由3个（x,y,z）组成，而颜色是4个（r,g,b,a））
- **type**,指定数组中每个组件的数据类型。可用的符号常量有GL_BYTE, GL_UNSIGNED_BYTE, GL_SHORT,GL_UNSIGNED_SHORT, GL_FIXED, 和 GL_FLOAT，初始值为GL_FLOAT。
- **normalized**,指定当被访问时，固定点数据值是否应该被归一化（GL_TRUE）或者直接转换为固定点值（GL_FALSE）。
- **stride**,指定连续顶点属性之间的偏移量。如果为0，那么顶点属性会被理解为：它们是紧密排列在一起的。初始值为0。
- **pointer**,指定第一个组件在数组的第一个顶点属性中的偏移量。该数组与GL_ARRAY_BUFFER绑定，储存于缓冲区中。初始值为0；

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