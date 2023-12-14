# Instrucciones
- Instalar [Python](https://www.python.org/downloads/) si no lo tienes instalado
- Crear un entorno virtual o virtualenv en el directorio del proyecto con  `python -m venv env`
- Activar el entorno virtual con `env\Scripts\activate`
- Instalar las dependencias con `pip install -r requirements.txt`
- Ejecutar el programa con `python main.py`

### Si se está ejecutando este programa de manera definitiva:
- Si se está ejecutando este programa de manera definitiva en una Raspberry Pi, se debe descomentar la línea `pwm = pi_init()` en el archivo `main.py` y comentar la línea `pwm = 0`
- Además, la Raspberry debe tener el daemon `pigpiod` ejecutándose en segundo plano. Para ello, ejecutar `sudo systemctl enable pigpiod` en la terminal de la Raspberry.