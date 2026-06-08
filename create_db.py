import asyncio
import asyncpg
import os

async def create_database():
    try:
        # Connect to default postgres database
        conn = await asyncpg.connect(user='postgres', password='8', host='localhost', port=5432, database='postgres')
        # Create database cora
        await conn.execute('CREATE DATABASE cora')
        print("Database 'cora' created successfully.")
        await conn.close()
    except asyncpg.exceptions.DuplicateDatabaseError:
        print("Database 'cora' already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    asyncio.run(create_database())
