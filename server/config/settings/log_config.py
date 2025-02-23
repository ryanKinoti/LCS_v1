import logging
import os
from pathlib import Path
from typing import Optional, Union
from datetime import datetime


class ColorFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to console output while safely handling
    both string messages and message formats with arguments.
    """
    COLORS = {
        'DEBUG': '\033[37m',    # White
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[41m',  # Red background
        'RESET': '\033[0m'      # Reset color
    }

    def __init__(self, use_colors: bool = True):
        super().__init__(
            fmt='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            datefmt='%d/%b/%Y %H:%M:%S'
        )
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the specified record safely handling both direct messages and
        format strings with arguments.
        """
        # Early return if colors are disabled
        if not self.use_colors:
            return super().format(record)

        # Store original values
        original_msg = record.msg
        original_args = record.args
        original_levelname = record.levelname

        try:
            # Handle the coloring
            if record.levelname in self.COLORS:
                color = self.COLORS[record.levelname]
                reset = self.COLORS['RESET']

                # Color the level name
                record.levelname = f"{color}{record.levelname}{reset}"

                # Handle the message differently based on whether it has arguments
                if record.args:
                    # If we have arguments, format the message first
                    formatted_msg = str(original_msg) % record.args
                    record.msg = f"{color}{formatted_msg}{reset}"
                    record.args = ()  # Clear args since we've used them
                elif isinstance(record.msg, str):
                    # Direct string message
                    record.msg = f"{color}{record.msg}{reset}"

            # Format the record
            formatted_record = super().format(record)

            return formatted_record

        finally:
            # Restore original values
            record.msg = original_msg
            record.args = original_args
            record.levelname = original_levelname


class ErrorTracebackHandler(logging.Handler):
    """
    Custom handler that manages error logging with traceback support.
    Creates separate traceback files and maintains clean, concise error summaries.
    """
    def __init__(self, base_dir: str, level: int = logging.ERROR):
        super().__init__(level)
        self.base_dir = Path(base_dir)
        self.errors_dir = self.base_dir / 'errors'
        self.tracebacks_dir = self.errors_dir / 'tracebacks'
        self.tracebacks_dir.mkdir(parents=True, exist_ok=True)

        # Configure formatters for different outputs
        self.summary_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            '%d/%b/%Y %H:%M:%S'
        )
        self.traceback_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s]\n%(message)s',
            '%d/%b/%Y %H:%M:%S'
        )

    def format_message(self, record: logging.LogRecord) -> str:
        """
        Formats the message part of the record, handling both string messages
        and messages with arguments.
        """
        msg = record.msg
        if record.args:
            try:
                if isinstance(msg, str):
                    msg = msg % record.args
                else:
                    msg = str(msg)
            except Exception:
                # If formatting fails, concatenate message and args
                msg = f"{msg} {str(record.args)}"
        return msg

    def get_error_summary(self, record: logging.LogRecord) -> str:
        """
        Creates a clean error summary from the record, focusing on the essential
        error information without the full traceback.
        """
        # Handle different logger types differently
        if record.name == 'django.request':
            # For request errors, extract just the error type
            msg = str(record.msg)
            if ': ' in msg:
                return msg.split(': ', 1)[0]
            return msg
        elif record.name == 'django.server':
            # For server errors, format as 'METHOD PATH STATUS'
            try:
                if record.args and len(record.args) >= 3:
                    method = record.args[0]
                    path = record.args[1]
                    status = record.args[2]
                    return f"{method} {path} HTTP {status}"
                return str(record.msg)
            except Exception:
                return str(record.msg)

        # For all other errors, use base formatting
        return self.format_message(record)

    def emit(self, record):
        """
        Processes the log record, creating both a summary in the main error log
        and a detailed traceback file when applicable.
        """
        try:
            # Store original record state
            original_exc_info = record.exc_info
            original_msg = record.msg
            original_args = record.args

            try:
                # Get clean error summary
                clean_msg = self.get_error_summary(record)
                record.msg = clean_msg
                record.args = ()

                # Create traceback file if we have exception info
                if original_exc_info:
                    record.exc_info = None  # Remove traceback for summary
                    tb_file = self._write_traceback_file(record, original_exc_info)

                    # Write summary with reference to traceback
                    summary = self.summary_formatter.format(record)
                    summary += f"\nFull traceback available in: {tb_file.relative_to(self.base_dir)}"
                else:
                    # For non-exception errors, just format the message
                    summary = self.summary_formatter.format(record)

                # Write to error log
                with open(self.errors_dir / 'errors.log', 'a', encoding='utf-8') as f:
                    f.write(summary + '\n')

            finally:
                # Restore original record state
                record.exc_info = original_exc_info
                record.msg = original_msg
                record.args = original_args

        except Exception as e:
            # If something goes wrong, log a basic error message
            with open(self.errors_dir / 'errors.log', 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] "
                        f"ERROR: Failed to process error record: {str(e)}\n")

    def _write_traceback_file(self, record, exc_info) -> Path:
        """
        Writes the complete traceback information to a separate file.
        Returns the path to the created file.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        tb_file = self.tracebacks_dir / f'traceback_{timestamp}.log'

        try:
            with open(tb_file, 'w', encoding='utf-8') as f:
                # Write the original error message
                record.exc_info = exc_info
                f.write(self.traceback_formatter.format(record) + '\n')

                if exc_info:
                    import traceback
                    f.write('Detailed Traceback:\n')
                    f.write(''.join(traceback.format_exception(*exc_info)))

                # Add request information if available
                if hasattr(record, 'request'):
                    f.write('\nRequest Information:\n')
                    f.write(f"Path: {getattr(record.request, 'path', 'N/A')}\n")
                    f.write(f"Method: {getattr(record.request, 'method', 'N/A')}\n")

            return tb_file

        except Exception as e:
            raise RuntimeError(f"Failed to write traceback file: {str(e)}")