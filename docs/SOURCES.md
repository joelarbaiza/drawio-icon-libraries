# Origen de los iconos

Los iconos y las marcas pertenecen a sus respectivos propietarios (Microsoft y otros).
Este repositorio publica librerías técnicas para Draw.io y los scripts que las generan;
**no** transfiere derechos de uso. Consulta los términos de cada fuente antes de usarlos.

Los paquetes de origen se identificaron a partir de las rutas de los notebooks originales
(eliminados en la etapa 3; recuperables desde el tag `v0-legacy`).

| Librería(s) | Paquete de origen | Carpeta en `svg/` | Página oficial (por verificar) |
|---|---|---|---|
| Azure (20 librerías) | `Azure_Public_Service_Icons_V22`, carpeta `Icons/<categoría>` | `svg/Azure/<librería>/source` (SVG de 18×18) | https://learn.microsoft.com/azure/architecture/icons/ |
| Dynamics 365, Dynamics 365 Mixed Reality, Dynamics 365 sub app icons | `Dynamics_365_Icons_scalable_2024` | `svg/Dynamics 365/<librería>/source` | https://learn.microsoft.com/dynamics365/get-started/icons |
| Microsoft Fabric | Paquete de iconos de Fabric, carpeta `icons/package/dist/svg`; se conservan solo las variantes de 48 px (sin `filled`/`regular`) | `svg/Fabric/source` (SVG de 48×48) | https://learn.microsoft.com/fabric/fundamentals/icons |
| Microsoft Entra ID | `Microsoft Entra architecture icons - Oct 2023`, carpeta `Microsoft Entra color icons SVG` | `svg/Microsoft Entra ID/source` | https://learn.microsoft.com/entra/architecture/architecture-icons |
| Power Platform | `Power_Platform_scalable` | `svg/Power Platform/source` | https://learn.microsoft.com/power-platform/guidance/icons |
| Office 365 | Recopilación manual (sin paquete documentado) | `svg/Office 365/source` | — |
| Operating Systems | Recopilación manual (sin paquete documentado) | `svg/Operating Systems/source` | — |
| Developing | Recopilación manual (sin paquete documentado) | `svg/Developing/source` | — |
| Programming | Recopilación manual (sin paquete documentado) | `svg/Programming/source` | — |

## Pendiente

- [ ] Verificar cada URL y anotar versión y fecha de descarga.
- [ ] Documentar el origen y la licencia de cada icono de las recopilaciones manuales
      (Office 365, Operating Systems, Developing, Programming).
- [ ] 27 iconos embeben imágenes raster en lugar de vectores (25 de Office 365, Windows y Micronaut);
      ver la etapa 4 de `TODO.md`.
