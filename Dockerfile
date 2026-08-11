# ---- Stage 1: builder ----
    FROM python:3.12-slim AS builder

    WORKDIR /app
    
    COPY requirements.txt .
    
    RUN python -m pip install --upgrade pip \
        && pip install --user -r requirements.txt
    
    # ---- Stage 2: runtime ----
    FROM python:3.12-slim
    
    WORKDIR /app
    
    # Create a non-root user to run the app as.
    RUN useradd --create-home --shell /bin/bash app
    
    # Bring in only the installed dependencies from the builder stage.
    COPY --from=builder --chown=app:app /root/.local /home/app/.local
    
    # Copy only the application package needed at runtime.
    COPY --chown=app:app app ./app
    
    ENV PATH=/home/app/.local/bin:$PATH \
        PYTHONUNBUFFERED=1
    
    EXPOSE 8000
    
    HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
        CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
    
    USER app
    
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]