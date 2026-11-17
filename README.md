# TextMoodBot

Учебный Telegram-бот для классификации англоязычных сообщений. Он принимает текст и возвращает оценку модели для депрессивного содержания сообщения.

## Как работает бот

1. Telegram-бот на aiogram принимает сообщение.
2. Код приводит текст к нижнему регистру, очищает его и преобразует в идентификаторы токенов с помощью BERT-токенизатора.
3. Модель TensorFlow/Keras с `Embedding` и `Conv1D` обрабатывает блоки по 10 токенов. Код агрегирует оценки блоков и возвращает число по шкале от 0 до 100.

Бот рассчитан на английские сообщения. Текущая предобработка удаляет кириллицу.

## Структура проекта

```text
text-mood-bot/
├── final_model/
├── .gitignore
├── config.py
├── depression_dataset_reddit_cleaned.csv
├── engine.py
├── main.py
├── README.md
├── text_messages.py
└── tokenizer
```

`config.py` — локальная конфигурация. `.venv` и `__pycache__` создаются при установке и запуске.

## Обучение модели

Код подготовки данных, эксперименты и обучение находятся в ноутбуке [KTEup.ipynb в Google Colab](https://colab.research.google.com/drive/1yShquluW1XOGeERn_K8pVDDIcp4B0tV8).

1. В ноутбуке загружаются размеченные тексты Reddit и Twitter и положительные отзывы IMDb. Для модели текст преобразуется в идентификаторы токенов с помощью словаря BERT, а последовательности в батче дополняются до общей длины. Для валидации выделяется 20% данных.
2. Классификатор `TEXT_MODEL` на TensorFlow/Keras использует обучаемый слой `Embedding`, три параллельных `Conv1D` с окнами 2, 3 и 4 токена и выход с sigmoid. Модель обучалась три эпохи с Adam и `binary_crossentropy`. В сохранённом выводе Colab — **85,46% accuracy на валидационной выборке**.
3. Ноутбук экспортирует модель в `final_model/` и сохраняет токенизатор в файл `tokenizer`. Эти артефакты загружаются в `engine.py`. В ноутбуке также есть отдельный эксперимент с LSTM на PyTorch.

Для повторного обучения понадобятся CSV, на которые ссылаются ячейки Google Drive. В репозитории лежит набор Reddit. Для запуска бота достаточно сохранённых модели и токенизатора.

## Установка и запуск на Windows

Понадобится `uv`. Команды ниже создают окружение на Python 3.11 и устанавливают зависимости. Для `bert-for-tf2` закреплена версия `setuptools`, совместимая со сборкой пакета.

Выполни команды из корня репозитория в одном окне PowerShell.

```powershell
$sourceDir = (Get-Location).Path
$buildConstraints = Join-Path $env:TEMP 'text-mood-bot-build-constraints.txt'
'setuptools==69.5.1' | Set-Content -LiteralPath $buildConstraints -Encoding ascii

uv venv --python 3.11 .venv
uv pip install --python .\.venv\Scripts\python.exe `
  --build-constraints "$buildConstraints" `
  'aiogram==2.25.1' 'tensorflow==2.15.0' 'numpy==1.26.4' 'pandas==2.3.3' `
  'scikit-learn==1.9.1' 'nltk==3.10.4' 'translate==3.8.1' 'bert-for-tf2==0.14.9'
```

### Проверка модели без Telegram

TensorFlow на Windows может ошибаться при чтении модели из пути с кириллицей. Следующие команды копируют модель и токенизатор в рабочую папку с латинским путём. Если путь к `%TEMP%` содержит кириллицу, укажи в `$runDir` другой доступный путь без кириллицы.

```powershell
$runDir = Join-Path $env:TEMP 'text-mood-bot-run'
New-Item -ItemType Directory -Path $runDir -Force | Out-Null
$modelFiles = @((Join-Path $sourceDir 'final_model'), (Join-Path $sourceDir 'tokenizer'))
Copy-Item -LiteralPath $modelFiles -Destination $runDir -Recurse -Force
Set-Location -LiteralPath $runDir
$env:TEXTMOODBOT_SOURCE = $sourceDir

& "$sourceDir\.venv\Scripts\python.exe" -B -u -c "import os, sys; sys.path.insert(0, os.environ['TEXTMOODBOT_SOURCE']); from engine import everythin_is_fine; print(everythin_is_fine('I had a good day today.'))"
```

После сообщений TensorFlow должно появиться число.

### Запуск бота

Получи токен у BotFather и создай локальный `config.py` со следующим содержимым:

```python
import os

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
```

Перед запуском задай токен в PowerShell. Ввод в этой команде скрыт. Храни токен локально и исключи старый `config.py` с токеном из публикации.

```powershell
$env:TELEGRAM_BOT_TOKEN = [System.Net.NetworkCredential]::new('', (Read-Host 'Telegram bot token' -AsSecureString)).Password
& "$sourceDir\.venv\Scripts\python.exe" -u "$sourceDir\main.py"
```

Когда в консоли появится `Bot is working!`, отправь боту `/start`, затем сообщение на английском.
