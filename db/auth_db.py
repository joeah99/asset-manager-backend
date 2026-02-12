from sqlalchemy import text
from typing import Optional
from models.auth_models import SignupRequest, UserResponse
from db.connection import get_db
import hashlib
import logging

# Setup logging
logger = logging.getLogger(__name__)

class AuthDbContext:
    def __init__(self):
        pass

    async def _get_password_hash(self, password: str) -> str:
        """Basic SHA256 hashing for demo purposes"""
        return hashlib.sha256(password.encode()).hexdigest()

    async def login_user_async(self, email: str, password: str) -> Optional[UserResponse]:
        """
        Validate user credentials
        """
        hashed_password = await self._get_password_hash(password)
        
        query = text("""
            SELECT "UserId", "FullName", "Email", "Company", "CreatedAt"
            FROM "Users"
            WHERE "Email" = :email AND "HashedPassword" = :password_hash
        """)
        
        try:
            async for session in get_db():
                result = await session.execute(query, {
                    "email": email, 
                    "password_hash": hashed_password
                })
                row = result.mappings().fetchone()
                
                if row:
                    return UserResponse(
                        user_id=row["UserId"],
                        full_name=row["FullName"],
                        email=row["Email"],
                        company=row["Company"],
                        created_at=row["CreatedAt"]
                    )
                return None
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            raise

    async def create_user_async(self, request: SignupRequest) -> Optional[UserResponse]:
        """
        Create a new user
        """
        hashed_password = await self._get_password_hash(request.password)
        
        # Check if email exists
        check_query = text('SELECT 1 FROM "Users" WHERE "Email" = :email')
        
        insert_query = text("""
            INSERT INTO "Users" ("FullName", "Email", "HashedPassword", "Company", "Username")
            VALUES (:full_name, :email, :password_hash, :company, :email)
            RETURNING "UserId", "FullName", "Email", "Company", "CreatedAt"
        """)
        
        try:
            async for session in get_db():
                print("DEBUG: DB Session acquired for signup")
                # Check existing
                print(f"DEBUG: Checking if user exists: {request.email}")
                existing = await session.execute(check_query, {"email": request.email})
                if existing.fetchone():
                    print("DEBUG: User already exists")
                    return None # User exists
                
                # Insert
                print("DEBUG: Inserting new user...")
                result = await session.execute(insert_query, {
                    "full_name": request.full_name,
                    "email": request.email,
                    "password_hash": hashed_password,
                    "company": request.company,
                })
                await session.commit()
                print("DEBUG: Insert committed")
                
                row = result.mappings().fetchone()
                if row:
                    print(f"DEBUG: User created: {row['UserId']}")
                    return UserResponse(
                        user_id=row["UserId"],
                        full_name=row["FullName"],
                        email=row["Email"],
                        company=row["Company"],
                        created_at=row["CreatedAt"]
                    )
                return None
        except Exception as e:
            print(f"DEBUG: DB Error in signup: {e}")
            logger.error(f"Error creating user: {e}")
            raise
