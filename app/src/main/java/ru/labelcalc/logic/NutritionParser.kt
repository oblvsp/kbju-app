package ru.labelcalc.logic

import kotlin.math.roundToInt

/**
 * Эвристический парсер текстов этикеток (наследник OCR-модуля).
 *
 * Понимает форматы:
 *  - «Белки, г — 16,5 / Жиры, г — 0,5 / Углеводы, г — 3,3»;
 *  - «Б/Ж/У: 10/5/60» и «б 10 ж 5 у 60»;
 *  - табличный макет: строка заголовков «Белки Жиры Углеводы», ниже — числа;
 *  - кДж («Энергетическая ценность 770 кДж») с пересчётом в ккал (/4.184);
 *  - запятую и точку как десятичный разделитель;
 *  - латинские двойники кириллицы (e→е, p→р, c→с, o→о, a→а, x→х, y→у, k→к, m→м, T→Т, H→Н).
 */
object NutritionParser {

    data class Result(
        val name: String?,
        val protein: Double?,
        val fat: Double?,
        val carbs: Double?,
        val kcal: Double?
    )

    private const val KJ_PER_KCAL = 4.184

    private val LATIN_LOOKALIKES = mapOf(
        'e' to 'е', 'E' to 'Е', 'p' to 'р', 'o' to 'о', 'c' to 'с', 'a' to 'а',
        'x' to 'х', 'y' to 'у', 'k' to 'к', 'm' to 'м', 'T' to 'Т', 'H' to 'Н'
    )

    private fun normalize(s: String): String =
        s.map { LATIN_LOOKALIKES[it] ?: it }.joinToString("")
            .replace('\u00A0', ' ')
            .replace('−', '-')

    private const val NUM_SRC = """\d+(?:[.,]\d+)?"""

    // Числовой блок: запятая и точка оба принимаются как десятичный разделитель.
    private val NUM_RE = Regex(NUM_SRC)

    // Ключевые слова Б/Ж/У (значение ищется отдельно — см. valueAfter).
    private val KEY_PROTEIN = Regex("(?:белк[а-яё]*|протеин)", RegexOption.IGNORE_CASE)
    private val KEY_FAT = Regex("(?:жир[а-яё]*|липид)", RegexOption.IGNORE_CASE)
    private val KEY_CARBS = Regex("углевод[а-яё]*", RegexOption.IGNORE_CASE)

    // «84 ккал» / «Калорийность — 84» / «Кал: 350» (без суффикса кДж).
    private val KCAL_RE = Regex(
        "([0-9][0-9.,]*)\\s*ккал|" +
            "(?:кал[а-яё]{2,10})[^0-9]{0,20}([0-9][0-9.,]*)(?!\\s*(?:кдж|kj))|" +
            "(?:^|[^а-яёa-z])кал\\s*[:\\-–—]?\\s*([0-9][0-9.,]*)(?!\\s*(?:кдж|kj))",
        RegexOption.IGNORE_CASE
    )

    // Строки, которые никогда не являются названием продукта.
    private val NON_NAME_RE = Regex(
        "ценност|100\\s*г|ккал|кдж|\\bkcal\\b|\\bkj\\b",
        RegexOption.IGNORE_CASE
    )
    // «Энергетическая ценность 770 кДж» — только с эксплицитным суффиксом кДж.
    private val KJ_RE = Regex(
        "([0-9][0-9.,]*)\\s*(?:кдж|kj)|" +
            "(?:энергетическ[а-яё]+\\s+ценност[ьыя])[^0-9]{0,20}([0-9][0-9.,]*)\\s*(?:кдж|kj)",
        RegexOption.IGNORE_CASE
    )
    private val SLASH_RE = Regex(
        "б\\s*/\\s*ж\\s*/\\s*у\\s*[:\\-–—]?\\s*($NUM_SRC)\\s*[/,]\\s*($NUM_SRC)\\s*[/,]\\s*($NUM_SRC)",
        RegexOption.IGNORE_CASE
    )
    private val SHORT_RE = Regex(
        "(?:^|[\\s,;:])(?:б|b)[:\\-–—]?\\s*($NUM_SRC)[\\s,;]+(?:ж|f)[:\\-–—]?\\s*($NUM_SRC)" +
            "[\\s,;]+(?:у|u)[:\\-–—]?\\s*($NUM_SRC)"
    )

    private val HEADER_P_RE = Regex("^белк[а-яё]*$", RegexOption.IGNORE_CASE)
    private val HEADER_F_RE = Regex("^жир[а-яё]*$", RegexOption.IGNORE_CASE)
    private val HEADER_C_RE = Regex("^углевод[а-яё]*$", RegexOption.IGNORE_CASE)
    private val ONLY_NUMS_RE = Regex("^(?:$NUM_SRC)(?:\\s+$NUM_SRC){1,}$")

    // Пересчёт кДж → ккал с округлением до 0.1 (как в CalorieMath.format).
    private fun roundKjToKcal(kj: Double): Double =
        (kj / KJ_PER_KCAL * 10.0).roundToInt() / 10.0

    private fun num(raw: String?): Double? =
        raw?.replace(',', '.')?.toDoubleOrNull()?.takeIf { it >= 0.0 && it < 100_000.0 }

    // Первое число в той же строке, что и ключевое слово («Белки, г — 16,5», «белки 12,5»).
    // Если перед словом стоит % (жирность «Молоко 3,2%»), берётся ближайшее число ПОСЛЕ слова.
    private fun valueAfterLine(line: String, keyword: Regex): Double? {
        val km = keyword.find(line) ?: return null
        val numbers = NUM_RE.findAll(line).map { it.range to it.value }.toList()
            .filter { it.first.first > km.range.last }
        if (numbers.isEmpty()) return null
        val (range, token) = numbers.first()
        val after = range.last + 1
        if (after < line.length && line[after] == '%') return null
        return num(token)
    }

    private fun firstGroup(text: String, re: Regex): Double? =
        re.find(text)?.groupValues?.let { g ->
            (1..3).mapNotNull { i -> g.getOrNull(i)?.takeIf { it.isNotEmpty() }?.let(::num) }
                .firstOrNull()
        }

    fun parse(rawText: String): Result {
        val text = normalize(rawText)
        val lines = text.lines().map { it.trim() }.filter { it.isNotEmpty() }

        // Кандидат в название отсекаем от строк с ключевыми словами БЖУ/энергетической ценности,
        // иначе «Молоко 3,2% Белки …» потеряет имя, а «Пищевая ценность…» станет названием.
        val nameLines = lines.filter { !NON_NAME_RE.containsMatchIn(it) }

        var protein: Double? = null
        var fat: Double? = null
        var carbs: Double? = null
        for (line in lines) {
            if (protein == null) protein = valueAfterLine(line, KEY_PROTEIN)
            if (fat == null) fat = valueAfterLine(line, KEY_FAT)
            if (carbs == null) carbs = valueAfterLine(line, KEY_CARBS)
        }

        if (protein == null || fat == null || carbs == null) {
            SLASH_RE.find(text)?.let { m ->
                protein = protein ?: num(m.groupValues[1])
                fat = fat ?: num(m.groupValues[2])
                carbs = carbs ?: num(m.groupValues[3])
            }
        }
        if (protein == null || fat == null || carbs == null) {
            SHORT_RE.find(text)?.let { m ->
                protein = protein ?: num(m.groupValues[1])
                fat = fat ?: num(m.groupValues[2])
                carbs = carbs ?: num(m.groupValues[3])
            }
        }

        // Табличный макет: строка заголовков «Белки Жиры Углеводы», ниже — строка из ≥2 чисел.
        if (protein == null || fat == null || carbs == null) {
            for (i in lines.indices) {
                val words = lines[i].split(Regex("\\s+"))
                val firstNumberWord = words.indexOfFirst { w -> w.matches(Regex("^[0-9]")) }
                val limit = if (firstNumberWord >= 0) firstNumberWord else words.size
                val idxP = words.indexOfFirst { limit > 0 && it.matches(HEADER_P_RE) }
                    .takeIf { it in 0 until limit } ?: -1
                val idxF = words.indexOfFirst { it.matches(HEADER_F_RE) }
                    .takeIf { it in 0 until limit } ?: -1
                val idxC = words.indexOfFirst { it.matches(HEADER_C_RE) }
                    .takeIf { it in 0 until limit } ?: -1
                if (idxP < 0 || idxF < 0 || idxC < 0) continue
                val numbersLine = lines.asSequence().drop(i + 1).firstOrNull {
                    it.matches(ONLY_NUMS_RE)
                } ?: continue
                val nums = NUM_RE.findAll(numbersLine).mapNotNull { num(it.value) }.toList()
                if (nums.size < 2) continue
                protein = protein ?: nums.getOrNull(idxP)
                fat = fat ?: nums.getOrNull(idxF)
                carbs = carbs ?: nums.getOrNull(idxC)
                break
            }
        }

        var kcal = firstGroup(text, KCAL_RE)
        if (kcal == null) {
            val kj = firstGroup(text, KJ_RE)
            if (kj != null) kcal = roundKjToKcal(kj)
        }

        return Result(guessName(nameLines), protein, fat, carbs, kcal)
    }

    private fun guessName(lines: List<String>): String? {
        var fallback: String? = null
        for (line in lines) {
            // Строка с макронутриентами — название целиком не подходит, но в однострочной
            // этикетке («Молоко 3,2% Белки …») имя продукта стоит префиксом до ключевого слова.
            // Ключевое слово ищем как отдельное слово (\b), иначе «обезжиренный» дало бы ложный префикс.
            val macroMatch = findMacroWord(line)
            if (macroMatch != null) {
                val prefix = line.substring(0, macroMatch.range.first).trim().trimEnd(':', ',', '-', '–', '—').trim()
                if (prefix.length in 2..80 && !NON_NAME_RE.containsMatchIn(prefix)) return prefix
                continue
            }
            // Строка только из чисел — значения таблицы, не название.
            if (ONLY_NUMS_RE.matches(line)) continue
            // Первый чистый текст — кандидат, но если позже найдётся префикс с именем — он точнее.
            if (fallback == null && line.length in 2..80) fallback = line.trim()
        }
        return fallback
    }

    // Первое вхождение БЖУ-термина именно как отдельного слова.
    private fun findMacroWord(line: String): MatchResult? {
        val candidates = listOf(KEY_PROTEIN, KEY_FAT, KEY_CARBS).mapNotNull { it.find(line) }
            .filter { m -> isStandaloneWord(line, m.range) }
        return candidates.minByOrNull { it.range.first }
    }

    private fun isStandaloneWord(line: String, range: IntRange): Boolean {
        val before = range.first - 1
        val after = range.last + 1
        val okBefore = before < 0 || !line[before].isLetterOrDigit()
        val okAfter = after >= line.length || !line[after].isLetterOrDigit()
        return okBefore && okAfter
    }

    /** Форматирует результат для предпросмотра («Б 16.5 · Ж 0.5 · У 3.3 · 84 ккал»). */
    fun formatSummary(r: Result): String {
        val parts = buildList {
            r.protein?.let { add("Б ${CalorieMath.format(it)}") }
            r.fat?.let { add("Ж ${CalorieMath.format(it)}") }
            r.carbs?.let { add("У ${CalorieMath.format(it)}") }
            r.kcal?.let { add("${CalorieMath.format(it)} ккал") }
        }
        return if (parts.isEmpty()) "—" else parts.joinToString(" · ")
    }
}
