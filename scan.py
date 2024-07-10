import os
import subprocess
import logging
import time

def fortify_taramasi_yap(proje_yolu, vsdevcmd):
    try:
        calisma_dizini = os.path.dirname(proje_yolu)
        proje_adi = os.path.splitext(os.path.basename(proje_yolu))[0]
        build_id = proje_adi

        batch_komutlari = f"""
        call "{vsdevcmd}"
        cd "{calisma_dizini}"
        sourceanalyzer -b "{build_id}" -clean
        sourceanalyzer -b "{build_id}" msbuild /t:rebuild "{os.path.basename(proje_yolu)}"
        sourceanalyzer -b "{build_id}" -scan -f "{calisma_dizini}\\{proje_adi}.fpr"
        """
        
        logging.info("Fortify tarama batch komutlari calistiriliyor.")
        
        with open("run_fortify.bat", "w") as batch_dosyasi:
            batch_dosyasi.write(batch_komutlari)

        with open("fortify_tarama_output.txt", "w") as output_dosyasi:
            islem = subprocess.Popen("run_fortify.bat", shell=True, stdout=output_dosyasi, stderr=subprocess.STDOUT)
            while islem.poll() is None:
                print("Tarama yapiliyor", flush=True)
                time.sleep(1)
            islem.wait()

        if islem.returncode != 0:
            logging.error("Fortify tarama batch islemi basarisiz oldu.")
            print("Batch dosyasi basarisiz oldu. Daha fazla bilgi icin fortify_tarama_output.txt dosyasini kontrol edin.")
            return False

        logging.info("Fortify tarama basariyla tamamlandi.")
        return True
    except Exception as e:
        logging.error(f"Fortify tarama hatasi: {e}")
        print(f"Fortify taramasi sirasinda bir hata olustu: {e}")
        return False

def fpr_dosyasi_kontrol_et(fpr_yolu):
    max_bekleme_suresi = 300
    bekleme_suresi = 0
    while not os.path.isfile(fpr_yolu) and bekleme_suresi < max_bekleme_suresi:
        logging.info("FPR dosyasinin olusturulmasi bekleniyor.")
        print("FPR dosyasi olusturuluyor, lutfen bekleyin...", flush=True)
        time.sleep(5)
        bekleme_suresi += 5
    if os.path.isfile(fpr_yolu):
        logging.info("FPR dosyasi bulundu.")
        return True
    else:
        logging.error("FPR dosyasi maksimum bekleme suresi icinde bulunamadi.")
        return False
