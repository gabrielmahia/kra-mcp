# AI-KungFU East Africa MCP Server
# Glama-compatible Dockerfile for kra-mcp
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/gabrielmahia/kra-mcp"
LABEL org.opencontainers.image.description="kra-mcp — East Africa AI Coordination Infrastructure"
LABEL org.opencontainers.image.licenses="MIT"

RUN pip install --no-cache-dir kra-mcp

CMD ["kra-mcp"]
