# Offline Zpravodajský Portál (PWA + Flask + SQLite)

Kompletní a plně funkční webová aplikace, která shromažďuje aktuální zprávy z RSS kanálů a umožňuje jejich prohlížení v plnohodnotném offline režimu pomocí Service Workera a lokální databáze IndexedDB.

## Struktura projektu

- `backend.py`: Flask REST API server v Pythonu, který periodicky stahuje zprávy ze zdrojů v SQLite databázi.
- `news_database.db`: SQLite databáze uchovávající články a zdroje.
- `frontend/`:
  - `index.html`: Moderní responzivní rozhraní s podporou IndexedDB a detekcí stavu sítě.
  - `sw.js`: Service Worker pro cachování statických souborů webu.

## Instalace a spuštění

### Prerekvizity
Máte nainstalovaný Python verze 3.8+.

### 1. Krok: Instalace závislostí
V kořenovém adresáři spusťte:
```bash
pip install feedparser flask flask-cors
```

### 2. Krok: Spuštění backendu
Spusťte backendový server, který inicializuje databázi, provede první stažení článků a zpřístupní API:
```bash
python backend.py
```
Server poběží na adrese `http://localhost:5000`.

### 3. Krok: Spuštění frontendu
PWA aplikace vyžaduje pro bezpečné fungování Service Workera lokální server. Spusťte jej ve složce `frontend`:
```bash
cd frontend
python -m http.server 8000
```
Nyní v prohlížeči otevřete adresu **`http://localhost:8000`**.

## Testování offline režimu
1. Otevřete aplikaci na adrese `http://localhost:8000` s aktivním internetem (zprávy se poprvé stáhnou a uloží do IndexedDB).
2. Otevřete Vývojářské nástroje v prohlížeči (F12) -> záložka **Network** -> zaškrtněte možnost **Offline**.
3. Obnovte stránku (F5). Web se bez problému načte a zobrazí uložená data s indikací, že jste v offline režimu.
