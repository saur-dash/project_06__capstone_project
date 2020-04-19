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
        SORTKEY (entity);
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
        SORTKEY (date_time);
        """
    )

    create_dim_fx_rate = (
        """
        CREATE TABLE IF NOT EXISTS public.dim_fx_rate (
            id BIGINT NOT NULL PRIMARY KEY ENCODE RAW,
            "date" TIMESTAMP DISTKEY ENCODE AZ64,
            base VARCHAR(3) ENCODE ZSTD,
            gbp NUMERIC(18, 10) ENCODE AZ64,
            hkd NUMERIC(18, 10) ENCODE AZ64,
            idr NUMERIC(18, 10) ENCODE AZ64,
            php NUMERIC(18, 10) ENCODE AZ64,
            lvl NUMERIC(18, 10) ENCODE AZ64,
            inr NUMERIC(18, 10) ENCODE AZ64,
            chf NUMERIC(18, 10) ENCODE AZ64,
            mxn NUMERIC(18, 10) ENCODE AZ64,
            sgd NUMERIC(18, 10) ENCODE AZ64,
            czk NUMERIC(18, 10) ENCODE AZ64,
            thb NUMERIC(18, 10) ENCODE AZ64,
            bgn NUMERIC(18, 10) ENCODE AZ64,
            eur NUMERIC(18, 10) ENCODE AZ64,
            myr NUMERIC(18, 10) ENCODE AZ64,
            nok NUMERIC(18, 10) ENCODE AZ64,
            cny NUMERIC(18, 10) ENCODE AZ64,
            hrk NUMERIC(18, 10) ENCODE AZ64,
            pln NUMERIC(18, 10) ENCODE AZ64,
            ltl NUMERIC(18, 10) ENCODE AZ64,
            try NUMERIC(18, 10) ENCODE AZ64,
            zar NUMERIC(18, 10) ENCODE AZ64,
            cad NUMERIC(18, 10) ENCODE AZ64,
            brl NUMERIC(18, 10) ENCODE AZ64,
            ron NUMERIC(18, 10) ENCODE AZ64,
            dkk NUMERIC(18, 10) ENCODE AZ64,
            nzd NUMERIC(18, 10) ENCODE AZ64,
            eek NUMERIC(18, 10) ENCODE AZ64,
            jpy NUMERIC(18, 10) ENCODE AZ64,
            rub NUMERIC(18, 10) ENCODE AZ64,
            krw NUMERIC(18, 10) ENCODE AZ64,
            usd NUMERIC(18, 10) ENCODE AZ64,
            aud NUMERIC(18, 10) ENCODE AZ64,
            huf NUMERIC(18, 10) ENCODE AZ64,
            sek NUMERIC(18, 10) ENCODE AZ64,
            extracted_at TIMESTAMP DEFAULT GETDATE() ENCODE AZ64
        ) DISTSTYLE KEY
        SORTKEY ("date");
        """
    )

    create_fact_transaction = (
        """
        CREATE TABLE IF NOT EXISTS public.fact_transaction (
            id BIGINT PRIMARY KEY IDENTITY(0, 1) ENCODE RAW,
            country_id BIGINT ENCODE ZSTD REFERENCES public.dim_country(id),
            customer_id VARCHAR(50) ENCODE ZSTD,
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
            "date" VARCHAR(255),
            base VARCHAR(255),
            gbp VARCHAR(255),
            hkd VARCHAR(255),
            idr VARCHAR(255),
            php VARCHAR(255),
            lvl VARCHAR(255),
            inr VARCHAR(255),
            chf VARCHAR(255),
            mxn VARCHAR(255),
            sgd VARCHAR(255),
            czk VARCHAR(255),
            thb VARCHAR(255),
            bgn VARCHAR(255),
            eur VARCHAR(255),
            myr VARCHAR(255),
            nok VARCHAR(255),
            cny VARCHAR(255),
            hrk VARCHAR(255),
            pln VARCHAR(255),
            ltl VARCHAR(255),
            try VARCHAR(255),
            zar VARCHAR(255),
            cad VARCHAR(255),
            brl VARCHAR(255),
            ron VARCHAR(255),
            dkk VARCHAR(255),
            nzd VARCHAR(255),
            eek VARCHAR(255),
            jpy VARCHAR(255),
            rub VARCHAR(255),
            krw VARCHAR(255),
            usd VARCHAR(255),
            aud VARCHAR(255),
            huf VARCHAR(255),
            sek VARCHAR(255)
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
