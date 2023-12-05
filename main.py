import asyncio
from time import perf_counter
from typing import Iterable

import websockets
from prometheus_client import (
    start_http_server,
    REGISTRY,
)
from prometheus_client.metrics_core import (
    GaugeMetricFamily,
    Metric,
)
from prometheus_client.registry import Collector

URI_LIST = ['ws://ssssss', 'wss://fffffffffff']
SLEEP_DELAY = 10
PROMETHEUS_PORT = 9000
PROMETHEUS_ADDR = '127.0.0.1'


class ProbeResult:
    def __init__(self, uri: str, is_up: bool, latency: int | float):
        self.uri = uri
        self.is_up = is_up
        self.latency: float = round(latency, 2)


async def get_probe_results() -> list[ProbeResult]:
    results = []
    for uri in URI_LIST:
        t_start = perf_counter()
        async with websockets.connect(uri) as ws:
            latency_ms = (perf_counter() - t_start) * 1000
            results.append(ProbeResult(uri, bool(ws), latency_ms))
    return results


class ResultCollector(Collector):
    def collect(self) -> Iterable[Metric]:
        for result in asyncio.run(get_probe_results()):
            yield GaugeMetricFamily(
                'websocket_probe_success',
                '1 if websocket is up, 0 otherwise',
                value=int(result.is_up),
                labels=[result.uri]
            )
            yield GaugeMetricFamily(
                'websocket_probe_latency',
                'latency in connection',
                value=result.latency,
                unit='milliseconds',
                labels=[result.uri]
            )


if __name__ == '__main__':
    REGISTRY.register(ResultCollector())
    start_http_server(port=PROMETHEUS_PORT, addr=PROMETHEUS_ADDR)
