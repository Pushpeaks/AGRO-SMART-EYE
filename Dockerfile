# Stage 1: Build the React Frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
# Since VITE_API_URL is empty in production, it will use the relative path automatically
RUN npm run build

# Stage 2: Setup Python Backend and Serve
FROM python:3.10-slim

# Create a user to avoid running as root (required by Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy requirements and install dependencies
COPY --chown=user backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and model
COPY --chown=user backend/ ./backend/

# Copy built frontend assets from stage 1
COPY --chown=user --from=frontend-build /app/frontend/dist ./frontend/dist

# Expose the default port for Hugging Face
EXPOSE 7860
ENV PORT=7860

# Set working directory to backend so relative file loads work properly
WORKDIR /app/backend

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
