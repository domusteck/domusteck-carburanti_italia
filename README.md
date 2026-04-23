<p align="center">
  <img src="custom_components/carburanti_italia/images/logo.png" alt="Domusteck Carburanti Italia Logo" width="300">
</p>

## 🚀 Carburanti Italia GPS Mod

Fork con:
- filtro GPS
- raggio dinamico
- ordinamento intelligente

# Carburanti Italia per Home Assistant
![GitHub Stars](https://img.shields.io/github/stars/domusteck/domusteck-carburanti_italia?style=social)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Maintainer](https://img.shields.io/badge/maintainer-Domusteck-blue.svg)](https://www.domusteck.it)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-blue.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=hdjweb@hotmail.it)

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
2. Copia la cartella `carburanti_italia
