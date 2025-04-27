# Qntropy

Qntropy es una aplicación en Python diseñada para analizar y procesar archivos CSV exportados desde CoinTracking.info, proporcionando información valiosa sobre tus transacciones de criptomonedas y ayudando a la preparación de informes fiscales para inversores españoles.

## Descripción

Esta herramienta permite importar datos de transacciones de criptomonedas desde archivos CSV de CoinTracking.info y realizar diversos análisis, como:

- Detección y corrección de operaciones faltantes
- Consolidación de saldos
- Resumen de transacciones por tipo (depósitos, retiros, trades, comisiones)
- Análisis de rendimiento por activo
- Cálculo de ganancias y pérdidas para declaración fiscal
- Visualizaciones de la evolución de tu portafolio
- Exportación de datos procesados para informes fiscales compatibles con la legislación española

## Estructura del Proyecto

```
Qntropy/
├── config/           # Archivos de configuración
├── data/
│   ├── input/        # Archivos CSV originales de CoinTracking.info
│   └── output/       # Archivos de resultados procesados
├── docs/             # Documentación
├── src/              # Código fuente
│   └── qntropy/      # Módulo principal
├── tests/            # Tests unitarios y de integración
│   ├── fixtures/     # Datos de muestra para pruebas
│   ├── unit/         # Tests unitarios
│   └── integration/  # Tests de integración
├── tools/            # Herramientas auxiliares
├── pyproject.toml    # Configuración de Poetry y del proyecto
├── LICENSE           # Información de licencia
└── README.md         # Este archivo
```

## Requisitos

- Python 3.11+
- [Poetry](https://python-poetry.org/) para gestión de dependencias

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/yourusername/Qntropy.git
   cd Qntropy
   ```

2. Instala Poetry si aún no lo tienes:
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Instala las dependencias usando Poetry:
   ```
   poetry install
   ```

4. (Opcional) Instala los hooks de pre-commit:
   ```
   poetry run pre-commit install
   ```

## Uso

### Importar transacciones desde Cointracking.info

```bash
# Activar el entorno virtual de Poetry
poetry shell

# Importar un archivo CSV de Cointracking.info
qntropy import-cointracking path/to/cointracking_export.csv

# Guardar las transacciones importadas en formato JSON
qntropy import-cointracking path/to/cointracking_export.csv -o transactions.json

# Ver ayuda y opciones disponibles
qntropy import-cointracking --help
```

### Mostrar versión

```bash
qntropy version
```

## Formato de Datos de Entrada

La aplicación está diseñada para trabajar con archivos CSV de CoinTracking.info que contienen las siguientes columnas:
- Type (tipo de operación: Deposit, Trade, Withdrawal, etc.)
- Buy Amount (cantidad comprada)
- Buy Currency (moneda comprada)
- Sell Amount (cantidad vendida)
- Sell Currency (moneda vendida)
- Fee (comisión)
- Fee Currency (moneda de la comisión)
- Exchange (plataforma de intercambio)
- Group (grupo de transacción)
- Comment (comentario)
- Date (fecha y hora)

## Desarrollo

### Ejecutar Tests

```bash
# Ejecutar todos los tests
poetry run pytest

# Ejecutar tests con cobertura
poetry run pytest --cov=qntropy

# Ejecutar solo tests unitarios o de integración
poetry run pytest tests/unit/
poetry run pytest tests/integration/
```

### Linting y Formateo

```bash
# Ejecutar linters
poetry run ruff check .
poetry run mypy .

# Formatear código
poetry run black .
```

## Contribuir

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
4. Haz push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo los términos especificados en el archivo LICENSE.

## Contacto

Si tienes preguntas o sugerencias, no dudes en abrir un issue en este repositorio.
