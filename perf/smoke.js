// Smoke test de k6: comprueba que k6 funciona y que la API responde.
// Uso:  k6 run perf/smoke.js            (con la app corriendo en http://localhost:8000)
//       k6 run -e BASE_URL=http://localhost:8001 perf/smoke.js
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  vus: 2,
  duration: '10s',
  thresholds: {
    http_req_failed: ['rate<0.01'],   // menos de 1% de errores
    http_req_duration: ['p(95)<500'], // el 95% responde en menos de 500 ms
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/api/products?page=1`);
  check(res, {
    'responde 200': (r) => r.status === 200,
    'trae productos': (r) => r.json('total') > 0,
  });
  sleep(1);
}
