import asyncio
import sys

import psutil
from api.api import API
from client.client import Client
from common.constants import *
from scheduler.scheduler import Scheduler
from simulator.simulator import Simulator

USAGE = "usage: ./program number_of_client_calls:int client_retry_time_ms:int server_response_time:int"
MIN_ARG_LEN = 3
MAX_ARG_LEN = 4
CLIENT_CALLS_IDX = 1
RETRY_TIME_IDX = 2
RESPONSE_TIME_IDX = 3


async def main(calls:int, client_retry, response_time:int):

	stop_event = asyncio.Event()
	scheduler = Scheduler(stop_event=stop_event)
	api = API()

	def _client_factory() -> Client:
		return Client(client_retry, api, scheduler)

	simulator = Simulator(_client_factory)
	
	scheduler_task = asyncio.create_task(scheduler.run())

	await simulator.simulate(calls)

	stop_event.set()
	await scheduler_task


if __name__ == "__main__":
	length = len(sys.argv)

	if length < MIN_ARG_LEN or length > MAX_ARG_LEN:
		print(USAGE)
		exit(1)

	try:
		calls = max(MIN_CLIENT_CALLS, max(0, int(sys.argv[CLIENT_CALLS_IDX])))
		client_retry = max(MIN_RETRY_TIME, max(0, int(sys.argv[RETRY_TIME_IDX])))
		if len(sys.argv) == MAX_ARG_LEN:
			response_time = min(DEFAULT_SERVER_RESPONSE_TIME, int(sys.argv[RESPONSE_TIME_IDX]))
		else:
			response_time = DEFAULT_SERVER_RESPONSE_TIME
	except Exception as ex:
		print(USAGE)
		print(ex)
		exit(1)

	print(f"{calls}_client_calls_{client_retry}_ms_retry", file=sys.stdout)

	asyncio.run(main(calls,client_retry, response_time))
	
	sys.stdout.flush()