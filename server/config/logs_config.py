import logging


class ColorFormatter(logging.Formatter):
    """Custom formatter to add colors to console logs"""

    COLORS = {
        'DEBUG': '\033[37m',  # White
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[41m',  # Red background
        'RESET': '\033[0m'  # Reset color
    }

    # Mapping of logging levels to their names
    LEVEL_MAP = {
        logging.DEBUG: 'DEBUG',  # 10
        logging.INFO: 'INFO',  # 20
        logging.WARNING: 'WARNING',  # 30
        logging.ERROR: 'ERROR',  # 40
        logging.CRITICAL: 'CRITICAL',  # 50
    }

    def format(self, record):
        # Get the level name from either the level number or existing name
        level_name = self.LEVEL_MAP.get(record.levelno, record.levelname)

        if level_name in self.COLORS:
            # Color for the level name
            colored_level = f"{self.COLORS[level_name]}{record.levelname}{self.COLORS['RESET']}"
            # Color for the message
            colored_msg = f"{self.COLORS[level_name]}{record.msg}{self.COLORS['RESET']}"

            # Store original values
            original_level = record.levelname
            original_msg = record.msg

            # Set colored values
            record.levelname = colored_level
            record.msg = colored_msg

            # Format the record
            result = super().format(record)

            # Restore original values
            record.levelname = original_level
            record.msg = original_msg

            return result

        return super().format(record)
