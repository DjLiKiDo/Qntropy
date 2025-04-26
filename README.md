# Qntropy

Qntropy es una aplicación en Python diseñada para analizar y procesar archivos CSV exportados desde CoinTracking, proporcionando información valiosa sobre tus transacciones de criptomonedas.

## Descripción

Esta herramienta permite importar datos de transacciones de criptomonedas desde archivos CSV de CoinTracking y realizar diversos análisis, como:

- Deteccion y correccion de operaciones faltantes
- Consolidacion de saldos
- Resumen de transacciones por tipo (depósitos, retiros, trades, comisiones)
- Análisis de rendimiento por activo
- Cálculo de ganancias y pérdidas
- Visualizaciones de la evolución de tu portafolio
- Exportación de datos procesados para informes fiscales

## Estructura del Proyecto

```
Qntropy/
├── data/
│   ├── input/        # Archivos CSV originales de CoinTracking
│   └── output/       # Archivos de resultados procesados
├── docs/             # Documentación
├── src/              # Código fuente
├── tests/            # Tests unitarios y de integración
├── LICENSE           # Información de licencia
└── README.md         # Este archivo
```

## Requisitos

- Python 3.11+
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/yourusername/Qntropy.git
   cd Qntropy
   ```

2. Crea y activa un entorno virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows usa: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Uso

1. Coloca tu archivo CSV exportado de CoinTracking en la carpeta `data/input/`.
2. Ejecuta el script principal:
   ```
   python src/main.py
   ```
3. Los resultados procesados se guardarán en la carpeta `data/output/`.

## Formato de Datos de Entrada

La aplicación está diseñada para trabajar con archivos CSV de CoinTracking que contienen las siguientes columnas:
- Type (tipo de operación: Deposit, Trade, Withdrawal, etc.)
- Buy (cantidad comprada)
- Cur. (moneda comprada)
- Sell (cantidad vendida)
- Cur.1 (moneda vendida)
- Fee (comisión)
- Cur.2 (moneda de la comisión)
- Exchange (plataforma de intercambio)
- Group (grupo de transacción)
- Comment (comentario)
- Date (fecha y hora)
- Tx-ID (identificador de transacción)

## Características

- Procesamiento eficiente de grandes volúmenes de datos
- Detección y manejo de diferentes formatos de fecha
- Cálculo automático de ganancias y pérdidas
- Generación de informes personalizados
- Visualizaciones interactivas del comportamiento de tu portafolio

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