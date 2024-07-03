# Volatility Manager

## Running in Docker

To start the container you can use this command

```sh
docker compose up --build
```

The program will execute `binance_volatility_manager`, fetching data from 'https://api.binance.com/api/v3/klines' for the following pairs:

- BTCUSDT
- ETHBTC
- LTCBTC
- DGBBTC
- DOGEBTC

Data will be retrieved at 1-minute intervals with a limit of 60 entries.

## Alternative providers

If you wish to use another provider for this data, you would have to subclass the abstract volatility manager and implement its fetch_data with your own provider while preserving the return type.
