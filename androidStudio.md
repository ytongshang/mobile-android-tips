#### 找不到源码
* 升级as,下载了android 源码，但找不到源码
* 解决办法，找到jdk.table.xml这个文件，在<sourcePath>节点下添加这一句

```
Windows file location: C:\Users{USER_NAME}.AndroidStudio2.0\config\options\jdk.table.xml
Linix file location: ~/Library/Preferences/AndroidStudioBeta/options/jdk.table.xml
<root type="simple" url="file://D:/android/sdk/sources/android-23" />
```
