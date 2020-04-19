class InsertSQL:

    insert_dim_country = (
        """
        INSERT INTO public.dim_country (
            id,
            entity,
            currency,
            alpha_code,
            numeric_code,
            minor_unit
        )
        SELECT DISTINCT
            ROW_NUMBER () OVER (ORDER BY entity) :: SMALLINT,
            entity :: VARCHAR,
            currency :: VARCHAR,
            alpha_code :: VARCHAR,
            numeric_code :: SMALLINT,
            minor_unit :: SMALLINT
        FROM public.staging_country__{tstamp}
        ORDER BY entity;
        """
    )

    insert_dim_date = (
        """
        INSERT INTO public.dim_date (
            id,
            date_time,
            date,
            hour,
            day,
            week,
            month,
            year,
            week_day
        )
        SELECT DISTINCT
            EXTRACT(epoch FROM invoice_date :: TIMESTAMP) :: BIGINT,
            invoice_date :: TIMESTAMP AS date_time,
            invoice_date :: DATE AS date,
            EXTRACT (HOUR FROM date_time) :: SMALLINT,
            EXTRACT(DAY FROM date_time) :: SMALLINT,
            EXTRACT(WEEK FROM date_time) :: SMALLINT,
            EXTRACT(MONTH FROM date_time) :: SMALLINT,
            EXTRACT(YEAR FROM date_time) :: SMALLINT,
            EXTRACT(DOW FROM date_time) :: SMALLINT
        FROM public.staging_transaction__{tstamp};
        """
    )

    insert_dim_fx_rate = (
        """
        INSERT INTO public.dim_fx_rate (
            id,
            date,
            base,
            gbp,
            hkd,
            idr,
            php,
            lvl,
            inr,
            chf,
            mxn,
            sgd,
            czk,
            thb,
            bgn,
            eur,
            myr,
            nok,
            cny,
            hrk,
            pln,
            ltl,
            try,
            zar,
            cad,
            brl,
            ron,
            dkk,
            nzd,
            eek,
            jpy,
            rub,
            krw,
            usd,
            aud,
            huf,
            sek
        )
        SELECT DISTINCT
            EXTRACT(epoch FROM TO_TIMESTAMP(date, 'YYYY-MM-DD')) :: BIGINT,
            TO_TIMESTAMP(date, 'YYYY-MM-DD') :: TIMESTAMP,
            base :: VARCHAR,
            gbp :: NUMERIC(18, 10),
            hkd :: NUMERIC(18, 10),
            idr :: NUMERIC(18, 10),
            php :: NUMERIC(18, 10),
            lvl :: NUMERIC(18, 10),
            inr :: NUMERIC(18, 10),
            chf :: NUMERIC(18, 10),
            mxn :: NUMERIC(18, 10),
            sgd :: NUMERIC(18, 10),
            czk :: NUMERIC(18, 10),
            thb :: NUMERIC(18, 10),
            bgn :: NUMERIC(18, 10),
            eur :: NUMERIC(18, 10),
            myr :: NUMERIC(18, 10),
            nok :: NUMERIC(18, 10),
            cny :: NUMERIC(18, 10),
            hrk :: NUMERIC(18, 10),
            pln :: NUMERIC(18, 10),
            ltl :: NUMERIC(18, 10),
            try :: NUMERIC(18, 10),
            zar :: NUMERIC(18, 10),
            cad :: NUMERIC(18, 10),
            brl :: NUMERIC(18, 10),
            ron :: NUMERIC(18, 10),
            dkk :: NUMERIC(18, 10),
            nzd :: NUMERIC(18, 10),
            eek :: NUMERIC(18, 10),
            jpy :: NUMERIC(18, 10),
            rub :: NUMERIC(18, 10),
            krw :: NUMERIC(18, 10),
            usd :: NUMERIC(18, 10),
            aud :: NUMERIC(18, 10),
            huf :: NUMERIC(18, 10),
            sek :: NUMERIC(18, 10)
        FROM public.staging_fx_rate__{tstamp};
        """
    )

    insert_fact_transaction = (
        """
        BEGIN;

        CREATE TEMP TABLE t1 AS
        SELECT DISTINCT
            id,
            entity
        FROM public.dim_country t1;

        CREATE TEMP TABLE t2 AS
        SELECT DISTINCT
            EXTRACT(
                epoch FROM TO_TIMESTAMP(date, 'YYYY-MM-DD')) :: BIGINT AS id,
            '{tstamp}' AS tstamp
        FROM public.staging_fx_rate__{tstamp} t2;

        CREATE TEMP TABLE t3 AS
        SELECT
            customer_id,
            EXTRACT(epoch FROM invoice_date :: TIMESTAMP) :: BIGINT,
            invoice_id,
            invoice_date,
            stock_code,
            description,
            country,
            quantity,
            price,
            '{tstamp}' AS tstamp
        FROM public.staging_transaction__{tstamp} t3;

        INSERT INTO public.fact_transaction (
            country_id,
            customer_id,
            date_id,
            fx_rate_id,
            invoice_id,
            invoice_date,
            stock_code,
            description,
            quantity,
            price
        )
        SELECT
            t1.id :: BIGINT,
            t3.customer_id ::VARCHAR,
            EXTRACT(epoch FROM t3.invoice_date :: TIMESTAMP) :: BIGINT,
            t2.id :: BIGINT,
            t3.invoice_id :: VARCHAR,
            t3.invoice_date :: TIMESTAMP,
            t3.stock_code :: VARCHAR,
            t3.description :: VARCHAR,
            t3.quantity :: INT,
            t3.price :: NUMERIC(12,2)
        FROM t3
        LEFT JOIN t1
               ON t1.entity = UPPER(t3.country)
        LEFT JOIN t2
               ON t2.tstamp = t3.tstamp;

        DROP TABLE IF EXISTS t1;
        DROP TABLE IF EXISTS t2;
        DROP TABLE IF EXISTS t3;

        COMMIT;
        """
    )
