package ru.labelcalc

import org.junit.Assert.assertEquals
import org.junit.Test
import ru.labelcalc.logic.CalorieMath

class CalorieMathTest {

    @Test
    fun declaredKcalWins() {
        assertEquals(380.0, CalorieMath.kcalPer100(12.5, 5.0, 60.0, 380.0), 0.001)
    }

    @Test
    fun computedFromMacros() {
        assertEquals(335.0, CalorieMath.kcalPer100(12.5, 5.0, 60.0), 0.001)
    }

    @Test
    fun zeroDeclaredFallsBackToMacros() {
        assertEquals(335.0, CalorieMath.kcalPer100(12.5, 5.0, 60.0, 0.0), 0.001)
    }

    @Test
    fun scaleToGrams() {
        assertEquals(837.5, CalorieMath.scale(335.0, 250.0), 0.001)
    }

    @Test
    fun formatValues() {
        assertEquals("335", CalorieMath.format(335.0))
        assertEquals("837.5", CalorieMath.format(837.5))
        assertEquals("33.4", CalorieMath.format(33.36))
    }
}
