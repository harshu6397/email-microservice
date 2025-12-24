from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.config.settings import settings

security = HTTPBasic()


def verify_docs_access(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify credentials for accessing documentation."""
    if credentials.password != settings.docs_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials
