package ru.labelcalc.logic

import java.util.Locale
import kotlin.math.roundToInt

object CalorieMath {

    const val KCAL_PER_PROTEIN = 4.0
    const val KCAL_PER_CARB = 4.0
    const val KCAL_PER_FAT = 9.0

    fun kcalPer100(
        proteinPer100: Double,
        fatPer100: Double,
        carbsPer100: Double,
        declaredKcal: Double? = null
    ): Double {
        if (declaredKcal != null && declaredKcal > 0.0) return declaredKcal
        return proteinPer100 * KCAL_PER_PROTEIN +
            carbsPer100 * KCAL_PER_CARB +
            fatPer100 * KCAL_PER_FAT
    }

    fun scale(per100: Double, grams: Double): Double = per100 * grams / 100.0

    fun format(value: Double): String {
        val rounded = (value * 10).roundToInt() / 10.0
        return if (rounded == rounded.toLong().toDouble()) {
            rounded.toLong().toString()
        } else {
            String.format(Locale.US, "%.1f", rounded)
        }
    }
}
