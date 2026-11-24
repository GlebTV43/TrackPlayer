import sys
import os
import subprocess
import time
import random

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QHeaderView, QMainWindow, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtCore, QtMultimedia

from .library import (
    db_agree_file,
    db_album_table_initialization,
    db_auto_generate_album,
    db_create_album,
    db_creating_table_all_tracks_initialization,
    db_get_album_list,
    db_get_current_file,
    db_get_information_about_file,
    db_get_new_files,
    db_initialization,
    db_play_all_tracks_initialization,
    db_table_all_tracks_initialization,
    db_table_currect_album_initialization,
    db_update,
    take_length,
)
from .ui.add_files import Ui_Dialog_ADF
from .ui.auto_generator import Ui_Dialog_AGW
from .ui.choose_album_creation import Ui_Dialog_CCAW
from .ui.create_album_manually import Ui_Dialog_CAYSW
from .ui.help_dialog import Ui_Dialog_Helper
from .ui.main_window import Ui_MainWindow
from .ui.welcome_dialog import Ui_Dialog_Start


# Окно помощи
class HelpWidget(QDialog, Ui_Dialog_Helper):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Загружаем дизайн

        # БИНДЫ
        self.pushButton_Close.clicked.connect(self.close)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(":/Icon/Icon.jpg"))


# Окно первого запуска
class StartHiWidget(QDialog, Ui_Dialog_Start):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Загружаем дизайн

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(":/Icon/Icon.jpg"))

        # БИНДЫ
        self.pushButton_Cancel.clicked.connect(self.cancel)
        self.pushButton_Agree.clicked.connect(self.agree)

        # Переменные класса
        self.dir_path = '%s\\TrackPlayer\\' % os.environ['APPDATA']

    def cancel(self):
        sys.exit()

    def agree(self):
        # Создание собственной директории в AppData\Roaming
        dir_path = '%s\\TrackPlayer\\' % os.environ['APPDATA']
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            os.makedirs(os.path.join(dir_path, 'Configs'))
            db_initialization()

        # Открытие директории
        subprocess.Popen(fr'explorer /open,"{self.dir_path}')
        ex = MainWidget()

        # Выход
        ex.show()
        self.close()


# Окно выбора жанра при добавлении
class AddingWidget(QDialog, Ui_Dialog_ADF):
    def __init__(self, file_name, id):
        super().__init__()
        self.setupUi(self)  # Загружаем дизайн

        self.setWindowIcon(QIcon(":/Icon/Icon.jpg"))

        # Переменные
        dir_path = '%s\\TrackPlayer\\' % os.environ['APPDATA']

        self.name = file_name
        self.id = id
        self.isPlaying = False

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        print(take_length(dir_path + file_name), dir_path + file_name)  # Дебаг
        print(' '.join(file_name.split('.')[:-1]), take_length(dir_path + file_name))  # Дебаг

        time_format = time.strftime("%H:%M:%S",
                                    time.gmtime(take_length(dir_path + file_name)))  # Формат времени

        self.label_CompositionName.setText(
            f"<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">"
            f"{' '.join(file_name.split('.')[:-1])}"
            f"</span></p></body></html>")
        self.label_CompositionDuration.setText(str(time_format))

        # БИНДЫ
        self.pushButton_Continue.clicked.connect(self.adding_to_bd)
        self.pushButton_PlayThis.clicked.connect(self.play_this)

    def adding_to_bd(self):
        genre = self.comboBox_Genre.currentText()
        db_agree_file(self.id, genre)

        self.close()

    def play_this(self):
        self.player = QtMultimedia.QMediaPlayer()
        if self.isPlaying:
            self.pushButton_PlayThis.setText('Play this')

            print('Paused')  # Дебаг
            self.player.stop()
            self.isPlaying = False
        else:
            self.pushButton_PlayThis.setText('Stop this')
            print('Playing')  # Дебаг
            file = db_get_current_file(self.id)
            self.load_mp3(file)
            self.player.play()
            self.player.setVolume(50)
            self.isPlaying = True

    # Инициализация проигрывателя
    def load_mp3(self, filename):
        filename = filename.replace('\\', '/')
        media = QtCore.QUrl.fromLocalFile(filename)
        content = QtMultimedia.QMediaContent(media)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(content)
        print(filename, media, content)


# Окно Авто-создания альбома
class AutoGenWidget(QDialog, Ui_Dialog_AGW):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Загружаем дизайн

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(":/Icon/Icon.jpg"))

        # БИНДЫ
        self.pushButton_Cancel.clicked.connect(self.cancel)
        self.pushButton_ContinueGenerate.clicked.connect(self.generate)

    def cancel(self):
        self.close()

    def generate(self):
        # Соотношение настроений к жанрам
        alf = {'Freedom': ['Early romanticism', 'Late romanticism', 'Folk music', 'Country music', 'Jazz', 'Bard songs',
                           'Soul', 'Disco', 'Pop'], 'Transparency': ['Impressionism'], 'Compassion': ['Expressionism'],
               'Impotence': ['Expressionism'], 'Awareness': ['Neoclassicism'], 'Irony': ['Neoclassicism'],
               'Definition': ['March', 'Rock'], 'Cheerfulness': ['March', 'Rock', 'Hip-hop'],
               'Ideology': ['Symphonic music'], 'Emotionality': ['Symphonic music', 'Chanson'], 'Humor': ['Operetta'],
               'Satire': ['Operetta'],
               'Love affair': ['Operetta', 'Latin American music'], 'Passion': ['Latin American music'],
               'Disharmony': ['Blues', 'Rhythm and blues', 'Soul', 'Pop'],
               'Dissonance': ['Blues', 'Rhythm and blues', 'Soul', 'Pop'],
               'Rhythm': ['Jazz', 'Rock', 'Reggae', 'Soul', 'Rhythm and blues', 'Funk', 'Pop'],
               'Tragie': ['Early romanticism', 'Romance'],
               'Activity': ['Hip-hop'], 'Severity': ['Motet', 'March', 'Mass', 'Chanson', 'Trance', 'Hardcore'],
               'Importance': ['Motet', 'Mass', 'Romance', 'New wave'],
               'Expressiveness': ['Early baroque', 'Late baroque', 'Expressionism'],
               'Contrast': ['Early baroque', 'Late baroque'], 'Drama': ['Early baroque', 'Late baroque', 'Opera'],
               'Clarity': ['Early classicism', 'Late classicism'],
               'Simplicity': ['Early classicism', 'Late classicism', 'Minimalism', 'Folk music', 'Country music'],
               'Ease': ['Early classicism', 'Late classicism', 'Folk music', 'Country music'],
               'Harmony': ['Early classicism', 'Late classicism', 'Jazz']}

        print(self.comboBox_Feeling.currentText())  # Дебаг
        tmp_list = alf[self.comboBox_Feeling.currentText()]
        print(tmp_list)  # Дебаг
        print(self.lineEdit_Name.text(), self.lineEdit_Description.text())  # Дебаг
        flag = db_auto_generate_album(tmp_list, self.lineEdit_Name.text(),
                                      self.lineEdit_Description.text())  # Флаг проверки успешности создания
        if flag:
            self.pushButton_ContinueGenerate.setText('Impossible to generate')
            return
        print('Generated')  # Дебаг
        self.close()


# Окно создания альбома вручную
class CreateYourSelfWidget(QDialog, Ui_Dialog_CAYSW):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Загружаем дизайн

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(":/Icon/Icon.jpg"))

        # БИНДЫ
        self.pushButton_Cancel.clicked.connect(self.cancel)
        self.pushButton_CreateAlbum.clicked.connect(self.create)

        # Инициализация
        self.initialization()

    def initialization(self):
        self.tableWidget_Display.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_Display.horizontalHeader().hide()
        self.tableWidget_Display.verticalHeader().setStyleSheet('QHeaderView::section{background-color: #8b94a3;}')

        self.tableWidget_Display.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tableWidget_Display.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tableWidget_Display.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tableWidget_Display.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        db_creating_table_all_tracks_initialization(self.tableWidget_Display)

    def cancel(self):
        self.close()

    def create(self):
        tmp = db_create_album(self.tableWidget_Display, self.lineEdit_NameAlbum, self.lineEdit_Description,
                              self.label_NameYourAlbum)  # Флаг проверки создания
        if tmp:
            print('Created')
            self.close()


# Окно выбора создания
class ChooseCreatingWidget(QDialog, Ui_Dialog_CCAW):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Загружаем дизайн

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(":/Icon/Icon.jpg"))

        # БИНДЫ
        self.pushButton_Cancel.clicked.connect(self.cancel)
        self.pushButton_CreateYourSelf.clicked.connect(self.create_yourself)
        self.pushButton_GenerateAlbum.clicked.connect(self.generate)

    def cancel(self):
        self.close()

    def create_yourself(self):
        dwindow = CreateYourSelfWidget()
        self.close()
        dwindow.exec_()

    def generate(self):
        dwindow = AutoGenWidget()
        self.close()
        dwindow.exec_()


# Основное окно
class MainWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Загружаем дизайн

        self.setWindowIcon(QIcon(":/Icon/Icon.jpg"))

        # Заставляем показать окно раньше
        self.show()

        # ВАЖНО 16777215 - Максимальный размер виджетов

        # БИНДЫ
        self.pushButton_Albums.clicked.connect(self.changer)
        self.pushButton_Compositions.clicked.connect(self.changer)
        self.pushButton_PauseContinue.clicked.connect(self.player_controller)
        self.pushButton_Repeat.clicked.connect(self.repeater_controller)
        self.pushButton_Mixing.clicked.connect(self.mixing)
        self.pushButton_Previous.clicked.connect(self.previous)
        self.pushButton_Next.clicked.connect(self.next)

        self.pushButton_Update.clicked.connect(self.update_table)

        self.pushButton_AddFiles.clicked.connect(self.add_files)
        self.pushButton_Help.clicked.connect(self.helper)

        self.pushButton_CreatingAlbum.clicked.connect(self.creating_album)

        self.pushButton_PlayAll.clicked.connect(self.play_all_tracks)

        self.horizontalSlider_TimeBar.valueChanged.connect(self.duration_change)
        self.horizontalSlider_Volume.valueChanged.connect(self.volum_controller)

        # Переменные класса
        self.dir_path = '%s\\TrackPlayer\\' % os.environ['APPDATA']  # Путь
        self.isPlaying = [False]  # Проигрывается ли сейчас (для кнопок). Список ради ссылок

        # 0 - Повторение отключено, 1 - Повторение альбома, 2 - Повторение конкретного аудифайла
        self.repeaterChecker = 0

        self.areAdding = False  # Добавляется ли что-то
        self.album_id = ''  # Конкретный выбранный альбом
        self.playing_list = []  # Конкретный набор треков
        self.player = QtMultimedia.QMediaPlayer()  # Объявление плеера
        self.arePlaying = [False]  # Проигрывается ли сейчас дествительно (не для кнопок), схожу с другим, но другое

        self.curIndexAlbum = 0  # Индекс конкретной проигрываемой композиции (Local)
        self.all_playing = False  # Проигрывается ли все

        # Переменные синхронизации аналогичной локальной переменной
        self.TableAlbumWidget.album_id = ''
        self.TableAlbumWidget.player = self.player
        self.TableAlbumWidget.arePlaying = self.arePlaying
        self.TableAlbumWidget.btnPlay = self.pushButton_PauseContinue
        self.TableAlbumWidget.isPlaying = self.isPlaying
        self.arePlaying = self.TableAlbumWidget.arePlaying
        self.isPlaying = self.TableAlbumWidget.isPlaying
        self.TableWidgetForAll.playing_list = self.playing_list
        self.TableAlbumWidget.playing_list = self.playing_list

        # Инициализация
        self.ui_initialization()

        # Инициализация таймера
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timebar)

        # Синхронизация таймера
        self.TableAlbumWidget.timer = self.timer

    # Функция смены вкладок
    def changer(self):
        if self.TableWidgetForAll.isEnabled():
            self.TableWidgetForAll.setEnabled(False)
            self.TableWidgetForAll.hide()
            self.TableWidgetForAll.clearSelection()
            self.AllTracksWidget.setMaximumSize(0, 0)
            self.TableAlbumWidget.setEnabled(True)
            self.TableAlbumWidget.show()
            self.AlbumWidget.setMaximumSize(16777215, 16777215)
        else:
            # Важная проверка отдельного сценария
            if self.TableCurrentAlbumWidget.rowCount() != 0:
                if self.TableAlbumWidget.album_id and self.TableAlbumWidget.album_id != -1:
                    self.playing_list = db_get_album_list(self.TableAlbumWidget.album_id)
                    self.TableWidgetForAll.playing_list = self.playing_list
                    self.album_id = self.TableAlbumWidget.album_id
            self.TableWidgetForAll.setEnabled(True)
            self.TableWidgetForAll.show()
            self.AllTracksWidget.setMaximumSize(16777215, 16777215)
            self.TableAlbumWidget.setEnabled(False)
            self.TableAlbumWidget.hide()
            self.TableAlbumWidget.clearSelection()
            self.AlbumWidget.setMaximumSize(0, 0)

        # Обновление всего
        db_update()
        db_table_all_tracks_initialization(self.TableWidgetForAll, cur_list=self.playing_list)
        db_album_table_initialization(self.TableAlbumWidget, self.TableCurrentAlbumWidget)

    # Инициализация (функция)
    def ui_initialization(self):
        # По умполчанию отображаются композиции
        self.TableAlbumWidget.setEnabled(False)
        self.TableAlbumWidget.hide()
        self.TableAlbumWidget.clearSelection()
        self.AlbumWidget.setMaximumSize(0, 0)

        # Растягиваем таблицу на все предоставленное пространство
        self.TableWidgetForAll.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.TableAlbumWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.TableCurrentAlbumWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Выделяем особенности столбцов
        # self.TableWidgetForAll.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.TableWidgetForAll.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.TableWidgetForAll.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.TableWidgetForAll.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.TableAlbumWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.TableAlbumWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.TableAlbumWidget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.TableCurrentAlbumWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        # Убираем верхние заголовки таблиц
        self.TableWidgetForAll.horizontalHeader().hide()
        self.TableAlbumWidget.horizontalHeader().hide()
        self.TableCurrentAlbumWidget.horizontalHeader().hide()

        # Смена цвета ячеек заголовка таблиц(ы)
        self.TableCurrentAlbumWidget.verticalHeader().setStyleSheet(
            'QHeaderView::section{background-color: #0E1116; color: White}')
        self.TableWidgetForAll.verticalHeader().setStyleSheet('QHeaderView::section{background-color: #8b94a3;}')
        self.TableAlbumWidget.verticalHeader().setStyleSheet('QHeaderView::section{background-color: #8b94a3;}')

        # ИНИЦИАЛИЗАЦИЯ МЕНЮ ПРОИГРЫВАНИЯ
        self.horizontalSlider_Volume.setValue(50)
        self.player.setVolume(50)

        # ФУНКЦИИ
        self.update_table()

    # Функция для проигрывания всего
    def play_all_tracks(self):
        self.timer.stop()
        self.player.stop()
        self.isPlaying = [False]
        self.arePlaying = [False]
        self.TableAlbumWidget.arePlaying = self.arePlaying
        self.TableAlbumWidget.isPlaying = self.isPlaying
        self.curIndexAlbum = 0
        self.pushButton_PauseContinue.setStyleSheet("border-image: url(:/Continue/Continue.png);\n"
                                                    "background-color: #0E1116;\n"
                                                    "color: white")
        self.playing_list = db_play_all_tracks_initialization(self.TableCurrentAlbumWidget)
        db_table_all_tracks_initialization(self.TableWidgetForAll, self.playing_list)
        self.album_id = -1
        self.TableAlbumWidget.album_id = -1

    # Функция переключения композиции назад
    def previous(self):
        if not self.playing_list:
            self.playing_list = self.TableAlbumWidget.playing_list
            self.TableWidgetForAll.playing_list = self.playing_list
            if self.playing_list:
                self.album_id = self.TableAlbumWidget.album_id
        if self.album_id != self.TableAlbumWidget.album_id:
            self.playing_list = self.TableAlbumWidget.playing_list
            self.TableWidgetForAll.playing_list = self.playing_list
            self.album_id = self.TableAlbumWidget.album_id
            self.curIndexAlbum = 0
        if self.curIndexAlbum < 0 or self.curIndexAlbum >= len(self.playing_list):
            self.player.stop()
            self.arePlaying = [False]
            self.isPlaying = [False]
            self.TableAlbumWidget.arePlaying = self.arePlaying
            self.TableAlbumWidget.isPlaying = self.isPlaying
            print('ERROR ILLEGAL INDEX')
            return
        if self.curIndexAlbum == 0:
            if self.repeaterChecker == 1:
                self.player.stop()
                self.arePlaying = [False]
                self.isPlaying = [False]
                self.TableAlbumWidget.arePlaying = self.arePlaying
                self.TableAlbumWidget.isPlaying = self.isPlaying
                print('At end')
                self.curIndexAlbum = len(self.playing_list) - 1
                self.player_controller()
                return
            print("It's minimal")
            return
        self.player.stop()
        self.arePlaying = [False]
        self.isPlaying = [False]
        self.TableAlbumWidget.arePlaying = self.arePlaying
        self.TableAlbumWidget.isPlaying = self.isPlaying
        self.curIndexAlbum -= 1
        self.player_controller()
        print('Previous')

    # Функция переключения вперед (+авто-смена)
    def next(self, is_auto=False):
        if is_auto and self.repeaterChecker == 2:
            self.player.stop()
            self.arePlaying = [False]
            self.isPlaying = [False]
            self.TableAlbumWidget.arePlaying = self.arePlaying
            self.TableAlbumWidget.isPlaying = self.isPlaying
            print('Repeat')
            self.player_controller(is_auto)
            return
        if not self.playing_list:
            self.playing_list = self.TableAlbumWidget.playing_list
            self.TableWidgetForAll.playing_list = self.playing_list
            if self.playing_list:
                self.album_id = self.TableAlbumWidget.album_id
        if self.album_id != self.TableAlbumWidget.album_id:
            self.playing_list = self.TableAlbumWidget.playing_list
            self.TableWidgetForAll.playing_list = self.playing_list
            self.album_id = self.TableAlbumWidget.album_id
            self.curIndexAlbum = 0
        if self.curIndexAlbum < 0 or self.curIndexAlbum >= len(self.playing_list):
            self.player.stop()
            self.arePlaying = [False]
            self.isPlaying = [False]
            self.TableAlbumWidget.arePlaying = self.arePlaying
            self.TableAlbumWidget.isPlaying = self.isPlaying
            print('ERROR ILLEGAL INDEX')
            return
        if self.curIndexAlbum == len(self.playing_list) - 1:
            if self.repeaterChecker == 1:
                self.player.stop()
                self.arePlaying = [False]
                self.isPlaying = [False]
                self.TableAlbumWidget.arePlaying = self.arePlaying
                self.TableAlbumWidget.isPlaying = self.isPlaying
                print('At start')
                self.curIndexAlbum = 0
                self.player_controller(is_auto)
                return
            print("It's maximum", self.curIndexAlbum, self.playing_list)
            return
        self.player.stop()
        self.arePlaying = [False]
        self.isPlaying = [False]
        self.TableAlbumWidget.arePlaying = self.arePlaying
        self.TableAlbumWidget.isPlaying = self.isPlaying
        self.curIndexAlbum += 1
        self.player_controller(is_auto)
        print('Next')

    # Контроллер проигрывания
    def player_controller(self, is_auto=False):
        if is_auto:
            file = db_get_current_file(self.playing_list[self.curIndexAlbum])
            information = db_get_information_about_file(self.playing_list[self.curIndexAlbum])
            len_file = take_length(file)  # MP3(file).info.length
            self.horizontalSlider_TimeBar.setMaximum(int(len_file))
            self.horizontalSlider_TimeBar.setValue(0)
            format_duration = time.strftime("%H:%M:%S", time.gmtime(int(len_file)))
            self.label_FileLen.setText(format_duration)
            if len(information[1]) > 50:
                self.Current_file.setText(information[1][:50] + '...')
            else:
                self.Current_file.setText(information[1])
            self.load_mp3(file)
            self.player.play()
            self.timer.start(1000)
            self.isPlaying = [True]
            self.arePlaying = [True]
            self.TableAlbumWidget.arePlaying = self.arePlaying
            self.TableAlbumWidget.isPlaying = self.isPlaying
            return
        self.arePlaying = self.TableAlbumWidget.arePlaying
        self.isPlaying = self.TableAlbumWidget.isPlaying
        print('***' * 10)
        if self.isPlaying[0]:
            self.pushButton_PauseContinue.setStyleSheet("border-image: url(:/Continue/Continue.png);\n"
                                                        "background-color: #0E1116;\n"
                                                        "color: white")
            self.player.pause()
            print('Paused', self.TableAlbumWidget.album_id, self.playing_list)
            self.isPlaying = [False]
            self.timer.stop()
            print('BREAK 1')
        else:
            if not self.TableAlbumWidget.album_id and not self.playing_list:
                print('NOTHING SELECTED')
                self.timer.stop()
                print('BREAK 2')
                return
            self.pushButton_PauseContinue.setStyleSheet("border-image: url(:/Pause/Pause.png);\n"
                                                        "background-color: #0E1116;\n"
                                                        "color: white")
            if not self.playing_list or self.TableAlbumWidget.album_id != self.album_id:
                self.curIndexAlbum = 0
                self.album_id = self.TableAlbumWidget.album_id
                self.playing_list = db_get_album_list(self.TableAlbumWidget.album_id)
                self.TableWidgetForAll.playing_list = self.playing_list
                file = db_get_current_file(self.playing_list[self.curIndexAlbum])
                information = db_get_information_about_file(self.playing_list[self.curIndexAlbum])
                len_file = take_length(file)
                print(len_file)
                self.timer.stop()
                self.horizontalSlider_TimeBar.setMaximum(int(len_file))
                self.horizontalSlider_TimeBar.setValue(0)
                print(file)
                format_duration = time.strftime("%H:%M:%S", time.gmtime(int(len_file)))
                self.label_FileLen.setText(format_duration)
                if len(information[1]) > 50:
                    self.Current_file.setText(information[1][:50] + '...')
                else:
                    self.Current_file.setText(information[1])
                self.load_mp3(file)
                self.player.play()
                self.timer.start(1000)
                self.arePlaying = [True]
                print('BREAK 3')
            else:
                file = db_get_current_file(self.playing_list[self.curIndexAlbum])
                information = db_get_information_about_file(self.playing_list[self.curIndexAlbum])
                print(file)
                if not self.arePlaying[0] \
                        or self.horizontalSlider_TimeBar.value() >= self.horizontalSlider_TimeBar.maximum():
                    len_file = take_length(file)  # MP3(file).info.length
                    format_duration = time.strftime("%H:%M:%S", time.gmtime(int(len_file)))
                    self.load_mp3(file)
                    self.horizontalSlider_TimeBar.setMaximum(int(len_file))
                    self.horizontalSlider_TimeBar.setValue(0)
                    self.label_FileLen.setText(format_duration)
                    if len(information[1]) > 50:
                        self.Current_file.setText(information[1][:50] + '...')
                    else:
                        self.Current_file.setText(information[1])
                    self.arePlaying = [True]
                self.timer.start(1000)
                self.player.play()
                print('BREAK 4')
            print('Playing', self.TableAlbumWidget.album_id, self.playing_list)
            self.isPlaying = [True]
        print(self.TableAlbumWidget.isPlaying, self.isPlaying, self.TableAlbumWidget.arePlaying, self.arePlaying)
        self.TableAlbumWidget.isPlaying = self.isPlaying
        self.TableAlbumWidget.arePlaying = self.arePlaying
        print(self.TableAlbumWidget.isPlaying, self.isPlaying, self.TableAlbumWidget.arePlaying, self.arePlaying)

    # Функция перемешки
    def mixing(self):
        # Получение и перемешка
        self.player.stop()
        self.pushButton_PauseContinue.setStyleSheet("border-image: url(:/Continue/Continue.png);\n"
                                                    "background-color: #0E1116;\n"
                                                    "color: white")
        self.isPlaying = [False]
        self.arePlaying = [False]
        self.TableAlbumWidget.isPlaying = self.isPlaying
        self.TableAlbumWidget.arePlaying = self.arePlaying
        if not self.TableAlbumWidget.album_id:
            return
        if self.album_id == -1:
            tmp_list = self.playing_list
            random.shuffle(tmp_list)
        else:
            tmp_list = db_get_album_list(self.TableAlbumWidget.album_id)
            random.shuffle(tmp_list)
            self.album_id = self.TableAlbumWidget.album_id

        self.curIndexAlbum = 0

        self.playing_list = tmp_list
        self.TableWidgetForAll.playing_list = self.playing_list
        db_table_currect_album_initialization(table_widget=self.TableCurrentAlbumWidget, current_list=tmp_list)

        print('Mixed')

    # Инициализация аудиофайла
    def load_mp3(self, filename):
        filename = filename.replace('\\', '/')
        media = QtCore.QUrl.fromLocalFile(filename)
        content = QtMultimedia.QMediaContent(media)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(content)

        self.TableAlbumWidget.player = self.player

        self.player.setVolume(self.horizontalSlider_Volume.value())
        print(filename, media, content)

    # Функция изменения тайм-бара вручную
    def duration_change(self):
        if not self.isPlaying[0]:
            return
        self.timer.stop()
        print(int(self.horizontalSlider_TimeBar.value()))
        self.player.setPosition(self.horizontalSlider_TimeBar.value() * 1000)
        self.horizontalSlider_TimeBar.clearFocus()
        self.timer.start(1000)

    # Функция повторения
    def repeater_controller(self):
        if self.repeaterChecker == 0:  # Если выключено
            self.pushButton_Repeat.setStyleSheet("border-image: url(:/Repeat/Repeat.png);\n"
                                                 "background-color: #0E1116;\n"
                                                 "color: white")
            print('Repeat Album')
            self.repeaterChecker = 1
        elif self.repeaterChecker == 1:  # Если повторялся альбом
            self.pushButton_Repeat.setStyleSheet("border-image: url(:/RepeatDouble/RepeatDouble.png);\n"
                                                 "background-color: #0E1116;\n"
                                                 "color: white")
            print('Repeat current file')
            self.repeaterChecker = 2
        elif self.repeaterChecker == 2:  # Если повторялась конкретная композиция
            self.pushButton_Repeat.setStyleSheet("border-image: url(:/RepeatOff/RepeatOff.png);\n"
                                                 "background-color: #0E1116;\n"
                                                 "color: white")
            print('Repeat off')
            self.repeaterChecker = 0
        else:
            print('ERROR')
            self.pushButton_Repeat.setStyleSheet("border-image: url(:/RepeatOff/RepeatOff.png);\n"
                                                 "background-color: #0E1116;\n"
                                                 "color: white")
            print('Repeat off')
            self.repeaterChecker = 0

    # Функция изменения тайм-бара (Auto)
    def update_timebar(self):
        self.horizontalSlider_TimeBar.blockSignals(True)
        self.horizontalSlider_TimeBar.setValue(self.horizontalSlider_TimeBar.value() + 1)
        if self.horizontalSlider_TimeBar.value() >= self.horizontalSlider_TimeBar.maximum():  # Вызов авто-переклюсения
            print("GO")
            self.timer.stop()
            self.next(is_auto=True)

        self.horizontalSlider_TimeBar.blockSignals(False)

    # Функция изменения громкости
    def volum_controller(self):
        self.player.setVolume(self.horizontalSlider_Volume.value())
        print(self.horizontalSlider_Volume.value())

    # Функция добавления файлов
    def add_files(self):
        if self.isPlaying[0] and self.arePlaying[0]:
            self.timer.stop()
            self.player.pause()
        if self.areAdding:
            self.update_table()
        else:
            subprocess.Popen(fr'explorer /open,"{self.dir_path}')
            self.areAdding = True
            self.pushButton_AddFiles.setText('Update...')
        if self.isPlaying[0] and self.arePlaying[0]:
            self.timer.start(1000)
            self.player.play()

    # Функция обновления значений и синхронизации
    def update_table(self):
        # Синхронизация значений кнопок
        self.areAdding = False
        self.pushButton_AddFiles.setText('Add files...')

        db_update()
        db_album_table_initialization(self.TableAlbumWidget, self.TableCurrentAlbumWidget)

        tmp_results = db_get_new_files()
        for x in tmp_results:
            self.adding_widget_initialization(x[3], x[0])
        db_table_all_tracks_initialization(self.TableWidgetForAll, cur_list=self.playing_list)

    # Функция вызова окна добавления
    def adding_widget_initialization(self, fullname, id):
        dwindow = AddingWidget(fullname, id)
        dwindow.exec_()

    # Функция создания альбома
    def creating_album(self):
        if self.isPlaying[0] and self.arePlaying[0]:
            self.timer.stop()
            self.player.pause()
        dwindow = ChooseCreatingWidget()
        dwindow.exec_()
        db_album_table_initialization(self.TableAlbumWidget, self.TableCurrentAlbumWidget)
        if self.isPlaying[0] and self.arePlaying[0]:
            self.timer.start(1000)
            self.player.play()

    # Функция вызова окна помощи
    def helper(self):
        dwindow = HelpWidget()
        dwindow.exec_()

    # Функция закрытия всего
    def closeEvent(self, event):
        for window in QApplication.topLevelWidgets():
            window.close()


def main():
    dir_path = '%s\\TrackPlayer\\' % os.environ['APPDATA']
    app = QApplication(sys.argv)
    # Проверка наличия необходимых файлов/директорий
    if os.path.exists(dir_path):
        if not os.path.exists(os.path.join(dir_path, 'Configs')):
            os.makedirs(os.path.join(dir_path, 'Configs'))
            db_initialization()
        print(os.path.exists(os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')))
        if not os.path.exists(os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')):
            db_initialization()
        ex = MainWidget()
        ex.show()
        return app.exec()
    else:
        ex = StartHiWidget()
        ex.show()
        ex.exec_()
        if os.path.exists(dir_path):
            d = HelpWidget()
            d.show()
            ex = MainWidget()
            ex.show()
            return app.exec()
        return 0
