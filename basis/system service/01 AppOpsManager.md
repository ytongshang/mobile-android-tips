# AppOpsManager

[Android 5.1 AppOps总结](http://blog.csdn.net/lewif/article/details/49124757)

## 定义

- AppOps全称是 Application Operations，类似我们平时常说的应用程序的操作（权限）管理，AppOps是Google原生Android包含的功能，Android M的动态权限申请就是基于AppOps
- AppOps虽然涵盖了 App的权限管理，但是Google原生的设计并不仅仅是对“权限”的管理，而是对App的“动作”的管理。
 我们平时讲的权限管理多是针对具体的权限（App开发者在Manifest里申请的权限），而AppOps所管理的是所有可能涉及用户隐私和安全的操作，包括 access notification, keep weak lock,  activate vpn, display toast 等等，有些操作是不需要Manifest里申请权限的。

## 相关函数

```java
// 快速检查某项动作是否允许，不会校验uid与packageName的一致性
public int checkOp(String op, int uid, String packageName)
public int checkOpNoThrow(String op, int uid, String packageName)

// 必须同时传入uid与packageName,并且成功的话，会修改该app这项动作的最后执行时间
public int noteOp(String op, int uid, String packageName)
public int noteOpNoThrow(String op, int uid, String packageName)

// app开始执行一项长时间的动作时传入，必须同时传入uid与packageName
// 长时间行为完成后，必须调用finishOp
public int startOp(String op, int uid, String packageName)
public int startOpNoThrow(String op, int uid, String packageName)
public void finishOp(String op, int uid, String packageName)
```

```java
@TargetApi(Build.VERSION_CODES.LOLLIPOP)
private static boolean checkUsageStatsPermission(Context context) {
    try {
        PackageManager packageManager = context.getPackageManager();
        ApplicationInfo applicationInfo = packageManager.getApplicationInfo(context.getPackageName(), 0);
        AppOpsManager appOpsManager = (AppOpsManager) context.getSystemService(Context.APP_OPS_SERVICE);
        int mode = appOpsManager.checkOpNoThrow(AppOpsManager.OPSTR_GET_USAGE_STATS, applicationInfo.uid, applicationInfo.packageName);
        return (mode == AppOpsManager.MODE_ALLOWED);
    } catch (PackageManager.NameNotFoundException e) {
        return false;
    }
}
```

## 使用

- 由于AppOpsManager是在API 23引入的，所以在调用的时候，我们应应当使用AppOpsManagerCompat
- **但是要注意的是默认23以下的实现返回的是MODE_IGNORED**

```java
// 开源库AndPermission中的权限检查，因为23以前只要在Manifest中申请就可以了，所以23以下默认返回true
 public static boolean hasPermission(@NonNull Context context, @NonNull String... permissions) {
        if(Build.VERSION.SDK_INT < Build.VERSION_CODES.M) return true;
        for (String permission : permissions) {
            String op = AppOpsManagerCompat.permissionToOp(permission);
            int result = AppOpsManagerCompat.noteProxyOp(context, op, context.getPackageName());
            if (result == AppOpsManagerCompat.MODE_IGNORED) return false;
            result = ContextCompat.checkSelfPermission(context, permission);
            if(result != PackageManager.PERMISSION_GRANTED) return false;
        }
        return true;
    }
```