from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from multiprocessing import Pool,Queue
from functools import partial
import MangaSiteleri
import re
import sys
import urllib.request,urllib.parse
import os


def worker(img, konum):

    try:
        os.makedirs(konum)
    except:
        pass
    os.chdir(konum)
    sayfa = img[img.rfind("/") + 1:img.rfind(".")]
    urllib.request.urlretrieve(img, sayfa + ".jpg")
    print(konum,sayfa,"indi.")
class Thread(QThread):
    signal=pyqtSignal(str,int)
    def __init__(self,indilecek_konum,site, parent=None,**bolumler):

        super(Thread,self).__init__(parent)
        self.bolumler=bolumler
        self.site=site

        manga=list(bolumler.keys())[0]
        manga = manga[0:manga.rfind(" ",0,len(manga)-1)]
        self.konum=indilecek_konum+"/"+manga+site.name
    def run(self):
        bolum=list(self.bolumler.keys())
        link=list(self.bolumler.values())
        print(self.bolumler)
        for index in range(len(bolum)):
            self.signal.emit(bolum[index],1)
            self.pool = Pool(5)
            self.pool.map(partial(worker, konum=self.konum+"/"+bolum[index]),self.site.resim_listesi_al(link[index]))
            self.pool.close()
            print(bolum[index],"indi")
            self.signal.emit(bolum[index],2)
    def stop(self):
        self.terminate()
        self.pool.close()


class Pencere(QMainWindow):
    def __init__(self):
        super().__init__()
        self.site=MangaSiteleri.PuzzMos()
        self.bolumler={}
        self.indexAralik={}

        self.seceneklerUI()
        self.indirmeyoneticiUI()
        self.anaekranUI()
        self.bolumpencereUI()





    def anaekranUI(self):
        mangalar = self.site.mangalist
        manga_isimleri=list(mangalar.keys())
        manga_isimleri.sort()
        self.setCentralWidget(QWidget(self))
        self.setMaximumSize(950, 400)
        self.setMinimumSize(950, 400)
        self.setWindowTitle("Manga İndirici")

        self.gridMain = QGridLayout()
        self.gridMain.setContentsMargins(QMargins(3, 3, 3, 3))
        self.gridMain.setSpacing(3)
        self.centralWidget().setLayout(self.gridMain)

        self.liste_manga = QListWidget()
        self.liste_manga.addItems(manga_isimleri)

        self.combo_manga = QComboBox()
        self.combo_manga.addItems(["PuzzMos", "Manga-tr"])
        self.combo_manga.currentIndexChanged.connect(self.liste_sifirla)

        self.buton_listele = QPushButton("Bölüm Listele")
        self.buton_listele.clicked.connect(self.bolum_liste_goster)

        self.gridMain.addWidget(self.combo_manga, 1, 1)
        self.gridMain.addWidget(self.buton_listele, 2, 2)
        self.gridMain.addWidget(self.grup_indirme, 1, 3, 2, 1)
        self.gridMain.addWidget(self.liste_manga, 2, 1)
    def indirmeyoneticiUI(self):
        self.grup_label = QLabel("Selman")
        self.grup_indirme = QGroupBox(self)
        self.grup_indirme.setFixedSize(600, 397)

        self.gridYonetici = QGridLayout()
        self.grup_indirme.setLayout(self.gridYonetici)
        self.gridYonetici.setSpacing(3)
        self.gridYonetici.setContentsMargins(0, 0, 0, 0)

        self.yonetici_table = QTableWidget()
        self.yonetici_table.setColumnCount(3)
        self.yonetici_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.yonetici_table.verticalHeader().setVisible(False)
        
        self.yonetici_table.setShowGrid(False)
        self.yonetici_table.setHorizontalHeaderLabels(["#", "Manga", "Durum"])
        header=self.yonetici_table.horizontalHeader()
        header.setDefaultSectionSize(20)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)


        self.yonetici_buton_baslat = QPushButton("Başla")
        self.yonetici_buton_baslat.clicked.connect(self.indirme_baslat)
        self.yonetici_buton_durdur = QPushButton("Durdur")
        ##self.yonetici_buton_durdur.clicked.connect(self.Thread.stop) henüz oluşmadığı için hatalı indirme başlarken tanımladım
        self.yonetici_buton_reset = QPushButton("Sıfırla")
        self.yonetici_buton_reset.clicked.connect(self.yoneticiSifirla)
        self.yonetici_buton_sil=QPushButton("Sil")
        self.yonetici_buton_sil.clicked.connect(self.yoneticiSil)
        self.yonetici_buton_secenekler = QPushButton("Seçenekler")
        self.yonetici_buton_secenekler.clicked.connect(self.pencere_secenek.show)

        self.gridYonetici.addWidget(self.yonetici_buton_baslat, 1, 1)
        self.gridYonetici.addWidget(self.yonetici_buton_durdur, 1, 2)
        self.gridYonetici.addWidget(self.yonetici_buton_reset, 1, 3)
        self.gridYonetici.addWidget(self.yonetici_buton_sil,1,4)
        self.gridYonetici.addWidget(self.yonetici_buton_secenekler, 1, 7)
        self.gridYonetici.addWidget(self.yonetici_table, 2, 1, 3, 7)
    def bolumpencereUI(self):
        self.pencere_bolum = QDialog()
        self.pencere_bolum.setMaximumSize(400, 300)
        self.pencere_bolum.setMinimumSize(400, 300)

        self.gridBolum = QGridLayout()
        self.gridBolum.setSpacing(3)
        self.gridBolum.setContentsMargins(QMargins(3, 3, 3, 3))
        self.pencere_bolum.setLayout(self.gridBolum)

        self.liste_bolum = QListWidget()
        self.liste_bolum.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.buton_indirsecilen = QPushButton("Seçilenleri Listeye Ekle")
        self.buton_indirsecilen.clicked.connect(self.manga_liste_ekle)

        self.gridBolum.addWidget(self.liste_bolum, 0, 0)
        self.gridBolum.addWidget(self.buton_indirsecilen, 0, 1, alignment=Qt.AlignTop)
    def seceneklerUI(self):
        self.pencere_secenek=QDialog()
        self.pencere_secenek.setMaximumSize(400, 250)
        self.pencere_secenek.setMinimumSize(400, 250)

        self.gridSecenek=QGridLayout()
        self.pencere_secenek.setLayout(self.gridSecenek)
        self.gridSecenek.setSpacing(3)

        self.secenek_konum = QLineEdit("D:/Mangas", self)

        self.gridSecenek.addWidget(QLabel("Konum"),1,1)
        self.gridSecenek.addWidget(self.secenek_konum,1,2)



    def yoneticiSil(self):
        row=self.yonetici_table.currentItem().row()
        manga=self.yonetici_table.item(row,1).text()
        print(manga,row)
        if manga in self.indexAralik.keys():
            for index in range(self.indexAralik[manga][0]-1,self.indexAralik[manga][1]+1):
                self.yonetici_table.removeRow(row)
                print(index)
        else:
            self.yonetici_table.removeRow(row)
    def yoneticiChanged(self):
        for manga,konum in self.indexAralik.items():
            temp={}
            for index in range(konum[0],konum[1]+1):
                temp[self.yonetici_table.item(index,1).text()]=self.yonetici_table.item(index,2).text()
            sirali=sorted(temp.keys(),key=self.stringSplitByNumbers)
            tempindex = 0
            for index in range(konum[0],konum[1]+1):
                self.yonetici_table.setItem(index, 1, QTableWidgetItem(sirali[tempindex]))
                self.yonetici_table.setItem(index, 2, QTableWidgetItem(temp[sirali[tempindex]]))
                tempindex+=1
    def yoneticiSifirla(self):
        for item in self.yonetici_table.findItems("Tamamlandı",Qt.MatchExactly):
            self.yonetici_table.setItem(item.row(),item.column(),QTableWidgetItem("Bekliyor"))
    def liste_sifirla(self):
        text=self.combo_manga.currentText()
        if text=="Manga-tr":
            self.site=MangaSiteleri.MangaTR()
        elif text=="PuzzMos":
            self.site=MangaSiteleri.PuzzMos()
        self.liste_manga.clear()
        mangalar = self.site.mangalist
        manga_isimleri=list(mangalar.keys())
        manga_isimleri.sort()
        self.liste_manga.addItems(manga_isimleri)
    def yonetici_genislet(self):
        button = qApp.focusWidget()
        index = self.yonetici_table.indexAt(button.pos())
        manga=self.yonetici_table.item(index.row(),1).text()
        aralik=self.indexAralik[manga]

        if button.text()=="+":
            button.setText("-")
            for x in range(aralik[0],aralik[1]+1):
                self.yonetici_table.showRow(x)
        else:
            button.setText("+")
            for x in range(aralik[0],aralik[1]+1):
                self.yonetici_table.hideRow(x)
    def stringSplitByNumbers(self,x):
        r = re.compile('(\d+)')
        l = r.split(x)
        return [int(y) if y.isdigit() else y for y in l]
    def bolum_liste_goster(self):
        self.liste_bolum.clear()
        manga=self.liste_manga.currentItem().text()
        manga_url=self.site.mangalist[manga]
        bolumler=self.site.bolum_listesi_al(manga_url)
        self.bolumler.update(bolumler)
        bolum_liste=list(bolumler.keys())

        self.pencere_bolum.show()
        self.liste_bolum.show()
        self.buton_indirsecilen.show()
        self.liste_bolum.addItems(sorted(bolum_liste,key=self.stringSplitByNumbers))
        for index in range(self.liste_bolum.count()):
            x=self.liste_bolum.item(index)
            if self.yonetici_table.findItems(x.text(),Qt.MatchExactly):
                x.setFlags(Qt.ItemIsSelectable)
                x.setFlags(Qt.ItemIsEnabled)
                x.setFlags(Qt.ItemIsUserCheckable)





    @pyqtSlot(str,int)#tamamlanan bölüm
    def sinyal(self,text,durum):
        row = self.yonetici_table.findItems(text, Qt.MatchExactly)[0].row()

        manga_row = self.yonetici_table.findItems(text[0:text.rfind(" ",0,len(text)-1)], Qt.MatchExactly)[0].row()
        genel_durum=[int(x) for x in self.yonetici_table.item(manga_row,2).text().split("/")]
        if(durum==2):
            genel_durum[0]+=1
            self.yonetici_table.setItem(row, 2, QTableWidgetItem("Tamamlandı"))
            son_durum=str(genel_durum[0])+"/"+str(genel_durum[1])
            self.yonetici_table.setItem(manga_row, 2, QTableWidgetItem(son_durum))
        else:
            self.yonetici_table.setItem(row, 2, QTableWidgetItem("İndiriliyor"))



        print("Sinyal alındı###################"+text)
    def indirme_baslat(self):
        items=[]
        row=self.yonetici_table.currentItem().row()
        if(self.yonetici_table.cellWidget(row,0)):
            manga=self.yonetici_table.item(row,1).text()
            for index in range(self.indexAralik[manga][0],self.indexAralik[manga][1]+1):
                if (self.yonetici_table.item(index, 2).text() != "Tamamlandı"):
                    items.append(self.yonetici_table.item(index, 1))
        else:
            for aralik in self.yonetici_table.selectedRanges():
                for index in range(aralik.topRow(),aralik.bottomRow()+1):
                    if(self.yonetici_table.item(index,2).text()!="Tamamlandı"):
                        items.append(self.yonetici_table.item(index,1))
        bolumler = {i.text(): self.bolumler[i.text()] for i in items}
        print(bolumler)
        print("sdasdsa")

        self.Thread = Thread(self.secenek_konum.text(), self.site, self, **bolumler)
        self.Thread.start()
        self.Thread.signal.connect(self.sinyal)
        self.yonetici_buton_durdur.clicked.connect(self.Thread.stop)
        self.pencere_bolum.hide()
    def manga_liste_ekle(self):

        bolumler=self.bolumler
        items = self.liste_bolum.selectedItems()
        indilecek = {i.text():bolumler[i.text()] for i in items}
        manga = list(indilecek.keys())[0]
        manga = manga[0:manga.rfind(" ",0,len(manga)-1)]

        if self.yonetici_table.findItems(manga,Qt.MatchExactly):###########################prototip
            konum=self.yonetici_table.findItems(manga,Qt.MatchExactly)[0].row()
            for key, value in self.indexAralik.items():

                diger = self.yonetici_table.findItems(key, Qt.MatchExactly)[0].row()
                if manga==key:
                    value[1]+=len(indilecek)
                    durum=self.yonetici_table.item(konum,2)
                    a=durum.text().split("/")
                    a[1]=str(int(a[1])+len(indilecek))
                    son="/".join(a)
                    self.yonetici_table.setItem(konum,2,QTableWidgetItem(son))
                else:
                    if konum < diger:
                        value[0] += len(indilecek)
                        value[1] += len(indilecek)

            bolumkonum=self.indexAralik[manga][0]
        else:
            for key, value in self.indexAralik.items():

                value[0] += len(indilecek) + 1
                value[1] += len(indilecek) + 1

            self.indexAralik[manga]=[1,len(indilecek)]
            buton_genislet=QPushButton("-")
            buton_genislet.clicked.connect(self.yonetici_genislet)
            self.yonetici_table.insertRow(0)
            self.yonetici_table.setCellWidget(0,0,buton_genislet)
            self.yonetici_table.setItem(0,1,QTableWidgetItem(manga))
            self.yonetici_table.item(0,1).setFont(QFont("Times", 10, QFont.Bold))
            self.yonetici_table.setItem(0,2,QTableWidgetItem("0/"+str(len(indilecek))))
            self.yonetici_table.setRowHeight(0,20)
            bolumkonum=1
        for key in indilecek.keys():
            self.yonetici_table.insertRow(bolumkonum)
            self.yonetici_table.setItem(bolumkonum,1,QTableWidgetItem(key))
            self.yonetici_table.setItem(bolumkonum,2,QTableWidgetItem("Bekliyor"))
            self.yonetici_table.setRowHeight(bolumkonum,15)

        self.yoneticiChanged()
sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook
if __name__ == '__main__':
    uygulama=QApplication(sys.argv)
    pencere=Pencere()
    pencere.show()
    try:
        uygulama.exec_()
    except:
        print("exiting")