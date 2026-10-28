package ru.labelcalc.ui.screens

import android.Manifest
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.compose.LocalLifecycleOwner
import ru.labelcalc.logic.NutritionParser
import ru.labelcalc.ui.ProductPrefill
import ru.labelcalc.ui.ScreenBar
import kotlin.math.roundToInt

/**
 * Экран «Сканирование этикетки».
 *
 * OCR-модуль (Tesseract) удалён из сборки ради лёгкого APK. Вместо снимка с распознаванием
 * экран предлагает вставить текст этикетки — NutritionParser разберёт его и заполнит карточку
 * продукта через колбэк [onRecognized].
 */
@Composable
fun ScanScreen(
    dishId: Long,
    onBack: () -> Unit,
    onRecognized: (ProductPrefill) -> Unit
) {
    var cameraGranted by remember { mutableStateOf(false) }
    var labelDraft by remember { mutableStateOf("") }
    var status by remember { mutableStateOf<String?>(null) }

    val requestPermission = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        cameraGranted = granted
        if (!granted) status = "Нет доступа к камере — можно вставить текст этикетки вручную."
    }

    fun applyParsed(result: NutritionParser.Result) {
        if (result.protein == null && result.fat == null && result.carbs == null && result.kcal == null) {
            status = "Не удалось распознать БЖУ. Проверьте текст или заполните карточку вручную."
            return
        }
        val rounded = result.copy(
            kcal = result.kcal?.let { it.roundToInt().toDouble() }
        )
        onRecognized(
            ProductPrefill(
                name = rounded.name,
                protein = rounded.protein,
                fat = rounded.fat,
                carbs = rounded.carbs,
                kcal = rounded.kcal
            )
        )
    }

    Scaffold(topBar = { ScreenBar("Сканирование этикетки", onBack) }) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
        ) {
            OutlinedTextField(
                value = labelDraft,
                onValueChange = { labelDraft = it },
                label = { Text("Текст этикетки") },
                placeholder = { Text("Белки 16,5 · Жиры 0,5 · Углеводы 3,3 · 84 ккал") },
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f, fill = false),
                maxLines = 10,
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done)
            )
            Spacer(Modifier.height(8.dp))
            Button(onClick = { applyParsed(NutritionParser.parse(labelDraft)) }) {
                Text("Распознать")
            }
            Spacer(Modifier.height(12.dp))
            status?.let {
                Text(
                    it,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(
                            MaterialTheme.colorScheme.surfaceVariant,
                            RoundedCornerShape(8.dp)
                        )
                        .padding(12.dp)
                )
                Spacer(Modifier.height(12.dp))
            }
            if (!cameraGranted) {
                OutlinedButton(onClick = { requestPermission.launch(Manifest.permission.CAMERA) }) {
                    Text("Включить камеру")
                }
            } else {
                CameraPreview(Modifier
                    .fillMaxWidth()
                    .height(220.dp))
                Spacer(Modifier.height(8.dp))
                Text(
                    "Распознавание по фото отключено (OCR удалён из сборки). Используйте текстовый ввод выше.",
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

@Composable
private fun CameraPreview(modifier: Modifier = Modifier) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val previewView = remember { PreviewView(context) }
    val providerFuture = remember { ProcessCameraProvider.getInstance(context) }
    LaunchedEffect(Unit) {
        val provider = providerFuture.await()
        val preview = Preview.Builder().build().also {
            it.setSurfaceProvider(previewView.surfaceProvider)
        }
        provider.unbindAll()
        provider.bindToLifecycle(
            lifecycleOwner,
            CameraSelector.DEFAULT_BACK_CAMERA,
            preview
        )
    }
    DisposableEffect(providerFuture) {
        onDispose { providerFuture.get().unbindAll() }
    }
    AndroidView(factory = { previewView }, modifier = modifier)
}
