# API de Gestión de Acueductos

## Propósito

La API permite consultar y registrar información sobre cobertura, consumo
y estado operativo de acueductos veredales.

## Ownership

- Equipo responsable: equipo-datos-agua
- Responsable técnico: Líder del equipo de datos de agua
- Canal de soporte: #soporte-datos-agua
- Correo: datos-agua@ejemplo.com

## Despliegue GitOps

- Repositorio de aplicación: gestion-acueductos-api (carpeta `repo-aplicacion/`)
- Repositorio GitOps: repo-gitops (carpeta `repo-gitops/` de https://github.com/bermudezkenny03/laboratorio-plataforma-gitops)
- Ruta que observa Argo CD: `repo-gitops/apps/gestion-acueductos-api`
- Herramienta de despliegue: Argo CD
- Namespace: gestion-acueductos-api
- Estrategia: sincronización automática desde Git (`automated` con `prune` y `selfHeal`)

## Procedimiento de despliegue

1. Modificar el manifiesto en el repositorio GitOps.
2. Crear un commit descriptivo.
3. Publicar los cambios en la rama main.
4. Argo CD detecta el cambio y sincroniza el clúster.
5. Verificar que la aplicación esté Synced y Healthy.
6. Verificar los pods con `kubectl get pods -n gestion-acueductos-api`.

No se ejecuta `kubectl apply` sobre los manifiestos del servicio: si alguien cambia el
clúster a mano, Argo CD revierte el cambio al estado declarado en Git (`selfHeal`).

## Soporte

- Incidente crítico: abrir ticket en #soporte-datos-agua.
- Consulta funcional: contactar al equipo-datos-agua.
- Consulta técnica: revisar este documento y el repositorio GitOps.

## Preguntas frecuentes

### ¿Quién es el responsable del servicio?

El equipo propietario es `equipo-datos-agua`.

### ¿Cómo se despliega el servicio?

Se modifica el manifiesto en el repositorio GitOps y Argo CD sincroniza el cambio.

### ¿Cómo se verifica el despliegue?

Se revisa que la aplicación esté Synced y Healthy, y que los pods estén Running.
