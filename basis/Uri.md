# Android中的Uri

- [Uri详解之——Uri结构与代码提取](http://blog.csdn.net/harvic880925/article/details/44679239)
- [Uri详解之二——通过自定义Uri外部启动APP与Notification启动](http://blog.csdn.net/harvic880925/article/details/44781557)
- [Java魔法堂：URI、URL（含URL Protocol Handler）和URN](http://www.cnblogs.com/fsjohnhuang/p/4280369.html)

## Uri结构解析

```html

[scheme:]scheme-specific-part[#fragment]

[scheme:][//authority][path][?query][#fragment]

[scheme:][//host:port][path][?query][#fragment]

```

- **path可以有多个，每个用/连接**，比如

    scheme://authority/path1/path2/path3?query#fragment

- **query参数可以带有对应的值，也可以不带，如果带对应的值用=表示**，如

    scheme://authority/path1/path2/path3?id = 1#fragment，这里有一个参数id，它的值是1

- **query参数可以有多个，每个用&连接**

    scheme://authority/path1/path2/path3?id = 1&name = mingming&old#fragment

    这里有三个参数：

    参数1：id，其值是:1

    参数2：name，其值是:mingming

    参数3：old，没有对它赋值，所以它的值是null

- **在android中，除了scheme、authority是必须要有的，其它的几个path、query、fragment，它们每一个可以选择性的要或不要，但  顺序不能变**，比如：

    其中"path"可不要：scheme://authority?query#fragment

    其中"path"和"query"可都不要：scheme://authority#fragment

    其中"query"和"fragment"可都不要：scheme://authority/path

    "path","query","fragment"都不要：scheme://authority


## 例子解析

```html
http://www.java2s.com:8080/yourpath/fileName.htm?stove=10&path=32&id=4#harvic
```

- **scheme**:匹对上面的两个Uri标准形式，很容易看出在：前的部分是scheme，所以这个Uri字符串的sheme是：http

- **scheme-specific-part**:很容易看出scheme-specific-part是包含在scheme和fragment之间的部分，也就是包括第二部分的[//authority][path][?query]这几个小部分，所在这个Uri字符串的scheme-specific-part是：//www.java2s.com:8080/yourpath/fileName.htm?stove=10& path=32&id=4 ，**注意要带上//**，因为除了[scheme:]和[#fragment]部分全部都是scheme-specific-part，当然包括最前面的//；

- **fragment**:这个是更容易看出的，**因为在最后用#分隔的部分就是fragment**，所以这个Uri的fragment是：harvic下面就是对scheme-specific-part进行拆分了；在scheme-specific-part中，最前端的部分就是authority，？后面的部分是query，中间的部分就是path

- **authority**：很容易看出scheme-specific-part最新端的部分是：www.java2s.com:8080

- **query**:**在scheme-specific-part中，？后的部分为**：stove=10&path=32&id=4

- **path**:在query:在scheme-specific-part中，除了authority和query其余都是path的部分:/yourpath/fileName.htm,又由于**authority又一步可以划分为host:port形式，其中host:port用冒号分隔，冒号前的是host，冒号后的是port**，所以：

- **host**:www.java2s.com

- **port**:8080

## 代码提取

```html
http://www.java2s.com:8080/yourpath/fileName.htm?stove=10&path=32&id=4#harvic

```

- **getScheme()** :获取Uri中的scheme字符串部分，在这里即，http
- **getSchemeSpecificPart()**:获取Uri中的scheme-specific-part:部分，这里是：//www.java2s.com:8080/yourpath/fileName.htm?
- **getFragment()**:获取Uri中的Fragment部分，即harvic
- **getAuthority()**:获取Uri中Authority部分，即www.java2s.com:8080
- **getPath()**:获取Uri中path部分，即/yourpath/fileName.htm
- **getQuery()**:获取Uri中的query部分，即stove=10&path=32&id=4
- **getHost()**:获取Authority中的Host字符串，即www.java2s.com
- **getPort()**:获取Authority中的Port字符串，即8080
- **List< String> getPathSegments()**:上面我们的getPath()是把path部分整个获取下来：/yourpath/fileName.htm，getPathSegments()的作用就是依次提取出Path的各个部分的字符串，以字符串数组的形式输出
- **getQueryParameter(String key)**:在上面我们通过getQuery()获取整个query字段：stove=10&path=32&id=4，getQueryParameter(String key)作用就是通过传进去path中某个Key的字符串，返回他对应的值

## 从scheme启动app

- 原理：通过隐式的intent匹配可以处理对应scheme的activity

- 如果想从网络浏览器打开app,必须指定

```java
<category android:name="android.intent.category.BROWSABLE" />
```

- 示例

```xml

 <activity
    android:name=".ui.Activity_Scheme"
    android:configChanges="orientation|keyboardHidden|navigation|locale|screenSize"
    android:label="@string/app_name"
    android:launchMode="singleTop"
    android:theme="@android:style/Theme.NoTitleBar"
    android:windowSoftInputMode="adjustPan|stateHidden">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="chushoutv" />
    </intent-filter>
</activity>

```

```java
    private static final String SCHEME = "chushoutv";

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Intent intent = getIntent();
        if (null == intent ||
                intent.getAction() == null ||
                intent.getAction().compareTo(Intent.ACTION_VIEW) != 0) {
            finish();
            return;
        }

        Uri uri = intent.getData();
        if (null == uri) {
            finish();
            return;
        }

        String scheme = uri.getScheme();
        if (null == scheme || !scheme.equals(SCHEME)) {
            finish();
            return;
        }

        // 然后针对uri中的query param做具体的跳转
    }

```