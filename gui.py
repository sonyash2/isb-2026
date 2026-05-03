import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from file_utils import load_config, read_file, write_file, read_text_file, write_text_file
from asymmetric_crypto import AsymmetricCrypto
from symmetric_crypto import SymmetricCrypto


class HybridCryptoGUI:
    """GUI приложение для гибридной криптосистемы."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Гибридная криптосистема RSA + IDEA")
        self.root.geometry("600x500")
        
        self.config = load_config()
        self.asymmetric = AsymmetricCrypto()
        self.symmetric = SymmetricCrypto()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса пользователя."""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.gen_frame = ttk.Frame(notebook)
        self.enc_frame = ttk.Frame(notebook)
        self.dec_frame = ttk.Frame(notebook)
        
        notebook.add(self.gen_frame, text='Генерация ключей')
        notebook.add(self.enc_frame, text='Шифрование')
        notebook.add(self.dec_frame, text='Расшифрование')
        
        self.setup_gen_tab()
        self.setup_enc_tab()
        self.setup_dec_tab()
    
    def setup_gen_tab(self):
        """Настройка вкладки генерации ключей."""
        frame = ttk.LabelFrame(self.gen_frame, text="Параметры", padding=10)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Путь для открытого ключа:").grid(row=0, column=0, sticky='w', pady=5)
        self.pub_key_entry = ttk.Entry(frame, width=40)
        self.pub_key_entry.insert(0, self.config['public_key'])
        self.pub_key_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Обзор", command=lambda: self.browse_file(self.pub_key_entry, 'save')).grid(row=0, column=2, padx=5)
        
        ttk.Label(frame, text="Путь для закрытого ключа:").grid(row=1, column=0, sticky='w', pady=5)
        self.priv_key_entry = ttk.Entry(frame, width=40)
        self.priv_key_entry.insert(0, self.config['private_key'])
        self.priv_key_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Обзор", command=lambda: self.browse_file(self.priv_key_entry, 'save')).grid(row=1, column=2, padx=5)
        
        ttk.Label(frame, text="Зашифрованный симметричный ключ:").grid(row=2, column=0, sticky='w', pady=5)
        self.enc_sym_entry = ttk.Entry(frame, width=40)
        self.enc_sym_entry.insert(0, self.config['encrypted_symmetric_key'])
        self.enc_sym_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Обзор", command=lambda: self.browse_file(self.enc_sym_entry, 'save')).grid(row=2, column=2, padx=5)
        
        ttk.Label(frame, text="Размер ключа RSA (бит):").grid(row=3, column=0, sticky='w', pady=5)
        self.key_size_var = tk.StringVar(value=str(self.config['algorithms']['key_size']))
        ttk.Combobox(frame, textvariable=self.key_size_var, values=['2048', '4096'], state='readonly').grid(row=3, column=1, sticky='w', padx=5)
        
        ttk.Button(frame, text="Сгенерировать ключи", command=self.generate_keys_thread).grid(row=4, column=0, columnspan=3, pady=20)
        
        self.gen_log = tk.Text(frame, height=15, width=70)
        self.gen_log.grid(row=5, column=0, columnspan=3, pady=10)
    
    def setup_enc_tab(self):
        """Настройка вкладки шифрования."""
        frame = ttk.LabelFrame(self.enc_frame, text="Параметры", padding=10)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Исходный файл:").grid(row=0, column=0, sticky='w', pady=5)
        self.input_entry = ttk.Entry(frame, width=40)
        self.input_entry.insert(0, self.config['initial_file'])
        self.input_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Обзор", command=lambda: self.browse_file(self.input_entry, 'open')).grid(row=0, column=2, padx=5)
        
        ttk.Label(frame, text="Зашифрованный файл:").grid(row=1, column=0, sticky='w', pady=5)
        self.enc_out_entry = ttk.Entry(frame, width=40)
        self.enc_out_entry.insert(0, self.config['encrypted_file'])
        self.enc_out_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Обзор", command=lambda: self.browse_file(self.enc_out_entry, 'save')).grid(row=1, column=2, padx=5)
        
        ttk.Label(frame, text="Закрытый ключ RSA:").grid(row=2, column=0, sticky='w', pady=5)
        self.enc_priv_entry = ttk.Entry(frame, width=40)
        self.enc_priv_entry.insert(0, self.config['private_key'])
        self.enc_priv_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Обзор", command=lambda: self.browse_file(self.enc_priv_entry, 'open')).grid(row=2, column=2, padx=5)
        
        ttk.Label(frame, text="Зашифрованный симметричный ключ:").grid(row=3, column=0, sticky='w', pady=5)
        self.enc_sym_in_entry = ttk.Entry(frame, width=40)
        self.enc_sym_in_entry.insert(0, self.config['encrypted_symmetric_key'])
        self.enc_sym_in_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Обзор", command=lambda: self.browse_file(self.enc_sym_in_entry, 'open')).grid(row=3, column=2, padx=5)
        
        ttk.Button(frame, text="Зашифровать файл", command=self.encrypt_file_thread).grid(row=4, column=0, columnspan=3, pady=20)
        
        self.enc_log = tk.Text(frame, height=12, width=70)
        self.enc_log.grid(row=5, column=0, columnspan=3, pady=10)
    
    def setup_dec_tab(self):
        """Настройка вкладки расшифрования."""
        frame = ttk.LabelFrame(self.dec_frame, text="Параметры", padding=10)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Зашифрованный файл:").grid(row=0, column=0, sticky='w', pady=5)
        self.dec_in_entry = ttk.Entry(frame, width=40)
        self.dec_in_entry.insert(0, self.config['encrypted_file'])
        self.dec_in_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Обзор", command=lambda: self.browse_file(self.dec_in_entry, 'open')).grid(row=0, column=2, padx=5)
        
        ttk.Label(frame, text="Расшифрованный файл:").grid(row=1, column=0, sticky='w', pady=5)
        self.dec_out_entry = ttk.Entry(frame, width=40)
        self.dec_out_entry.insert(0, self.config['decrypted_file'])
        self.dec_out_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Обзор", command=lambda: self.browse_file(self.dec_out_entry, 'save')).grid(row=1, column=2, padx=5)
        
        ttk.Label(frame, text="Закрытый ключ RSA:").grid(row=2, column=0, sticky='w', pady=5)
        self.dec_priv_entry = ttk.Entry(frame, width=40)
        self.dec_priv_entry.insert(0, self.config['private_key'])
        self.dec_priv_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Обзор", command=lambda: self.browse_file(self.dec_priv_entry, 'open')).grid(row=2, column=2, padx=5)
        
        ttk.Label(frame, text="Зашифрованный симметричный ключ:").grid(row=3, column=0, sticky='w', pady=5)
        self.dec_sym_entry = ttk.Entry(frame, width=40)
        self.dec_sym_entry.insert(0, self.config['encrypted_symmetric_key'])
        self.dec_sym_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Обзор", command=lambda: self.browse_file(self.dec_sym_entry, 'open')).grid(row=3, column=2, padx=5)
        
        ttk.Button(frame, text="Расшифровать файл", command=self.decrypt_file_thread).grid(row=4, column=0, columnspan=3, pady=20)
        
        self.dec_log = tk.Text(frame, height=12, width=70)
        self.dec_log.grid(row=5, column=0, columnspan=3, pady=10)
    
    def browse_file(self, entry, mode='open'):
        """Открывает диалог выбора файла."""
        if mode == 'open':
            filename = filedialog.askopenfilename()
        else:
            filename = filedialog.asksaveasfilename()
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)
    
    def log(self, widget, message):
        """Добавляет сообщение в лог."""
        widget.insert(tk.END, message + "\n")
        widget.see(tk.END)
    
    def generate_keys_thread(self):
        """Запускает генерацию ключей в отдельном потоке."""
        thread = threading.Thread(target=self.generate_keys)
        thread.daemon = True
        thread.start()
    
    def generate_keys(self):
        """Выполняет генерацию ключей."""
        self.log(self.gen_log, "Начало генерации ключей...")
        try:
            self.config['public_key'] = self.pub_key_entry.get()
            self.config['private_key'] = self.priv_key_entry.get()
            self.config['encrypted_symmetric_key'] = self.enc_sym_entry.get()
            self.config['algorithms']['key_size'] = int(self.key_size_var.get())
            
            symmetric = SymmetricCrypto(key_size=self.config['algorithms']['idea_key_size'])
            asymmetric = AsymmetricCrypto(key_size=self.config['algorithms']['key_size'])
            
            self.log(self.gen_log, "1. Генерация симметричного ключа...")
            symmetric_key = symmetric.generate_key()
            self.log(self.gen_log, f"    Ключ сгенерирован ({len(symmetric_key)} байт)")
            
            self.log(self.gen_log, "2. Генерация ключей RSA...")
            private_key, public_key = asymmetric.generate_key_pair()
            self.log(self.gen_log, f"   Ключи сгенерированы ({self.config['algorithms']['key_size']} бит)")
            
            self.log(self.gen_log, "3. Сохранение ключей...")
            write_file(self.config['public_key'], asymmetric.serialize_public_key(public_key))
            write_file(self.config['private_key'], asymmetric.serialize_private_key(private_key))
            
            self.log(self.gen_log, "4. Шифрование симметричного ключа...")
            encrypted_key = asymmetric.encrypt_with_public_key(symmetric_key, public_key)
            write_file(self.config['encrypted_symmetric_key'], encrypted_key)
            
            self.log(self.gen_log, "\n Генерация ключей завершена!")
        except Exception as e:
            self.log(self.gen_log, f"\n Ошибка: {e}")
    
    def encrypt_file_thread(self):
        """Запускает шифрование в отдельном потоке."""
        thread = threading.Thread(target=self.encrypt_file)
        thread.daemon = True
        thread.start()
    
    def encrypt_file(self):
        """Выполняет шифрование файла."""
        self.log(self.enc_log, "Начало шифрования...")
        try:
            input_path = self.input_entry.get()
            output_path = self.enc_out_entry.get()
            private_key_path = self.enc_priv_entry.get()
            enc_sym_path = self.enc_sym_in_entry.get()
            
            asymmetric = AsymmetricCrypto()
            symmetric = SymmetricCrypto()
            
            self.log(self.enc_log, "1. Загрузка закрытого ключа...")
            private_key_bytes = read_file(private_key_path)
            private_key = asymmetric.deserialize_private_key(private_key_bytes)
            
            self.log(self.enc_log, "2. Расшифровка симметричного ключа...")
            enc_sym_key = read_file(enc_sym_path)
            symmetric_key = asymmetric.decrypt_with_private_key(enc_sym_key, private_key)
            
            self.log(self.enc_log, f"3. Загрузка файла: {input_path}")
            plaintext = read_file(input_path)
            self.log(self.enc_log, f"   Размер: {len(plaintext)} байт")
            
            self.log(self.enc_log, "4. Шифрование...")
            encrypted_data = symmetric.encrypt(plaintext, symmetric_key)
            write_file(output_path, encrypted_data)
            self.log(self.enc_log, f"    Сохранено: {output_path}")
            self.log(self.enc_log, f"    Размер: {len(encrypted_data)} байт")
            
            self.log(self.enc_log, "\n Шифрование завершено!")
        except Exception as e:
            self.log(self.enc_log, f"\n Ошибка: {e}")
    
    def decrypt_file_thread(self):
        """Запускает расшифрование в отдельном потоке."""
        thread = threading.Thread(target=self.decrypt_file)
        thread.daemon = True
        thread.start()
    
    def decrypt_file(self):
        """Выполняет расшифрование файла."""
        self.log(self.dec_log, "Начало расшифрования...")
        try:
            input_path = self.dec_in_entry.get()
            output_path = self.dec_out_entry.get()
            private_key_path = self.dec_priv_entry.get()
            enc_sym_path = self.dec_sym_entry.get()
            
            asymmetric = AsymmetricCrypto()
            symmetric = SymmetricCrypto()
            
            self.log(self.dec_log, "1. Загрузка закрытого ключа...")
            private_key_bytes = read_file(private_key_path)
            private_key = asymmetric.deserialize_private_key(private_key_bytes)
            
            self.log(self.dec_log, "2. Расшифровка симметричного ключа...")
            enc_sym_key = read_file(enc_sym_path)
            symmetric_key = asymmetric.decrypt_with_private_key(enc_sym_key, private_key)
            
            self.log(self.dec_log, f"3. Загрузка файла: {input_path}")
            encrypted_data = read_file(input_path)
            self.log(self.dec_log, f"   Размер: {len(encrypted_data)} байт")
            
            self.log(self.dec_log, "4. Расшифрование...")
            decrypted_data = symmetric.decrypt(encrypted_data, symmetric_key)
            write_file(output_path, decrypted_data)
            self.log(self.dec_log, f"   Сохранено: {output_path}")
            self.log(self.dec_log, f"   Размер: {len(decrypted_data)} байт")
            
            self.log(self.dec_log, "\n Расшифрование завершено!")
        except Exception as e:
            self.log(self.dec_log, f"\n Ошибка: {e}")


def main():
    """Запуск GUI приложения."""
    root = tk.Tk()
    app = HybridCryptoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()