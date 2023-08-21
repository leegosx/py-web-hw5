import asyncio
import logging
import aiohttp
import platform
import websockets
import aiofiles
import names
from datetime import datetime, timedelta
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects.')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects.')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)
            logging.info(f'{ws.remote_address} closed.')
    
    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.startswith('exchange'):
                await self.send_to_clients(f"{ws.name}: {message}")
                try:
                    if message == 'exchange':
                        num_days = 1
                    else:
                        split_msg = message.split()  # Extract the number of days
                        if len(split_msg) > 1:
                            num_days = int(split_msg[1])
                        else:
                            await ws.send("Invalid command. Usage: 'exchange <days>'")
                            continue  # Skip further processing for this iteration
                    
                    if num_days > 0:
                        exchange_rates = await self.get_exchange_rates_for_days(num_days)
                        formatted_response = self.formated_exchange_rates(exchange_rates)
                        await ws.send(formatted_response)
                        await self.log_exchange_command(ws.name, num_days)
                    else:
                        await ws.send("Invalid command. Usage: 'exchange <days>'")
                except ValueError:
                    await ws.send("Invalid command. Usage: 'exchange <days>'")
            else:
                await self.send_to_clients(f"{ws.name}: {message}")

    def formated_exchange_rates(self, exchange_rates):
        formatted = "Exchange Rates:\n"
        for rates in exchange_rates:
            date, currencies = list(rates.items())[0]
            formatted += f"Date: {date}\n"
            for currency, values in currencies.items():
                sale_rate = values['sale']
                purchase_rate = values['purchase']
                formatted += f"{currency}: Sale - {sale_rate}, Purchase - {purchase_rate}\n|"
        return formatted

    async def get_exchange_rates_for_days(self, days):
        exchange_rate = []
        today = datetime.now()
        for day in range(days, 0, -1):
            date = (today - timedelta(days=day)).strftime('%d.%m.%Y')  
            rates = await self.get_exchange_rates(date)
            if rates:
                filtered_rates = []
                for rate in rates['exchangeRate']:
                    if rate['currency'] in ['USD', 'EUR']:
                        filtered_rates.append(rate)
                exchange_rate.append({
                    date: {
                        rate['currency']: {
                            'sale': rate['saleRate'],
                            'purchase': rate['purchaseRate']
                        }
                        for rate in filtered_rates
                    }
                })
        return exchange_rate
          
    async def get_exchange_rates(self, date):
        api_url = f'https://api.privatbank.ua/p24api/exchange_rates?date={date}'
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(api_url) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result
            except aiohttp.ClientError as e:
                logging.error(f"An error occurred during the request: {e}")
                return None

    async def log_exchange_command(self, user_name, days):
        log_line = f"{user_name} executed 'exchange' command for {days} days"
        async with aiofiles.open('exchange_log.txt', mode='a') as log_file:
            await log_file.write(log_line + '\n')


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future() 


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())