# CLAUDE.md

回显的思考以及回复尽可能使用中文。

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CompressPasswordProbe is a GUI-based password cracking tool for compressed archives (ZIP, 7Z, RAR), built with Python 3 and PySide6. It uses dictionary attacks and optionally GPU acceleration to test passwords against encrypted archive files.

**⚠️ Security Notice**: This is a defensive security tool intended for legitimate password recovery and security testing. Only use on archives you own or have explicit permission to test.

## Development Commands

### Environment Setup

```bash
# Create virtual environment and install dependencies
python -m venv venv

# Windows activation
.\venv\Scripts\activate

# Linux/macOS activation  
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Direct execution
python main.py

# Platform-specific scripts
# Windows
setup.bat

# Linux/macOS
./setup.sh
```

### Building and Packaging

```bash
# Build executable using custom build script
python build.py

# Direct PyInstaller usage
pyinstaller CompressPasswordProbe.spec

# Clean build artifacts
python -c "import shutil; [shutil.rmtree(d, ignore_errors=True) for d in ['build', 'dist', '__pycache__']]"
```

## Architecture Overview

### Core Components

**Main Application Flow**: `main.py` → `gui/main_window_simple.py` → Core modules

**Archive Handling (`core/archive_handler.py`)**:

- Abstract `ArchiveHandler` base class with pluggable format handlers
- `ZipHandler`, `SevenZipHandler`, `RarHandler` - Format-specific implementations
- `ArchiveManager` - Facade coordinating all handlers and volume detection
- Supports multi-volume archives (split archives like .z01, .r00, .7z.001)

**Password Cracking (`core/crack_engine.py`)**:

- `PasswordCrackEngine` - Main engine with Qt signals for UI communication
- `PasswordCrackWorker` - QThread worker for background processing  
- Dual-mode processing: CPU sequential testing vs GPU batch processing
- Performance monitoring with speed metrics and slow password detection

**Dictionary Processing (`core/dictionary.py`)**:

- `DictionaryReader` - Efficient streaming reader for large dictionary files
- Memory-efficient batch processing for GPU mode
- Encoding detection and error handling

**GPU Acceleration (`core/gpu_accelerator.py`)**:

- `GPUManager` - CUDA/OpenCL detection and management
- Optional GPU acceleration for batch password testing
- Automatic CPU fallback if GPU unavailable

### Key Design Patterns

- **Strategy Pattern**: Pluggable archive handlers for different formats
- **Observer Pattern**: Qt signals/slots for UI updates from background workers
- **Factory Pattern**: Archive format detection and handler selection
- **Template Method**: Abstract base classes with concrete implementations

### Multi-Volume Archive Support

The system automatically detects and handles split archives:

- ZIP: `.zip` + `.z01`, `.z02`, etc.
- RAR: `.rar` + `.r00`, `.r01` or `.part1.rar`, `.part2.rar`
- 7Z: `.7z.001`, `.7z.002`, etc.

## External Tool Dependencies

### Required for Full Functionality

- **7-Zip**: Required for advanced 7Z archive handling (`7z.exe` or `7za.exe`)
  - Fallback: py7zr library (limited support for complex archives)
- **WinRAR/UnRAR**: Required for accurate RAR password validation
  - Fallback: rarfile library (may produce false positives without external tool)

### Tool Detection Logic

The system automatically searches common installation paths:

- Windows: `C:\Program Files\7-Zip\`, `C:\Program Files\WinRAR\`  
- PATH environment: `7z.exe`, `rar.exe`, `unrar.exe`

## Configuration System

Configuration managed via `core/config.py` with JSON persistence in `config.json`:

```python
# Key configuration options
{
    "gpu_acceleration": bool,    # Enable GPU processing
    "max_attempts": int,         # Limit password attempts (0 = unlimited)
    "batch_size": int,           # GPU batch size (default: 1000)
    "max_threads": int,          # CPU thread limit
    "log_level": str            # Logging verbosity
}
```

## Threading and Performance

### Thread Architecture

- **Main Thread**: GUI event handling (PySide6)
- **Worker Thread**: Password cracking (`PasswordCrackWorker` QThread)
- **Background Tasks**: File I/O, dictionary loading

### Performance Considerations

- Large archives trigger timeout protection and partial content testing
- Dictionary files are streamed to handle large wordlists efficiently
- GPU batching reduces per-password overhead for supported operations
- Automatic slow password detection with user warnings

## Development Guidelines

### Working with Archive Handlers

- Always test against the first volume for multi-volume archives
- Implement timeout protection for operations that may hang
- Prefer partial content reading over full extraction for password validation
- Handle external tool availability gracefully with fallback methods

### Adding New Archive Formats

1. Create new handler class inheriting from `ArchiveHandler`
2. Implement `test_password()` and `extract_info()` methods
3. Add format detection logic to `ArchiveManager._detect_archive_type()`
4. Register handler in `ArchiveManager.handlers` dictionary

### GPU Integration

- GPU acceleration is optional and automatically disabled if unavailable
- Always provide CPU fallback for all GPU-accelerated operations
- Test both GPU and CPU code paths during development

## Testing Files

Several test scripts exist for development and debugging:

- `test_*.py` - Unit tests for specific components
- `debug_*.py` - Debugging tools for development
- `verify_*.py` - Validation scripts for fixes

Run tests individually as needed:

```bash
python test_complete_functionality.py
python debug_password.py [archive_path] [password]
```

## Logging

Comprehensive logging via `core/logger.py`:

- Automatic log file rotation in `logs/` directory  
- Configurable log levels
- Performance metrics and error tracking
- Thread-safe logging for concurrent operations
