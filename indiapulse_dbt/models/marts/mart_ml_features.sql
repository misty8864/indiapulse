{{ config(materialized='table') }}

with momentum as (
    select * from {{ ref('fct_sector_momentum') }}
),

volatility as (
    select
        trade_date,
        sector,
        stddev(avg_daily_return) over (
            partition by sector order by trade_date
            rows between 9 preceding and current row
        ) as volatility_10d,
        avg(avg_daily_return) over (
            partition by sector order by trade_date
            rows between 19 preceding and current row
        ) as momentum_20d,
        sum(total_volume) over (
            partition by sector order by trade_date
            rows between 9 preceding and current row
        ) as volume_10d
    from momentum
)

select
    m.trade_date,
    m.sector,
    m.avg_daily_return,
    m.momentum_5d,
    m.total_volume,
    v.volatility_10d,
    v.momentum_20d,
    v.volume_10d,
    lead(m.avg_daily_return, 1) over (
        partition by m.sector order by m.trade_date
    ) as next_day_return
from momentum m
join volatility v on m.trade_date = v.trade_date and m.sector = v.sector
where m.momentum_5d is not null