# 🔁 Class Renamer

**HTML ve CSS projelerinde kullanılan class isimlerini güvenli bir şekilde yeniden adlandırır.**

## 🚀 Özellikler

- HTML ve CSS dosyalarındaki tüm class'ları analiz eder
- Problemli veya kısa class isimlerini hariç tutar
- Rastgele yeni class isimleri oluşturur (örneğin: `aabbcc`, `zzxxyy`)
- Tüm değişikliklerden önce otomatik yedek alır
- Güncellenmiş class isimlerini HTML ve CSS dosyalarında uygular
- JSON formatında mapping ve istatistik raporu oluşturur
- Geri alma (rollback) desteği sunar

---

## 📦 Kurulum

```bash
git clone https://github.com/fastuptime/Class_Renamer.git
cd Class_Renamer
````

---

##  Kullanım

### Class'ları yeniden adlandırmak için:

```bash
python class_renamer.py
```

> İşlem başlamadan önce örnek eşleşmeler gösterilir ve onay istenir.

### Geri alma (Rollback) işlemi:

```bash
python class_renamer.py rollback <backup_dizini>
```

> Örnek:
>
> ```bash
> python class_renamer.py rollback backup_20250825_154030
> ```

---

## 📁 Oluşturulan Dosyalar

* `backup_YYYYMMDD_HHMMSS/` → Güncellenmeden önceki orijinal dosyalar
* `class_rename_report.json` → Tüm class mapping’lerini ve dosya istatistiklerini içeren rapor

---

## 📊 Örnek Mapping (çalışma sırasında gösterilir)

```text
header → fjdksa
content → uqpzmx
footer → ilxwbe
...
```

---

## ⚙️ Gereksinimler

* Python 3.6 veya üstü (standart kütüphaneler dışında bir bağımlılık yok)

---

## 📌 Uyarılar

* `node_modules`, `.git`, `backup_` klasörleri otomatik olarak atlanır.
* Çok kısa, sayıdan oluşan veya CSS anahtar kelimeleri içeren class isimleri yeniden adlandırılmaz.
* CSS bozulmalarına karşı güncellemeden sonra yapı doğrulaması yapılır, sorun olursa yedekten geri alınır.

---

## 👤 Geliştirici

**fastuptime**

🔗 GitHub: [https://github.com/fastuptime](https://github.com/fastuptime)
📫 İletişim: GitHub profilim üzerinden ulaşabilirsiniz

---

## 📝 Lisans

Bu proje MIT lisansı ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.
