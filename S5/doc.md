# S5 Faculty Service - Справочник отделений СПО

## Сущность: Department (Отделение)

### 1. Информация для создания сущности

| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|-----------|----------------|-----|-------------|----------------------|
| name | Название отделения | Да | string | 2-200 символов | — |
| code | Шифр направления подготовки | Да | string | 2-20 символов | — |
| head_name | ФИО заведующего отделением | Да | string | 2-150 символов | — |
| head_specialty | Специальность заведующего | Нет | string | 2-200 символов | null |
| head_phone | Телефон заведующего | Нет | string | до 20 символов | null |
| head_email | Email заведующего | Нет | string | 2-255 символов | null |
| head_cabinet_id | Номер кабинета заведующего | Нет | integer | целое число | null |
| reception_is_active | Активен ли приём | Нет | boolean | true/false | false |
| reception_schedule | Время приёма заведующего | Нет | string | до 500 символов | null |

**Уникальные комбинации параметров:** (name, code)

### 2. Информация, возвращаемая при успешном создании

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| code | string |
| head_name | string |
| head_specialty | string (null) |
| head_phone | string (null) |
| head_email | string (null) |
| head_cabinet_id | integer (null) |
| reception_is_active | boolean |
| reception_schedule | string (null) |
| created_at | datetime |
| is_active | boolean |

## Изменить сущность по ID

### 3. Параметры запроса

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| id | Уникальный идентификатор отделения | Да | integer | положительное число |

### 4. Информация для изменения сущности

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| name | Название отделения | Нет | string | 2-200 символов |
| code | Шифр направления подготовки | Нет | string | 2-20 символов |
| head_name | ФИО заведующего отделением | Нет | string | 2-150 символов |
| head_specialty | Специальность заведующего | Нет | string | 2-200 символов |
| head_phone | Телефон заведующего | Нет | string | до 20 символов |
| head_email | Email заведующего | Нет | string | 2-255 символов |
| head_cabinet_id | Номер кабинета заведующего | Нет | integer | целое число |
| reception_is_active | Активен ли приём | Нет | boolean | true/false |
| reception_schedule | Время приёма заведующего | Нет | string | до 500 символов |

### 5. Информация, возвращаемая при успешном изменении

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| code | string |
| head_name | string |
| head_specialty | string (null) |
| head_phone | string (null) |
| head_email | string (null) |
| head_cabinet_id | integer (null) |
| reception_is_active | boolean |
| reception_schedule | string (null) |
| created_at | datetime |
| is_active | boolean |

## Удалить сущность по ID

Удаление реализовано как **мягкое удаление** (soft delete): запись не удаляется физически из БД, а устанавливается флаг `is_active = False`.

**Параметры запроса:**

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| id | Уникальный идентификатор отделения | Да | integer | положительное число |

**Возвращаемое значение:** `{"deleted": true}` или `{"deleted": false}`

## Получить сущность по ID

### 6. Параметры запроса

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| id | Уникальный идентификатор отделения | Да | integer | положительное число |

### 7. Информация, возвращаемая при успешном поиске

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| id | Уникальный номер отделения | integer |
| name | Название отделения | string |
| code | Шифр направления подготовки | string |
| head_name | ФИО заведующего отделением | string |
| head_specialty | Специальность заведующего | string (null) |
| head_phone | Телефон заведующего | string (null) |
| head_email | Email заведующего | string (null) |
| head_cabinet_id | Номер кабинета заведующего | integer (null) |
| reception_is_active | Активен ли приём | boolean |
| reception_schedule | Время приёма заведующего | string (null) |
| created_at | Дата и время создания записи | datetime |
| is_active | Активна ли запись | boolean |

## Получить список сущностей по заданным параметрам

### 8. Параметры для получения списка

| Параметр | Пояснение | Тип | Ограничение |
|----------|-----------|-----|-------------|
| page | Номер страницы | integer | ≥ 1 |
| size | Количество записей на странице | integer | 1-100 |
| name | Поиск по части названия отделения | string | частичное совпадение |

### 9. Информация, возвращаемая в виде списка сущностей

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| code | string |
| head_name | string |
| head_specialty | string (null) |
| head_phone | string (null) |
| head_email | string (null) |
| head_cabinet_id | integer (null) |
| reception_is_active | boolean |
| reception_schedule | string (null) |
| created_at | datetime |
| is_active | boolean |

## ER-диаграмма

![ER-диаграмма](./erd.png)