from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings, logger
from app.db import crud
from app.schemas.user_schema import UserCreate
from app.core.enums import UserRole

async def init_db(db: AsyncSession) -> None:
    """
    Initializes the database by creating the first superuser if it doesn't exist.
    """
    logger.info("Checking if superuser needs to be created...")
    user = await crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        logger.info(f"Creating superuser: {settings.FIRST_SUPERUSER}")
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD.get_secret_value(),
            is_superuser=True,
            is_active=True,
            role=UserRole.ADMIN  # Superuser must have ADMIN role
        )
        try:
            user = await crud.user.create(db=db, obj_in=user_in)
            logger.info("Superuser created successfully.")
        except Exception as e:
            logger.error(f"Error creating superuser: {e}")
            # Depending on the error, you might want to handle it differently
            # For example, if the error is due to a race condition where another process
            # created the user, you might just log a warning.
            # Re-fetch user to confirm if creation succeeded despite error log
            user = await crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
            if user:
                 logger.warning("Superuser already existed or was created concurrently.")
            else:
                 raise # Re-raise if creation truly failed
    else:
        logger.info("Superuser already exists.")