import time
from scrapy.downloadermiddlewares.retry import RetryMiddleware


class CustomRetryMiddleware(RetryMiddleware):
    def _retry(self, request, reason, spider):
        retry_times = request.meta.get("retry_times", 0)
        retry_delay = 2**retry_times
        spider.logger.info(f"Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
        return super()._retry(request, reason, spider)
