package ru.labelcalc.ui

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.text.style.TextOverflow
import java.net.URLEncoder

object Routes {
    const val DISHES = "dishes"
    const val DISH_PATTERN = "dish/{dishId}"
    const val SCAN_PATTERN = "scan/{dishId}"
    const val PICK_PATTERN = "pick/{dishId}"
    const val PRODUCT_PATTERN = "product/{dishId}?name={name}&p={p}&f={f}&c={c}&k={k}"
    const val DIARY = "diary"

    fun dish(dishId: Long) = "dish/$dishId"
    fun scan(dishId: Long) = "scan/$dishId"
    fun pick(dishId: Long) = "pick/$dishId"

    fun product(dishId: Long, prefill: ProductPrefill): String {
        val name = URLEncoder.encode(prefill.name ?: "", "UTF-8").replace("+", "%20")
        return "product/$dishId" +
            "?name=$name" +
            "&p=${numArg(prefill.protein)}" +
            "&f=${numArg(prefill.fat)}" +
            "&c=${numArg(prefill.carbs)}" +
            "&k=${numArg(prefill.kcal)}"
    }

    private fun numArg(value: Double?): String = value?.toString() ?: ProductPrefill.MISSING
}

data class ProductPrefill(
    val name: String? = null,
    val protein: Double? = null,
    val fat: Double? = null,
    val carbs: Double? = null,
    val kcal: Double? = null
) {
    companion object {
        const val MISSING = "-1"

        fun fromArgs(name: String?, p: String?, f: String?, c: String?, k: String?): ProductPrefill =
            ProductPrefill(
                name = name?.takeIf { it.isNotBlank() },
                protein = p.argToDouble(),
                fat = f.argToDouble(),
                carbs = c.argToDouble(),
                kcal = k.argToDouble()
            )

        private fun String?.argToDouble(): Double? =
            this?.toDoubleOrNull()?.takeIf { it >= 0.0 }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ScreenBar(
    title: String,
    onBack: (() -> Unit)? = null,
    actions: @Composable () -> Unit = {}
) {
    TopAppBar(
        title = { Text(title, maxLines = 1, overflow = TextOverflow.Ellipsis) },
        navigationIcon = {
            if (onBack != null) {
                IconButton(onClick = onBack) {
                    Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Назад")
                }
            }
        },
        actions = { actions() }
    )
}
