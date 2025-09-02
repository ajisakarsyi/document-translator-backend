# Multilingual Document Translator API with Role-Based Authentication

This project is a **FastAPI-based document translation service** that supports **PDF, PPTX, and DOCX** files.  
It integrates with a self-hosted **Ollama LLM API** for translations and enforces **role-based authentication** (User/Admin) via an external Auth server.

---

## Features

- **Authentication & Authorization**
  - OAuth2 token introspection against external Auth server
  - Role-based access (`user` vs `admin`)
- **Document Support**
  - Upload & translate **PDF → DOCX**, **DOCX**, **PPTX**
- **Translation Backend**
  - Uses **Ollama** self-hosted LLM API
  - Preserves formatting, placeholders, and line breaks
- **Health Checks**
  - `/health` (basic)
  - `/health/auth` (requires valid token)
- **User Identity**
  - `/whoami` returns token claims

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally or remotely
- An OAuth2-compliant Authentication Server (e.g., Authentik, Keycloak)

---

## Installation

1. **Clone the repository or download the code.**
2. **Create a virtual environment (recommended):**
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
# Auth server config
AUTH_SERVER_URL=http://localhost:4000
INTROSPECTION_ENDPOINT=/connect/introspect
AUTH_CLIENT_ID=your-client-id
AUTH_CLIENT_SECRET=your-client-secret
REQUIRED_AUDIENCE=auth-template-api
REQUIRED_SCOPES=read write

# Ollama config
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=mistral-nemo:12b
```

You can adjust the `OLLAMA_MODEL_NAME` according to the model you have installed in Ollama.

---

## Running the API

Start the FastAPI server with:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
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

## API Endpoints

### Health
- `GET /health` → basic health check
- `GET /health/auth` → requires valid token

### Authenticated Identity
- `GET /whoami` → returns token subject, client, scopes, role

### Document Workflow
- `POST /user/upload` → user uploads document (pending approval)
- `POST /admin/upload` → admin uploads and auto-approves
- `POST /admin/approve/{request_id}` → admin approves user uploads

### Translation
- `POST /translate-document/`  
  **Form Data:**
  - `file`: PDF, DOCX, PPTX
  - `source_language`: one of [English, Japanese, Indonesian, French, Spanish, German]
  - `target_language`: same list (must differ from source)

Returns the translated file in the correct format.

---

## Example Usage (cURL)

```bash
curl -X POST "http://localhost:8000/translate-document/"   -H "Authorization: Bearer <ACCESS_TOKEN>"   -F "source_language=English"   -F "target_language=Indonesian"   -F "file=@document.pdf"   -o translated.docx
```

---

## Notes

- PDF translation converts the file to DOCX format.
- PPTX slides must contain editable text (non-image text).
- Requires a running Ollama server with the specified model downloaded.
- Authentication caching is done using `cachetools.TTLCache`.
- This project is **not production-hardened**; persistent storage is not included.

---

## License

MIT
