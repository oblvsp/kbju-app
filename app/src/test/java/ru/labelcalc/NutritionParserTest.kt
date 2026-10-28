package ru.labelcalc

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test
import ru.labelcalc.logic.NutritionParser

class NutritionParserTest {

    @Test
    fun fullLabel() {
        val text = """
            Творог обезжиренный
            Пищевая ценность на 100 г продукта:
            Белки, г — 16,5
            Жиры, г — 0,5
            Углеводы, г — 3,3
            Калорийность — 84 ккал
        """.trimIndent()
        val r = NutritionParser.parse(text)
        assertEquals("Творог обезжиренный", r.name)
        assertEquals(16.5, r.protein!!, 0.001)
        assertEquals(0.5, r.fat!!, 0.001)
        assertEquals(3.3, r.carbs!!, 0.001)
        assertEquals(84.0, r.kcal!!, 0.001)
    }

    @Test
    fun simpleTable() {
        val r = NutritionParser.parse("Молоко 3,2% Белки 2,9 Жиры 3,2 Углеводы 4,7")
        assertEquals("Молоко 3,2%", r.name)
        assertEquals(2.9, r.protein!!, 0.001)
        assertEquals(3.2, r.fat!!, 0.001)
        assertEquals(4.7, r.carbs!!, 0.001)
        assertNull(r.kcal)
    }

    @Test
    fun kjOnly() {
        val r = NutritionParser.parse("Энергетическая ценность 770 кДж")
        assertNull(r.name)
        assertNull(r.protein)
        assertNull(r.fat)
        assertNull(r.carbs)
        assertEquals(184.0, r.kcal!!, 1.0)
    }

    @Test
    fun slashFormat() {
        val r = NutritionParser.parse("Молоко 3,2%\nБ/Ж/У: 10/5/60")
        assertEquals("Молоко 3,2%", r.name)
        assertEquals(10.0, r.protein!!, 0.001)
        assertEquals(5.0, r.fat!!, 0.001)
        assertEquals(60.0, r.carbs!!, 0.001)
    }

    @Test
    fun bjuLetters() {
        val r = NutritionParser.parse("Творог 9%\nб 10 ж 5 у 60")
        assertEquals("Творог 9%", r.name)
        assertEquals(10.0, r.protein!!, 0.001)
        assertEquals(5.0, r.fat!!, 0.001)
        assertEquals(60.0, r.carbs!!, 0.001)
    }

    @Test
    fun ignoresHeader100g() {
        val r = NutritionParser.parse("Пищевая ценность в 100 г: белки 12,5 жиры 5,0 углеводы 60,0")
        assertNull(r.name)
        assertEquals(12.5, r.protein!!, 0.001)
        assertEquals(5.0, r.fat!!, 0.001)
        assertEquals(60.0, r.carbs!!, 0.001)
    }

    @Test
    fun latinLookalikes() {
        val r = NutritionParser.parse("Бeлки 12,5 Жиpы 5,0 Углеводы 60,0")
        assertEquals(12.5, r.protein!!, 0.001)
        assertEquals(5.0, r.fat!!, 0.001)
        assertEquals(60.0, r.carbs!!, 0.001)
    }

    @Test
    fun tableLayout() {
        val text = """
            Пищевая ценность в 100 г:
            Белки Жиры Углеводы
            12,5 5,0 60,0
        """.trimIndent()
        val r = NutritionParser.parse(text)
        assertEquals(12.5, r.protein!!, 0.001)
        assertEquals(5.0, r.fat!!, 0.001)
        assertEquals(60.0, r.carbs!!, 0.001)
    }
}
