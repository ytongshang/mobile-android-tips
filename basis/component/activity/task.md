# Task

- [google LaunchModes](http://developer.android.com/guide/components/tasks-and-back-stack.html#LaunchModes)
- [activity task相关](http://blog.csdn.net/liuhe688/article/details/6761337)

## Task 原理

- task是一个具有栈结构的对象，“先进后出”，一个task可以管理多个Activity，启动一个应用，
 也就创建一个与之对应的task。
- task中的activities是不会再排序的，因而当我们再次start一个前面已经start过的activity，
 只是在stack中新增了一个该activiry的instance,而不是将前面已有的activity重新排序(针对standard启动的)
- task与back stack的基本行为
>> When Activity A starts Activity B, Activity A is stopped, but the system retains its state (such as scroll position and text entered into forms). If the user presses the Back button while in Activity B, Activity A resumes with its state restored.
When the user leaves a task by pressing the Home button, the current activity is stopped and its task goes into the background. The system retains the state of every activity in the task. If the user later resumes the task by selecting the launcher icon that began the task, the task comes to the foreground and resumes the activity at the top of the stack.
If the user presses the Back button, the current activity is popped from the stack and destroyed. The previous activity in the stack is resumed. When an activity is destroyed, the system does not retain the activity's state.
Activities can be instantiated multiple times, even from other tasks.

## 改变task与back stack默认行为

- activity 属性

```java
taskAffinity
launchMode
allowTaskReparenting
clearTaskOnLaunch
alwaysRetainTaskState
finishOnTaskLaunch
```

- start activity时设置,intent的flag

```java
FLAG_ACTIVITY_NEW_TASK
FLAG_ACTIVITY_CLEAR_TOP
FLAG_ACTIVITY_SINGLE_TOP
```

## Manifest中定义launch mode

- 定义了一个新的activity的实例与当前task是怎样关联的
- 可以在要intent中定义，也可以manifest中定义，如果同时定义了，与intent中定义的为准
- manifest中可以定义4种：standard, singleTop,single Task ,single instance

### standard

- 默认的行为，一个activity 可以创建多个实例，每个实例可以分属不同的task，一个task可以有多个实例

### single top

- 对于Activity A，如果当前task的最顶部的是activity A的实例，不会再创建一个新的A的实例，
 intent通过onNewIntent()进行处理。
- 只要当前task的back stack的最顶部不是A的实例，那么A就可以多次被实例化，每个实例可以分属不同的task,
 每个task可以有多个A的实例

>>For example, suppose a task's back stack consists of root activity A with activities B, C, and D on top (the stack is A-B-C-D; D is on top). An intent arrives for an activity of type D. If D has the default "standard"launch mode, a new instance of the class is launched and the stack becomes A-B-C-D-D. However, if D's launch mode is "singleTop", the existing instance of D receives the intent through onNewIntent(), because it's at the top of the stack—the stack remains A-B-C-D. However, if an intent arrives for an activity of type B, then a new instance of B is added to the stack, even if its launch mode is "singleTop"

### single task

- 开始一个新的task，并且将该activity的实例作为task的root;
- 但是，如果已经一个task有了该activity的实例，该task会进入foreground,back stack中该activity实例之上  的所有的activity 都会出栈，而新的intent会传递到onNewIntent中去。该acitivy的实例，一次只能存在一次。

### single instance

- 与single task差不多，但是存有single instance的task不会再加入其它的activity,
 由single instance start的activity会开启一个新的activity
无论是哪种launch mode,按返回键，仍会回到原来的activity
android 浏览器 activity 指定的是single task，每次都会开启一个新的task，或者运行在已有的task内

## Intent flags

### FLAG_ACTIVITY_NEW_TASK

>> Start the activity in a new task. If a task is already running for the activity you are now starting, that task is brought to the foreground with its last state restored and the activity receives the new intent in onNewIntent().

- 同single task

### FLAG_ACTIVITY_SINGLE_TOP

>> If the activity being started is the current activity (at the top of the back stack), then the existing instance receives a call to onNewIntent(), instead of creating a new instance of the activity.
This produces the same behavior as the "singleTop" launchMode value, discussed in the previous section.

- 同single top

### FLAG_ACTIVITY_CLEAR_TOP

- 如果将要开启的activity,已经存在在back stack中，不会再创建一个该activity的实例，
 而是会将back stack中 该activity实例上面的activity会部destroyed掉，通过onNewIntent传递intent数据
- FLAG_ACTIVITY_CLEAR_TOP一般与FLAG_ACTIVITY_NEW_TASK一起使用，这样设置，可以定位一个已经存在的在其它task中的该activity实例，然后让它去处理new intent

## Handling affinities

- 定义了一个activity的task归属问题，默认情况下，同一个应用中的application会在同一个task中
- android:taskAffinity，接受一个参数，一般是一个包名，用来查找一个应用的默认包名
- SingleTask一般和TaskAffinity一起使用，这样才能发挥这种加载模式的特殊逻辑效果。
 当一个应用程序加载一singleTask模式的Activity时，首先该Activity会检查是否存在与它的taskAffinity相同的Task。1、如果存在，那么检查是否实例化，如果已经实例化，那么销毁在该Activity以上的Activity并调用onNewIntent。如果没有实例化，那么该Activity实例化并入栈。2、如果不存在，那么就重新创建Task，并入栈。

- 当一个应用程序加载一个singleInstance模式的Activity时，如果该Activity没有被实例化，那么就重新创建一个Task，并入栈，
 如果已经被实例化，那么就调用该Activity的onNewIntent。singleInstance的Activity所在的Task不允许存在其Activity，任何从该Activity加载的其它Actiivty（假设为Activity2）都会被放入其它的Task中，如果存在与Activity2相同affinity的Task，则在该Task内创建Activity2。如果不存在，则重新生成新的Task并入栈

- allowTaskReparenting，这个属性用来标记一个Activity实例在当前应用退居后台后，是否能从启动它的那个task移动到有共同affinity的task，“true”表示可以移动，“false”表示它必须呆在当前应用的task中，默认值为false。如果一个这个Activity的<activity>元素没有设定此属性，设定在<application>上的此属性会对此Activity起作用

## Clearing the back stack

- 当用户离开一个task非常长的时间后，android系统会清除back stack中除了了root activity其它的activity，
 可以设置修改activity的属性，该变这种默认行为：

### alwaysRetainTaskState

- 这个属性用来标记应用的task是否保持原来的状态，“true”表示总是保持，“false”表示不能够保证，默认为 “false”。
- 此属性只对task的根Activity起作用，其他的Activity都会被忽略。
- 默认情况下，如果一个应用在后台呆的太久例如30分钟，用户从主选单再次选择该应用时，系统就会对该应用的task进行清理，
 除了根Activity，其他Activity都会被清除出栈，但是如果在根Activity中设置了此属性之后，用户再次启动应用时，
 仍然可以看到上一次操作的界面。
- 这个属性对于一些应用非常有用，例如Browser应用程序，有很多状态，比如打开很多的tab，用户不想丢失这些状态，使用这个属性就极为恰当

### clearTaskOnLaunch

- 这个属性用来标记是否从task清除除根Activity之外的所有的Activity，“true”表示清除，“false”表示不清除，默认为“false”。
- 同样，这个属性也只对根Activity起作用，其他的Activity都会被忽略。
- 如果设置了这个属性为“true”，每次用户重新启动这个应用时，都只会看到根Activity，task中的其他Activity都会被清除出栈。
 如果我们的应用中引用到了其他应用的Activity，这些Activity设置了allowTaskReparenting属性为“true”，
 则它们会被重新宿主到有共同affinity的task中。

### finishOnTaskLaunch

- 与clearTaskOnLaunch类似，不同之处在于allowReparenting属性是重新宿主到有共同affinity的task中，而finishOnTaskLaunch属性是销毁实例。如果这个属性和android:allowReparenting都设定为“true”，则这个属性胜出





















