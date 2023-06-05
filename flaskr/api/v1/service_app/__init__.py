import logging
from os import getenv
from os.path import abspath, join, dirname, isfile
from typing import Optional
from wxc_sdk import WebexSimpleApi
from wxc_sdk.integration import Integration
from wxc_sdk.tokens import Tokens
from yaml import safe_load, safe_dump

log = logging.getLogger(__name__)


class ServiceApp:

    def __init__(self):
        """
        A Service App
        """
        self.tokens = self.get_tokens()
        self.api = WebexSimpleApi(tokens=self.tokens)

    @staticmethod
    def get_sa_token_file() -> str:
        path = abspath(join(dirname(__file__), '../..', 'service_app_tokens.yml'))
        return path

    @staticmethod
    def is_expired_token(time_remaining: int) -> bool:
        """
        Check if remaining access token lifetime is less than a day
        """
        if time_remaining < 24 * 60 * 60:
            log.info(f'Token expiring in {time_remaining} seconds. Needs refresh.')
            return True
        return False

    @staticmethod
    def is_valid_access(tokens: Tokens) -> bool:
        """
        Check for minimal access to Webex using the supplied token
        """
        try:
            api = WebexSimpleApi(tokens=tokens)
            api.webhook.list()
            return True
        except Exception as e:
            log.error(f'Webex API access error: {e}')
        return False

    def read_tokens(self) -> Optional[Tokens]:
        """
        Read tokens from a file.
        """
        sa_token_file = self.get_sa_token_file()
        if not isfile(sa_token_file):
            return None
        try:
            log.info(f'Reading Service App token file: {sa_token_file}')
            with open(sa_token_file, mode='r') as f:
                data = safe_load(f)
            tokens = Tokens.parse_obj(data)
            if self.is_expired_token(tokens.remaining) or not self.is_valid_access(tokens):
                return None
        except Exception as e:
            log.error(f'Error reading Service App token file, {sa_token_file}: {e}')
            return None
        return tokens

    def write_tokens(self, tokens: Tokens):
        sa_token_file = self.get_sa_token_file()
        with open(sa_token_file, mode='w') as f:
            log.info(f'Writing Service App token file: {sa_token_file}')
            safe_dump(tokens.dict(exclude_none=True), f)

    def get_access_token(self) -> Optional[Tokens]:
        """
        Leverage the wxc_sdk Integration package to refresh the Service App's access token and write the results to
        file.
        """
        tokens = Tokens(refresh_token=getenv('SERVICE_APP_REFRESH_TOKEN'))
        integration = Integration(client_id=getenv('SERVICE_APP_CLIENT_ID'),
                                  client_secret=getenv('SERVICE_APP_CLIENT_SECRET'),
                                  scopes=[], redirect_url='')
        integration.refresh(tokens=tokens)
        if not self.is_valid_access(tokens):
            return None
        self.write_tokens(tokens)
        return tokens

    def get_tokens(self) -> Optional[Tokens]:
        """
        Get tokens
        """
        # Try to read (valid) tokens from file
        tokens = self.read_tokens()
        # Otherwise create new access token using refresh token
        if tokens is None:
            tokens = self.get_access_token()
        return tokens
