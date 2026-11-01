package ai.autofix.alto800

import android.app.Activity
import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient

/**
 * AutoFix AI Android Companion Activity
 * Connects to the AutoFix AI SaaS Dashboard & local Bluetooth ELM327 v1.5 bridge
 */
class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.webViewClient = WebViewClient()
        // Loads local or cloud AutoFix AI SaaS endpoint
        webView.loadUrl("http://10.0.2.2:8080")
        setContentView(webView)
    }
}
