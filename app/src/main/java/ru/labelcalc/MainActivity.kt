package ru.labelcalc

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.Scaffold
import androidx.compose.material3.BottomNavigation
import androidx.compose.material3.BottomNavigationItem
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.ui.Modifier
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.CalendarToday
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import ru.labelcalc.data.AppDatabase
import ru.labelcalc.ui.CalcTheme
import ru.labelcalc.ui.ProductPrefill
import ru.labelcalc.ui.Routes
import ru.labelcalc.ui.ScanCache
import ru.labelcalc.ui.screens.DishListScreen
import ru.labelcalc.ui.screens.DishScreen
import ru.labelcalc.ui.screens.PickProductScreen
import ru.labelcalc.ui.screens.ProductScreen
import ru.labelcalc.ui.screens.ScanScreen
import ru.labelcalc.ui.screens.DiaryScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val db = (application as CalcApp).database
        setContent {
            CalcTheme {
                val nav = rememberNavController()
                val items = listOf(
                    Triple(Routes.DISHES, "Блюда", Icons.Default.List),
                    Triple(Routes.DIARY, "Дневник", Icons.Default.CalendarToday)
                )
                Scaffold(
                    bottomBar = {
                        BottomNavigation {
                            val current = nav.currentBackStackEntry?.destination?.route
                            items.forEach { (route, label, icon) ->
                                BottomNavigationItem(
                                    icon = { Icon(icon, contentDescription = null) },
                                    label = { Text(label) },
                                    selected = current == route,
                                    onClick = {
                                        if (current != route) {
                                            nav.navigate(route) {
                                                popUpTo(nav.graph.startDestinationId) { inclusive = true }
                                                launchSingleTop = true
                                            }
                                        }
                                    }
                                )
                            }
                        }
                    }
                ) { paddingValues ->
                    NavHost(
                        navController = nav,
                        startDestination = Routes.DISHES,
                        modifier = Modifier.padding(paddingValues)
                    ) {
                        composable(Routes.DISHES) {
                            DishListScreen(
                                db = db,
                                onOpenDish = { nav.navigate(Routes.dish(it)) }
                            )
                        }
                        composable(Routes.DISH_PATTERN) { entry ->
                            val dishId = entry.arguments?.getString("dishId")?.toLongOrNull()
                                ?: return@composable
                            DishScreen(
                                db = db,
                                dishId = dishId,
                                onBack = { nav.popBackStack() },
                                onScan = { nav.navigate(Routes.scan(dishId)) },
                                onPick = { nav.navigate(Routes.pick(dishId)) },
                                onAddManually = {
                                    ScanCache.rawText = ""
                                    nav.navigate(Routes.product(dishId, ProductPrefill()))
                                }
                            )
                        }
                        composable(Routes.SCAN_PATTERN) { entry ->
                            val dishId = entry.arguments?.getString("dishId")?.toLongOrNull()
                                ?: return@composable
                            ScanScreen(
                                dishId = dishId,
                                onBack = { nav.popBackStack() },
                                onRecognized = { prefill ->
                                    nav.navigate(Routes.product(dishId, prefill)) {
                                        popUpTo(Routes.DISH_PATTERN)
                                    }
                                }
                            )
                        }
                        composable(Routes.PICK_PATTERN) { entry ->
                            val dishId = entry.arguments?.getString("dishId")?.toLongOrNull()
                                ?: return@composable
                            PickProductScreen(
                                db = db,
                                onBack = { nav.popBackStack() },
                                onPicked = { product ->
                                    ScanCache.rawText = ""
                                    nav.navigate(
                                        Routes.product(
                                            dishId,
                                            ProductPrefill(
                                                name = product.name,
                                                protein = product.proteinPer100,
                                                fat = product.fatPer100,
                                                carbs = product.carbsPer100,
                                                kcal = product.kcalPer100.takeIf { it > 0.0 }
                                            )
                                        )
                                    )
                                }
                            )
                        }
                        composable(Routes.PRODUCT_PATTERN) { entry ->
                            val dishId = entry.arguments?.getString("dishId")?.toLongOrNull()
                                ?: return@composable
                            val prefill = ProductPrefill.fromArgs(
                                name = entry.arguments?.getString("name"),
                                p = entry.arguments?.getString("p"),
                                f = entry.arguments?.getString("f"),
                                c = entry.arguments?.getString("c"),
                                k = entry.arguments?.getString("k")
                            )
                            ProductScreen(
                                db = db,
                                dishId = dishId,
                                prefill = prefill,
                                onBack = { nav.popBackStack() },
                                onDone = { nav.popBackStack() }
                            )
                        }
                        composable(Routes.DIARY) {
                            // DiaryScreen will be added later
                            ru.labelcalc.ui.screens.DiaryScreen(db = db)
                        }
                    }
                }
            }
        }
    }
}
