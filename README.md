<p align="center">
  <img src="images/logo.png" alt="Domusteck Carburanti Italia Logo" width="300">
</p>

# Carburanti Italia per Home Assistant
![GitHub Stars](https://img.shields.io/github/stars/domusteck/domusteck-carburanti_italia?style=social)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Maintainer](https://img.shields.io/badge/maintainer-Domusteck-blue.svg)](https://www.domusteck.it)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-blue.svg)](mailto:hdjweb@hotmail.it)

Questa integrazione personalizzata permette di monitorare in tempo reale i prezzi dei carburanti (Benzina, Diesel, GPL, Metano) in Italia. I dati sono integrati per funzionare perfettamente con Home Assistant, permettendoti di trovare sempre il distributore più conveniente nella tua zona.

## ✨ Caratteristiche principali
* ⛽ **Copertura Nazionale**: Dati aggiornati sui prezzi dei carburanti in tutta Italia.
* 📊 **Sensori Dettagliati**: Monitoraggio per diverse tipologie di carburante e punti vendita.
* 🔄 **Efficienza**: Utilizzo del `DataUpdateCoordinator` per aggiornamenti costanti senza sovraccaricare il sistema.
* 🛠️ **Configurazione Semplice**: Supporto completo a `config_flow` per un'installazione guidata tramite interfaccia grafica.

## 🚀 Installazione

### Metodo 1: HACS (Consigliato)
1. Assicurati che [HACS](https://hacs.xyz/) sia installato.
2. Apri **HACS** > **Integrazioni**.
3. Clicca sui tre puntini in alto a destra e seleziona **Custom repositories**.
4. Inserisci l'URL: `https://github.com/domusteck/domusteck-carburanti_italia`
5. Seleziona la categoria **Integration** e clicca su **Add**.
6. Cerca "Carburanti Italia" nella lista e clicca su **Installa**.
7. Riavvia Home Assistant.

### Metodo 2: Manuale
1. Scarica l'archivio di questa repository.
2. Copia la cartella `carburanti_italia` (che trovi dentro `custom_components/`) nella cartella `custom_components/` del tuo Home Assistant.
3. Riavvia Home Assistant.

## ⚙️ Configurazione
Una volta installato e riavviato il sistema:
1. Vai in **Impostazioni** > **Dispositivi e servizi**.
2. Clicca su **Aggiungi integrazione**.
3. Cerca **"Carburanti Italia"** e inserisci i dati richiesti nella procedura guidata.

---

## ☕ Sostieni il progetto
Se trovi utile questa integrazione e vuoi sostenere lo sviluppo e il mantenimento dei servizi offerti da **Domusteck**, puoi offrirmi un caffè tramite PayPal. Il tuo supporto è fondamentale per mantenere il progetto aggiornato e gratuito per tutti!

<p align="left">
  <a href="mailto:hdjweb@hotmail.it">
    <img src="https://img.shields.io/badge/PayPal-Donate-blue.svg?style=for-the-badge&logo=paypal" alt="Donate with PayPal">
  </a>
</p>

---

## 📬 Supporto e Contatti
Hai riscontrato un problema o vuoi suggerire una funzione?
- **Sito Ufficiale**: [www.domusteck.it](https://www.domusteck.it)
- **Email**: [info@domusteck.it](mailto:info@domusteck.it)
- **GitHub**: Apri una [Issue](https://github.com/domusteck/domusteck-carburanti_italia/issues) se trovi un bug nel codice.

---
*Creato con passione da Domusteck. Se ti piace il mio lavoro, lascia una ⭐ su questa repository: aiuta il progetto a crescere e a raggiungere più utenti!*
