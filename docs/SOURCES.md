# Origen de los iconos

Los iconos y las marcas pertenecen a sus respectivos propietarios (Microsoft y otros).
Este repositorio publica librerías técnicas para Draw.io y los scripts que las generan;
**no** transfiere derechos de uso. Consulta los términos de cada fuente antes de usarlos.

Los paquetes de origen se identificaron a partir de las rutas de los notebooks originales
(eliminados en la etapa 3; recuperables desde el tag `v0-legacy`).

| Librería(s) | Paquete de origen | Carpeta en `svg/` | Página oficial (verificada 05-10-2026) |
|---|---|---|---|
| Azure (20 librerías) | `Azure_Public_Service_Icons_V22`, carpeta `Icons/<categoría>` | `svg/Azure/<librería>/source` (SVG de 18×18) | https://learn.microsoft.com/azure/architecture/icons/ |
| Dynamics 365, Dynamics 365 Mixed Reality, Dynamics 365 sub app icons | `Dynamics_365_Icons_scalable_2024` | `svg/Dynamics 365/Dynamics 365 App Icons\|Mixed Reality Icons\|Sub App Icons/source` | https://learn.microsoft.com/dynamics365/get-started/icons |
| Microsoft Fabric | Paquete de iconos de Fabric, carpeta `icons/package/dist/svg`; se conservan solo las variantes de 48 px (sin `filled`/`regular`) | `svg/Fabric/source` (SVG de 48×48) | https://learn.microsoft.com/fabric/fundamentals/icons |
| Microsoft Entra ID | `Microsoft Entra architecture icons - Oct 2023`, carpeta `Microsoft Entra color icons SVG` | `svg/Microsoft Entra ID/source` | https://learn.microsoft.com/entra/architecture/architecture-icons |
| Power Platform | `Power_Platform_scalable` | `svg/Power Platform/source` | https://learn.microsoft.com/power-platform/guidance/icons |
| Office 365 | Recopilación manual (sin paquete documentado) | `svg/Office 365/source` | — |
| Operating Systems | Recopilación manual (sin paquete documentado) | `svg/Operating Systems/source` | — |
| Developing | Recopilación manual (sin paquete documentado) | `svg/Developing/source` | — |
| Programming | Recopilación manual (sin paquete documentado) | `svg/Programming/source` | — |

## Iconos sustituidos por versiones vectoriales (etapa 4, 05-10-2026)

Estos 27 iconos embebían imágenes PNG dentro del SVG. Se reemplazaron por versiones
100 % vectoriales del **mismo diseño**, comprobado visualmente contra el original.

| Icono(s) | Origen de la versión vectorial | Licencia / términos |
|---|---|---|
| Office 365: Access, Clipchamp, Defender, Excel, Family Safety, Forms, OneDrive, OneNote, Outlook, Planner, Power Apps, Power Automate, Power BI, PowerPoint, Project, Publisher, SharePoint, Stream, Sway, Teams, To Do, Visio, Word | [DamoBird365/microsoft-cloud-icons](https://github.com/DamoBird365/microsoft-cloud-icons) (commit `771f282`, 2026-04-01) | ⚠️ El repositorio **no declara licencia ni la procedencia** de cada icono. El arte es © Microsoft, igual que el de los iconos raster que sustituye. Elegido por el mantenedor por ser el único origen vectorial encontrado con el diseño actual (2025). Power Apps, Power Automate y Power BI pasan además del diseño anterior al de 2025. |
| Office 365: Exchange | [Wikimedia Commons: Microsoft Exchange (2019-present).svg](https://commons.wikimedia.org/wiki/File:Microsoft_Exchange_(2019-present).svg), atribuido a Microsoft | Dominio público según Commons (geometría simple); sigue siendo marca registrada de Microsoft. |
| Office 365: Editor | El mismo SVG que ya estaba en el repo, **sin sus capas PNG** (eran sombras suaves: cambia < 0,3 % de los píxeles al renderizar) | Igual que el original. |
| Operating Systems: Windows | [Wikimedia Commons: Windows 11 start button icon.svg](https://commons.wikimedia.org/wiki/File:Windows_11_start_button_icon.svg), atribuido a Microsoft | Dominio público según Commons (geometría simple); marca registrada de Microsoft. |
| Programming: Micronaut | Logo oficial «Stacked Black»: https://micronaut.io/micronaut-assets/logos/micronaut-stacked-black.svg ([página de logos](https://micronaut.io/brand-guidelines/micronaut-logos/)) | Marca de Object Computing. Uso comunitario permitido sin consentimiento previo según la [Micronaut Trademark Policy](https://micronaut.io/brand-guidelines/), siempre que no sea en nombre ni en medios de un usuario comercial. |

Fuentes evaluadas y **descartadas**:

- Fluent UI «Office brand icons» (CDN `res-1.cdn.office.net/.../brand-icons/product/svg`): oficiales, pero el
  *Microsoft Fabric Assets License* solo permite usarlos «para desarrollar para Office y otros endpoints de
  Office 365» (Add-ins, SharePoint…), no redistribuirlos en una librería. Además es el diseño de 2019.
- Microsoft 365 architecture icons (`2024-microsoft-365-content-icons.zip`): licencia adecuada para diagramas,
  pero solo contiene iconos de contenido, no logotipos de producto.

## Pendiente

- [x] Verificar cada URL de la tabla principal (las 5 responden, 05-10-2026).
- [ ] Anotar versión y fecha de descarga de cada paquete.
- [ ] Documentar el origen y la licencia del resto de iconos de las recopilaciones manuales
      (Office 365, Operating Systems, Developing, Programming).
- [ ] Si aparece una fuente oficial con licencia clara para los iconos de producto de Microsoft 365,
      sustituir los 23 tomados de DamoBird365.
