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
├── requirements.txt  # Dependencias del proyecto
├── LICENSE           # Información de licencia
└── README.md         # Este archivo
```

## Requisitos

- Python 3.11+

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/yourusername/Qntropy.git
   cd Qntropy
   ```

2. Crea un entorno virtual:
   ```
   python -m venv venv
   ```

3. Activa el entorno virtual:
   ```
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

4. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

5. (Opcional) Instala las dependencias de desarrollo:
   ```
   pip install -r requirements-dev.txt
   ```

6. (Opcional) Instala los hooks de pre-commit:
   ```
   pre-commit install
   ```

## Uso

### Importar transacciones desde Cointracking.info

```bash
# Importar un archivo CSV de Cointracking.info
python -m qntropy import-cointracking path/to/cointracking_export.csv

# Guardar las transacciones importadas en formato JSON
python -m qntropy import-cointracking path/to/cointracking_export.csv -o transactions.json

# Ver ayuda y opciones disponibles
python -m qntropy import-cointracking --help
```

### Mostrar versión

```bash
python -m qntropy version
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
pytest

# Ejecutar tests con cobertura
pytest --cov=qntropy

# Ejecutar solo tests unitarios o de integración
pytest tests/unit/
pytest tests/integration/
```

### Linting y Formateo

```bash
# Ejecutar linters
ruff check .
mypy .

# Formatear código
black .
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
