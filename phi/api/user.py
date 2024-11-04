from typing import Optional, Union, Dict, List

from httpx import Response, codes

from phi.api.api import api, invalid_response
from phi.api.routes import ApiRoutes
from phi.api.schemas.user import UserSchema, EmailPasswordAuthSchema
from phi.cli.config import PhiCliConfig
from phi.cli.settings import phi_cli_settings
from phi.utils.log import logger


def user_ping() -> tuple[bool, float]:
    """Ping the phidata servers and return success status and runtime in milliseconds"""

    if not phi_cli_settings.api_enabled:
        return False, 0.0

    import time

    logger.debug("--**-- Ping user api")
    with api.Client() as api_client:
        try:
            start_time = time.perf_counter()
            r: Response = api_client.get(ApiRoutes.USER_HEALTH)
            runtime_ms = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds

            if invalid_response(r):
                return False, runtime_ms

            if r.status_code == codes.OK:
                return True, runtime_ms
        except Exception as e:
            logger.debug(f"Could not ping user api: {e}")
    return False, 0.0


def authenticate_and_get_user(auth_token: str, existing_user: Optional[UserSchema] = None) -> Optional[UserSchema]:
    if not phi_cli_settings.api_enabled:
        return None

    from phi.cli.credentials import read_auth_token

    logger.debug("--**-- Getting user")
    auth_header = {phi_cli_settings.auth_token_header: auth_token}
    anon_user = None
    if existing_user is not None:
        if existing_user.email == "anon":
            logger.debug(f"Claiming anonymous user: {existing_user.id_user}")
            anon_user = {
                "email": existing_user.email,
                "id_user": existing_user.id_user,
                "auth_token": read_auth_token() or "",
            }
    with api.Client() as api_client:
        try:
            r: Response = api_client.post(ApiRoutes.USER_CLI_AUTH, headers=auth_header, json=anon_user)
            if invalid_response(r):
                return None

            user_data = r.json()
            if not isinstance(user_data, dict):
                return None

            return UserSchema.model_validate(user_data)
        except Exception as e:
            logger.debug(f"Could not authenticate user: {e}")
    return None


def sign_in_user(sign_in_data: EmailPasswordAuthSchema) -> Optional[UserSchema]:
    if not phi_cli_settings.api_enabled:
        return None

    from phi.cli.credentials import save_auth_token

    logger.debug("--**-- Signing in user")
    with api.Client() as api_client:
        try:
            r: Response = api_client.post(ApiRoutes.USER_SIGN_IN, json=sign_in_data.model_dump())
            if invalid_response(r):
                return None

            phidata_auth_token = r.headers.get(phi_cli_settings.auth_token_header)
            if phidata_auth_token is None:
                logger.error("Could not authenticate user")
                return None

            user_data = r.json()
            if not isinstance(user_data, dict):
                return None

            current_user: UserSchema = UserSchema.model_validate(user_data)
            if current_user is not None:
                save_auth_token(phidata_auth_token)
                return current_user
        except Exception as e:
            logger.debug(f"Could not sign in user: {e}")
    return None


def user_is_authenticated() -> bool:
    if not phi_cli_settings.api_enabled:
        return False

    logger.debug("--**-- Checking if user is authenticated")
    phi_config: Optional[PhiCliConfig] = PhiCliConfig.from_saved_config()
    if phi_config is None:
        return False
    user: Optional[UserSchema] = phi_config.user
    if user is None:
        return False

    with api.AuthenticatedClient() as api_client:
        try:
            r: Response = api_client.post(
                ApiRoutes.USER_AUTHENTICATE, json=user.model_dump(include={"id_user", "email"})
            )
            if invalid_response(r):
                return False

            response_json: Union[Dict, List] = r.json()
            if response_json is None or not isinstance(response_json, dict):
                logger.error("Could not parse response")
                return False
            if response_json.get("status") == "success":
                return True
        except Exception as e:
            logger.debug(f"Could not check if user is authenticated: {e}")
    return False


def create_anon_user() -> Optional[UserSchema]:
    if not phi_cli_settings.api_enabled:
        return None

    from phi.cli.credentials import save_auth_token

    logger.debug("--**-- Creating anon user")
    with api.Client() as api_client:
        try:
            r: Response = api_client.post(
                ApiRoutes.USER_CREATE_ANON,
                json={"user": {"email": "anon", "username": "anon", "is_machine": True}},
                timeout=2.0,
            )
            if invalid_response(r):
                return None

            phidata_auth_token = r.headers.get(phi_cli_settings.auth_token_header)
            if phidata_auth_token is None:
                logger.error("Could not authenticate user")
                return None

            user_data = r.json()
            if not isinstance(user_data, dict):
                return None

            current_user: UserSchema = UserSchema.model_validate(user_data)
            if current_user is not None:
                save_auth_token(phidata_auth_token)
                return current_user
        except Exception as e:
            logger.debug(f"Could not create anon user: {e}")
    return None
