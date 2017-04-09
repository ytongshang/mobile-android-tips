# Task 和 Back-Stack

- [google LaunchModes](http://developer.android.com/guide/components/tasks-and-back-stack.html#LaunchModes)
- [activity task相关](http://blog.csdn.net/liuhe688/article/details/6761337)

## Task

- **任务是指在执行特定作业时与用户交互的一系列Activity**。 这些Activity按照各自的打开顺序排列在back-stack中。
 启动一个应用,也就创建一个与之对应的task。
- 当用户触摸应用启动器中的图标（或主屏幕上的快捷方式）时，该应用的任务将出现在前台。如果应用不存在任务（应用最近未曾使用），则会创建一个新任务，并且该应用的“主”Activity 将作为堆栈中的根Activity打开。
- **任务是一个有机整体，当用户开始新任务或通过“主页”按钮转到主屏幕时，可以移动到“后台”**。
- **当任务处在后台时，该任务中的所有Activity全部停止，但是任务的返回栈仍旧不变**，也就是说，当另一个任务发生时，该任务仅仅失去焦点而已。
- 任务可以再次返回到“前台”，用户就能够回到离开时的状态
- **后台可以同时运行多个任务**
- **如果用户同时运行多个后台任务，则系统可能会开始销毁后台Activity，以回收内存资源，从而导致 Activity 状态丢失**

## Back-Stack

- 任务栈是一个具有栈结构的对象，“先进后出”
- **默认情况下，所有activity所需的任务栈的名字为应用的包名，当然我们也可以通过taskAffinity为每一个activity指定一个任务栈**
- 任务栈中的Activity永远不会重新排列，仅推入和弹出堆栈，因而当我们再次start一个前面已经start过的activity，只是在stack中新增了一个该activiry的instance,而不是将前面已有的activity重新排序(针对standard启动的)

## Task与Back-Stack的默认行为

- 当Activity A启动Activity B时，Activity A将会停止，但系统会保留其状态（例如，滚动位置和已输入表单中的文本）。
 如果用户在处于 Activity B 时按“返回”按钮，则 Activity A 将恢复其状态，继续执行。
- 用户通过按“Home”按钮离开任务时，当前Activity将停止且其任务会进入后台。 系统将保留任务中每个Activity的状态。
 如果用户稍后通过选择开始任务的启动器图标来恢复任务，则任务将出现在前台并恢复执行堆栈顶部的Activity。
- 如果用户按“返回”按钮，则当前Activity会从堆栈弹出并被销毁。堆栈中的前一个 Activity 恢复执行。销毁 Activity 时，
 系统不会保留该Activity 的状态。
- **即使来自其他任务，Activity也可以多次实例化**。

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

- 默认的行为，一个任务栈可以有多个实例，每个实例也可以属于不同的任务栈，在这种模式下，
 谁启动了这个Activity,那么这个Activity就运行在启动它的那个Activity的任务栈
- **对于standard启动模式的Activity,如果由非Activity的Context（Application/Service）启动，必须加上Intent.FLAG_ACTIVITY_NEW_TASK标识.**

### single top

- 对于Activity A，如果当前task的最顶部的是activity A的实例，不会再创建一个新的A的实例，intent通过onNewIntent()进行处理。
- 只要当前task的back stack的最顶部不是A的实例，那么A就可以多次被实例化，每个实例可以分属不同的task,
 每个task可以有多个A的实例

>>For example, suppose a task's back stack consists of root activity A with activities B, C, and D on top (the stack is A-B-C-D; D is on top). An intent arrives for an activity of type D. If D has the default "standard"launch mode, a new instance of the class is launched and the stack becomes A-B-C-D-D. However, if D's launch mode is "singleTop", the existing instance of D receives the intent through onNewIntent(), because it's at the top of the stack—the stack remains A-B-C-D. However, if an intent arrives for an activity of type B, then a new instance of B is added to the stack, even if its launch mode is "singleTop"

### single task

比如以singleTask启动A

- 系统首先会查找是否存在A想要的任务栈，如果不存在，就重新创建一个任务栈，然后创建A的实例后将A放到栈中
- 如果存在A所需要的栈,这时要查看是否有A的实例，如果实例存在，那么系统就会把A调到栈顶并调用它的onNewIntent方法
- 如果实例不存在，就创建A然后把A压入栈中

### single instance

- 与single task差不多，具有SingleTask的所有特性，还加强了一点，具有此种模式的Activity只能单独地位于一个任务栈中

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

### FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS

- 如果设置这个标志，这个Activity就不会显示在最近启动的Activity中

### FLAG_ACTIVITY_NO_HISTORY

- 如果设置这个标志，新的Activity就不会在历史栈中保存。用户一旦离开，这个Activity就会finish掉。也可以使用noHistory属性设置

### FLAG_ACTIVITY_NO_USER_ACTION

- 如果设置了这个标志，可以在避免用户离开当前Activity时回调到 onUserLeaveHint(). 通常，Activity可以通过这个回调表明有明确的用户行为将当前activity切出前台。 
 这个回调标记了activity生命周期中的一个恰当的点，可以用来“在用户看过通知之后”将它们清除。
- 如果Activity是由非用户驱动的事件（如电话呼入或闹钟响铃）启动的，那这个标志就应该被传入Context.startActivity，以确保被打断的activity不会认为用户已经看过了通知

## Handling affinities

### android:taskAffinity

- 定义了一个activity的task归属问题，默认情况下，所有Activity所需要的任务栈
- android:taskAffinity，接受一个参数，一般是一个包名，用来指定Activity所属任务栈的名字
- TaskAffinity一般和SingleTask或者allowTaskReparenting一起使用
- **当SingleTask与TaskAffinity一起使用时**，它是具有该模式的Activity的目前任务栈的名字，**待启动的Activity会运行在名字和TaskAffinity相同的任务栈中**

### allowTaskReparenting

- allowTaskReparenting，**这个属性用来标记一个Activity实例在当前应用退居后台后，是否能从启动它的那个task移动到有共同affinity的task中**，“true”表示可以移动，
 “false”表示它必须呆在当前应用的task中，默认值为false。如果一个Activity的<activity>元素没有设定此属性，设定在<application>上的此属性会对此Activity起作用
- 当taskAffinity和allowTaskReparenting一起使用时，当应用A启动了应用B的某个Activity后，如果这个Activity的allowTaskReparenting为true的话，
 当应用B被启动后，此Activity会直接从应用A的任务栈移动到应用B的任务栈

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





















