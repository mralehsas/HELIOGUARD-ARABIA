# ملاحظات دمج Android WebView

- ضع محتويات المجلد داخل:
  `app/src/main/assets/`
- حمّل:
  `file:///android_asset/index.html`
- أضف صلاحية الإنترنت:
  `<uses-permission android:name="android.permission.INTERNET" />`
- فعّل JavaScript وDOM Storage:
  - `webView.getSettings().setJavaScriptEnabled(true);`
  - `webView.getSettings().setDomStorageEnabled(true);`
- يفضّل تفعيل:
  - `setAllowFileAccess(true)`
  - `setAllowContentAccess(true)`
- لا تستخدم Mixed Content؛ جميع الروابط HTTPS.
- اختبر CORS داخل WebView. إذا حجب مزود خارجي أصل `file://`، نضيف لاحقًا طبقة Proxy موثوقة أو WebViewAssetLoader.
- شاشة كاملة مناسبة لجهاز Infinix Note 40 Pro.


## v1.0 — CCMC and DONKI Gateway
- اختبر طلب `kauai.ccmc.gsfc.nasa.gov` داخل WebView.
- إن ظهر حظر CORS مع أصل `file://`، استخدم `WebViewAssetLoader` بنطاق HTTPS محلي أو طبقة proxy موثوقة.
- لا تعطل التحقق من TLS.
- أضف النطاق إلى Network Security Config فقط عند الحاجة وبـ HTTPS.
