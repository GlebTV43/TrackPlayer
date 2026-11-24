import os.path
import sqlite3
import time
import ast

from pathlib import Path

from mutagen.mp3 import MP3
from mutagen.aac import AAC
from mutagen.wave import WAVE
from mutagen.flac import FLAC

from PyQt5 import QtGui, QtMultimedia, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem, QCheckBox, QPushButton, QTableWidget, QLineEdit, QLabel, QDialog, \
    QHeaderView

from .ui.album_information import Ui_Dialog_AIW
from .ui.change_composition import Ui_Dialog_CCW


# Функция получения длины
def take_length(file):
    CORRECT_TYPES_FILES = ['mp3', 'aac', 'wav', 'flac']
    cur_type = file.split('\\')[-1].split('.')[-1]
    if cur_type == CORRECT_TYPES_FILES[0]:
        return int(MP3(file).info.length)
    if cur_type == CORRECT_TYPES_FILES[1]:
        return int(AAC(file).info.length)
    if cur_type == CORRECT_TYPES_FILES[2]:
        return int(WAVE(file).info.length)
    if cur_type == CORRECT_TYPES_FILES[3]:
        return int(FLAC(file).info.length)


# Функция инициализации БД (Создание)
def db_initialization():
    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    file_path = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

    genres = [['Rock'], ['Pop'], ['Rap'], ['Jazz'], ['Opera'], ['Classical'], ['Heavy metal'], ['Motet'],
              ['Early baroque'], ['Late baroque'], ['Early classicism'], ['Late classicism'], ['Early romanticism'],
              ['Late romanticism'], ['Impressionism'], ['Expressionism'], ['Minimalism'], ['Neoclassicism'],
              ['March'], ['Symphonic music'], ['Operetta'], ['Mass'], ['Folk music'], ['Country music'],
              ['Latin American music'], ['Blues'], ['Rhythm and blues'], ['Chanson'], ['Romance'], ['Bard songs'],
              ['Electronic music'], ['Techno'], ['Trance'], ['Hardcore'], ['House'], ['Hip-hop'], ['Reggae'], ['Funk'],
              ['New wave'], ['Soul'], ['Disco']]

    # Подключение к БД
    con = sqlite3.connect(file_path)

    # Создание курсора
    cur = con.cursor()

    cur.execute("""CREATE TABLE Album (
                    AlbumID     INTEGER          PRIMARY KEY AUTOINCREMENT,
                    AlbumName   NVARCHAR (250),
                    Description NVARCHAR (10000),
                    TrackList   STRING,
                    Duration    INTEGER,
                    IsDeleted   INTEGER
                );""")
    cur.execute("""CREATE TABLE Genre (
                    GenreID   INTEGER        PRIMARY KEY,
                    GenreName NVARCHAR (250) 
                );""")
    cur.execute("""CREATE TABLE Track (
                    TrackID   INTEGER         PRIMARY KEY AUTOINCREMENT,
                    TrackName NVARCHAR (250),
                    GenreID   INTEGER,
                    FileName  NVARCHAR (1000),
                    Duration  INTEGER,
                    Status    INTEGER         DEFAULT 2
                );""")

    cur.executemany("""INSERT INTO Genre(GenreName) VALUES (?)""", (genres))
    con.commit()


# Окно информации альбома
class InformationAlbumWidget(QDialog, Ui_Dialog_AIW):
    def __init__(self, idd):
        super().__init__()
        self.setupUi(self)  # Загружаем дизайн

        self.setWindowIcon(QIcon(":/Icon/Icon.jpg"))

        self.id = idd

        self.initialization()

        # БИНДЫ
        self.pushButton_Cancel.clicked.connect(self.cancel)
        self.pushButton_Apply.clicked.connect(self.apply)
        self.pushButton_Delete.clicked.connect(self.delete)

    def initialization(self):
        dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
        # name = str(dir_path) + '\\Configs' + 'TrackPlayerDataBase.db'
        name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

        # Подключение к БД
        con = sqlite3.connect(name)

        # Создание курсора
        cur = con.cursor()
        result = cur.execute(f"""SELECT * FROM Album WHERE AlbumID = '{self.id}' AND IsDeleted = '0'""").fetchall()
        if len(result) == 0:
            print('SMT ERROR')
            self.close()
        format_duration = time.strftime("%H:%M:%S", time.gmtime(int(result[0][4])))
        self.label_NameAlbum.setText(f"<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">"
                                     f"{str(result[0][1])}</span></p></body></html>")
        self.lineEdit_NameAlbum.setText(str(result[0][1]))
        self.lineEdit_Description.setText(str(result[0][2]))
        self.label_Duration.setText(f"<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">"
                                    f"{format_duration}</span></p></body></html>")

        self.tableWidget_Display.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_Display.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tableWidget_Display.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tableWidget_Display.verticalHeader().setStyleSheet('QHeaderView::section{background-color: #8b94a3;}')
        self.tableWidget_Display.horizontalHeader().hide()

        result_list = ast.literal_eval(result[0][3])
        self.tableWidget_Display.setRowCount(len(result_list))
        for i in range(len(result_list)):
            x = result_list[i]
            file_results = cur.execute(f"""SELECT * FROM Track WHERE TrackID = '{int(x)}'""").fetchall()
            for j, val in enumerate(file_results[0]):
                if j == 0:
                    continue
                if j == 1:
                    if len(val) > 100:
                        val = val[:100]
                    self.tableWidget_Display.setItem(i, 0, QTableWidgetItem(val))
                if j == 2:
                    self.tableWidget_Display.setItem(i, 1, QTableWidgetItem(
                        str(cur.execute(f"""SELECT GenreName FROM Genre WHERE Genreid='{val}'""").fetchall()[0][0])))
                if j == 4:
                    if file_results[0][5] == 0:
                        self.tableWidget_Display.setItem(i, 2, QTableWidgetItem("NONE"))
                        size_col = self.tableWidget_Display.columnCount()
                        for x in range(size_col):
                            print(i, x)
                            item = self.tableWidget_Display.item(i, x)
                            print(item)
                            item.setBackground(QtGui.QColor(100, 30, 30))
                        continue
                    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
                    all_dir_path = str(dir_path) + "\\" + file_results[0][3]
                    # audio = MP3(all_dir_path)
                    time_format = time.strftime("%H:%M:%S",
                                                time.gmtime(take_length(all_dir_path)))  # int(audio.info.length)
                    self.tableWidget_Display.setItem(i, 2, QTableWidgetItem(str(time_format)))
                else:
                    continue

    def cancel(self):
        self.close()

    def apply(self):
        dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
        name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

        # Подключение к БД
        con = sqlite3.connect(name)

        # Создание курсора
        cur = con.cursor()
        if not self.lineEdit_NameAlbum.text():
            cur.execute(f"""UPDATE Album
                        SET Description = '{self.lineEdit_Description.text()}'
                        WHERE AlbumID = '{int(self.id)}'""")
            con.commit()
            con.close()
            self.close()
        else:
            print('CHANGED')
            cur.execute(f"""UPDATE Album
                        SET Description = '{self.lineEdit_Description.text()}', 
                        AlbumName = '{self.lineEdit_NameAlbum.text()}'
                        WHERE AlbumID = '{self.id}'""")
            con.commit()
            con.close()
            self.close()

    def delete(self):
        dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
        name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

        # Подключение к БД
        con = sqlite3.connect(name)

        # Создание курсора
        cur = con.cursor()

        cur.execute(f"""UPDATE Album
                    SET IsDeleted = '1'
                    WHERE AlbumID = {self.id}""")
        con.commit()
        con.close()
        self.close()


# Окно редактора аудиофайла
class CompositionChangerWidget(QDialog, Ui_Dialog_CCW):
    def __init__(self, idd):
        super().__init__()
        self.setupUi(self)  # Загружаем дизайн

        self.setWindowIcon(QIcon(":/Icon/Icon.jpg"))

        self.id = idd

        self.initialization()

        # БИНДЫ
        self.pushButton_Cancel.clicked.connect(self.cancel)
        self.pushButton_Apply.clicked.connect(self.apply)
        self.pushButton_Delete.clicked.connect(self.delete)

    def initialization(self):
        dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
        name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

        # Подключение к БД
        con = sqlite3.connect(name)

        # Создание курсора
        cur = con.cursor()
        result = cur.execute(f"""SELECT * FROM Track WHERE TrackID = '{self.id}'""").fetchall()

        all_dir_path = str(dir_path) + "\\" + result[0][3]
        # audio = MP3(all_dir_path)
        time_format = time.strftime("%H:%M:%S", time.gmtime(take_length(all_dir_path)))  # int(audio.info.length)

        genre_id = result[0][2]
        genre = cur.execute(f"""SELECT GenreName from Genre
                            WHERE GenreID = '{genre_id}'""").fetchall()[0][0]

        self.comboBox_Genre.setCurrentText(genre)

        self.label_CompositionName.setText(f"<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">"
                                           f"{result[0][1]}</span></p></body></html>")
        self.label_CompositionDuration.setText(time_format)

        print(result)

    def cancel(self):
        self.close()

    def apply(self):
        dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
        name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

        # Подключение к БД
        con = sqlite3.connect(name)

        # Создание курсора
        cur = con.cursor()
        genre_id = cur.execute(f"""SELECT GenreID from Genre 
                                WHERE GenreName = '{self.comboBox_Genre.currentText()}'""").fetchall()[0][0]

        cur.execute(f"""UPDATE Track
                    SET GenreID = '{genre_id}'
                    WHERE TrackID = '{self.id}'""")
        con.commit()
        con.close()
        self.close()

    def delete(self):
        dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
        name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

        # Подключение к БД
        con = sqlite3.connect(name)

        # Создание курсора
        cur = con.cursor()

        file_name = cur.execute(f"""SELECT FileName from Track
                                WHERE TrackID = '{self.id}'""").fetchall()[0][0]
        path = os.path.join(dir_path, file_name)
        os.remove(path)

        cur.execute(f"""UPDATE Track
                    SET Status = '0'
                    WHERE TrackID = '{self.id}'""")

        con.commit()
        con.close()
        self.close()


# Класс кнопки проигрывания альбома
class IndexedButtonWidget_PlayAlbum(QPushButton):
    def init(self, text='', parent=None):
        super(QPushButton, self).init(text, parent=parent)
        self.button_row = 0
        self.button_column = 0
        self.button_text = ""
        self.album_id = ""
        self.table_widget = QTableWidget

    def db_start_playing_album(self):
        self.parent().parent().player.stop()
        self.parent().parent().timer.stop()
        self.parent().parent().btnPlay.setStyleSheet("border-image: url(:/Continue/Continue.png);\n"
                                                     "background-color: #0E1116;\n"
                                                     "color: white")
        self.parent().parent().arePlaying = [False]
        self.parent().parent().isPlaying = [False]
        self.parent().parent().playing_list = db_get_album_list(self.album_id)
        print(self.parent().parent().arePlaying, self.parent().parent().isPlaying)

        db_table_currect_album_initialization(self.table_widget, int(self.album_id))
        print('SELECTED AND PLAYING')
        self.parent().parent().album_id = self.album_id


# Класс кнопки информации альбома
class IndexedButtonWidget_InfoAlbum(QPushButton):
    def init(self, text='', parent=None):
        super(QPushButton, self).init(text, parent=parent)
        self.button_row = 0
        self.button_column = 0
        self.button_text = ""
        self.album_id = ""
        self.table_widget = QTableWidget()

    def db_get_information_album(self):
        if self.parent().parent().album_id == self.album_id:
            return
        dwindow = InformationAlbumWidget(self.album_id)
        dwindow.exec_()

        # Обновление таблицы
        db_album_table_initialization(self.parent().parent(), self.table_widget)


# Класс кнопки информации файла
class IndexedButtonWidget_InfoComposition(QPushButton):
    def init(self, text='', parent=None):
        super(QPushButton, self).init(text, parent=parent)
        self.button_row = 0
        self.button_column = 0
        self.button_text = ""
        self.file_dir = ""

    def db_get_information_composition(self):
        # print(self.parent().parent())
        if not self.it_works:
            return
        dwindow = CompositionChangerWidget(self.file_dir)
        dwindow.exec_()

        # Обновление таблицы
        db_table_all_tracks_initialization(self.parent().parent(), self.parent().parent().playing_list)


# Класс чек-бокса выбора файла
class IndexedCheckBoxWidget_Adding(QCheckBox):
    def init(self, text='', parent=None):
        super(QCheckBox, self).init(text, parent=parent)
        self.button_row = 0
        self.button_column = 0
        self.button_text = ""
        self.file_dir = ""

    def tmpfunc(self):
        print(self.isChecked())


# Класс кнопки проигрывания в окне создания альбома
class IndexedButtonWidget_PlayThis(QPushButton):
    def init(self, text='', parent=None):
        super(QPushButton, self).init(text, parent=parent)
        self.button_row = 0
        self.button_column = 0
        self.button_text = ""
        self.file_dir = ""
        self.isPlaying = False
        self.setStyleSheet("border-image: url(:/Continue/Continue.png);\n"
                           "background-color: #0E1116;\n"
                           "color: white")

    def player_controller(self):
        self.player = QtMultimedia.QMediaPlayer()
        if self.isPlaying:
            self.setStyleSheet("border-image: url(:/Continue/Continue.png);\n"
                               "background-color: #0E1116;\n"
                               "color: white")

            print('Paused')
            self.player.stop()
            self.isPlaying = False
        else:
            self.setStyleSheet("border-image: url(:/Pause/Pause.png);\n"
                               "background-color: #0E1116;\n"
                               "color: white")
            print('Playing')
            file = db_get_current_file(self.file_dir)
            self.load_mp3(file)
            self.player.play()
            self.player.setVolume(50)
            self.isPlaying = True

    def load_mp3(self, filename):
        filename = filename.replace('\\', '/')
        media = QtCore.QUrl.fromLocalFile(filename)
        content = QtMultimedia.QMediaContent(media)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(content)
        print(filename, media, content)


# Функция инициализации выбранного альбома
def db_table_currect_album_initialization(table_widget=QTableWidget, album_id=0, current_list=[]):
    print(table_widget, album_id, current_list)
    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

    table_widget.setRowCount(0)

    # Подключение к БД
    con = sqlite3.connect(name)

    # Создание курсора
    cur = con.cursor()

    if current_list:
        table_widget.setRowCount(len(current_list))
        for i, elem in enumerate(current_list):
            track_list = cur.execute(f"""SELECT * FROM Track
                                            WHERE TrackID = '{elem}'""").fetchall()[0]
            if track_list[-1] == 0:
                table_widget.setRowCount(table_widget.rowCount() - 1)
                continue
            for j, val in enumerate(track_list):
                if j == 1:
                    if len(val) > 120:
                        val = val[:120]
                    table_widget.setItem(i, 0, QTableWidgetItem(val))
                if j == 4:
                    all_dir_path = str(dir_path) + "\\" + track_list[3]
                    # audio = MP3(all_dir_path)
                    time_format = time.strftime("%H:%M:%S", time.gmtime(take_length(all_dir_path)))  # audio.info.length
                    table_widget.setItem(i, 1, QTableWidgetItem(str(time_format)))
        table_widget.resizeRowsToContents()
        return

    results = ast.literal_eval(cur.execute(f"""SELECT * FROM Album 
        WHERE AlbumID = '{album_id}'""").fetchall()[0][3])
    print(results)
    table_widget.setRowCount(len(results))

    if not results:
        print('ERROR')
        return 0
    i = -1
    for elem in results:
        track_list = cur.execute(f"""SELECT * FROM Track
                                WHERE TrackID = '{elem}'""").fetchall()[0]
        print(track_list)
        if track_list[-1] == 0:
            print(table_widget.rowCount())
            table_widget.setRowCount(table_widget.rowCount() - 1)
            print(table_widget.rowCount())
            continue
        i += 1
        for j, val in enumerate(track_list):
            print(j, val)
            if j == 1:
                if len(val) > 120:
                    val = val[:120]
                table_widget.setItem(i, 0, QTableWidgetItem(val))
            if j == 4:
                all_dir_path = str(dir_path) + "\\" + track_list[3]
                print(all_dir_path)
                # audio = MP3(all_dir_path)
                time_format = time.strftime("%H:%M:%S",
                                            time.gmtime(take_length(all_dir_path)))  # int(audio.info.length)
                table_widget.setItem(i, 1, QTableWidgetItem(str(time_format)))
            else:
                continue
    table_widget.resizeRowsToContents()


# Инициализация таблицы всех файлов
def db_table_all_tracks_initialization(table_widget, cur_list=[]):
    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

    table_widget.setRowCount(0)

    # Подключение к БД
    con = sqlite3.connect(name)

    # Создание курсора
    cur = con.cursor()

    results = cur.execute("""SELECT * FROM Track 
    WHERE Status = '1'""").fetchall()
    if not results:
        print('ERROR')
        return 0

    table_widget.setRowCount(len(results))
    for i, elem in enumerate(results):
        for j, val in enumerate(elem):
            if j == 0:
                continue
            if j == 1:
                if len(val) > 100:
                    val = val[:100]
                table_widget.setItem(i, 0, QTableWidgetItem(val))
            if j == 2:
                table_widget.setItem(i, 1, QTableWidgetItem(
                    str(cur.execute(f"""SELECT GenreName FROM Genre WHERE Genreid='{val}'""").fetchall()[0][0])))
            if j == 4:
                all_dir_path = str(dir_path) + "\\" + elem[3]
                # audio = MP3(all_dir_path)
                time_format = time.strftime("%H:%M:%S",
                                            time.gmtime(take_length(all_dir_path)))  # int(audio.info.length)
                table_widget.setItem(i, 2, QTableWidgetItem(str(time_format)))
            else:
                continue

        btn_changer = IndexedButtonWidget_InfoComposition('Info')
        btn_changer.button_row = i
        btn_changer.button_column = 3
        btn_changer.button_text = 'Info'
        btn_changer.file_dir = elem[0]
        if elem[0] in cur_list:
            btn_changer.setStyleSheet("""background-color: #8B2635;
                                        color: white; border-radius: 9px;""")
            btn_changer.it_works = False
        else:
            btn_changer.setStyleSheet("""background-color: #0E1116;
                                                    color: white; border-radius: 9px;""")
            btn_changer.it_works = True
        btn_changer.clicked.connect(btn_changer.db_get_information_composition)
        table_widget.setCellWidget(i, 3, btn_changer)

    # table_widget.resizeRowsToContents()


# Инициализации таблицы в окне создания альбома
def db_creating_table_all_tracks_initialization(table_widget):
    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

    table_widget.setRowCount(0)

    # Подключение к БД
    con = sqlite3.connect(name)

    # Создание курсора
    cur = con.cursor()

    results = cur.execute("""SELECT * FROM Track 
    WHERE Status = '1'""").fetchall()
    if not results:
        print('ERROR')
        return 0

    table_widget.setRowCount(len(results))

    for i, elem in enumerate(results):
        for j, val in enumerate(elem):
            if j == 0:
                continue
            if j == 1:
                if len(val) > 120:
                    val = val[:120]
                table_widget.setItem(i, 0, QTableWidgetItem(val))
            if j == 2:
                table_widget.setItem(i, 1, QTableWidgetItem(
                    str(cur.execute(f"""SELECT GenreName FROM Genre WHERE Genreid='{val}'""").fetchall()[0][0])))
            if j == 4:
                all_dir_path = str(dir_path) + "\\" + elem[3]
                # audio = MP3(all_dir_path)
                time_format = time.strftime("%H:%M:%S",
                                            time.gmtime(take_length(all_dir_path)))  # int(audio.info.length)
                table_widget.setItem(i, 2, QTableWidgetItem(str(time_format)))
            else:
                continue

        # Ячейка выбора
        chb_add = IndexedCheckBoxWidget_Adding('Add')
        chb_add.button_row = i
        chb_add.button_column = 4
        chb_add.button_text = 'Add'
        chb_add.file_dir = elem[0]
        chb_add.setStyleSheet("""background-color: #0E1116;
        color: white; border-radius: 9px;""")
        chb_add.clicked.connect(chb_add.tmpfunc)
        table_widget.setCellWidget(i, 4, chb_add)

        # Проиграть конкретный файл
        btn_playthis = IndexedButtonWidget_PlayThis('')
        btn_playthis.setStyleSheet("border-image: url(:/Continue/Continue.png);\n"
                                   "background-color: #0E1116;\n"
                                   "color: white")
        btn_playthis.button_row = i
        btn_playthis.button_column = 3
        btn_playthis.button_text = ''
        btn_playthis.file_dir = elem[0]
        btn_playthis.isPlaying = False
        btn_playthis.clicked.connect(btn_playthis.player_controller)
        table_widget.setCellWidget(i, 3, btn_playthis)

    # table_widget.resizeRowsToContents()


# Инициализации таблицы всех альбомов
def db_album_table_initialization(table_widget=QTableWidget, using_table_widget=QTableWidget):
    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

    table_widget.setRowCount(0)

    # Подключение к БД
    con = sqlite3.connect(name)

    # Создание курсора
    cur = con.cursor()

    results = cur.execute("""SELECT * FROM Album WHERE IsDeleted = '0'""").fetchall()
    if not results:
        print('ERROR')
        return 0

    table_widget.setRowCount(len(results))

    for i, elem in enumerate(results):
        for j, val in enumerate(elem):
            if j == 0:
                continue
            if j == 1:
                if len(val) > 75:
                    val = val[:75]
                table_widget.setItem(i, 0, QTableWidgetItem(val))
            if j == 2:
                if len(val) > 55:
                    val = val[:55]
                table_widget.setItem(i, 1, QTableWidgetItem(val))
            if j == 4:
                format_duration = time.strftime("%H:%M:%S", time.gmtime(int(val)))
                table_widget.setItem(i, 2, QTableWidgetItem(str(format_duration)))
            else:
                continue

        # Кнопка информации
        btn_info = IndexedButtonWidget_InfoAlbum('Info')
        btn_info.button_row = i
        btn_info.button_column = 3
        btn_info.button_text = 'Info'
        btn_info.album_id = elem[0]
        btn_info.table_widget = using_table_widget
        btn_info.setStyleSheet("""background-color: #0E1116;
                color: white; border-radius: 9px;""")
        btn_info.clicked.connect(btn_info.db_get_information_album)
        table_widget.setCellWidget(i, 3, btn_info)

        # Кнопка проигрывания/выбора
        btn_play = IndexedButtonWidget_PlayAlbum('Play')
        btn_play.button_row = i
        btn_play.button_column = 3
        btn_play.button_text = 'Play'
        btn_play.album_id = elem[0]
        btn_play.table_widget = using_table_widget
        btn_play.setStyleSheet("""background-color: #0E1116;
                        color: white; border-radius: 9px;""")
        btn_play.clicked.connect(btn_play.db_start_playing_album)
        table_widget.setCellWidget(i, 4, btn_play)

    # table_widget.resizeRowsToContents()


# Функция добавления нового альбома
def db_create_album(table_widget=QTableWidget, name=QLineEdit, description=QLineEdit, name_label=QLabel):
    size_row = table_widget.rowCount()
    print(size_row)
    tmp_base = []
    for x in range(size_row):
        item = table_widget.cellWidget(x, 4)
        if type(item) == IndexedCheckBoxWidget_Adding and item.isChecked():
            tmp_base += [item.file_dir]

    if not name.text().split():
        print('NONE')  # 8B2635
        name.setStyleSheet("background-color: #580411;\n"
                           "color: white")
        name_label.setStyleSheet("background-color: #580411;\n"
                                 "color: white")
        if len(tmp_base) == 0:
            size_row = table_widget.rowCount()
            for x in range(size_row):
                item = table_widget.cellWidget(x, 4)
                item.setStyleSheet("background-color: #580411;\n"
                                   "color: white")
        else:
            size_row = table_widget.rowCount()
            for x in range(size_row):
                item = table_widget.cellWidget(x, 4)
                item.setStyleSheet("background-color: #8B94A3;\n"
                                   "color: white")
        return False
    name.setStyleSheet("background-color: #8b94a3;"
                       "color: white")
    name_label.setStyleSheet("background-color: #0E1116;"
                             "color: white")
    if len(tmp_base) == 0:
        size_row = table_widget.rowCount()
        for x in range(size_row):
            item = table_widget.cellWidget(x, 4)
            item.setStyleSheet("background-color: #580411;\n"
                               "color: white")
        return False

    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    nameBD = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

    # Подключение к БД
    con = sqlite3.connect(nameBD)

    # Создание курсора
    cur = con.cursor()

    all_duration = 0
    for x in tmp_base:
        result_file = cur.execute(f"""SELECT FileName FROM Track WHERE TrackID = '{x}'""").fetchall()
        all_file_path = str(dir_path) + "\\" + result_file[0][0]
        all_duration += take_length(all_file_path)  # int(MP3(all_file_path).info.length)

    description_text = description.text()
    if not description_text:
        description_text = 'NONE'
    cur.execute(
        f"""INSERT INTO Album(TrackList, Description, AlbumName, Duration, IsDeleted) 
        VALUES('{tmp_base}', '{description_text}', '{name.text()}', '{all_duration}', '0')""")

    con.commit()
    con.close()
    print(tmp_base)
    return True


# Функция обновления, синхронизации папки и БД
def db_update():
    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')
    CORRECT_TYPES_FILES = ['mp3', 'aac', 'wav']

    # Подключение к БД
    con = sqlite3.connect(name)

    # Создание курсора
    cur = con.cursor()

    for x in dir_path.rglob("*"):
        tmp = str(x).split('\\')[-1]
        if tmp.split('.')[-1] not in CORRECT_TYPES_FILES:
            print('BAD FILE ', tmp)
            continue

        result = cur.execute(f"""SELECT TrackName FROM Track
        WHERE FileName = '{tmp}' AND (Status = '1' OR Status = '2')
        """).fetchall()
        if len(result) == 0:
            print('Nothing', tmp, '...')
            print('...' * 10)
            cur.execute(f"""INSERT INTO Track(TrackName, FileName, Status) 
            VALUES('{' '.join(tmp.split('.')[:-1])}', '{tmp}', '2')
            """)

        else:
            print('Something OK', tmp)

    track_list = cur.execute("""SELECT * FROM Track WHERE Status = '1' OR Status = '2'""").fetchall()

    for x in track_list:
        all_dir_path = str(dir_path) + """\\""" + x[3]
        print(all_dir_path)
        check_file = os.path.exists(all_dir_path)
        if check_file:
            continue
        else:
            cur.execute(f"""UPDATE Track
        SET Status = '0'
        WHERE FileName = '{x[3]}'""")

    con.commit()
    con.close()


# Фонкция для каждого нового файла
def db_get_new_files():
    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

    # Подключение к БД
    con = sqlite3.connect(name)

    # Создание курсора
    cur = con.cursor()

    return cur.execute(f"""SELECT * FROM Track
        WHERE Status = '2'
        """).fetchall()


# Функция подтверждения добавления
def db_agree_file(file_id, genre):
    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

    # Подключение к БД
    con = sqlite3.connect(name)

    # Создание курсора
    cur = con.cursor()

    genreID = cur.execute(f"""SELECT GenreID FROM Genre
    WHERE GenreName = '{genre}'""").fetchall()

    cur.execute(f"""UPDATE Track
    SET GenreID = '{genreID[0][0]}', Status = '1'
    WHERE TrackID = '{file_id}'""")

    con.commit()
    con.close()


# Получение списка композиций альбома по ID
def db_get_album_list(album_id):
    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

    # Подключение к БД
    con = sqlite3.connect(name)

    # Создание курсора
    cur = con.cursor()

    tmp_list = ast.literal_eval(cur.execute(f"""SELECT TrackList from Album 
                                        WHERE AlbumID = '{album_id}'""").fetchall()[0][0])
    cur_list = []

    for x in tmp_list:
        tmp = cur.execute(f"""SELECT * FROM Track WHERE Status = '1' AND TrackID = '{x}'""").fetchall()
        # print(tmp, tmp[0][0])
        if tmp:
            cur_list += [tmp[0][0]]
    return cur_list


# Получение ссылки файла по ID
def db_get_current_file(track_id):
    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

    # Подключение к БД
    con = sqlite3.connect(name)

    # Создание курсора
    cur = con.cursor()

    return str(dir_path) + '\\' + \
           cur.execute(f"""SELECT FileName FROM Track WHERE TrackID = '{track_id}'""").fetchall()[0][0]


# Получение всей информации файла по ID
def db_get_information_about_file(track_id):
    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

    # Подключение к БД
    con = sqlite3.connect(name)

    # Создание курсора
    cur = con.cursor()

    return cur.execute(f"""SELECT * FROM Track WHERE TrackID = '{track_id}'""").fetchall()[0]


# Функция проигрывания всего
def db_play_all_tracks_initialization(table_widget=QTableWidget):
    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

    # Подключение к БД
    con = sqlite3.connect(name)

    # Создание курсора
    cur = con.cursor()

    results = cur.execute(f"""SELECT * FROM Track WHERE Status = '1'""").fetchall()

    all_list = []

    table_widget.setRowCount(len(results))

    for i, elem in enumerate(results):
        for j, val in enumerate(elem):
            if j == 1:
                if len(val) > 120:
                    val = val[:120]
                table_widget.setItem(i, 0, QTableWidgetItem(val))
            if j == 4:
                all_dir_path = str(dir_path) + "\\" + elem[3]
                # audio = MP3(all_dir_path)
                time_format = time.strftime("%H:%M:%S",
                                            time.gmtime(take_length(all_dir_path)))  # int(audio.info.length)
                table_widget.setItem(i, 1, QTableWidgetItem(str(time_format)))
        all_list += [elem[0]]
        table_widget.resizeRowsToContents()
    print(all_list)
    return all_list


# Функция авто-генератора
def db_auto_generate_album(genre_list, name_album, description):
    dir_path = Path('%s\\TrackPlayer\\' % os.environ['APPDATA'])
    name = os.path.join(dir_path, 'Configs', 'TrackPlayerDataBase.db')

    # Подключение к БД
    con = sqlite3.connect(name)

    # Создание курсора
    cur = con.cursor()

    all_duration = 0
    album_list = []
    for genre in genre_list:
        print(genre)
        genreID = cur.execute(f"""SELECT GenreID from Genre WHERE GenreName = '{genre}'""").fetchall()[0][0]
        print(genre, genreID)
        if not genreID:
            continue
        results = cur.execute(f"""SELECT TrackID from Track WHERE GenreID = '{genreID}'""").fetchall()
        print(results, 'RESULTS')
        if not results:
            continue
        for x in results:
            result_file = cur.execute(f"""SELECT FileName FROM Track WHERE TrackID = '{x[0]}'""").fetchall()
            all_file_path = str(dir_path) + "\\" + result_file[0][0]
            all_duration += take_length(all_file_path)  # int(MP3(all_file_path).info.length)
            album_list += [x[0]]

    if not album_list:
        return True

    if name_album == '':
        name_album = 'AutoGenerated Album'

    # format_duration = time.strftime("%H:%M:%S", time.gmtime(all_duration))
    print('END')
    cur.execute(f"""INSERT INTO Album(TrackList, Description, AlbumName, Duration, IsDeleted) 
                VALUES('{album_list}', '{description}', '{name_album}', '{all_duration}', '0')""")
    con.commit()
    cur.close()
    return False
