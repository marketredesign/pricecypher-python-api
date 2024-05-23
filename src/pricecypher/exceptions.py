import warnings


class HttpException(Exception):
    def __init__(self, message: str, **kwargs):
        super().__init__(message)
        self.message = kwargs.get('message', message)
        self.status_code = kwargs.get('status_code', 500)
        self.code = kwargs.get('error_code', "Internal Server Error")

    def __str__(self):
        return f'{self.status_code} {self.code}: {self.message}'

    def format_response(self) -> dict:
        return {
            'statusCode': self.status_code,
            'headers': {
                'Content-Type': 'text/plain',
                'x-amzn-ErrorType': self.code,
            },
            'isBase64Encoded': False,
            'body': f'{self.code}: {str(self)}'
        }


class PriceCypherError(HttpException):
    def __init__(self, status_code, error_code, message):
        warnings.warn('Use of the class `PriceCypherError` is deprecated. Please use `HttpException` instead.')
        super().__init__(message, status_code=status_code, error_code=error_code)


class RateLimitError(HttpException):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = 429
        self.code = kwargs.get('error_code', 'Too Many Requests')
        self.reset_at = kwargs.get('reset_at')
