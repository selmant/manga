from bs4 import BeautifulSoup
import requests


class MangaTR:
    def __init__(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0', }
        sayfa = requests.get('http://www.manga-tr.com/manga-list.html', headers=headers)
        soup = BeautifulSoup(sayfa.content, "html.parser")
        a = soup.find_all("span", {"data-toggle": "mangapop"})
        manga_list = {x.get_text(): "http://www.manga-tr.com/" + x.find("a").get("href") for x in a}
        self.mangalist=manga_list
        self.name="(Manga-tr)"
    def bolum_listesi_al(self,url):
        bolum_list = {}
        a = requests.get(url)
        soup = BeautifulSoup(a.content, "html.parser")
        soup = soup.find_all("script", {"type": "text/javascript"})
        for x in soup:
            if str(x).find("manga_cek") != -1:
                script = str(x)
        script = script[script.find("?manga_cek") + 11:script.find(")", script.find("?manga_cek")) - 1]
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        page = 1
        bolumler = [1]
        while bolumler != []:
            data = {'page': str(page)}
            url = 'http://www.manga-tr.com/cek/fetch_pages_manga.php?manga_cek=' + script
            a = requests.post(url, headers=headers, data=data)
            soup = BeautifulSoup(a.content, "html.parser")
            pages = soup.find_all("ul", {"class", "pagination1"})
            bolumler = soup.find_all("td", {"align": "left"})
            for bolum in bolumler:
                bolum_list[bolum.find("a").get_text()] = "http://www.manga-tr.com/" + bolum.find("a").get("href")
            page += 1
        return bolum_list
    def resim_listesi_al(self,url):
        sayfa=requests.request("GET",url,cookies={"read_type":"1"})
        soup=BeautifulSoup(sayfa.content,"html.parser")
        liste=list(soup.find_all("img",{"class":"chapter-img"}))
        liste=["http://www.manga-tr.com/"+x.get("src") for x in liste]
        return liste
class PuzzMos:
    def __init__(self):
        sayfa = requests.get("http://puzzmos.com/directory?type=text")
        soup = BeautifulSoup(sayfa.content, "html.parser")
        a = soup.find_all("span", {"data-toggle": "mangapop"})
        manga_list = {x.get_text(): x.find("a").get("href") for x in a}
        self.mangalist=manga_list
        self.name="(PuzzMos)"
    def bolum_listesi_al(self,url):
        sayfa = requests.get(url)
        soup = BeautifulSoup(sayfa.content, "html.parser")
        a = soup.find("table", {"id": "bolumler"})
        a = a.find_all("tr")
        bolum_list = {x.find("td").get_text(): x.find("a").get("href") for x in a}
        return bolum_list
    def resim_listesi_al(self,url):
        cookie = url[url.rfind("/", None, url.rfind("/")) + 1:url.rfind("/")]
        sayfa = requests.request("GET", url, cookies={cookie: "webtoon"})
        soup = BeautifulSoup(sayfa.content, "html.parser")
        liste = list(soup.find_all("img", {"class": "chapter-img2"}))
        liste = [x.get("src") for x in liste]
        return liste
