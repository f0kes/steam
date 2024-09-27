import logging

import aiologger
import aiologger.handlers
from aiologger.handlers.files import AsyncFileHandler


class GenericLogger:
    async def debug(self, message):
        pass

    async def info(self, message):
        pass

    async def warning(self, message):
        pass

    async def error(self, message):
        pass

    async def critical(self, message):
        pass


class AsyncLogger(GenericLogger):
    def __init__(self, log_file=None, log_level=logging.DEBUG, log_format='%(asctime)s - %(levelname)s - %(message)s'):
        self.logger = aiologger.Logger.with_default_handlers(name=__name__)
        self.logger.level = log_level
        formatter = logging.Formatter(log_format)

        # Add file handler if log_file is provided
        if log_file:
            file_handler = AsyncFileHandler(log_file)
            self.logger.add_handler(file_handler)

    async def debug(self, message):
        await self.logger.debug(f"debug: {message}")

    async def info(self, message):
        await self.logger.info(f"info: {message}")

    async def warning(self, message):
        await self.logger.warning(f"warning: {message}")

    async def error(self, message):
        await self.logger.error(f"error: {message}")

    async def critical(self, message):
        await self.logger.critical(f"critical: {message}")
