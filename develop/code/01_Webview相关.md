# Webview

## JsBridge

- [JSbridge系列解析（一）:JS-Native调用方法](https://www.jianshu.com/p/7d820c00642a)

### js native交互方式

#### JS -> Native

- 通过WebView的addJavascriptInterface进行对象映射
- 通过 WebViewClient 的shouldOverrideUrlLoading方法回调拦截 url
- 通过 WebChromeClient 的onJsAlert、onJsConfirm、onJsPrompt方法回调拦截JS对话框alert、confirm、prompt消息

### native -> js

- 通过WebView的loadUrl方法，该方法必须在主线程中调用
- 通过WebView的evaluateJavascript，该方法可获取JS返回值，但4.4及以上才能使用

### 为什么要用jsbridge

- [WebView 安全之 addJavascriptInterface](https://www.jianshu.com/p/6309d243e4c0)
- 与ios一致，前端代码方便统一
- “异步”调用，支持回调

### 实现原理

#### 原理总结

- native调用js,使用webview的loadUrl,**必须要主线程**
- js调用native,通过html dom 的iframe的src变化，触发android webviewclient的shouldOverrideUrlLoading,通过拦截shouldOverrideUrlLoading的url,根据约定好的交互uri格式实现调用java方法

#### Web端发消息给Native代码流程具体分析

1. 注入js
    - webview调用loadUrl加载页面；
    - 加载完成后，在onPageFinished注入WebViewJavascriptBridge.js

```java
    // CSWebViewClient.java
    @Override
    public void onPageFinished(WebView view, String url) {
        if (mInterceptor != null) {
            mInterceptor.onPageFinished(view, url);
        }
        if (null != view) {
            view.getSettings().setBlockNetworkImage(false);
        }
        super.onPageFinished(view, url);
    }

    // WebViewClientInterceptor.java
    public void onPageFinished(WebView view, String url) {
        BridgeUtil.webViewLoadLocalJs(view, INJECT_JS);
        List<Message> list = mJsBridge.getStartupMessage();
        if (list != null) {
            for (Message m : list) {
                mJsBridge.dispatchMessage(m);
            }
        }
    }

    public static void webViewLoadLocalJs(WebView view, String path) {
        String jsContent = assetFile2Str(view.getContext(), path);
        view.loadUrl("javascript:" + jsContent);
    }
```

2. 调用callHandler方法
    - 点击jsbridge.html页面中点击"确定"按钮，调用WebViewJavascriptBridge.js中的callHandler方法

```js
function btn1OnClick() {
        var method = document.getElementById("text1").value;
        var params = {
            data: document.getElementById("text2").value
        };
        window.connectWebViewJavascriptBridge(function (bridge) {
            bridge.callHandler(method, params, function (responseData) {
                dealNativeResponse(responseData, new ResponseHandler(
                    function (obj) {
                        document.getElementById("resp_from_native").innerHTML = obj;
                    },
                    function (code, message) {
                        console.log("code:" + code + ",msg=" + message)
                    }
                ));
            })
        });

    }
```

3. js发送消息
    - 调用WebViewJavascriptBridge发送消息调用_doSend；
    - 将消息存放在sendMessageQueue中
    - 将responseCallbck放在responseCallbacks数组中，并设置message的callbackId。callbackId由uniqueId配合时间生成，用于后续查找responseCallback回调。
    - 更换iFrame的src，触发BridgeWebViewClient的shouldOverrideUrlLoading方法。

```js
    // 调用natvie方法handlerName,参数为data,responseCallback为异步回调
    function callHandler(handlerName, data, responseCallback) {
        if (arguments.length === 2 && typeof data === 'function') {
            responseCallback = data;
            data = null;

        }
        _doSend({handlerName: handlerName, data: data}, responseCallback);
    }

    //sendMessage add message, 触发native处理 sendMessage
    function _doSend(message, responseCallback) {
        if (responseCallback) {
            var callbackId = 'cb_' + (uniqueId++) + '_' + new Date().getTime();
            responseCallbacks[callbackId] = responseCallback;
            message.callbackId = callbackId;
        }

        sendMessageQueue.push(message);
        messagingIframe.src = CUSTOM_PROTOCOL_SCHEME + '://' + QUEUE_HAS_MESSAGE;
    }
```

4. iframe的src变化
    - 触发android的shouldOverrideUrlLoading
    - 方法根据url的前缀，进入了BridgeWebView的flushMessageQueue方法。

```java
    // 此是返回的url为 csjsbridge://__QUEUE_MESSAGE__/
    public boolean shouldOverrideUrlLoading(WebView view, String url) {
        String parsedUrl = "";
        try {
            url = URLDecoder.decode(url, "UTF-8");
        } catch (UnsupportedEncodingException ignored) {
            url = "";
        }

        if (url.startsWith(BridgeUtil.URI_RETURN_DATA)) { // 如果是返回数据
            mJsBridge.handlerReturnData(url);
            return true;
        } else if (url.startsWith(BridgeUtil.SCHEME_JSBRIDGE)) { //
            mJsBridge.flushMessageQueue();
            return true;
        }
        return false;
    }
```

5. flushMessageQueue
    - 通过loadUrl调用到WebViewJavascriptBridge.js中的_fetchQueue()方法
    - 注册了一个回调函数,将其存放在responseCallbacks

```java
//BridgeWebView.java
void flushMessageQueue() {
    // 调用 javascript:WebViewJavascriptBridge._fetchQueue();
    if (Thread.currentThread() == Looper.getMainLooper().getThread()) {
        loadUrl(BridgeUtil.JS_FETCH_QUEUE_FROM_JAVA, new CallBackFunction() {
            @Override
            public void onCallBack(String data) {
                // deserializeMessage
                ......
            }
        });
    }
}

private void loadUrl(String jsUrl, CallBackFunction returnCallback) {
    mWebView.loadUrl(jsUrl);
    responseCallbacks.put(BridgeUtil.parseFunctionName(jsUrl), returnCallback);
}
```

6. js调用_fetchQueue方法
    - _fetchQueue方法将sendMessageQueue数组中的所有消息，序列化为json字符串
    - 通过更改iFrame的src，触发shouldOverrideUrlLoading方法

```js
//WebViewJavascriptBridge.js
// 提供给native调用,该函数作用:获取sendMessageQueue返回给native,由于android不能直接获取返回的内容,所以使用url shouldOverrideUrlLoading 的方式返回内容

    function _fetchQueue() {
        var messageQueueString = JSON.stringify(sendMessageQueue);
        sendMessageQueue = [];
        //android can't read directly the return data, so we can reload iframe src to communicate with java
        messagingIframe.src = CUSTOM_PROTOCOL_SCHEME + '://return/_fetchQueue/' + encodeURIComponent(messageQueueString);
    }
```

7. handlerReturnData
    - 进入shouldOverrideUrlLoading方法根据url的前缀，进入了BridgeWebView的handlerReturnData方法。
    - 根据传入的url获取回调函数的functionName为_fetchQueue。根据步骤5，最终调用了flushMessageQueue中loadUrl传入的回调函数

```java
// url csjsbridge://return/_fetchQueue/[{"handlerName":"functionFromNative","data":{"data":"传给Native的参数"},"callbackId":"cb_1_1542089192852"}]
void handlerReturnData(String url) {
    String functionName = BridgeUtil.getFunctionFromReturnUrl(url);
    CallBackFunction f = responseCallbacks.get(functionName);
    String data = BridgeUtil.getDataFromReturnUrl(url);

    if (f != null) {
        f.onCallBack(data);
        responseCallbacks.remove(functionName);
        return;
    }
}

```

8. flushMessageQueue设置的回调
    - _fetchQueue的回调函数，将json数据转化为Message数组，依次处理Message数组中的消息
    - 此时消息的responseId为空，callbackId是在步骤3的_doSend中生，用于标记send方法的回调
    - 获得js具体想要调用的方法为functionFromNative，参数为js传入的参数
    - 如果java注册了对应的functionFromNative方法,那么调用对应注册的方法，否则调用默认handler处理
    - 如果js方法需要回调native的结果，那么会将native方法执行的结果包装成Message,其中data为native执行结果
    responseId则为js中的callbackId,也就是js中最初调用callHandler生成的callbackId

```java
// url csjsbridge://return/_fetchQueue/[{"handlerName":"functionFromNative","data":{"data":"传给Native的参数"},"callbackId":"cb_1_1542089192852"}]
void flushMessageQueue() {
        if (Thread.currentThread() == Looper.getMainLooper().getThread()) {
            loadUrl(BridgeUtil.JS_FETCH_QUEUE_FROM_JAVA, new CallBackFunction() {

                @Override
                public void onCallBack(String data) {
                    // deserializeMessage 反序列化消息
                    List<Message> list;
                    try {
                        list = Message.toArrayList(data);
                    } catch (Exception e) {
                        e.printStackTrace();
                        return;
                    }
                    if (list == null || list.size() == 0) {
                        return;
                    }
                    for (int i = 0; i < list.size(); i++) {
                        Message m = list.get(i);
                        String responseId = m.getResponseId();
                        // 是否是response  CallBackFunction
                        if (!TextUtils.isEmpty(responseId)) {
                            CallBackFunction function = responseCallbacks.get(responseId);
                            String responseData = m.getResponseData();
                            function.onCallBack(responseData);
                            responseCallbacks.remove(responseId);
                        } else {
                            CallBackFunction responseFunction;
                            // if had callbackId 如果有回调Id,
                            // 说明js需要native方法执行结果的回调
                            final String callbackId = m.getCallbackId();
                            if (!TextUtils.isEmpty(callbackId)) {
                                // 如果js方法需要回调
                                responseFunction = new CallBackFunction() {
                                    @Override
                                    public void onCallBack(String data) {
                                        Message responseMsg = new Message();
                                        responseMsg.setResponseId(callbackId);
                                        responseMsg.setResponseData(data);
                                        queueMessage(responseMsg);
                                    }
                                };
                            } else {
                                responseFunction = new CallBackFunction() {
                                    @Override
                                    public void onCallBack(String data) {
                                        // do nothing
                                    }
                                };
                            }
                            // BridgeHandler执行
                            BridgeHandler handler = null;
                            if (!TextUtils.isEmpty(m.getHandlerName())) {
                                handler = messageHandlers.get(m.getHandlerName());
                            }
                            // 如果没有找到注册的方法，那么使用defaultHandler处理
                            if (handler == null) {
                                handler = defaultHandler;
                            }
                            if (handler != null) {
                                handler.handler(m.getData(), responseFunction);
                            }
                        }
                    }
                }
            });
        }
    }
```

8. queueMessage
    - native方法执行结束后，执行结果包装成Message调用queueMessage
    - 进而调用js的_handleMessageFromNative

```java
    private void queueMessage(Message m) {
        if (startupMessage != null) {
            startupMessage.add(m);
        } else {
            dispatchMessage(m);
        }
    }

    void dispatchMessage(Message m) {
        String messageJson = m.toJson();
        //escape special characters for json string  为json字符串转义特殊字符
        messageJson = messageJson.replaceAll("(\\\\)([^utrn])", "\\\\\\\\$1$2");
        messageJson = messageJson.replaceAll("(?<=[^\\\\])(\")", "\\\\\"");
        final String javascriptCommand = String.format(BridgeUtil.JS_HANDLE_MESSAGE_FROM_JAVA, messageJson);
        // 必须要找主线程才会将数据传递出去 --- 划重点
        if (Thread.currentThread() == Looper.getMainLooper().getThread()) {
            mWebView.loadUrl(javascriptCommand);
        } else {
            mWebView.post(new Runnable() {
                @Override
                public void run() {
                    mWebView.loadUrl(javascriptCommand);
                }
            });
        }
    }
```

9. _handleMessageFromNative
    - 进而调用_dispatchMessageFromNativeInternal
    - 此时responseId不为空，并且等于3中生成的callbackId
    - 然后会回调2中调用callHandler时设置的callback，进而完成了调用native方法，获得natvie方法执行的结果整个过程

```js
    function _handleMessageFromNative(messageJSON) {
        _dispatchMessageFromNative(messageJSON);
    }

    function _dispatchMessageFromNativeInternal(messageJSON) {
        var message = JSON.parse(messageJSON);
        var responseCallback;
        //java call finished, now need to call js callback function
        if (message.responseId) {
            // js调用native,native回调会走这里
            responseCallback = responseCallbacks[message.responseId];
            if (!responseCallback) {
                return;
            }
            responseCallback(message.responseData);
            delete responseCallbacks[message.responseId];
        } else {
            //native 调用 js,native需要js的回调，也就是js方法以执行完有结果
            if (message.callbackId) {
                var callbackResponseId = message.callbackId;
                responseCallback = function (responseData) {
                    _doSend({
                        responseId: callbackResponseId,
                        responseData: responseData
                    });
                };
            }

            var handler = WebViewJavascriptBridge._defaultMessageHandler;
            if (message.handlerName) {
                handler = messageHandlers[message.handlerName];
            }
            //查找指定handler
            try {
                handler(message.data, responseCallback);
            } catch (exception) {
                if (typeof console !== 'undefined') {
                    console.log("WebViewJavascriptBridge: WARNING: javascript handler threw.", message, exception);
                }
            }
        }
    }
```

#### native调用Web端方法

- 原理同上面类似

### 触手native与js交互格式定义

- 无论函数参数还是函数返回，必须是json格式
- 函数参数只要求是json就可以
- 函数返回与服务器数据返回一样，包含code,message,和data，对data无限制，双方约定就可以

```java
// 正常执行
public static final int CODE_OK = 0;
// 发生错误
public static final int CODE_UNKNOWN_ERROR = -1;
// js调用native时，native不存在该方法
public static final int CODE_HANDLER_NOT_FOUND = -2;

public static class Result {
    public int code;
    public String message;
    public Object data;
}

mWebView.registerHandler("functionFromNative", (data, function) -> {
    KasLog.d(TAG, "js调用native方法:functionFromNative, 来自web的参数 = " + data);
    BaseChushouJS.Result result = new BaseChushouJS.Result();
    result.code = BaseChushouJS.CODE_OK;
    result.message = "";
    result.data = "functionFromNative方法执行完毕，返回数据来自java";
    if (function != null) {
        function.onCallBack(JsonUtils.toJson(result));
    }
});
```

```js
CODE_OK = 0;
CODE_UNKNOWN_ERROR = -1;
CODE_HANDLER_NOT_FOUND = -2;

window.connectWebViewJavascriptBridge(function (bridge) {
    // 注册一个方法供native调用
    bridge.registerHandler("functionInJS", function (params, responseCallback) {
        document.getElementById("params_from_native").innerHTML = params;
        if (responseCallback) {
            var resp = {
                code: CODE_OK,
                message: "",
                data: document.getElementById("text3").value
            };
            responseCallback(resp);
        }
    });
});
```

- 如何判断是否存在一个方法,原理：**注册一个默认的handler, 当方法不存在时，使用默认handler处理，通过返回数据的格式知道我们是否存在这个方法**

```java
 mBridge.setDefaultHandler((data, function) -> {
    Result result = new Result();
    result.code = CODE_HANDLER_NOT_FOUND;
    result.message = mContext.getString(R.string.basejs_handler_not_found);
    result.data = "";
    if (function != null) {
        function.onCallBack(toJson(result));
    }
});

// jsbridge 的flushMessageQueue方法
```

```js
window.connectWebViewJavascriptBridge(function (bridge) {
    // 注册默认的供native调用的方法
    // 当native调用一个js未注册的方法，会使用下面的函数处理
    bridge.setDefaultHandler(function (params, responseCallback) {
        console.log("js默认handler收到native的消息:" + params);
        var resp = {
            code: CODE_HANDLER_NOT_FOUND,
            message: "js不支持该函数"
        };
        if (responseCallback) {
            responseCallback(resp);
        }
    });
});

// WebViewJavascriptBridge.js的_dispatchMessageFromNativeInternal方法
```

### js注入前

- 如果js注入前，native调用了js,或者js调用了native会怎么样

#### native调用js

- native通过callHandler调用js，进而调用调用doSend,进而调用queueMessage
- 在js注入成功之前，startMessage不为空，会将调用的方法存入到startMessage中
- js注入成功后，会调用之前想要调用方法，并且清空startMessage

```java
    @Override
    public void callHandler(String handlerName, String data, CallBackFunction callBack) {
        doSend(handlerName, data, callBack);
    }

    /**
     * 保存message到消息队列
     *
     * @param handlerName      handlerName
     * @param data             data
     * @param responseCallback CallBackFunction
     */
    private void doSend(String handlerName, String data, CallBackFunction responseCallback) {
        Message m = new Message();
        if (!TextUtils.isEmpty(handlerName)) {
            m.setHandlerName(handlerName);
        }
        if (!TextUtils.isEmpty(data)) {
            m.setData(data);
        }
        if (responseCallback != null) {
            String callbackStr = String.format(BridgeUtil.CALLBACK_ID_FORMAT, ++uniqueId + (BridgeUtil.UNDERLINE_STR + SystemClock.currentThreadTimeMillis()));
            responseCallbacks.put(callbackStr, responseCallback);
            m.setCallbackId(callbackStr);
        }
        queueMessage(m);
    }

    private void queueMessage(Message m) {
        if (startupMessage != null) {
            startupMessage.add(m);
        } else {
            dispatchMessage(m);
        }
    }

    List<Message> getStartupMessage() {
        List<Message> list = startupMessage;
        startupMessage = null;
        return list;
    }

    // js注入成功后
    public void onPageFinished(WebView view, String url) {
        BridgeUtil.webViewLoadLocalJs(view, INJECT_JS);
        List<Message> list = mJsBridge.getStartupMessage();
        if (list != null) {
            for (Message m : list) {
                mJsBridge.dispatchMessage(m);
            }
        }
    }
```

#### js调用native

- 定义connectWebViewJavascriptBridge方法
- 如果js注入成功之前，会将想要调用的方法存放到window.WVJBCallbacks，否则直接js调用native
- native成功注入js后，如果window.WVJBCallbacks不为空，会调用先前想要调用的所有native方法

```js
window.connectWebViewJavascriptBridge = function (handler) {
        if (window.WebViewJavascriptBridge) {
            handler(window.WebViewJavascriptBridge);
            return
        }
        if (window.WVJBCallbacks) {
            window.WVJBCallbacks.push(handler);
            return
        }
        window.WVJBCallbacks = [handler];
    };

    setTimeout(function () {
        var callbacks = window.WVJBCallbacks;
        delete window.WVJBCallbacks;
        if (callbacks != null) {
            for (var i = 0; i < callbacks.length; i++) {
                callbacks[i](WebViewJavascriptBridge);
            }
        }
    }, 0);
```

#### js注入时机

- 本身功能与jsbridge无关，我们目前前端的cat.js代码

```js
// cat.js
var g = !1, h = "", i = navigator.userAgent.toUpperCase();
    /IPHONE|IPAD|IPOD/.test(i) && (a("_appVersion") > 6514 ? (window.connectWebViewJavascriptBridge = function (a) {
        if (window.WebViewJavascriptBridge) return a(WebViewJavascriptBridge);
        if (window.WVJBCallbacks) return window.WVJBCallbacks.push(a);
        window.WVJBCallbacks = [a];
        var b = document.createElement("iframe");
        b.style.display = "none", b.src = "wvjbscheme://__BRIDGE_LOADED__", document.documentElement.appendChild(b), setTimeout(function () {
            document.documentElement.removeChild(b)
        }, 0)
    }, d()) : (window.connectWebViewJavascriptBridge = function (a) {
        window.WebViewJavascriptBridge ? a(WebViewJavascriptBridge) : document.addEventListener("WebViewJavascriptBridgeReady", function () {
            a(WebViewJavascriptBridge)
        }, !1)
```

##### ios中的注入

- ios在首次调用connectWebViewJavascriptBridge后，会新建一个iframe,然后src设置为注入js的scheme，当ios的webview拦截到这个scheme时，会注入js代码

```java
window.connectWebViewJavascriptBridge = function (handler) {
        if (window.WebViewJavascriptBridge) {
            handler(window.WebViewJavascriptBridge);
            return
        }
        if (window.WVJBCallbacks) {
            window.WVJBCallbacks.push(handler);
            return
        }
        window.WVJBCallbacks = [handler];
        var b = document.createElement("iframe");
        b.style.display = "none";
        b.src = "wvjbscheme://__BRIDGE_LOADED__";
        document.documentElement.appendChild(b);
        setTimeout(function () {
            document.documentElement.removeChild(b)
        }, 0)
    };
```

#### android先择注入时机

- 如果webview注入时间过早，而js中的代码有操作html dom,js代码写有head之前，则可能出现错误
- android选择注入的时间为在onPageFinished
- 为保持与ios一致，所以我们在收到上面的scheme时，什么都不做

```java
    // 这一逻辑本身与jsbridge无关，所以我们仅仅写在CSWebViewClient中
    private static final String SCHEME_INJECT_JS = "wvjbscheme://__BRIDGE_LOADED__";

    @CallSuper
    @Override
    public boolean shouldOverrideUrlLoading(WebView view, String url) {
        if (!TextUtils.isEmpty(url) && url.startsWith(SCHEME_INJECT_JS)) {
            return true;
        }
        if (mInterceptor != null && mInterceptor.shouldOverrideUrlLoading(view, url)) {
            return true;
        }
        if (csShouldOverrideUrlLoading(view, url)) {
            return true;
        }
        return super.shouldOverrideUrlLoading(view, url);
    }

    @Override
    public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            String url = request.getUrl().toString();
            if (!TextUtils.isEmpty(url) && url.startsWith(SCHEME_INJECT_JS)) {
                return true;
            }
        }
        if (mInterceptor != null && mInterceptor.shouldOverrideUrlLoading(view, request)) {
            return true;
        }
        return super.shouldOverrideUrlLoading(view, request);
    }
```

### 接入方法

- gralde引入

```groovy
jsbridge = '1.0.2'
basejs = '1.0.1'

implementation "tv.chushou.widget:jsbridge:$rootProject.jsbridge" + "@aar"
implementation "tv.chushou.widget:basejs:$rootProject.basejs" + "@aar"
```

- 自定义WebviewClient,并重写以下3个方法

```java

public class CSWebViewClient extends WebViewClient {

    private static final String SCHEME_INJECT_JS = "wvjbscheme://__BRIDGE_LOADED__";
    private static final String TAG = "CSWebViewClient";
    private WebViewClientInterceptor mInterceptor;

    public CSWebViewClient() {
    }

    public void setJsBridge(JsBridge bridge) {
        if (bridge != null) {
            mInterceptor = new WebViewClientInterceptor(bridge);
        }
    }

    @CallSuper
    @Override
    public boolean shouldOverrideUrlLoading(WebView view, String url) {
         if (!TextUtils.isEmpty(url) && url.startsWith(SCHEME_INJECT_JS)) {
            return true;
        }
        if (mInterceptor != null && mInterceptor.shouldOverrideUrlLoading(view, url)) {
            return true;
        }
        return super.shouldOverrideUrlLoading(view, url);
    }

    @Override
    public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            String url = request.getUrl().toString();
            if (!TextUtils.isEmpty(url) && url.startsWith(SCHEME_INJECT_JS)) {
                return true;
            }
        }
        if (mInterceptor != null && mInterceptor.shouldOverrideUrlLoading(view, request)) {
            return true;
        }
        return super.shouldOverrideUrlLoading(view, request);
    }

    @Override
    public void onPageFinished(WebView view, String url) {
        if (mInterceptor != null) {
            mInterceptor.onPageFinished(view, url);
        }
        super.onPageFinished(view, url);
    }
}

```

- 创建jsbridge,设置webviewclient

```java
// 打开js
WebSettings ws = getSettings();
ws.setJavaScriptEnabled(true);

// 创建jsbridge
 mBridge = new JsBridge(this);

// 创建webviewclient
WebViewClient client = new CSWebViewClient();
client.setJsBridge(mBridge);
webview.setWebViewClient(client);
```

- **一定要记得**

```java
// 如果没有开启，会出各种神奇的问题
// 因为这个问题，我被坑了好几天！！！！！
webview.onResume();
webview.resumeTimers();
```

- 设置默认handler与默认handler供js调用

```java
 mBridge.setDefaultHandler((data, function) -> {
    Result result = new Result();
    result.code = CODE_HANDLER_NOT_FOUND;
    result.message = mContext.getString(R.string.basejs_handler_not_found);
    result.data = "";
    if (function != null) {
        function.onCallBack(toJson(result));
    }
});

mWebView.registerHandler("functionFromNative", (data, function) -> {
    KasLog.d(TAG, "js调用native方法:functionFromNative, 来自web的参数 = " + data);
    BaseChushouJS.Result result = new BaseChushouJS.Result();
    result.code = BaseChushouJS.CODE_OK;
    result.message = "";
    result.data = "functionFromNative方法执行完毕，返回数据来自java";
    if (function != null) {
        function.onCallBack(JsonUtils.toJson(result));
    }
});
```

- 调用js方法

```java
 Map<String, Object> map = new HashMap<>();
    map.put("param1", "参数1");
    map.put("param2", "参数2");
    map.put("_t", System.currentTimeMillis());
    String params = JsonUtils.toJson(map);
    KasLog.d(TAG, "调用js方法functionInJS， 参数:" + params);
    mBridge.callHandler("functionInJS", params, data -> {
        KasLog.d(TAG, "js执行完后，来自js的返回:" + data);
});
```

### 怎样与原生无缝切换

- 原理：我们只用写满足条件的方法(返回格式不限，但是参数要么为空，要么只有一个参数，并且这个参数是json格式)，然后利用java的反射特定，将方法注入到我们的jsbridge中去
- 注入的限制
    - 只会注入public方法
    - 只会注入自身定义的方法，不会注入其父类的方法
    - 函数要么参数为空，要么只有一个参数，并且参数是json string,使用json是为了后续可能的扩展的灵活性
    - 如果不希望某些函数注入js,那么应当在namesShouldNotInjected中返回这些函数名

```java
    public void inject() {
        if (mBridge == null) {
            return;
        }
        Class<?> c = getClass();
        Set<String> shouldNotInjected = namesShouldNotInjected();
        if (shouldNotInjected == null) {
            shouldNotInjected = new HashSet<>();
        }
        shouldNotInjected.add("namesShouldNotInjected");
        Method[] methods = c.getDeclaredMethods();
        for (Method m : methods) {
            int modifier = m.getModifiers();
            // 如果不是public方法，不要注入
            if (!Modifier.isPublic(modifier)) {
                continue;
            }
            final Method method = m;
            final String name = method.getName();
            // 如果是一些保留的方法不需要注入
            if (shouldNotInjected.contains(name)) {
                continue;
            }
            if (TextUtils.isEmpty(name) || name.contains("$")) {
                continue;
            }
            final Class<?> returntype = method.getReturnType();
            final Class<?>[] params = method.getParameterTypes();
            // 函数参数只支持为空，或者参数为json字符串
            if (params.length == 0 || (params.length == 1 && params[0] == String.class)) {
                mBridge.registerHandler(name, (s, callBackFunction) -> {
                    Result result = new Result();
                    try {
                        Object obj = null;
                        if (params.length == 0) {
                            if (Void.TYPE.equals(returntype)) {
                                method.invoke(BaseChushouJS.this);
                            } else {
                                obj = method.invoke(BaseChushouJS.this);
                            }
                        } else {
                            if (Void.TYPE.equals(returntype)) {
                                method.invoke(BaseChushouJS.this, s);
                            } else {
                                obj = method.invoke(BaseChushouJS.this, s);
                            }
                        }
                        result.code = CODE_OK;
                        result.message = "";
                        result.data = Void.TYPE.equals(returntype) ? null : obj;
                    } catch (Exception e) {
                        result.code = CODE_UNKNOWN_ERROR;
                        result.message = mContext.getString(R.string.basejs_handler_executed_exception);
                        result.data = null;
                    }
                    if (callBackFunction != null) {
                        callBackFunction.onCallBack(toJson(result));
                    }
                });
            }
        }
    }
```

### 注意事项

- 再次提醒一次，一定要记得

```java
webview.onResume();
webview.resumeTimers();
```

## 缓存

- [Android：手把手教你构建 全面的WebView 缓存机制 & 资源加载方案](https://www.jianshu.com/p/5e7075f4875f)
- [彻底弄懂HTTP缓存机制及原理](https://www.cnblogs.com/chenqf/p/6386163.html)

### 缓存原理

- 对于静态资源，比如js,png,jpeg，当加载成功一次后，我们缓存在本地，再次加次加载这个页面时，直接从本地读取，而不需要从网络请求，从而加快了页面的渲染速度
- 主要问题，在于缓存中的置换问题，怎么判断是不是更新了了？本地是否一直保存了？

### http 缓存相关的header

- [expires](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Expires)
- [Pragma](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Pragma)
- [Cache-Control](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Cache-Control)
- [Last-Modified](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Last-Modified)
- [ETag](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/ETag)

### 具体实现

- 目前项目中的webview缓存主要缓存静态资源,视频文件不缓存，**而对于html则不会缓存**

```java
public class CacheExtensionConfig {
    //全局默认的
    private static final HashSet<String> STATIC;
    private static final HashSet<String> NO_CACH;

    static {
        STATIC = new HashSet<>();
        STATIC.add("html");
        STATIC.add("htm");
        STATIC.add("js");
        STATIC.add("ico");
        STATIC.add("css");
        STATIC.add("png");
        STATIC.add("jpg");
        STATIC.add("jpeg");
        STATIC.add("gif");
        STATIC.add("bmp");
        STATIC.add("ttf");
        STATIC.add("woff");
        STATIC.add("woff2");
        STATIC.add("otf");
        STATIC.add("eot");
        STATIC.add("svg");
        STATIC.add("xml");
        STATIC.add("swf");
        STATIC.add("txt");
        STATIC.add("text");
        STATIC.add("conf");
        STATIC.add("webp");

        NO_CACH = new HashSet<>();
        NO_CACH.add("mp4");
        NO_CACH.add("mp3");
        NO_CACH.add("ogg");
        NO_CACH.add("avi");
        NO_CACH.add("wmv");
        NO_CACH.add("flv");
        NO_CACH.add("rmvb");
        NO_CACH.add("3gp");
    }
}
```

- 对于webview主要则是重写webviewclient的下面两个方法，如果返回null,则由webview本身决定其行为

```java
    @Nullable
    @Override
    public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
        return WebViewCacheInterceptorInst.getInstance().interceptRequest(request);
    }

    @Nullable
    @Override
    public WebResourceResponse shouldInterceptRequest(WebView view, String url) {
        return WebViewCacheInterceptorInst.getInstance().interceptRequest(url);
    }
```

- 现阶段缓存使用Okhttp自带的缓存实现

```java
// WebViewCacheInterceptor.java
private void initHttpClient(Builder builder) {
        File parent = mCacheFile.getParentFile();
        if (!parent.exists()) {
            //noinspection ResultOfMethodCallIgnored
            parent.mkdirs();
        }
        mCache = new Cache(mCacheFile, mCacheSize);
        OkHttpClient.Builder newBuilder;
        if (builder.mOkHttpClient != null) {
            newBuilder = builder.mOkHttpClient.newBuilder();
            List<Interceptor> list = newBuilder.interceptors();
            list.clear();
        } else {
            newBuilder = new OkHttpClient.Builder();
        }
        newBuilder.cache(mCache)
                .retryOnConnectionFailure(true)
                .connectTimeout(builder.mConnectTimeout, TimeUnit.SECONDS)
                .readTimeout(builder.mReadTimeout, TimeUnit.SECONDS)
                .addNetworkInterceptor(new HttpCacheInterceptor());
        if (mTrustAllHostname) {
            newBuilder.hostnameVerifier(new HostnameVerifier() {
                @SuppressLint("BadHostnameVerifier")
                @Override
                public boolean verify(String hostname, SSLSession session) {
                    return true;
                }
            });
        }
        if (mSSLSocketFactory != null && mX509TrustManager != null) {
            newBuilder.sslSocketFactory(mSSLSocketFactory, mX509TrustManager);
        }
        mHttpClient = newBuilder.build();
    }
```

- 缓存header主要包括request与response两个部分，其中request主要代码如下，其中html文件request头使用
 no-cache

```java
private WebResourceResponse interceptRequest(String url, Map<String, String> headers) {
        if (mCacheType == CacheType.NOCACHE) {
            return null;
        }
        // if url is empty
        if (TextUtils.isEmpty(url)) {
            return null;
        }
        // 不是http开头的
        if (!url.startsWith("http")) {
            return null;
        }
        // 如果是视频相关的不缓存
        if (mCacheExtensionConfig.isMedia(url)) {
            return null;
        }
        // 如果不是特定的静态文件
        if (!mCacheExtensionConfig.canCache(url)) {
            return null;
        }
        String extension = MimeTypeMapUtils.getFileExtensionFromUrl(url);
        if (TextUtils.isEmpty(extension)) {
            return null;
        }
        try {
            Request.Builder reqBuilder = new Request.Builder().url(url);
            addHeader(reqBuilder, headers);
            boolean isHtml = mCacheExtensionConfig.isHtml(url);
            if (isHtml) {
                reqBuilder.addHeader(HEADER_CACHE_STRAGETY, CacheType.NOCACHE.ordinal() + "");
                reqBuilder.removeHeader("pragma")
                        .removeHeader("Cache-Control")
                        .addHeader("Cache-Control", "no-cache");
            }
            Request request = reqBuilder.build();
            Response response = mHttpClient.newCall(request).execute();
            Response cacheRes = response.cacheResponse();
            if (cacheRes != null) {
                CacheWebViewLog.d(String.format("from cache: %s", url), mDebug);
            } else {
                CacheWebViewLog.d(String.format("from server: %s", url), mDebug);
            }
            String mimeType = MimeTypeMapUtils.getMimeTypeFromUrl(url);
            WebResourceResponse webResourceResponse = new WebResourceResponse(mimeType, "", response.body().byteStream());
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                webResourceResponse.setResponseHeaders(NetUtils.multimapToSingle(response.headers().toMultimap()));
            }
            return webResourceResponse;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
```

- 对于response部分，对于html强制设置为no-cahce不缓存。而对于其它静态资源，目前我们保证对于每一个资源变化了，其url都会变化，而缓存的key是由整个url生成的，所以我们可以强制更改其缓存头，加上max-age来进行缓存

```java
    public Response intercept(Chain chain) throws IOException {
        Request request = chain.request();
        Response originResponse = chain.proceed(request);
        Builder builder = originResponse.newBuilder();
        if (originResponse.code() != 200) {
            builder.removeHeader("pragma").removeHeader("Cache-Control").addHeader("Cache-Control", "no-cache");
        } else {
            String cacheStragety = request.header("WebResourceInterceptor-CaChe-Stragety");
            if (!TextUtils.isEmpty(cacheStragety) && cacheStragety.equals(CacheType.NOCACHE.ordinal() + "")) {
                builder.removeHeader("pragma").removeHeader("Cache-Control").addHeader("Cache-Control", "no-cache");
            } else {
                builder.removeHeader("pragma").removeHeader("Cache-Control").header("Cache-Control", "max-age=2592000");
            }
        }

        return builder.build();
    }
```

- OKhttp其内部的一些实现,这里要注意的是我们自定义的HttpCacheInterceptor设置的位置，addNetworkInterceptor?addInterceptor?

```java
// RealCall.java
@Override public Response execute() throws IOException {
    synchronized (this) {
      if (executed) throw new IllegalStateException("Already Executed");
      executed = true;
    }
    try {
      client.dispatcher().executed(this);
      Response result = getResponseWithInterceptorChain();
      if (result == null) throw new IOException("Canceled");
      return result;
    } finally {
      client.dispatcher().finished(this);
    }
  }

  private Response getResponseWithInterceptorChain() throws IOException {
    // Build a full stack of interceptors.
    List<Interceptor> interceptors = new ArrayList<>();
    interceptors.addAll(client.interceptors());
    interceptors.add(retryAndFollowUpInterceptor);
    interceptors.add(new BridgeInterceptor(client.cookieJar()));
    interceptors.add(new CacheInterceptor(client.internalCache()));
    interceptors.add(new ConnectInterceptor(client));
    if (!retryAndFollowUpInterceptor.isForWebSocket()) {
      interceptors.addAll(client.networkInterceptors());
    }
    interceptors.add(new CallServerInterceptor(
        retryAndFollowUpInterceptor.isForWebSocket()));

    Interceptor.Chain chain = new RealInterceptorChain(
        interceptors, null, null, null, 0, originalRequest);
    return chain.proceed(originalRequest);
  }
```

### 缓存接入方法

- marven引入

```groovy
cachewebviewlib = '1.0.0'

implementation "tv.chushou.widget:cachewebviewlib:$rootProject.cachewebviewlib" + "@aar"
```

- 初始化

```java
    public static void initCacheWebview(Context context) {
        WebViewCacheInterceptorInst instance = WebViewCacheInterceptorInst.getInstance();
        if (!instance.initialized()) {
            File f = new File(KasGlobalDef.WEB_CACHE_PATH);
            File parent = f.getParentFile();
            if (!parent.exists()) {
                //noinspection ResultOfMethodCallIgnored
                parent.mkdirs();
            }
            // 创建.nomedia file
            File nomediaFile = new File(KasGlobalDef.WEB_CACHE_PATH, ".nomedia");
            if (!nomediaFile.exists()) {
                try {
                    //noinspection ResultOfMethodCallIgnored
                    nomediaFile.createNewFile();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            WebViewCacheInterceptor.Builder builder = new WebViewCacheInterceptor.Builder(context.getApplicationContext())
                    .setCachePath(f)
                    .setCacheType(CacheType.FORCE)
                    .setCacheSize(KasGlobalDef.WEB_CACHE_SIZE)
                    .setConnectTimeoutSecond(MyHttpMgr.HTTP_TIME_OUT)
                    .setReadTimeoutSecond(MyHttpMgr.HTTP_TIME_OUT)
                    .setOkHttpClient(MyHttpMgr.Instance().mHttpClient)
                    .setDebug(KasLog.isLogEnalbed());
            instance.init(builder);
        }
    }
```

- 自定义webviewclient

```java
    // CSWebViewClient.java
    @CallSuper
    @Nullable
    @Override
    public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
        return WebViewCacheInterceptorInst.getInstance().interceptRequest(request);
    }

    @CallSuper
    @Nullable
    @Override
    public WebResourceResponse shouldInterceptRequest(WebView view, String url) {
        return WebViewCacheInterceptorInst.getInstance().interceptRequest(url);
    }
```

### 缓存注意事项

- 现阶段，我们是强制使用缓存，这样要保证，每换一个资源，我们必须保证其资源的url必须变化
- 但是对于第三方，比如游戏，我们不能保证第三方会这么做，而且即使这么做了，不同游戏也可能会出现相同url,所以对于游戏必须每一个游戏必须用一个缓存目录
- 注意游戏页面关闭时，我们需要关闭cache的DiskLruCache

```java
public class GameWebviewClient extends WebViewClient {
    private WebViewRequestInterceptor mCacheInterceptor;

    @Nullable
    @Override
    public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
        if (mCacheInterceptor != null) {
            return mCacheInterceptor.interceptRequest(request);
        }
        return null;
    }

    @Nullable
    @Override
    public WebResourceResponse shouldInterceptRequest(WebView view, String url) {
        if (mCacheInterceptor != null) {
            return mCacheInterceptor.interceptRequest(url);
        }
        return null;
    }

    void setWebviewCacheInterceptor(WebViewRequestInterceptor interceptor) {
        mCacheInterceptor = interceptor;
    }
}

```

```java

    public void loadGame(String gameId, String gameModel, String gameVersion, String csghStartGameUrl) {
        if (mWebView instanceof CacheWebview) {
            // 由于第三方的游戏不能保证它们的资源不会冲突
            // 所以对于一个游戏，一个版本都做一个单独的缓存
            String name = String.valueOf(gameId) + "_" + gameVersion;
            setWebviewCacheInterceptor(name);
        }
        mWebView.loadUrl(csghStartGameUrl);
        GameHotelConstants.GameTimeCount.TIME_START_LOADING_GAME = System.currentTimeMillis();
    }

    private void setWebviewCacheInterceptor(String name) {
        if (mWebviewClient == null) {
            return;
        }
        File cacheFile = new File(Environment.getExternalStorageDirectory(),
                GameHotelConstants.GAME_WEBVIEW_CACHE_NAME + name + File.separator);
        WebViewCacheInterceptor.Builder builder = new WebViewCacheInterceptor.Builder(Utils.mContext)
                .setCachePath(cacheFile)
                .setCacheType(CacheType.FORCE)
                .setCacheSize(GameHotelConstants.CACHE_SIZE)
                .setConnectTimeoutSecond(10)
                .setReadTimeoutSecond(10)
                .setOkHttpClient(GameHotelMgr.getInstance().getOkHttpClient())
                .setDebug(KasLog.isLogEnalbed());
        mCacheInterceptor = builder.build();
        mWebviewClient.setWebviewCacheInterceptor(mCacheInterceptor);
    }

    @Override
    public void destroy() {
        super.destroy();
        // 缓存不通用，关闭游戏，关闭缓存
        mCacheInterceptor.release();
    }
```

### 如何适配到x5Webview

- 我们的缓存实现，支持的是原生的Webview的WebResourceRequest，WebResourceResponse，对于x5的webview,我们只需要一个简单的适配者模式

```java
// WebResourceRequestAdapter.java
@TargetApi(Build.VERSION_CODES.LOLLIPOP)
public class WebResourceRequestAdapter implements WebResourceRequest {
    private com.tencent.smtt.export.external.interfaces.WebResourceRequest mWebResourceRequest;

    private WebResourceRequestAdapter(com.tencent.smtt.export.external.interfaces.WebResourceRequest x5Request) {
        mWebResourceRequest = x5Request;
    }

    public static WebResourceRequestAdapter adapter(com.tencent.smtt.export.external.interfaces.WebResourceRequest x5Request) {
        return new WebResourceRequestAdapter(x5Request);
    }

    @Override
    public Uri getUrl() {
        return mWebResourceRequest.getUrl();
    }

    @Override
    public boolean isForMainFrame() {
        return mWebResourceRequest.isForMainFrame();
    }

    @Override
    public boolean isRedirect() {
        return mWebResourceRequest.isRedirect();
    }

    @Override
    public boolean hasGesture() {
        return mWebResourceRequest.hasGesture();
    }

    @Override
    public String getMethod() {
        return mWebResourceRequest.getMethod();
    }

    @Override
    public Map<String, String> getRequestHeaders() {
        return mWebResourceRequest.getRequestHeaders();
    }
}
```

```java
// WebResourceResponseAdapter.java
public class WebResourceResponseAdapter extends WebResourceResponse {
    private android.webkit.WebResourceResponse mWebResourceResponse;

    private WebResourceResponseAdapter(android.webkit.WebResourceResponse webResourceResponse) {
        mWebResourceResponse = webResourceResponse;
    }

    public static WebResourceResponseAdapter adapter(android.webkit.WebResourceResponse webResourceResponse) {
        if (webResourceResponse == null) {
            return null;
        }
        return new WebResourceResponseAdapter(webResourceResponse);
    }

    @Override
    public String getMimeType() {
        return mWebResourceResponse.getMimeType();
    }

    @Override
    public InputStream getData() {
        return mWebResourceResponse.getData();
    }

    @TargetApi(Build.VERSION_CODES.LOLLIPOP)
    @Override
    public int getStatusCode() {
        return mWebResourceResponse.getStatusCode();
    }

    @TargetApi(Build.VERSION_CODES.LOLLIPOP)
    @Override
    public Map<String, String> getResponseHeaders() {
        return mWebResourceResponse.getResponseHeaders();
    }

    @Override
    public String getEncoding() {
        return mWebResourceResponse.getEncoding();
    }

    @TargetApi(Build.VERSION_CODES.LOLLIPOP)
    @Override
    public String getReasonPhrase() {
        return mWebResourceResponse.getReasonPhrase();
    }
}

```

```java
// X5GameWebviewClient.java
public class X5GameWebviewClient extends WebViewClient {
    private WebViewRequestInterceptor mCacheInterceptor;

    @Override
    public WebResourceResponse shouldInterceptRequest(WebView webView, String s) {
        if (mCacheInterceptor != null) {
            return WebResourceResponseAdapter.adapter(mCacheInterceptor.interceptRequest(s));
        }
        return super.shouldInterceptRequest(webView, s);
    }

    @Override
    public WebResourceResponse shouldInterceptRequest(WebView webView, WebResourceRequest webResourceRequest) {
        if (mCacheInterceptor != null) {
            return WebResourceResponseAdapter.adapter(mCacheInterceptor.interceptRequest(
                    WebResourceRequestAdapter.adapter(webResourceRequest)
            ));
        }
        return super.shouldInterceptRequest(webView, webResourceRequest);
    }

    @Override
    public WebResourceResponse shouldInterceptRequest(WebView webView, WebResourceRequest webResourceRequest, Bundle bundle) {
        if (mCacheInterceptor != null) {
            return WebResourceResponseAdapter.adapter(mCacheInterceptor.interceptRequest(
                    WebResourceRequestAdapter.adapter(webResourceRequest)
            ));
        }
        return super.shouldInterceptRequest(webView, webResourceRequest);
    }
}

```

### 预加载的实现

- 将我们web页面的一些常用资源加载到本地，比如jquery,cat.js等等
- 前端写一个页面，这个页面包含我们常用的一些资源，然后利用我们的CacheWebview加载这个链接

```java
// WebviewPreCacheTask.java
public class WebviewPreCacheTask {
    private static final String TAG = "WebviewPreCacheTask";

    private static final int DURATION = 60;
    private static final String DEFAULTURL = "https://kascdn.kascend.com/appcache.html";

    private Context mContext;
    private int mDuration;
    private String mUrl;
    private CSWebView mWebView;

    public WebviewPreCacheTask(Context context) {
        mContext = context.getApplicationContext();
        mDuration = DURATION;
        mUrl = DEFAULTURL;
    }

    public WebviewPreCacheTask(Context context, int duration, String url) {
        mContext = context.getApplicationContext();
        mDuration = duration;
        mUrl = url;
    }

    public void start() {
        if (mContext == null || Utils.isEmpty(mUrl)) {
            return;
        }
        if (mWebView == null) {
            mWebView = new CSWebView(mContext);
            CSWebView.initWebviewSetting(mWebView, mContext, new CSWebViewClient(), null);
        }
        mWebView.loadUrl(mUrl);
        RxExecutor.postDelayed(null, EventThread.MAIN_THREAD, mDuration, TimeUnit.SECONDS, () -> {
            if (mWebView == null) {
                return;
            }
            release();
        });
    }

    public void release() {
        if (mWebView != null) {
            mWebView.destroy();
            mWebView = null;
        }
        mContext = null;
        mUrl = null;
    }
}

```