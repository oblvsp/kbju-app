package ru.labelcalc.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import ru.labelcalc.data.AppDatabase
import ru.labelcalc.data.DishItemEntity
import ru.labelcalc.data.ProductEntity
import ru.labelcalc.logic.CalorieMath
import ru.labelcalc.ui.ProductPrefill
import ru.labelcalc.ui.ScreenBar

private fun parseNum(s: String): Double? =
    s.replace(',', '.').trim().toDoubleOrNull()?.takeIf { it >= 0.0 }

@Composable
fun ProductScreen(
    db: AppDatabase,
    dishId: Long,
    prefill: ProductPrefill,
    onBack: () -> Unit,
    onDone: () -> Unit
) {
    val scope = rememberCoroutineScope()
    var name by remember { mutableStateOf(prefill.name ?: "") }
    var grams by remember { mutableStateOf("100") }
    var protein by remember { mutableStateOf(prefill.protein?.let(CalorieMath::format) ?: "") }
    var fat by remember { mutableStateOf(prefill.fat?.let(CalorieMath::format) ?: "") }
    var carbs by remember { mutableStateOf(prefill.carbs?.let(CalorieMath::format) ?: "") }
    var kcal by remember { mutableStateOf(prefill.kcal?.let(CalorieMath::format) ?: "") }
    var error by remember { mutableStateOf<String?>(null) }

    val p = parseNum(protein)
    val f = parseNum(fat)
    val c = parseNum(carbs)
    val k = parseNum(kcal)
    val suggestKcal = CalorieMath.kcalPer100(p ?: 0.0, f ?: 0.0, c ?: 0.0)

    fun save() {
        val g = parseNum(grams)
        if (g == null || g <= 0.0) {
            error = "Укажите вес порции в граммах"
            return
        }
        val pv = parseNum(protein) ?: 0.0
        val fv = parseNum(fat) ?: 0.0
        val cv = parseNum(carbs) ?: 0.0
        val kv = parseNum(kcal)
        val kcalPer100 = kv?.takeIf { it > 0.0 } ?: CalorieMath.kcalPer100(pv, fv, cv)
        val finalName = name.trim().ifBlank { "Продукт" }
        scope.launch {
            db.dishDao().insertItem(
                DishItemEntity(
                    dishId = dishId,
                    name = finalName,
                    grams = g,
                    kcalPer100 = kcalPer100,
                    proteinPer100 = pv,
                    fatPer100 = fv,
                    carbsPer100 = cv
                )
            )
            if (pv > 0 || fv > 0 || cv > 0 || kcalPer100 > 0) {
                if (db.productDao().findByName(finalName) == null) {
                    db.productDao().insert(
                        ProductEntity(
                            name = finalName,
                            kcalPer100 = kcalPer100,
                            proteinPer100 = pv,
                            fatPer100 = fv,
                            carbsPer100 = cv
                        )
                    )
                }
            }
            onDone()
        }
    }

    Scaffold(topBar = { ScreenBar("Продукт", onBack) }) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
                .imePadding()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            OutlinedTextField(
                value = name,
                onValueChange = { name = it },
                label = { Text("Название") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
            OutlinedTextField(
                value = grams,
                onValueChange = { grams = it },
                label = { Text("Вес порции, г") },
                singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                modifier = Modifier.fillMaxWidth()
            )
            Text("На 100 г продукта", style = MaterialTheme.typography.titleSmall)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(
                    value = protein,
                    onValueChange = { protein = it },
                    label = { Text("Б, г") },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    modifier = Modifier.weight(1f)
                )
                OutlinedTextField(
                    value = fat,
                    onValueChange = { fat = it },
                    label = { Text("Ж, г") },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    modifier = Modifier.weight(1f)
                )
                OutlinedTextField(
                    value = carbs,
                    onValueChange = { carbs = it },
                    label = { Text("У, г") },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    modifier = Modifier.weight(1f)
                )
            }
            OutlinedTextField(
                value = kcal,
                onValueChange = { kcal = it },
                label = { Text("Калорийность, ккал (если указана)") },
                singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                modifier = Modifier.fillMaxWidth()
            )
            if (k == null && ((p ?: 0.0) > 0 || (f ?: 0.0) > 0 || (c ?: 0.0) > 0)) {
                Text(
                    "Расчёт по БЖУ: ≈ ${CalorieMath.format(suggestKcal)} ккал на 100 г",
                    style = MaterialTheme.typography.bodySmall
                )
            }
            error?.let {
                Text(it, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall)
            }
            Button(onClick = { save() }, modifier = Modifier.fillMaxWidth()) {
                Text("Добавить в блюдо")
            }
        }
    }
}
