# INFERENCIA DE ORDENES EN LENGUAJE NATURAL A COMANDOS DE ROBOT INDUSTRIAL

**Universidad Nacional de Colombia**
**Facultad de Ingeniería - Departamento de mecánica y mecatrónica**

- **Yovany Esneider Vargas Gutiérrez** *(Ingeniero Mecatrónico)*
- **Pedro Fabián Cárdenas Herrera** *(Profesor, Universidad Nacional de Colombia)*  

---

## Resumen del proyecto

<div style = 'text-align: justify;'>
Con el auge de la inteligencia artificial y los <b>LLM</b> varias industrias han implementado efectivamente esta tecnología en sus procesos de monitoreo y producción, mejorando en términos de eficiencia y productividad, no siendo la robótica ajena a este fenómeno, se propone la integración de un LLM para la interpretación de órdenes habladas en lenguaje natural a instrucciones de comando en robot industrial con el fin de reducir considerablemente los tiempos de programación de rutinas de control robótico, partiendo de una respuesta a un prompt inicial, se realiza un mapeo de esta información a comandos compatibles con el controlador del robot en cuestión. En el desarrollo se utiliza Python para la integración de la API de <b>Groq</b> donde se ejecuta <b>Whisper large v3</b> para el paso de voz a texto plano, y el LLM <b>Llama 3.3 70b versátil</b>, adicionalmente el modulo encargado del mapeo a comandos de robot, basado en la respuesta del LLM. Partiendo de la contextualización del LLM al rol y tareas a realizar, seguidamente la simulación con smart components en <b>Robot Studio 2024</b> y  en posterior validación de resultados en el LabSir con el robot industrial ABB <b>IRB 140 6 0.81</b>. Con la implementación del sistema, el robot responde correctamente a las órdenes expuestas, limitándose unicamente en los casos en los que el propio controlador del robot determina que el punto a alcanzar es de alto riesgo para el efector final o presenta problemas de singularidad. Estos resultados demuestran la capacidad de esta tecnología en la mejora de la eficiencia y la productividad en la planificación de rutinas de control robótico a nivel industrial.
</div>
---

## Objetivo del Proyecto

- Desarrollar un sistema capaz de inferir ordenes en lenguaje natural a instrucciones de comando de robot industrial
- Seleccionar un LLM que cuente con API de ejecución local
- Seleccionar un modelo de voz a texto que soporte el idioma español
- Crear los módulos que permitan la ejecución y conexión via socket del sistema con el controlador IRC5
- Ejecutar los comandos resultantes en el robot industrial IRB 140 6 0.81

## Resultados

[![Ver Video](https://img.youtube.com/vi/Xe3ISFExZHU/0.jpg)](https://www.youtube.com/watch?v=Xe3ISFExZHU)