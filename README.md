# Предсказание популярности текстов в социальных сетях.
Я хочу научиться с помощью машинного обучения предсказывать количество лайков, которые получит текстовый пост в социальной сети vk.com. 

## В данный момент

### Обучающая и тестовая выборка
+ 17 групп
+ около 7000  постов
+ тестирование на всей обучающей выборке (кросс-валидация по 5 фолдам)

### Предобработка
+ удаление тегов и ссылок

### Признаки 

#### Нетекстовые:
+ тип поста (post - свой пост, copy - репост)
+ помечен ли пост как реклама
+ количество приложенных фото, видео, аудио, ссылок. 

#### Текстовые:
+ длина поста в словах
+ матрица tf-idf (без стоп-слов)

## Нужно сделать

### Обучающая и тестовая выборка
- [ ] дополнительная тестовая выборка

### Предобработка
- [ ] лемматизация (?)

### Признаки 

#### Текстовые:
- [ ] полярность 
- [ ] количество нецензурных слов