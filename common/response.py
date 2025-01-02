import enum

from api.status import STATUS_SUCCESS

class Status(enum.Enum):
	OK = 1
	ERR = 2

class Response:
	def __init__(self, id:int, status:Status, msg:str, active_conns:int):
		self.id:int = id
		self.status:Status = status
		self.message:str = msg
		self.active_conns:int = active_conns

	def __str__(self) -> str:
		return f"[status: {self.status} message: {self.message} conns: {self.active_conns}]"


def get_ok_response(id:int, conns:int) -> Response:
	return Response(id, Status.OK, STATUS_SUCCESS, conns)

def get_err_response(id:int, msg:str, conns:int) -> Response:
	return Response(id, Status.ERR, msg, conns)