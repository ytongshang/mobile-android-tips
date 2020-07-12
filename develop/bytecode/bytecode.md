# 字节码

- [jvm bytecode](https://docs.oracle.com/javase/specs/jvms/se11/html/index.html)
- [android bytecode](https://source.android.com/devices/tech/dalvik/dalvik-bytecode)
- [asm gralde plugin](https://github.com/stven0king/AndroidPluginStudy)

## 查看字节码

```bash
javac Sample.java   // 生成Sample.class，也就是Java字节码
javap -v Sample     // 查看Sample类的Java字节码

//通过Java字节码，生成Dalvik字节码
dx --dex --output=Sample.dex Sample.class

dexdump -d Sample.dex   // 查看Sample.dex的Dalvik的字节码

```

