#!/bin/bash

echo "Setting up MCP Code Analyzer development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
# Docker 関連ファイルを置くディレクトリ
mkdir -p docker

# スクリプト格納用
mkdir -p scripts

# アプリ本体
mkdir -p src/api/endpoints
mkdir -p src/core/models
mkdir -p src/core/schemas
mkdir -p src/analyzers
mkdir -p src/knowledge
mkdir -p src/plugins/python
mkdir -p src/workers

# テスト
mkdir -p tests/unit tests/integration

# ドキュメント
mkdir -p docs

echo "Creating __init__.py files…"

# src/ 以下をパッケージ化
touch src/__init__.py

# 各機能ディレクトリ
touch src/analyzers/__init__.py
touch src/api/__init__.py
touch src/api/endpoints/__init__.py
touch src/core/__init__.py
touch src/core/models/__init__.py
touch src/core/schemas/__init__.py
touch src/knowledge/__init__.py
touch src/plugins/__init__.py       # もし python サブフォルダしかなければ不要ですが、混在する場合に
touch src/plugins/python/__init__.py
touch src/workers/__init__.py

# テストもパッケージ化
touch tests/__init__.py

# Copy environment file
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cat > .env << EOL
# Application
DEBUG=true
SECRET_KEY=your-secret-key-here-change-in-production

# Database
DATABASE_URL=postgresql+asyncpg://mcp_user:mcp_password@localhost:5432/mcp_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AI/ML
MODEL_CACHE_DIR=/tmp/mcp_models
EMBEDDING_MODEL=microsoft/codebert-base

# ChromaDB
CHROMA_PERSIST_DIR=/tmp/mcp_chroma

# Analysis
MAX_FILE_SIZE_MB=10
ANALYSIS_TIMEOUT=300
MAX_CONCURRENT_ANALYSES=4
EOL
fi


# Create .gitignore if it doesn't already exist
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'EOL'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual environments
env/
venv/
.venv

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Pytest
.pytest_cache/
.coverage
htmlcov/

# Mypy
.mypy_cache/

# Ruff
.ruff_cache/

# Environment files
.env
.env.local
.env.*.local

# IDEs and editors
.vscode/
.idea/
*.swp
*.swo
*~

# macOS
.DS_Store

# Windows
Thumbs.db

# Logs and temporary files
/logs/
/tmp/
*.log

# Docker
docker-compose.override.yml
EOL
fi


# Build Docker images
echo "Building Docker images..."
docker-compose build

# Start services
echo "Starting services..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "Initializing database..."
docker-compose run --rm api python scripts/init_db.py

echo "Development environment setup complete!"
echo ""
echo "To start the application, run:"
echo "  docker-compose up"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API docs will be available at: http://localhost:8000/api/v1/docs"
echo "Flower (Celery monitoring) will be available at: http://localhost:5555"