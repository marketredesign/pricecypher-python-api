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


class MissingInputException(HttpException):
    """Exception raised when one of the necessary inputs is missing.

    Attributes:
        scopes -- scope missing from user input
        business_cell -- boolean value, if True, business cell scope is missing
        message -- explanation of the error
    """

    def __init__(self, scopes, business_cell=False, message="MissingInputException: Missing input variables: "):
        self.statusCode = 400
        self.code = 'Bad Request'
        self.scopes = scopes
        self.business_cell = business_cell
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        if self.business_cell:
            return self.message + self.scopes + ". Please provide business cell input."
        else:
            return self.message + ", ".join(self.scopes)


class DataNotFoundException(HttpException):
    """Exception raised when one of the necessary input by the user is missing from the dataset.

    Attributes:
        key -- column/scope with missing data
        value -- data value that is missing
        message -- explanation of the error
    """

    def __init__(self, key, value, message="DataNotFoundException: Data point not found in dataset for column "):
        self.statusCode = 404
        self.code = 'Not Found'
        self.key = key
        self.value = value
        self.message = message + str(key) + ": " + str(value)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class IncorrectVolumeException(HttpException):
    """Exception raised when user input has incorrect volume.

    Attributes:
        val -- incorrect volume value
        message -- explanation of the error
    """

    def __init__(self, val, message="IncorrectVolumeException: Incorrect volume entered: "):
        self.statusCode = 400
        self.code = 'Bad Request'
        self.message = message + str(val) + ". Please enter a positive value."
        super().__init__(self.message)

    def __str__(self):
        return self.message


class MissingRepresentationException(HttpException):
    """Exception raised when the script expects a representation,
    but it is not found due to excel configuration.

    Attributes:
        val -- column that should be indicated as a representation
        message -- explanation of the error
    """

    def __init__(self, val, message="MissingRepresentationException: "):
        self.statusCode = 409
        self.code = 'Conflict'
        self.message = message + f""""{val} column is not a representation. 
        Please update scopes file to include a scope with the representation."""
        super().__init__(self.message)

    def __str__(self):
        return self.message
