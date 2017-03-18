# Android Studio

- [android stuido找不到源码](#android-stuido找不到源码)
- [自定义BuildConfig变量](#自定义buildconfig变量)


## android stuido找不到源码

- 升级as,下载了android 源码，但找不到源码解决办法，找到jdk.table.xml这个文件

```java

Windows file location:
C:\Users{USER_NAME}.AndroidStudio2.0\config\options\jdk.table.xml

Linix file location:
~/Library/Preferences/AndroidStudioBeta/options/jdk.table.xml

<root type="simple" url="file://D:/android/sdk/sources/android-23" />

```

## 自定义BuildConfig变量

- 比如app的引导页，只有在引导页的版本发生了变化，才要显示出来，一种简单的做法就是自定义BuildConfig变量

```java

android {
    //...

    defaultConfig {
        //引导页的版本号，如果更新引导页，需要修改这个值
        buildConfigField "int", "GUIDE_VERSION", "1"
    }
    //...
}

if (BuildConfig.GUIDE_VERSION > SP_Manager.Instance().mGuideVersion) {
    // 显示引导页
}

```

## v2SigningEnabled

- Android 7.0 中新增了 APK Signature Scheme v2 签名方式,目前比较流行的2套 多渠道打包脚本,实质上都会在签名后修改APK文件,目前都会造成在7.0以上版本签名认证失败
    - 在APK内注入${channel}.txt 文件
    - 在APK的zip info中写入 channel 信息

```java

signingConfigs {
       release {
           storeFile file("xxxx")
           storePassword "xxxx"
           keyAlias "xxxx"
           keyPassword "xxxx"
           v2SigningEnabled false
       }
       debug {
           storeFile file("xxxx")
           storePassword "xxxx"
           keyAlias "xxxx"
           keyPassword "xxxx"
           v2SigningEnabled false
       }
   }

```
