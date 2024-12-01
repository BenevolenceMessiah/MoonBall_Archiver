import os
import zstandard as zstd
import brotli
import lzma
import hashlib
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from transformers import pipeline
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
import argparse
import pyotp

class MoonBallArchive:
    def __init__(self, encryption_key=None):
        self.files = []
        self.index = []
        self.encryption_key = encryption_key
        self.ml_model = RandomForestClassifier()
        self.embedding_model = pipeline('feature-extraction', model='distilbert-base-uncased')
        self.load_config()

    def load_config(self):
        with open('config.yml', 'r') as config_file:
            import yaml
            self.config = yaml.safe_load(config_file)

    def add_file(self, file_path, chunk_size=5242880):  # Default chunk size: 5MB
        with open(file_path, 'rb') as f:
            chunk_id = 0
            while chunk := f.read(chunk_size):
                self.compress_chunk(chunk, file_path, chunk_id)
                chunk_id += 1

    def compress_chunk(self, chunk, file_path, chunk_id):
        algo = self.predict_compression_algo(file_path, chunk)
        compressed_data = self.compress_data(chunk, algo)

        if self.encryption_key:
            compressed_data = self.encrypt_data(compressed_data)

        embedding = self.generate_embedding(chunk)

        chunk_entry = {
            'file_name': file_path,
            'chunk_id': chunk_id,
            'original_size': len(chunk),
            'compressed_size': len(compressed_data),
            'compression_algo': algo,
            'data': compressed_data,
            'embedding': embedding
        }

        self.files.append(chunk_entry)
        self.index.append({
            'file_name': file_path,
            'chunk_id': chunk_id,
            'original_size': len(chunk),
            'compressed_size': len(compressed_data),
            'compression_algo': algo,
            'embedding': embedding
        })

    def predict_compression_algo(self, file_path, chunk):
        # Placeholder ML logic
        features = np.array([[len(chunk), self.calculate_entropy(chunk)]])
        algo_index = self.ml_model.predict(features)[0]
        algo_map = {0: 'brotli', 1: 'lzma', 2: 'zstd'}
        return algo_map.get(algo_index, 'zstd')

    def calculate_entropy(self, data):
        if len(data) == 0:
            return 0
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1
        entropy = 0
        for count in byte_counts:
            if count > 0:
                p = count / len(data)
                entropy -= p * math.log2(p)
        return entropy

    def generate_embedding(self, chunk):
        base64_chunk = base64.b64encode(chunk).decode('utf-8')
        output = Command('python3').args(['generate_embedding.py', base64_chunk]).output()
        if not output.status.success():
            raise Exception(f"Failed to generate embedding: {output.stderr}")
        return json.loads(output.stdout)

    def add_files_parallel(self, file_paths):
        with ThreadPoolExecutor() as executor:
            list(tqdm(executor.map(self.add_file, file_paths), total=len(file_paths), desc='Indexing and Compressing Files'))

    def add_directory(self, dir_path):
        for root, _, files in os.walk(dir_path):
            for file in files:
                self.add_file(os.path.join(root, file))

    def save(self, archive_path):
        if not (archive_path.endswith(".mnbl") or archive_path.endswith("\U0001F315")):
            raise ValueError("Invalid file extension. Please use '.mnbl' or '.🌕' for the archive.")

        with open(archive_path, 'wb') as archive:
            index_data = str(self.index).encode('utf-8')
            if self.encryption_key:
                index_data = self.encrypt_data(index_data)
            archive.write(index_data)
            archive.write(b'\n')

            for file in tqdm(self.files, desc='Writing chunks to archive'):
                archive.write(file['data'])
                archive.write(b'\n')

            checksum = hashlib.sha256(index_data).hexdigest().encode('utf-8')
            if self.encryption_key:
                checksum = self.encrypt_data(checksum)
            archive.write(checksum)

    def extract(self, archive_path, output_dir):
        if not (archive_path.endswith(".mnbl") or archive_path.endswith("\U0001F315")):
            raise ValueError("Invalid file extension. Please use '.mnbl' or '.🌕' for the archive.")

        with open(archive_path, 'rb') as archive:
            lines = archive.readlines()

            index_data = lines[0].strip()
            if self.encryption_key:
                index_data = self.decrypt_data(index_data)
            index_data = eval(index_data.decode('utf-8'))

            for file_meta in tqdm(index_data, desc='Extracting chunks'):
                compressed_data = lines[file_meta['chunk_id'] + 1].strip()

                if self.encryption_key:
                    compressed_data = self.decrypt_data(compressed_data)

                decompressed_data = self.decompress_data(compressed_data, file_meta['compression_algo'])

                output_path = os.path.join(output_dir, os.path.basename(file_meta['file_name']))
                mode = 'wb' if file_meta['chunk_id'] == 0 else 'ab'
                with open(output_path, mode) as out_file:
                    out_file.write(decompressed_data)

    def semantic_search(self, query):
        query_embedding = self.embedding_model([query])[0][0]
        results = []
        for file_meta in self.index:
            similarity = np.dot(query_embedding, file_meta['embedding'])
            if similarity > self.config['semantic_search']['threshold']:
                results.append(file_meta['file_name'])
        return results

    def encrypt_data(self, data):
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashlib.sha256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key.encode('utf-8')))
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = self.padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return salt + iv + encrypted_data

    def decrypt_data(self, data):
        salt = data[:16]
        iv = data[16:32]
        kdf = PBKDF2HMAC(
            algorithm=hashlib.sha256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key.encode('utf-8')))
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded_data = decryptor.update(data[32:]) + decryptor.finalize()
        unpadder = self.padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
        return decrypted_data

    def compress_data(self, data, algo):
        if algo == 'brotli':
            compressed_data = brotli.compress(data)
        elif algo == 'lzma':
            compressed_data = lzma.compress(data)
        else:
            cctx = zstd.ZstdCompressor(level=9)  # Adjust level as needed
            compressed_data = cctx.compress(data)
        return compressed_data

    def decompress_data(self, data, algo):
        if algo == 'brotli':
            decompressed_data = brotli.decompress(data)
        elif algo == 'lzma':
            decompressed_data = lzma.decompress(data)
        else:
            dctx = zstd.ZstdDecompressor()
            decompressed_data = dctx.decompress(data)
        return decompressed_data

    def clean_up_temporary_files(self):
        for file_meta in self.files:
            chunk_path = f"{file_meta['file_name']}_{file_meta['chunk_id']}.mbc"
            if os.path.exists(chunk_path):
                os.remove(chunk_path)

def launch_gui():
    def add_files():
        files = filedialog.askopenfilenames()
        if files:
            for file in files:
                file_listbox.insert(tk.END, file)

    def add_directory():
        dir_path = filedialog.askdirectory()
        if dir_path:
            file_listbox.insert(tk.END, dir_path)

    def compress_files():
        files = file_listbox.get(0, tk.END)
        if not files:
            messagebox.showerror('Error', 'No files or directories selected for compression.')
            return
        output_path = filedialog.asksaveasfilename(defaultextension='.mnbl', filetypes=[('MoonBall Archive', '*.mnbl'), ('MoonBall Archive Emoji', '🌕')])
        if not output_path:
            return
        encryption_key = simpledialog.askstring("Encryption Key", "Enter an encryption key (or leave blank for no encryption):", show='*')
        archive = MoonBallArchive(encryption_key=encryption_key)
        for item in files:
            if os.path.isdir(item):
                archive.add_directory(item)
            else:
                archive.add_file(item)
        archive.save(output_path)
        messagebox.showinfo('Success', f'Archive saved as {output_path}')

    def extract_archive():
        archive_path = filedialog.askopenfilename(filetypes=[('MoonBall Archive', '*.mnbl'), ('MoonBall Archive Emoji', '🌕')])
        if not archive_path:
            return
        output_dir = filedialog.askdirectory()
        if not output_dir:
            return
        encryption_key = simpledialog.askstring("Encryption Key", "Enter the encryption key (if set):", show='*')
        archive = MoonBallArchive(encryption_key=encryption_key)
        secret_key = 'your_secret_key_here'  # Replace with actual secret key
        otp = simpledialog.askstring("2FA OTP", "Enter the 2FA OTP (if set):", show='*')
        if verify_otp(secret_key, otp):
            archive.extract(archive_path, output_dir)
            messagebox.showinfo('Success', f'Files extracted to {output_dir}')
        else:
            messagebox.showerror('Error', 'Invalid OTP.')

    def semantic_search():
        query = simpledialog.askstring("Semantic Search", "Enter your search query:")
        if query:
            archive = MoonBallArchive()
            results = archive.semantic_search(query)
            result_str = "\n".join(results) if results else "No files found matching the query."
            messagebox.showinfo('Search Results', result_str)

    root = tk.Tk()
    root.title('MoonBall Archiver')
    root.geometry('600x500')

    try:
        moonball_logo = Image.open(os.path.join('assets', 'moonball_file.ico'))
        moonball_logo = moonball_logo.resize((50, 50), Image.LANCZOS)
        logo_img = ImageTk.PhotoImage(moonball_logo)
        logo_label = tk.Label(root, image=logo_img)
        logo_label.image = logo_img
        logo_label.pack(pady=10)
    except FileNotFoundError:
        print('assets/moonball_icon.png not found. Skipping logo display.')

    add_button = tk.Button(root, text='Add Files', command=add_files)
    add_button.pack(pady=5)

    add_dir_button = tk.Button(root, text='Add Directory', command=add_directory)
    add_dir_button.pack(pady=5)

    file_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=60, height=10)
    file_listbox.pack(pady=5)

    compress_button = tk.Button(root, text='Compress to Archive', command=compress_files)
    compress_button.pack(pady=5)

    extract_button = tk.Button(root, text='Extract Archive', command=extract_archive)
    extract_button.pack(pady=5)

    search_button = tk.Button(root, text='Semantic Search', command=semantic_search)
    search_button.pack(pady=5)

    root.mainloop()

def verify_otp(secret_key, provided_otp):
    totp = pyotp.TOTP(secret_key, digest="sha1", digits=6, interval=30)
    return totp.verify(provided_otp)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='MoonBall Archiver')
    parser.add_argument('--add', type=str, nargs='+', help='Files or directories to add to the archive')
    parser.add_argument('--extract', type=str, help='Archive to extract')
    parser.add_argument('--output', type=str, help='Output directory or archive name')
    parser.add_argument('--scheme', choices=['fast', 'balanced', 'max'], default='balanced', help='Compression scheme')
    parser.add_argument('--extension', choices=['mnbl', '🌕'], default='mnbl', help='File extension for the archive')
    parser.add_argument('--gui', action='store_true', help='Launch graphical user interface')
    parser.add_argument('--search', type=str, help='Semantic search query')
    args = parser.parse_args()

    if args.gui:
        launch_gui()
    else:
        encryption_key = simpledialog.askstring("Encryption Key", "Enter an encryption key (or leave blank for no encryption):", show='*') if args.add or args.extract else None
        archive = MoonBallArchive(encryption_key=encryption_key)

        if args.add:
            for item in args.add:
                if os.path.isdir(item):
                    archive.add_directory(item)
                else:
                    archive.add_file(item)
            archive_name = args.output if args.output else f'archive.{args.extension}'
            archive.save(archive_name)
            print(f'Archive saved as {archive_name}')
        elif args.extract:
            if not args.extract or not args.output:
                print('Please provide both the archive to extract and the output directory.')
                return
            os.makedirs(args.output, exist_ok=True)
            secret_key = 'your_secret_key_here'  # Replace with actual secret key
            otp = simpledialog.askstring("2FA OTP", "Enter the 2FA OTP (if set):", show='*')
            if verify_otp(secret_key, otp):
                archive.extract(args.extract, args.output)
                print(f'Files extracted to {args.output}')
            else:
                print("Invalid OTP.")
        elif args.search:
            results = archive.semantic_search(args.search)
            if results:
                print(f"Files matching the query: {', '.join(results)}")
            else:
                print("No files found matching the query.")

if __name__ == '__main__':
    main()