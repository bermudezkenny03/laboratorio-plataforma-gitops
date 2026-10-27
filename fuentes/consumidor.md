# Identificación del consumidor

## Perfil

- Rol: Desarrolladora backend junior.
- Experiencia: 6 meses en la organización.
- Herramientas: Git, Visual Studio Code, terminal, Postman.

## Necesidad

Crear un microservicio nuevo con repositorio, catálogo, documentación,
manifiestos Kubernetes y despliegue automatizado mediante GitOps.

## Problema actual

- Debe solicitar despliegues manualmente.
- No sabe qué manifiestos crear ni dónde guardarlos.
- No conoce el estado real del servicio en el clúster.
- No encuentra quién es el responsable ni cómo solicitar soporte.

## Resultado esperado

Crear un servicio, registrarlo en Backstage y desplegarlo en Kubernetes
mediante Argo CD sin ejecutar `kubectl apply` manualmente.

## Validación

- ¿La necesidad es concreta? **Sí.** Se trata de un único flujo: crear y desplegar un
  microservicio con repositorio, catálogo, documentación y manifiestos.
- ¿El problema es medible? **Sí.** Se puede medir con el número de solicitudes manuales
  de despliegue, el tiempo desde "tengo el código" hasta "el pod está Running" y la
  cantidad de pasos que la desarrolladora ejecuta con `kubectl`.
- ¿El resultado esperado es verificable? **Sí.** Argo CD expone el estado de la aplicación
  (`Synced` / `Healthy`) y Kubernetes el estado de los pods (`Running`).
- ¿Qué evidencia demostraría que el problema se resolvió?
  1. El componente `gestion-acueductos-api` aparece en el catálogo de Backstage con
     owner `equipo-datos-agua` y sistema `plataforma-gestion-agua`.
  2. `argocd app get gestion-acueductos-api` muestra **Sync Status: Synced** y
     **Health Status: Healthy**.
  3. `kubectl get pods -n gestion-acueductos-api` muestra los pods en estado **Running**.
  4. Un cambio en Git (por ejemplo `replicas: 2`) llega al clúster sin que nadie ejecute
     `kubectl apply`, y un cambio manual en el clúster es revertido por Argo CD (`selfHeal`).

**Criterio clave:** Argo CD muestra el servicio sincronizado y healthy sin que la
desarrolladora aplique manifiestos manualmente.
