# Makefile for audio2text-timestamped

.PHONY: help install test quick-test unit-test test-legacy example models troubleshoot clean transcribe convert

# Variables
PYTHON = .venv/bin/python
PIP = .venv/bin/pip

help:
	@echo "Available commands:"
	@echo "  install        - Install dependencies"
	@echo "  test           - Run integration test"
	@echo "  quick-test     - Quick test with demo"
	@echo "  unit-test      - Run unit tests"
	@echo "  test-legacy    - Run old test with audio file creation"
	@echo "  example        - Run example"
	@echo "  models         - Show model information"
	@echo "  troubleshoot   - Show troubleshooting"
	@echo "  clean          - Clean temporary files"
	@echo "  transcribe     - Transcribe audio file (FILE=path/to/audio.mp3 MODEL=medium)"
	@echo "  convert        - Convert result.json to CSV and SRT"
	@echo "  help           - Show this help"

install:
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed"

test:
	@echo "Running integration test..."
	$(PYTHON) integration_test.py

quick-test:
	@echo "Running quick test..."
	$(PYTHON) quick_test.py

unit-test:
	@echo "Running unit tests..."
	$(PYTHON) unit_test.py

test-legacy:
	@echo "Running old test with audio file creation..."
	$(PYTHON) test.py

example:
	@echo "Running example..."
	$(PYTHON) example.py

models:
	@echo "Showing model information..."
	$(PYTHON) model_info.py

troubleshoot:
	@echo "Showing troubleshooting..."
	$(PYTHON) model_info.py trouble

clean:
	@echo "Cleaning temporary files..."
	rm -f test_result.json
	rm -f transcription_result.json
	rm -f test_audio.wav
	rm -f test_audio.aiff
	rm -f test_simple.aiff
	rm -f result.json
	rm -f result.csv
	rm -f result.srt
	rm -f *_transcript.json
	rm -f *.pyc
	rm -rf __pycache__
	@echo "Cleanup complete"

# Example usage with audio file
transcribe:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make transcribe FILE=path/to/audio.mp3 [MODEL=medium]"; \
		exit 1; \
	fi
	@MODEL_SIZE=$${MODEL:-medium}; \
	echo "Transcribing with model: $$MODEL_SIZE"; \
	$(PYTHON) audio2text_timestamped.py $(FILE) --model $$MODEL_SIZE --output result.json --pretty
	@echo "Result saved to result.json"

# Convert result to various formats
convert:
	@if [ ! -f "result.json" ]; then \
		echo "File result.json not found. Please run transcription first."; \
		exit 1; \
	fi
	$(PYTHON) utils.py result.json --csv result.csv --srt result.srt --stats
	@echo "Results converted to CSV and SRT formats"
