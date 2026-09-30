# Reto universal: Screen Sharing sin app

## 1. ¿Qué es técnicamente posible?
Es posible implementar la funcionalidad de **Screen Sharing** utilizando la API de **WebRTC** (específicamente el método `navigator.mediaDevices.getDisplayMedia`). 

- **En Desktop (Chrome, Firefox, Edge)**: Funciona plenamente. El navegador solicita permiso al usuario para compartir una pestaña específica, una ventana o la pantalla completa.
- **En Android (Chrome)**: Es posible compartir la pantalla completa del dispositivo mediante el navegador, aunque el usuario debe otorgar un permiso explícito a nivel de sistema operativo que advierte que "la aplicación Chrome grabará todo lo que ocurra en la pantalla".
- **En iOS (Safari)**: Es posible compartir la pantalla, pero con restricciones severas. Safari permite el uso de `getDisplayMedia`, pero generalmente se limita a la pestaña actual o requiere que el usuario esté en un flujo muy específico de interacción.

## 2. ¿Qué NO es posible y por qué?
**No es posible visualizar la navegación por "otras aplicaciones" en iPhone (iOS) a través de un enlace web.**

**Razón**: El **Sandboxing** de Apple. Por razones de seguridad y privacidad, iOS prohíbe estrictamente que una aplicación (incluyendo el navegador Safari) acceda al flujo de video de la pantalla del sistema mientras el usuario interactúa con otras apps, a menos que se utilice la API de `ReplayKit`, la cual **requiere obligatoriamente una aplicación nativa instalada** y aprobada en la App Store. No existe una API web que rompa el aislamiento del navegador en iOS para espiar otras aplicaciones.

## 3. Diferencias entre plataformas

| Plataforma | Posibilidad (vía Web) | Limitación Principal |
| :--- | :--- | :--- |
| **Desktop** | ✅ Total | Ninguna significativa; soporte amplio en navegadores modernos. |
| **Android** | ⚠️ Parcial | Requiere permiso de sistema "Cast/Screen Recording"; puede variar según versión de OS. |
| **iOS** | ❌ Muy Limitada | Sandbox estricto; no puede ver otras apps fuera de Safari vía web. |

## 4. Solución Técnica Alternativa Recomendada

Dado que el objetivo es guiar al cliente sin que instale una app, propongo dos caminos según el nivel de control necesario:

### Opción A: Co-Browsing (Navegación Compartida)
En lugar de intentar "ver la pantalla" del cliente, implementaría una sesión de **Co-browsing**. 
- **Cómo funciona**: Se utiliza un script (ej. using *FullStory* o *Cobrowse.io*) que replica el DOM de la página web en la que el cliente se encuentra.
- **Ventaja**: Funciona en iOS/Android/Desktop sin apps.
- **Limitación**: Solo puedes ver las páginas que están bajo tu mismo dominio o donde tengas el script instalado. No puedes ver el "WhatsApp" del cliente, pero sí el formulario de tu seguro.

### Opción B: Flujo Híbrido de Soporte
1. **Enlace Web**: El cliente abre el link.
2. **Detección de OS**: Si el sistema es iOS, el sitio le informa: *"Para guiarte en tiempo real, necesitamos usar una herramienta de videollamada"*.
3. **Deep Linking**: El enlace redirige al cliente a una sesión de **Google Meet** o **Zoom** (que ya vienen preinstaladas en la mayoría de móviles). Estas apps sí tienen los permisos nativos para compartir pantalla en iOS.

**Fuentes consultadas:**
- MDN Web Docs: `getDisplayMedia()` API.
- Apple Developer Documentation: `ReplayKit` framework.
- WebRTC.org: Real-time Communication specifications.
