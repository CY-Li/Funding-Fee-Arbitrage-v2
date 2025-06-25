# Funding Fee Arbitrage Bot

This project is a cryptocurrency trading bot that implements a funding fee arbitrage strategy between Gate.io and Bitget. It includes a trading bot, a web server for monitoring, and data analysis scripts.

## Deployment to Zeabur (via Docker)

This project is configured for easy deployment on [Zeabur](https://zeabur.com/) using Docker, which provides a more stable and consistent environment.

### 1. Fork and Connect Your Repository

1.  **Fork this repository** to your own GitHub account.
2.  **Create a new project** on your Zeabur dashboard.
3.  **Connect your GitHub account** and select the forked repository.

Zeabur will automatically detect the `Dockerfile` and build a Docker image from it.

### 2. Create and Configure Services

You need to create two services from this single Docker image.

1.  From your Zeabur project dashboard, click "Add Service" and choose "Deploy your source code".
2.  Select your repository. Zeabur will build it. After the build is complete, you will have one service.
3.  Rename this service to **`web`**.
4.  Go to the **`web`** service's **Settings** tab and set the **Start Command** to:
    ```bash
    python main.py
    ```
5.  Now, create the second service for the bot. Go back to your project dashboard, click the "..." menu on the service you just configured, and select **"Duplicate"**.
6.  Rename the new duplicated service to **`worker`**.
7.  Go to the **`worker`** service's **Settings** tab and change its **Start Command** to:
    ```bash
    python trading_bot.py
    ```

### 3. Configure Environment Variables

For **both** services (`web` and `worker`), go to the "Variables" tab and add the following environment variables.

#### Required API Keys:

These are essential for the bot to connect to the exchanges.

| Variable Name           | Description                      |
| ----------------------- | -------------------------------- |
| `GATEIO_API_KEY`        | Your Gate.io API Key             |
| `GATEIO_SECRET_KEY`     | Your Gate.io API Secret          |
| `BITGET_API_KEY`        | Your Bitget API Key              |
| `BITGET_SECRET_KEY`     | Your Bitget API Secret           |
| `BITGET_API_PASSPHRASE` | Your Bitget API Passphrase       |

#### Trading Mode:

Set this to `False` to enable live trading.

| Variable Name | Value   | Description                    |
| ------------- | ------- | ------------------------------ |
| `TEST_MODE`   | `False` | Enables live trading. (Default is `True`) |

#### Optional Strategy Parameters:

You can override the default strategy parameters by setting these variables. If you don't set them, the default values from `config.py` will be used.

| Variable Name                   | Default | Description                                 |
| ------------------------------- | ------- | ------------------------------------------- |
| `POSITION_SIZE_USDT`            | `100.0` | Position size in USDT.                      |
| `MIN_FUNDING_RATE_DIFFERENCE`   | `0.10`  | 10% min annualized rate diff to open.       |
| `MAX_PRICE_SPREAD`              | `0.005` | 0.5% max price spread to open.              |
| `CLOSE_FUNDING_RATE_DIFFERENCE` | `0.02`  | 2% rate diff to close.                      |
| `STOP_LOSS_USDT`                | `-2.0`  | PnL in USDT to trigger stop-loss.           |
| `MAX_HOLDING_DURATION_HOURS`    | `168`   | 7 days max holding time.                    |
| `MIN_HOLDING_HOURS_FOR_REVERSAL`| `4.0`   | Min hours to hold before closing on reversal.|
| `MAX_HOLDING_PRICE_SPREAD`      | `0.01`  | 1% max price spread while holding.          |
| `LOOP_INTERVAL_SECONDS`         | `60`    | Seconds between each check cycle.           |


### 4. Final Deploy

Once the variables are set, **re-deploy** both services from the Zeabur dashboard if they haven't started automatically.

-   The `web` service will provide a public URL for the monitoring dashboard.
-   The `worker` service will run the bot, and you can view its logs on Zeabur.

## Local Development (with Docker)

1.  **Build the Docker image**:
    ```bash
    docker build -t funding-arbitrage .
    ```
2.  **Run the web server**:
    ```bash
    docker run -p 8080:8080 --env-file .env funding-arbitrage python main.py
    ```
    *(Note: You'll need to create a `.env` file for local testing with your API keys)*
3.  **Run the bot**:
    ```bash
    docker run --env-file .env funding-arbitrage python trading_bot.py
    ``` 