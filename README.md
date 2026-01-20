chess-analysis-api
♟️ Chess Analysis API

Production-grade FastAPI backend for chess game analysis and engine play using Stockfish. Designed with clean architecture, performance-aware engine pooling, and extensible domain logic.

This project focuses on correct system design, clear separation of concerns, and real-world backend practices, not just chess logic.

🚀 Features Game Analysis

Full PGN game analysis

Move-by-move evaluation (before/after)

Move quality classification:

BOOK, BRILLIANT, BEST, GOOD, INACCURACY, MISTAKE, BLUNDER

Key moments detection (blunders, turning points, missed wins)

Opening detection with ECO codes & names

Opening book recognition (excluded from stats)

Performance Metrics

Average Centipawn Loss (ACPL)

Accuracy percentage

Mistake / blunder counts

Estimated playing strength (ELO + confidence)

Engine Play

Stateless play-vs-engine endpoint

Supports mid-game positions via FEN

Native Stockfish ELO limiting (where supported)

Humanized engine behavior for lower ELOs

Adaptive depth scaling based on ELO

🧱 Architecture

The codebase follows a clean, layered architecture with strict boundaries:

app/ ├── api/ # FastAPI routers (thin controllers) ├── services/ # Orchestration & business flow ├── domain/ # Pure chess logic (no FastAPI / engine imports) ├── infrastructure/ # Stockfish engine pool & wrappers ├── schemas/ # Request/response contracts ├── core/ # Configuration & application lifecycle Design Principles

Domain layer is framework-independent

Services orchestrate, domain computes

No global engine state

Additive-only architecture

Request-scoped engine usage

⚙️ Engine Management

Thread-safe Stockfish engine pool

Engines are:

Pre-created on startup

Acquired per request

Safely released after use

Prevents engine exhaustion and resource leaks

Supports concurrent analysis requests

📡 API Endpoints Analyze Game

POST /api/v1/analysis

{ "pgn": "1.e4 e5 2.Nf3 Nc6 ..." }

Returns:

Move-by-move analysis

Summary statistics

Key moments

Opening information

Estimated ELO

Play vs Engine

POST /api/v1/play/move

{ "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1", "elo": 1200 }

Returns:

Engine move (SAN + UCI)

Updated FEN

Evaluation

Check / checkmate flags

Parse PGN

POST /api/v1/parse

Lightweight PGN parsing without engine usage.

🛠️ Tech Stack

Python

FastAPI

python-chess

Stockfish

Pydantic

Uvicorn

🧠 What This Project Demonstrates

Clean backend architecture

Safe management of shared resources

Domain-driven design

API contract discipline

Performance-aware computation

Extensible analysis pipelines

📌 Status

Actively developed and architected as a foundation for:

Advanced training tools

Chess analytics dashboards

Educational platforms

👤 Author

Alok Vishwakarma Backend-focused developer with strong interest in system design, chess engines, and clean architecture.