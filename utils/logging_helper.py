import logging
import logging.handlers # Added for TimedRotatingFileHandler
import os
import datetime
from pathlib import Path
# --- Global Helper ---
def _print(statement: str, verbose: bool = True):
    """Prints the statement if verbose is True."""
    if verbose:
        print(statement)

# --- Custom Exception ---
class DirectoryCreationError(Exception):
    """Custom exception for errors during directory creation."""
    pass

# --- Directory Utility ---
def _checkDirectory(dir_path: str, pardir: str = None) -> str:
    """
    Checks if a directory exists. If not, creates it.
    If dir_path is relative, it's resolved against pardir (or os.getcwd() if pardir is None).
    If dir_path is absolute, pardir is ignored.

    Args:
        dir_path (str): The directory path to check/create.
        pardir (str, optional): The parent directory for relative paths. Defaults to None (uses os.getcwd()).

    Returns:
        str: The absolute, normalized path to the directory.

    Raises:
        DirectoryCreationError: If the directory cannot be created.
    """
    if not os.path.isabs(dir_path):
        pardir_to_use = pardir or os.getcwd()
        target_path = os.path.join(pardir_to_use, dir_path)
    else:
        target_path = dir_path
    
    target_path = os.path.normpath(target_path)

    if not os.path.isdir(target_path):
        _print(f"\nCreating new directory at {target_path}")
        try:
            os.makedirs(target_path, exist_ok=True)
            _print(f"Created directory {target_path}\n")
        except OSError as e: # More specific exception
            raise DirectoryCreationError(f"Unable to create directory {target_path}\n\t{e}")
    else:
        _print(f"Directory {target_path} already exists.")
    return target_path


# --- Base Logger Initializer (Helper Methods) ---
class InitLogger:
    """
    Base class with helper methods for initializing logger components.
    Subclasses are expected to use these methods to configure a logger instance.
    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs # Kept for potential future extension as per original.

    def _create_logger_instance(self, logger_name: str, verbose: bool = True) -> logging.Logger:
        """Gets or creates a logger instance with the given name."""
        _print(f"Initializing logger instance '{logger_name}'", verbose)
        logger = logging.getLogger(logger_name)
        _print(f"Logger instance '{logger_name}' obtained.\n", verbose)
        return logger

    def _set_logger_level(self, logger: logging.Logger, log_level: int, verbose: bool = True) -> None:
        """Sets the logging level for the logger."""
        _print(f"Setting logger level for '{logger.name}' to: {logging.getLevelName(log_level)}", verbose)
        logger.setLevel(log_level)
        _print("Logger level set.\n", verbose)

    def _create_timed_rotating_file_handler(
            self,
            log_file_path: str,
            when: str = "midnight",
            interval: int = 1,
            backup_count: int = 7,
            verbose: bool = True
        ) -> logging.handlers.TimedRotatingFileHandler:
        """Initializes a TimedRotatingFileHandler."""
        _print(f"Initializing a TimedRotatingFileHandler for {log_file_path}.", verbose)
        handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file_path,
            when=when,
            interval=interval,
            backupCount=backup_count
        )
        _print(f"TimedRotatingFileHandler initialized for {log_file_path}.\n", verbose)
        return handler

    def _create_file_handler(
            self,
            log_file_path: str,
            write_mode: str = "a",
            verbose: bool = True
        ) -> logging.FileHandler:
        """Initializes a basic logging.FileHandler."""
        _print(f"Initializing a FileHandler for {log_file_path} (mode: {write_mode}).", verbose)
        handler = logging.FileHandler(filename=log_file_path, mode=write_mode)
        _print(f"FileHandler initialized for {log_file_path}.\n", verbose)
        return handler

    def _set_handler_level(self, handler: logging.Handler, log_level: int, verbose: bool = True) -> None:
        """Sets the logging level for a given Handler."""
        _print(f"Setting handler {type(handler).__name__} level to: {logging.getLevelName(log_level)}", verbose)
        handler.setLevel(log_level)
        _print("Handler level set.\n", verbose)

    def _set_handler_formatter(
            self,
            handler: logging.Handler,
            log_format: str,
            date_format: str,
            verbose: bool = True
        ) -> None:
        """Sets the formatter for a logging Handler."""
        _print(f"Setting log format for handler {type(handler).__name__}.", verbose)
        formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
        handler.setFormatter(formatter)
        _print("Formatter for handler set.\n", verbose)

    def _add_handler_to_logger(self, logger: logging.Logger, handler: logging.Handler, verbose: bool = True) -> None:
        """Adds a handler to a specified logger, avoiding obvious duplicates."""
        is_duplicate = False
        if isinstance(handler, logging.FileHandler): # Checks FileHandler and its subclasses like TimedRotatingFileHandler
            for h in logger.handlers:
                if isinstance(h, type(handler)) and getattr(h, 'baseFilename', None) == handler.baseFilename:
                    is_duplicate = True
                    _print(f"Handler {type(handler).__name__} for file '{handler.baseFilename}' seems to be a duplicate. Skipping add.", verbose)
                    break
        elif isinstance(handler, logging.StreamHandler):
             for h in logger.handlers: # Check stream for StreamHandlers (e.g., sys.stdout, sys.stderr)
                if isinstance(h, type(handler)) and getattr(h, 'stream', None) == getattr(handler, 'stream', None):
                    is_duplicate = True
                    _print(f"Handler {type(handler).__name__} for stream '{getattr(handler, 'stream', 'N/A')}' seems to be a duplicate. Skipping add.", verbose)
                    break
        
        if not is_duplicate:
            _print(f"Adding handler {type(handler).__name__} to logger '{logger.name}'.", verbose)
            logger.addHandler(handler)
            _print("Handler added to logger.\n", verbose)


# --- Main Application Logger Class ---
class AppLogger(InitLogger):
    """
    A configurable logger that writes messages to a file and/or to the console.
    Manages a single logger instance configured upon instantiation.
    """
    def __init__(self,
                 logger_name: str,
                 log_level: int = logging.INFO,
                 log_directory: str = "logs",
                 log_file_name: str = None,
                 log_file_extension: str = ".log",
                 log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                 date_format: str = "%Y-%m-%d %H:%M:%S",
                 use_timed_rotating_handler: bool = False,
                 timed_rotating_when: str = "midnight",
                 timed_rotating_interval: int = 1,
                 timed_rotating_backup_count: int = 7,
                 file_write_mode: str = "a",
                 log_to_console: bool = True,
                 console_log_level: int = None,
                 clear_existing_handlers: bool = True,
                 verbose: bool = True,
                 **kwargs):
        super().__init__(**kwargs)

        self.logger_name = logger_name
        self.log_level = log_level # Overall logger level
        self.verbose = verbose

        # Determine default log_file_name if not provided
        actual_log_file_name = log_file_name if log_file_name else self.logger_name

        # Ensure log_file_extension starts with a dot
        if not log_file_extension.startswith("."):
            actual_log_file_extension = "." + log_file_extension
        else:
            actual_log_file_extension = log_file_extension
        
        _print(f"\n===== Initializing AppLogger: {self.logger_name} =====", self.verbose)

        # 1. Obtain logger instance
        self.logger = self._create_logger_instance(self.logger_name, verbose=self.verbose)
        
        # 2. Set overall logger level
        self._set_logger_level(self.logger, self.log_level, verbose=self.verbose)
        
        # 3. Optionally clear existing handlers
        if clear_existing_handlers and self.logger.hasHandlers():
             _print(f"Logger '{self.logger.name}' has existing handlers. Clearing them as per configuration.", self.verbose)
             for handler_to_remove in self.logger.handlers[:]:
                 self.logger.removeHandler(handler_to_remove)
                 handler_to_remove.close() # Important to close handlers

        # 4. Setup File Handler
        self.file_handler = None
        if log_directory and actual_log_file_name:
            try:
                self.log_dir_path = _checkDirectory(log_directory, pardir=kwargs.get('pardir_for_log_dir')) # Allow pardir override
                
                full_log_file_path = os.path.join(self.log_dir_path, f"{actual_log_file_name}{actual_log_file_extension}")

                if use_timed_rotating_handler:
                    self.file_handler = self._create_timed_rotating_file_handler(
                        log_file_path=full_log_file_path,
                        when=timed_rotating_when,
                        interval=timed_rotating_interval,
                        backup_count=timed_rotating_backup_count,
                        verbose=self.verbose
                    )
                else:
                    self.file_handler = self._create_file_handler(
                        log_file_path=full_log_file_path,
                        write_mode=file_write_mode,
                        verbose=self.verbose
                    )
                
                self._set_handler_level(self.file_handler, self.log_level, verbose=self.verbose) # File handler typically uses logger's level
                self._set_handler_formatter(self.file_handler, log_format, date_format, verbose=self.verbose)
                self._add_handler_to_logger(self.logger, self.file_handler, verbose=self.verbose)
            
            except DirectoryCreationError as e:
                _print(f"Error setting up file handler for logger '{self.logger_name}': {e}", verbose=True) # Always print this error
            except Exception as e:
                _print(f"Unexpected error setting up file handler for '{self.logger_name}': {e}", verbose=True)
        else:
            _print(f"File logging skipped for '{self.logger_name}' (log_directory or log_file_name not provided).", self.verbose)

        # 5. Setup Console Handler (StreamHandler)
        self.console_handler = None
        if log_to_console:
            self.console_handler = logging.StreamHandler() # Defaults to sys.stderr
            actual_console_log_level = console_log_level if console_log_level is not None else self.log_level
            self._set_handler_level(self.console_handler, actual_console_log_level, verbose=self.verbose)
            self._set_handler_formatter(self.console_handler, log_format, date_format, verbose=self.verbose)
            self._add_handler_to_logger(self.logger, self.console_handler, verbose=self.verbose)
            
        self.logger.propagate = False # Uncomment if you want to stop messages from going to parent loggers

        _print(f"===== AppLogger '{self.logger_name}' initialization complete. ====\n", self.verbose)

    # Standard logging methods
    def debug(self, message: str, *args, **kwargs): self.logger.debug(message, *args, **kwargs)
    def info(self, message: str, *args, **kwargs): self.logger.info(message, *args, **kwargs)
    def warning(self, message: str, *args, **kwargs): self.logger.warning(message, *args, **kwargs)
    def error(self, message: str, exc_info=None, *args, **kwargs): self.logger.error(message, exc_info=exc_info, *args, **kwargs)
    def critical(self, message: str, exc_info=None, *args, **kwargs): self.logger.critical(message, exc_info=exc_info, *args, **kwargs)
    def exception(self, message: str, *args, **kwargs): self.logger.exception(message, *args, **kwargs) # Logs ERROR with exc_info=True

    def close(self) -> None:
        """Closes all handlers associated with this logger instance and removes them."""
        _print(f"Closing handlers for logger '{self.logger.name}'.", self.verbose)
        for handler in self.logger.handlers[:]: # Iterate over a copy
            try:
                handler.close()
                self.logger.removeHandler(handler)
            except Exception as e:
                 _print(f"Error closing/removing handler {handler}: {e}", self.verbose)
        _print(f"All handlers closed and removed for '{self.logger.name}'.\n", self.verbose)


# --- Convenience Wrappers (Optional - can use AppLogger directly) ---

class BasicLogger(AppLogger):
    """A convenience wrapper for AppLogger with common defaults for general logging."""
    def __init__(self,
                 logger_name: str = "basic_app",
                 log_level: int = logging.INFO,
                 log_directory: str = "logs",
                 log_file_name: str = None, # Defaults to logger_name in AppLogger
                 log_file_extension: str = ".log",
                 **kwargs): # Pass through any other AppLogger params
        super().__init__(
            logger_name=logger_name,
            log_level=log_level,
            log_directory=log_directory,
            log_file_name=log_file_name if log_file_name else logger_name, # Ensure logger_name is used if None
            log_file_extension=log_file_extension,
            **kwargs
        )

class ErrorOnlyLogger(AppLogger):
    """A convenience wrapper for AppLogger, defaulting to ERROR level and .err extension."""
    def __init__(self,
                 logger_name: str = "error_app",
                 log_level: int = logging.ERROR, # Default to ERROR
                 log_directory: str = "error_logs", # Separate directory for errors
                 log_file_name: str = None, # Defaults to logger_name in AppLogger
                 log_file_extension: str = ".err",
                 log_to_console: bool = True, # Errors are often important for console
                 **kwargs):
        super().__init__(
            logger_name=logger_name,
            log_level=log_level,
            log_directory=log_directory,
            log_file_name=log_file_name if log_file_name else logger_name,
            log_file_extension=log_file_extension,
            log_to_console=log_to_console,
            **kwargs
        )


# --- Example Usage ---
if __name__ == '__main__':
    # Get the directory of the current script
    script_dir = os.path.abspath(os.path.dirname(__file__))
    
    print("--- Testing BasicLogger (INFO level, file and console) ---")
    # Use pardir_for_log_dir to make log directory relative to script, not CWD
    basic_log_dir_path = os.path.join(script_dir, "my_app_logs_script_relative")

    logger1 = BasicLogger(
        logger_name="App1",
        log_directory="my_app_logs_cwd_relative", # Log dir relative to current working directory
        # log_directory=basic_log_dir_path, # Alternative: log dir relative to script
        # pardir_for_log_dir=script_dir, # Use with relative log_directory to base off script_dir
        log_file_name="application",
        verbose=True,
        log_to_console=True
    )
    logger1.info("This is an info message from App1.")
    logger1.warning("This is a warning message from App1.")
    logger1.debug("This debug App1 message won't appear (logger level is INFO).")
    
    # To enable debug messages for App1 at runtime (example):
    # logger1.logger.setLevel(logging.DEBUG)
    # if logger1.console_handler: logger1.console_handler.setLevel(logging.DEBUG)
    # if logger1.file_handler: logger1.file_handler.setLevel(logging.DEBUG)
    # logger1.debug("This App1 debug message would now appear IF levels were changed.")

    print("\n--- Testing ErrorOnlyLogger (ERROR level, .err file, timed rotation) ---")
    error_logger = ErrorOnlyLogger(
        logger_name="CriticalErrors",
        log_directory="error_logs_cwd_relative",
        use_timed_rotating_handler=True,
        timed_rotating_backup_count=3, # Keep 3 backup error logs
        verbose=True
    )
    error_logger.info("This info msg from CriticalErrors won't be logged (level is ERROR).")
    error_logger.error("This is an error message from CriticalErrors logger.")
    try:
        x = 1 / 0
    except ZeroDivisionError:
        error_logger.exception("A division error occurred!") # .exception logs ERROR + stack trace

    print("\n--- Testing AppLogger directly (DEBUG, no console, custom format) ---")
    custom_logger = AppLogger(
        logger_name="DebugTrace",
        log_level=logging.DEBUG,
        log_directory="debug_traces_cwd_relative",
        log_file_name="trace_details",
        log_file_extension=".dbg",
        log_format="%(asctime)s [%(levelname)-8s] %(funcName)s:%(lineno)d - %(message)s",
        date_format="%H:%M:%S",
        log_to_console=False,
        verbose=True
    )
    custom_logger.debug("A detailed debug message for tracing.")
    custom_logger.info("An info message from custom_logger (DebugTrace).")

    print("\n--- Testing shared logger name behavior (reconfiguration) ---")
    # logger1_again will reconfigure the "App1" logger.
    logger1_again = BasicLogger(
        logger_name="App1", # Same name as logger1
        log_directory="my_app_logs_cwd_relative",
        log_file_name="application_reconfigured", # New file name
        log_level=logging.DEBUG, # New level
        verbose=False # Less verbose setup for this instance
    )
    # logger1 (original instance) will now use the new configuration for "App1"
    logger1.info("Info from original logger1 instance (now reconfigured by logger1_again).")
    logger1_again.info("Info from logger1_again instance (App1).")
    logger1_again.debug("Debug from logger1_again instance (App1) - should appear.")

    print("\n--- Testing logger closure ---")
    error_logger.error("One last error before closing error_logger.")
    error_logger.close()
    # After closing, messages sent to error_logger might not appear or might go to a default/root handler
    # error_logger.error("This message is after closing error_logger's handlers.")

    print("\nAll tests finished. Check log files in created 'logs' directories.")