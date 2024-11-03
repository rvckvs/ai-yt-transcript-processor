# Transcript Formatter with Speaker Identification

![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue.svg)
![OpenAI API](https://img.shields.io/badge/OpenAI-API-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
  - [Examples](#examples)
- [Script Details](#script-details)
  - [Code Structure](#code-structure)
  - [Logging System](#logging-system)
  - [AI Integration](#ai-integration)
  - [Error Handling](#error-handling)
- [Limitations](#limitations)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## Overview

The **Transcript Formatter with Speaker Identification** is a command-line tool built with Python that processes raw transcripts of interviews or conversations, formats them for readability, and adds speaker identification using OpenAI's advanced language models. This tool is designed to make transcripts clearer and more informative for easier review and analysis.

## Features

- **AI-Powered Speaker Identification**: Utilizes OpenAI's API to label and distinguish speakers based on context.
- **Chunked Processing**: Splits lengthy transcripts into manageable chunks for processing and maintains optimal performance.
- **Formatted Output**: Cleans up transcripts by adding paragraph breaks, speaker labels, and structured spacing.
- **Verbose Logging**: Detailed logging output that provides feedback on the processing status with colored, real-time logs.
- **Retry Mechanism**: Includes retry logic with exponential backoff for API rate limits or temporary failures.

## Prerequisites

1. **Python 3.7 or Higher**: Make sure Python is installed. [Download here](https://www.python.org/downloads/).
2. **OpenAI API Key**: Obtain your API key from the [OpenAI API Keys](https://platform.openai.com/account/api-keys) section.
3. **Python Packages**: The required package is `openai`. Ensure it's installed before running the script.

## Installation

1. **Clone the Repository**:

   ```
   git clone https://github.com/rvckvs/ai-yt-transcript-processor.git
   cd ai-yt-transcript-processor
   ```

2. **Set Up a Virtual Environment** (Optional but recommended):

   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```
   pip install openai
   ```

## Usage

Run the script via the command line by specifying the input file path and output file path. Optional arguments include the API key and model selection.

### Command-Line Arguments

```
python format_transcript.py input_file.txt output_file.txt [--api_key YOUR_API_KEY] [--model MODEL_NAME] [--max_retries RETRY_COUNT]
```

- **Positional Arguments**:
  - `input_file`: The path to the input transcript file (e.g., `raw_transcript.txt`).
  - `output_file`: The path for saving the formatted transcript (e.g., `formatted_transcript.txt`).

- **Optional Arguments**:
  - `--api_key`: Your OpenAI API key (can be set via the `OPENAI_API_KEY` environment variable).
  - `--model`: The OpenAI model to use (default: `gpt-4o-mini`).
  - `--max_retries`: The number of retry attempts for API calls (default: `5`).

### Examples

1. **Basic Usage**:

   ```
   python format_transcript.py raw_transcript.txt formatted_transcript.txt --api_key sk-XXXXXXXXXXXXXXXXXXXX
   ```

2. **Using Environment Variable for API Key**:

   ```
   export OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXX
   python format_transcript.py raw_transcript.txt formatted_transcript.txt
   ```

3. **Specify a Different Model**:

   ```
   python format_transcript.py raw_transcript.txt formatted_transcript.txt --model gpt-3.5-turbo
   ```

### Sample Execution Output

```
[INFO] Reading input file: raw_transcript.txt
[INFO] Successfully read 12345 characters from input file.
[INFO] Splitting text into chunks with max 2000 characters each.
[INFO] Total chunks created: 7
[DEBUG] Processing chunk 1/7...
[INFO] Successfully formatted chunk 1/7.
[DEBUG] Processing chunk 2/7...
...
[SUCCESS] Completed formatting. Saved to formatted_transcript.txt.
```

## Script Details

### Code Structure

- **`setup_logging()`**: Configures and sets up the logging with colored outputs.
- **`parse_arguments()`**: Handles command-line argument parsing.
- **`get_api_key()`**: Retrieves the API key either from arguments or environment variables.
- **`read_input_file()` / `write_to_file()`**: Handles file I/O operations.
- **`split_text()`**: Splits the transcript into chunks for efficient API processing.
- **`format_transcript()`**: Sends chunks to the OpenAI API for formatting and labeling.
- **`main()`**: Manages the main script workflow.

### Logging System

The script uses the `logging` module to deliver real-time, colored feedback:

- **Colored Severity Levels**:
  - `[INFO]` in blue
  - `[WARNING]` in yellow
  - `[ERROR]` in red
  - `[SUCCESS]` in green
- **Detailed Logs**: Displays step-by-step processing and API interaction logs for traceability.

### AI Integration

The script integrates OpenAI's API for formatting, powered by customizable prompts that instruct the model to:

- Format the transcript.
- Identify and label speakers.
- Add proper paragraphing and clarity to the text.

### Error Handling

- **Rate Limit Handling**: Implements exponential backoff if the API rate limit is exceeded.
- **General API Errors**: Captures API errors and logs them.
- **File and System Errors**: Handles common file I/O and system issues gracefully.

## Limitations

- **Potential Costs**: Processing large transcripts with advanced models may incur significant costs.
- **Speaker Identification Accuracy**: The AI may not always accurately attribute speakers, especially with complex dialogues.
- **Terminal Compatibility**: Some terminals may not support ANSI color codes used in the log output.

## Future Enhancements ???

- **Parallel Processing**: Add support for concurrent chunk processing to improve speed.
- **Token-Based Chunking**: Use tokenizers for more precise chunk splitting.
- **Enhanced Speaker Recognition**: Implement Named Entity Recognition (NER) for better speaker identification.
- **GUI Version**: Develop a user-friendly graphical interface.
- **Log to File**: Include an option to save log outputs for easier review.

## Contributing

Contributions are welcome! To contribute:

1. **Fork the Repo**: Click on "Fork" at the top of the repository page.
2. **Clone Your Fork**:

   ```
   git clone https://github.com/yourusername/transcript-formatter.git
   cd ai-yt-transcript-processor
   ```

3. **Create a New Branch**:

   ```
   git checkout -b feature/YourFeatureName
   ```

4. **Make Changes and Commit**:

   ```
   git commit -m "Add feature: YourFeatureName"
   ```

5. **Push and Create a PR**:

   ```
   git push origin feature/YourFeatureName
   ```

### Reporting Issues

Report bugs or feature requests by [opening an issue](https://github.com/rvckvs/ai-yt-transcript-processor/issues).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---

*Created with ❤️ by [rvckvs](https://github.com/rvckvs)*

---
