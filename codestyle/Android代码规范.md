# Android代码规范

- Created by Rancune@126.com on 2016/10/21
- V1.0

- [代码格式](#代码格式)
    - [总体代码风络](#总体代码风络)
    - [类名](#类名)
    - [成员变量](#成员变量)
    - [方法](#方法)
    - [布局资源命名](#布局资源命名)
    - [资源id命名规范](#资源id命名规范)
    - [selector资源命令](#selector资源命令)
    - [注解相关](#注解相关)
    - [泛型相关](#泛型相关)
- [代码优化](#代码优化)
    - [性能优化](#性能优化)
    - [内存泄漏](#内存泄漏)
    - [代码中访问级别的问题](#代码中访问级别的问题)
        - [类与接口的可访问性](#类与接口的可访问性)
        - [类成员的可访问性](#类成员的可访问性)
    - [布局优化](#布局优化)
    - [代码优化Tips](#代码优化tips)

## 代码格式

### 总体代码风络

- 具体参看google java code style

- **最最最最重要的是，代码写完后，记得全选代码，然后code ->Reformat code一下**
  - 统一的缩进风格 Editor->java
  - 统一的import风格 Editor->General->Auto Import

- 变量声明
  - 一行一个变量，哪怕连续几行的变量的类型是一样的
  - 尽可能将逻辑功能相关联的变量的声明放到一起
  - static final 放到最上面，然后static的，其次才是类的成员变量
  - java类的成员**对象变量，是不用显示声明为null的**，
   当然基本类型的值如果有特殊的值的时候，记得手动初始化，否则会默认初始化，**所以对于基本类型的值我们最好都手动初始化一下**
  - 当需要时才声明，尽快完成初始化，局部变量**不应该习惯性地放在语句块的开始处声明**，而应该尽量离它第一次使用的地方最近的地声明，以减小它们的使用范围。
   局部变量**应该在声明的时候就进行初始化**

- 数组，习惯问题
  - 方括号应该是变量类型的一部分，因此不应该和变量名放在一起。例如：应该是 String [] args，而不是 String args[]

- 变量修饰，用这个顺序比较好
  - 多个类和成员变量的修饰符，按 Java Lauguage Specification 中介绍的先后顺序排序。具体是：
   public protected private abstract static final transient volatile synchronized native strictfp

- 成员函数问题
  - **重载的函数一定记得要加上@Override注解**（VideoPlayer中的onMyKeyDown问题）
  - **对于activity和fragment重载它的多个生命周期函数时，最好重载函数顺序和它的生命周期一致** ，
  比如按顺序onCreate, onStart, onResume等等
  - **是否应当将重载函数写在类的最前面？**（?讨论后定下来）
  - 成员函数： public 包作用域 protected private的顺序问题（?讨论后定下来）
  - 如果实现interface,同一个interface的函数在一起

- 长行断行，**最主要记得长行要记得断行,Android Studio有一个建议代码一行长度最长的线，一般不要超过它**
  - 当一个非赋值运算的语句断行时，在运算符号之前断行
  - 当一个赋值运算语句断行时，一般在赋值符号之后断行。但是也可以在之前断行。
  - 在调用函数或者构造函数需要断行时，与函数名相连的左括号要在一行。也就是在左括号之后断行
  - 逗号断行时，要和逗号隔开的前面的语句断行。也就是在逗号之后断行
  - 当断行之后，在第一行之后的行，我们叫做延续行。每一个延续行在第一行的基础上至少缩进四个字符

- 内部空格，**用Reformat code可以解决**，了解一下也不错
  - 所有保留的关键字与紧接它之后的位于同一行的左括号之间需要用空格隔开。（例如 if、for、catch）
  - 所有保留的关键字与在它之前的右花括号之间需要空格隔开。（例如 else、catch）
  - 在左花括号之前都需要空格隔开。只有两种例外@SomeAnnotation({a, b})，String [][] x = {{ "foo" }};
  - 所有的二元运算符和三元运算符的两边，都需要空格隔开。
  - 逗号、冒号、分号和右括号之后，需要空格隔开。
  - 双斜线开始一行注释时。双斜线两边都应该用空格隔开。并且可使用多个空格，但是不做强制要求。
  - 变量声明时，变量类型和变量名之间需要用空格隔开。
  - 初始化一个数组时，花括号之间可以用空格隔开，也可以不使用。（例如：new int[] {5, 6} 和 new int[] { 5, 6 } 都可以）

### 类名

- 采用大驼峰式命名法
- 类名应当尽可能只包含字母，不要包含特殊字符（比如下划线等）。如果不是必要，最好不要包含数字
- 尽量避免缩写，除非该缩写是众所周知的，比如HTML，URL
- 如果类名称包含单词缩写，则单词缩写的每个字母均应大写
- 常用类命名方法

Header One        | Header Two    | Header Three
:---------------- | :------------ | :-----------------
activity 类        | Activity为后缀标识 | WelcomeActivity
fragment 类        | fragment为后缀标识 | WelcomeFragment
adapter 类         | adapter为后缀标识  | ContactListAdapter
service 类         | Service为后缀标识  | DownloadService
broadcastReceiver | Receiver为后缀标识 | RecordReceiver
database          | dbhelper为后缀标识 | ImHelper
base 类            | Base 开头       | BaseActivity

### 成员变量

- 类成员变量以m开头，比如mContext,(但是对应的getter和setter不应当包含,boolean类型返回值的getter各setter)
- static变量以s开头，比如sInstance(只要是static,对象，考虑内存泄漏,T.FastToast例子)
- 变量小驼峰命名法 比如 mStudentName
- 局部变量，**不用带前缀m**,正常单词组合的小驼峰命名法
- 变量最好不要包含特殊字符（比如下划线等）。如果不是必要，最好不要包含数字
- 常量命名只能包含字母和_，单词之间用_ 隔开，字母全部大写 比如RESULT_SUCCESS, RESULT_CANCEL
- 常量的定义（static final,不可变对象，数组的返回,static内部类等）

### 方法

- 动词或动名词，采用小驼峰命名法

- **如果方法有默认行为，首先方法注释应当有说明，其次方法名有提示，或在方法加入参数**

  ```java
  @Nullable
  Bitmap compressBitmap(@NonNull Bitmap source, boolean recycle)
  ```

- 方法参数与方法返回可能为空
  - **如果一个函数的某个参数可以传入null,注意用@Nullable注解，代码中注意非null判断**，比如api中的callback
  - 如果方法参数不能为空，**对该参数用NonNull注解，方法中依然要检测是否为空，记得NonNull注解并不能确保传入的参数不是空的**
  - **如果方法返回有可能为空，必须对返回结果用Nullable注解**，这样方便在调用函数时，会执行非空检测
  - 因为@NonNull的歧义性，@NonNull只能作为一种提示，所以应当尽可能使用@Nullable
  - **尽可能的避免方法的返回为null,返回null是一个有歧义的行为**，比如集合可以用Collections.emptyList()，字符串可以用""返回

- 常用方法的名字

方法          | 说明
:---------- | :---------------------------------------
initXX()    | 初始化相关方法,使用init为前缀标识，如初始化布局initView()
isXX()      | checkXX()方法返回值为boolean型的请使用is或check为前缀标识
getXX()     | 返回某个值的方法，使用get为前缀标识
release()   | 释放资源
getInstance | 单例

- 一个方法，尽可能是一种可以通用的情况，不要包含太多的特殊处理（eg.Zues中的图片保存）

### 布局资源命名

- 全部小写，采用下划线命名法。其中{module_name}为业务模块或是功能模块等模块化的名称或简称（eg. zues中的资源命名）

- **一个模块的命名应当类似，可以很方便的查找**（eg.ListItem 中layout的命名，titleView中icon的命名）

- 如果是主module, 则前面的module_name可以不用
  - activity layout： {module_name}_activity_{名称} 例如： activity_main.xml , crm_activity_shopping.xml
  - fragment layout:{module_name}_fragment_{名称} 例如： fragment_main.xml , crm_fragment_shopping.xml
 （eg.不要出现很奇怪的命名方法(比如老的View_Base以及相关联的命名)）
  - Dialog layout: {module_name}_dialog_{名称} 例如： dialog_confirm.xml crm_dialog_loading.xml
  - 列表项布局命名：{module_name}_item_{名称} 例如： item_listitem_double_room.xml
  - 包含项布局命名：include_{名称} 例如： include_head.xml
  - widget layout： {module_name}_widget_{名称} 例如： crm_widget_shopping_detail.xml

### 资源id命名规范

- 命名模式为：{view缩写}_{module_name}_{view的逻辑名称}，如：ll_crm_content

- **可以用重复的命名的**

- 常用简写

View类型         | 简写
:------------- | :-----
LinearLayout   | ll
RelativeLayout | rl
FrameLayout    | fl
TextView       | tv
Button         | btn
ImageView      | iv
CheckBox       | cb
RadioButton    | rb
EditText       | et
ProgressBar    | proBar
WebView        | wv
ScrollView     | sv
ListView       | lv
GridView       | gv
RecyclerView   | rv

### selector资源命令

- 正常 normal download_normal.png
- 按下 pressed download_pressed.png
- 不可用 disabled download_disabled.png
- selector download_selector（?讨论是否完整单词，还有selector的命名）

### 注解相关

- @Override **必须注解**

- @Nullable 和 @NonNull 同上面方法中说明

- 自己写的方法，如果用到了资源相关的，**尽可能** 的使用相关的注解，比如 @ColorRes @ColorInt @DrawableRes...等等，**注意 @ColorRes @ColorInt 这两个注解的区别**

- 如是参数有特定范围,比如@IntRange，还可以自定义注解（@ThreadType，@RoomRole等）

- 自己写的方法，如果必须对方法的返回值处理，那么 **必须使用 @CheckResult 注解**，否则忽略返回值此就会经常出问题的


### 泛型相关

- 不要使用原生的类型，如果有泛型参数，务必加上参数
- 如果是对所有的类都适用，**请使用使用泛型参数"？"**，
- 优先使用list而不是数组（eg.不可变问题）
- 如是有泛型参数有上下界，注意使用extends 与super,当然如果是extends的话，也可以直接用extends的类或接口做为参数，两者是等价的。
- 考虑使用泛型类
- 优先考虑泛型方法，而不是泛型类


## 代码优化

### 性能优化

- **避免创建不必要的对象**,比如onClickListener，一个activity，fragment一个就足够了

- 尽可能的重用对象
  - 比如将常用的**不可变对象**定义为static final，配合懒加载等 (eg.BlurpostProcessor）)
  - 对于比较小的对象，jvm创建的代价是很低的，所以**不要提供所谓的"再次初始化方法"**，否则不利于阅读

- 使用缓存
  - 单例模式
  - view缓存（eg.listview, photoGallery）
  - 线程池
  - BufferedInputStream替代InputStream，BufferedReader替代Reader
  - 资源缓存 (eg.ComboNumberView中的drawable)
  - 消息缓存，Handler 的 obtainMessage

- **尽可能的使用static final int 而不是使用enum**，
 因而在其它地方需**要传入定义的static final int值的时候，必须用定义的变量名**，而不能直接传入相应的int值，
 这种限定传值的方式，其实可以用**新生成一个注解**解决，具体查看ThreadType.Thread的注解

- 尽可能的使用基本类型，而不是包装类(eg.RxBus中的问题, View_Banrrage中的问题)

- 多使用ArrayMap,SparseArray,SparseBooleanArray,SparseLongArray,LongSparseArray,LongSparseLongArray等轻量级数据结构
 问题在于请使用V4包中提供的对应的轻量级数据结构

- 对于容器类，多使用for-each, 和for index语法（相比较于iterator）

- 多使用Parcelable而不是Serializable，如果使用Serializable，注意序列化id（Android Studio inspection修改一下就行）
 (Android Studio， code inspections-Serializable)

- 消除过期对象的引用
  > 清空对象的引用是一种例外，而不是一种规范行为

- android中为了效率，少使用getter和setter，直接操作成员变量会快一些，**当然这并不是一种好的java代码**

- 优先考虑使用静态方法

- 数据库读写使用事务

- 策略模式多使用函数对象（eg.BlurpostProcessor）

- 优先考虑静态类（eg. 嵌套类的比较）

- **如果内部类要访问外部类的成员，最好将外部类的成员定义为包级别**，而不是private级别的

- 同步改为异步(eg.ImageLoader中的savePicture)

### 内存泄漏

- 内存泄漏的原因
  - 垃圾回收机制（环形引用是不会造成内存泄漏的），长生命周期的对象持有短生命周期的对象
   (eg.static,匿名内部类，回调，集合引用)
  - thread
  - 异步造成
  - 系统资源（eg.file cursor）
  - native

- 原则：
  - 只要是自己管理内存的代码，注意内存泄漏(特别注意static,context，单例)
  - 关闭要关注的对象（cursor,closable）
  - 异步相关（handler,timer,timerTask,CountDownTimer，AnsyncTask，回调）


### 代码中访问级别的问题

- 原则：**尽可能使类或类的成员不被外界访问**

#### 类与接口的可访问性

- 对于顶层的类与接口，访问性只能是public或都包访问级别的

- 类与接口，如果它是public的，那么它就是包的导出api的一部分，那么有责任永远的支持它

- 但是如果它是包访问级别的的，那么它就是包的实现的一部分，以后对这部分修改、替换、删除，都不用担心现有的客户端程序

- 如果一个包访问级别的类只在一个类的内部被用到，那么应当考虑使它成为那个唯一使用它的那个类的的私有嵌套类

#### 类成员的可访问性

- private
- 包访问级别
- protected,**子类以及声明该成员的包内部的任何类也可以访问这个成员，protected具有包访问权限的一切特性**
- public
- 一般情况下，都会将成员变成私有的，**只有当包内的另一个类真正需要访问这个成员时，才将其声明为包访问级别的**
- 对于**公有类的protected成员，其也是公有类的导出API的一部分**，必须永远得到支持，所以**protected的成员应当尽可能的少用**
- 为了测试，可以将private成员变成包访问级别的，但是绝对不能变成不能高于包访问级别
- **public类的成员变量，绝不能是公有的**，如是成员变量是非final的，或者是一个指向可变对象的final引用，那么一旦使这个成员变量变成公有的，那么就放弃了对
 存储在这个成员变量中的值进行限定的方法，**包含公有可变成员变量的类绝对不是线程安全的**
- 对于static成员变量，上述对public成员变量的规则同样适用。
- 对于static成员变量，只有static final可以声明为public这一种例外，**static final的成员变量要么包含基本类型，要么包含指向不可变对象的引用**，
 **如果final成员变量包含可变对象的引用，那么它便具有final成员变量的所有缺点，引用本身不可变，但是引用的对象却可以被修改**
- 长度非0的数组总是可变的，所有类具有public static final数组成员变量，或者返回这种成员变量的访问方法，这几乎总是错误的
 解决办法是返回对象的clone,或都返回对应的不可修改的collection

```java
// public static final 数组总是有问题的
public static final Thing[] VALUES = {...};

private static final Thing[] PRIVATE_VALUES = {...};
public static final List<Thing> VALUES = Collections.unmodifiableList(Arrays.asList(PRIVATE_VALUES);)

private static final Thing[] PRIVATE_VALUES = {...};
public static final Thing[] values() {
    return PRIVATE_VALUES.clone();
}
```


### 布局优化

- **最最重要的减少布局的层次**

- 使用include，merge等标签

- 延时加载View. 采用ViewStub 避免一些不经常的视图长期被引用，占用内存

- 如果确信在Activity中使用不透明的背景，那么可以移除Activity的默认背景。 在代码中：getWindow().setBackgroundDrawable(null); 也可以通过定义style解决

- 在不增加布局层次的时候，使用LinearLayout和FrameLayout而不是RelativeLayout

- 使用RelativeLayout减少布局层次

- Space控件，GridLayout的使用（space是不会绘制的！）

- 将布局抽象成控件,这样通用布局改变了只用修改一个地方 （eg. EmptyLoadingView, SubscribeButton）

- 使用view缓存（eg.比如PhotoGallery, ListView等）

- 多使用style，可以避免一个小修改，要修改所有的xml




### 代码优化Tips

- 尽可能的少的创建对象，比如对于activity,尽可能的在一个View.OnClickListener中处理所有的逻辑 再比如对于RecyclerView的每一个item的点击事件，尽可能统一处理
 (eg.CommonRecyclerViewAdapter,ListItemAdapter, 统计中的json生成等)

- 对于线程，如果一直要创建新的线程，考虑使用线程池，而不是一直new Thread，引入Rxjava后，考虑多使用Rxjava中自带的线程池
 （先去RxExcutor中找一找）

- 一般情况下不要在循环内部try catch 异常，除非必要（eg.IOUtils.closeQuitely()）

- 注意生命周期结束时，取消异步操作
  - handler
  - timer
  - CountDownTimer
  - AnsyncTask

- 使用Rxjava后，注意在生命周期函数结束时，取消异步调用

- 异步代码，主是要api请求，api返回时有可能已经不用更新ui,使用mvp结构更加要注意，**注意isAttached()方法的调用**，
 注意presenter的detchView的调用时机

- 使用static变量时，注意内存泄漏，比如在一个单例中保存某个activity的引用，所以单例如果要使用context初始化，应该使用context.getApplicationContext()

- io,cursor注意关闭（**IOUtils.closeIOQuietly(Closeable closeable)**）

- 恰当的使用SoftReference，WeakRefrence,**主要在于缓存与异步调用**

- 即时清理不必要的对象，（eg.有关bitmap.recycle()的问题，特别是fresco中问题）

- 尽可能的使用Spanny而不是多个TextView

- **strings.xml中使用%1$s实现字符串的通配**

- 多使用系统已有的类，方法等，（eg.RoundedBitmapDrawable,System.arraycopy等)

- EventBus的使用

- 将标签类转化为类层次（eg.ListItem）

- 接口只用来定义类型，接口优先于抽象类，不要使用常量接口，**如果是常量，请使用static final 不可初始化的工具类，如果分类型，可以使用static 内部类**

- 要么专为继承而设计，要么禁止继承（eg.BaseActivity中的调顺序问题）

- 单例的写法问题

```java
public class SingleTon {
    public static final volatile INSTANCE = new SingleTon();

    public static SingleTon getInstance() {
        return INSTANCE;
    }

    private SingleTon() {}
}
```

```java
public class SingleTon {
    public static class SingleTonHolder {
        public static final volatile SingleTon INSTANCE = new SingleTon();
    }

    public static SingleTon getInstance() {
        return SingleTonHolder.INSTANCE;
    }

     private Singleton () {}
}

```


```java
public class SingleTon{
    public static volatile INSTANCE = null;

    public static SingleTon getInstance() {
        if (INSTANCE == null) {
            synchronized(SingleTon.class) {
                if (INSTANCE == null) {
                    INSTANCE = new SingleTon();
                }
            }
        }
        return INSTANCE;
    }

    private SingleTon() {}

}
```

```java

public enum SingleTon {
    INSTANCE;

    public static SingleTon getInstance() {
        return INSTANCE;
    }
}

- LayoutInflater的使用 (eg View_Banrrage中layoutInflater的问题)

```java

 public View inflate(XmlPullParser parser, ViewGroup root)
 public View inflate(int resource, ViewGroup root, boolean attachToRoot)

```

## 其它

- 代码和布局文件等尽可能没有警告，**多看代码警告提示和相关的解决方法总会学到很多东西**

- 代码中尽可能不要使用过时的方法，除非有必要（eg.ContextCompact,ActivityCompact等等）

- 代码尽可能的少用反射相关的代码（eg.获得statusbar的高度）

- 代码逻辑比较复杂，不是一下可以看明白的，多加一些注释，对人对己都是有好处的
  >当你要写注释时，请先尝试重构，试着让所有的注释都变得多余

- 代码update后发现有更新的，可以看一下有哪些更改，看修改总会学到新的东西

- 在加一个新的功能前，如果觉得在原来的代码的基础上无从下手，或者改起来太麻烦了，试着先重构，然后加新功能
 （eg.比如ListItemAdapter与原来首页的实现比较，比如showStatus()方法与原先的showLoading,hideLoading方法）

- 学会Android Lint进行代码检查

- 代码完成提交前，**最好format一下**


