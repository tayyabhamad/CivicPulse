# ADR 003: Container networking

Compose separates `edge` from internal `data`. Frontend joins only edge; PostgreSQL and Redis join only data; backend bridges both. This limits blast radius while preserving the backend’s hosted-LLM route.
