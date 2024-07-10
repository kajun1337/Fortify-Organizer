import os
import logging
import time
import requests
from scan import fortify_taramasi_yap, fpr_dosyasi_kontrol_et
from upload import sscye_yukle

logging.basicConfig(filename='debug_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def afis_goster():
    afis = r"""
██╗  ██╗ █████╗      ██╗██╗   ██╗███╗   ██╗ ██╗██████╗ ██████╗ ███████╗
██║ ██╔╝██╔══██╗     ██║██║   ██║████╗  ██║███║╚════██╗╚════██╗╚════██║
█████╔╝ ███████║     ██║██║   ██║██╔██╗ ██║╚██║ █████╔╝ █████╔╝    ██╔╝
██╔═██╗ ██╔══██║██   ██║██║   ██║██║╚██╗██║ ██║ ╚═══██╗ ╚═══██╗   ██╔╝ 
██║  ██╗██║  ██║╚█████╔╝╚██████╔╝██║ ╚████║ ██║██████╔╝██████╔╝   ██║  
╚═╝  ╚═╝╚═╝  ╚═╝ ╚════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═╝╚═════╝ ╚═════╝    ╚═╝      

    """
    print(afis)
    logging.info("Afis gosterildi.")

def proje_yolu_al():
    yol = input("Lutfen .sln dosyanizin yolunu girin: ")
    logging.info(f"Proje yolu girildi: {yol}")
    return yol

def ssc_bilgilerini_al():
    url = input("Lutfen SSC URL'sini girin: ")
    proje_tokeni = input("Lutfen proje bilgilerini almak icin auth token'i girin: ")
    yukleme_tokeni = input("Lutfen FPR yuklemek icin auth token'i girin: ")
    vsdevcmd = input("Lutfen Visual Studio Developer Command Prompt yolunu girin: ")
    logging.info(f"SSC URL: {url}")
    logging.info("Tokenler ve vsdevcmd yolu girildi.")
    return url, proje_tokeni, yukleme_tokeni, vsdevcmd

def proje_surumlerini_al(url, proje_tokeni):
    basliklar = {
        'Authorization': f'FortifyToken {proje_tokeni}',
        'Content-Type': 'application/json'
    }
    try:
        logging.info("SSC'den proje surumleri aliniyor.")
        yanit = requests.get(f'{url}/api/v1/projectVersions', headers=basliklar, verify=False)
        yanit.raise_for_status()
        logging.info("Proje surumleri basariyla alindi.")
        return yanit.json()['data']
    except requests.exceptions.HTTPError as http_hatasi:
        logging.error(f"HTTP hatasi olustu: {http_hatasi}")
        if yanit.status_code == 401:
            print("Yetkilendirme hatasi: Auth token'inizi kontrol edin.")
        else:
            print(f"HTTP hatasi olustu: {http_hatasi}")
    except Exception as hata:
        logging.error(f"Proje surumlerini alirken hata olustu: {hata}")
        print(f"Baska bir hata olustu: {hata}")
    return []

def ana():
    logging.info("Program basladi.")
    afis_goster()
    proje_yolu = proje_yolu_al()

    if not os.path.isfile(proje_yolu):
        logging.error("Gecersiz proje yolu girildi.")
        print("Girilen yol gecerli degil. Lutfen gecerli bir .sln dosya yolu saglayin.")
        return

    url, proje_tokeni, yukleme_tokeni, vsdevcmd = ssc_bilgilerini_al()

    proje_surumleri = proje_surumlerini_al(url, proje_tokeni)
    if proje_surumleri:
        print("Lutfen yuklemek istediginiz projeyi secin:")
        projeler = {}
        for surum in proje_surumleri:
            proje_adi = surum['project']['name']
            if proje_adi not in projeler:
                projeler[proje_adi] = []
            projeler[proje_adi].append(surum)
        
        proje_adlari = list(projeler.keys())
        for i, proje_adi in enumerate(proje_adlari, start=1):
            print(f"{i}. {proje_adi}")
        proje_secimi = int(input("Seciminizi yapin (1, 2, 3, ...): ")) - 1
        secilen_proje_adi = proje_adlari[proje_secimi]
        secilen_proje_surumleri = projeler[secilen_proje_adi]
        
        print("Lutfen yuklemek istediginiz proje surumunu secin:")
        for i, surum in enumerate(secilen_proje_surumleri, start=1):
            print(f"{i}. {surum['name']}")
        surum_secimi = int(input("Seciminizi yapin (1, 2, 3, ...): ")) - 1
        secilen_surum = secilen_proje_surumleri[surum_secimi]['name']
        
        logging.info(f"Secilen proje: {secilen_proje_adi}, surum: {secilen_surum}")
    else:
        logging.error("Proje surumu bulunamadi.")
        print("Mevcut proje surumu bulunamadi.")
        return

    fpr_yolu = f'{os.path.dirname(proje_yolu)}\\{os.path.splitext(os.path.basename(proje_yolu))[0]}.fpr'

    print("Tarama yapiliyor", flush=True)
    if fortify_taramasi_yap(proje_yolu, vsdevcmd):
        print("\nFortify taramasi basariyla tamamlandi.", flush=True)
        print("FPR dosyasi olusturuluyor", flush=True)
        while not fpr_dosyasi_kontrol_et(fpr_yolu):
            for i in range(4):
                print("\rFPR dosyasi olusturuluyor, lutfen bekleyin" + "." * i, end="", flush=True)
                time.sleep(1)
        print("\nFPR dosyasi olusturuldu, yukleme islemi basliyor...", flush=True)
        print("Yukleme yapiliyor", flush=True)
        if sscye_yukle(url, yukleme_tokeni, secilen_proje_adi, secilen_surum, fpr_yolu):
            print("\nFPR dosyasi SSC'ye basariyla yüklendi.", flush=True)
        else:
            print("\nFPR dosyasi SSC'ye yuklenemedi. Daha fazla bilgi icin yukleme_output.txt dosyasini kontrol edin.", flush=True)
    else:
        print("\nFortify taramasi basarisiz oldu.", flush=True)
    logging.info("Program sona erdi.")

if __name__ == "__main__":
    ana()
