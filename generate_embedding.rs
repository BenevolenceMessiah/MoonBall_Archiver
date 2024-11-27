use std::process::Command;
use base64::{Engine as _, engine::general_purpose};

fn generate_embedding(input_bytes: &str) -> Result<Vec<f32>, Box<dyn std::error::Error>> {
    let decoded_bytes = general_purpose::STANDARD.decode(input_bytes)?;
    let input_str = String::from_utf8_lossy(&decoded_bytes);

    let output = Command::new("python3")
        .arg("generate_embedding.py")
        .arg(input_str)
        .output()?;

    if !output.status.success() {
        return Err(Box::new(std::io::Error::new(
            std::io::ErrorKind::Other,
            format!("Failed to generate embedding: {}", String::from_utf8_lossy(&output.stderr)),
        )));
    }

    let output_str = String::from_utf8(output.stdout)?;
    let embeddings: Vec<f32> = serde_json::from_str(&output_str)?;

    Ok(embeddings)
}

fn main() {
    if std::env::args().len() != 2 {
        eprintln!("Usage: generate_embedding <base64_encoded_chunk>");
        return;
    }

    let input_data = std::env::args().nth(1).unwrap();
    match generate_embedding(&input_data) {
        Ok(embedding) => println!("{}", serde_json::to_string(&embedding).unwrap()),
        Err(e) => eprintln!("Error: {}", e),
    }
}