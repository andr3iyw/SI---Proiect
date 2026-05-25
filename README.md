# Documentație proiect - Sistem de gestiune criptografică

## 1. Scopul aplicației și arhitectura generală

Proiectul implementează un sistem de gestiune criptografică pentru importul, criptarea, decriptarea și monitorizarea performanței operațiilor efectuate asupra fișierelor. Aplicația permite lucrul cu mai multe algoritmi și framework-uri criptografice, stochează metadatele în MySQL și oferă atât o interfață CLI, cât și o interfață grafică realizată cu `customtkinter`.

Arhitectura este separată pe straturi:

- `models/` conține modelele de date folosite în aplicație: `Algorithm`, `Framework`, `FileRecord`, `KeyStorage`, `CryptoOperation`.
- `repository/` conține clasele care comunică direct cu baza de date: `FileRepository`, `KeyRepository`, `AlgorithmRepository`, `FrameworkRepository`, `OperationRepository`.
- `services/crypto_service.py` conține logica principală de criptare/decriptare, generarea cheilor, importul fișierelor și logarea metricilor.
- `db_info/` conține conexiunea la MySQL, scriptul de inițializare și schema DBML.
- `gui_app.py` implementează interfața grafică, iar `cli_menu.py` oferă o variantă simplă de operare din consolă.
- directoarele `files/`, `encrypted_files/`, `decrypted_files/` și `keys/` sunt folosite pentru stocarea fișierelor originale, criptate, decriptate și a cheilor.

Separarea pe repository-uri și servicii ajută la izolarea responsabilităților. Repository-urile execută operații CRUD și interogări SQL, în timp ce `CryptoService` orchestrează fluxul complet: citește fișierul și cheia, aplică algoritmul ales, scrie rezultatul pe disc și actualizează baza de date.

## 2. Algoritmii și framework-urile alese

### AES-256 în modul CBC

Pentru criptarea simetrică a fost ales algoritmul AES cu cheie de 256 biți, folosit în modul CBC. AES este potrivit pentru fișiere deoarece este rapid și eficient pentru volume mari de date. Modul CBC procesează datele în blocuri și necesită un vector de inițializare (`IV`) de 16 bytes. Pentru că AES lucrează cu blocuri fixe, datele sunt completate cu padding PKCS7 înainte de criptare și curățate prin unpadding la decriptare.

Implementarea AES este disponibilă în două framework-uri:

- Framework 1: biblioteca `cryptography`, prin wrapper-ul OpenSSL.
- Framework 2: `PyCryptodome`, ca implementare alternativă pentru comparație.

Porțiunea semnificativă pentru AES cu `cryptography` este:

```python
iv = os.urandom(16)
cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
encryptor = cipher.encryptor()

padder = padding.PKCS7(algorithms.AES.block_size).padder()
padded_data = padder.update(plaintext) + padder.finalize()
ciphertext = encryptor.update(padded_data) + encryptor.finalize()

with open(output_path, 'wb') as f:
    f.write(iv + ciphertext)
```

IV-ul este generat aleator la fiecare criptare și este salvat la începutul fișierului criptat. Această alegere simplifică decriptarea, deoarece metoda de decriptare citește primele 16 bytes ca IV și restul conținutului ca text criptat:

```python
with open(enc_path, 'rb') as f:
    iv = f.read(16)
    ciphertext = f.read()
```

Implementarea cu `PyCryptodome` păstrează aceeași logică, dar folosește API-ul specific bibliotecii:

```python
cipher = AES_PyCrypto.new(key_bytes, AES_PyCrypto.MODE_CBC)
iv = cipher.iv
padded_data = pad(plaintext, AES_PyCrypto.block_size)
ciphertext = cipher.encrypt(padded_data)
```

Această dublă implementare este utilă pentru comparații de performanță între framework-uri și pentru verificarea faptului că același algoritm poate fi integrat prin API-uri diferite.

### RSA-2048 cu OAEP și SHA-256

Pentru criptarea asimetrică a fost ales RSA cu chei de 2048 biți. RSA este folosit cu padding OAEP și SHA-256, ceea ce este mai sigur decât padding-ul clasic PKCS#1 v1.5. În aplicație, criptarea RSA necesită cheia publică, iar decriptarea necesită cheia privată. Această validare este făcută în metoda `execute_crypto_operation`, unde tipul cheii este verificat înainte de apelarea funcției concrete.

RSA nu este eficient pentru fișiere mari și nici nu poate cripta direct blocuri de orice dimensiune. Din acest motiv, implementarea citește fișierul în bucăți de 190 bytes la criptare, iar decriptarea citește blocuri criptate de 256 bytes, corespunzătoare unei chei RSA de 2048 biți:

```python
chunk_size = 190
with open(file_record['original_path'], "rb") as f_in, open(output_path, "wb") as f_out:
    while True:
        chunk = f_in.read(chunk_size)
        if not chunk:
            break
        encrypted_chunk = public_key.encrypt(
            chunk,
            rsa_padding.OAEP(
                mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        f_out.write(encrypted_chunk)
```

La decriptare se aplică operația inversă:

```python
chunk_size = 256
with open(enc_path, "rb") as f_in, open(output_path, "wb") as f_out:
    while True:
        chunk = f_in.read(chunk_size)
        if not chunk:
            break
        decrypted_chunk = private_key.decrypt(
            chunk,
            rsa_padding.OAEP(
                mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        f_out.write(decrypted_chunk)
```

Această abordare permite testarea RSA pe fișiere, deși în aplicații reale se preferă criptarea hibridă: fișierul este criptat cu AES, iar cheia AES este criptată cu RSA.

### PyNaCl SecretBox

Al treilea framework folosit este `PyNaCl`, care oferă `SecretBox`. Acesta este tot un mecanism simetric, dar diferă de AES-CBC prin faptul că include autentificarea mesajului. Cheia trebuie să aibă exact 32 bytes, iar biblioteca gestionează intern nonce-ul și formatul rezultatului criptat.

Fragmentul principal este:

```python
with open(key_record.key_path, 'rb') as kf:
    key_bytes = kf.read()

box = nacl.secret.SecretBox(key_bytes)
encrypted = box.encrypt(plaintext)
```

La decriptare, aceeași cheie este folosită pentru inițializarea `SecretBox`, iar metoda `decrypt` verifică și integritatea mesajului:

```python
box = nacl.secret.SecretBox(key_bytes)
plaintext = box.decrypt(encrypted_contents)
```

Integrarea PyNaCl a fost utilă pentru a compara o soluție care include autentificarea implicită cu variantele AES-CBC, unde integritatea trebuie tratată separat.

## 3. Detalii de implementare

Fluxul principal pornește din `execute_crypto_operation`. Metoda primește operația (`ENCRYPT` sau `DECRYPT`), fișierul, cheia și framework-ul selectat din interfață. În funcție de tipul cheii, alege automat algoritmul corect:

```python
key_record = self.key_repo.get_by_id(key_id)
if not key_record:
    raise ValueError("Cheia selectata nu exista in baza de date.")

if key_record.key_type == 'SYMMETRIC':
    if framework_id == 1:
        return self.encrypt_file_aes(file_id, key_id, 1)
    elif framework_id == 2:
        return self.encrypt_file_aes_pycrypto(file_id, key_id)
    elif framework_id == 3:
        return self.encrypt_file_nacl(file_id, key_id)
elif key_record.key_type in ['PUBLIC', 'PRIVATE']:
    ...
```

Această rutare face ca interfața să rămână simplă: utilizatorul selectează fișierul, cheia și framework-ul, iar serviciul decide ce funcție trebuie apelată.

Importul fișierelor este implementat prin copierea fișierului sursă în folderul `files/`, calcularea hash-ului SHA-256 și înregistrarea metadatelor în baza de date:

```python
filename = os.path.basename(source_path)
dest_path = os.path.join("files", filename)
shutil.copy2(source_path, dest_path)

file_hash = calculate_sha256(dest_path)

cursor.execute("""
    INSERT INTO files (original_name, original_path, file_extension, size_bytes, checksum, status)
    VALUES (%s, %s, %s, %s, %s, 'UPLOADED')
""", (filename, dest_path, ext, size, file_hash))
```

Calculul SHA-256 se face eficient, citind fișierul în blocuri de 4096 bytes:

```python
with open(filepath, "rb") as f:
    for byte_block in iter(lambda: f.read(4096), b""):
        sha256_hash.update(byte_block)
```

Generarea cheilor este inclusă tot în serviciu. Pentru AES se generează 32 bytes aleatori, iar pentru RSA se creează o pereche publică/privată de 2048 biți:

```python
if key_type == "AES":
    with open(key_path, "wb") as f:
        f.write(os.urandom(32))
elif key_type == "RSA":
    key = rsa.generate_private_key(65537, 2048)
```

După fiecare operație reușită se apelează `_log_complete`, care actualizează statusul fișierului, inserează o înregistrare în `crypto_operations` și salvează datele de performanță în `performance_metrics`:

```python
duration = int((time.time() - start_time) * 1000)
cpu_usage = psutil.cpu_percent(interval=None)
file_size = os.path.getsize(out_path)

cursor.execute("""
    INSERT INTO performance_metrics
    (operation_id, execution_time_ms, memory_usage_kb, cpu_usage_percent, file_size_bytes, notes)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (op_id, duration, final_memory_kb, cpu_usage, file_size, f"Framework: {fw_id}"))
```

Pentru memorie se folosește `tracemalloc`, iar valoarea salvată este vârful de consum în KB pentru operația curentă. Această informație este folosită ulterior în graficele din interfața grafică.

## 4. Modelul bazei de date

Baza de date `crypto_manager_db` este construită în jurul următoarelor tabele:

- `algorithms`: algoritmii disponibili, de exemplu AES și RSA.
- `frameworks`: framework-urile sau bibliotecile folosite pentru implementare.
- `keys_storage`: cheile disponibile, cu tip, dimensiune și cale pe disc.
- `files`: fișierele importate și statusul lor curent.
- `crypto_operations`: istoricul operațiilor de criptare/decriptare.
- `performance_metrics`: timpul, memoria, CPU-ul și dimensiunea rezultatului pentru fiecare operație.

Relațiile sunt definite prin chei străine. De exemplu, `crypto_operations` referă fișierul, algoritmul, cheia și framework-ul folosit, iar `performance_metrics` referă operația pentru care au fost colectate metricile. Această structură permite urmărirea completă a fiecărei operații și afișarea istoricului pentru un fișier.

Un exemplu de interogare relevantă este cea pentru statistici de performanță. Metoda `get_performance_stats` calculează media timpului și a memoriei pe framework, cu filtrarea valorilor foarte mari:

```sql
WITH RawAverages AS (
    SELECT op.framework_id,
           AVG(m.execution_time_ms) as raw_avg_time,
           AVG(m.memory_usage_kb) as raw_avg_mem
    FROM performance_metrics m
    JOIN crypto_operations op ON m.operation_id = op.id
    WHERE op.algorithm_id = %s
    GROUP BY op.framework_id
)
SELECT f.name,
       AVG(m.execution_time_ms) as avg_time,
       AVG(m.memory_usage_kb) as avg_mem
FROM performance_metrics m
JOIN crypto_operations op ON m.operation_id = op.id
JOIN frameworks f ON op.framework_id = f.id
JOIN RawAverages ra ON op.framework_id = ra.framework_id
WHERE op.algorithm_id = %s
  AND m.execution_time_ms <= (ra.raw_avg_time * 3)
  AND m.memory_usage_kb <= (ra.raw_avg_mem * 3)
GROUP BY f.name
```

Filtrarea valorilor care depășesc de trei ori media brută reduce influența outlierelor, de exemplu întârzieri cauzate de inițializarea bibliotecilor sau de accesul la disc.

## 5. Interfața aplicației și analiza performanței

Aplicația poate fi folosită în două moduri. `cli_menu.py` oferă un meniu simplu pentru listarea fișierelor, criptare, decriptare, import și generare de chei. Această variantă este utilă pentru testare rapidă și debugging.

Interfața principală este `gui_app.py`, construită cu `customtkinter`. Aceasta conține:

- un panou lateral cu acțiuni: import fișier, criptare, decriptare, generare chei, statistici;
- un explorator de fișiere care afișează statusul fiecărui fișier;
- o consolă de loguri pentru mesaje de succes sau eroare;
- ferestre modale pentru selecția fișierului, cheii și framework-ului;
- o fereastră de statistici care afișează grafice Matplotlib pentru timp mediu și consum mediu de memorie.

Pentru fiecare fișier se poate vizualiza istoricul ultimei criptări, inclusiv cheia, tipul cheii, framework-ul și data operației. Astfel, utilizatorul nu vede doar rezultatul de pe disc, ci și contextul operațional salvat în baza de date.

Graficele de performanță sunt construite pe baza datelor returnate de `get_performance_stats`. Interfața permite comutarea între AES și RSA printr-un control segmentat, iar pentru fiecare algoritm sunt afișate două grafice: timp mediu de execuție și consum mediu de memorie.

## 6. Dificultăți întâmpinate și soluții

O primă dificultate a fost gestionarea corectă a căilor către fișiere și chei. Datele inițiale din baza de date foloseau uneori căi cu `/` la început, de forma `/keys/aes_main.key`, ceea ce nu corespundea structurii locale a proiectului pe Windows. Pentru această problemă a fost adăugat scriptul `utils/fix_all_paths.py`, care elimină primul caracter `/` din câmpurile `key_path` și `original_path` acolo unde este cazul.

A doua dificultate a fost diferența dintre API-urile bibliotecilor criptografice. Deși AES-CBC este același concept, `cryptography` și `PyCryptodome` folosesc clase și funcții diferite pentru cipher, padding și IV. Implementarea a fost separată în metode distincte, astfel încât codul să rămână lizibil și să se poată măsura performanța fiecărui framework independent.

A treia dificultate a fost RSA pe fișiere. RSA nu poate cripta direct un fișier întreg, iar dimensiunea maximă a blocului depinde de cheia folosită și de padding. Pentru RSA-2048 cu OAEP-SHA256 s-a folosit o dimensiune conservatoare de 190 bytes la criptare și 256 bytes la decriptare. Această soluție funcționează pentru testare și comparație, dar are costuri de performanță mai mari decât AES.

O altă problemă a fost colectarea metricilor. Măsurarea memoriei procesului cu `psutil` poate include mult zgomot, deoarece include și memoria folosită de interpreter și biblioteci. Pentru operațiile criptografice s-a preferat `tracemalloc`, iar în baza de date se salvează vârful de memorie observat în timpul operației. Pentru timp se folosește diferența dintre `time.time()` la început și la final, convertită în milisecunde.

În final, integrarea GUI-ului cu baza de date a necesitat sincronizarea stării vizuale după fiecare operație. După import, criptare sau decriptare, lista de fișiere este reîncărcată prin `populate_file_explorer`, astfel încât statusul afișat să fie aliniat cu tabela `files`.

## 7. Concluzii

Proiectul oferă o aplicație completă pentru management criptografic la nivel educațional: importă fișiere, calculează hash-uri SHA-256, generează chei, criptează/decriptează cu mai multe biblioteci și salvează istoricul operațiilor. Alegerea AES-256-CBC este potrivită pentru fișiere datorită vitezei, RSA-2048 demonstrează criptarea asimetrică și diferența dintre cheia publică și cea privată, iar PyNaCl adaugă o variantă modernă de criptare simetrică autentificată.

Prin schema relațională și colectarea metricilor, aplicația nu se limitează la operația criptografică propriu-zisă, ci oferă și trasabilitate, istoric și comparații de performanță. Cele mai importante direcții de îmbunătățire ar fi folosirea criptării hibride pentru RSA, adăugarea autentificării pentru AES-CBC prin HMAC sau migrarea către AES-GCM, validări mai stricte pentru cheile PyNaCl și o gestionare mai sigură a cheilor stocate pe disc.
