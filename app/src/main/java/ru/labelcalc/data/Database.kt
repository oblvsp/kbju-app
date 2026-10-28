package ru.labelcalc.data

import android.content.Context
import androidx.room.Dao
import androidx.room.Database
import androidx.room.Embedded
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.Insert
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.Relation
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.Transaction
import kotlinx.coroutines.flow.Flow

@Entity(tableName = "dishes")
data class DishEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val name: String,
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(
    tableName = "dish_items",
    foreignKeys = [
        ForeignKey(
            entity = DishEntity::class,
            parentColumns = ["id"],
            childColumns = ["dishId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("dishId")]
)
data class DishItemEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val dishId: Long,
    val name: String,
    val grams: Double,
    val kcalPer100: Double,
    val proteinPer100: Double,
    val fatPer100: Double,
    val carbsPer100: Double
)

@Entity(tableName = "products")
data class ProductEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val name: String,
    val kcalPer100: Double,
    val proteinPer100: Double,
    val fatPer100: Double,
    val carbsPer100: Double
)

data class DishWithItems(
    @Embedded val dish: DishEntity,
    @Relation(parentColumn = "id", entityColumn = "dishId")
    val items: List<DishItemEntity>
)

data class DishTotalsRow(
    val grams: Double,
    val kcal: Double,
    val protein: Double,
    val fat: Double,
    val carbs: Double
)

@Entity(
    tableName = "diary_entries",
    foreignKeys = [
        ForeignKey(
            entity = ProductEntity::class,
            parentColumns = ["id"],
            childColumns = ["productId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("productId")]
)
data class DiaryEntryEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val productId: Long,
    val date: Long = System.currentTimeMillis()
)

@Dao
interface DishDao {

    @Query("SELECT * FROM dishes ORDER BY createdAt DESC")
    fun observeDishes(): Flow<List<DishEntity>>

    @Transaction
    @Query("SELECT * FROM dishes WHERE id = :dishId")
    fun observeDishWithItems(dishId: Long): Flow<DishWithItems?>

    @Query(
        """SELECT COALESCE(SUM(grams), 0.0) AS grams,
            COALESCE(SUM(kcalPer100 * grams / 100.0), 0.0) AS kcal,
            COALESCE(SUM(proteinPer100 * grams / 100.0), 0.0) AS protein,
            COALESCE(SUM(fatPer100 * grams / 100.0), 0.0) AS fat,
            COALESCE(SUM(carbsPer100 * grams / 100.0), 0.0) AS carbs
            FROM dish_items WHERE dishId = :dishId"""
    )
    fun observeTotals(dishId: Long): Flow<DishTotalsRow>

    @Insert
    suspend fun insertDish(dish: DishEntity): Long

    @Query("UPDATE dishes SET name = :name WHERE id = :id")
    suspend fun renameDish(id: Long, name: String)

    @Query("DELETE FROM dishes WHERE id = :id")
    suspend fun deleteDish(id: Long)

    @Insert
    suspend fun insertItem(item: DishItemEntity): Long

    @Query("DELETE FROM dish_items WHERE id = :id")
    suspend fun deleteItem(id: Long)
}

@Dao
interface DiaryDao {
    @Insert
    suspend fun insertEntry(entry: DiaryEntryEntity): Long

    @Query("SELECT * FROM diary_entries ORDER BY date DESC")
    fun observeEntries(): Flow<List<DiaryEntryEntity>>
}

@Dao
interface ProductDao {

    @Query("SELECT * FROM products ORDER BY name COLLATE NOCASE")
    fun observeProducts(): Flow<List<ProductEntity>>

    @Query("SELECT * FROM products WHERE name = :name LIMIT 1")
    suspend fun findByName(name: String): ProductEntity?

    @Insert
    suspend fun insert(product: ProductEntity): Long

    @Query("SELECT * FROM products WHERE id = :id LIMIT 1")
    suspend fun findById(id: Long): ProductEntity?

    @Query("DELETE FROM products WHERE id = :id")
    suspend fun delete(id: Long)
}

@Database(
    entities = [DishEntity::class, DishItemEntity::class, ProductEntity::class, DiaryEntryEntity::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {

    abstract fun dishDao(): DishDao
    abstract fun productDao(): ProductDao
    abstract fun diaryDao(): DiaryDao

    companion object {
        @Volatile
        private var instance: AppDatabase? = null

        fun get(context: Context): AppDatabase =
            instance ?: synchronized(this) {
                instance ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "labelcalc.db"
                ).build().also { instance = it }
            }
    }
}
