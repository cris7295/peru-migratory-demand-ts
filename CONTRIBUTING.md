# Cómo trabajamos en este repositorio

Guía simple para nosotros dos, nada complicado:

1. **Nunca se sube código directo a `main`.** Para cualquier cambio, se crea una rama nueva:
   ```
   git checkout -b nombre-corto-del-cambio
   ```
2. Se hacen los cambios, se comitea, y se sube esa rama:
   ```
   git add .
   git commit -m "Explicación corta de qué se hizo"
   git push origin nombre-corto-del-cambio
   ```
3. En GitHub, se abre un **Pull Request** desde esa rama hacia `main`. Ahí el otro revisa y aprueba
   (o comenta si algo hay que ajustar).
4. Una vez aprobado, se mezcla ("merge") a `main`.

## Sobre los datos
No se sube ningún CSV pesado al repositorio. Cada quien descarga sus propias copias desde los
enlaces en `docs/fuentes_datos.md` y las guarda en `data/raw/` (esa carpeta no se sube, ver `.gitignore`).

## Sobre el PRD
El PRD (`docs/PRD.md`) es la referencia fija del proyecto una vez que se termine de redactar.
No se cambia por decisión de una sola persona — cualquier ajuste se conversa entre los dos primero.
