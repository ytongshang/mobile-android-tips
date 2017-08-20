# Intent

## 隐式intent与显式intent

- 对于隐式intent，将intent的内容与AndroidManifest.xml中定义的intent filter相匹配，
 如果匹配，则启动该 activity，如果有多个匹配，则显示对话框让用户选择
- **一个component只有定义了intent filter才可能被隐式intent启动**，否则只能被显式Intent启动


## 构建intent

- componet,action,data,category,决定了由哪一个或哪些处理intent,而extras则包含了更详细的数据flags，指定了intent的metadata,比如FLAG_ACTIVITY_NEW_TASK 等等

### Component

- 可选，如果指定了就是显式inent
- **对于service,必须指定component**
- 可以通过setComponent(),setClass(),setClassName(), 或者构造函数指定component

### Action

- intent的action指定了要执行什么动作，从而也间接影响了intent的其它数据结构，比如extras与data
- 通过setAction（）和构造函数指定具体的action
- 如果是自定义action,一般情况下必须在action前加上完整的package name

```java
// 常见的action
Intent.ACTION_VIEW
Intent.ACTION_SEND

// 自定义action,加上package name
public static final String ACTION_TIMETRAVEL = "com.example.action.TIMETRAVEL";
```

### Data

- intent的data属性决定了可以操作的对象的uri或者mine type
- 通过setData()指定uri
- 通过setType()指定mine type
- **如果要同时设置uri与mine type，不要先后使用setData(),setType()，因为设置一个会影响另一个的，应该使用setDataAndType()**

### Category

- 包含了component应当怎样处理intent的额外信息，
- 一个intent可以加入多个category，
- 一般不需要自动设置category,startActivity()与startActivityForResult()的intent自动增加了CATEGORY_DEFAULT
- 通过addCategory（）指定category,常见的category有

```java
Intent.CATEGORY_BROWSABLE
//可以用浏览器打开
Intent.CATEGORY_LAUNCHER
//启动
```


## 隐式Intent

- 对于隐式intent，可能没有任何应用可以处理,需要先判断是否有应用可以处理

```java
static final int REQUEST_IMAGE_CAPTURE = 1;
Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
    startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE);
}
```

## Intent Filter

- 若activity中的intent filter满足以下intent对象的标准，系统就能够把特定的intent发送给activity:
- Action:一个想要执行的动作的名称。一般是intent里面的常量，比如Intent.ACTION_VIEW
- Data:Intent附带数据的描述。在intent filter中通过<data>指定它的值，可以使用一个或者多个属性，决定了URI的scheme, host, port, path，也可以指定附带数据的mine type
- Category:提供一个附加的方法来标识这个activity能够handle的intent,**所有的implicit intents都默认是 CATEGORY_DEFAULT 类型的**,所以在定义隐式intent时的时候，必须指定category为CATEGORY_DEFAULT,在intent filter中用<category>指定它的值

```xml
<activity android:name="ShareActivity">
    <intent-filter>
        <action android:name="android.intent.action.SEND"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <data android:mimeType="text/plain"/>
        <data android:mimeType="image/*"/>
    </intent-filter>
</activity>
```

## intent与intent filter的匹配

### action 匹配

- 一个intent只能有一个action
- 一个intent fileter却可以有多个action
- 如果intent filter没有任何action,那么任何Intent都不能与之匹配上
- 如果intent 没有action，只要intent fileter有action，就有可能匹配上，当然要对category,data进一步匹配

### category匹配

- 一个intent filter可以有多个categories
- intent中的每一个category都要与intent fileter中的某个匹配，否则就不能通过category检测，
 反之，如果intent fileter中的category多于intent中的，intent可通过了category检测

### data 匹配

- data的匹配，可以指定URI的 scheme, host, port, 和 path，这其中的任何一个都是可选的，但是之间有依赖关系
- 如果没有指定scheme,那么host无效
- 如果没能指定host，那么port无效
- 如果scheme和host都没指定，那么path无效
- 当intent与intent filter进行匹配时，只会检查在intent filter中指定了的部分，如果intent filter只指定了scheme，那么只会检测scheme，如果只指定了scheme 与authority,那么只会检测scheme与authority

### mine type与uri的匹配

- intent mine type与uri都没指定，只有当intent filter也都没指定才会通过
- intent 指定了uri，没有mine type(也没有隐式的指定mine type),只有当intent fileter与intent的uri格式相同，也没指定mine type才通过
- intent只指定了mine type，没有指定uri,只有intent filter也指定了相同的mine type,没有指定uri才会通过
- 如果两者都指定，首先要intent中的type要与intent filter中的某项相匹配，另外intent的 uri与uri filter中的某项相匹配，或者intetn是一个content：或file: URI，并且intent fileter没有指定uri

### intent filter的其它应用

- intent与intent filter的匹配，不仅可以找到一个符合的component来激活，而且可以发现系统上的componets，比如指定Intent.ACTION_MAIN,Intent.CATEGORY_LAUNCHER来查找系统上安装的应用
- 可以通过 Intent的方法queryIntentActivities()，queryIntentServices()， queryBroadcastReceivers()查找符合对应的activity, service, broadcast

```java

//Intent.ACTION_MAIN,Intent.CATEGORY_LAUNCHER可以查询安装了哪些应用
Intent startupIntent = new Intent(Intent.ACTION_MAIN);
startupIntent.addCategory(Intent.CATEGORY_LAUNCHER);
PackageManager pm = getActivity().getPackageManager();
List<ResolveInfo> activities = pm.queryIntentActivities(startupIntent, 0);
```

## startActivity()

- 对于隐式intent来说，startActivity()并不是打开满足intent的activity,而是打开默认的满足intent的activity,
 所以如果要每次都显示可的应用，可用chooser

```java
public static Intent createChooser(Intent target, String title)
```


## Pending intent

- Intent 是及时启动，intent 随所在的activity 消失而消失。
- PendingIntent 可以看作是对intent的包装，通常通过PendngIntent.getActivity(),PendingIntent.getBroadcast (),PendingInteng.getService()来得到pendingintent的实例。
- 正由于pendingintent中 保存有当前App的Context，使它赋予外部App一种能力，使得外部App可以如同当前App一样的执行pendingintent里的Intent， 就算在执行时当前App已经不存在了，也能通过存在pendingintent里的Context照样执行Intent。
- 常见的pending Intent的使用地方
    - notification，用户操作通知时的动作，由NotificationManager处理PendingIntent
    - App widget，当用户与app widget交户时，由HomeScren app处理pendingInten
    - 将来某个时间点做的事情，由alarmManager处理pendingIntent

## Task

- android使用task来记录用户在每一个application的状态
- task实际是一个stack，里面记录了相关联的activities
- 一个task可能含有不同application的activity
- Intent.FLAG_ACTIVITY_NEW_TASK 可以以一个新的task来启动activity

```java
Intent i = new Intent(Intent.ACTION_MAIN);
i.setClassName(activityInfo.applicationInfo.packageName, activityInfo.name);
i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
startActivity(i);
```

- 如果启动一次intent i,当再次以Intent.FLAG_ACTIVITY_NEW_TASK启动intent时，只会有一个
- 一个task有来自己不同application的activity,这些activity的process是不同的，
 都在对应的application的   Process中运行，但是他们是同一个task
- process可以kill,task不能kill




