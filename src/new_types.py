from typing import NewType

import httpx

__all__ = ('AuthCredentialsStorageHttpClient', 'DodoIsHttpClient')

AuthCredentialsStorageHttpClient = NewType(
    'AuthCredentialsStorageHttpClient',
    httpx.Client,
)
DodoIsHttpClient = NewType('DodoIsHttpClient', httpx.Client)
