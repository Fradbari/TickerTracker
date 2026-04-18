# Mock SSE Manager for now to unblock compilation
# Will be fully implemented soon
class SSEManager:
    async def broadcast(self, data: dict):
        pass

sse_manager = SSEManager()
