import asyncio
import random
import time
from common import Response, get_err_response, get_ok_response
from api.status import ERR_MAX_CONN, ERR_PROB_FAULT
from common.constants import *
from common.request import Request

random.seed(time.time())
rng = random.Random()

class API:
	def __init__(
			self, 
			max_connections:int=MAX_CONNECTIONS,
			min_compute_time:int=MIN_COMPUTE_TIME, 
			max_compute_time:int=MAX_COMPUTE_TIME,
			error_margin:float=ERROR_MARGIN,
			response_time:int=DEFAULT_SERVER_RESPONSE_TIME,
			):
		
		self._current_connections:int = 0
		self._error_margin:float = error_margin
		self._max_connections:int = max_connections
		self._max_compute_time:int = max_compute_time
		self._min_compute_time:int = min_compute_time
		self._current_connections_lock = asyncio.Lock()
		self._response_time = response_time

	def _get_compute_time(self, conns):
		return 0.250
		# return (rng.randint(self._min_compute_time, self._max_compute_time) * rng.random()) / 1000.0 * max(conns, 1) if self._response_time == DEFAULT_SERVER_RESPONSE_TIME else self._response_time / 1000.0
		
	async def _compute_response(self, conns, req_id) -> Response:
		await asyncio.sleep(self._get_compute_time(conns))
		return get_err_response(req_id, ERR_PROB_FAULT, conns) if rng.random() <= self._error_margin else get_ok_response(req_id, conns)
				
	async def get(self, request:Request) -> Response:
		active_conns = 0

		print(f'{request.ID}:{time.time():2.3f}:-1:server')
		async with self._current_connections_lock:
			if self._current_connections == MAX_CONNECTIONS:
				print(f'{request.ID}:{time.time():2.3f}:1')
				return get_err_response(request.ID, ERR_MAX_CONN, self._current_connections)
			
			self._current_connections += 1
			active_conns = self._current_connections

		response = await self._compute_response(active_conns, request.ID)

		async with self._current_connections_lock:
			self._current_connections -= 1

		print(f'{request.ID}:{time.time():2.3f}:1:server')

		return response
