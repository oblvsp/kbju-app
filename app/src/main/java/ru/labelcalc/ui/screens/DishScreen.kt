package ru.labelcalc.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.ElevatedCard
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import ru.labelcalc.data.AppDatabase
import ru.labelcalc.data.DishTotalsRow
import ru.labelcalc.logic.CalorieMath
import ru.labelcalc.ui.ScreenBar

@Composable
fun DishScreen(
    db: AppDatabase,
    dishId: Long,
    onBack: () -> Unit,
    onScan: () -> Unit,
    onPick: () -> Unit,
    onAddManually: () -> Unit
) {
    val scope = rememberCoroutineScope()
    val dishWithItems by db.dishDao().observeDishWithItems(dishId)
        .collectAsState(initial = null)
    val totals by db.dishDao().observeTotals(dishId)
        .collectAsState(initial = DishTotalsRow(0.0, 0.0, 0.0, 0.0, 0.0))
    var showRename by remember { mutableStateOf(false) }
    var showDelete by remember { mutableStateOf(false) }
    val dish = dishWithItems?.dish
    val dishItems = dishWithItems?.items ?: emptyList()

    Scaffold(
        topBar = {
            ScreenBar(
                title = dish?.name ?: "Блюдо",
                onBack = onBack,
                actions = {
                    IconButton(onClick = { showRename = true }) {
                        Icon(Icons.Default.Edit, contentDescription = "Переименовать")
                    }
                    IconButton(onClick = { showDelete = true }) {
                        Icon(Icons.Default.Delete, contentDescription = "Удалить блюдо")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            ElevatedCard(
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            ) {
                Column(Modifier.padding(16.dp)) {
                    Row(
                        Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Итого", style = MaterialTheme.typography.titleMedium)
                        Text(
                            "${CalorieMath.format(totals.kcal)} ккал",
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                    Text(
                        "Вес: ${CalorieMath.format(totals.grams)} г · " +
                            "Б ${CalorieMath.format(totals.protein)} · " +
                            "Ж ${CalorieMath.format(totals.fat)} · " +
                            "У ${CalorieMath.format(totals.carbs)}",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }

            Row(
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilledTonalButton(onClick = onScan, modifier = Modifier.weight(1f)) {
                    Text("Сканировать")
                }
                FilledTonalButton(onClick = onPick, modifier = Modifier.weight(1f)) {
                    Text("Справочник")
                }
                FilledTonalButton(onClick = onAddManually, modifier = Modifier.weight(1f)) {
                    Text("Вручную")
                }
            }

            if (dishItems.isEmpty()) {
                Box(
                    Modifier
                        .weight(1f)
                        .fillMaxWidth(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        "Добавьте продукты:\nотсканируйте этикетку,\nвыберите из справочника или введите вручную.",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            } else {
                LazyColumn(
                    Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .padding(top = 8.dp)
                ) {
                    items(dishItems, key = { it.id }) { item ->
                        ListItem(
                            headlineContent = { Text(item.name, maxLines = 1) },
                            supportingContent = {
                                Text(
                                    "${CalorieMath.format(item.grams)} г · " +
                                        "${CalorieMath.format(CalorieMath.scale(item.kcalPer100, item.grams))} ккал · " +
                                        "Б ${CalorieMath.format(CalorieMath.scale(item.proteinPer100, item.grams))} · " +
                                        "Ж ${CalorieMath.format(CalorieMath.scale(item.fatPer100, item.grams))} · " +
                                        "У ${CalorieMath.format(CalorieMath.scale(item.carbsPer100, item.grams))}"
                                )
                            },
                            trailingContent = {
                                IconButton(onClick = {
                                    scope.launch { db.dishDao().deleteItem(item.id) }
                                }) {
                                    Icon(Icons.Default.Delete, contentDescription = "Удалить")
                                }
                            }
                        )
                        HorizontalDivider()
                    }
                }
            }
        }
    }

    if (showRename) {
        var text by remember { mutableStateOf(dish?.name ?: "") }
        AlertDialog(
            onDismissRequest = { showRename = false },
            title = { Text("Название блюда") },
            text = {
                OutlinedTextField(
                    value = text,
                    onValueChange = { text = it },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )
            },
            confirmButton = {
                TextButton(onClick = {
                    scope.launch {
                        db.dishDao().renameDish(dishId, text.trim().ifBlank { "Блюдо" })
                    }
                    showRename = false
                }) { Text("Сохранить") }
            },
            dismissButton = {
                TextButton(onClick = { showRename = false }) { Text("Отмена") }
            }
        )
    }

    if (showDelete) {
        AlertDialog(
            onDismissRequest = { showDelete = false },
            title = { Text("Удалить блюдо?") },
            text = { Text("«${dish?.name ?: "Блюдо"}» и все его продукты будут удалены.") },
            confirmButton = {
                TextButton(onClick = {
                    showDelete = false
                    scope.launch {
                        db.dishDao().deleteDish(dishId)
                        onBack()
                    }
                }) { Text("Удалить") }
            },
            dismissButton = {
                TextButton(onClick = { showDelete = false }) { Text("Отмена") }
            }
        )
    }
}
