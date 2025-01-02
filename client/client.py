import asyncio
import sys
import time
from api.api import API
from common.constants import MAX_CONNECTIONS
from common.request import Request
from common.response import Response, Status
from scheduler.scheduler import Scheduler

class Client:
	def __init__(self, retry_ms:int, api_stub:API, scheduler:Scheduler):
		self._retry_time_ms = retry_ms
		self._limit_semaphore = asyncio.Semaphore(MAX_CONNECTIONS)
		self._scheduler = scheduler
		self._api_stub = api_stub

	def _get_retry_time(self) -> float:
		return self._retry_time_ms / 1000.0
	
	def _print(self, msg:str):
		print(f"{msg}", file=sys.stdout)

	async def _init_api_call(self, request:Request):
		return await self._scheduler.add_task(request.ID, self._api_stub.get(request))
	
	async def _wait_on_result(self, event:asyncio.Event, id:int) -> Response:
		while not event.is_set():
			await event.wait()

		return await self._scheduler.get_result(id)

	async def get(self, request:Request) -> Response:
		tries = 1

		self._print(f"{request.ID}:{time.time():2.3f}:-1:client")

		response = await self._init_api_call(request)

		if isinstance(response, asyncio.Event):
			response = await self._wait_on_result(response, request.ID)

		while response.status != Status.OK:
			await asyncio.sleep(self._get_retry_time())
			
			start = time.time()
			response = await self._init_api_call(request)
			
			if isinstance(response, asyncio.Event):
				response = await self._wait_on_result(response, request.ID)

			tries += 1	

		self._print(f"{request.ID}:{time.time():2.3f}:{tries}:client")

		return response