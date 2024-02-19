# Instrucciones
- Instalar [Python](https://www.python.org/downloads/) si no lo tienes instalado
- Crear un entorno virtual o virtualenv en el directorio del proyecto con  `python -m venv env`
- Activar el entorno virtual con `env\Scripts\activate` y asegurarse de que se ha hecho bien viendo el cambio en el prompt de la consola.
- Instalar las dependencias con `pip install -r requirements.txt`
- Ejecutar el programa con `python main.py`. Si se está ejecutando en la Raspberry Pi y se quiere mandar la señal PWM a los servomotores ejecutar: `python main.py -r`. Si no, no se moverán los servomotores.
- La Raspberry debe tener el daemon `pigpiod` ejecutándose en segundo plano para poder manejar las señales de los servomotores. Para ello, ejecutar `sudo systemctl enable pigpiod` en la terminal de la Raspberry.
