package ru.labelcalc.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.ExtendedFloatingActionButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
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
import ru.labelcalc.data.DishEntity
import ru.labelcalc.ui.ScreenBar
import java.text.DateFormat
import java.util.Date

@Composable
fun DishListScreen(db: AppDatabase, onOpenDish: (Long) -> Unit) {
    val scope = rememberCoroutineScope()
    val dishes by db.dishDao().observeDishes().collectAsState(initial = emptyList())
    var pendingDelete by remember { mutableStateOf<DishEntity?>(null) }

    Scaffold(
        topBar = { ScreenBar("Калорийность блюд") },
        floatingActionButton = {
            ExtendedFloatingActionButton(
                onClick = {
                    scope.launch {
                        val id = db.dishDao().insertDish(DishEntity(name = "Новое блюдо"))
                        onOpenDish(id)
                    }
                },
                icon = { Icon(Icons.Default.Add, contentDescription = null) },
                text = { Text("Новое блюдо") }
            )
        }
    ) { padding ->
        if (dishes.isEmpty()) {
            Box(
                Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(24.dp),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    "Нет блюд.\nНажмите «Новое блюдо», затем добавляйте продукты:\nсканируйте этикетку, выбирайте из справочника или вводите вручную.",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        } else {
            LazyColumn(
                Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                items(dishes, key = { it.id }) { dish ->
                    ListItem(
                        headlineContent = { Text(dish.name, maxLines = 1) },
                        supportingContent = {
                            Text(
                                DateFormat.getDateInstance(DateFormat.SHORT)
                                    .format(Date(dish.createdAt))
                            )
                        },
                        trailingContent = {
                            IconButton(onClick = { pendingDelete = dish }) {
                                Icon(Icons.Default.Delete, contentDescription = "Удалить")
                            }
                        },
                        modifier = Modifier.clickable { onOpenDish(dish.id) }
                    )
                    HorizontalDivider()
                }
            }
        }
    }

    pendingDelete?.let { dish ->
        AlertDialog(
            onDismissRequest = { pendingDelete = null },
            title = { Text("Удалить блюдо?") },
            text = { Text("«${dish.name}» и все его продукты будут удалены.") },
            confirmButton = {
                TextButton(onClick = {
                    scope.launch { db.dishDao().deleteDish(dish.id) }
                    pendingDelete = null
                }) { Text("Удалить") }
            },
            dismissButton = {
                TextButton(onClick = { pendingDelete = null }) { Text("Отмена") }
            }
        )
    }
}
