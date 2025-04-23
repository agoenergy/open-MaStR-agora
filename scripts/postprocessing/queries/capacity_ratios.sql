TRUNCATE TABLE temp_mastr.{{gen_type}}_capa;
INSERT INTO temp_mastr.{{gen_type}}_capa (date_id, capa)
WITH RECURSIVE date_series AS (
    -- Extend the series to include "tomorrow"
    SELECT
        generate_series('2018-06-01'::date, CURRENT_DATE + INTERVAL '7 day', '1 day'::interval)::date AS date_id
),
daily_start_grouped AS (
    SELECT
        COALESCE("Inbetriebnahmedatum", "DatumLetzteAktualisierung")::date AS start_date,
        SUM("Bruttoleistung") AS daily_sum
    FROM
        temp_mastr.{{gen_type}}_extended
    WHERE
        NOT ("Inbetriebnahmedatum" IS NULL AND "DatumEndgueltigeStilllegung" IS NULL)
    GROUP BY
        start_date
    ORDER BY
        start_date
),
cumsum_start_plants AS (
    SELECT
        start_date,
        daily_sum,
        SUM(daily_sum) OVER (ORDER BY start_date) AS start_netto_cumsum
    FROM
        daily_start_grouped
    ORDER BY
        start_date
),
filled_start_data AS (
    -- Start with the first date in date_series
    SELECT
        ds.date_id,
        csp.start_netto_cumsum
    FROM
        date_series ds
    LEFT JOIN
        cumsum_start_plants csp ON csp.start_date = ds.date_id
    WHERE
        ds.date_id = (SELECT MIN(date_id) FROM date_series)

    UNION ALL

    -- Recursively carry forward the last known cumulative value, ensuring it's never reset to NULL or zero
    SELECT
        ds.date_id,
        CASE
            WHEN csp.start_netto_cumsum IS NOT NULL THEN csp.start_netto_cumsum
            ELSE fsd.start_netto_cumsum
        END AS start_netto_cumsum
    FROM
        date_series ds
    LEFT JOIN
        cumsum_start_plants csp ON csp.start_date = ds.date_id
    JOIN
        filled_start_data fsd ON ds.date_id = fsd.date_id + INTERVAL '1 day'
    WHERE
        ds.date_id > (SELECT MIN(date_id) FROM date_series)
),
daily_end_grouped AS (
    SELECT
        -- plus 5 days is randomly chosen just needs to be sufficiently far in the future
        COALESCE("DatumEndgueltigeStilllegung", CURRENT_DATE + INTERVAL '5 day')::date AS end_date,
        SUM("Bruttoleistung") AS daily_sum
    FROM
        temp_mastr.{{gen_type}}_extended
    WHERE
        NOT ("Inbetriebnahmedatum" IS NULL AND "DatumEndgueltigeStilllegung" IS NULL)
    GROUP BY
        end_date
    ORDER BY
        end_date
),
cumsum_end_plants AS (
    SELECT
        end_date,
        daily_sum,
        SUM(daily_sum) OVER (ORDER BY end_date) AS end_netto_cumsum
    FROM
        daily_end_grouped
    ORDER BY
        end_date
),
filled_end_data AS (
    -- Start with the first date in date_series
    SELECT
        ds.date_id,
        cep.end_netto_cumsum
    FROM
        date_series ds
    LEFT JOIN
        cumsum_end_plants cep ON cep.end_date = ds.date_id
    WHERE
        ds.date_id = (SELECT MIN(date_id) FROM date_series)

    UNION ALL

    -- Recursively carry forward the last known cumulative value, ensuring it's never reset to NULL or zero
    SELECT
        ds.date_id,
        CASE
            WHEN cep.end_netto_cumsum IS NOT NULL THEN cep.end_netto_cumsum
            ELSE fed.end_netto_cumsum
        END AS end_netto_cumsum
    FROM
        date_series ds
    LEFT JOIN
        cumsum_end_plants cep ON cep.end_date = ds.date_id
    JOIN
        filled_end_data fed ON ds.date_id = fed.date_id + INTERVAL '1 day'
    WHERE
        ds.date_id > (SELECT MIN(date_id) FROM date_series)
)
SELECT
    fd_start.date_id,
    (COALESCE(fd_start.start_netto_cumsum, 0) - COALESCE(fd_end.end_netto_cumsum, 0))::numeric(18,3) AS capa
FROM
    filled_start_data fd_start
FULL OUTER JOIN
    filled_end_data fd_end ON fd_start.date_id = fd_end.date_id
WHERE
    fd_start.date_id >= '2019-01-01'::date
ORDER BY
    fd_start.date_id;
