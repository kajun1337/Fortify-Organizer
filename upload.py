import subprocess
import logging
import time

def sscye_yukle(url, yukleme_tokeni, proje_adi, proje_surumu, fpr_yolu):
    try:
        yukleme_komutu = f'fortifyclient uploadFPR -file "{fpr_yolu}" -project "{proje_adi}" -version "{proje_surumu}" -authtoken "{yukleme_tokeni}" -url "{url}"'
        
        logging.info(f"Yukleme komutu calistiriliyor: {yukleme_komutu}")
        
        with open("yukleme_output.txt", "w") as output_dosyasi:
            islem = subprocess.Popen(yukleme_komutu, shell=True, stdout=output_dosyasi, stderr=subprocess.STDOUT)
            while islem.poll() is None:
                print("Yukleme yapiliyor", flush=True)
                time.sleep(1)
            islem.wait()

        if islem.returncode != 0:
            logging.error("FPR yukleme islemi basarisiz oldu. Detaylar icin yukleme_output.txt dosyasini kontrol edin.")
            with open("yukleme_output.txt", "r") as dosya:
                logging.error(dosya.read())
            print("FPR yuklemesi sirasinda hata olustu. Daha fazla bilgi icin yukleme_output.txt dosyasini kontrol edin.")
            return False
        logging.info("FPR basariyla yüklendi.")
        return True
    except Exception as e:
        logging.error(f"FPR yukleme hatasi: {e}")
        print(f"FPR yukleme sirasinda bir hata olustu: {e}")
        return False
