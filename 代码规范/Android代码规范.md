# Android代码规范

- Created by Rancune@126.com on 2016/10/21
- V 1.0

## 类名

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

## 成员变量

- 类成员变量以m开头，比如mContext
- static变量以s开头，比如sInstance
- 变量小驼峰命名法 比如 mStudentName
- 局部变量，**不用带前缀m**,正常单词组合的小驼峰命名法
- 变量最好不要包含特殊字符（比如下划线等）。如果不是必要，最好不要包含数字
- 常量命名只能包含字母和_，单词之间用_ 隔开，字母全部大写 比如RESULT_SUCCESS, RESULT_CANCEL

## 方法

- 动词或动名词，采用小驼峰命名法

- 如果方法有默认行为，首先方法注释应当有说明，其次方法名有提示，或在方法加入参数

  ```

  @Nullable
  Bitmap compressBitmap(Bitmap source, boolean recycler)
  ```

- 方法参数与方法返回可能为空

  - 如果方法参数不能为空，对该参数用NonNull注解，方法中要检测是否为空

  - 如果方法返回有可能为空，对返回结果用Nullable注解，这样方便对函数返回检测，方便代码理解

  - **尽可能的避免方法的返回为空**，比如集合可以用空集合，字符串可以用""返回

- 常用方法的名字

方法          | 说明
:---------- | :---------------------------------------
initXX()    | 初始化相关方法,使用init为前缀标识，如初始化布局initView()
isXX()      | checkXX()方法返回值为boolean型的请使用is或check为前缀标识
getXX()     | 返回某个值的方法，使用get为前缀标识
release()   | 释放资源
getInstance | 单例

## 布局资源命名

- 全部小写，采用下划线命名法。其中{module_name}为业务模块或是功能模块等模块化的名称或简称。

- 如果是主module, 则前面的module_name可以不用

- activity layout： {module_name}_activity_{名称} 例如： activity_main.xml , crm_activity_shopping.xml

- fragment layout:{module_name}_fragment_{名称} 例如： fragment_main.xml , crm_fragment_shopping.xml

- Dialog layout: {module_name}_dialog_{名称} 例如： dialog_confirm.xml crm_dialog_loading.xml

- 列表项布局命名：{module_name}_listitem_{名称} 例如： listitem_customer.xml

- 包含项布局命名：include_{名称} 例如： include_head.xml

- widget layout： {module_name}_widget_{名称} 例如： crm_widget_shopping_detail.xml

## 资源id命名规范

- 命名模式为：{view缩写}_{module_name}_{view的逻辑名称}，如：ll_crm_content

- 常用简写

Header One     | Header Two
:------------- | :---------
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

## selector资源命令

- 正常 normal download_normal.png
- 按下 pressed download_pressed.png
- 不可用 disabled download_disabled.png
- selector download_selector

## 注解相关

- @Override **必须注解**

- @Nullable 和 @NonNull 同上面方法中说明

- 自己写的方法，如果用到了资源相关的，**尽可能** 的使用相关的注解，比如 @ColorRes @ColorInt @DrawableRes...等等

- 自己写的方法，如果必须对方法的返回值处理，那么 **必须使用 @CheckResult 注解**

## 性能优化

- 避免创建不必要的对象

- 尽可能的使用static final int 而不是使用enum，因而在其它地方需要传入定义的static final int值的时候，**必须用定义的变量名**，而不能直接传入相应的int值

- 多使用ArrayMap,SparseArray,SparseBooleanArray,SparseLongArray,LongSparseArray,LongSparseLongArray等轻量级数据结构

- 对于容器类，多使用for-each语法

- 多使用Parcelable而不是Serializable，如果使用Serializable，注意序列化id

- 如果内部类要访问外部类的成员，最好将外部类的成员定义为package级别，而不是private级别的

- 少使用getter和setter

- 数据库读写使用事务

## 布局优化

- 使用include，merge等标签,将布局抽象成控件

- 延时加载View. 采用ViewStub 避免一些不经常的视图长期被引用，占用内存

- 如果确信在Activity中使用不透明的背景，那么可以移除Activity的默认背景。 在代码中：getWindow().setBackgroundDrawable(null); 也可以通过定义style解决

- 在不增加布局层次的时候，使用LinearLayout而不是RelativeLayout.使用RelativeLayout减少布局层次

- Space控件，GridLayout的使用

- 多使用style

- 对于公共的padding margin不使用硬编码，在xml中定义

## 代码优化

- 尽可能的少的创建对象，比如对于activity,尽可能的在一个View.OnClickListener中处理所有的逻辑 再比如对于RecyclerView的每一个item的点击事件，尽可能统一处理

- 对于线程，如果一直要创建新的线程，考虑使用线程池，而不是一直new Thread，引入Rxjava后，考虑多使用Rxjava中自带的线程池

- 一般情况下不要在循环内部try catch 异常，除非必要

- 注意生命周期结束时，使用handler时，注意remove相关的消息，使用AnsyncTask,注意取消task, 使用CountDownTimer和TimerTask注意取消定时器

- 异步代码，主是要api请求，api返回时有可能已经不用更新ui,使用mvp结构更加要注意

- 使用static变量时，注意内存泄漏，比如在一个单例中保存某个activity的引用，所以单例如果要使用context初始化，应该使用context.getApplicationContext()

- io,cursor注意关闭

- 恰当的使用SoftReference，WeakRefrence

- 即时清理不必要的对象，比如清理集合中的对象，比如Bitmap的回收等

- 尽可能的使用Spanny而不是多个TextView

- strings.xml中使用%1$s实现字符串的通配

## 其它

- 代码和布局文件等尽可能没有警告，多看代码警告提示和相关的解决方法

- 代码中尽可能不要使用过时的方法，除非有必要

- 代码尽可能的少用反射相关的代码

- 代码完成提交前，最好format一下

- 代码逻辑比较复杂，不是一下可以看明白的，多加一些注释
