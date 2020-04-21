class CreateSQL:

    create_dim_country = (
        """
        CREATE TABLE IF NOT EXISTS public.dim_country (
            id BIGINT PRIMARY KEY ENCODE RAW,
            entity VARCHAR(100) ENCODE ZSTD,
            currency VARCHAR(100) ENCODE ZSTD,
            alpha_code VARCHAR(3) ENCODE ZSTD,
            numeric_code SMALLINT ENCODE AZ64,
            minor_unit SMALLINT ENCODE AZ64,
            extracted_at TIMESTAMP DEFAULT GETDATE() ENCODE AZ64
        ) DISTSTYLE ALL
        SORTKEY (id);
        """
    )

    create_dim_date = (
        """
        CREATE TABLE IF NOT EXISTS public.dim_date (
            id BIGINT NOT NULL PRIMARY KEY ENCODE RAW,
            date_time TIMESTAMP DISTKEY ENCODE AZ64,
            "date" DATE NOT NULL ENCODE AZ64,
            "hour" SMALLINT ENCODE AZ64,
            "day" SMALLINT ENCODE AZ64,
            week SMALLINT ENCODE AZ64,
            "month" SMALLINT ENCODE ZSTD,
            "year" SMALLINT ENCODE AZ64,
            week_day SMALLINT ENCODE ZSTD,
            extracted_at TIMESTAMP DEFAULT GETDATE() ENCODE AZ64
        ) DISTSTYLE KEY
        SORTKEY (id);
        """
    )

    create_dim_fx_rate = (
        """
        CREATE TABLE IF NOT EXISTS public.dim_fx_rate (
            id BIGINT PRIMARY KEY IDENTITY(0, 1) ENCODE RAW,
            exchange VARCHAR(3) ENCODE ZSTD,
            base VARCHAR(3) ENCODE ZSTD,
            rates NUMERIC(18, 10) ENCODE AZ64,
            "date" TIMESTAMP DISTKEY ENCODE AZ64,
            file_date TIMESTAMP ENCODE AZ64,
            extracted_at TIMESTAMP DEFAULT GETDATE() ENCODE AZ64
        ) DISTSTYLE KEY
        SORTKEY (date, exchange);
        """
    )

    create_fact_transaction = (
        """
        CREATE TABLE IF NOT EXISTS public.fact_transaction (
            id BIGINT PRIMARY KEY IDENTITY(0, 1) ENCODE RAW,
            country_id BIGINT ENCODE ZSTD REFERENCES public.dim_country(id),
            customer_id BIGINT ENCODE ZSTD,
            date_id BIGINT DISTKEY ENCODE AZ64,
            fx_rate_id BIGINT ENCODE ZSTD REFERENCES public.dim_country(id),
            invoice_id VARCHAR(50) ENCODE ZSTD,
            invoice_date TIMESTAMP ENCODE AZ64,
            stock_code VARCHAR(50) ENCODE ZSTD,
            description VARCHAR(255) ENCODE ZSTD,
            quantity INT ENCODE AZ64,
            price NUMERIC(12,2) ENCODE AZ64,
            extracted_at TIMESTAMP DEFAULT GETDATE() ENCODE AZ64
        ) SORTKEY (date_id);
        """
    )

    create_staging_country = (
        """
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            entity VARCHAR(255),
            currency VARCHAR(255),
            alpha_code VARCHAR(255),
            numeric_code VARCHAR(255),
            minor_unit VARCHAR(255)
        ) BACKUP NO;
        """
    )

    create_staging_fx_rate = (
        """
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            exchange VARCHAR(255),
            base VARCHAR(255),
            rates VARCHAR(255),
            date VARCHAR(255),
            file_date VARCHAR(255)
        ) BACKUP NO;
        """
    )

    create_staging_transaction = (
        """
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            invoice_id VARCHAR(255),
            stock_code VARCHAR(255),
            description VARCHAR(255),
            quantity VARCHAR(255),
            invoice_date VARCHAR(255),
            price VARCHAR(255),
            customer_id VARCHAR(255),
            country VARCHAR(255)
        ) BACKUP NO;
        """
    )
