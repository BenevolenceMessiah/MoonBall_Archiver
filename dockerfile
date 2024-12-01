# Base image for Python dependencies
FROM python:3.10-slim as base

# Install Rust (for the Rust implementation)
RUN apt-get update && \
    apt-get install -y curl gcc g++ make && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    source $HOME/.cargo/env

# Install additional dependencies for Rust
RUN rustup update && \
    rustc --version && \
    cargo --version

# Set working directory
WORKDIR /app

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Expose any ports that might be used (for the GUI, for instance)
EXPOSE 5000

# Stage for Rust build
FROM base as rust-build
WORKDIR /app
RUN cargo build --release

# Final stage with both Python and Rust binaries
FROM base
COPY --from=rust-build /app/target/release/moonball_archiver .
COPY generate_embedding.py .

# Run the CLI tool by default (this could be changed to start the GUI if needed)
ENTRYPOINT ["./moonball_archiver"]