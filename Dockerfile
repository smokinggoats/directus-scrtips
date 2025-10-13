FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

EXPOSE 5000

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

COPY . /app
RUN uv sync --locked --no-install-project --no-dev
RUN uv sync --locked --no-dev

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

CMD ["uv", "run", "main.py"     ]