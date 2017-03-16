# Android开发第三方知识点笔记

## android stuido找不到源码

- 升级as,下载了android 源码，但找不到源码解决办法，找到jdk.table.xml这个文件

```text

Windows file location:
C:\Users{USER_NAME}.AndroidStudio2.0\config\options\jdk.table.xml

Linix file location:
~/Library/Preferences/AndroidStudioBeta/options/jdk.table.xml

<root type="simple" url="file://D:/android/sdk/sources/android-23" />

```

## 微信UnionID

- **OpenID**:一个用户在一个接入了微信登录的第三方APP下的唯一标识符，无论授权多少次，只要第三方app不变，那么它的OpenID不变，在不同app下的OpenID不同

- **UnionID**:**同一个微信开发者账号下**有多个app,网站等，它们分别用微信登录，**获得的UnionID是一样的**，但是OpenID是不一样的
