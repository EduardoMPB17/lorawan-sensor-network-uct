Diseño,implementaciónyevaluacióndelrendimientodeunared
LoRaWANparalasensorizacióndelCampusDr.LuisRivasdelCanto
por
EduardoRemigioMariqueoPorma
TrabajodeTítulopresentadoala
FacultaddeIngenieríadelaUniversidadCatólicadeTemuco
ParaOptaralTítulodeIngenieroCivilInformático.
–Temuco,Septiembre2026–

COMISIÓNEXAMENDETÍTULO
Este Examen de Título ha sido realizado en la Escuela de Ingeniería
Informática:
PresidenteComisión: ..................................
Pordesignar
EscueladeIngenieríaInformática
ProfesorGuía: ..................................
Prof.MarioVillanueva
ProfesorGuía
EscueladeIngenieríaInformática
ProfesorInformante: ..................................
Pordesignar
EscueladeIngenieríaInformática
JefedeCarrerade ..................................
IngenieríaCivil
Informática:
Prof.MarioVillanueva
MagísterenGestiónde
TecnologíasdelaInformación
IngenieroInformático
JefedeCarreraIng.Civil
Informática
Temuco,4deseptiembrede2026.

INFORMETRABAJODETÍTULO
TÍTULO : “Diseño,implementaciónyevaluacióndel
rendimientodeunaredLoRaWANparala
sensorizacióndelCampusDr.LuisRivasdel
Canto”
ALUMNO : EduardoMariqueo
En mi calidad de Profesor Guía, mis apreciaciones del presente informe
deTrabajodeTítulosonlassiguientes:
Apreciación1.
Apreciación2.
Apreciación3.
DeacuerdoconestasconsideracionescalificoeldesarrollodeesteTrabajo
deTítuloconnotaX,X(notaenletras).
Prof.MarioVillanueva
ProfesorGuía
Temuco,4deseptiembrede2026.

INFORMETRABAJODETÍTULO
TÍTULO : “Diseño,implementaciónyevaluacióndel
rendimientodeunaredLoRaWANparala
sensorizacióndelCampusDr.LuisRivasdel
Canto”
ALUMNO : EduardoMariqueo
En mi calidad de Profesor Informante, mis apreciaciones del presente
informedeTrabajodeTítulosonlassiguientes:
Apreciación1.
Apreciación2.
Apreciación3.
DeacuerdoconestasconsideracionescalificoeldesarrollodeesteTrabajo
deTítuloconnotaX,X(notaenletras).
Pordesignar
ProfesorInformante
Temuco,4deseptiembrede2026.

AGRADECIMIENTOS
Agradezco a mi profesor guía y Jefe de Carrera, Prof. Mario Villanueva,
por su orientación, disposición y respaldo durante el desarrollo de este
Trabajo de Título. Agradezco también a la Universidad Católica de
Temuco y a la Escuela de Ingeniería Informática por facilitar el acceso
a la infraestructura y el equipamiento necesarios para el desarrollo del
prototipo. Finalmente, agradezco a mi familia por su apoyo constante a
lolargodeesteproceso.
Notadelautor:Sedeclaraquedurantelaredaccióndeestetrabajoseutilizaron
herramientasdeinteligenciaartificialexclusivamentecomoapoyoauxiliarpara
tareas de redacción y revisión lingüística, sin intervenir en el planteamiento
conceptual,lametodologíanilosresultadosdelestudio.

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
Índice general
Resumen V
Abstract VI
1 Introducción 1
1.1. Contextogeneral . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1
1.2. Problema . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1
1.3. Alcanceydelimitaciones . . . . . . . . . . . . . . . . . . . . . . . 2
1.4. Estadodelarte . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
1.4.1. Síntesisdetrabajosrelacionados . . . . . . . . . . . . . . 4
1.5. Objetivos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
1.5.1. Objetivogeneral . . . . . . . . . . . . . . . . . . . . . . . . 4
1.5.2. Objetivosespecíficos . . . . . . . . . . . . . . . . . . . . . 5
1.5.3. CriteriosSMART . . . . . . . . . . . . . . . . . . . . . . . 6
1.6. ContribucióndelaEtapa1 . . . . . . . . . . . . . . . . . . . . . . 6
2 AntecedentesyDefinicióndelProblema 7
2.1. Contextodelproyecto . . . . . . . . . . . . . . . . . . . . . . . . . 7
2.2. Inventariotecnológico . . . . . . . . . . . . . . . . . . . . . . . . . 7
2.2.1. Arquitecturadecomunicaciones:LoRaWAN . . . . . . . 8
2.3. Partesinteresadas . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
2.3.1. Validacióndestakeholders . . . . . . . . . . . . . . . . . . 10
2.4. Análisispreliminardelescenariodedespliegue . . . . . . . . . . 11
3 ObjetivosyTrazabilidad 12
3.1. Matrizdetrazabilidad . . . . . . . . . . . . . . . . . . . . . . . . . 12
4 EspecificacióndeRequerimientos 14
4.1. Requerimientosfuncionales . . . . . . . . . . . . . . . . . . . . . . 14
4.2. Requerimientosnofuncionalesyrestricciones . . . . . . . . . . . 15
4.3. Criteriosdeevaluación . . . . . . . . . . . . . . . . . . . . . . . . 16
4.3.1. Pérdidadepaquetes . . . . . . . . . . . . . . . . . . . . . 17
4.3.2. Tiempodeconfirmacióndeluplink(Retardo) . . . . . . . 17
4.3.3. Disponibilidad . . . . . . . . . . . . . . . . . . . . . . . . . 17
I

4.4. Fundamentoteóricodepropagación . . . . . . . . . . . . . . . . . 18
4.5. Evaluacióncríticadealternativas . . . . . . . . . . . . . . . . . . . 19
5 PlanificacióndelProyecto 21
5.1. Metodología . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
5.2. Épicasdelbacklog . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
5.3. Resumendelbacklog . . . . . . . . . . . . . . . . . . . . . . . . . 22
5.4. Cronogramadelproyecto . . . . . . . . . . . . . . . . . . . . . . . 22
6 ConclusionesdelaEtapa1 24
A DetalledelBacklogporÉpica 25
A.1. Épica1:Topologíadeldespliegue . . . . . . . . . . . . . . . . . . 25
A.2. Épica2:Marcoregulatorio. . . . . . . . . . . . . . . . . . . . . . . 26
A.3. Épica3:Arquitecturadelprototipo. . . . . . . . . . . . . . . . . . 27
A.4. Épica4:Desplieguefísico . . . . . . . . . . . . . . . . . . . . . . . 28
A.5. Épica5:Pruebasderendimiento . . . . . . . . . . . . . . . . . . . 29
Referencias 31

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
Índice de cuadros
1.1. Síntesisdelestadodelarte . . . . . . . . . . . . . . . . . . . . . . . . . 4
1.2. ObjetivosespecíficosycriteriosSMART . . . . . . . . . . . . . . . . . 6
2.1. Partesinteresadasynecesidadespreliminares . . . . . . . . . . . . . 10
2.2. Plandevalidaciónysoportedestakeholders . . . . . . . . . . . . . . 11
3.1. Matriz de trazabilidad entre problema, stakeholders, objetivos y
requerimientos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
4.1. Requerimientosfuncionalesdelprototipo . . . . . . . . . . . . . . . . 14
4.2. Requerimientosnofuncionales,restriccionesycriteriosdeverificación 16
4.3. Comparacióncríticadealternativasparaelcasodeestudio . . . . . . 20
5.1. Resumendepriorizaciónyesfuerzodelbacklog . . . . . . . . . . . . 22
5.2. Cronogramadetrabajoporépicasyetapas(DiagramadeGantt) . . 23
A.1. Backlog–Épica1:Topologíadeldespliegue . . . . . . . . . . . . . . 25
A.2. Backlog–Épica2:Marcoregulatorio . . . . . . . . . . . . . . . . . . . 26
A.3. Backlog–Épica3:Arquitecturadelprototipo . . . . . . . . . . . . . . 27
A.4. Backlog–Épica4:Desplieguefísico . . . . . . . . . . . . . . . . . . . 28
A.5. Backlog–Épica5:Pruebasderendimiento . . . . . . . . . . . . . . . 29
III

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
Índice de figuras
2.1. DiagramadearquitecturadelprototipodeconectividadLoRaWAN
intra-campus . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
IV

Resumen
EstedocumentopresentalaEtapa1delTrabajodeTítulo,orientada
a definir el problema, establecer objetivos SMART, especificar
requerimientos y planificar el desarrollo de un prototipo de red
LoRaWAN para la sensorización del Campus Dr. Luis Rivas del
Canto de la Universidad Católica de Temuco (UCT). El proyecto
consideraunGatewayLoRaWANcentral,ubicadoenlaFacultadde
Ingeniería,yalmenosdosnodossensoresdistribuidosendistintos
puntos del campus, cuyos datos serán recibidos, publicados hacia
Internet y visualizados en un dashboard de visualización simple.
La problemática se concentra en la necesidad de disponer de una
alternativa de conectividad adecuada para telemetría de baja tasa,
con bajo consumo energético e infraestructura propia, que permita
monitorear variables de interés dentro del campus considerando
la presencia de obstáculos estructurales (edificios, muros) sin
depender de la cobertura Wi-Fi existente. La Etapa 1 establece
el problema, los stakeholders, los objetivos, los requerimientos
funcionalesynofuncionales,elfundamentoteóricodepropagación
bajopérdidasportrayectoriayelbacklogdetrabajo.Lavalidación
empírica del rendimiento queda planificada para las etapas
posteriores.
Palabras clave: LoRaWAN, IoT, sensórica, dashboard, LPWAN,
PPDIOO.

Abstract
This document presents Stage 1 of the Degree Project, focused on
defining the problem, establishing SMART objectives, specifying
requirements, and planning the development of a LoRaWAN
network prototype for sensorizing the Dr. Luis Rivas del
Canto Campus of the Universidad Católica de Temuco (UCT).
The project considers a central LoRaWAN Gateway, located
at the Faculty of Engineering, and at least two sensor nodes
distributed across different points of the campus, whose data
will be received, published to the Internet, and visualized on a
simple visualization dashboard. The problem concerns the need
for a suitable low-rate telemetry connectivity alternative with
low energy consumption and university-owned infrastructure,
allowing the monitoring of variables of interest within the
campuswhileaccountingforstructuralobstacles(buildings,walls),
without depending on the existing Wi-Fi coverage. Stage 1
establishes the problem, stakeholders, objectives, functional and
non-functional requirements, path loss propagation foundations,
and the project backlog. Empirical performance validation is
plannedforsubsequentstages.
Keywords:LoRaWAN,IoT,sensing,dashboard,LPWAN,PPDIOO.

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
1
Introducción
1.1. Contexto general
El proyecto aborda la necesidad de contar con una red de conectividad de
bajo consumo para sensores IoT dentro del Campus Dr. Luis Rivas del Canto
(Facultad de Ingeniería) de la Universidad Católica de Temuco. A diferencia
de una red Wi-Fi tradicional, una solución basada en LoRaWAN permitiría
transportar datos de sensores distribuidos en distintos puntos del campus con
menor consumo energético y sin depender necesariamente de la cobertura
inalámbricainstitucionalexistente.
La propuesta contempla la implementación de un prototipo de conectividad
basado en tecnología LoRaWAN, con un Gateway LoRaWAN central y al
menos dos nodos sensores desplegados dentro del campus, cuyos datos se
publicarán hacia Internet y se visualizarán en un dashboard de visualización
simple. El propósito de esta etapa no es presentar como demostrada la
superioridad de LoRaWAN frente a otras tecnologías, sino establecer una base
técnica y metodológica que permita evaluar posteriormente su desempeño en
el escenario de estudio, considerando la presencia de obstáculos estructurales
propiosdelcampus(edificios,muros).
1.2. Problema
La necesidad de este proyecto se relaciona con la disponibilidad de una
alternativa de conectividad de bajo consumo y de bajo costo operativo para
el transporte de datos de sensores IoT dentro del campus. Actualmente no se
cuenta con una infraestructura propia, de bajo consumo energético, orientada
específicamente a este tipo de telemetría, lo que limita el desarrollo de futuras
aplicacionesdesensóricadentrodelaFacultaddeIngeniería.
Una solución de conectividad para nodos de telemetría debe considerar
restricciones de consumo energético, alcance dentro del campus, operación
1

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
radioeléctrica, la presencia de obstáculos estructurales (edificios, muros) y
facilidad de integración con los sistemas de visualización existentes. Por ello,
el proyecto considera necesario estudiar una alternativa que pueda operar con
infraestructura propia y que sea adecuada para el transporte de datos de baja
tasa.
Elproblemaseformulaoperacionalmentedelasiguientemanera:
| La UCT      | requiere      | evaluar | una           | alternativa |         | de conectividad |                 | propia       | para      |
| ----------- | ------------- | ------- | ------------- | ----------- | ------- | --------------- | --------------- | ------------ | --------- |
| transportar | datos         | de      | sensores      | IoT dentro  | del     | Campus          | Dr.             | Luis         | Rivas del |
| Canto,      | considerando  |         | restricciones | de          | consumo | energético,     |                 | la presencia | de        |
| obstáculos  | estructurales |         | y la          | dependencia |         | de la           | infraestructura |              | de red    |
existente,ypermitiendolavisualizacióndedichosdatosenundashboard.
Apartirdeestaformulaciónseplantealasiguientepreguntadeinvestigación:
¿EnquémedidaunprototipoderedLoRaWANimplementadodentrodel
| Campus      | Dr. Luis | Rivas     | del Canto    | permite |         | transportar  | y   | visualizar | datos     |
| ----------- | -------- | --------- | ------------ | ------- | ------- | ------------ | --- | ---------- | --------- |
| de sensores | IoT      | de manera | técnicamente |         | viable, | considerando |     | la         | presencia |
deobstáculosestructuralesdentrodelcampus?
| 1.3. Alcance |     | y   | delimitaciones |     |     |     |     |     |     |
| ------------ | --- | --- | -------------- | --- | --- | --- | --- | --- | --- |
Elalcancedeestaetapacomprendeladefinicióndelproblema,laidentificación
de stakeholders, el establecimiento de objetivos, la especificación inicial de
requisitos,larevisióndelfundamentotécnicoylaplanificacióndelproyecto.
La evaluación final se plantea mediante pruebas controladas sobre la red
desplegada dentro del campus. No se considera, dentro del alcance declarado,
una operación continua de la infraestructura durante periodos prolongados ni
unaoptimizaciónmatemáticadelared.
LaarquitecturadecomunicacionesdelprototiposeráLoRaWANestándar.Esta
decisión se fundamenta en que el Gateway LoRaWAN opera nativamente bajo
el protocolo LoRaWAN; una arquitectura LoRa punto a punto (P2P) habría
requerido modificaciones adicionales de firmware o hardware sobre dicho
equipo, incrementando la complejidad de la solución en lugar de reducirla. El
detalledeestaarquitecturasepresentaenlaSección2.2.1.
2

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
1.4. Estado del arte
El estado del arte sustenta la selección tecnológica y los requerimientos de
rendimiento mediante estudios previos sobre LoRa/LoRaWAN, telemetría
IoT, propagación y medición de enlaces. Dado que el escenario del proyecto
involucra la propagación de señal dentro de un campus universitario –con
edificiosyotrasestructurasqueactúancomoobstáculosrelevantes–sepriorizan
trabajos que caractericen empíricamente la pérdida de trayectoria en entornos
urbanos y construidos bajo condiciones de obstrucción parcial (Ahmed et al.,
2024; Bianco et al., 2021; Callebaut & Van der Perre, 2020; Rademacher et al.,
2021).
En particular, Rademacher et al. (2021) reportan una campaña de medición
a gran escala (más de 112.000 muestras) en un área urbana de 200 km2,
comparando once modelos de pérdida de trayectoria y concluyendo que
el modelo log-distancia y modelos empíricos clásicos (Okumura, Winner+)
ofrecen estimaciones razonables frente a modelos basados en terreno. Por su
parte,CallebautyVanderPerre(2020)caracterizanenlacesLoRapuntoapunto
entresentornos–urbano,forestalycostero–,mostrandoquelabajaalturadelas
antenas incrementa la pérdida de trayectoria respecto a una topología estrella.
El trabajo de Bianco et al. (2021) aporta un antecedente adicional sobre la
propagacióndeLoRaencondicionesdeobstrucciónsevera.Finalmente,Ahmed
etal.(2024)cuantificanelefectodeobstáculosnaturalessobreeldesempeñode
nodosLoRa,observandocaídasenlatasadeentregadepaquetes(PDR)yenla
relaciónseñal-ruidoamedidaqueaumentaladistanciaylaobstrucción.
Estos antecedentes permiten establecer que las condiciones del canal
intra-campus no deben modelarse únicamente mediante espacio libre cuando
existen obstáculos estructurales, y que la evaluación empírica planificada para
lasetapasposterioresdeesteTrabajodeTítuloescoherenteconlametodología
utilizadaenlaliteraturareciente.
Aunque los estudios revisados caracterizan la propagación y pérdida de
trayectoria de LoRa en entornos urbanos, forestales y bajo condiciones
de obstrucción, estos antecedentes no caracterizan específicamente una
implementación LoRaWAN orientada a sensorización intra-campus en el
CampusDr.LuisRivasdelCanto.Enconsecuencia,elpresentetrabajopropone
evaluarexperimentalmenteelcomportamientodeunaredLoRaWANendicho
escenario.
3

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
| 1.4.1. Síntesis | de trabajos |     | relacionados |     |     |     |     |     |
| --------------- | ----------- | --- | ------------ | --- | --- | --- | --- | --- |
En el Cuadro 1.1 se resumen las principales investigaciones que sustentan el
abordajetécnicodelpresenteproyecto.
Cuadro1.1:Síntesisdelestadodelarte
| Referencia      | Problema   |     | Enfoque    |     |     | Aportealproyecto |     |        |
| --------------- | ---------- | --- | ---------- | --- | --- | ---------------- | --- | ------ |
| Rademacheretal. | Predicción |     | de Campaña |     | de  | Sustenta         | el  | uso de |
(2021) cobertura en redes medición a gran modeloslog-distancia
|     | LoRa         | urbanas | escala            | (230 | días,     | como             | línea base   | para |
| --- | ------------ | ------- | ----------------- | ---- | --------- | ---------------- | ------------ | ---- |
|     | mediante     | modelos | >112.000          |      | muestras) | estimar          | la cobertura |      |
|     | de pérdida   |         | de y comparación  |      | de 11     | dentrodelcampus. |              |      |
|     | trayectoria. |         | modelosempíricos. |      |           |                  |              |      |
Callebaut & Van Caracterización de Campañas de Aporta evidencia de
derPerre(2020) enlaces LoRa punto medición en urbano, que la baja altura de
|     | a punto   | en distintos | forestal     | y    | costero;  | antena             | incrementa    |           |
| --- | --------- | ------------ | ------------ | ---- | --------- | ------------------ | ------------- | --------- |
|     | entornos. |              | modelamiento |      | de        | la                 | pérdida       | de        |
|     |           |              | path         | loss | con datos | trayectoria,       |               | relevante |
|     |           |              | censurados.  |      |           | paranodossensoresa |               |           |
|     |           |              |              |      |           | baja               | altura dentro | del       |
campus.
Bianco et al. Comunicación LoRa Mediciones de Antecedente sobre el
| (2021) | en condiciones     |     | de path        | loss | bajo     | comportamiento        |             |         |
| ------ | ------------------ | --- | -------------- | ---- | -------- | --------------------- | ----------- | ------- |
|        | obstrucciónsevera. |     | condiciones    |      | adversas | de                    | LoRa        | ante    |
|        |                    |     | depropagación. |      |          | obstáculos,aplicablea |             |         |
|        |                    |     |                |      |          | la                    | obstrucción | parcial |
|        |                    |     |                |      |          | por                   | edificios   | dentro  |
delcampus.
Ahmed et al. Efecto de obstáculos Mediciones de PDR Justifica considerar
(2024) naturales sobre la y SNR en función efectos adicionales al
|     | comunicaciónLoRa. |     | de la           | distancia | y    | la modelo  | de       | espacio |
| --- | ----------------- | --- | --------------- | --------- | ---- | ---------- | -------- | ------- |
|     |                   |     | obstrucción,    |           | para | libre      | cuando   | existen |
|     |                   |     | distintos       | factores  | de   | obstáculos | entre    | los     |
|     |                   |     | dispersión(SF). |           |      | nodos      | sensores | y el    |
GatewayLoRaWAN.
1.5. Objetivos
| 1.5.1. Objetivo | general |     |     |     |     |     |     |     |
| --------------- | ------- | --- | --- | --- | --- | --- | --- | --- |
Diseñar, implementar y evaluar el rendimiento de un prototipo de red
LoRaWAN para la sensorización del Campus Dr. Luis Rivas del Canto de la
UCT, determinando su viabilidad técnica mediante pruebas controladas de
funcionamientoyrendimiento.
4

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
1.5.2. Objetivos específicos
1. O1. Desplegar la infraestructura física del prototipo, compuesta por un
Gateway LoRaWAN ubicado en la Facultad de Ingeniería y al menos
dos nodos sensores Heltec LoRa 32 en distintos puntos del Campus Dr.
Luis Rivas del Canto, verificando su instalación y funcionamiento básico
durantelaEtapa2(Septiembre–Octubre2026).
2. O2.IntegrarelGatewayLoRaWANconelentornoderedIPdefinidopara
el prototipo, verificando que las tramas correctamente recibidas puedan
ser publicadas hacia Internet y entregadas al destino de prueba durante
laEtapa2(Septiembre–Octubre2026).
3. O3. Implementar un dashboard de visualización simple –dadas las
restricciones de tiempo del proyecto– que consuma los datos publicados
haciaInternet(p.ej.víaMQTT)ymuestre,comomínimo,elidentificador
del nodo sensor, la marca temporal y el valor medido, sin incorporar
analíticaavanzada,durantelaEtapa2(Septiembre–Octubre2026).
4. O4. Evaluar el rendimiento de la red desplegada dentro del campus
mediante 3 sesiones de tráfico controlado de 100 tramas por nodo,
midiendopérdidadepaquetes,retardoydisponibilidad,durantelaEtapa
3(Octubre2026)ylaEtapa4(Noviembre–Diciembre2026).
5

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
| 1.5.3. Criterios | SMART |     |     |     |     |
| ---------------- | ----- | --- | --- | --- | --- |
Cuadro1.2:ObjetivosespecíficosycriteriosSMART
| ID Objetivo | S:específico | M:medible | A:alcanzable | R:relevante | T:  |
| ----------- | ------------ | --------- | ------------ | ----------- | --- |
temporizado
O1 Desplegarla 1Gateway Instalaciónde1 Los Construyeel Septiembre–Octubre
infraestructura LoRaWANyal Gateway antecedentes escenario 2026(Etapa2).
| físicadel  | menos2nodos  | LoRaWANyal   | delproyecto   | requerido   |     |
| ---------- | ------------ | ------------ | ------------- | ----------- | --- |
| prototipo. | sensoresenel | menos2nodos, | identificanel | parala      |     |
|            | campus.      | conprueba    | hardware      | evaluación. |     |
|            |              | funcional    | disponible    |             |     |
|            |              | básica.      | provistopor   |             |     |
lafacultad.
O2
Integrarel Recibiry Verificarla Selimitaal Permite Septiembre–Octubre
Gatewayconel publicarala publicaciónde alcancede utilizarlos 2026(Etapa2).
| entornoIPde | redIPlas       | lastramasque | integración  | datosfuera |     |
| ----------- | -------------- | ------------ | ------------ | ---------- | --- |
| prueba.     | tramas         | lleganal     | definidopara | delenlace  |     |
|             | recibidas      | Gateway      | elprototipo. | radio.     |     |
|             | correctamente. | LoRaWAN.     |              |            |     |
O3 Implementar MostrarIDde Verificarquelas Sedisponede Facilitala Septiembre–Octubre
undashboard nodo,marca tramas unservidoro observación 2026(Etapa2).
| de            | temporaly    | consumidas    | dashboard   | directadelos |     |
| ------------- | ------------ | ------------- | ----------- | ------------ | --- |
| visualización | valormedido, | queden        | local       | datosdelos   |     |
| simple.       | sinanalítica | identificadas | considerado | sensores.    |     |
|               | avanzada.    | pororigenen   | enel        |              |     |
|               |              | pantalla.     | proyecto.   |              |     |
O4 Evaluarel Ejecutar Mediciónen3 Seplantea Permite Octubre2026
rendimientode sesiones sesionesde100 comoprueba determinarla (Etapa3)y
lareddentro controladasde tramaspor experimental viabilidad Noviembre–Diciembre
delcampus. tráficoen nodo(Packet puntualy técnicadel 2026(Etapa4).
|     | distintos | Loss,retardoy    | controlada. | prototipo. |     |
| --- | --------- | ---------------- | ----------- | ---------- | --- |
|     | puntosde  | disponibilidad). |             |            |     |
cobertura.
| 1.6. Contribución |     | de la | Etapa 1 |     |     |
| ----------------- | --- | ----- | ------- | --- | --- |
Esta etapa establece una definición operacional del problema, una primera
identificación de stakeholders, objetivos SMART trazables, requisitos
funcionales y no funcionales, una justificación preliminar de la alternativa
tecnológica y un backlog estructurado mediante PPDIOO. La evidencia
empíricaderendimientosereservaparalasetapasposteriores.
6

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
2
Antecedentes y Definición del
Problema
2.1. Contexto del proyecto
La red propuesta se despliega dentro del Campus Dr. Luis Rivas del
Canto (Facultad de Ingeniería). El Gateway LoRaWAN central se ubicará
en la Facultad de Ingeniería, concentrando la recepción de las tramas de
radiofrecuencia y su publicación hacia Internet/red IP institucional, mientras
quealmenosdosnodossensoressedistribuyenendistintospuntosdelcampus
–por ejemplo, distintos edificios o sectores– para transmitir datos de sensores
IoT hacia el Gateway LoRaWAN, considerando la presencia de obstáculos
estructurales(edificios,muros)entrecadanodoyelGatewayLoRaWAN.
Laseleccióndelasubicacionesdefinitivasdelosnodossensores,laconfirmación
y asignación formal del modelo de Gateway LoRaWAN institucional y las
variables físicas a monitorear se consolidarán formalmente durante la fase de
desplieguedelaEtapa2,enfuncióndelosimplementosprovistosporlaEscuela
deIngenieríaInformática.
2.2. Inventario tecnológico
Los antecedentes disponibles contemplan un Gateway LoRaWAN (modelo
institucional actualmente en proceso de evaluación y provisión técnica) y
módulos Heltec LoRa 32 como nodos sensores (al menos dos). También se
considera el desarrollo del firmware mediante C/C++ y Arduino IDE, además
deunservidorodashboardlocalparavisualización.
Advertencia de operación del hardware: los módulos Heltec deben utilizar
su antena física correspondiente antes de ser energizados o utilizados en las
pruebas,deacuerdoconlasinstruccionesdeoperaciónproporcionadasparael
proyecto.
7

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
| 2.2.1. Arquitectura |     | de  | comunicaciones: |     | LoRaWAN |     |     |
| ------------------- | --- | --- | --------------- | --- | ------- | --- | --- |
El prototipo adopta LoRaWAN como protocolo de comunicaciones, en lugar
de una implementación LoRa punto a punto (P2P), siguiendo la especificación
oficialdelprotocolo(LoRaAlliance,2020).Estadecisiónrespondedirectamente
alascapacidadesdelhardwareautilizar:elGatewayLoRaWANes,pordiseño,
un dispositivo concentrador LoRaWAN cuya etapa de recepción demodula
y procesa tramas que siguen la estructura estándar MAC definida en dicha
especificación(encabezadoMAC,DevAddr,MIC,FPort),descartandopaquetes
crudosfueradenorma.
En la Figura 2.1 se detalla la arquitectura de integración extremo a extremo
propuestaparaelprototipo.
Nodo
Heltec1
RFLoRa
SensoresIoT
| (AU915             | Gateway     |            | Network    |           |                  |             |                        |
| ------------------ | ----------- | ---------- | ---------- | --------- | ---------------- | ----------- | ---------------------- |
|                    | LoR a W AN  |            |            |           | Broker           |             | D a s h b o a r d      |
| OTAA)              |             | BackhaulIP | Server     | JSON/MQTT | MQTT             | Suscripción |                        |
|                    | ( E n       |            | (Embebidoo |           |                  |             | V is u a li z ac i ó n |
|                    | evaluación/ |            |            |           | (Infraestructura |             | (Node-RED              |
| Nodo               | provisto    |            | ChirpStack |           | IP               |             |                        |
|                    |             |            | Local)     |           | Institucional)   |             | /Web)                  |
| Heltec2            | porTI)      |            |            |           |                  |             |                        |
| SensoresIoT RFLoRa |             |            |            |           |                  |             |                        |
(AU915
OTAA)
Figura 2.1: Diagrama de arquitectura del prototipo de conectividad LoRaWAN
intra-campus
Enconsecuencia,loscomponentesdelsistemaquedandefinidosdelasiguiente
forma:
NodossensoresHeltecLoRa32(almenosdos):seconfiguraránmediante
unalibreríaLoRaWANestándarparaArduino(RadioLiboMCCILMIC),
autenticándosemedianteOver-The-AirActivation(OTAA)(LoRaAlliance,
2020). Cada nodo transmitirá periódicamente tramas de telemetría bajo
el plan regional AU915 (915–928 MHz), banda habilitada en Chile por la
SUBTEL(SubsecretaríadeTelecomunicacionesdeChile(SUBTEL),2017).
Gateway LoRaWAN: se ubicará en la Facultad de Ingeniería. Operará
enlazado hacia un Network Server (ya sea integrado en el propio equipo
o desplegado como servicio local ChirpStack sobre la red provista),
publicando las tramas procesadas hacia la red IP mediante el protocolo
MQTT.
Dashboard de visualización simple: interfaz mínima que se suscribe
al broker MQTT y presenta en pantalla el identificador del nodo
8

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
sensor, la marca temporal (timestamp) y el valor medido, satisfaciendo el
requerimientoRF4.
Respecto a la evaluación experimental (RQS1–RQS2): para la medición
rigurosa de la tasa de pérdida de paquetes (PL) se emplearán tramas no
confirmadas o transmisiones con reintentos desactivados (NbTrans = 1),
asegurando caracterizar directamente la atenuación física del canal sin que las
retransmisionesdelapilaenmascarenlospaquetesperdidos.Paralaestimación
deltiempodeconfirmación(T ),serealizaránsesionescontroladasespecíficas
conf
mediante tramas confirmadas (confirmed uplinks), registrando el intervalo hasta
la recepción del ACK en las ventanas temporizadas RX1/RX2 (LoRa Alliance,
2020).
2.3. Partes interesadas
La identificación de stakeholders distingue claramente entre la justificación de
lanecesidadinstitucionalylaviabilidadoperativadeldespliegue.Lanecesidad
delproyectoestálideradaporlaFacultaddeIngenieríaatravésdelaDirección
de la Carrera de Ingeniería Civil Informática, encabezada por el Prof. Mario
Villanueva en calidad de patrocinador académico y propietario del proyecto,
quienvalidalapertinenciayapruebalosrequerimientos.
Por su parte, el Área de Redes/TI y la Dirección de Informática intervienen
principalmente en calidad de prestadores y facilitadores de equipamiento e
infraestructura técnica (servidores, segmento IP institucional y provisión del
GatewayLoRaWAN),simplificandolaarticulaciónoperativadeldespliegue.
9

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
Cuadro2.1:Partesinteresadasynecesidadespreliminares
| Stakeholder     |     | Necesidadpreliminar |              |                    |           | Implicancia       |     |             |     |
| --------------- | --- | ------------------- | ------------ | ------------------ | --------- | ----------------- | --- | ----------- | --- |
| ÁreadeRedes/TI/ |     | Proveer             |              | la infraestructura |           | Facilitador       |     |             | de  |
| Informática     |     | de                  | conectividad |                    |           | IP, equipamiento  |     |             | e   |
|                 |     | direccionamiento    |              |                    |           | y integración     |     | del Gateway |     |
|                 |     | equipamiento        |              |                    | de prueba | enlareddelcampus. |     |             |     |
|                 |     | (Gateway            |              | y                  | hosting   |                   |     |             |     |
básico).
| Facultad       | de  | Disponer    |     | de una          | red     | de Justifica         | la  | selección |     |
| -------------- | --- | ----------- | --- | --------------- | ------- | -------------------- | --- | --------- | --- |
| Ingeniería     |     | / sensórica |     | IoT             | propia, | de tecnología        |     | LPWAN     |     |
| Investigadores |     | abierta     |     | y de            | bajo    | costo de bajo        |     | consumo   | y   |
|                |     | para        |     | experimentación |         | administraciónlocal. |     |           |     |
académica.
| Dirección        | de     | Fomentar      |           | la     | innovación | Valida        |                | formalmente |     |
| ---------------- | ------ | ------------- | --------- | ------ | ---------- | ------------- | -------------- | ----------- | --- |
| Carrera          |        | / en          | IoT       | dentro |            | de la         | relevancia     |             | del |
| Propietario      | del    | la            | facultad, |        | validar    | problema      |                | y aprueba   |     |
| proyecto         | (Prof. | empíricamente |           |        |            | la los        | requerimientos |             |     |
| MarioVillanueva) |        | viabilidad    |           | de     | LoRaWAN    | prioritarios. |                |             |     |
|                  |        | intra-campus  |           | y      | disponer   |               |                |             |     |
|                  |        | de            | una       |        | plataforma |               |                |             |     |
replicable.
| Estudiantes       |     | y Contar                 |              | con  |         | una Exige         | rigor          |          | en  |
| ----------------- | --- | ------------------------ | ------------ | ---- | ------- | ----------------- | -------------- | -------- | --- |
| futurostesistas   |     | arquitectura             |              |      |         | la                | especificación |          |     |
|                   |     | documentada,             |              |      | modular | y técnica,        |                | manuales |     |
|                   |     | reproducible             |              | para | futuros | de                | configuración  |          | y   |
|                   |     | desarrollosdetelemetría. |              |      |         | reproducibilidad. |                |          |     |
| 2.3.1. Validación |     | de                       | stakeholders |      |         |                   |                |          |     |
Lapertinenciaynecesidaddelproyectohansidovalidadasdirectamenteconel
propietariodelproyecto,elProf.MarioVillanueva(JefedeCarreradeIngeniería
Civil Informática). Respecto a los implementos y accesos de red, su provisión
se coordina de manera directa como soporte técnico de infraestructura para el
iniciodelaEtapa2.
10

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
Cuadro2.2:Plandevalidaciónysoportedestakeholders
| Actor |     | Qué se | debe | validar | / Evidencia |     |
| ----- | --- | ------ | ---- | ------- | ----------- | --- |
coordinar
| Dirección | de     | Relevancia    |     | institucional | Validación | formal de |
| --------- | ------ | ------------- | --- | ------------- | ---------- | --------- |
| Carrera   | (Prof. | del problema, |     | pertinencia   | necesidad  | realizada |
Mario Villanueva, de la sensorización en el (Agosto 2026); respaldo
| Propietario) |     | campus | y              | aprobación | institucionaldelproyecto. |     |
| ------------ | --- | ------ | -------------- | ---------- | ------------------------- | --- |
|              |     | de     | requerimientos |            |                           |     |
funcionales.
Área de Redes Entrega y asignación del Coordinación de entrega
| / Informática |     | Gateway  |     | institucional, | de                | equipamiento |
| ------------- | --- | -------- | --- | -------------- | ----------------- | ------------ |
| (Soporte)     |     | segmento | de  | red            | IP y programada   | para el      |
|               |     | soporte  | de  | conectividad   | iniciodelaEtapa2. |              |
paraelbrokerMQTT.
| 2.4. Análisis |     | preliminar |     | del | escenario | de  |
| ------------- | --- | ---------- | --- | --- | --------- | --- |
despliegue
El escenario de despliegue corresponde al Campus Dr. Luis Rivas del Canto,
recinto que concentra los edificios de la Facultad de Ingeniería. A nivel
preliminar, se propone ubicar el Gateway LoRaWAN en un punto central de la
Facultadquefavorezcalacoberturahaciaelrestodelcampus,mientrasquelos
nodossensoressedistribuiránendistintoslugaresdeinterésdentrodelcampus,
seleccionados de manera que representen escenarios de propagación diversos
–tantodelíneadevistadirecta(LOS)comoconalgúngradodeobstrucciónpor
edificiosomuros(NLOSparcial)–,sincomprometeraúnubicacionesexactasni
distanciasespecíficas.
Estaprimeraaproximaciónbuscaúnicamentedelimitareltipodeescenarioque
enfrentará el prototipo –un entorno intra-campus con obstáculos estructurales
típicos de un recinto universitario– y no reemplaza la caracterización espacial
detallada que corresponde realizar en la Etapa 2, una vez que se cuente con
acceso a los planos oficiales del campus, se releven las distancias reales entre
los puntos candidatos y se confirmen las ubicaciones definitivas del Gateway
LoRaWANydecadanodosensorjuntoconelpersonaldesoporteylaDirección
deCarrera.
11

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
3
Objetivos y Trazabilidad
3.1. Matriz de trazabilidad
La matriz vincula los objetivos y requerimientos con el problema, las
necesidades identificadas y la evidencia que permitirá verificar su
cumplimiento.
12

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
Cuadro 3.1: Matriz de trazabilidad entre problema, stakeholders, objetivos y
requerimientos
Req. Obj. Stakeholder Necesidad/problema Justificaciónyverificación
RF1 O1,O4 Direcciónde Transmitirdatosdesdelos Sintransmisiónradiono
|     | Carrera(Prof.    | nodossensores. | existeunprototipo      |
| --- | ---------------- | -------------- | ---------------------- |
|     | MarioVillanueva) |                | evaluable.Severificará |
mediantepruebasdeenvío
yrecepción.
| RF2 O1,O2 | SoporteTI/  | Concentraryprocesarla   | ElGatewayLoRaWAN         |
| --------- | ----------- | ----------------------- | ------------------------ |
|           | Informática | informaciónrecibidaenel | constituyeelpuntocentral |
|           |             | Gateway.                | derecepción.Severificará |
medianteregistrosylogs
detramas.
RF3 O2,O3 SoporteTI/ Entregardatosalentorno Permiteverificarla
|     | Informática | IPdeprueba. | integraciónconlared |
| --- | ----------- | ----------- | ------------------- |
institucionalybroker.Se
contrastarántramasradio
versuspublicaciones
MQTT.
RF4 O3,O4 Direcciónde Distinguirelorigende Laidentificacióndel
|     | Carrera(Prof.    | cadasensorenel | origenpermiteatribuir   |
| --- | ---------------- | -------------- | ----------------------- |
|     | MarioVillanueva) | dashboard.     | correctamentecadadatoal |
sensorcorrespondiente.
| RF5 O4    | Direcciónde      | Obtenerevidencia        | Lassesionescontroladas |
| --------- | ---------------- | ----------------------- | ---------------------- |
|           | Carrera(Prof.    | empíricadelrendimiento. | permitencalcularlas    |
|           | MarioVillanueva) |                         | métricasdefinidas.     |
| RT1 O1–O4 | Marco            | Operaciónenbanday       | Garantizacumplimiento  |
|           | Regulatorio      | potencialegalmente      | normativomediante      |
|           | (SUBTEL)         | permitidaenChile.       | configuracióndelplan   |
AU915.
RT2–RT3O1–O4 Equipode Restriccionesdeintegridad Usoobligatoriodeantenas
|     | Desarrollo/ | dehardwareyentornode | antesdeenergizary      |
| --- | ----------- | -------------------- | ---------------------- |
|     | Tesista     | programación.        | desarrolloenC/C++sobre |
ArduinoIDE.
| RQS1 O4 | Equipode    | Necesidaddecuantificar | Secalcularálatasade |
| ------- | ----------- | ---------------------- | ------------------- |
|         | Desarrollo/ | confiabilidaddelcanal  | pérdidadepaquetesa  |
|         | Tesista     | radio.                 | partirdeenvíossin   |
retransmisión
(NbTrans=1).
| RQS2 O4 | Equipode    | Necesidaddecuantificar | Semedirámediante      |
| ------- | ----------- | ---------------------- | --------------------- |
|         | Desarrollo/ | retardodeconfirmación. | sesionesdeconfirmed   |
|         | Tesista     |                        | uplinks,registrandoel |
tiempohastalarecepción
delACK.
| RQS3 O4 | Equipode    | Necesidaddecaracterizar  | Seregistraráel     |
| ------- | ----------- | ------------------------ | ------------------ |
|         | Desarrollo/ | ladisponibilidaddelared. | cumplimientodela   |
|         | Tesista     |                          | ventanaderecepción |
temporalcontinuadurante
laspruebas.
13

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
4
| Especificación      | de Requerimientos |     |     |
| ------------------- | ----------------- | --- | --- |
| 4.1. Requerimientos | funcionales       |     |     |
Cuadro4.1:Requerimientosfuncionalesdelprototipo
| ID Requerimiento             | Justificación  | Obj.  | Verificación |
| ---------------------------- | -------------- | ----- | ------------ |
| RF1 Losnodossensores(almenos | Eslafunción    | O1,O4 | Pruebade     |
| dos)debencapturardatosde     | básicaque      |       | transmisióny |
| pruebaytransmitirtramas      | permiteevaluar |       | registrode   |
| medianteelprotocolo          | lared.         |       | recepción.   |
LoRaWANAU915.
| RF2 ElGatewayLoRaWANdebe  | Constituyeel   | O1,O2 | Logsy          |
| ------------------------- | -------------- | ----- | -------------- |
| recibiryprocesarlastramas | puntocentralde |       | trazabilidadde |
| provenientesdelosnodos    | latopología.   |       | mensajes.      |
sensoressegúnlaarquitectura
quesedefinaparael
prototipo.
RF3 Elsistemadebepublicarhacia Permiteintegrar O2,O3 Comparación
| Internet/entornoIPdeprueba | lainformaciónde |     | entrerecepcióny |
| -------------------------- | --------------- | --- | --------------- |
| lastramascorrectamente     | radioconel      |     | publicación.    |
| recibidasporelGateway      | entornoIP.      |     |                 |
LoRaWAN.
| RF4 Eldashboarddevisualización | Esnecesario     | O3,O4 | Dashboardo    |
| ------------------------------ | --------------- | ----- | ------------- |
| simpledebeidentificarel        | distinguirel    |       | registro      |
| nodosensordeorigeny            | origendecada    |       | estructurado. |
| mostrar,comomínimo,            | datoparasu      |       |               |
| identificador,marcatemporal    | correcta        |       |               |
| yvalormedido,sin               | interpretación. |       |               |
incorporaranalíticaavanzada.
| RF5 Elsistemadebepermitir | Laevaluacióndel | O4  | Archivode     |
| ------------------------- | --------------- | --- | ------------- |
| ejecutarsesionesdetráfico | prototipo       |     | resultadospor |
| controladoyregistrarlos   | requiere        |     | sesión.       |
| resultadosdecadasesión.   | evidencia       |     |               |
reproducible.
14

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
4.2. Requerimientos no funcionales y
restricciones
EnelCuadro4.2sedetallanlosrequerimientosnofuncionales,lasrestricciones
normativasyloscriteriosdeverificacióntécnicaquecondicionaneldiseñoyla
operacióndelprototipoderedLoRaWAN.
15

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
Cuadro 4.2: Requerimientos no funcionales, restricciones y criterios de
verificación
| ID Categoría | Requisito | Justificación | Verificación |
| ------------ | --------- | ------------- | ------------ |
RT1 Tecnología Elhardwarederadiofrecuenciadebe Delimitala Configuración
| /         | operarbajoelplanregionalAU915  | operación         | documentada |
| --------- | ------------------------------ | ----------------- | ----------- |
| normativa | (915–928MHz),bandaypotencia    | radioeléctricadel | yrespaldo   |
|           | permitidaporlanormativachilena | prototipoala      | normativo.  |
|           | aplicableaequiposdealcance     | bandaautorizada   |             |
|           | reducido(Subsecretaríade       | enChile.          |             |
TelecomunicacionesdeChile
(SUBTEL),2017).
RT2 Hardware LosmódulosHeltecdebenutilizar Esunacondición Checklist
|     | suantenafísicacorrespondiente | deoperación | previoa       |
| --- | ----------------------------- | ----------- | ------------- |
|     | durantelaspruebas.            | seguradel   | energización. |
hardware
utilizado.
RT3 Desarrollo Elfirmwaredelosnodosdebe Mantienela Repositorioy
|     | desarrollarseenC/C++mediante | solucióndentro | proyectode |
| --- | ---------------------------- | -------------- | ---------- |
|     | ArduinoIDE.                  | delentorno     | firmware.  |
tecnológico
disponible.
RQS1 Calidadde Elsistemadebepermitircalcularla Laconfiabilidad Cálculoa
| servicio | tasadePacketLossen            | físicadelenlace   | partirde    |
| -------- | ----------------------------- | ----------------- | ----------- |
|          | radiofrecuencia,operandosin   | requiereaislarlas | tramas      |
|          | retransmisionesautomáticas    | pérdidasdel       | enviadasy   |
|          | (NbTrans=1)durantelassesiones | mediodela         | recibidasen |
|          | deevaluaciónfísicadelcanal.   | lógicade          | logs.       |
reintentos.
RQS2 Calidadde Elsistemadebepermitirmedirel Elretardode Registro
| servicio | tiempodeconfirmaciónde         | enlaceLoRaWAN  | diferencialde |
| -------- | ------------------------------ | -------------- | ------------- |
|          | transmisiónmediantesesiones    | integrael      | marcas        |
|          | controladasdeconfirmeduplinks, | Time-on-Airyla | temporalesde  |
|          | computandoelretardohastala     | ventanade      | envíoy        |
|          | recepcióndelACK.               | respuesta      | recepción.    |
temporizadaRX.
RQS3 Calidadde Elsistemadebepermitirregistrarla Formaliza Análisisde
| servicio | disponibilidaddelenlacedurantela | matemáticamente | marcasde   |
| -------- | -------------------------------- | --------------- | ---------- |
|          | ventanadeevaluación,definiendo   | lacontinuidad   | tiempoenel |
|          | caídasinoserecibentramasenun     | operativadel    | registrode |
|          | lapsomayoratresperiodos          | prototipo.      | recepción. |
nominales.
| 4.3. Criterios | de evaluación |     |     |
| -------------- | ------------- | --- | --- |
Lasprincipalesmétricasderendimientoconsideradasson:
16

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
| 4.3.1. Pérdida | de  | paquetes |     |                   |     |     |
| -------------- | --- | -------- | --- | ----------------- | --- | --- |
|                |     |          |     | (cid:18) (cid:19) |     |     |
N
|     |     | PL(%) | = 100 | 1− rec |     | (4.1) |
| --- | --- | ----- | ----- | ------ | --- | ----- |
N
env
donde N env es el número de tramas físicas transmitidas por el nodo y N rec
el número de tramas recibidas y demoduladas correctamente por el Gateway.
Para el Objetivo 4, cada sesión de prueba considerará el envío de 100 tramas
pornodo,en3sesionesindependientes.Duranteestasmedicionesdepérdidas,
=
el stack de comunicaciones fijará el parámetro de reintentos en NbTrans 1,
asegurandoquelamétricareflejelatasadeerrorrealinducidaporlosobstáculos
y la distancia, sin que los reintentos automáticos enmascaren el desempeño de
propagación.
| 4.3.2. Tiempo | de  | confirmación |     | del uplink | (Retardo) |     |
| ------------- | --- | ------------ | --- | ---------- | --------- | --- |
El retardo de transmisión se evaluará a través del tiempo de confirmación del
uplink LoRaWAN (T conf ), aprovechando el mecanismo de tramas confirmadas
(confirmeduplinks)ensesionescontroladas:
|     |     |     | T = T | −T      |     | (4.2) |
| --- | --- | --- | ----- | ------- | --- | ----- |
|     |     |     | conf  | ACK env |     |       |
donde T corresponde a la marca temporal en que el nodo sensor Heltec
env
finaliza la transmisión de la trama hacia el Gateway y T representa el
ACK
instante exacto en que el nodo demodula con éxito el acuse de recibo (ACK)
emitido en las ventanas RX1 o RX2. Esta métrica integra el tiempo en el aire
(Time-on-Air), el procesamiento en el Network Server y los retardos fijos de
sincronizacióndeventanapropiosdelestándardecapaMAC.
| 4.3.3. Disponibilidad |     |     |     |     |     |     |
| --------------------- | --- | --- | --- | --- | --- | --- |
La disponibilidad de la conectividad se evaluará cuantitativamente sobre el
tiempoefectivoduranteelcualelcanalsemantienefuncional:
|     |     |     |     | (cid:18) (cid:19) |     |     |
| --- | --- | --- | --- | ----------------- | --- | --- |
∑T
caída
|     |     | A(%) | = 100 | 1−  |     | (4.3) |
| --- | --- | ---- | ----- | --- | --- | ----- |
T
prueba
| donde T | es la | duración | total | de la sesión | y ∑T representa | el  |
| ------- | ----- | -------- | ----- | ------------ | --------------- | --- |
| prueba  |       |          |       |              | caída           |     |
tiempo acumulado en estado de interrupción o pérdida de enlace. Se define
17

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
formalmente un estado de caída si el intervalo transcurrido entre dos tramas
recibidasconsecutivassuperaunaventanalímite:
∆t
|     |     |     | >   | 3·T     |     |     | (4.4) |
| --- | --- | --- | --- | ------- | --- | --- | ----- |
|     |     |     | rec | periodo |     |     |       |
donde T corresponde al tiempo nominal de muestreo programado entre
periodo
transmisionessucesivasdelnodo.
| 4.4. Fundamento |     |     | teórico | de  | propagación |     |     |
| --------------- | --- | --- | ------- | --- | ----------- | --- | --- |
Para evaluar cuantitativamente el canal de radiofrecuencia intra-campus se
partedelbalancedeenlacegeneral:
|     |     | P = | P +G | +G −L | −L  |     | (4.5) |
| --- | --- | --- | ---- | ----- | --- | --- | ----- |
|     |     | r   | t t  | r     | p   | s   |       |
dondeP t eslapotenciadetransmisión,G t yG r correspondenalasgananciasde
lasantenas, L representalapérdidatotaldepropagaciónenlatrayectoriay L
| p   |     |     |     |     |     |     | s   |
| --- | --- | --- | --- | --- | --- | --- | --- |
agrupapérdidasadicionalesdelsistema(cables,conectores).
Comoreferenciateóricadepropagaciónsinobstáculosseutilizalaformulación
depérdidaenespaciolibre(FreeSpacePathLoss,FSPL)(Seybold,2005):
|     | L    | = 20log | (d)+20log |     | (f)+32,44 |     | (4.6) |
| --- | ---- | ------- | --------- | --- | --------- | --- | ----- |
|     | FSPL |         | 10        |     | 10        |     |       |
donde d se expresa en kilómetros y f en MHz. Sin embargo, en el Campus
Dr. Luis Rivas del Canto la propagación de las ondas electromagnéticas
está condicionada por edificios, muros de hormigón armado e interferencias
estructurales. En tales condiciones de obstrucción parcial (NLOS), la pérdida
enespaciolibresubestimadrásticamentelaatenuaciónreal.
Por ello, se adopta como base analítica el modelo log-distancia con
desvanecimiento por sombra (Log-Distance Path Loss Model), respaldado en
la literatura empírica sobre redes LoRa/LoRaWAN (Ahmed et al., 2024;
Rademacheretal.,2021):
|     |     |     |     |     | (cid:18) | (cid:19) |     |
| --- | --- | --- | --- | --- | -------- | -------- | --- |
d
|     | PL(d) | = PL(d | )+10n |     |     | +X  |       |
| --- | ----- | ------ | ----- | --- | --- | --- | ----- |
|     |       |        | 0     | log |     | σ   | (4.7) |
10 d
0
donde:
18

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
d esladistanciadereferenciaencampocercano(típicamente1mo10m).
0
PL(d ) es la pérdida en la distancia de referencia calculada mediante la
0
ecuación (4.6), asegurando la coherencia dimensional al expresar d en
0
kilómetros(porejemplo,d = 1m = 10−3 km).
0
nrepresentaelexponentedepérdidadetrayectoria,parámetroquecuantifica
el grado de obstrucción del medio. Mientras que en espacio libre n = 2,
en recintos urbanos construidos y campus universitarios con obstáculos
estructurales toma valores empíricos típicos entre 2,7 y 4,5 (Rademacher
etal.,2021).
X ∼ N(0,σ2) es una variable aleatoria gaussiana de media cero con
σ
desviación estándar σ (en dB), que modela el desvanecimiento lento por
sombra (shadowing) inducido por muros y estructuras opacas entre el
nodosensoryelGatewayLoRaWAN.
Esta formulación proporciona el sustento teórico formal para contrastar
las mediciones de terreno (Packet Loss, tiempo de confirmación y
disponibilidad) planificadas en los requerimientos RQS1–RQS3 durante
lasetapasexperimentales.
4.5. Evaluación crítica de alternativas
La selección de LoRaWAN se considera preliminar y se fundamenta en la
adecuacióndelescenarioacomunicacionesdebajatasadedatos,bajoconsumo
y posibilidad de utilizar infraestructura propia. La validez final de la selección
dependerádelosresultadosexperimentales.
19

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
Cuadro4.3:Comparacióncríticadealternativasparaelcasodeestudio
| Criterio | Wi-Fi | LTE/5G | Satelital | LoRaWAN |
| -------- | ----- | ------ | --------- | ------- |
Dependenciade Dependedela Dependedeun Dependedeun Puedeoperar
| terceros | infraestructura | operadorydesu | proveedor  | sobre           |
| -------- | --------------- | ------------- | ---------- | --------------- |
|          | Wi-Fi           | cobertura.    | satelital. | infraestructura |
|          | institucional   |               |            | propia,         |
|          | existente.      |               |            | independientede |
laredWi-Fi
institucional.
Consumoennodo Noestáorientado Puedepresentar Puedeincorporar Adecuadapara
|     | principalmentea | mayores        | restricciones | telemetríadebaja |
| --- | --------------- | -------------- | ------------- | ---------------- |
|     | telemetríade    | requerimientos | energéticas   | tasaybajo        |
|     | muybaja         | energéticosque | relevantes.   | consumo.         |
|     | potencia.       | soluciones     |               |                  |
LPWAN.
Adecuacióna Requiereevaluar Presenta Presenta Eslaalternativa
sensóricaIoT coberturay característicasde característicasde seleccionada
intra-campus capacidaddela capacidady capacidady preliminarmente
|     | redinstitucional | costosoperativos | costosoperativos | parala         |
| --- | ---------------- | ---------------- | ---------------- | -------------- |
|     | paramuchos       | quenoseajustan   | queexcedenlos    | conectividadde |
|     | nodosdebajo      | prioritariamente | requerimientos   | sensoresIoT    |
|     | consumo.         | alasnecesidades  | deunescenario    | dentrodel      |
|     |                  | detelemetría     | intra-campus.    | campus.        |
dentrodel
campus.
Costooperativo Dependedela Presentacostos Presentacostos Puedereducir
|     | infraestructura | recurrentespor | recurrentesde | costos        |
| --- | --------------- | -------------- | ------------- | ------------- |
|     | requerida.      | servicio.      | servicio.     | recurrentesal |
utilizar
infraestructura
propia.
20

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
5
Planificación del Proyecto
5.1. Metodología
El proyecto se organiza mediante el ciclo de vida de redes PPDIOO (Prepare,
Plan, Design, Implement, Operate, Optimize), metodología definida formalmente
porCiscoparaeldiseñoeimplementaciónderedes(Teare&Paquet,2006).Para
elalcancedeesteTrabajodeTítuloseutilizanlasfasesnecesariasparapreparar,
diseñar,implementaryoperarelprototipo,mientrasquelaoptimizaciónqueda
fueradelobjetivoprincipaldelestudio.
La priorización de las tareas se expresa mediante una adaptación de MoSCoW,
utilizando las categorías Must y Should. Las horas corresponden a una
estimacióndeesfuerzotécnicorealistaparaunproyectodetitulaciónsemestral.
5.2. Épicas del backlog
El backlog del proyecto se organiza en cinco épicas alineadas con el ciclo
PPDIOO: (1) Topología del despliegue, (2) Marco regulatorio, (3) Arquitectura
del prototipo, (4) Despliegue físico y (5) Pruebas de rendimiento. El desglose
completodecadaépicasepresentaenelAnexoA.
21

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
| 5.3. Resumen del | backlog |     |     |
| ---------------- | ------- | --- | --- |
Cuadro5.1:Resumendepriorizaciónyesfuerzodelbacklog
| Épica                                 | FasePPDIOO   | Objetivos | Esfuerzo |
| ------------------------------------- | ------------ | --------- | -------- |
| Topologíadeldespliegue                | Prepare/Plan | O1,O4     | 20horas  |
| Marcoregulatorio                      | Prepare/Plan | O1        | 10horas  |
| Arquitecturadelprototipo              | Design       | O1,O2,O3  | 36horas  |
| Desplieguefísico                      | Implement    | O1,O2     | 52horas  |
| Pruebasderendimiento                  | Operate      | O4        | 46horas  |
| Totalesfuerzoestimadodetrabajotécnico |              |           | 164horas |
| 5.4. Cronograma                       | del proyecto |           |          |
El cronograma general de trabajo se estructura en dieciséis semanas efectivas
dedesarrollo,distribuidasdemanerahomogéneaencuatroperiodosdecuatro
semanas (sprints) de acuerdo con los hitos oficiales del curso de Trabajo de
Título. En el Cuadro 5.2 se ilustra la planificación temporal de las cinco épicas
delproyectoalolargodelsemestreacadémico.
22

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
Cuadro5.2:Cronogramadetrabajoporépicasyetapas(DiagramadeGantt)
Etapa1(Ago–Sep) Etapa2(Sep–Oct) Etapa3(Oct) Etapa4(Nov–Dic)
Épica/Hito S1 S2 S3 S4 S5 S6 S7 S8 S9 S10 S11 S12 S13 S14 S15 S16
Levantamiento y
requerimientos
Épica 1: Topología del
despliegue
Épica2:Marcoregulatorio
Épica 3: Arquitectura y
dashboard
Épica4:Desplieguefísicoen
campus
Épica 5: Pruebas de
rendimiento
Cierre, análisis y memoria
final
Nota:Lasceldasencolorazulrepresentanlaejecuciónactivadelastareas;laceldasombreadaen
celesteenS8indicalaformulacióndelprotocoloexperimentalprevioalasmediciones.
23

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
6
Conclusiones de la Etapa 1
La Etapa 1 permitió delimitar formalmente la problemática de conectividad
para telemetría IoT en el Campus Dr. Luis Rivas del Canto, sustentando la
necesidaddeunainfraestructurapropiadeconectividadparasensorizaciónIoT,
evaluándose LoRaWAN como alternativa tecnológica frente a las restricciones
decoberturayconsumodelaredWi-Fiinstitucional.Lapertinenciayrelevancia
académicadelapropuestaquedaronvalidadasformalmentejuntoalaDirección
de la Carrera de Ingeniería Civil Informática, liderada por el Prof. Mario
Villanuevaensuroldepatrocinadorypropietariodelproyecto.
Asimismo, se articularon cuatro objetivos SMART con trazabilidad directa
hacia los requerimientos técnicos y de calidad de servicio. En este ámbito,
se sustentó preliminarmente la selección de LoRaWAN para el escenario
analizado, se definió una estrategia robusta para la medición del retardo
y la pérdida de paquetes distinguiendo el comportamiento de propagación
física, se fundamentó el impacto de los obstáculos estructurales a través del
modelo de pérdidas log-distancia y se especificó la arquitectura extremo a
extremo mediante el desacoplamiento entre las tramas de radiofrecuencia y la
publicacióndedatosenformatoJSONsobreMQTThaciaundashboardsimple.
Finalmente, el desarrollo se estructuró bajo la metodología PPDIOO y
priorización MoSCoW, consolidando un cronograma temporal y un backlog
de cinco épicas presentado en el Anexo A. Como trabajo inmediato para la
Etapa 2, se contempla el despliegue físico del Gateway LoRaWAN y los nodos
Heltec LoRa 32 en la Facultad de Ingeniería, la coordinación técnica para la
conectividadIPylaformalizacióndelprotocoloexperimentalparalassesiones
detráficocontrolado.
24

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
A
Detalle del Backlog por Épica
Este anexo presenta el desglose completo de cada épica del backlog resumido
en la Sección 5.3: historia de usuario, tareas técnicas priorizadas mediante
MoSCoW (M = Must, S = Should), etapa de ejecución planificada, horas
estimadasycriteriosdeaceptación/evidencia.
A.1. Épica 1: Topología del despliegue
Prepare/Plan–Topologíadeldespliegue
Épica
O1,O4
Objetivo(s)
Alta
Prioridad
20horas
Esfuerzo
CuadroA.1:Backlog–Épica1:Topologíadeldespliegue
Historia de usuario: Como investigador, quiero definir la ubicación del
GatewayLoRaWANydelosnodossensoresdentrodelcampusparaestablecer
ydocumentarelescenariodedespliegue.
25

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
| Tareatécnica |            |             |     |        |     | Pr. | Etapa | Horas |
| ------------ | ---------- | ----------- | --- | ------ | --- | --- | ----- | ----- |
| Relevar      | y proponer | ubicaciones |     | dentro | del | M   | 2     | 8     |
campus
| Documentar |     | distancias |     | y obstáculos |     | M   | 2   | 6   |
| ---------- | --- | ---------- | --- | ------------ | --- | --- | --- | --- |
aproximadosenplano
| Identificar | puntos | críticos | de  | cobertura | (LOS | S   | 2   | 4   |
| ----------- | ------ | -------- | --- | --------- | ---- | --- | --- | --- |
/NLOS)
| Consolidar | ficha | técnica | del | escenario | de  | M   | 2   | 2   |
| ---------- | ----- | ------- | --- | --------- | --- | --- | --- | --- |
despliegue
Criterios de aceptación/evidencia: escenario de despliegue documentado, con
ubicacionespropuestasyplanodereferenciadelcampus.
| A.2. | Épica | 2: Marco |     | regulatorio |     |     |     |     |
| ---- | ----- | -------- | --- | ----------- | --- | --- | --- | --- |
Prepare/Plan–Marcoregulatorio
Épica
O1
Objetivo(s)
Alta
Prioridad
10horas
Esfuerzo
CuadroA.2:Backlog–Épica2:Marcoregulatorio
Historia de usuario: Como investigador, quiero formalizar las restricciones
regulatorias para asegurar una implementación compatible con la normativa
aplicableenChile.
26

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
| Tareatécnica |                |         |        |       | Pr. | Etapa | Horas |
| ------------ | -------------- | ------- | ------ | ----- | --- | ----- | ----- |
| Revisar      | especificación | técnica | SUBTEL | (Res. | M   | 2     | 4     |
Ex.1.985)
| Verificar | canales | y máscaras | de frecuencia | en  | M   | 2   | 3   |
| --------- | ------- | ---------- | ------------- | --- | --- | --- | --- |
planAU915
| Consolidar | checklist | de potencia | y duty-cycle |     | S   | 2   | 3   |
| ---------- | --------- | ----------- | ------------ | --- | --- | --- | --- |
permitido
Criterios de aceptación/evidencia: matriz de cumplimiento normativo
completadaydocumentada.
| A.3. | Épica | 3: Arquitectura |     | del | prototipo |     |     |
| ---- | ----- | --------------- | --- | --- | --------- | --- | --- |
Design–Arquitecturadelprototipo
Épica
O1,O2,O3
Objetivo(s)
Alta
Prioridad
36horas
Esfuerzo
CuadroA.3:Backlog–Épica3:Arquitecturadelprototipo
Historia de usuario: Como investigador, quiero estructurar la arquitectura
del prototipo para conectar los nodos sensores, el Gateway LoRaWAN y el
dashboarddevisualización.
27

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
| Tareatécnica |                |         |           | Pr. | Etapa | Horas |
| ------------ | -------------- | ------- | --------- | --- | ----- | ----- |
| Especificar  | flujo de datos | extremo | a extremo | M   | 2     | 6     |
LoRa/IP
| Definirinterfazderedydireccionamientodel |     |     |     | M   | 2   | 6   |
| ---------------------------------------- | --- | --- | --- | --- | --- | --- |
Gateway
| Configurar | parámetros | de red | LoRaWAN y | M   | 2   | 8   |
| ---------- | ---------- | ------ | --------- | --- | --- | --- |
credencialesOTAA
| Estructurar | esquema | de tópicos | y payloads | S   | 2   | 6   |
| ----------- | ------- | ---------- | ---------- | --- | --- | --- |
MQTT
| Implementar | interfaz | del dashboard | simple y | M   | 2   | 10  |
| ----------- | -------- | ------------- | -------- | --- | --- | --- |
clienteMQTT
Criterios de aceptación/evidencia: arquitectura validada, tópicos MQTT
operativosydashboardfuncionaldesplegado.
| A.4. | Épica 4: | Despliegue | físico |     |     |     |
| ---- | -------- | ---------- | ------ | --- | --- | --- |
Implement–Desplieguefísico
Épica
O1,O2
Objetivo(s)
Alta
Prioridad
52horas
Esfuerzo
CuadroA.4:Backlog–Épica4:Desplieguefísico
Historia de usuario: Como estudiante ejecutor, quiero desplegar el Gateway
LoRaWAN y los nodos sensores para disponer del prototipo físico operativo
dentrodelcampus.
28

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
| Tareatécnica |        |                |             |     | Pr. | Etapa | Horas |
| ------------ | ------ | -------------- | ----------- | --- | --- | ----- | ----- |
| Instalación  | física | y energización | del Gateway |     | M   | 2     | 12    |
institucional
| Programación | de  | firmware | base en | nodos | M   | 2   | 16  |
| ------------ | --- | -------- | ------- | ----- | --- | --- | --- |
HeltecLoRa32
| Verificación | de  | antenas, | mediciones | de  | M   | 2   | 14  |
| ------------ | --- | -------- | ---------- | --- | --- | --- | --- |
potenciayenlace
| Prueba | funcional | básica | de recepción | y   | S   | 2   | 10  |
| ------ | --------- | ------ | ------------ | --- | --- | --- | --- |
registrodelogs
Criterios de aceptación/evidencia: infraestructura física instalada, primer
enlacefuncionalverificadoychecklistdeseguridaddehardware.
| A.5. | Épica | 5: Pruebas | de  | rendimiento |     |     |     |
| ---- | ----- | ---------- | --- | ----------- | --- | --- | --- |
Operate–Pruebasderendimiento
Épica
O4
Objetivo(s)
Alta
Prioridad
46horas
Esfuerzo
CuadroA.5:Backlog–Épica5:Pruebasderendimiento
Historia de usuario: Como investigador, quiero ejecutar sesiones controladas
detráficoparamedirelrendimientodelaredendistintospuntosdelcampus.
29

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
| Tareatécnica |           |              |           | Pr. | Etapa | Horas |
| ------------ | --------- | ------------ | --------- | --- | ----- | ----- |
| Formalizar   | protocolo | experimental | (sesiones | M   | 2     | 8     |
de100tramas)
| Ejecución | de Sesión | 1 en condiciones | de línea | M   | 3   | 10  |
| --------- | --------- | ---------------- | -------- | --- | --- | --- |
devista(LOS)
| Ejecución | de Sesión | 2 en condiciones | de  | M   | 3   | 10  |
| --------- | --------- | ---------------- | --- | --- | --- | --- |
obstrucción(NLOS)
| EjecucióndeSesión3yregistrosimultáneode |     |     |     | M   | 3/4 | 10  |
| --------------------------------------- | --- | --- | --- | --- | --- | --- |
métricas
| Consolidacióndedataset,cálculodepérdidas |     |     |     | S   | 4   | 8   |
| ---------------------------------------- | --- | --- | --- | --- | --- | --- |
yanálisis
Criterios de aceptación/evidencia: dataset reproducible (3 sesiones de 100
tramas por nodo), protocolo documentado y cálculo de métricas de calidad de
servicio.
30

TrabajodeTítuloINFO-1197
RedLoRaWANUCT
Referencias
Ahmed, S., Reza, M. N., Samsuzzaman, Karim, M. R., Jin, H., Kim, H.,
& Chung, S.-O. (2024). Vegetation Effects on LoRa-Based Wireless
Sensor Communication for Remote Monitoring of Automatic
Orchard Irrigation Status. IoT, 6(1), 2. https://doi.org/10.3390/
iot6010002
Bianco,G.M.,Giuliano,R.,Marrocco,G.,Mazzenga,F.,&Mejia-Aguilar,
A. (2021). LoRa System for Search and Rescue: Path-Loss Models
and Procedures in Mountain Scenarios. IEEE Internet of Things
Journal, 8(3), 1985-1999. https://doi.org/10.1109/JIOT.2020.
3017044
Callebaut, G., & Van der Perre, L. (2020). Characterization of LoRa
Point-to-PointPath-Loss:MeasurementCampaignsandModeling
Considering Censored Data. IEEE Internet of Things Journal, 7(3),
1859-1867.https://doi.org/10.1109/JIOT.2019.2953804
LoRa Alliance. (2020). TS001-1.0.4 LoRaWAN® L2 1.0.4 Specification (inf.
téc.). LoRa Alliance, Inc. https://resources.lora-alliance.org/
technical- specifications/ts001- 1- 0- 4- lorawan- l2- 1- 0- 4-
specification
Rademacher,M.,Linka,H.,Horstmann,T.,&Henze,M.(2021).PathLoss
in Urban LoRa Networks: A Large-Scale Measurement Study.
2021 IEEE 94th Vehicular Technology Conference (VTC2021-Fall).
https://doi.org/10.48550/arXiv.2109.07768
Seybold,J.S.(2005).IntroductiontoRFPropagation.Wiley.
Subsecretaría de Telecomunicaciones de Chile (SUBTEL). (2017).
Resolución Exenta N.º 1.985 de 2017, que Fija Norma Técnica
de Equipos de Alcance Reducido [Modificada por Resoluciones
Exentas N.º 737 y N.º 2.219 (actualizada a 2025). Biblioteca del
CongresoNacional].https://bcn.cl/zHimxM
Teare, D., & Paquet, C. (2006). Authorized Self-Study Guide: Designing for
CiscoInternetworkSolutions(DESGN)(2nd).CiscoPress.
31