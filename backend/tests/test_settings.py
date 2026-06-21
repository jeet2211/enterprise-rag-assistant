from app.config.settings import Settings


def test_cors_origins_parse_json():
    settings = Settings(CORS_ORIGINS='["https://app.example.com", "https://admin.example.com"]')

    assert settings.cors_origins == ["https://app.example.com", "https://admin.example.com"]


def test_cors_origins_parse_csv():
    settings = Settings(CORS_ORIGINS="https://one.example.com, https://two.example.com")

    assert settings.cors_origins == ["https://one.example.com", "https://two.example.com"]


def test_cors_origins_accepts_list_value():
    settings = Settings()
    settings.cors_origins_raw = ["https://app.example.com"]

    assert settings.cors_origins == ["https://app.example.com"]
