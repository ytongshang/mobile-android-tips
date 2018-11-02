# Android Studio

- [android  library版本配置](#android--library版本配置)
- [android studio 常用插件](#android-studio-常用插件)
- [android stuido找不到源码](#android-stuido找不到源码)
- [自定义BuildConfig变量](#自定义buildconfig变量)
- [v2SigningEnabled](#v2signingenabled)
- [混淆配置](#混淆配置)
- [adb查看最上层的activity](#adb查看最上层的activity)
- [Android依赖关系查找](#android依赖关系查找)

## android  library版本配置

``` java

ext {
    minSdkVersion = 14
    targetSdkVersion = 25
    compileSdkVersion = 25
    buildToolsVersion = "25.0.2"
    versionCode = 1
    versionName = "1.0"

    supportlibrary = "25.3.0"
    rxjava = "2.0.7"
    rxandroid = "2.0.1"
    okhttp = "3.6.0"
    fresco = "1.2.0"
}

```

## android studio 常用插件

```java

FindViewByMe
Gradle View
ADB Idea
Android Parcelable code generator
WakaTime

AndroidProguardPlugin
https://github.com/zhonghanwen/AndroidProguardPlugin

```

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

- 比如app的引导页，只有在引导页的版本发生了变化，才要显示出来，一种简单的做法就是自定义BuildConfig变量

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

- Android 7.0 中新增了 APK Signature Scheme v2 签名方式,目前比较流行的2套多渠道打包脚本,实质上都会在签名后修改APK文件,目前都会造成在7.0以上版本签名认证失败
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

## 混淆配置

- 一个android stuido工程有多个library project,在每个library project都定义了混淆配置，
 **最后还必须将library的混淆复制到主工程的混淆配置中**
- 另外一种方法是，在Library指定混淆配置，然后将混淆配置文件保留

```groovy
android {

    compileSdkVersion rootProject.ext.compileSdkVersion
    buildToolsVersion rootProject.ext.buildToolsVersion

    defaultConfig {
        minSdkVersion rootProject.ext.minSdkVersion
        targetSdkVersion rootProject.ext.targetSdkVersion
        versionCode 1
        versionName "1.0.0"
        // 保留混淆配置文件
        consumerProguardFiles 'proguard-rules.pro'

    }
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }

    lintOptions {
        abortOnError false
    }
}
```

## adb查看最上层的activity

- 查看最上面的activity

```bash
Linux:
adb shell dumpsys activity | grep "mFocusedActivity"

windows:
adb shell dumpsys activity | findstr "mFocusedActivity"
```

## Android依赖关系查找

```bash
gradlew -q app:dependencies
```

其中app是指module的名字
