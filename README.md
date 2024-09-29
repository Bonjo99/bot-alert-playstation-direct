# ALERT BOT PRODUCT AVAIABLE PLAYSTATION DIRECT

Questo bot controlla la disponibilità dei prodotti su PlayStation Direct e invia notifiche tramite WhatsApp o Telegram.

## Requisiti

- Python 3.x
- Google Chrome
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

## Installazione

1. **Clona il repository:**

    ```sh
    git clone https://github.com/tuo-username/alert-bot-playstation-direct.git
    cd alert-bot-playstation-direct
    ```

2. **Installa le dipendenze:**

    ```sh
    pip install -r requirements.txt
    ```

3. **Installa Tesseract OCR:**

    Scarica e installa Tesseract OCR dal [sito ufficiale](https://github.com/tesseract-ocr/tesseract). Dopo l'installazione, configura il percorso di Tesseract nel tuo script Python:

    ```python
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    ```