package ru.labelcalc

import android.app.Application
import ru.labelcalc.data.AppDatabase

class CalcApp : Application() {
    val database: AppDatabase by lazy { AppDatabase.get(this) }
}
