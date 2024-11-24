// model_manager.rs - Rust Model Manager for MoonBall Archiver

use std::fs;
use std::process::Command;
use std::path::Path;
use std::io;
use std::error::Error;

const MODEL_DOWNLOAD_PATH: &str = "./models";

fn main() {
    match download_model("distilbert-base-uncased") {
        Ok(_) => println!("Model downloaded successfully."),
        Err(e) => eprintln!("Error downloading model: {}", e),
    }
}

// Function to download a model
fn download_model(model_name: &str) -> Result<(), Box<dyn Error>> {
    let model_path = format!("{}/{}", MODEL_DOWNLOAD_PATH, model_name);
    if Path::new(&model_path).exists() {
        println!("Model '{}' already exists.", model_name);
        return Ok(());
    }

    // Create the models directory if it doesn't exist
    fs::create_dir_all(MODEL_DOWNLOAD_PATH)?;

    // Use a shell command to download the model (e.g., using wget or curl)
    let output = Command::new("curl")
        .arg("-L")
        .arg(format!("https://huggingface.co/{}/resolve/main/pytorch_model.bin", model_name))
        .arg("-o")
        .arg(&model_path)
        .output()?;

    if !output.status.success() {
        return Err(Box::new(io::Error::new(
            io::ErrorKind::Other,
            format!("Failed to download model: {}", String::from_utf8_lossy(&output.stderr)),
        )));
    }

    Ok(())
}

// Function to list available models in the models directory
fn list_models() -> Result<(), Box<dyn Error>> {
    let paths = fs::read_dir(MODEL_DOWNLOAD_PATH)?;

    for path in paths {
        println!("Model: {}", path?.path().display());
    }

    Ok(())
}

// Function to delete a model
fn delete_model(model_name: &str) -> Result<(), Box<dyn Error>> {
    let model_path = format!("{}/{}", MODEL_DOWNLOAD_PATH, model_name);
    if Path::new(&model_path).exists() {
        fs::remove_file(model_path)?;
        println!("Model '{}' deleted successfully.", model_name);
    } else {
        println!("Model '{}' not found.", model_name);
    }

    Ok(())
}

// Function to check if a model exists
fn model_exists(model_name: &str) -> bool {
    let model_path = format!("{}/{}", MODEL_DOWNLOAD_PATH, model_name);
    Path::new(&model_path).exists()
}
