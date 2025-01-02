import asyncio
from common.constants import MAX_CONNECTIONS, SCHEDULE_PERIOD
from common.response import Response


class Scheduler:
	def __init__(self, stop_event:asyncio.Event, schedule_period:float=SCHEDULE_PERIOD, max_active_tasks=MAX_CONNECTIONS):
		self._task_queue = asyncio.Queue()
		self._maximum_active_tasks = max_active_tasks
		self._schedule_period = schedule_period

		self._results = {}
		self._results_events = {}
		self._results_lock = asyncio.Lock()
		self._stop_event = stop_event

		self._active_tasks = 0
		self._active_tasks_lock = asyncio.Lock()


	async def _handle_task(self, task:asyncio.Task[Response]):
		response = await task

		async with self._results_lock:
			if response.id in self._results_events:
				self._results_events[response.id].set()
				self._results[response.id] = response


	async def _periodic_schedule(self):
		while not self._stop_event.is_set():
			await asyncio.sleep(self._schedule_period)
			activated = 0

			async with self._active_tasks_lock:
				free_slots = self._maximum_active_tasks - self._active_tasks

				if free_slots > 0:
					activated = min(free_slots, self._task_queue.qsize())
					self._active_tasks += activated

			if activated > 0:
				batch = [await self._task_queue.get() for _ in range(activated)]
				await asyncio.gather(*(self._handle_task(t) for t in batch))
				async with self._active_tasks_lock:
					self._active_tasks -= activated

	
	async def _enqueue(self,id:int, task:asyncio.Task[Response]) -> asyncio.Event:
		await self._task_queue.put(task)

		async with self._results_lock:
			if id not in self._results_events or not self._results_events[id]:
				event = asyncio.Event()
				self._results_events[id] = event
			else:
				event = self._results_events[id]

		return event


	async def _execute_immediately(self, task:asyncio.Task[Response]) -> Response:
		async with self._active_tasks_lock:
			if self._active_tasks < self._maximum_active_tasks:
				self._active_tasks += 1
			else:
				return None

		result = await task
		async with self._active_tasks_lock:
			self._active_tasks -= 1

		return result


	async def add_task(self, id:int, task):

		result = await self._execute_immediately(task)

		if not result:
			return await self._enqueue(id, task)
		
		return result
	
	async def get_result(self, id:int) -> Response:
		result = None
		async with self._results_lock:
			if id in self._results:
				result = self._results[id]
				self._results_events[id] = None
			return result
		
	
	async def run(self):
		return asyncio.create_task(self._periodic_schedule())