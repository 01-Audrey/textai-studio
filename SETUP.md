# ==================================================
# TextAI Studio - Setup Instructions
# ==================================================

## Quick Start

1. **Install Dependencies**
```bash
   pip install -r requirements.txt
```

2. **Configure Environment**
```bash
   # Copy example to .env
   cp .env.example .env

   # Edit .env and fill in your values
   nano .env
```

3. **Generate Secrets**
```bash
   # Generate SECRET_KEY
   python -c "import secrets; print(secrets.token_hex(32))"

   # Add to .env file
```

4. **Configure Streamlit (Optional)**
```bash
   # Copy example secrets
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml

   # Edit secrets
   nano .streamlit/secrets.toml
```

5. **Run Application**
```bash
   # Using launcher
   python run.py

   # Or directly
   streamlit run textai_studio_app.py
```

## Environment Variables

### Required
- `SECRET_KEY` - Session encryption (generate with command above)
- `ADMIN_PASSWORD` - Admin account password

### Optional
- `APP_ENV` - Environment (development/production)
- `DEBUG` - Enable debug mode (true/false)
- `PORT` - Server port (default: 8501)
- `MAX_UPLOAD_SIZE` - Max file size in MB (default: 10)

See `.env.example` for complete list.

## Security Checklist

- [ ] Generated strong SECRET_KEY
- [ ] Changed default ADMIN_PASSWORD
- [ ] Set DEBUG=false in production
- [ ] Reviewed all environment variables
- [ ] Added .env to .gitignore
- [ ] Never committed secrets to git

## Troubleshooting

### Dependencies
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check versions
pip list
```

### Models
```bash
# Models will download on first run
# Check MODEL_CACHE_DIR in .env
# Default: ./models
```

### Port Already in Use
```bash
# Change PORT in .env
# Or kill existing process:
# Windows: netstat -ano | findstr :8501
# Linux/Mac: lsof -ti:8501 | xargs kill
```

## Next Steps

1. Test application locally
2. Review deployment documentation
3. Prepare for Docker containerization
4. Deploy to production
