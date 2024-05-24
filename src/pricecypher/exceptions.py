import warnings


class HttpException(Exception):
    def __init__(self, message: str, **kwargs):
        super().__init__(message)

        self.message = kwargs.get('message', message)
        self.status_code = kwargs.get('status_code', 500)
        self.code = kwargs.get('error_code', "Internal Server Error")
        self.extra = kwargs.get('extra')

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
            'body': f'{self.code}: {str(self)}',
            'extra': self.extra,
        }


class PriceCypherError(HttpException):
    def __init__(self, status_code, error_code, message):
        warnings.warn('Use of the class `PriceCypherError` is deprecated. Please use `HttpException` instead.')
        super().__init__(message, status_code=status_code, error_code=error_code)


class MissingInputException(HttpException):
    """Exception raised when one of the necessary inputs is missing.

    Attributes:
        scopes -- scope missing from user input
        business_cell -- boolean value, if True, business cell scope is missing
        message -- explanation of the error
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)
        scopes: list[str] = kwargs.get('scopes', [])

        self.statusCode = 400
        self.code = kwargs.get('error_code', 'Bad Request')
        self.code = 'Bad Request'
        self.message = f'{message or "Missing input variables:"} {", ".join(scopes)}'
        self.extra = {'scopes': kwargs.get('scopes')}


class IncorrectVolumeException(HttpException):
    """Exception raised when user input has incorrect volume.

    Attributes:
        val -- incorrect volume value
        message -- explanation of the error
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(self.message)
        val = kwargs.get('val')

        self.statusCode = 400
        self.code = 'Bad Request'
        self.message = f'''
            {message or "IncorrectVolumeException: Incorrect volume entered. Please enter positive value"} 
            ({val})'message + str(val) + ". Please enter a positive value."'''
        self.extra = {'volume': val}


class DataNotFoundException(HttpException):
    """Exception raised when one of the necessary input by the user is missing from the dataset.

    Attributes:
        key -- column/scope with missing data
        value -- data value that is missing
        message -- explanation of the error
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(self.message)
        key = kwargs.get('key', "Unknown")
        value = kwargs.get('value', "Unknown")

        self.statusCode = 404
        self.code = 'Not Found'
        self.message = f'{message or "Data point not found in dataset for column"} {key}: {value}.'
        self.extra = {'key': key, 'value': value}


class MissingRepresentationException(HttpException):
    """Exception raised when the script expects a representation,
    but it is not found due to excel configuration.

    Attributes:
        val -- column that should be indicated as a representation
        message -- explanation of the error
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(self.message)
        val = kwargs.get('val')

        self.statusCode = 409
        self.code = 'Conflict'
        self.message = f'{message or "Unable to find representation. Please update scopes file."} ({val})'
        self.extra = {'column': val}


class RateLimitError(HttpException):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)

        self.status_code = 429
        self.code = kwargs.get('error_code', 'Too Many Requests')
        self.extra = {'reset_at': kwargs.get('reset_at')}
