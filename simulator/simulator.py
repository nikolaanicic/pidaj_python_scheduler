




import asyncio
import random
import time
from client.client import Client
from common.request import Request


class Simulator:
	def __init__(self, client_factory):
		random.seed(time.time())
		self._rng = random.Random()
		self._client_factory = client_factory
	

	async def _one(self, id:int):
		t = self._rng.randrange(10, 100)
		await asyncio.sleep(t / 1000.0)
		client = self._client_factory()
		
		await client.get(Request(id))



	async def simulate(self, calls:int):
		tasks = [asyncio.create_task(self._one(id)) for id in range(calls)]
		await asyncio.gather(*tasks)


	
