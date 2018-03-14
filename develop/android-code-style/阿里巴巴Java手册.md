# 阿里巴巴-Java

## 命名规约

- 抽象类命名使用Abstract或Base开头；异常类命名使用Exception结尾；测试类命名以它要测试的类名开始，以Test 结尾

- POJO 类中布尔类型的变量，都不要加is前缀，否则部分框架解析会引起序列化错误

- **包名统一使用单数形式，但是类名如果有复数含义，类名可以使用复数形式**

- **如果模块、接口、类、方法使用了设计模式，在命名时体现出具体模式。**
    - public class OrderFactory
    - public class LoginProxy
    - public class ResourceObserver;

- **枚举类名建议带上 Enum 后缀**，枚举成员名称需要全大写，单词间用下划线隔开

## 代码格式

- 注释的双斜线与注释内容之间有且仅有一个空格

### OOP规约

- **序列化类新增属性时，请不要修改 serialVersionUID 字段，避免反序列失败；如果完全不兼容升级，避免反序列化混乱，那么请修改 serialVersionUID 值。**

- **构造方法里面禁止加入任何业务逻辑，如果有初始化逻辑，请放在init方法中**

- **使用索引访问用 String 的 split 方法得到的数组时，需做最后一个分隔符后有无内容的检查，否则会有抛 IndexOutOfBoundsException 的风险**。

```java
String str = "a,b,c,,";
String[] ary = str.split(",");
// 预期大于 3，结果是 3
System.out.println(ary.length);
```

- 推荐：**类内方法定义的顺序依次是：公有方法或保护方法 > 私有方法 > getter/setter方法。**

- 类成员与方法访问控制从严：
    - 如果不允许外部直接通过 new 来创建对象，那么构造方法必须是 private。
    - 工具类不允许有 public 或 default 构造方法。
    - 类非static成员变量并且与子类共享，必须是 protected。
    - 类非static成员变量并且仅在本类使用，必须是 private。
    - 类static成员变量如果仅在本类使用，必须是 private。
    - 若是static成员变量，必须考虑是否为 final。
    - 类成员方法只供类内部调用，必须是 private。
    - 类成员方法只对继承类公开，那么限制为 protected。

## 集合处理

- equals与hashCode
    - 只要重写 equals，就必须重写 hashCode。
    - 因为 Set 存储的是不重复的对象，依据 hashCode 和 equals 进行判断，所以 **Set 存储的对象必须重写这两个方法。**
    - 如果自定义对象作为 Map 的键，那么必须重写 hashCode 和 equals。

- subList
    - ArrayList的subList结果不可强转成ArrayList
    - **subList是原List的一个视图，对于 SubList 子列表的所有操作最终会反映到原列表上**
    - 在 subList 场景中，高度注意对原集合元素个数的修改，会导致子列表的遍历、增加、删除均会产生 ConcurrentModificationException 异常
    - **删除一部分的数据,list.subList(0,3).clear();**

- **使用集合转数组的方法，必须使用集合的 toArray(T[] array)，传入的是类型完全一样的数组，大小就是 list.size()**

```java
List<String> list = new ArrayList<String>(2);
list.add("guan");
list.add("bao");
String[] array = new String[list.size()];
// 直接使用 toArray 无参方法存在问题，此方法返回值只能是 Object[]类，
// 若强转其它类型数组将出现 ClassCastException 错误
array = list.toArray(array);
```

- Arrays.asList()
    - Arrays.asList()把数组转换成集合时，不能使用其修改集合相关的方法
    - **Arrays.asList体现的是适配器模式，只是转换接口，后台的数据仍是数组**

```java
String[] str = new String[] { "you", "wu" };
List list = Arrays.asList(str);

// 那么 list.get(0)也会随之修改
str[0] = "gujin";
```

- **不要在foreach循环里进行元素的remove/add 操作。remove 元素请使用 Iterator方式**

- 集合初始化时，指定集合初始值大小
    - **initialCapacity = (需要存储的元素个数 / 负载因子) + 1**。注意负载因子（即 loaderfactor）默认为 0.75
    - **如果暂时无法确定初始值大小，请设置为 16**

- Map中K/V能否为null的情况

集合类            | Key           | Value         | Super       | 说明
------------------|---------------|---------------|-------------|----------------------
Hashtable         | 不允许为 null | 不允许为 null | Dictionary  | 线程安全
ConcurrentHashMap | 不允许为 null | 不允许为 null | AbstractMap | 锁分段技术（JDK8:CAS）
TreeMap           | 不允许为 null | 允许为 null   | AbstractMap | 线程不安全
HashMap           | 允许为 null   | 允许为 null   | AbstractMap | 线程不安全

- **利用Set对元素去重**