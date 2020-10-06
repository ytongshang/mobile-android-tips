# CMake

## 变量定义

```cmake
# 定义变量，变量名为 var，值为 hello
set(var hello)

# 引用 var 变量
${var}

# 通过 message 在命令行中输出打印内容
set(var hello)
message(${var})
```

## 数学操作与字符串

- math 支持 +, -, *, /, %, |, &, ^, ~, <<, >> 等操作

```cmake
# math 使用，EXPR 为大小
math(EXPR <output-variable> <math-expression>)
math(EXPR var "1+1")

# 输出结果为 2
message(${var})
```

## 字符串

```cmake
set(var "this is  string")
set(sub "this")

# 字符串的查找，在var中查找sub,结果保存在 result 变量中
string(FIND ${var} ${sub} result )
# 找到了输出 0 ，否则为 -1
message(${result})

# 将字符串全部大写
string(TOUPPER ${var} result)
message(${result})

# 求字符串的长度
string(LENGTH ${var} num)
message(${num})
```

- **通过空白或者分隔符号可以表示字符串序列**
- **当字符串中需要用到空白或者分隔符时，再用双括号""表示为同一个字符串内容**

```cmake
# 实际内容为字符串序列
# foo相当于一个List<String>，它有4个元素，this, is, a ,list
set(foo this is a list)
message(${foo})

# foo是一个字符串
set(foo "this is a list") // 实际内容为一个字符串
message(${foo})
```

## 文件操作

```cmake
# 文件重命名
file(RENAME "test.txt" "new.txt")

# 文件下载
# 把文件 URL 设定为变量
set(var "http://img.zcool.cn/community/0117e2571b8b246ac72538120dd8a4.jpg")

使用 DOWNLOAD 下载
file(DOWNLOAD ${var} "/Users/glumes/CLionProjects/HelloCMake/image.jpg")
```

- **GLOB 指令会将所有匹配 *.cpp 表达式的文件组成一个列表，并保存在 ROOT_SOURCE 变量中**
- **GLOB_RECURSE 指令和 GLOB 类似，但是它会遍历匹配目录的所有文件以及子目录下面的文件**

```cmake
# GLOB 的使用
# 当前目录所有的.cpp文件保存在ROOT_SOURCE
file(GLOB ROOT_SOURCE *.cpp)

# GLOB_RECURSE 的使用
file(GLOB_RECURSE CORE_SOURCE ./detail/*.cpp)
```

## 预定义的常量

-   **CMAKE_CURRENT_SOURCE_DIR**, 指当前 CMake 文件所在的文件夹路径
-   **CMAKE_SOURCE_DIR**, 指当前工程的 CMake 文件所在路径
-   **CMAKE_CURRENT_LIST_FILE**,指当前 CMake 文件的完整路径
-   **PROJECT_SOURCE_DIR**,指当前工程的路径

```cmake
# 利用预定义的常量来指定文件路径
add_library( # Sets the name of the library.
             openglutil
             # Sets the library as a shared library.
             SHARED
             # Provides a relative path to your source file(s).
             ${CMAKE_CURRENT_SOURCE_DIR}/opengl_util.cpp
             )
```

-   **WIN32**, 如果编译的目标系统是 Window,那么 WIN32 为 True 。
-   **UNIX**, 如果编译的目标系统是 Unix 或者类 Unix 也就是 Linux ,那么 UNIX 为 True 。
-   **MSVC**, 如果编译器是 Window 上的 Visual C++ 之类的，那么 MSVC 为 True 。
-   **ANDROID**, 如果目标系统是 Android ，那么 ANDROID 为 1 。
-   **APPLE**, 如果目标系统是 APPLE ，那么 APPLE 为 1

```cmake
if(WIN32){
   # do something
}elseif(UNIX){
    # do something
}
```

## 函数，宏，控制流

-   **function 为定义函数，第一个参数为函数名称，后面为函数参数**
-   **调用函数时，参数之间用空格隔开，不要用逗号**

```cmake
function(add a b)
    message("this is function call")
    math(EXPR num "${a} + ${b}" )
    message("result is ${aa}")
endfunction()

add(1 2)
```

-   **在流程控制方面，CMake 也提供了 if、else 这样的操作**
-   **CMake 提供了 AND、OR、NOT、LESS、EQUAL 等等这样的操作来对数据进行判断，比如 AND 就是要求两边同为 True 才行**

```cmake
set(num 0)
if (1 AND ${num})
    message("and operation")
elseif (1 OR ${num})
    message("or operation")
else ()
    message("not reach")
endif ()
```

- 循环

```cmake
set(stringList this is string list)
foreach (str ${stringList})
    message("str is ${str}")
endforeach ()
```

## option

- **CMake 还提供了一个 option 指令。可以通过它来给 CMake 定义一些全局选项**

```cmake
option(ENABLE_SHARED "Build shared libraries" TRUE)
option(USE_STATIC_MBEDTLS_LIBRARY "Build mbed TLS static library." ON)

if(ENABLE_SHARED)
   # do something
else()
    # do something
endif()
```

## 其它

### include_directories,添加头文件

- 在使用的时候有一个容易忽略的步骤就是添加头文件，通过 include_directories 指令把头文件目录包含进来。这样就可以直接使用 #include "header.h" 的方式包含头文件，而不用  #include "path/path/header.h" 这样添加路径的方式来包含

### aux_source_directory

- 将dir下的所有源文件的名字保存在variable的列表中
- **坏处是，有的时候加了一个文件，原先生成的并不知道，可能需要重新调用Cmake指令**

```cmake
# 查找当前目录下的所有源文件
# 并将名称保存到 DIR_SRCS 变量
aux_source_directory(. DIR_SRCS)

# 指定生成目标
add_executable(Demo ${DIR_SRCS})
```

### add_subdirectory

-   一般情况下，我们的项目各个子项目都在一个总的项目根目录下，但有的时候，我们需要使用外部的文件夹，怎么办呢？ 
add_subdirectory命令，可以将指定的文件夹加到build任务列表中
-   **原来add_subdirectory还有一个 binary_dir参数(一般这个参数用不到，所以从来没关注过),这个参数用来指定source_dir在输出文件夹中的位置，如果没有指定的时候，就用source_dir的值。 如果要添加外部文件夹，binary_dir就必须指定**

```cmake
#定义CASSDK位置
if(NOT CASSDK_DIR)
    set( CASSDK_DIR ${CMAKE_SOURCE_DIR}/../cassdk)
endif()
if( IS_DIRECTORY ${CASSDK_DIR} )
    # 第二个cassdk.out参数用于指定外部文件夹在输出文件夹中的位置
    add_subdirectory( ${CASSDK_DIR}/cassdk cassdk.out)
else()
    message(FATAL_ERROR   "INVALID FOLDER 'CASSDK_DIR'=${CASSDK_DIR}" )
endif()
```

### find_library

```cmake
find_library (<VAR> name1 [path1 path2 ...])
```

```cmake
# 查找代码中使用到的系统库
find_library( # Sets the name of the path variable.
        log-lib

        # Specifies the name of the NDK library that
        # you want CMake to locate.
        log)
```

### add_library

```cmake
cmake_minimum_required(VERSION 3.12)

# 指定编译的库和文件，SHARED 编译动态库
add_library(share_lib SHARED lib.cpp)

# STATIC 编译静态库
# add_library(share_lib STATIC lib.cpp)
```

### set_target_properties

- [set_target_properties](https://cmake.org/cmake/help/v3.9/manual/cmake-properties.7.html#target-properties)

```cmake
set_target_properties(target1 target2 ...
                     PROPERTIES prop1 value1
                      prop2 value2 ...)

# 将编译的库改个名称
set_target_properties(native-lib PROPERTIES OUTPUT_NAME "testlib" )

# 实现动态库的版本
set_target_properties(native-lib PROPERTIES VERSION 1.2 SOVERSION 1 )
```

- **IMPORTED表示导入库，使用 IMPORTED_LOCATION 属性指定库的路径**

```cmake
# 使用 IMPORTED 表示导入库
add_library(avcodec-57_lib SHARED IMPORTED)

# 使用 IMPORTED_LOCATION 属性指定库的路径
set_target_properties(avcodec-57_lib PROPERTIES IMPORTED_LOCATION
                        ${CMAKE_CURRENT_SOURCE_DIR}/src/main/jniLibs/armeabi/libavcodec-57.so )
```

### target_link_libraries

- 如果编译了多个库，并且想库与库之间进行链接，那么就要通过 target_link_libraries

```cmake
target_link_libraries( native-lib
                       glm
                      turbojpeg
                       log )
```

- 如果要链接自己编译的多个库文件，首先要保证每个库的代码都对应一个 CMakeLists.txt 文件，这个 CMakeLists.txt 文件指定当前要编译的库的信息。然后在当前库的 CMakeLists.txt 文件中通过 ADD_SUBDIRECTORY 将其他库的目录添加进来，这样才能够链接到。

```cmake
ADD_SUBDIRECTORY(src/main/cpp/turbojpeg)
ADD_SUBDIRECTORY(src/main/cpp/glm)
```

