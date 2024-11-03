import openai
import argparse
import os
import sys
import time
import logging
import datetime
import gc  # Import garbage collection module

# ANSI escape codes for colored output in the terminal
class Colors:
    HEADER = '\033[95m'  # Magenta color for debug messages
    BLUE = '\033[94m'    # Blue color for informational messages
    GREEN = '\033[92m'   # Green color for success messages
    WARNING = '\033[93m' # Yellow color for warning messages
    RED = '\033[91m'     # Red color for error messages
    ENDC = '\033[0m'     # Reset color to default
    BOLD = '\033[1m'     # Bold text

def setup_logging():
    """
    Configures the logging format and level.
    Adds color to log messages based on their severity using a custom formatter.
    """
    class ColoredFormatter(logging.Formatter):
        def format(self, record):
            if record.levelno == logging.INFO:
                record.msg = f"{Colors.BLUE}[INFO]{Colors.ENDC} {record.msg}"
            elif record.levelno == logging.WARNING:
                record.msg = f"{Colors.WARNING}[WARNING]{Colors.ENDC} {record.msg}"
            elif record.levelno == logging.ERROR:
                record.msg = f"{Colors.RED}[ERROR]{Colors.ENDC} {record.msg}"
            elif record.levelno == logging.SUCCESS:
                record.msg = f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {record.msg}"
            elif record.levelno == logging.DEBUG:
                record.msg = f"{Colors.HEADER}[DEBUG]{Colors.ENDC} {record.msg}"
            return super().format(record)

    # Add custom log level for success
    logging.SUCCESS = 25
    logging.addLevelName(logging.SUCCESS, "SUCCESS")

    # Define a method for the success level in the Logger class
    def success(self, message, *args, **kws):
        if self.isEnabledFor(logging.SUCCESS):
            self._log(logging.SUCCESS, message, args, **kws)

    # Attach the custom success method to the Logger class
    logging.Logger.success = success

    # Configure the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels

    # Create and configure the console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = ColoredFormatter('%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Ensure that all log levels, including the custom one, are working
    logger.debug("Logging setup complete. Custom log level 'success' added.")

def parse_arguments():
    """
    Parses command-line arguments for the script.
    
    Returns:
        argparse.Namespace: An object containing all the parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Format transcript and add speaker identification with names."
    )
    parser.add_argument(
        "input_file", type=str, help="Path to the input transcript file."
    )
    parser.add_argument(
        "output_file", type=str, help="Path to the output formatted transcript file."
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default=None,
        help="OpenAI API key. Can also be set via OPENAI_API_KEY environment variable.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model to use (e.g., gpt-4, gpt-3.5-turbo).",
    )
    parser.add_argument(
        "--max_retries",
        type=int,
        default=5,
        help="Maximum number of retries for API calls.",
    )
    return parser.parse_args()

def get_api_key(provided_key):
    """
    Retrieves the OpenAI API key from command-line arguments or environment variables.
    
    Args:
        provided_key (str): The API key passed as a command-line argument.
    
    Returns:
        str: The API key to be used for OpenAI API requests.
    """
    if provided_key:
        logging.info("Using API key provided via command-line argument.")
        return provided_key
    elif os.getenv("OPENAI_API_KEY"):
        logging.info("Using API key from OPENAI_API_KEY environment variable.")
        return os.getenv("OPENAI_API_KEY")
    else:
        logging.error("OpenAI API key must be provided via --api_key or OPENAI_API_KEY environment variable.")
        sys.exit(1)

def read_input_file(file_path):
    """
    Reads the content of the input file.
    
    Args:
        file_path (str): The path to the input file.
    
    Returns:
        str: The content of the file.
    """
    logging.info(f"Reading input file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            logger = logging.getLogger()
            logger.success(f"Successfully read {len(content)} characters from input file.")
            return content
    except Exception as e:
        logging.error(f"Error reading input file: {e}")
        sys.exit(1)

def write_to_file(file_path, content, mode='a'):
    """
    Writes the given content to a file at the specified path.
    
    Args:
        file_path (str): The path to the file.
        content (str): The content to write to the file.
        mode (str): The file mode, default is 'a' (append).
    """
    try:
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
            f.write("\n\n")  # Ensure separation between chunks
            logger = logging.getLogger()
            logger.success(f"Successfully wrote chunk to {file_path}.")
    except Exception as e:
        logging.error(f"Error writing to output file: {e}")
        sys.exit(1)

def split_text(text, max_tokens=2000):
    """
    Splits the input text into chunks that are within the specified token limit.
    
    Args:
        text (str): The text to split.
        max_tokens (int): The maximum number of characters per chunk.
    
    Returns:
        list: A list of text chunks.
    """
    logging.info(f"Splitting text into chunks with max {max_tokens} characters each.")
    chunks = []
    total_length = len(text)
    logging.info(f"Total length of input text: {total_length} characters.")
    
    try:
        while len(text) > max_tokens:
            split_at = text.rfind('.', 0, max_tokens)
            if split_at == -1:
                split_at = max_tokens
            chunk = text[:split_at].strip()
            if chunk:
                logging.debug(f"Adding chunk with {len(chunk)} characters. Remaining text length: {len(text) - split_at} characters.")
                chunks.append(chunk)
                logging.debug(f"Getting the next text...")
                text = text[split_at:].strip()
            else:
                logging.warning("Empty chunk found. Skipping...")
                text = text[max_tokens:].strip()
        if text:
            logging.debug(f"Adding final chunk with {len(text)} characters.")
            chunks.append(text)
        
        logging.info(f"Total chunks created: {len(chunks)}")
    except Exception as e:
        logging.error(f"Error while splitting text: {e}")
        sys.exit(1)
    
    logging.debug("Successfully split text into chunks.")
    return chunks

def format_transcript(client, model, text, max_retries=5, chunk_number=1, total_chunks=1):
    """
    Formats the given text using the OpenAI API and handles retries in case of errors.
    
    Args:
        client (OpenAI): The OpenAI client instance.
        model (str): The model to use for formatting (e.g., 'gpt-4').
        text (str): The text chunk to format.
        max_retries (int): The maximum number of retry attempts.
        chunk_number (int): The current chunk number being processed.
        total_chunks (int): The total number of chunks to process.
    
    Returns:
        str: The formatted text.
    """
    system_prompt = (
        "You are a professional transcriber. Format the following transcript by adding speaker identification tags with their actual names "
        "(e.g., 'Joe Rogan', 'Guest'). Use context within the text to identify the interviewer and interviewee by name wherever possible. "
        "Ensure proper formatting with clear speaker labels and appropriate paragraphing."
    )

    attempt = 0
    while attempt <= max_retries:
        try:
            start_time = datetime.datetime.now()
            logging.debug(f"Starting API call for chunk {chunk_number}/{total_chunks} at {start_time}.")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.5,
            )
            
            end_time = datetime.datetime.now()
            logging.debug(f"Completed API call for chunk {chunk_number}/{total_chunks} at {end_time}, duration: {end_time - start_time}.")
            formatted_text = response.choices[0].message.content.strip()
            logging.info(f"Successfully formatted chunk {chunk_number}/{total_chunks}.")
            return formatted_text
        except openai.RateLimitError:
            attempt += 1
            if attempt > max_retries:
                logging.error("Exceeded maximum retries due to rate limits.")
                sys.exit(1)
            wait_time = 2 ** attempt
            logging.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds... (Attempt {attempt}/{max_retries})")
            time.sleep(wait_time)
        except openai.APIError as e:
            logging.error(f"OpenAI API error: {e}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error during API call: {e}")
            sys.exit(1)

def main():
    """
    The main entry point for the script. Handles argument parsing, input reading,
    processing, and output writing.
    """
    setup_logging()
    args = parse_arguments()
    api_key = get_api_key(args.api_key)

    # Initialize OpenAI client instance
    client = openai.OpenAI(api_key=api_key)

    raw_text = read_input_file(args.input_file)
    chunks = split_text(raw_text, max_tokens=2000)

    total_chunks = len(chunks)
    logging.info(f"Starting to process {total_chunks} chunks.")
    
    for idx, chunk in enumerate(chunks):
        logging.debug(f"Processing chunk {idx + 1}/{total_chunks} with {len(chunk)} characters.")
        formatted = format_transcript(
            client,
            args.model,
            chunk,
            max_retries=args.max_retries,
            chunk_number=idx + 1,
            total_chunks=total_chunks
        )
        write_to_file(args.output_file, formatted, mode='a')  # Write each chunk to the output file incrementally
        gc.collect()  # Manually trigger garbage collection to free up memory
        time.sleep(2)  # Increase delay between requests
        logging.info(f"Completed processing chunk {idx + 1}/{total_chunks}.\n")

    logging.info("Transcript formatting and speaker identification completed successfully.")

if __name__ == "__main__":
    main()
