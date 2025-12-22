# Imágenes para Planes de Viaje

Esta carpeta contiene las imágenes que se envían junto con los planes de viaje personalizados.

## Estructura recomendada

- `plan_default.png` - Imagen por defecto si no hay específica para la ciudad
- `plan_canelones.png` - Imagen específica para Canelones
- `plan_[ciudad].png` - Imágenes específicas por ciudad (futuro)

## Especificaciones

- **Formato**: PNG, JPG o WEBP
- **Tamaño máximo**: 5MB (límite de WhatsApp)
- **Dimensiones recomendadas**: 800x1200px o similar (vertical funciona mejor en WhatsApp)
- **Aspecto**: Imágenes atractivas relacionadas con viajes, turismo, o la ciudad específica

## Uso

Las imágenes se envían automáticamente cuando se presenta un plan al usuario.
Si no existe una imagen específica para la ciudad, se usa `plan_default.png`.

## Nota

Si no hay imágenes en esta carpeta, el sistema enviará solo el texto del plan sin interrumpir el flujo.

