class TgPyErrorBase(Exception):
	pass


class ApiError(TgPyErrorBase):
	def __init__(self, answer, msg=None):
		if msg is None:
			msg = f'Api answered with an error: {answer}'
		super(ApiError, self).__init__(msg)


if __name__ == '__main__':
	pass