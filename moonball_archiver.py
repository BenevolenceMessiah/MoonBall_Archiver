import os
import zstandard as zstd
import brotli
import lzma
import hashlib
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from sklearn.ensemble import RandomForestClassifier  # Example ML model for decision-making
import numpy as np
from transformers import pipeline  # Transformers.js equivalent in Python for demonstration purposes
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
from cryptography.fernet import Fernet  # For encryption

class MoonBallArchive:
    def __init__(self, encryption_key=None):
        self.files = []
        self.index = []
        self.encryption_key = encryption_key
        self.encryption_cipher = Fernet(encryption_key) if encryption_key else None
        # Placeholder for a trained ML model; in practice, load a pre-trained model
        self.ml_model = RandomForestClassifier()
        # Load or initialize embedding model for indexing and retrieval
        self.embedding_model = pipeline('feature-extraction', model='distilbert-base-uncased')

    def add_file(self, file_path, chunk_size=5242880):  # Default chunk size: 5MB
        # Read the file and split into chunks
        with open(file_path, 'rb') as f:
            chunk_id = 0
            while chunk := f.read(chunk_size):
                self.compress_chunk(chunk, file_path, chunk_id)
                chunk_id += 1

    def compress_chunk(self, chunk, file_path, chunk_id):
        # Use machine learning to determine the optimal compression algorithm
        algo = self.predict_compression_algo(file_path, chunk)
        if algo == 'brotli':
            compressed_data = brotli.compress(chunk)
        elif algo == 'lzma':
            compressed_data = lzma.compress(chunk)
        else:
            compressed_data = zstd.ZstdCompressor().compress(chunk)

        # Encrypt the compressed data if encryption is enabled
        if self.encryption_cipher:
            compressed_data = self.encryption_cipher.encrypt(compressed_data)

        # Generate embedding for the chunk
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
        # Example features for ML model: file extension, chunk size, entropy (compression predictability)
        file_extension = os.path.splitext(file_path)[1]
        entropy = self.calculate_entropy(chunk)
        features = np.array([[len(chunk), entropy]])

        # Use ML model to predict the best algorithm
        algo_index = self.ml_model.predict(features)[0]
        algo_map = {0: 'brotli', 1: 'lzma', 2: 'zstd'}
        return algo_map.get(algo_index, 'zstd')

    def calculate_entropy(self, data):
        # Calculate entropy as a measure of randomness
        import math
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
        # Generate embedding for the chunk using an embedding model
        return self.embedding_model(chunk.tolist())[0][0]

    def add_files_parallel(self, file_paths):
        with ThreadPoolExecutor() as executor:
            list(tqdm(executor.map(self.add_file, file_paths), total=len(file_paths), desc='Indexing and Compressing Files'))

    def add_directory(self, dir_path):
        # Recursively add all files from the directory and subdirectories
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                self.add_file(file_path)

    def save(self, archive_path):
        if not (archive_path.endswith(".mnbl") or archive_path.endswith("\U0001F315")):
            raise ValueError("Invalid file extension. Please use '.mnbl' or '.🌕' for the archive.")
        
        with open(archive_path, 'wb') as archive:
            # Write header (index as bytes)
            index_data = str(self.index).encode('utf-8')
            if self.encryption_cipher:
                index_data = self.encryption_cipher.encrypt(index_data)
            archive.write(index_data)
            archive.write(b'\n')
            
            # Write each file chunk
            for file in tqdm(self.files, desc='Writing chunks to archive'):
                archive.write(file['data'])
                archive.write(b'\n')
            
            # Write footer (checksum)
            checksum = hashlib.sha256(index_data).hexdigest().encode('utf-8')
            if self.encryption_cipher:
                checksum = self.encryption_cipher.encrypt(checksum)
            archive.write(checksum)

    def extract(self, archive_path, output_dir):
        if not (archive_path.endswith(".mnbl") or archive_path.endswith("\U0001F315")):
            raise ValueError("Invalid file extension. Please use '.mnbl' or '.🌕' for the archive.")

        with open(archive_path, 'rb') as archive:
            lines = archive.readlines()
            
            # Read index from header
            index_data = lines[0]
            if self.encryption_cipher:
                index_data = self.encryption_cipher.decrypt(index_data)
            index_data = eval(index_data.decode('utf-8'))
            
            # Extract chunks based on index
            for file_meta in tqdm(index_data, desc='Extracting chunks'):
                compressed_data = lines[file_meta['chunk_id'] + 1].strip()
                
                # Decrypt the compressed data if encryption is enabled
                if self.encryption_cipher:
                    compressed_data = self.encryption_cipher.decrypt(compressed_data)
                
                # Decompress based on algorithm
                if file_meta['compression_algo'] == 'brotli':
                    data = brotli.decompress(compressed_data)
                elif file_meta['compression_algo'] == 'lzma':
                    data = lzma.decompress(compressed_data)
                else:
                    data = zstd.ZstdDecompressor().decompress(compressed_data)
                
                # Write the chunk to the output file
                output_path = os.path.join(output_dir, os.path.basename(file_meta['file_name']))
                mode = 'wb' if file_meta['chunk_id'] == 0 else 'ab'
                with open(output_path, mode) as out_file:
                    out_file.write(data)

    def semantic_search(self, query):
        # Generate embedding for the search query
        query_embedding = self.embedding_model([query])[0][0]

        # Compare with stored embeddings and return relevant files
        results = []
        for file_meta in self.index:
            similarity = np.dot(query_embedding, file_meta['embedding'])  # Simplified similarity calculation
            if similarity > 0.8:  # Threshold for relevance
                results.append(file_meta['file_name'])
        return results

        def clean_up_temporary_files(self):
        # Remove any temporary files created during compression or extraction
            for file_meta in self.files:
                chunk_path = f"{file_meta['file_name']}_{file_meta['chunk_id']}.mbc"
            if os.path.exists(chunk_path):
                os.remove(chunk_path)

# Graphical User Interface (GUI)
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
        encryption_key = encryption_key.encode() if encryption_key else None
        archive = MoonBallArchive(encryption_key=encryption_key)
        for item in files:
            if os.path.isdir(item):
                archive.add_directory(item)
            else:
                archive.add_file(item)
        archive.save(output_path)
        archive.clean_up_temporary_files()
        messagebox.showinfo('Success', f'Archive saved as {output_path}')

    def extract_archive():
        archive_path = filedialog.askopenfilename(filetypes=[('MoonBall Archive', '*.mnbl'), ('MoonBall Archive Emoji', '🌕')])
        if not archive_path:
            return
        output_dir = filedialog.askdirectory()
        if not output_dir:
            return
        encryption_key = simpledialog.askstring("Encryption Key", "Enter the encryption key (if set):", show='*')
        encryption_key = encryption_key.encode() if encryption_key else None
        archive = MoonBallArchive(encryption_key=encryption_key)
        archive.extract(archive_path, output_dir)
        messagebox.showinfo('Success', f'Files extracted to {output_dir}')

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

    # Add MoonBall logo to the GUI
    try:
        moonball_logo = Image.open(os.path.join('assets', 'moonball_icon.png'))
        moonball_logo = moonball_logo.resize((50, 50), Image.ANTIALIAS)
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

# Command Line Interface (CLI)
def main():
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
        archive = MoonBallArchive(encryption_key=None)

        if args.add:
            for item in args.add:
                if os.path.isdir(item):
                    archive.add_directory(item)
                else:
                    archive.add_file(item)
            archive_name = args.output if args.output else f'archive.{args.extension}'
            archive.save(archive_name)
            archive.clean_up_temporary_files()
            print(f'Archive saved as {archive_name}')
        elif args.extract:
            if not args.extract or not args.output:
                print('Please provide both the archive to extract and the output directory.')
                return
            os.makedirs(args.output, exist_ok=True)
            archive.extract(args.extract, args.output)
            print(f'Files extracted to {args.output}')
        elif args.search:
            results = archive.semantic_search(args.search)
            if results:
                print(f"Files matching the query: {', '.join(results)}")
            else:
                print("No files found matching the query.")

if __name__ == '__main__':
    main()
       