# AI Audio Mixer 🎵🤖

**AI Audio Mixer** è uno strumento pensato per musicisti e cantanti che vogliono personalizzare le tracce audio delle canzoni:

- **Suoni la batteria?** Ottieni la versione **drumless** della canzone o isola solo la traccia della **batteria**.  
- **Vuoi cantare o fare karaoke?** Rimuovi la voce principale per avere una traccia pronta al canto.

---

## Caratteristiche principali

- Scarica l’audio direttamente da YouTube in formato MP3.  
- Separa le tracce con **Demucs** (vocals, drums, bass, other).  
- Crea mix personalizzati: **Karaoke**, **Drumless**, **Drums only**.  
- Interfaccia semplice e interattiva tramite **ipywidgets**, pronta per Jupyter o Colab.  
- Ascolta subito il risultato nel notebook e salva il file nella cartella `output/`.

---

## Come usarlo

1. Apri il notebook in **Jupyter** o **Google Colab**.  
2. Inserisci il link di YouTube.  
3. Scegli il tipo di mix: **Karaoke**, **Drumless** o **Drums only**.  
4. Clicca su **Crea Mix Audio** e attendi il completamento.  

---

## Requisiti

- Python 3.8+  
- Jupyter Notebook o Google Colab  
- Connessione a Internet  

Le librerie necessarie vengono installate automaticamente:

```python
!pip install yt-dlp
!pip install demucs -q
!pip install pydub -q
````
