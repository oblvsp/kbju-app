package ru.labelcalc.ui.screens

import android.Manifest
import android.content.pm.PackageManager
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
34 | import androidx.compose.ui.Alignment
35 | import androidx.compose.ui.Modifier
36 | import androidx.compose.ui.platform.LocalContext
37 | import androidx.compose.ui.unit.dp
38 | import androidx.compose.ui.viewinterop.AndroidView
39 | import androidx.core.content.ContextCompat
40 | import androidx.lifecycle.compose.LocalLifecycleOwner
41 | import kotlinx.coroutines.launch
import androidx.compose.ui.graphics.Color
42 | // OCR utilities removed – no image processing in this build.
import ru.labelcalc.ui.ScreenBar
import java.io.File

@Composable
fun ScanScreen(
    dishId: Long,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var hasPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) ==
                PackageManager.PERMISSION_GRANTED
        )
    }
    var imageCapture by remember { mutableStateOf<ImageCapture?>(null) }
    var status by remember { mutableStateOf<String?>(null) }
    var busy by remember { mutableStateOf(false) }

    val requestPermission = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        hasPermission = granted
        if (!granted) status = "Нет доступа к камере.\nРазрешите камеру в настройках."
    }

    LaunchedEffect(Unit) {
        if (!hasPermission) requestPermission.launch(Manifest.permission.CAMERA)
    }

    fun process(uri: Uri) {
        if (busy) return
        busy = true
        status = "Распознавание…"
        // OCR removed – the screen now simply acknowledges the capture.
        scope.launch {
            status = "OCR removed – no processing performed."
            busy = false
        }
    }

    Scaffold(topBar = { ScreenBar("Сканирование этикетки", onBack) }) { padding ->
        Box(
            Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            if (hasPermission) {
                CameraPreview(Modifier.fillMaxSize()) { imageCapture = it }
                if (busy) {
                    Box(
                        Modifier
                            .fillMaxSize()
                            .background(Color.Black.copy(alpha = 0.5f)),
                        contentAlignment = Alignment.Center
                    ) { CircularProgressIndicator() }
                } else {
                    Button(
                        onClick = {
                            val capture = imageCapture ?: return@Button
                            val file = File(context.cacheDir, "scan_${System.currentTimeMillis()}.jpg")
                            val opts = ImageCapture.OutputFileOptions.Builder(file).build()
                            capture.takePicture(
                                opts,
                                ContextCompat.getMainExecutor(context),
                                object : ImageCapture.OnImageSavedCallback {
                                    override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                                        process(Uri.fromFile(file))
                                    }

                                    override fun onError(exception: ImageCaptureException) {
                                        status = "Ошибка камеры: ${exception.message}"
                                    }
                                }
                            )
                        },
                        modifier = Modifier
                            .align(Alignment.BottomCenter)
                            .padding(32.dp)
                    ) { Text("Сделать снимок") }
                }
                status?.let {
                    Text(
                        it,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier
                            .align(Alignment.TopCenter)
                            .padding(16.dp)
                            .background(
                                MaterialTheme.colorScheme.surface,
                                RoundedCornerShape(8.dp)
                            )
                            .padding(12.dp)
                    )
                }
            } else {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(status ?: "Требуется доступ к камере")
                        Spacer(Modifier.height(12.dp))
                        Button(onClick = { requestPermission.launch(Manifest.permission.CAMERA) }) {
                            Text("Разрешить")
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun CameraPreview(modifier: Modifier = Modifier, onReady: (ImageCapture) -> Unit) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val previewView = remember {
        PreviewView(context).apply { scaleType = PreviewView.ScaleType.FILL_CENTER }
    }
    val imageCapture = remember {
        ImageCapture.Builder()
            .setCaptureMode(ImageCapture.CAPTURE_MODE_MAXIMIZE_QUALITY)
            .build()
    }

    AndroidView(factory = { previewView }, modifier = modifier)

    LaunchedEffect(previewView) {
        val providerFuture = ProcessCameraProvider.getInstance(context)
        providerFuture.addListener({
            try {
                val provider = providerFuture.get()
                val preview = Preview.Builder().build().also {
                    it.setSurfaceProvider(previewView.surfaceProvider)
                }
                provider.unbindAll()
                provider.bindToLifecycle(
                    lifecycleOwner,
                    CameraSelector.DEFAULT_BACK_CAMERA,
                    preview,
                    imageCapture
                )
                onReady(imageCapture)
            } catch (_: Exception) {
            }
        }, ContextCompat.getMainExecutor(context))
    }
}
