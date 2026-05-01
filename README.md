
# 🎮 Akinator Clone (Guessing Game)

Questo progetto è un clone semplificato di Akinator basato su probabilità bayesiane.
Il sistema prova a indovinare il personaggio a cui stai pensando facendoti una serie di domande.
Non utilizza nessuna Intelligenza Artificiale, non gli serve... è già bravo così! 💅🏼  
Provalo!

---

## 🚀 Come avviare il gioco (Windows, macOS, Linux)

### 📦 Requisiti

* Python 3.8 o superiore
* pip installato
* (consigliato) ambiente virtuale

---

## 🪟 Windows

### 1. Apri il terminale (PowerShell o CMD)

### 2. Crea e attiva ambiente virtuale

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Avvia il gioco

```bash
python src\main\script.py
```

---

## 🍎 macOS

### 1. Apri il Terminale

### 2. Crea e attiva ambiente virtuale

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Avvia il gioco

```bash
python3 src/main/script.py
```

---

## 🐧 Linux

### 1. Apri il terminale

### 2. Crea e attiva ambiente virtuale

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Avvia il gioco

```bash
python src/main/script.py
```

---

## 🎯 Obiettivo del gioco

Il gioco cerca di indovinare il personaggio a cui stai pensando facendo domande a cui puoi rispondere.

Il sistema aggiorna continuamente le probabilità dei personaggi possibili fino a trovare quello più probabile.

---

## 🧠 Come rispondere alle domande

Durante il gioco ti verranno poste domande.

Devi rispondere usando UNA di queste opzioni:

* `s` → sì
* `ps` → più sì che no
* `non so` → non lo so / incerto
* `pn` → più no che sì
* `n` → no

Esempio:

```
Il personaggio è reale?
(s/ps/pn/n/non so): s
```

---

## 🧩 Come funziona il sistema

Il gioco usa un modello probabilistico (Bayes semplificato):

* Ogni personaggio ha una probabilità iniziale
* Ogni risposta aggiorna queste probabilità
* Il sistema sceglie le domande più informative (entropia minima)
* Quando la confidenza è alta, fa una “guess”

---

## 📁 Cos’è `data.json`

Il file `data.json` è il **database del gioco**.

Contiene tre sezioni principali:

### 1. `questions`

Lista delle domande che il sistema può fare:

```json
"questions": [
  "Il personaggio è reale?",
  "È un videogioco?",
  "È italiano?"
]
```

---

### 2. `characters`

Contiene i personaggi conosciuti e le loro risposte storiche.

Struttura:

```json
"characters": {
  "Mario": [
    {"yes": 10, "no": 2, "unknown": 1},
    {"yes": 3, "no": 8, "unknown": 2}
  ]
}
```

Ogni posizione della lista corrisponde a una domanda.

---

### 3. `stats`

Memorizza statistiche di apprendimento:

```json
"stats": {
  "Mario": {
    "times_seen": 5,
    "times_correct": 4
  }
}
```

Serve per migliorare le probabilità iniziali.

---

## 🧪 Modalità apprendimento

Se il gioco non indovina il personaggio:

* ti chiederà il nome corretto
* aggiornerà il dataset
* migliorerà le probabilità future

In questo modo il sistema “impara” giocando.

---

## ⚠️ Requisiti minimi

Il gioco NON parte se:

* `questions` è vuoto
* non esistono personaggi nel database

---

## 🔧 Struttura del progetto

```
Akinator/
│
├── resources/
│   └── data.json        # database del gioco
│
├── src/main/
│   └── script.py        # entry point
│
└── .venv/               # ambiente virtuale Python
```

---

## 💡 Suggerimenti

* Più giochi, più il sistema diventa preciso
* Più personaggi aggiungi, migliore diventa
* Le domande sono fondamentali: devono essere generiche e discriminanti

---

## 👤 Autore

Progetto creato da [Elio Magliari](https://eliomagliari.com/)

---
