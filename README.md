# 🌍 Career AI Maps

Un'applicazione web intelligente per aiutare gli utenti a trovare la migliore offerta lavorativa nel mondo, considerando posizione, guadagni, costi di vita e distanza.

## 📌 Funzionalità

- Inserimento della propria posizione e preferenze (mobilità, tipo di lavoro, ecc.)
- Calcolo della distanza geografica verso possibili offerte di lavoro
- Visualizzazione delle migliori opportunità lavorative in base a un algoritmo A*
- Visualizzazione stile mappa (Leaflet)
- Dataset reali e simulati su offerte di lavoro, costi della vita e stipendi

## 🛠️ Tecnologie usate

- **Frontend**: HTML, JavaScript
- **Backend**: Python (Flask)
- **AI**: Algoritmo A* per la ricerca del lavoro migliore
- **Dati geografici**: geopy & leafletjs API https://leafletjs.com/
- **Elaborazione dati**: pandas
- **Dataset Jobs**: https://www.kaggle.com/datasets/ravindrasinghrana/job-description-dataset
- **Dataset Cost of Life**: https://www.kaggle.com/datasets/ankanhore545/cost-of-living-index-2022

## 📂 Struttura del progetto

        project/
        │
        ├── A*/ # Algoritmo di pathfinding A*
        │ └── pathfinding.py
        ├── templates/ # HTML pages (Flask) and JS into HTML
        ├── data/ # 🔽 Dataset (da scaricare e inserire manualmente)
        │ └── job_descriptions.csv
        ├── app.py # Applicazione principale Flask
        ├── requirements.txt
        └── README.md



## 📥 Dataset

Scarica i file necessari dal seguente link (Google Drive):

👉 [Scarica dataset](https://drive.google.com/drive/folders/1fud-aUBoIciJydLr25gSKKhCfPAWrvFf?usp=drive_link)

Una volta scaricato lo zip, estrai tutto nella **cartella `data/`** da creare nella root del progetto, accanto ad `app.py`.

## ▶️ Come eseguire

1. Clona il repository:
   ```bash
   git clone https://github.com/tuo-username/career-ai-maps.git
   cd career-ai-maps
   
2. Crea un ambiente virtuale (opzionale ma consigliato):

   ```bash
    python3 -m venv env
    source env/bin/activate  # o .\env\Scripts\activate su Windows
   
3. Installa le dipendenze:
    ```bash
    pip install -r requirements.txt


4. Avvia l'app:

    ```bash
    python app.py
    
5. Visita http://localhost:5000 nel browser.


# PRIMA DI USARLO LEGGERE ATTENTAMENTE:
Quando si va a creare un lavoro non è stato messo ancora alcun caricamento, pertanto si prega di aspettare.
Quando il lavoro sarà stato creato e metto nel dataset, la schermata del lavoro si risetterà cancellando tutti i dati inseriti
Quando ciò avviene significa che è stato caricato correttamente.
Per verificare andare nella schermata iniziale, dove c'è la mappa ed andare a scegliere un lavoro, il nuovo lavoro se non esisteva dovrebbe trovarsi in fondo alla pagina.

