FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv pip install -e ".[dev]" --system
COPY . .
CMD ["python", "-m", "anima_def_cai"]
