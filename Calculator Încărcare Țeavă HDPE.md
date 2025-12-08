# **Arhitectura și Dezvoltarea Sistemului "Calculator Încărcare Țeavă HDPE"**

## **1\. Introducere și Definirea Contextului Operațional**

Industria logistică a materialelor de construcții, în special segmentul dedicat infrastructurii de apă și gaze, se confruntă cu o provocare unică: transportul elementelor voluminoase, dar cu densitate variabilă. Țevile din polietilenă de înaltă densitate (HDPE), esențiale pentru rețelele moderne de utilități, prezintă o problemă complexă de optimizare geometrică și masică. Solicitarea dumneavoastră de a dezvolta o aplicație dedicată, denumită "Calculator încărcare țeavă HDPE", răspunde unei nevoi critice de eficiență economică și conformitate legală. Obiectivul central al acestui sistem este maximizarea utilizării spațiului și a capacității de încărcare a camioanelor standard de 24 de tone, utilizând principiul "țeavă-în-țeavă" (cunoscut tehnic sub denumirea de telescopare sau *nesting*).

Prezentul raport oferă o analiză exhaustivă, structurată pe multiple dimensiuni—de la fizica materialelor și constrângerile geometrice, până la algoritmii de optimizare combinatorială și arhitectura software necesară. Vom explora în detaliu parametrii furnizați (SDR 26, 21, 17, 11\) și implicațiile lor asupra strategiei de încărcare, având în vedere lungimile variabile de 12m, 12.5m și 13m.

### **1.1. Problematica Transportului de HDPE: Volum vs. Masă**

În transportul rutier de mărfuri, eficiența este dictată de doi factori limitativi: volumul util al semiremorcii și masa maximă autorizată. Țevile HDPE prezintă o dualitate interesantă. Țevile cu pereți subțiri (SDR 26, PN6) au o densitate volumetrică scăzută; un camion plin cu astfel de țevi va atinge limita de volum mult înainte de a atinge limita de greutate de 24 de tone. În contrast, țevile cu pereți groși (SDR 11, PN16) au o masă liniară considerabilă; un camion va atinge limita de greutate având un volum ocupat de doar 30-40%.

Aplicația propusă trebuie să funcționeze ca un arbitru inteligent între aceste două extreme. Principiul telescopării permite transformarea spațiului gol din interiorul țevilor mari în spațiu util de marfă.1 Totuși, această operațiune nu este trivială. Introducerea unei țevi SDR 11 în interiorul unei țevi SDR 26 poate duce rapid la depășirea sarcinii pe osie sau la deformarea țevii exterioare. Prin urmare, algoritmul nu trebuie să caute doar "ce intră în ce", ci să echilibreze distribuția masei pe întreaga lungime a semiremorcii, respectând limitele legale din România și Uniunea Europeană.3

### **1.2. Obiectivele Raportului**

Acest document servește drept specificație funcțională și tehnică completă pentru echipa de dezvoltare, acoperind:

1. **Analiza Datelor de Intrare:** O disecție a tabelului de specificații furnizat pentru a stabili regulile de compatibilitate.  
2. **Fizica Telescopării:** Determinarea spațiilor de siguranță (*clearance*) necesare pentru a preveni blocarea țevilor, luând în considerare ovalitatea și toleranțele de producție.  
3. **Algoritmică:** Propunerea unei soluții hibride pentru problema "Bin Packing" cu constrângeri de includere (*nesting*).  
4. **Arhitectură Software:** Structura bazei de date, a interfeței utilizator și a logicii de backend.  
5. **Conformitate și Siguranță:** Integrarea normelor de transport și a măsurilor de siguranță în logica aplicației.

## ---

**2\. Analiza Materialului și Parametrizarea Inventarului**

Fundamentul oricărui calculator de încărcare este acuratețea datelor fizice. Setul de date furnizat include patru clase de presiune distincte (PN6, PN8, PN10, PN16), fiecare corespunzând unui Raport Standard Dimensional (SDR). Înțelegerea profundă a relației dintre acești parametri este vitală pentru scrierea codului de validare a încărcării.

### **2.1. Standard Dimension Ratio (SDR) și Implicațiile Structurale**

SDR-ul este definit ca raportul dintre diametrul exterior nominal ($D\_n$) și grosimea peretelui ($e\_n$): $SDR \= D\_n / e\_n$. Această valoare este invers proporțională cu grosimea peretelui și, implicit, cu rigiditatea inelară a țevii.

#### **Analiza Clasei SDR 26 (PN6)**

Țevile din această categorie (ex: TPE200/PN6) au pereții cei mai subțiri din setul de date. De exemplu, un diametru de 200mm are un perete de doar 7.7mm.

* **Comportament la Încărcare:** Aceste țevi sunt extrem de susceptibile la ovalizare (deformarea secțiunii transversale din cerc în elipsă) sub propria greutate sau sub greutatea stivei.5  
* **Constrângere Algoritmică:** Atunci când o țeavă SDR 26 este folosită ca "țeavă gazdă" (cea exterioară), aplicația trebuie să impună o marjă de siguranță (*gap*) mai mare pentru țeava interioară. Riscul ca o țeavă SDR 26 să se aplatizeze ușor și să blocheze țeava interioară este major. De asemenea, numărul de nivele de stivuire pentru SDR 26 trebuie limitat software pentru a preveni colapsul stivei de la bază.1

#### **Analiza Clasei SDR 11 (PN16)**

La polul opus, SDR 11 reprezintă țevile cele mai robuste. TPE200/PN16 are un perete de 18.2mm și o greutate de 10.57 kg/m, mai mult decât dublu față de varianta PN6 (4.73 kg/m).

* **Comportament la Încărcare:** Rigiditatea este excelentă, permițând stivuirea pe înălțimi mai mari fără risc de ovalizare semnificativă.  
* **Constrângere Algoritmică:** Limita principală devine masa. Încărcarea a 5 țevi TPE800 PN16 într-un camion poate epuiza capacitatea de 24 de tone înainte ca spațiul să fie plin. Aplicația trebuie să prioritizeze calculul masei cumulative în timp real. Mai mult, telescoparea în țevi SDR 11 reduce drastic sarcina utilă rămasă.

### **2.2. Normalizarea Datelor și Toleranțele de Fabricație**

Tabelul furnizat conține diametrul interior (DI) teoretic. Totuși, în realitate, țevile HDPE sunt produse conform standardelor precum ISO 4427 sau DIN 8074, care admit toleranțe.6 Diametrul exterior este controlat strict, dar grosimea peretelui poate varia pozitiv.

* **Regula de Siguranță:** Calculatorul nu trebuie să folosească DI-ul nominal exact pentru verificarea compatibilității. Trebuie aplicat un "Factor de Reducere a Spațiului" (Space Reduction Factor \- SRF).  
* Calculul DI Efectiv ($DI\_{eff}$):

  $$DI\_{eff} \= DI\_{tabel} \- (Toleranță\_{perete} \+ Ovalitate\_{transport})$$

  Analiza documentației tehnice sugerează că ovalitatea poate atinge 3-4% din diametru în timpul stocării și transportului.8 Prin urmare, pentru o țeavă de 500mm, ovalitatea poate reduce diametrul vertical cu 15-20mm. Ignorarea acestui aspect în software ar duce la generarea unor planuri de încărcare imposibil de executat fizic, unde țevile s-ar bloca la inserție.

### **2.3. Matricea de Masă Liniară**

Un element critic pentru algoritm este greutatea pe metru liniar. Datele furnizate arată variații enorme:

* TPE020/PN10: 0.07 kg/m (neglijabil pentru masa totală, relevant doar pentru manipulare).  
* TPE800/PN16: 168.7 kg/m.  
  * O singură țeavă de 13m TPE800/PN16 cântărește: $168.7 \\times 13 \= 2,193.1$ kg.  
  * Limita de 24.000 kg permite maxim 10 astfel de țevi într-un camion, fără a mai pune nimic altceva.  
  * Dacă utilizatorul dorește să introducă și țevi mai mici în interior, numărul țevilor mari trebuie redus drastic.

Acest contrast subliniază necesitatea unui algoritm care să nu funcționeze doar geometric (tetris), ci să fie guvernat strict de o funcție de cost bazată pe greutate.

## ---

**3\. Fizica Telescopării și Reguli de Compatibilitate**

Aplicația "Calculator încărcare țeavă HDPE" trebuie să simuleze realitatea fizică a inserției unei țevi cilindrice flexibile într-o altă țeavă cilindrică flexibilă. Aceasta nu este o simplă scădere a diametrelor.

### **3.1. Definirea Spațiului de Siguranță (Gap Clearance)**

Literatură de specialitate și ghidurile de bune practici în transportul țevilor indică faptul că un simplu "fit" matematic ($DI \> DE$) este insuficient. Factori precum curbura longitudinală a țevii (banana effect), cordoanele de sudură interioare (dacă există) și frecarea necesită un spațiu de manevră.10

Propunem implementarea în aplicație a următoarei formule dinamice pentru validarea telescopării:

$$Gap\_{min} (mm) \= C\_{bază} \+ (Factor\_{diametru} \\times DN\_{exterior})$$  
Unde:

* $C\_{bază}$ \= 15mm (spațiu minim absolut pentru manipulare și introducerea chingilor de tragere).  
* $Factor\_{diametru}$ \= 0.015 (1.5% din diametru pentru a compensa ovalitatea proporțională).

Exemplu de Validare Logică:  
Să analizăm posibilitatea introducerii unei țevi TPE315/PN6 într-o țeavă TPE400/PN6.

* **TPE400/PN6:** DI tabelar \= 369.40 mm.  
* **TPE315/PN6:** DE standard \= 315 mm.  
* **Spațiu Teoretic:** $369.40 \- 315 \= 54.4$ mm.  
* **Gap Necesar:** $15 \+ (0.015 \\times 400\) \= 15 \+ 6 \= 21$ mm.  
* **Decizie:** $54.4 \\ge 21$ \-\> **VALID**.

Să analizăm **TPE355/PN6** în **TPE400/PN6**.

* **TPE355/PN6:** DE standard \= 355 mm.  
* **Spațiu Teoretic:** $369.40 \- 355 \= 14.4$ mm.  
* **Gap Necesar:** 21 mm.  
* Decizie: $14.4 \< 21$ \-\> INVALID.  
  Deși matematic țeava de 355 intră în cea de 369, riscul de blocare este de 100% în condiții de șantier sau depozit, unde țevile nu sunt perfect rotunde sau drepte. Aplicația trebuie să respingă automat această combinație pentru a proteja utilizatorul de erori operaționale costisitoare.

### **3.2. Frecarea și Forțele de Extracție**

Un aspect adesea ignorat în softurile de încărcare este dificultatea descărcării. Coeficientul de frecare HDPE pe HDPE este de aproximativ 0.2 \- 0.3.12  
Dacă aplicația permite inserarea a 3 țevi grele într-una mare, greutatea cumulată poate face extragerea imposibilă fără echipamente speciale.

* **Limitare Software:** Aplicația va calcula greutatea totală a pachetului intern (*nested bundle*). Dacă greutatea pachetului intern depășește o limită configurabilă (de exemplu, 2000 kg), aplicația va afișa un avertisment: *"Atenție: Necesită echipament greu pentru extragere"*.

### **3.3. Limita de Niveluri de Telescopare**

Teoretic, putem avea o structură fractalică (DN32 în DN63 în DN110 în DN200 în DN400...). Practic, fiecare nivel adaugă complexitate logistică.

* **Recomandare:** Limitarea recursivității la maxim 3 sau 4 niveluri.  
* **Motivație:**  
  1. **Stabilitatea sarcinii:** Greutatea concentrată pe generatoarea inferioară a țevii de bază poate duce la fisurarea acesteia dacă sarcina internă este punctiformă.  
  2. **Timpul de manipulare:** Încărcarea și descărcarea devin exponențial mai lente cu fiecare nivel adăugat.

## ---

**4\. Arhitectura Algoritmică și Strategia de Optimizare**

Nucleul aplicației este motorul de calcul. Problema descrisă este o variantă complexă a problemei clasice de optimizare **"Knapsack Problem" (Rucsacul)** combinată cu **"Bin Packing Problem" (Împachetarea în containere)**, având constrângerea suplimentară de **"Nesting" (Includere)**. Deoarece acestea sunt probleme NP-hard (nu există o soluție analitică perfectă care să poată fi găsită instantaneu pentru seturi mari de date), vom utiliza abordări euristice avansate.13

### **4.1. Strategia "Matryoshka" (De jos în sus)**

În loc să încercăm să umplem camionul direct cu țevi individuale, algoritmul va funcționa în două etape majore:

1. **Etapa de Compunere a Pachetelor (Bundling):** Crearea unor "meta-obiecte" optimizate.  
2. **Etapa de Încărcare a Camionului (Packing):** Așezarea acestor meta-obiecte în spațiul limitat al camionului.

#### **Pasul 1: Generarea Pachetelor Optime**

Algoritmul va sorta lista de comandă descrescător după diametru.

1. Se ia cea mai mare țeavă disponibilă (ex: DN800). Aceasta devine "Containerul Gazdă".  
2. Se caută în restul listei cea mai mare țeavă care satisface condiția de Gap\_min (ex: DN630).  
3. Dacă se găsește, DN630 este "consumată" virtual și introdusă în DN800. Capacitatea de volum a DN800 devine 0, dar capacitatea de volum a DN630 este acum disponibilă.  
4. Se repetă recursiv pentru interiorul DN630.  
5. Procesul continuă până când nu mai există țevi compatibile sau s-a atins limita de niveluri.  
6. Rezultatul este un "Pachet Telescopat" (ex: {DN800 \+ DN630 \+ DN500}). Acest pachet are acum o greutate cumulată și dimensiunile exterioare ale țevii DN800.

**Notă privind clasele de presiune:** Algoritmul trebuie să fie agnostic la PN în faza de geometrie, dar strict în faza de greutate. O țeavă PN16 poate intra într-una PN6, și invers, atâta timp cât diametrele permit. Totuși, introducerea unei țevi PN16 grele într-una PN6 ușoară este riscantă pentru integritatea celei exterioare. Aplicația va prioritiza introducerea țevilor ușoare în cele grele, sau a celor cu SDR similar.

#### **Pasul 2: Încărcarea Camionului (First Fit Decreasing \- FFD)**

Având o listă de "Pachete Telescopate" și "Țevi Individuale" (care nu au putut fi telescopate), algoritmul trece la umplerea camioanelor.

1. Se deschide un "Camion Virtual" cu capacitate: Masă \= 24.000 kg, Volum \= $L \\times l \\times h$.  
2. Se selectează cel mai greu pachet din listă.  
3. Verificare Masă: $Masa\_{curentă} \+ Masa\_{pachet} \\le 24.000$?  
4. Verificare Spațiu: Există loc geometric în secțiunea transversală a camionului? (Aici se folosește un algoritm de împachetare a cercurilor în dreptunghi \- *Circle Packing in Rectangle*).  
5. Dacă ambele condiții sunt ADEVĂRAT, pachetul este adăugat.  
6. Dacă NU, se încearcă următorul pachet mai ușor.  
7. Dacă niciun pachet nu mai intră, se declară camionul "PLIN" și se deschide un nou camion.

### **4.2. Optimizarea Secțiunii Transversale (2D Packing)**

Utilizatorul a specificat "varianta optimă". Încărcarea țevilor în camion se poate face în două moduri geometrice principale 15:

1. **Aranjament Pătrat (Square Packing):** Țevile sunt una peste alta. Este mai puțin eficient spațial ($\\pi/4 \\approx 78.5\\%$ densitate maximă), dar necesită mai puțin efort de calare.  
2. **Aranjament Hexagonal (Staggered Packing):** Țevile de pe rândul superior stau în adânciturile rândului inferior. Este mult mai eficient ($\\approx 90\\%$ densitate), dar exercită presiuni laterale asupra prelatei camionului.

Specificație Aplicație: Calculatorul va folosi implicit Aranjamentul Hexagonal pentru maximizarea volumului, dar va verifica stabilitatea.  
Calculul înălțimii stivei ($H$) în aranjament hexagonal pentru $n$ rânduri de țevi cu diametrul $D$:

$$H \= D \+ (n-1) \\times D \\times \\frac{\\sqrt{3}}{2}$$

Această formulă va fi folosită pentru a verifica dacă stiva depășește înălțimea utilă a camionului (2.7m sau 3.0m pentru Mega).

## ---

**5\. Specificații Funcționale și Interfața Utilizator (UI/UX)**

Pentru a fi utilă, aplicația trebuie să fie intuitivă, ascunzând complexitatea calculelor matematice în spate.

### **5.1. Modulul de Intrare a Comenzii**

Interfața va fi de tip "Tabel Dinamic" (Grid), similară cu Excel, dar cu validare strictă.

* **Selector Lungime:** Dropdown global pentru comandă: \[12m | 12.5m | 13m\]. Modificarea acestui parametru va recalcula automat greutățile totale.  
* **Adăugare Linii:** Buton "+ Adaugă Produs".  
* **Coloane:**  
  * *Produs/Diametru (DN):* Dropdown cu funcție de căutare (ex: scrii "110" și filtrează toate variantele de 110).  
  * *Presiune (PN/SDR):* Dropdown dependent de DN. Dacă utilizatorul alege DN500, acest dropdown va arăta doar PN-urile disponibile pentru DN500 în baza de date.  
  * *Cantitate (buc):* Input numeric.  
  * *Lungime (Info):* Read-only, preia valoarea globală.  
  * *Greutate Totală (Info):* Calculat automat ($Cantitate \\times Greutate/m \\times Lungime$).

**Feature Critical:** Import CSV/Excel. Utilizatorii au adesea comenzile în sisteme ERP. Aplicația trebuie să permită upload-ul unui fișier simplu (DN, PN, Cantitate) pentru a popula lista instantaneu.17

### **5.2. Dashboard-ul de Rezultate**

După apăsarea butonului "Calculează Încărcare", utilizatorul va fi direcționat către un Dashboard vizual.

* **Rezumat Executiv:**  
  * Total Țevi: 450 buc.  
  * Greutate Totală Marfă: 58.4 tone.  
  * Camioane Necesare: 3 (2 x Full, 1 x Parțial).  
* **Vizualizarea Camioanelor (Tab-uri: Camion 1, Camion 2...):**  
  * *Grafic 3D/2D:* O reprezentare schematică a secțiunii camionului (vedere din spate). Cercurile (țevile) vor fi desenate la scară.  
  * *Codul Culorilor:* Țevile exterioare (gazdă) colorate în Gri, țevile telescopate nivel 1 în Albastru, nivel 2 în Verde.  
  * *Indicatori de Performanță:*  
    * Grad de încărcare Masă: 98% (23.520 kg / 24.000 kg).  
    * Grad de umplere Volum: 85%.  
    * Centrul de Greutate: 6.8m de la capul tractor (Verde \= Optim, Roșu \= Dezechilibrat).

### **5.3. Raportul de Încărcare (Output)**

Aplicația va genera un PDF detaliat pentru gestionarul depozitului ("Loading Ticket").  
Acesta nu va conține doar lista, ci și instrucțiuni de asamblare:  
**Instrucțiune Camion 1:**

1. Pregătiți 5 pachete de tip A: (TPE630/PN6 conține TPE400/PN10).  
2. Pregătiți 3 pachete de tip B: (TPE630/PN6 conține TPE315/PN6 \+ TPE110/PN6).  
3. Încărcați pachetele de tip A pe podea.  
4. Încărcați pachetele de tip B pe rândul 2\.  
   ...

Această abordare transformă aplicația dintr-un simplu calculator într-un asistent operațional.

## ---

**6\. Arhitectura Tehnică (Software Stack)**

Pentru a asigura performanța calculelor combinatoriale și scalabilitatea, recomandăm următorul stack tehnologic:

### **6.1. Backend (Logic & Database)**

* **Limbaj:** **Python**. Este standardul de aur pentru optimizare matematică.  
* **Framework:** **FastAPI** sau **Django**. FastAPI este preferat pentru viteza de execuție a API-urilor.  
* **Biblioteci Cheie:**  
  * NumPy: Pentru calcule matriceale rapide ale diametrelor și greutăților.  
  * Google OR-Tools sau PuLP: Pentru rezolvarea problemei de Bin Packing. Aceste biblioteci au solveri optimizați care pot gestiona constrângerile de masă și volum mult mai eficient decât un algoritm scris de la zero.18  
  * SciPy: Pentru calcule geometrice complexe (packing 2D).  
* **Baza de Date:** **PostgreSQL**. Robustă, capabilă să stocheze structuri JSON complexe (pentru planurile de încărcare salvate) și date relaționale (catalogul de țevi).

### **6.2. Frontend (Interfață)**

* **Framework:** **React.js** sau **Vue.js**. Permit o interfață reactivă, unde modificarea unei cantități actualizează instantaneu calculele vizuale.  
* **Vizualizare:** **Three.js** sau **D3.js**.  
  * *Three.js* permite randarea 3D a camionului, oferind o perspectivă realistă a modului în care țevile sunt așezate și telescopate. Utilizatorul poate roti camionul virtual pentru a inspecta încărcarea.17

### **6.3. Structura Bazei de Date (Schema Simplificată)**

SQL

TABLE PipeCatalog (  
    id SERIAL PRIMARY KEY,  
    code VARCHAR(50), \-- e.g., "TPE200/PN6/BR"  
    dn\_mm INTEGER,  
    pn\_class VARCHAR(10),  
    sdr INTEGER,  
    outer\_diameter\_mm DECIMAL(10,2),  
    wall\_thickness\_mm DECIMAL(10,2),  
    inner\_diameter\_nominal\_mm DECIMAL(10,2),  
    weight\_per\_meter DECIMAL(10,2)  
);

TABLE TruckConfigs (  
    id SERIAL PRIMARY KEY,  
    name VARCHAR(50), \-- e.g., "Mega Trailer RO"  
    max\_payload\_kg INTEGER DEFAULT 24000,  
    internal\_length\_mm INTEGER DEFAULT 13600,  
    internal\_width\_mm INTEGER DEFAULT 2480,  
    internal\_height\_mm INTEGER DEFAULT 3000  
);

## ---

**7\. Conformitatea cu Reglementările de Transport din România**

Un "calculator optim" care generează o încărcătură ilegală este inutil. Aplicația trebuie să integreze constrângerile legislației rutiere din România (OG 43/1997 republicată și normele CNAIR).

### **7.1. Distribuția Sarcinii pe Axe**

În România, limita de 40 de tone pentru ansamblu (Cap Tractor \+ Semiremorcă) nu este singura restricție. Există limite stricte pe axe 4:

* **Axa Motoare (Tractor):** Max 11.5 tone.  
* **Grupul de Axe Triplu (Semiremorcă):** Max 24 tone (8t \+ 8t \+ 8t).

Dacă aplicația încarcă toate țevile grele (pachetele telescopate dense) în partea din față a remorcii (spre capul tractor), riscă să depășească limita de 11.5t pe axa motoare, chiar dacă totalul mărfii este sub 24t.

* **Logicã de Securitate:** Algoritmul va încerca să distribuie greutatea uniform. Centrul de Greutate (CoG) al încărcăturii trebuie să cadă într-o zonă optimă, calculată geometric (de obicei la 6-7 metri de peretele frontal al remorcii). Aplicația va alerta utilizatorul dacă CoG-ul este prea în față sau prea în spate.

### **7.2. Asigurarea Încărcăturii (EN 12195\)**

Țevile HDPE sunt alunecoase. Telescoparea reduce frecarea totală a încărcăturii cu podeaua (deoarece mai puține țevi ating podeaua).

* **Recomandare în Aplicație:** Raportul final trebuie să includă o estimare a numărului minim de chingi de ancorare. Pentru o încărcătură de 24 de tone HDPE, standardul necesită o forță de pretensionare considerabilă. Aplicația poate sugera: *"Recomandat: 10-12 chingi de ancorare cu STF 500daN, plus covoare antiderapante sub țevile de bază"*.

## ---

**8\. Analiză de Caz și Scenarii de Utilizare**

Pentru a demonstra utilitatea algoritmului propus, vom analiza trei scenarii bazate pe inventarul dumneavoastră.

### **Scenariul A: Comanda Voluminoasă (Doar PN6)**

* **Comandă:** 2000 metri de TPE110/PN6.  
* **Date:** Greutate \= 1.42 kg/m. Total \= 2.840 kg.  
* **Analiză:** Masă neglijabilă (mult sub 24t). Problema este volumul.  
* **Soluție:** Aplicația va stivui hexagonal până la limita de înălțime a camionului. Nu este nevoie de telescopare, deoarece nu avem țevi mai mici sau mai mari în comandă. Camionul va fi "plin ochi" dar foarte ușor.

### **Scenariul B: Comanda Grea (Doar PN16)**

* **Comandă:** 150 metri de TPE800/PN16.  
* **Date:** Greutate \= 168.7 kg/m. Total \= 25.305 kg.  
* **Analiză:** Depășire masă 24t.  
* **Soluție:** Aplicația va împărți comanda în două camioane.  
  * Camion 1: \~140m (23.6 tone).  
  * Camion 2: \~10m (1.7 tone).  
  * **Notă:** Aici se observă ineficiența. Camionul 2 transportă "aer". Aplicația ar putea sugera utilizatorului: *"Mai aveți loc de 22 de tone în Camionul 2\. Doriți să adăugați alte produse din stoc pentru a optimiza transportul?"*

### **Scenariul C: Comanda Mixtă (Optimă pentru Telescopare)**

* **Comandă:**  
  * 60m TPE630/PN6 (Țevi gazdă).  
  * 120m TPE315/PN6.  
  * 300m TPE110/PN6.  
* **Soluție Algoritm:**  
  1. TPE630 este baza.  
  2. Introduce 2 x TPE315 în interiorul TPE630? Verificăm: ID 581mm. 2 x OD 315 \= 630mm. **NU**. Nu intră două una lângă alta. Intră doar una central.  
  3. Introduce 1 x TPE315 în TPE630.  
  4. Introduce 3-4 x TPE110 în interiorul TPE315? ID TPE315 \= 290mm. 3 x 110mm \= 330mm (triunghi). Nu intră. Intră 2 x TPE110 (220mm \< 290mm).  
  5. Restul de TPE110 sunt plasate în golurile dintre țevile mari TPE630 ("interstiții").  
* **Rezultat:** Reducerea volumului total cu peste 40% față de încărcarea vrac. Transformarea a ceea ce ar fi fost 2 camioane într-un singur camion bine optimizat.

## ---

**9\. Considerații Economice și ROI**

Implementarea acestei aplicații nu este doar un exercițiu tehnic, ci unul financiar.

* **Cost Transport:** Un camion pe ruta internă (ex: București \- Cluj) costă aproximativ 3000-4500 RON.  
* **Economie:** Dacă algoritmul reușește să condenseze marfa din 5 camioane în 4 camioane prin telescopare inteligentă, economia este directă (100% din costul celui de-al 5-lea camion).  
* **Cost Ascuns:** Telescoparea necesită manoperă suplimentară la încărcare (timp de stivuitorist). Aplicația poate avea un parametru "Cost per oră manipulare". Dacă telescoparea economisește 1000 RON din transport dar costă 200 RON în manoperă suplimentară, este rentabilă.

## **10\. Concluzii și Recomandări Finale**

Construcția aplicației "Calculator încărcare țeavă HDPE" este perfect realizabilă folosind tehnologiile actuale și datele standardizate furnizate. Cheia succesului nu stă în interfața grafică, ci în **robustețea motorului matematic de backend**.

Recomandăm:

1. **Prioritizarea Siguranței:** Utilizarea unor marje de toleranță (gap) conservatoare pentru a evita blocarea țevilor.  
2. **Validarea cu Operatorii:** Înainte de lansarea finală, planurile generate de soft trebuie testate fizic în curte pentru a calibra coeficienții de frecare și toleranțele reale.  
3. **Dezvoltare Iterativă:** Începeți cu un MVP (Minimum Viable Product) care optimizează doar greutatea și volumul simplu, apoi adăugați logica complexă de nesting recursiv.

Această unealtă digitală va deveni un avantaj competitiv major, transformând departamentul logistic dintr-un centru de cost într-un centru de eficiență operațională.

## **11\. Structura Proiectului**

Structura Propusă
TLC4Pipe/
│
├── 📁 docs/                                    # Nivel 1: Documentație
│   ├── 📁 architecture/                        # Nivel 2: Arhitectură tehnică
│   │   ├── database-schema.md
│   │   ├── api-design.md
│   │   └── algorithms.md
│   ├── 📁 business/                            # Nivel 2: Documentație business
│   │   ├── requirements.md
│   │   ├── use-cases.md
│   │   └── regulations/                        # Nivel 3: Reglementări transport
│   │       ├── romania-transport-rules.md
│   │       └── eu-weight-limits.md
│   ├── 📁 technical/                           # Nivel 2: Ghiduri tehnice
│   │   ├── hdpe-pipe-specs.md
│   │   ├── sdr-calculations.md
│   │   └── nesting-rules.md
│   └── 📁 user-guides/                         # Nivel 2: Ghiduri utilizator
│       ├── getting-started.md
│       └── loading-workflow.md
│
├── 📁 backend/                                 # Nivel 1: Backend Python
│   ├── 📁 app/                                 # Nivel 2: Aplicația principală
│   │   ├── __init__.py
│   │   ├── main.py                             # Entry point FastAPI
│   │   ├── config.py                           # Configurații
│   │   │
│   │   ├── 📁 api/                             # Nivel 3: Endpoints API
│   │   │   ├── __init__.py
│   │   │   ├── 📁 v1/                          # Nivel 4: Versiunea API
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── pipes.py                # CRUD țevi
│   │   │   │   │   ├── trucks.py               # Configurații camioane
│   │   │   │   │   ├── orders.py               # Comenzi
│   │   │   │   │   ├── calculations.py         # Calcule încărcare
│   │   │   │   │   └── reports.py              # Generare rapoarte
│   │   │   │   └── dependencies.py
│   │   │   └── schemas/                        # Pydantic schemas
│   │   │       ├── __init__.py
│   │   │       ├── pipe.py
│   │   │       ├── truck.py
│   │   │       ├── order.py
│   │   │       └── calculation.py
│   │   │
│   │   ├── 📁 core/                            # Nivel 3: Logica de bază
│   │   │   ├── __init__.py
│   │   │   ├── 📁 algorithms/                  # Nivel 4: Algoritmi optimizare
│   │   │   │   ├── __init__.py
│   │   │   │   ├── bin_packing.py              # First Fit Decreasing
│   │   │   │   ├── nesting.py                  # Telescopare (Matryoshka)
│   │   │   │   ├── circle_packing.py           # Împachetare 2D cercuri
│   │   │   │   └── weight_optimizer.py         # Optimizare greutate
│   │   │   ├── 📁 calculators/                 # Nivel 4: Calcule fizice
│   │   │   │   ├── __init__.py
│   │   │   │   ├── gap_clearance.py            # Calcul spațiu siguranță
│   │   │   │   ├── weight_calculator.py        # Calcul greutăți
│   │   │   │   ├── ovality_calculator.py       # Calcul ovalitate
│   │   │   │   └── axle_distribution.py        # Distribuție sarcină axe
│   │   │   ├── 📁 validators/                  # Nivel 4: Validări
│   │   │   │   ├── __init__.py
│   │   │   │   ├── nesting_validator.py        # Validare telescopare
│   │   │   │   ├── weight_validator.py         # Validare limite greutate
│   │   │   │   └── transport_compliance.py     # Conformitate transport
│   │   │   └── 📁 geometry/                    # Nivel 4: Geometrie
│   │   │       ├── __init__.py
│   │   │       ├── hexagonal_packing.py        # Aranjament hexagonal
│   │   │       ├── stacking_calculator.py      # Calcul înălțime stivă
│   │   │       └── center_of_gravity.py        # Centru de greutate
│   │   │
│   │   ├── 📁 models/                          # Nivel 3: Modele SQLAlchemy
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── pipe_catalog.py
│   │   │   ├── truck_config.py
│   │   │   ├── order.py
│   │   │   ├── loading_plan.py
│   │   │   └── nested_bundle.py
│   │   │
│   │   ├── 📁 services/                        # Nivel 3: Servicii business
│   │   │   ├── __init__.py
│   │   │   ├── pipe_service.py
│   │   │   ├── truck_service.py
│   │   │   ├── order_service.py
│   │   │   ├── loading_service.py              # Orchestrare calcul încărcare
│   │   │   └── report_service.py               # Generare PDF
│   │   │
│   │   ├── 📁 repositories/                    # Nivel 3: Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── pipe_repository.py
│   │   │   ├── truck_repository.py
│   │   │   └── order_repository.py
│   │   │
│   │   └── 📁 utils/                           # Nivel 3: Utilități
│   │       ├── __init__.py
│   │       ├── constants.py                    # SDR, PN, constante fizice
│   │       ├── converters.py                   # Conversii unități
│   │       └── csv_parser.py                   # Import CSV/Excel
│   │
│   ├── 📁 database/                            # Nivel 2: Bază de date
│   │   ├── 📁 migrations/                      # Nivel 3: Alembic migrations
│   │   │   ├── env.py
│   │   │   ├── versions/                       # Nivel 4: Versiuni migrări
│   │   │   │   └── .gitkeep
│   │   │   └── alembic.ini
│   │   ├── 📁 seeds/                           # Nivel 3: Date inițiale
│   │   │   ├── pipe_catalog_seed.py
│   │   │   └── truck_configs_seed.py
│   │   └── connection.py
│   │
│   ├── 📁 tests/                               # Nivel 2: Teste backend
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── 📁 unit/                            # Nivel 3: Teste unitare
│   │   │   ├── 📁 algorithms/                  # Nivel 4
│   │   │   │   ├── test_bin_packing.py
│   │   │   │   ├── test_nesting.py
│   │   │   │   └── test_circle_packing.py
│   │   │   ├── 📁 calculators/                 # Nivel 4
│   │   │   │   ├── test_gap_clearance.py
│   │   │   │   └── test_weight_calculator.py
│   │   │   └── 📁 validators/                  # Nivel 4
│   │   │       ├── test_nesting_validator.py
│   │   │       └── test_weight_validator.py
│   │   ├── 📁 integration/                     # Nivel 3: Teste integrare
│   │   │   ├── test_loading_flow.py
│   │   │   └── test_api_endpoints.py
│   │   └── 📁 fixtures/                        # Nivel 3: Date test
│   │       ├── sample_orders.json
│   │       └── expected_results.json
│   │
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── pyproject.toml
│
├── 📁 frontend/                                # Nivel 1: Frontend React
│   ├── 📁 public/                              # Nivel 2: Fișiere publice
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── 📁 assets/                          # Nivel 3: Resurse statice
│   │       └── 📁 images/                      # Nivel 4
│   │           ├── logo.svg
│   │           └── truck-icon.svg
│   │
│   ├── 📁 src/                                 # Nivel 2: Cod sursă
│   │   ├── index.js
│   │   ├── App.jsx
│   │   │
│   │   ├── 📁 components/                      # Nivel 3: Componente React
│   │   │   ├── 📁 common/                      # Nivel 4: Componente comune
│   │   │   │   ├── Button/
│   │   │   │   │   ├── Button.jsx
│   │   │   │   │   └── Button.css
│   │   │   │   ├── Input/
│   │   │   │   ├── Dropdown/
│   │   │   │   ├── Modal/
│   │   │   │   └── Table/
│   │   │   ├── 📁 order/                       # Nivel 4: Modul comenzi
│   │   │   │   ├── OrderForm/
│   │   │   │   │   ├── OrderForm.jsx
│   │   │   │   │   └── OrderForm.css
│   │   │   │   ├── OrderGrid/
│   │   │   │   ├── PipeSelector/
│   │   │   │   └── FileImport/
│   │   │   ├── 📁 visualization/               # Nivel 4: Vizualizare 3D
│   │   │   │   ├── TruckView3D/
│   │   │   │   │   ├── TruckView3D.jsx
│   │   │   │   │   └── TruckView3D.css
│   │   │   │   ├── CrossSectionView/
│   │   │   │   ├── PipeBundle/
│   │   │   │   └── ColorLegend/
│   │   │   ├── 📁 dashboard/                   # Nivel 4: Dashboard
│   │   │   │   ├── SummaryCards/
│   │   │   │   ├── LoadingIndicators/
│   │   │   │   ├── TruckTabs/
│   │   │   │   └── CenterOfGravityIndicator/
│   │   │   └── 📁 reports/                     # Nivel 4: Rapoarte
│   │   │       ├── LoadingReport/
│   │   │       ├── InstructionsList/
│   │   │       └── PDFExport/
│   │   │
│   │   ├── 📁 pages/                           # Nivel 3: Pagini aplicație
│   │   │   ├── HomePage/
│   │   │   │   ├── HomePage.jsx
│   │   │   │   └── HomePage.css
│   │   │   ├── OrderEntryPage/
│   │   │   ├── ResultsDashboard/
│   │   │   ├── SettingsPage/
│   │   │   └── ReportPage/
│   │   │
│   │   ├── 📁 hooks/                           # Nivel 3: Custom hooks
│   │   │   ├── useOrders.js
│   │   │   ├── useCalculation.js
│   │   │   ├── useTruckConfig.js
│   │   │   └── usePipeCatalog.js
│   │   │
│   │   ├── 📁 services/                        # Nivel 3: API services
│   │   │   ├── api.js                          # Axios instance
│   │   │   ├── pipeService.js
│   │   │   ├── orderService.js
│   │   │   ├── calculationService.js
│   │   │   └── reportService.js
│   │   │
│   │   ├── 📁 store/                           # Nivel 3: State management
│   │   │   ├── index.js
│   │   │   ├── 📁 slices/                      # Nivel 4: Redux slices
│   │   │   │   ├── orderSlice.js
│   │   │   │   ├── pipeSlice.js
│   │   │   │   ├── truckSlice.js
│   │   │   │   └── calculationSlice.js
│   │   │   └── 📁 selectors/                   # Nivel 4
│   │   │       ├── orderSelectors.js
│   │   │       └── calculationSelectors.js
│   │   │
│   │   ├── 📁 utils/                           # Nivel 3: Utilități frontend
│   │   │   ├── formatters.js
│   │   │   ├── validators.js
│   │   │   └── constants.js
│   │   │
│   │   └── 📁 styles/                          # Nivel 3: Stiluri globale
│   │       ├── index.css
│   │       ├── variables.css
│   │       └── themes/                         # Nivel 4: Teme
│   │           ├── light.css
│   │           └── dark.css
│   │
│   ├── 📁 tests/                               # Nivel 2: Teste frontend
│   │   ├── 📁 unit/                            # Nivel 3
│   │   │   └── components/                     # Nivel 4
│   │   ├── 📁 integration/                     # Nivel 3
│   │   └── 📁 e2e/                             # Nivel 3: Playwright/Cypress
│   │
│   ├── package.json
│   └── vite.config.js
│
├── 📁 shared/                                  # Nivel 1: Resurse partajate
│   ├── 📁 data/                                # Nivel 2: Date statice
│   │   ├── pipe_catalog.json                   # Catalogul complet țevi
│   │   ├── truck_specifications.json           # Specificații camioane
│   │   └── 📁 sdr-tables/                      # Nivel 3: Tabele SDR
│   │       ├── sdr11.json
│   │       ├── sdr17.json
│   │       ├── sdr21.json
│   │       └── sdr26.json
│   ├── 📁 types/                               # Nivel 2: Tipuri TypeScript/JSON Schema
│   │   ├── pipe.schema.json
│   │   ├── order.schema.json
│   │   └── calculation-result.schema.json
│   └── 📁 constants/                           # Nivel 2: Constante partajate
│       ├── transport-limits.json               # Limite legale transport
│       ├── physical-constants.json             # Coeficienți frecare, etc.
│       └── safety-margins.json                 # Marje siguranță
│
├── 📁 scripts/                                 # Nivel 1: Scripturi utilitate
│   ├── 📁 setup/                               # Nivel 2: Configurare
│   │   ├── init-db.sh
│   │   └── seed-data.py
│   ├── 📁 build/                               # Nivel 2: Build & Deploy
│   │   ├── build-frontend.sh
│   │   └── docker-build.sh
│   └── 📁 analysis/                            # Nivel 2: Analiză date
│       ├── generate_pipe_data.py               # Generare date din tabel original
│       └── validate_catalog.py
│
├── 📁 docker/                                  # Nivel 1: Containerizare
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
│
├── 📁 .github/                                 # Nivel 1: GitHub Actions
│   └── 📁 workflows/                           # Nivel 2
│       ├── ci.yml
│       ├── deploy.yml
│       └── tests.yml
│
├── .gitignore
├── README.md
├── LICENSE
└── Makefile

Descrierea Componentelor Cheie

1. Backend (/backend)
Director	Scop
app/core/algorithms/	Algoritmi de optimizare: Bin Packing FFD, Telescopare Matryoshka, Circle Packing 2D
app/core/calculators/	Calcule fizice: gap clearance, greutăți, ovalitate, distribuție sarcină
app/core/validators/	Validări: compatibilitate telescopare, limite greutate, conformitate legală
app/core/geometry/	Geometrie: aranjament hexagonal, înălțime stivă, centru de greutate
app/services/	Orchestrare business logic și generare rapoarte PDF

2. Frontend (/frontend)
Director	Scop
components/order/	Componente pentru introducerea comenzii (tabel dinamic, import CSV)
components/visualization/	Vizualizare 3D cu Three.js (camion, secțiune transversală)
components/dashboard/	Dashboard rezultate (indicatori, tabs camioane)
pages/	Pagini principale ale aplicației

3. Shared (/shared)
Director	Scop
data/	Catalogul complet țevi HDPE, specificații camioane
constants/	Limite legale transport RO/EU, constante fizice, marje siguranță



#### **Lucrări citate**

1. Eiffel 101: HDPE Receiving and Handling Guide, accesată pe decembrie 5, 2025, [https://www.eiffeltrading.com/blog/post/eiffel-101-hdpe-receiving-and-handling-guide/](https://www.eiffeltrading.com/blog/post/eiffel-101-hdpe-receiving-and-handling-guide/)  
2. The Plastics Pipe Institute Handbook of Polyethylene Pipe \- us fusion, accesată pe decembrie 5, 2025, [https://usfusion.com/wp-content/uploads/2021/07/USF-The-Plastics-Pipe-Institute-Handbook-Polyethylene-Pipe.pdf](https://usfusion.com/wp-content/uploads/2021/07/USF-The-Plastics-Pipe-Institute-Handbook-Polyethylene-Pipe.pdf)  
3. DIMENSIONS MAXIMALES AUTORISES EN EUROPE, accesată pe decembrie 5, 2025, [https://www.itf-oecd.org/sites/default/files/docs/dimensions-2021.pdf](https://www.itf-oecd.org/sites/default/files/docs/dimensions-2021.pdf)  
4. Romania \- International Transport Forum (ITF), accesată pe decembrie 5, 2025, [https://www.itf-oecd.org/road-transport-group/weights-and-dimensions/romania](https://www.itf-oecd.org/road-transport-group/weights-and-dimensions/romania)  
5. HDPE PE100 & PE100-RC Pipe: Properties and Types \- PE100+ Association, accesată pe decembrie 5, 2025, [https://www.pe100plus.com/PE-Pipes/Technical-guidance/model/Materials/mrs/HDPE-PE100-PE100-RC-Pipe-Properties-and-Types-i4007.html](https://www.pe100plus.com/PE-Pipes/Technical-guidance/model/Materials/mrs/HDPE-PE100-PE100-RC-Pipe-Properties-and-Types-i4007.html)  
6. Polyethylene (PE) pipes, accesată pe decembrie 5, 2025, [http://mesener.com.tr/Uploads/files/DIN\_8074.pdf](http://mesener.com.tr/Uploads/files/DIN_8074.pdf)  
7. Din 8074 1999 | PDF | Pipe (Fluid Conveyance) | Engineering Tolerance \- Scribd, accesată pe decembrie 5, 2025, [https://www.scribd.com/document/717060186/DIN-8074-1999](https://www.scribd.com/document/717060186/DIN-8074-1999)  
8. Custom Size PE Pipes \- Mill-Pro, accesată pe decembrie 5, 2025, [https://www.mill-pro.com.hk/water/pipes/custom-size-pe-pipes/](https://www.mill-pro.com.hk/water/pipes/custom-size-pe-pipes/)  
9. INTERNATIONAL STANDARD ISO 4427-2, accesată pe decembrie 5, 2025, [https://cdn.standards.iteh.ai/samples/72184/609da055d422425c8ee69547f924e7cd/ISO-4427-2-2019.pdf](https://cdn.standards.iteh.ai/samples/72184/609da055d422425c8ee69547f924e7cd/ISO-4427-2-2019.pdf)  
10. Close-Fit Lining: Die Drawing \- HDPE pipe systems (plastic & polyethylene pipe), accesată pe decembrie 5, 2025, [https://www.pe100plus.com/PE-Pipes/Technical-guidance/Trenchless/Methods/Pipe-Rehabilitation/Close-Fit-Lining-Die-Drawing-i1312.html](https://www.pe100plus.com/PE-Pipes/Technical-guidance/Trenchless/Methods/Pipe-Rehabilitation/Close-Fit-Lining-Die-Drawing-i1312.html)  
11. 49 CFR § 195.250 \- Clearance between pipe and underground structures., accesată pe decembrie 5, 2025, [https://www.law.cornell.edu/cfr/text/49/195.250](https://www.law.cornell.edu/cfr/text/49/195.250)  
12. What is the coefficient of friction of an HDPE Puddle Flange? \- Blog \- DACHENG, accesată pe decembrie 5, 2025, [https://www.dachengplastic.com/blog/what-is-the-coefficient-of-friction-of-an-hdpe-puddle-flange-895364.html](https://www.dachengplastic.com/blog/what-is-the-coefficient-of-friction-of-an-hdpe-puddle-flange-895364.html)  
13. Bin packing problem \- Wikipedia, accesată pe decembrie 5, 2025, [https://en.wikipedia.org/wiki/Bin\_packing\_problem](https://en.wikipedia.org/wiki/Bin_packing_problem)  
14. formulation for nested binpacking problem \- Operations Research Stack Exchange, accesată pe decembrie 5, 2025, [https://or.stackexchange.com/questions/12834/formulation-for-nested-binpacking-problem](https://or.stackexchange.com/questions/12834/formulation-for-nested-binpacking-problem)  
15. Optimal Packing \- DataGenetics, accesată pe decembrie 5, 2025, [http://datagenetics.com/blog/june32014/index.html](http://datagenetics.com/blog/june32014/index.html)  
16. When is hexagonal stacking of circles more efficient? : r/askmath \- Reddit, accesată pe decembrie 5, 2025, [https://www.reddit.com/r/askmath/comments/wv7o3j/when\_is\_hexagonal\_stacking\_of\_circles\_more/](https://www.reddit.com/r/askmath/comments/wv7o3j/when_is_hexagonal_stacking_of_circles_more/)  
17. Load efficiently with the container loading software EasyCargo, accesată pe decembrie 5, 2025, [https://www.easycargo3d.com/en/](https://www.easycargo3d.com/en/)  
18. Thinking Inside the Box: How to Solve the Bin Packing Problem with Ray on Databricks, accesată pe decembrie 5, 2025, [https://www.databricks.com/blog/thinking-inside-box-how-solve-bin-packing-problem-ray-databricks](https://www.databricks.com/blog/thinking-inside-box-how-solve-bin-packing-problem-ray-databricks)  
19. The Bin Packing Problem | OR-Tools \- Google for Developers, accesată pe decembrie 5, 2025, [https://developers.google.com/optimization/pack/bin\_packing](https://developers.google.com/optimization/pack/bin_packing)  
20. 3D Load Planning with our Supply Chain Solution \- YouTube, accesată pe decembrie 5, 2025, [https://www.youtube.com/watch?v=2Q6d5ynxuqc](https://www.youtube.com/watch?v=2Q6d5ynxuqc)  
21. Maximum permitted weights and dimensions, goods transport \- UNTRR, accesată pe decembrie 5, 2025, [https://www.untrr.ro/media/wysiwyg/maximum-permitted-weights-and-dimensions-goods-transport-romania-136243122545bf139ba419f9434b5ee2a42eb7aaee.pdf](https://www.untrr.ro/media/wysiwyg/maximum-permitted-weights-and-dimensions-goods-transport-romania-136243122545bf139ba419f9434b5ee2a42eb7aaee.pdf)