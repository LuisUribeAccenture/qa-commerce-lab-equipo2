# Bitácora de uso de IA

Registra al menos 5 situaciones relevantes. Interesan sobre todo las veces en que la IA se equivocó, inventó algo o tomó una decisión que no le correspondía.

| # | Sesión | Herramienta | Qué le pedimos | Qué devolvió | Qué estaba mal o incompleto | Cómo lo detectamos | Qué hicimos |
1	Implementación del generador	ChatGPT	Implementar generar_clientes y generar_productos respetando RN-02, RN-03 y los docstrings.	Un archivo Python con ambas funciones implementadas.	La implementación cumplía las reglas principales, pero no garantizaba una cobertura completa de casos límite de edad.	Revisamos el código y los escenarios cubiertos por las pruebas.	Identificamos la necesidad de agregar pruebas específicas para los límites de edad.
2	Validación de reproducibilidad	ChatGPT	Verificar que los datos fueran reproducibles utilizando únicamente Faker y random.Random(seed).	Una implementación que utiliza semillas fijas y una fecha de referencia constante.	Las pruebas verificaban igualdad con la misma semilla y diferencia entre semillas, pero no todos los posibles usos de aleatoriedad.	Revisamos test_misma_semilla_mismo_resultado y test_distinta_semilla_distinto_resultado.	Complementamos la evaluación con una revisión del uso de random y de las fechas.
3	Validación de correos electrónicos	ChatGPT	Generar correos ficticios, únicos y con dominio example.com.	Correos sintéticos que cumplían las validaciones establecidas.	Aunque eran válidos, seguían un patrón de generación que limitaba su variedad.	Revisamos el formato de los correos y la prueba de unicidad.	Aceptamos el resultado porque cumplía los requisitos, pero registramos la limitación de variedad.
4	Validación de mayoría de edad	ChatGPT	Garantizar que todos los clientes cumplieran RN-03: tener al menos 18 años.	Fechas de nacimiento de clientes mayores de edad.	No se comprobaban explícitamente los escenarios de cumplir 18 años exactamente el día de referencia o al día siguiente.	Analizamos la prueba test_clientes_mayores_de_edad_rn03 y observamos que solo verificaba edades iguales o superiores a 18 años.	Propusimos agregar pruebas de valores límite para comprobar correctamente el cumpleaños.
5	Ejecución de pruebas	ChatGPT	Evaluar las pruebas Python del generador y reportar los resultados.	Un reporte de 8 pruebas exitosas y 1 prueba de integración pendiente.	No fue posible ejecutar la prueba de integración porque faltaba el fixture client.	Identificamos que test_el_dataset_se_carga_en_la_app dependía del entorno de la aplicación.	Registramos la prueba como pendiente, evitando reportarla como exitosa.
6	Verificación de modificaciones	ChatGPT	Confirmar que no se modificaron las pruebas originales.	Indicó que no había modificado intencionalmente test_generador.py.	No pudo demostrar que git diff tests/ estuviera vacío.	Revisamos la limitación del entorno, donde no estaba disponible la información del repositorio Git.	Dejamos pendiente ejecutar git diff tests/ dentro del repositorio original.

## Aprendizajes
Durante la implementación y evaluación del generador de datos sintéticos identificamos los siguientes aprendizajes:

1. Dar instrucciones específicas mejora los resultados. Indicar las reglas RN-02 y RN-03, los docstrings y las restricciones de reproducibilidad permitió que la IA generara código alineado con los requisitos.

2. No debemos confiar únicamente en que las pruebas pasen. Aunque las pruebas unitarias resultaron satisfactorias, identificamos escenarios adicionales que no estaban cubiertos, especialmente los límites de edad.

3. La IA puede tomar decisiones técnicas que necesitan revisión. Por ejemplo, la forma de generar fechas de nacimiento y distribuir los niveles de inventario puede cumplir los requisitos sin cubrir todos los escenarios relevantes para QA.

4. Es importante solicitar evaluaciones imparciales. Pedirle a ChatGPT que identificara errores, limitaciones y aspectos pendientes permitió distinguir entre requisitos cumplidos y verificaciones incompletas.

5. La reproducibilidad es fundamental en las pruebas automatizadas. Utilizar semillas fijas y evitar dependencias del reloj del sistema permite repetir los escenarios y comparar resultados.

6. La validación humana sigue siendo necesaria. La IA ayudó a implementar y analizar el código, pero fue necesario revisar las reglas de negocio, identificar casos límite y reconocer las pruebas que no podían ejecutarse.

<Qué prompts, instrucciones o controles funcionaron mejor.>
