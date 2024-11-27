# MoonBall Archiver

Welcome to **MoonBall Archiver**, a cutting-edge file compression and archiving solution designed to redefine the way we store and manage digital data. MoonBall is a forward-thinking, highly efficient, and AI-powered archiver that leverages advanced compression techniques to bring you the best currently possible performance for your storage needs. With a unique blend of machine learning, chunk-level adaptability, and interoperability, MoonBall aims to be the future of digital archiving.

- [GitHub Repository](https://github.com/BenevolenceMessiah/MoonBall_Archiver)
- [Moon Programming Language Website](https://www.moonlanguage.org/)
- [Moon GitHub Repository](https://github.com/BenevolenceMessiah/Moon)
- [Join our Discord Community](https://discord.gg/sUaj4xC9)

## Key Features

### Adaptive Compression Schemes

MoonBall uses a machine learning model to determine the optimal compression algorithm for each data chunk. It chooses from multiple algorithms such as **Brotli**, **LZMA**, and **Zstandard** (Zstd), depending on the type of data and its compressibility. This results in a highly efficient compression approach tailored specifically to each data type. There are currently 3 Compression Schemes: Fast, Balanced (being the default), and Maximum.

### Chunk-Level Compression

The MoonBall Archiver first indexes and then divides files into logical chunks for independent compression, ensuring that each chunk is handled in the most space-efficient way possible. Chunk-level compression not only improves compression ratios but also enables parallel processing for enhanced speed.

### Comprehensive Graphical User Interface (GUI)

MoonBall includes a user-friendly GUI, implemented in both **Python** and  **Rust** (using **Egui** with **Rust**), allowing even beginners to easily compress and decompress files or directories. This interface provides features like:

- Adding files or directories for compression
- Saving the resulting MoonBall archive
- Extracting compressed archives
- Semantic search

### Machine Learning Enhancements

MoonBall integrates **Transformers.js** (Python FFI in Rust version) to generate embeddings for each file chunk, which enhances the retrieval, clustering, and deduplication of data. These embeddings also enable semantic-based data retrieval and adaptive chunking.

### Integration with AI Tools

MoonBall leverages **Retrieval-Augmented Generation (RAG)** for enhanced data retrieval, clustering, and **semantic-based search**. This utilizes **Transformers** models for file content analysis and embedding generation, allowing users to find files based on context rather than exact filenames, even while the `.mnbl` archive is still compressed.

### Two-Factor Authentication (2FA)

The Rust implementation introduces an optional **Two-Factor Authentication (2FA)** feature for additional security when accessing encrypted archives. This uses OTP (One-Time Password) verification to ensure that only authorized users can extract the contents of an archive.

### Extended Encryption Options

MoonBall supports strong encryption for archives, with options for different algorithms, including **AES-ECB** and **AES-CBC** modes. These encryption features help protect sensitive data stored within MoonBall archives.

### Fun Emoji Extensions

Set the archive file extension (`.mnbl` or `.🌕`) in keeping with the spirit of the Moon Programming Language.

### Command-Line Interface (CLI)

For more advanced users, MoonBall provides a powerful CLI that allows adding files or directories, selecting compression schemes, running semantic-searches, and extracting archives directly from the terminal. The CLI supports enabling encryption, using 2FA, and other advanced options.

### Multi-Platform Compatibility

The MoonBall Archiver is designed with compatibility in mind, providing cross-platform functionality on both Windows and Unix-like systems.

### Extensible Design for Future Development

MoonBall has been designed with extensibility at its core, allowing for future enhancements:

- **Rust Implementation**: A parallel implementation in **Rust** has been created to complement the Python prototype. This Rust version enhances performance, security, and scalability.
- **Foreign Function Interface (FFI)**: To achieve interoperability, MoonBall leverages compression libraries via FFI, integrating with Python-based machine learning tools for tasks like embedding generation.
- **Moon Integration**: Utilizing Moon's standard library modules for file I/O and other basic functionalities to streamline development and make MoonBall a perfect match for the Moon ecosystem.

## How It Works

MoonBall Archiver operates in a structured and efficient sequence to optimize the compression and management of digital data. This process ensures that files are stored in the most space-efficient manner while maintaining easy access and integrity:

### 1. Indexing

**Indexing** is the initial step where MoonBall Archiver creates a structured list of all files and logical chunks within those files. This metadata index acts as the backbone of the archiver, facilitating efficient retrieval and management of archived data.

- **Functionality**: The archiver scans the specified files and directories, recording the structure, size, and other relevant metadata. This data is essential for subsequent steps like chunking and compression.
- **Benefit**: By maintaining a detailed index, MoonBall ensures that data can be quickly located and processed during compression, decompression, and retrieval. The index is stored in a way that it can be easily accessible and quickly updated.

### 2. Chunking

**Chunking** involves dividing each file into smaller, manageable parts, known as **chunks**. Each chunk is processed independently to determine the best compression algorithm and embedding generation method.

- **Functionality**: Files are split into chunks based on predefined criteria, such as size limits. This approach allows for more granular and efficient compression.
- **Benefit**: Chunking reduces the computational overhead by processing smaller data segments and enables parallel processing, which significantly speeds up the compression process. It also helps in adapting compression strategies to the nature of different data types.

### 3. Embeddings and Index Storage

**Embeddings** are numerical representations of each chunk, generated using machine learning models. These embeddings capture the semantic context and content of data, which is crucial for advanced features like semantic search.

- **Functionality**: For each chunk, MoonBall Archiver uses a pre-trained **Transformers** model to generate embeddings. These embeddings are stored alongside the index in the archive.
- **Benefit**: Embeddings enable semantic analysis, data deduplication, and retrieval. They allow the archiver to cluster similar files and provide meaningful search results, even when the content is compressed.

### 4. Compression

**Compression** is the process of reducing the size of each chunk to save storage space. MoonBall Archiver applies different compression algorithms to each chunk based on its type and compressibility.

- **Functionality**: For each chunk, the archiver evaluates several compression algorithms—such as Brotli, LZMA, and Zstandard—and selects the most suitable one based on machine learning predictions.
- **Benefit**: By choosing the best compression algorithm for each chunk, MoonBall Archiver achieves higher overall compression ratios and better performance.

### 5. Embeddings and Index Storage

After compression, the embeddings and index are stored in the **header** of the MoonBall archive file. This metadata is crucial for efficient data retrieval and management.

- **Functionality**: The index and embeddings are serialized and written to the beginning of the archive file.
- **Benefit**: Storing metadata in the header allows for quick access during retrieval and is essential for features like semantic search, file lookup, and archive validation.

### 6. Checksum Footer

A **checksum** is computed for the index and embedded data to ensure the integrity and consistency of the archive.

- **Functionality**: Using a hashing algorithm (e.g., SHA-256), the archiver generates a checksum of the metadata and attaches it to the end of the archive file.
- **Benefit**: The checksum allows the archiver to verify the integrity of the metadata during extraction, ensuring that the data has not been tampered with or corrupted.

### Example Workflow

To illustrate the process, consider the following example:

1. **Indexing**: The user adds a directory containing a project with multiple files (e.g., source code, images, and documentation).
2. **Chunking**: The archiver splits the files into chunks. For example, source code files might be split into 5MB chunks.
3. **Embeddings**: For each chunk, embeddings are generated using a Transformers model like **distilbert-base-uncased**. These embeddings capture the context and meaning of the data.
4. **Compression**: Each chunk is compressed using an optimal algorithm. For instance, text-based chunks might use Zstandard, while image chunks might use Brotli.
5. **Storage**: The embeddings and index are stored in the header of the archive file, along with the compressed chunks.
6. **Checksum**: A checksum is generated and stored in the footer to ensure the archive's integrity.

This structured approach ensures that MoonBall Archiver is highly efficient, adaptable, and reliable, making it the future of digital archiving.
## Key Terms

### Retrieval-Augmented Generation (RAG)

A technology that leverages machine learning models for retrieving relevant information to augment user queries and provide more contextually relevant results.

### Indexing

The process of creating a structured list of all files and chunks in an archive to facilitate efficient retrieval, compression, and decompression.

### Archive

A single file that contains multiple compressed files and metadata.

### Chunking

The process of dividing a file into smaller parts (chunks) for independent compression. Each chunk can be compressed using the best algorithm, leading to higher compression ratios and efficiency.

### Embedding

A numeric representation of a file chunk generated using a machine learning model. Embeddings help understand the context and content of data, improving retrieval and deduplication.

### Foreign Function Interface (FFI)

A mechanism that allows the MoonBall Archiver to call functions written in other programming languages like **Python**, enabling interoperability with existing libraries.

### Machine Learning Model

MoonBall uses a **Random Forest Classifier** (Python version) or predictive rules to select the most suitable compression algorithm for each file chunk based on features such as entropy and file extension.

### 2FA (Two-Factor Authentication)

A security feature that requires users to provide a One-Time Password (OTP) generated from a secret key, adding an additional layer of security when extracting files from encrypted archives.

## Command-Line Flags

Here is a list of available command-line flags:

- `--add`: Add files or directories to the archive.
- `--extract`: Extract files from an existing archive.
- `--output`: Specify the output file name or directory.
- `--scheme`: Choose a compression scheme (`fast`, `balanced`, `max`).
- `--extension`: Set the archive file extension (`mnbl` or `🌕`).
- `--gui`: Launch the graphical user interface.
- `--search`: Perform a semantic search query to find files based on context.
- `--encryption`: Enable strong password-protected encryption for your archive.
- `--2fa`: Enable Two-Factor Authentication for added security when extracting.
- `--help`: Display a list of available command-line flags and their usage.

## Installation

### Windows

Windows users can fully install and operate the MoonBall Archiver by:

1. **Clone or download the Repository or simply just download and run the .bat file**

   ```sh
   git clone https://github.com/BenevolenceMessiah/MoonBall_Archiver.git
   cd MoonBall_Archiver
   ```

2. **Run Run_moonball_archiver.bat**

   Run the .bat file and follow the instructions.

3. Enjoy!

### Non-Windows/Manual Installation

Follow these steps to install MoonBall Archiver in a virtual environment using Python 3.10:

1. **Clone the Repository**

   ```sh
   git clone https://github.com/BenevolenceMessiah/MoonBall_Archiver.git
   cd MoonBall_Archiver
   ```

2. **Set Up Virtual Environment**

   ```sh
   python3.10 -m venv .venv
   ```

3. **Activate Virtual Environment**

   - On Windows:

     ```sh
     .venv\Scripts\activate
     ```

   - On Linux/macOS:

     ```sh
     source .venv/bin/activate
     ```

4. **Install Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

5. **Add the MoonBall Icon**
   - Place the `moonball_icon.png` file in an `assets` folder located in the same directory as the Python script (`moonball_archiver.py`).

6. **Install Rust Toolchain**

   If you want to use the Rust implementation, make sure to have Rust installed:

   ```sh
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   rustup update
   ```

   Additionally, place `moonball_archiver.rs` and `generate_embedding.py` in the root directory.

## Usage

### Via Command-Line Interface (CLI)

#### Adding Files or Directories to an Archive

To add files or directories to a MoonBall archive:

```sh
cargo run --release -- --add file1.txt dir1 --output archive.mnbl
```

Or using the optional emoji-based extension:

```sh
cargo run --release -- --add file1.txt dir1 --output archive.🌕
```

#### Extracting Files from an Archive

To extract an archive:

```sh
cargo run --release -- --extract archive.mnbl --output extracted_files/ --otp 123456
```

#### Launching the GUI

To launch the MoonBall GUI:

```sh
cargo run --release -- --gui
```

### Graphical User Interface (GUI)

- **Add Files**: Use the "Add Files" button to select files to add to the archive.
- **Add Directory**: Use the "Add Directory" button to add all files from a folder.
- **Compress to Archive**: After adding files, click "Compress to Archive" to create the `.mnbl` archive.
- **Extract Archive**: Select an archive and destination directory to extract the files.
- **2FA Extraction**: If 2FA is enabled, you will be prompted to enter an OTP to proceed.

## Example Scenarios

### Scenario 1: Archiving a Project Directory

A user wants to compress a project directory containing source code, documentation, and assets. They add the directory using the GUI, select the **Balanced** scheme, and save the archive as `project.mnbl` or `project.🌕`. The MoonBall Archiver intelligently divides the contents into chunks and applies the best algorithm to each, resulting in a compact archive.

### Scenario 2: Compressing Media Files

A user has several large video files they need to archive efficiently. Using the CLI, they choose the **Maximum Compression** scheme and save the files in `videos.mnbl` or `videos.🌕`. MoonBall optimizes compression by splitting video files at keyframes and applying the most efficient algorithm, maximizing the storage savings.

### Scenario 3: Semantic File Retrieval

With its RAG-based retrieval system, MoonBall provides the potential for **semantic-based search** in future versions. A user could search for files based on context or descriptions instead of specific filenames, revolutionizing data accessibility.

### Scenario 4: Secure Extraction with 2FA

A user wants to protect their archive from unauthorized access. They enable **Two-Factor Authentication (2FA)** when creating the archive. To extract the files, the user must enter a valid One-Time Password (OTP) to proceed, ensuring the safety of their sensitive data.

## Further Expansion

### Two-Factor Authentication (2FA) for Archive Access

In future versions, we plan to implement **Two-Factor Authentication (2FA)** for enhanced security when accessing encrypted MoonBall archives. This will provide an additional layer of protection for sensitive data, ensuring that only authorized users can access the content.

### Rust-Based Implementation

In future versions, MoonBall will implement a parallel version in **Rust** to provide enhanced performance. Rust's memory safety and concurrency capabilities would allow us to mix and match Python and Rust libraries for even greater efficiency in compression and archiving.

### Interoperability with Moon

- Leveraging existing compression libraries via FFI is essential for integrating MoonBall's features into the **Moon Programming Language**. This will allow users of Moon to interact with MoonBall seamlessly, leveraging Moon's capabilities for future AI integration.
- Utilizing Moon’s standard library for file I/O and other basic functionalities will help streamline further development and make MoonBall a perfect match for the Moon ecosystem.

## Contributions

Contributions are welcome! Feel free to submit issues or pull requests on our [GitHub Repository](https://github.com/BenevolenceMessiah/MoonBall_Archiver).

## Support Us

If you like our work, please consider supporting us:

- **Bitcoin Wallet**: `bc1q4fwzcfpcm0s6pda7grt3w9a6hqyyxrzf68thcf`
- **Ethereum Wallet**: `0x775b3Ba958ceA83Ed567BAe6eC136e121877508D`

Thank you for your support!

## Join Our Community

- [Discord Group](https://discord.gg/sUaj4xC9): Join the discussion, share your thoughts, and connect with like-minded developers and users!

## License

MoonBall Archiver is an open-source project licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

MoonBall Archiver isn't just another file compression tool; it’s a vision for the future of data storage and retrieval. Leveraging machine learning, adaptive chunking, and extensible architecture, MoonBall pushes the boundaries of what’s possible in digital archiving. Get started today and be part of the future!
