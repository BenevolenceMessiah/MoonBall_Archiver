use std::fs::{File, OpenOptions};
use std::io::{Read, Write, BufReader, BufWriter, Seek, SeekFrom};
use zstd::stream::{copy_encode, copy_decode};
use brotli;
use lzma;
use serde::{Serialize, Deserialize};
use rayon::prelude::*;
use clap::{App, Arg};
use std::collections::HashMap;
use std::sync::Mutex;
use crypto::aes::{KeySize, cbc_encryptor, cbc_decryptor};
use crypto::buffer::{RefReadBuffer, RefWriteBuffer, BufferResult};
use crypto::symmetriccipher::{Encryptor, Decryptor};
use crypto::sha2::Sha256;
use crypto::hmac::Hmac;
use crypto::mac::Mac;
use eframe::egui;
use ndarray::Array1;
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};
use base32::Alphabet::RFC4648;
use base32;
use rand::Rng;
use totp_lite::totp_custom;
use log::{info, error};

#[derive(Serialize, Deserialize, Debug)]
struct ChunkMetadata {
    file_name: String,
    chunk_id: usize,
    original_size: usize,
    compressed_size: usize,
    compression_algo: String,
    embedding: Option<Vec<f32>>, // Embedding for semantic search
}

#[derive(Serialize, Deserialize, Debug)]
struct ArchiveMetadata {
    chunks: Vec<ChunkMetadata>,
    encryption_enabled: bool,
    requires_2fa: bool,
    secret_key: Option<String>, // 2FA Secret Key
}

pub struct MoonBallArchive {
    metadata: ArchiveMetadata,
    files: Mutex<HashMap<String, Vec<u8>>>, // Cache to store compressed chunks in memory for parallel operations
    config: Config,
}

#[derive(Serialize, Deserialize, Debug)]
struct Config {
    preset: String,
    custom_models: HashMap<String, String>,
    multi_modal_model: String,
    fallback_model: String,
    fallback_provider_settings: FallbackProviderSettings,
    caching: bool,
    model_download_path: String,
    logging_level: String,
    parallel_threads: String,
    compression_level: u8,
    chunk_size: usize,
    error_handling: String,
    auto_update_models: bool,
    scheme: String,
    preset_configs: HashMap<String, PresetConfig>,
    semantic_search: SemanticSearchConfig,
    encryption: EncryptionConfig,
    two_factor_authentication: TwoFactorAuthenticationConfig,
    compression_algorithms: CompressionAlgorithmsConfig,
    logging: LoggingConfig,
}

#[derive(Serialize, Deserialize, Debug)]
struct FallbackProviderSettings {
    ollama: OllamaSettings,
    openai: OpenAISettings,
}

#[derive(Serialize, Deserialize, Debug)]
struct OllamaSettings {
    provider: String,
    model: String,
    contextLength: u32,
    systemMessage: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct OpenAISettings {
    provider: String,
    model: String,
    contextLength: u32,
    apiKey: String,
    apiBase: String,
    systemMessage: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct PresetConfig {
    custom_models: HashMap<String, String>,
    multi_modal: bool,
}

#[derive(Serialize, Deserialize, Debug)]
struct SemanticSearchConfig {
    threshold: f32,
}

#[derive(Serialize, Deserialize, Debug)]
struct EncryptionConfig {
    algorithm: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct TwoFactorAuthenticationConfig {
    enabled: bool,
    issuer: String,
    algorithm: String,
    period: u32,
}

#[derive(Serialize, Deserialize, Debug)]
struct CompressionAlgorithmsConfig {
    brotli: BrotliConfig,
    lzma: LzmaConfig,
    zstd: ZstdConfig,
}

#[derive(Serialize, Deserialize, Debug)]
struct BrotliConfig {
    level: u32,
}

#[derive(Serialize, Deserialize, Debug)]
struct LzmaConfig {
    preset: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct ZstdConfig {
    level: i32,
}

#[derive(Serialize, Deserialize, Debug)]
struct LoggingConfig {
    file_path: String,
    max_size_mb: u32,
    backup_count: u32,
}

impl MoonBallArchive {
    pub fn new() -> Self {
        let config = load_config().expect("Failed to load configuration");
        MoonBallArchive {
            metadata: ArchiveMetadata {
                chunks: Vec::new(),
                encryption_enabled: false,
                requires_2fa: config.two_factor_authentication.enabled,
                secret_key: None, // Initialize with actual secret key
            },
            files: Mutex::new(HashMap::new()),
            config,
        }
    }

    pub fn add_file(&self, file_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        let file = File::open(file_path)?;
        let mut reader = BufReader::new(file);
        let mut buffer = vec![0; self.config.chunk_size];
        let mut chunk_id = 0;

        while let Ok(size) = reader.read(&mut buffer) {
            if size == 0 {
                break;
            }
            self.compress_chunk(&buffer[..size], file_path, chunk_id)?;
            chunk_id += 1;
        }

        Ok(())
    }

    fn compress_chunk(&self, chunk: &[u8], file_path: &str, chunk_id: usize) -> Result<(), Box<dyn std::error::Error>> {
        let algo = self.predict_compression_algo(chunk);
        let compressed_data = match algo.as_str() {
            "brotli" => brotli::CompressorReader::new(chunk, 4096, self.config.compression_algorithms.brotli.level as usize).read_to_end(&mut Vec::new())?,
            "lzma" => lzma::LzmaWriter::new_compressor(Vec::new(), self.config.compression_algorithms.lzma.preset.as_str()).write_all(chunk)?.get_buffer().to_vec(),
            _ => {
                let mut output = Vec::new();
                copy_encode(&mut &chunk[..], &mut output, self.config.compression_algorithms.zstd.level)?;
                output
            }
        };

        if self.metadata.encryption_enabled {
            let encrypted_data = self.encrypt_data(&compressed_data)?;
            compressed_data = encrypted_data;
        }

        let base64_chunk = base64::encode(chunk);
        let output = Command::new("python3")
            .arg("generate_embedding.py")
            .arg(base64_chunk)
            .output()?;
        
        if !output.status.success() {
            return Err(Box::new(std::io::Error::new(
                std::io::ErrorKind::Other,
                format!("Failed to generate embedding: {}", String::from_utf8_lossy(&output.stderr)),
            )));
        }

        let output_str = String::from_utf8(output.stdout)?;
        let embedding: Vec<f32> = serde_json::from_str(&output_str)?;

        let metadata = ChunkMetadata {
            file_name: file_path.to_string(),
            chunk_id,
            original_size: chunk.len(),
            compressed_size: compressed_data.len(),
            compression_algo: algo.clone(),
            embedding: Some(embedding),
        };

        self.metadata.chunks.push(metadata);

        // Save compressed data to memory cache
        let mut files = self.files.lock().unwrap();
        files.insert(format!("{}_{}.mbc", file_path, chunk_id), compressed_data);

        Ok(())
    }

    fn predict_compression_algo(&self, _chunk: &[u8]) -> String {
        // Placeholder ML logic
        "zstd".to_string()
    }

    pub fn save_archive(&self, archive_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        let archive_file = File::create(archive_path)?;
        let mut writer = BufWriter::new(archive_file);

        let metadata_json = serde_json::to_string(&self.metadata)?;

        if self.metadata.encryption_enabled {
            let encrypted_metadata = self.encrypt_data(metadata_json.as_bytes())?;
            writer.write_all(&encrypted_metadata)?;
        } else {
            writer.write_all(metadata_json.as_bytes())?;
        }

        writer.write_all(b"\n")?;

        for (file_name, data) in self.files.lock().unwrap().iter() {
            writer.write_all(data)?;
            writer.write_all(b"\n")?;
        }

        let checksum = format!("{:x}", md5::compute(metadata_json));
        if self.metadata.encryption_enabled {
            let encrypted_checksum = self.encrypt_data(checksum.as_bytes())?;
            writer.write_all(&encrypted_checksum)?;
        } else {
            writer.write_all(checksum.as_bytes())?;
        }

        Ok(())
    }

    pub fn extract(&self, archive_path: &str, output_dir: &str) -> Result<(), Box<dyn std::error::Error>> {
        if self.metadata.requires_2fa {
            let secret_key = self.metadata.secret_key.clone().ok_or("2FA secret key missing")?;
            let current_time = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();
            let expected_otp = totp_custom::<Sha256>(&secret_key, current_time, 30, 6, &RFC4648 { padding: false });
            if let Some(provided_otp) = self.ask_for_otp() {
                if provided_otp != expected_otp {
                    return Err(Box::new(std::io::Error::new(
                        std::io::ErrorKind::PermissionDenied,
                        "Invalid OTP",
                    )));
                }
            } else {
                return Err(Box::new(std::io::Error::new(
                    std::io::ErrorKind::PermissionDenied,
                    "OTP required for extraction",
                )));
            }
        }

        let archive_file = File::open(archive_path)?;
        let mut reader = BufReader::new(archive_file);
        let mut metadata_str = String::new();
        reader.read_line(&mut metadata_str)?;

        if self.metadata.encryption_enabled {
            let decrypted_metadata = self.decrypt_data(metadata_str.as_bytes())?;
            let metadata: ArchiveMetadata = serde_json::from_slice(&decrypted_metadata)?;
        } else {
            let metadata: ArchiveMetadata = serde_json::from_str(&metadata_str)?;
        }

        for (index, chunk_metadata) in metadata.chunks.iter().enumerate() {
            let mut compressed_data = vec![0; chunk_metadata.compressed_size];
            reader.read_exact(&mut compressed_data)?;

            if self.metadata.encryption_enabled {
                let decrypted_chunk = self.decrypt_data(&compressed_data)?;
                compressed_data = decrypted_chunk;
            }

            let output_path = std::path::Path::new(output_dir).join(&chunk_metadata.file_name);
            let mut output_file = File::create(&output_path)?;

            match chunk_metadata.compression_algo.as_str() {
                "brotli" => {
                    let mut decompressor = brotli::Decompressor::new(&compressed_data[..], 4096);
                    std::io::copy(&mut decompressor, &mut output_file)?;
                }
                "lzma" => {
                    let mut decompressor = lzma::LzmaReader::new_decompressor(&compressed_data[..])?;
                    std::io::copy(&mut decompressor, &mut output_file)?;
                }
                _ => {
                    copy_decode(&mut &compressed_data[..], &mut output_file)?;
                }
            }
        }

        Ok(())
    }

    fn encrypt_data(&self, data: &[u8]) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
        let salt = rand::thread_rng().gen::<[u8; 16]>();
        let kdf = Hmac::<Sha256>::new_from_slice(b"moonball").unwrap();
        let mut mac = kdf.clone();
        mac.update(&salt);
        let key = mac.finalize().into_bytes();

        let iv = rand::thread_rng().gen::<[u8; 16]>();
        let cipher = cbc_encryptor(KeySize::KeySize256, &key[..], &iv[..], crypto::blockmodes::PkcsPadding);
        let mut final_result = Vec::<u8>::new();
        let mut read_buffer = RefReadBuffer::new(data);
        let mut buffer = [0; 4096];
        let mut write_buffer = RefWriteBuffer::new(&mut buffer);

        loop {
            let result = cipher.encrypt(&mut read_buffer, &mut write_buffer, true)?;
            final_result.extend(write_buffer.take_read_buffer().take_remaining());
            match result {
                BufferResult::BufferUnderflow => break,
                BufferResult::BufferOverflow => {}
            }
        }

        Ok([salt.to_vec(), iv.to_vec(), final_result].concat())
    }

    fn decrypt_data(&self, data: &[u8]) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
        let salt = &data[..16];
        let iv = &data[16..32];
        let kdf = Hmac::<Sha256>::new_from_slice(b"moonball").unwrap();
        let mut mac = kdf.clone();
        mac.update(salt);
        let key = mac.finalize().into_bytes();

        let cipher = cbc_decryptor(KeySize::KeySize256, &key[..], iv, crypto::blockmodes::PkcsPadding);
        let mut final_result = Vec::<u8>::new();
        let mut read_buffer = RefReadBuffer::new(&data[32..]);
        let mut buffer = [0; 4096];
        let mut write_buffer = RefWriteBuffer::new(&mut buffer);

        loop {
            let result = cipher.decrypt(&mut read_buffer, &mut write_buffer, true)?;
            final_result.extend(write_buffer.take_read_buffer().take_remaining());
            match result {
                BufferResult::BufferUnderflow => break,
                BufferResult::BufferOverflow => {}
            }
        }

        Ok(final_result)
    }

    fn ask_for_otp(&self) -> Option<String> {
        println!("Enter 2FA OTP: ");
        let mut input = String::new();
        std::io::stdin().read_line(&mut input).ok()?;
        Some(input.trim().to_string())
    }
}

fn load_config() -> Result<Config, Box<dyn std::error::Error>> {
    let config_path = "config.yml";
    let file = File::open(config_path)?;
    let reader = BufReader::new(file);
    let config: Config = serde_yaml::from_reader(reader)?;

    Ok(config)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::Builder::from_default_env()
        .filter_level(log::LevelFilter::Info)
        .init();

    let matches = App::new("MoonBall Archiver")
        .version("1.0")
        .author("Your Name <your.email@example.com>")
        .about("A Rust implementation of MoonBall Archiver")
        .arg(
            Arg::with_name("add")
                .short('a')
                .long("add")
                .value_name("FILES/DIRECTORIES")
                .help("Files or directories to add to the archive")
                .multiple(true)
                .takes_value(true),
        )
        .arg(
            Arg::with_name("extract")
                .short('e')
                .long("extract")
                .value_name("ARCHIVE")
                .help("Archive to extract")
                .takes_value(true),
        )
        .arg(
            Arg::with_name("output")
                .short('o')
                .long("output")
                .value_name("DIR/FILENAME")
                .help("Output directory or archive name")
                .takes_value(true)
                .required_unless_one(&["add", "gui"]),
        )
        .arg(
            Arg::with_name("scheme")
                .short('s')
                .long("scheme")
                .possible_values(&["fast", "balanced", "max"])
                .default_value("balanced")
                .help("Compression scheme"),
        )
        .arg(
            Arg::with_name("extension")
                .short('x')
                .long("extension")
                .possible_values(&["mnbl", "🌕"])
                .default_value("mnbl")
                .help("File extension for the archive"),
        )
        .arg(
            Arg::with_name("gui")
                .short('g')
                .long("gui")
                .help("Launch graphical user interface"),
        )
        .arg(
            Arg::with_name("search")
                .short('S')
                .long("search")
                .value_name("QUERY")
                .help("Semantic search query")
                .takes_value(true),
        )
        .get_matches();

    if matches.is_present("gui") {
        // Launch GUI here (not implemented yet)
        println!("GUI not implemented yet.");
    } else if let Some(files) = matches.values_of("add") {
        let output_path = matches.value_of("output").unwrap();
        let extension = matches.value_of("extension").unwrap();

        let mut archive = MoonBallArchive::new();
        for file in files {
            if std::path::Path::new(file).is_dir() {
                // Add directory logic here (not implemented yet)
                println!("Adding directory: {}", file);
            } else {
                archive.add_file(file)?;
            }
        }

        let final_output_path = format!("{}.{}", output_path, extension);
        archive.save_archive(&final_output_path)?;
        info!("Archive saved as {}", final_output_path);
    } else if let Some(archive_path) = matches.value_of("extract") {
        let output_dir = matches.value_of("output").unwrap();
        let mut archive = MoonBallArchive::new(); // Initialize with metadata
        archive.extract(archive_path, output_dir)?;
        info!("Files extracted to {}", output_dir);
    } else if let Some(query) = matches.value_of("search") {
        let mut archive = MoonBallArchive::new(); // Initialize with metadata
        let results = archive.semantic_search(query); // Implement semantic search in Rust (not implemented yet)
        println!("Search results: {:?}", results);
    }

    Ok(())
}