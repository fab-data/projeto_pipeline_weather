-- Inicializa DB de dados no mesmo postgres do Airflow (UTF8)
-- Evita host.docker.internal e o erro latin1 0xe7
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'weather_user') THEN
        CREATE USER weather_user WITH PASSWORD '123456';
    END IF;
END
$$;

SELECT 'CREATE DATABASE aula_weather OWNER weather_user ENCODING ''UTF8'' LC_COLLATE ''en_US.UTF-8'' LC_CTYPE ''en_US.UTF-8'' TEMPLATE template0'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'aula_weather')\gexec

GRANT ALL PRIVILEGES ON DATABASE aula_weather TO weather_user;
-- Garante encoding do DB template0 é UTF8 (postgres:16 default já é UTF8)
