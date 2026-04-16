# Configuración de Proxy en Open Interpreter

Esta fork de Open Interpreter incluye soporte completo para proxies HTTP/HTTPS, necesario para descargar modelos LLM en entornos corporativos.

## Variables de Entorno Soportadas

Open Interpreter detecta automáticamente la configuración de proxy del sistema a través de variables de entorno estándar:

### Proxy HTTP/HTTPS

| Variable | Descripción |
|----------|-------------|
| `HTTP_PROXY` | URL del proxy HTTP (mayúsculas). Ejemplo: `http://proxy.empresa.com:8080` |
| `http_proxy` | URL del proxy HTTP (minúsculas). Tiene precedencia sobre mayúsculas. |
| `HTTPS_PROXY` | URL del proxy HTTPS (mayúsculas). Ejemplo: `https://proxy.empresa.com:8443` |
| `https_proxy` | URL del proxy HTTPS (minúsculas). Tiene precedencia sobre mayúsculas. |
| `ALL_PROXY` | URL del proxy para todos los protocolos (mayúsculas). |
| `all_proxy` | URL del proxy para todos los protocolos (minúsculas). |

### Exclusiones de Proxy

| Variable | Descripción |
|----------|-------------|
| `NO_PROXY` | Lista de exclusiones de proxy (mayúsculas). |
| `no_proxy` | Lista de exclusiones de proxy (minúsculas). Tiene precedencia sobre mayúsculas. |

**Formato de NO_PROXY**: Lista separada por comas de hosts/redes que NO deben usar proxy:
- Hostnames exactos: `localhost,myserver`
- IPs: `127.0.0.1,10.0.0.1`
- Rangos CIDR: `127.0.0.0/8,172.17.0.0/16,10.0.0.0/8`
- Dominios con wildcard: `*.local,*.internal,*.docker`

## Ejemplo de Configuración

```bash
# Configurar proxy
export HTTP_PROXY=http://proxy.empresa.com:8080
export HTTPS_PROXY=https://proxy.empresa.com:8443

# Excluir redes locales y Docker
export NO_PROXY=localhost,127.0.0.1,127.0.0.0/8,172.17.0.0/16,172.18.0.0/16,172.19.0.0/16,172.20.0.0/16,*.local,*.docker

# Ejecutar Open Interpreter
python -m interpreter
```

## Dónde se Usa el Proxy

El soporte de proxy se aplica en las siguientes operaciones:

1. **Descarga de modelos LLM** desde HuggingFace o repositorios externos (`local_setup.py`)
2. **Conexión a servidores Ollama** remotos para listar o descargar modelos (`llm.py`)
3. **Verificación de versiones** desde PyPI (`__init__.py`)
4. **Cualquier otra petición HTTP** que realice el intérprete

## Implementación Técnica

### Módulo `proxy_utils.py`

El soporte de proxy está centralizado en el módulo `interpreter/core/utils/proxy_utils.py`:

```python
from interpreter.core.utils.proxy_utils import get_proxy_config, get_wget_proxy_args

# Para requests
proxies = get_proxy_config()
response = requests.get(url, proxies=proxies)

# Para wget
wget_args = get_wget_proxy_args()
subprocess.run(['wget'] + wget_args + [url])
```

### Funciones Principales

- **`get_proxy_config()`**: Devuelve diccionario `{'http': '...', 'https': '...'}` listo para `requests`.
- **`get_wget_proxy_args()`**: Devuelve lista de argumentos de línea de comandos para `wget`.
- **`_should_bypass_proxy(url)`**: Valida si una URL debe excluirse del proxy según `NO_PROXY`.

### Soporte de Patrones NO_PROXY

El módulo implementa lógica avanzada de matching para `NO_PROXY`:

- **Wildcards de dominio**: `*.example.com` coincide con `api.example.com` pero no con `example.com`
- **Rangos CIDR**: `172.17.0.0/16` coincide con cualquier IP en ese rango
- **Hostnames exactos**: `localhost` solo coincide con `localhost`

## Integración con Docker

Cuando Open Interpreter se ejecuta dentro de un contenedor Docker, las variables de entorno de proxy deben pasarse desde el host:

```yaml
services:
  open-interpreter:
    image: intelewriter-open-interpreter:preview
    environment:
      - HTTP_PROXY=${HTTP_PROXY}
      - HTTPS_PROXY=${HTTPS_PROXY}
      - NO_PROXY=${NO_PROXY}
      - http_proxy=${HTTP_PROXY}
      - https_proxy=${HTTPS_PROXY}
      - no_proxy=${NO_PROXY}
```

## Debugging

Para verificar que la configuración de proxy es correcta:

```python
from interpreter.core.utils.proxy_utils import get_proxy_config
import os

print("HTTP_PROXY:", os.getenv('HTTP_PROXY'))
print("HTTPS_PROXY:", os.getenv('HTTPS_PROXY'))
print("NO_PROXY:", os.getenv('NO_PROXY'))
print("Proxy config:", get_proxy_config())
```

## Errores Comunes

### Error 403 Forbidden

**Síntoma**: `Request failed with status code 403`

**Causa**: El proxy está rechazando la conexión.

**Solución**: Verifica que la URL del proxy sea correcta y que tengas permisos de acceso.

### Error 503 Service Unavailable

**Síntoma**: `Request failed with status code 503`

**Causa**: Se está intentando usar el proxy para conexiones internas (Docker).

**Solución**: Añade las redes Docker a `NO_PROXY`:
```bash
export NO_PROXY=127.0.0.0/8,172.17.0.0/16,172.18.0.0/16,172.19.0.0/16,172.20.0.0/16
```

### Timeout en Descargas

**Síntoma**: Las descargas de modelos se quedan colgadas.

**Causa**: El proxy no está configurado o tiene problemas de conectividad.

**Solución**: 
1. Verifica que `http_proxy` y `https_proxy` estén configurados
2. Prueba la conexión manualmente: `curl -x $HTTP_PROXY https://huggingface.co`
3. Verifica que el proxy permita conexiones HTTPS (no solo HTTP)

## Commits Relacionados

- **feat: add proxy support to open-interpreter**: Implementación inicial del soporte de proxy
- **fix: add NO_PROXY support with CIDR range matching**: Soporte de exclusiones de proxy
- **fix: add proxy configuration logging**: Logging diagnóstico de configuración

## Testing

Para probar el soporte de proxy sin tener un proxy real:

```bash
# Simular proxy (sin NO_PROXY debería fallar)
export HTTP_PROXY=http://localhost:9999
python -c "from interpreter.core.utils.proxy_utils import get_proxy_config; print(get_proxy_config())"

# Verificar exclusiones
export NO_PROXY=localhost,127.0.0.1
python -c "from interpreter.core.utils.proxy_utils import _should_bypass_proxy; print(_should_bypass_proxy('http://localhost:8000'))"
```

## Contribuciones

Este soporte de proxy es una extensión específica de Intelequia y no está en el upstream de Open Interpreter. Para mantener compatibilidad con el proyecto original, todos los cambios están aislados en:

- `interpreter/core/utils/proxy_utils.py` (nuevo módulo)
- Modificaciones mínimas en archivos existentes que importan y usan `proxy_utils`

Si necesitas hacer cambios, mantén esta estructura para facilitar futuros merges con upstream.
