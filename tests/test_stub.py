from unittest import TestCase
from pjrpc import stub, spec


class StubTestCase(TestCase):
    def setUp(self):
        self.stub = stub.Stub(True)

    def test_server_pack_success_message(self):
        response = spec.SuccessResponseMessage(id=1, result={'name': 'Test', 'age': 1})
        data = self.stub.pack(response)
        self.assertEqual(stub.decompress(data), b'{"jsonrpc":"2.0","id":1,"result":{"name":"Test","age":1}}')

    def test_server_pack_error_message(self):
        response = spec.ErrorResponseMessage(id=1, error=spec.Error(1, 'message'))
        data = self.stub.pack(response)
        self.assertEqual(stub.decompress(data), b'{"jsonrpc":"2.0","id":1,"error":{"code":1,"message":"message","data":null}}')

    def test_server_unpack_message(self):
        data = stub.compress(b'{"id":1,"jsonrpc":"2.0","params":{"a":1,"b":2},"method":"rpc.add"}')
        request = self.stub.unpack(data)
        self.assertEqual(request.method, 'rpc.add')
        self.assertEqual(request.params, {'a': 1, 'b': 2})

    def test_client_pack_request(self):
        request = spec.CallingMessage(id=1, method='rpc.add', params={'a': 1, 'b': 2})
        data = self.stub.pack(request)
        self.assertEqual(stub.decompress(data), b'{"jsonrpc":"2.0","method":"rpc.add","params":{"a":1,"b":2},"id":1}')

    def test_client_unpack_success_response(self):
        data = stub.compress(b'{"id":1,"jsonrpc":"2.0","result":{"sum":3}}')
        response = self.stub.unpack(data)
        self.assertEqual(response.id, 1)
        self.assertEqual(response.result, {'sum': 3})

    def test_client_unpack_error_response(self):
        data = stub.compress(b'{"id":1,"jsonrpc":"2.0","error":{"code":1,"message":"error"}}')
        response = self.stub.unpack(data)
        self.assertEqual(response.id, 1)
        self.assertEqual(response.error, spec.Error(1, 'error'))
