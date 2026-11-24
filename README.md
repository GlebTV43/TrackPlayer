<p align="center">
  <img src="Icon.jpg" alt="Логотип TrackPlayer" width="104">
</p>

<h1 align="center">TrackPlayer</h1>

<p align="center">Локальный аудиоплеер для Windows с медиатекой и плейлистами по настроению.</p>
<p align="center"><strong>Python 3.9 · PyQt5 · SQLite</strong></p>
<p align="center"><a href="#возможности">Возможности</a> · <a href="#быстрый-старт">Быстрый старт</a> · <a href="#как-добавить-музыку">Как добавить музыку</a></p>

## Возможности

| Раздел | Что можно делать |
| --- | --- |
| **Медиатека** | Добавлять локальные файлы MP3, WAV и AAC, редактировать названия и жанры треков. |
| **Альбомы** | Собирать плейлисты вручную или подбирать треки из медиатеки по жанрам, связанным с выбранным настроением. |
| **Воспроизведение** | Слушать отдельные треки, альбомы или всю медиатеку. Управлять очередью, громкостью, перемоткой, повтором и перемешиванием. |

## Быстрый старт

Для запуска используйте **Windows и Python 3.9**. Версии зависимостей в `requirements.txt` взяты из исходного окружения проекта.

В PowerShell из папки репозитория выполните:

```powershell
py -3.9 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

При первом запуске подтвердите создание папки медиатеки. TrackPlayer создаст свою базу SQLite в `%APPDATA%\TrackPlayer\Configs\TrackPlayerDataBase.db`.

## Как добавить музыку

1. Нажмите **Add files…**. Откроется папка `%APPDATA%\TrackPlayer`.
2. Скопируйте аудиофайлы в эту папку и нажмите **Update…** в плеере.
3. Укажите жанры новых треков. В разделе **Compositions** откроется медиатека, а в **Albums** можно собрать первый плейлист.

## Устройство проекта

| Файл | Назначение |
| --- | --- |
| [`main.py`](main.py) | Запуск приложения, главное окно и управление воспроизведением. |
| [`DBWorker.py`](DBWorker.py) | Синхронизация папки с медиатекой, хранение треков и альбомов в SQLite. |
| [`MainDesign.ui`](MainDesign.ui) и другие `.ui` | Макеты окон Qt Designer. |
| [`Icons.qrc`](Icons.qrc) и [`Icons_rc.py`](Icons_rc.py) | Описание и скомпилированные ресурсы интерфейса. |

<details>
<summary>Сборка EXE</summary>

После установки зависимостей запустите PyInstaller из корня репозитория:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller main.spec
```

Исполняемый файл появится в `dist\main.exe`.

</details>
