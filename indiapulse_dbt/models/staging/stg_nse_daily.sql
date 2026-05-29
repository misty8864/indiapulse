{{ config(materialized='view') }}

select
    trade_date,
    ticker_symbol,
    series,
    sector,
    open_price,
    close_price,
    volume,
    daily_return,
    close_price - open_price as price_change,
    case
        when daily_return > 0 then 'positive'
        when daily_return < 0 then 'negative'
        else 'neutral'
    end as return_direction
from {{ source('raw', 'nse_bhavcopy') }}
where close_price is not null
  and open_price is not null
  and open_price > 0