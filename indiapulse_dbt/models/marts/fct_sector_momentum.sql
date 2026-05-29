{{ config(materialized='table') }}

with base as (
    select
        trade_date,
        sector,
        avg(daily_return)   as avg_daily_return,
        count(*)            as stock_count,
        sum(volume)         as total_volume
    from {{ ref('stg_nse_daily') }}
    group by trade_date, sector
),

with_momentum as (
    select
        *,
        avg(avg_daily_return) over (
            partition by sector
            order by trade_date
            rows between 4 preceding and current row
        ) as momentum_5d,
        sum(total_volume) over (
            partition by sector
            order by trade_date
            rows between 4 preceding and current row
        ) as volume_5d
    from base
)

select * from with_momentum
order by trade_date desc, sector