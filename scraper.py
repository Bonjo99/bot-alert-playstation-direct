import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image
import pytesseract

# Configura il percorso di Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def send_whatsapp_message(driver, message, phone_number):
    driver.get(f"https://web.whatsapp.com/send?phone={phone_number}&text={message}")
    time.sleep(15)  # Attendi che WhatsApp Web si carichi e il messaggio venga preparato
    send_button = driver.find_element(By.XPATH, "//span[@data-icon='send']")
    send_button.click()

def send_telegram_message(driver, message):
    time.sleep(5)  # Attendi che la chat si carichi
    message_box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
    message_box.send_keys(message)
    message_box.send_keys(Keys.RETURN)

def select_platform():
    global platform
    platform = None
    def set_platform(selected_platform):
        global platform
        platform = selected_platform
        platform_window.destroy()

    platform_window = tk.Toplevel(root)
    platform_window.title("Seleziona Piattaforma")
    tk.Label(platform_window, text="Seleziona la piattaforma per inviare il messaggio:").pack(pady=10)
    tk.Button(platform_window, text="WhatsApp", command=lambda: set_platform("WhatsApp")).pack(side=tk.LEFT, padx=20, pady=20)
    tk.Button(platform_window, text="Telegram", command=lambda: set_platform("Telegram")).pack(side=tk.RIGHT, padx=20, pady=20)
    platform_window.wait_window()

def show_overlay_message(text, duration=2000):
    overlay = tk.Toplevel()
    overlay.overrideredirect(True)  # Rimuovi il bordo della finestra
    overlay.attributes('-topmost', True)  # Mantieni la finestra in primo piano
    overlay.attributes('-alpha', 0.8)  # Imposta la trasparenza della finestra

    # Ottieni le dimensioni dello schermo
    screen_width = overlay.winfo_screenwidth()
    screen_height = overlay.winfo_screenheight()

    # Configura il contenuto e la posizione della finestra
    label = tk.Label(overlay, text=text, font=("Helvetica", 16), bg="yellow", fg="black")
    label.pack(ipadx=10, ipady=5)
    
    # Centra la finestra sullo schermo
    overlay_width = label.winfo_reqwidth()
    overlay_height = label.winfo_reqheight()
    x = (screen_width - overlay_width) // 2
    y = (screen_height - overlay_height) // 2
    overlay.geometry(f"{overlay_width}x{overlay_height}+{x}+{y}")

    # Distruggi la finestra dopo un certo tempo
    overlay.after(duration, overlay.destroy)


def wait_for_chat_selection(driver):
    previous_chat_title = None

    try:
        # Prova a ottenere il titolo della chat prima che l'utente selezioni una chat
        previous_chat_title = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div[4]/div/header/div[2]/div/div').text
    except NoSuchElementException:
        pass

    messagebox.showinfo("Seleziona Chat", "Seleziona la chat della persona, gruppo o canale su WhatsApp e premi OK per continuare.")

    # Attendi che il titolo della chat cambi, segno che l'utente ha selezionato una chat
    while True:
        try:
            current_chat_title = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div[4]/div/header/div[2]/div/div').text
            if current_chat_title != previous_chat_title:
                break
        except NoSuchElementException:
            pass
        time.sleep(1)

    show_overlay_message("Chat selezionata", duration=3000)

def get_whatsapp_phone_number(driver):
    try:
        # Attendi che l'elemento sia presente
        time.sleep(2)
        contact = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div[4]/div/header/div[2]/div/div')
        contact.click()
        time.sleep(2)  # Attendi che il popup si apra
        phone_number = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div[5]/span/div/span/div/div/section/div[1]/div[2]/div/span/span').text
        return phone_number
    except NoSuchElementException:
        print("Impossibile trovare il numero di telefono.")
        return None

# Funzione per avviare il controllo della disponibilità dei prodotti
def start_check():
    # Chiedi all'utente di inserire i link dei prodotti
    product_links = simpledialog.askstring("Input", "Inserisci i link dei prodotti separati da una virgola:")
    
    if not product_links:
        messagebox.showerror("Errore", "I link dei prodotti non possono essere vuoti.")
        return
    
    # Chiedi all'utente di selezionare la piattaforma
    select_platform()
    if platform not in ["WhatsApp", "Telegram"]:
        messagebox.showerror("Errore", "Piattaforma non valida. Inserisci 'WhatsApp' o 'Telegram'.")
        return
    
    # Impostazione del driver visibile per la scansione del QR code
    visible_options = webdriver.ChromeOptions()
    visible_driver = webdriver.Chrome(options=visible_options)
    
    # Naviga alla piattaforma selezionata per la scansione del QR code
    if platform == "WhatsApp":
        visible_driver.get("https://web.whatsapp.com")
        messagebox.showinfo("QR Code", "Scansiona il codice QR di WhatsApp e premi OK per continuare.")
        # Attendi che l'elemento della chat diventi visibile
        try:
            WebDriverWait(visible_driver, 25).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[2]/div[3]/header/header/div/div[1]/h1'))
            )
        except TimeoutException:
            messagebox.showerror("Errore", "Tempo scaduto per la scansione del QR code.")
            visible_driver.quit()
            return
        # Chiedi all'utente di selezionare la chat della persona, gruppo o canale
        #MDOFICA
        wait_for_chat_selection(visible_driver)
        if messagebox.askokcancel("Conferma", "Sei sicuro di voler mandare il messaggio a questa persona/gruppo? Clicca OK per confermare."):
            phone_number = get_whatsapp_phone_number(visible_driver)
            if phone_number:
                print(f"Numero di telefono: {phone_number}")
            else:
                messagebox.showerror("Errore", "Impossibile trovare il numero di telefono.")
                return
        else:
            messagebox.showinfo("Annullato", "Operazione annullata dall'utente.")
            return

    elif platform == "Telegram":
        # Impostazione del driver visibile per la scansione del QR code
        telegram_driver = webdriver.Chrome()
        
        # Naviga a Telegram Web per la scansione del QR code
        telegram_driver.get("https://web.telegram.org")
        messagebox.showinfo("QR Code", "Scansiona il codice QR di Telegram e premi OK per continuare.")
        
        # Chiedi all'utente di selezionare la chat della persona, gruppo o canale
        messagebox.showinfo("Seleziona Chat", "Seleziona la chat della persona, gruppo o canale su Telegram e premi OK per continuare.")
        messagebox.showinfo("Chat Selezionata", "Chat selezionata. Premi OK per continuare.")
        chat_url = telegram_driver.current_url
    
    # Dividi i link dei prodotti in una lista
    product_links = [link.strip() for link in product_links.split(",")]
    
    # Nascondi il driver visibile dopo la scansione del QR code
    visible_driver.set_window_position(-10000, 0)

    try:
        # Controllo continuo per ciascun prodotto
        while True:
            for product_link in product_links:
                try:
                    print(f"Controllo disponibilità per il prodotto: {product_link}")
                    visible_driver.get(product_link)
                    time.sleep(5)  # Attendi che la pagina si carichi completamente
                    title_product = visible_driver.find_element(By.XPATH, '/html/body/div[2]/div/div[3]/producthero-component/div/div/div[3]/producthero-info/div/h1').text

                    found_text = False
                    for i in range(4):
                        # Scorri leggermente la pagina verso il basso
                        visible_driver.execute_script("window.scrollBy(0, 250);")
                        time.sleep(1)  # Attendi che la pagina si aggiorni
                        
                        # Cattura uno screenshot della pagina
                        screenshot_path = "screenshot.png"
                        visible_driver.save_screenshot(screenshot_path)
                        
                        # Analizza lo screenshot per cercare il testo aggiornato
                        image = Image.open(screenshot_path)
                        text = pytesseract.image_to_string(image, lang='ita')
                        print(f"Testo rilevato: {text}")
                        
                        if "non disponibile" in text.lower() or "compra ora" in text.lower() or "aggiungi al carrello" in text.lower():
                            found_text = True
                            break
                    
                    if "non disponibile" in text.lower():
                        print(title_product, "non disponibile")
                        if platform == "WhatsApp":
                            send_whatsapp_message(visible_driver, f"{title_product}non disponibile", phone_number)
                        elif platform == "Telegram":
                            send_telegram_message(telegram_driver, f"{title_product} non disponibile")
                    else:
                        print(title_product, "disponibile")
                        if platform == "WhatsApp":
                            send_whatsapp_message(visible_driver, f"{title_product} disponibile LINK: {product_links }", phone_number)
                        elif platform == "Telegram":
                            send_telegram_message(telegram_driver, f"{title_product} disponibile LINK: {product_links }")
                    
                except NoSuchElementException:
                    print(f"Prodotto non disponibile: {product_link}")

            time.sleep(5)  # Attendi prima di controllare di nuovo

    except Exception as e:
        print(f"Errore: {e}")

    # Chiudi il browser
    visible_driver.quit()
    if platform == "Telegram":
        telegram_driver.quit()

# Crea la finestra principale
root = tk.Tk()
root.withdraw()  # Nascondi la finestra principale

# Avvia il controllo della disponibilità dei prodotti
start_check()