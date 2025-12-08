import asyncpg
from typing import Optional
from datetime import datetime, timedelta
from models.auth_models import AppUser, LoginDto
import os
from dotenv import load_dotenv
import argon2

load_dotenv()


class AccountDbContext:
    """Database operations for user accounts (equivalent to C# AccountDbContext)"""

    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv("POSTGRE_SQL_CONNECTIONSTRING")
        # Argon2 hasher for password hashing
        self.ph = argon2.PasswordHasher()

    async def user_exists(self, email: str) -> bool:
        """Check if a user exists by email"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = 'SELECT CASE WHEN EXISTS (SELECT 1 FROM "User" WHERE email = $1) THEN TRUE ELSE FALSE END'
            result = await conn.fetchval(query, email)
            return result if result is not None else False
        finally:
            await conn.close()

    async def username_exists(self, username: str) -> bool:
        """Check if a username exists"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = 'SELECT CASE WHEN EXISTS (SELECT 1 FROM "User" WHERE username = $1) THEN TRUE ELSE FALSE END'
            result = await conn.fetchval(query, username)
            return result if result is not None else False
        finally:
            await conn.close()

    async def is_password_valid(self, login_dto: LoginDto) -> bool:
        """Verify password using Argon2"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = 'SELECT hashed_password FROM "User" WHERE email = $1'
            hashed_password = await conn.fetchval(query, login_dto.email)

            if not hashed_password:
                return False

            try:
                # Argon2 verify
                self.ph.verify(hashed_password, login_dto.password)
                return True
            except argon2.exceptions.VerifyMismatchError:
                return False
            except Exception as e:
                print(f"Password verification error: {e}")
                return False

        finally:
            await conn.close()

    async def get_user_by_username(self, email: str) -> Optional[AppUser]:
        """Get user by email"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                SELECT user_id, full_name, username, company, email, created_at
                FROM "User"
                WHERE email = $1
            '''
            row = await conn.fetchrow(query, email)

            if not row:
                return None

            return AppUser(
                id=row['user_id'],
                full_name=row['full_name'],
                username=row['username'],
                company=row['company'] if row['company'] else "",
                email=row['email'],
                created_at=row['created_at']
            )

        finally:
            await conn.close()

    async def register_user(self, user: AppUser) -> Optional[AppUser]:
        """Register a new user"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                INSERT INTO "User" (full_name, username, hashed_password, email, created_at)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING user_id
            '''

            user_id = await conn.fetchval(
                query,
                user.full_name,
                user.username,
                user.password_hash,
                user.email,
                datetime.utcnow()
            )

            user.id = user_id
            return user if user_id > 0 else None

        finally:
            await conn.close()

    async def delete_user(self, email: str) -> bool:
        """Delete a user by email"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = 'DELETE FROM "User" WHERE email = $1'
            result = await conn.execute(query, email)

            # Parse rows affected from result string
            rows_affected = int(result.split()[-1])
            return rows_affected > 0

        finally:
            await conn.close()

    async def update_user(self, user: AppUser) -> bool:
        """Update user information"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                UPDATE "User"
                SET full_name = $1, company = $2, username = $3, email = $4
                WHERE user_id = $5
            '''

            result = await conn.execute(
                query,
                user.full_name,
                user.company,
                user.username,
                user.email,
                user.id
            )

            rows_affected = int(result.split()[-1])
            return rows_affected > 0

        finally:
            await conn.close()

    async def add_forgot_password_token(self, token: str, email: str) -> bool:
        """Add a password reset token to database"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                INSERT INTO "ForgotPasswordToken" (token_hash, created_at, email)
                VALUES ($1, $2, $3)
            '''

            result = await conn.execute(query, token, datetime.utcnow(), email)
            rows_affected = int(result.split()[-1])
            return rows_affected > 0

        finally:
            await conn.close()

    async def verify_password_reset_token(self, reset_token_hash: str, email: str) -> Optional[str]:
        """Verify password reset token (must be used within 30 minutes)"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                SELECT token_hash, created_at
                FROM "ForgotPasswordToken"
                WHERE token_hash = $1 AND email = $2
            '''

            row = await conn.fetchrow(query, reset_token_hash, email)

            if not row:
                return None

            token_hash = row['token_hash']
            created_at = row['created_at']

            # Check if token expired (30 minutes)
            if datetime.utcnow() > created_at + timedelta(minutes=30):
                return None

            return token_hash

        finally:
            await conn.close()

    async def change_password(self, password_hash: str, email: str) -> bool:
        """Change user password"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                UPDATE "User"
                SET hashed_password = $1
                WHERE email = $2
            '''

            result = await conn.execute(query, password_hash, email)
            rows_affected = int(result.split()[-1])
            return rows_affected > 0

        finally:
            await conn.close()

    async def save_user_column_preferences(self, user_id: int, column_preferences: str) -> bool:
        """Save or update user column preferences"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            # Try update first
            update_query = '''
                UPDATE "UserPreferences"
                SET column_preferences = $1, updated_at = $2
                WHERE user_id = $3
            '''

            result = await conn.execute(update_query, column_preferences, datetime.utcnow(), user_id)
            rows_affected = int(result.split()[-1])

            # If no rows updated, insert new record
            if rows_affected == 0:
                insert_query = '''
                    INSERT INTO "UserPreferences" (user_id, column_preferences, created_at, updated_at)
                    VALUES ($1, $2, $3, $4)
                '''

                result = await conn.execute(
                    insert_query,
                    user_id,
                    column_preferences,
                    datetime.utcnow(),
                    datetime.utcnow()
                )
                rows_affected = int(result.split()[-1])

            return rows_affected > 0

        finally:
            await conn.close()

    async def get_user_column_preferences(self, user_id: int) -> Optional[str]:
        """Get user column preferences"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = 'SELECT column_preferences FROM "UserPreferences" WHERE user_id = $1'
            result = await conn.fetchval(query, user_id)
            return result if result else None

        finally:
            await conn.close()
