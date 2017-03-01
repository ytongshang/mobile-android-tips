# Snippet

## 获得资源id

```java
Resources resources = context.getResources();
int indentify= getResources().getIdentifier("icon", "drawable", "org.anddev.android.testproject");

int resId = getResources().getIdentifier("background", "color", getPackageName());
startBtn.setTextColor(getResources().getColor(resId));

public static int getResourceId(Context context,String name,String type,String packageName) {
        Resources themeResources = null;
        PackageManager pm = context.getPackageManager();
        try {
            themeResources = pm.getResourcesForApplication(packageName);
            return themeResources.getIdentifier(name, type, packageName);
        } catch (NameNotFoundException e) {
            e.printStackTrace();
        }
        return 0;
 }
```

## 获得android res文件下的uri

- "res://" + 包名+类型名 + "/" + 资源id

```java
Uri uri = Uri.parse("android.resource://"+getPackageName()+"/"+R.raw.xinyueshenhua);
Uri uri = Uri.parse("android.resource://"+getPackageName()+"/"+R.drawable.ic_launcher);

public static  Uri getResourceUri(int resId,String packageName) {
    return Uri.parse("android.resource://"+packageName+"/"+resId);
}
```

## 给我们评分

```java
Intent intent = new Intent(Intent.ACTION_VIEW);
intent.setData(Uri.parse("market://details?id=" + mContext.getPackageName()));
if (intent.resolveActivity(mContext.getPackageManager()) != null) {
    startActivity(Intent.createChooser(intent, "给我们评分"));
}
```
