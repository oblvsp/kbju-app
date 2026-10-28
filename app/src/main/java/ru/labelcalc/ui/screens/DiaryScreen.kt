package ru.labelcalc.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material3.*
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.runtime.*
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import java.text.SimpleDateFormat
import java.util.*
import kotlinx.coroutines.flow.collectLatest
import ru.labelcalc.data.AppDatabase
import ru.labelcalc.data.DiaryEntryEntity
import ru.labelcalc.data.ProductEntity

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DiaryScreen(db: AppDatabase) {
    val entries by db.diaryDao().observeEntries().collectAsState(initial = emptyList())
    val products by db.productDao().observeProducts().collectAsState(initial = emptyList())
    val productMap = remember { mutableStateOf<Map<Long, ProductEntity>>(emptyMap()) }
    LaunchedEffect(entries, products) {
        productMap.value = products.associateBy { it.id }
    }

    // Group entries by day (midnight epoch)
    val grouped = remember(entries) {
        entries.groupBy { it.date / (24 * 60 * 60 * 1000) }
            .toSortedMap(compareByDescending { it })
    }
    val dateFormat = remember { SimpleDateFormat("dd.MM.yyyy – EEEE", Locale("ru")) }
    val dayState = remember { mutableStateMapOf<Long, Boolean>() }
    LazyColumn(modifier = Modifier.fillMaxSize()) {
        grouped.forEach { (dayKey, dayEntries) ->
            val dayDate = Date(dayKey * 24 * 60 * 60 * 1000)
            val header = dateFormat.format(dayDate)
            val isExpanded = dayState[dayKey] ?: true
            item {
                ListItem(
                    headlineContent = { Text(header) },
                    trailingContent = {
                        IconButton(onClick = {
                            dayState[dayKey] = !isExpanded
                        }) {
                            Icon(
                                imageVector = if (isExpanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                                contentDescription = if (isExpanded) "Свернуть" else "Развернуть"
                            )
                        }
                    },
                    modifier = Modifier.fillMaxWidth()
                )
            }
            if (isExpanded) {
                items(dayEntries, key = { it.id }) { entry ->
                    val product = productMap.value[entry.productId]
                    ListItem(
                        headlineContent = { Text(product?.name ?: "—") },
                        modifier = Modifier.clickable { /* possible future action */ }
                    )
                    HorizontalDivider()
                }
            }
        }
    }
}
