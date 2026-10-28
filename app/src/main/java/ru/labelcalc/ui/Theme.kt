package ru.labelcalc.ui

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = Color(0xFF2E7D32),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFB7F0C0),
    onPrimaryContainer = Color(0xFF00210A),
    secondary = Color(0xFF52634F),
    onSecondary = Color.White,
    background = Color(0xFFFBFDF7),
    onBackground = Color(0xFF191C19),
    surface = Color(0xFFFBFDF7),
    onSurface = Color(0xFF191C19)
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFF8BD494),
    onPrimary = Color(0xFF003913),
    primaryContainer = Color(0xFF1D5324),
    onPrimaryContainer = Color(0xFFA5F2AE),
    secondary = Color(0xFFB9CCB4),
    onSecondary = Color(0xFF243424),
    background = Color(0xFF191C19),
    onBackground = Color(0xFFE1E3DE),
    surface = Color(0xFF191C19),
    onSurface = Color(0xFFE1E3DE)
)

@Composable
fun CalcTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColors else LightColors,
        content = content
    )
}
