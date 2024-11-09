# MoonBall Archiver

Welcome to **MoonBall Archiver**, a cutting-edge file compression and archiving solution designed to redefine the way we store and manage digital data. MoonBall is a forward-thinking, highly efficient, and AI-powered archiver that leverages advanced compression techniques to bring you the best currently possible performance for your storage needs. With a unique blend of machine learning, chunk-level adaptability, and interoperability, MoonBall aims to be the future of digital archiving.

- [GitHub Repository](https://github.com/BenevolenceMessiah/MoonBall_Archiver)
- [Moon Programming Language Website](https://www.moonlanguage.org/)
- [Moon GitHub Repository](https://github.com/BenevolenceMessiah/Moon)
- [Join our Discord Community](https://discord.gg/sUaj4xC9)

## Key Features

### Adaptive Compression Schemes

MoonBall uses a machine learning model to determine the optimal compression algorithm for each data chunk. It chooses from multiple algorithms such as **Brotli**, **LZMA**, and **Zstandard** (Zstd), depending on the type of data and its compressibility. This results in a highly efficient compression approach tailored specifically to each data type. There are currently 3 Compression Schemes. Fast, Balanced (being the default)and Max.

### Chunk-Level Compression

The MoonBall Archiver first indexes and then divides files into logical chunks for independent compression, ensuring that each chunk is handled in the most space-efficient way possible. Chunk-level compression not only improves compression ratios but also enables parallel processing for enhanced speed.

### Comprehensive Graphical User Interface (GUI)

MoonBall includes a user-friendly GUI, allowing even beginners to easily compress and decompress files or directories. This interface provides features like:

- Adding files or directories for compression
- Saving the resulting MoonBall archive
- Extracting compressed archives
- Semantic search

### Machine Learning Enhancements

MoonBall integrates **Transformers.js** to generate embeddings for each file chunk, which enhances the retrieval, clustering, and deduplication of data. These embeddings also enable semantic-based data retrieval and adaptive chunking.

### Integration with AI Tools

MoonBall currently leverages **Retrieval-Augmented Generation (RAG)** for enhanced data retrieval, clustering, and **semantic-based search**. This further utilizes **Transformers** models for file content analysis and embedding generation. This enables MoonBall to offer features like `semantic search`, allowing users to find files based on context rather than exact filenames like traditional file manager indexing and searching, moreover, while the .mnbl archive is still compressed.

### Fun Emoji Extensions

Set the archive file extension (`.mnbl` or `.🌕`) in keeping with the spirit of the Moon Programming Language.

### Command-Line Interface (CLI)

For more advanced users, MoonBall provides a powerful CLI that allows adding files or directories, selecting compression schemes, running semantic-searches, and extracting archives directly from the terminal.

### Multi-Platform Compatibility

The MoonBall Archiver is designed with compatibility in mind, providing cross-platform functionality on both Windows and Unix-like systems.

### Extensible Design for Future Development

MoonBall has been designed with extensibility at its core, allowing for future enhancements:

- **Rust Implementation**: A parallel implementation in **Rust** to complement the Python prototype. This Rust version could mix and match existing Python and Rust libraries for performance enhancements via Moon.
- **Foreign Function Interface (FFI)**: To achieve interoperability, MoonBall leverages compression libraries via FFI or other binding mechanisms, which is crucial for integration into other languages like Moon.
- **Moon Integration**: Utilizing Moon's standard library modules for I/O, math, and other functionalities to streamline development.

## How It Works

MoonBall Archiver operates in a structured and efficient sequence:

1. **Indexing**: First, the contents of the files are indexed, which involves creating a structured list of all files and chunks. This index serves as the foundation for efficient retrieval, compression, and decompression.

2. **Chunking**: Files are then divided into logical chunks, each of which is compressed independently. This chunking process ensures that each chunk is handled in the most efficient way possible, improving both compression ratios and processing speed.

3. **Embeddings and Index Storage**: Embeddings are generated for each chunk, which help in understanding the context and content of data. The index and embeddings are stored in the header of the .mnbl archive file, allowing for efficient data retrieval and management.

4. **Checksum Footer**: A checksum is computed for the index and stored in the footer of the archive. This ensures data integrity and allows for verification during extraction.

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

A mechanism that allows the Moon Programming Language and MoonBall Archiver to call functions written in other programming languages like **C** or **Rust**, enabling interoperability with existing libraries.

### Machine Learning Model

MoonBall uses a **Random Forest Classifier** to predict the most suitable compression algorithm for each file chunk based on features such as entropy and file extension.

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

## Usage

### Via Command-Line Interface (CLI)

#### Adding Files or Directories to an Archive

To add files or directories to a MoonBall archive:

```sh
python moonball_archiver.py --add file1.txt dir1 --output archive.mnbl
```

Or using the optional emoji-based extension:

```sh
python moonball_archiver.py --add file1.txt dir1 --output archive.🌕
```

#### Extracting Files from an Archive

To extract an archive:

```sh
python moonball_archiver.py --extract archive.mnbl --output extracted_files/
```

#### Launching the GUI

To launch the MoonBall GUI:

```sh
python moonball_archiver.py --gui
```

### Graphical User Interface (GUI)

- **Add Files**: Use the "Add Files" button to select files to add to the archive.
- **Add Directory**: Use the "Add Directory" button to add all files from a folder.
- **Compress to Archive**: After adding files, click "Compress to Archive" to create the `.mnbl` archive.
- **Extract Archive**: Select an archive and destination directory to extract the files.

## Example Scenarios

### Scenario 1: Archiving a Project Directory

A user wants to compress a project directory containing source code, documentation, and assets. They add the directory using the GUI, select the **Balanced** scheme, and save the archive as `project.mnbl` or `project.🌕`. The MoonBall Archiver intelligently divides the contents into chunks and applies the best algorithm to each, resulting in a compact archive.

### Scenario 2: Compressing Media Files

A user has several large video files they need to archive efficiently. Using the CLI, they choose the **Maximum Compression** scheme and save the files in `videos.mnbl` or `videos.🌕`. MoonBall optimizes compression by splitting video files at keyframes and applying the most efficient algorithm, maximizing the storage savings.

### Scenario 3: Semantic File Retrieval

With its RAG-based retrieval system, MoonBall provides the potential for **semantic-based search** in future versions. A user could search for files based on context or descriptions instead of specific filenames, revolutionizing data accessibility.

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
