package ru.labelcalc.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import ru.labelcalc.data.AppDatabase
import ru.labelcalc.data.ProductEntity
import ru.labelcalc.logic.CalorieMath
import ru.labelcalc.ui.ScreenBar

@Composable
fun PickProductScreen(
    db: AppDatabase,
    onBack: () -> Unit,
    onPicked: (ProductEntity) -> Unit
) {
    val products by db.productDao().observeProducts().collectAsState(initial = emptyList())
    var query by remember { mutableStateOf("") }
    val q = query.trim().lowercase()
    val filtered = products.filter { q.isBlank() || it.name.lowercase().contains(q) }

    Scaffold(topBar = { ScreenBar("Справочник продуктов", onBack) }) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                label = { Text("Поиск") },
                singleLine = true,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            )
            if (filtered.isEmpty()) {
                Box(
                    Modifier
                        .fillMaxSize()
                        .padding(24.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        "Нет сохранённых продуктов.\nОтсканируйте этикетку — продукт сохранится в справочник.",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            } else {
                LazyColumn(Modifier.fillMaxSize()) {
                    items(filtered, key = { it.id }) { product ->
                        ListItem(
                            headlineContent = { Text(product.name, maxLines = 1) },
                            supportingContent = {
                                Text(
                                    "Б ${CalorieMath.format(product.proteinPer100)} · " +
                                        "Ж ${CalorieMath.format(product.fatPer100)} · " +
                                        "У ${CalorieMath.format(product.carbsPer100)} · " +
                                        "${CalorieMath.format(product.kcalPer100)} ккал"
                                )
                            },
                            modifier = Modifier.clickable { onPicked(product) }
                        )
                        HorizontalDivider()
                    }
                }
            }
        }
    }
}
