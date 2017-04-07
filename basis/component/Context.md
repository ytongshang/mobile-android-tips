# Context

## Context的应用场景

![Context应用场景](./../../image-resources/Context的应用场景.jpg)

- 有一些NO上添加了一些数字，其实这些从能力上来说是可以的，下面一个一个解释：
    - 数字1：启动Activity在这些类中是可以的，但是需要创建一个新的task,也就是要设置Intent.FLAG_ACTIVITY_NEW_TASK
    - 数字2：在这些类中去layout inflate是合法的，但是会使用系统默认的主题样式，如果你自定义了某些样式可能不会被使用。
    - 数字3：在receiver为null时允许，在4.2或以上的版本中，用于获取黏性广播的当前值。（可以无视）

- 其实在Application／Service也是可以启动dialog的，
 不过要设置Window的类型为WindowManager.LayoutParams.TYPE_SYSTEM_ALERT，
 也就需要对应的权限"android.permission.SYSTEM_ALERT_WINDOW"

```java
sweetAlertDialog.getWindow().setType((WindowManager.LayoutParams.TYPE_SYSTEM_ALERT));
```