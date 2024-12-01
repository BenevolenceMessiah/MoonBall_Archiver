use std::fs;
use std::process::Command;
use std::path::Path;
use log::{info, error};

const MODEL_DOWNLOAD_PATH: &str = "./models";

fn main() {
    env_logger::Builder::from_default_env()
        .filter_level(log::LevelFilter::Info)
        .init();

    match download_model("distilbert-base-uncased") {
        Ok(_) => info!("Model downloaded successfully."),
        Err(e) => error!("Error downloading model: {}", e),
    }
}

fn download_model(model_name: &str) -> Result<(), Box<dyn std::error::Error>> {
    let model_path = format!("{}/{}", MODEL_DOWNLOAD_PATH, model_name);
    if Path::new(&model_path).exists() {
        info!("Model '{}' already exists.", model_name);
        return Ok(());
    }

    // Create the models directory if it doesn't exist
    fs::create_dir_all(MODEL_DOWNLOAD_PATH)?;

    let output = Command::new("curl")
        .arg("-L")
        .arg(format!("https://huggingface.co/{}/resolve/main/pytorch_model.bin", model_name))
        .arg("-o")
        .arg(&model_path)
        .output()?;

    if !output.status.success() {
        return Err(Box::new(std::io::Error::new(
            std::io::ErrorKind::Other,
            format!("Failed to download model: {}", String::from_utf8_lossy(&output.stderr)),
        )));
    }

    Ok(())
}

fn list_models() -> Result<(), Box<dyn std::error::Error>> {
    let paths = fs::read_dir(MODEL_DOWNLOAD_PATH)?;

    if !paths.count() > 0 {
        info!("No models available.");
        return Ok(());
    }

    for path in paths {
        info!("Model: {}", path?.path().display());
    }

    Ok(())
}

fn delete_model(model_name: &str) -> Result<(), Box<dyn std::error::Error>> {
    let model_path = format!("{}/{}", MODEL_DOWNLOAD_PATH, model_name);
    if Path::new(&model_path).exists() {
        fs::remove_file(&model_path)?;
        info!("Model '{}' deleted successfully.", model_name);
    } else {
        info!("Model '{}' not found.", model_name);
    }

    Ok(())
}

fn model_exists(model_name: &str) -> bool {
    let model_path = format!("{}/{}", MODEL_DOWNLOAD_PATH, model_name);
    Path::new(&model_path).exists()
}