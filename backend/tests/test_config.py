from app.core.config import Settings


def test_connection_urls_escape_credentials():
    settings = Settings(
        postgres_user="loci/user",
        postgres_password="p@ss/word:with+chars",
        postgres_host="localhost",
        postgres_port=5432,
        postgres_db="loci",
        redis_password="redis/p@ss:with+chars",
    )

    assert (
        settings.sqlalchemy_database_url
        == "postgresql+asyncpg://loci%2Fuser:p%40ss%2Fword%3Awith%2Bchars"
        "@localhost:5432/loci"
    )
    assert settings.redis_dsn == "redis://:redis%2Fp%40ss%3Awith%2Bchars@localhost:6379/0"
