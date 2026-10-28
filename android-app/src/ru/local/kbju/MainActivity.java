package ru.local.kbju;

import android.app.Activity;
import android.app.WallpaperColors;
import android.app.WallpaperManager;
import android.content.res.Configuration;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Locale;

public class MainActivity extends Activity {

    private WebView web;
    private static final long MAX_DOWNLOAD = 20L * 1024 * 1024;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web = new WebView(this);
        WebSettings st = web.getSettings();
        st.setJavaScriptEnabled(true);
        st.setDomStorageEnabled(true);
        st.setAllowFileAccess(true);
        web.setWebViewClient(new WebViewClient());
        web.addJavascriptInterface(new Bridge(), "AppBridge");
        loadApp();
        setContentView(web);
    }

    private File updateFile() {
        return new File(getFilesDir(), "update" + File.separator + "index.html");
    }

    private void loadApp() {
        File f = updateFile();
        String url = f.exists() ? Uri.fromFile(f).toString() : "file:///android_asset/index.html";
        web.loadUrl(url);
    }

    private boolean systemDark() {
        Configuration cfg = getResources().getSystem().getConfiguration();
        return (cfg.uiMode & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES;
    }

    private class Bridge {

        @JavascriptInterface
        public String getTheme() {
            JSONObject o = new JSONObject();
            try {
                o.put("dark", systemDark());
                if (Build.VERSION.SDK_INT >= 27) {
                    WallpaperManager wm = WallpaperManager.getInstance(MainActivity.this);
                    WallpaperColors wc = wm.getWallpaperColors(WallpaperManager.FLAG_SYSTEM);
                    if (wc != null) {
                        int c = wc.getPrimaryColor().toArgb();
                        o.put("color", String.format(Locale.US, "#%06X", 0xFFFFFF & c));
                    }
                }
            } catch (Exception e) {}
            return o.toString();
        }

        @JavascriptInterface
        public String setStatusBar(final String arg) {
            runOnUiThread(new Runnable() {
                public void run() {
                    try {
                        JSONObject o = new JSONObject(arg);
                        getWindow().setStatusBarColor(Color.parseColor(o.optString("color", "#FEF7FF")));
                        if (Build.VERSION.SDK_INT >= 23) {
                            View d = getWindow().getDecorView();
                            int flags = d.getSystemUiVisibility();
                            if (o.optBoolean("iconsLight", true)) {
                                flags |= View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
                            } else {
                                flags &= ~View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
                            }
                            d.setSystemUiVisibility(flags);
                        }
                    } catch (Exception e) {}
                }
            });
            return "OK";
        }

        @JavascriptInterface
        public String httpGet(String url) throws JSONException {
            JSONObject o = new JSONObject();
            try {
                HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
                c.setConnectTimeout(15000);
                c.setReadTimeout(20000);
                c.setInstanceFollowRedirects(true);
                int code = c.getResponseCode();
                if (code != 200) {
                    c.disconnect();
                    o.put("ok", false);
                    o.put("error", "HTTP " + code);
                    return o.toString();
                }
                InputStream in = c.getInputStream();
                ByteArrayOutputStream buf = new ByteArrayOutputStream();
                byte[] b = new byte[8192];
                long total = 0;
                int n;
                while ((n = in.read(b)) != -1) {
                    total += n;
                    if (total > MAX_DOWNLOAD) {
                        in.close();
                        throw new IOException("файл больше 20 МБ");
                    }
                    buf.write(b, 0, n);
                }
                in.close();
                o.put("ok", true);
                o.put("body", new String(buf.toByteArray(), StandardCharsets.UTF_8));
            } catch (Exception e) {
                o.put("ok", false);
                o.put("error", e.getMessage() == null ? "ошибка сети" : e.getMessage());
            }
            return o.toString();
        }

        @JavascriptInterface
        public String saveUpdate(String html) throws JSONException {
            JSONObject o = new JSONObject();
            try {
                File dir = new File(getFilesDir(), "update");
                if (!dir.exists()) dir.mkdirs();
                File tmp = new File(dir, "index.tmp");
                FileOutputStream fos = new FileOutputStream(tmp);
                fos.write(html.getBytes(StandardCharsets.UTF_8));
                fos.close();
                File dst = updateFile();
                if (dst.exists()) dst.delete();
                if (!tmp.renameTo(dst)) throw new IOException("не удалось заменить файл");
                o.put("ok", true);
            } catch (Exception e) {
                o.put("ok", false);
                o.put("error", e.getMessage() == null ? "ошибка записи" : e.getMessage());
            }
            return o.toString();
        }

        @JavascriptInterface
        public boolean updateExists() {
            return updateFile().exists();
        }

        @JavascriptInterface
        public boolean removeUpdate() {
            File f = updateFile();
            return !f.exists() || f.delete();
        }

        @JavascriptInterface
        public String restart() {
            runOnUiThread(new Runnable() {
                public void run() {
                    loadApp();
                }
            });
            return "OK";
        }
    }
}
