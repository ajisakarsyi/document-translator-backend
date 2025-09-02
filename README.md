# Multilingual Document Translator API

This FastAPI application provides an API for translating documents (PDF, DOCX, PPTX) between supported languages using the Ollama large language model (LLM). It preserves the formatting of the original documents and reconstructs translated files accordingly.

---

## Requirements

- Python 3.8+
- pip (Python package manager)

---

## Installation

1. **Clone the repository or download the code.**
2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=mistral-nemo:12b
```

You can adjust the `OLLAMA_MODEL_NAME` according to the model you have installed in Ollama.

---

## How to Run

Start the FastAPI server with:

```bash
uvicorn main:app --reload
```

Once running, the API will be available at `http://localhost:8000`.

You can access the interactive Swagger UI at:

```
http://localhost:8000/docs
```

---

## Supported File Types

- `.pdf` - Converted internally to DOCX before translation.
- `.docx` - Translates all paragraphs.
- `.pptx` - Translates all text from shapes per slide.

---

## Supported Languages

- English
- Japanese
- Indonesian
- French
- Spanish
- German

---

## API Usage

### Endpoint: `/translate-document/`

**Method:** `POST`  
**Form Parameters:**

- `file`: UploadFile (PDF, DOCX, PPTX)
- `source_language`: One of the supported languages
- `target_language`: One of the supported languages

### Example using `curl`:

```bash
curl -X 'POST'   'http://localhost:8000/translate-document/'   -F 'file=@yourfile.pdf'   -F 'source_language=English'   -F 'target_language=Japanese'   --output translated_file.docx
```

---

## Notes

- PDF translation converts the file to DOCX format.
- PPTX slides must contain editable text (non-image text).
- Requires a running Ollama server with the specified model downloaded.

---

## License

This project is provided as-is for demonstration purposes. Please respect licenses of underlying packages and models.
