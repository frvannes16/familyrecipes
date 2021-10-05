from typing import Optional, Dict


from fastapi import status, Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}

        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        # Extract the token from the access_token cookie.
        authorization: Optional[str] = request.cookies.get("access_token")
        if authorization:
            scheme, param = get_authorization_scheme_param(authorization)
            if not authorization or scheme.lower() != "bearer":
                if self.auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not authenticated",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                else:
                    return None
            return param

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
