class Request:
	def __init__(self, id:int):
		self.ID = id
	
	def __str__(self) -> str:
		return f"[request id: {self.ID}]"
	
