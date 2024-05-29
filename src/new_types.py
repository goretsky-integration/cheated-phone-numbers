from typing import NewType

import httpx

__all__ = ('AuthCredentialsStorageHttpClient',)

AuthCredentialsStorageHttpClient = NewType(
    'AuthCredentialsStorageHttpClient',
    httpx.Client,
)
