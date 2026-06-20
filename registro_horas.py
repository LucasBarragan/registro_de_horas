import time
import csv
import os
import subprocess
from datetime import datetime

ARCHIVO = "registro_horas.csv"

contador_activo = False
inicio_contador = None


def obtener_fecha():
    ahora = datetime.now()

    dias_semana = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo"
    }

    meses = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre"
    }

    return dias_semana[ahora.weekday()], ahora.day, meses[ahora.month], ahora.year

try:

    subprocess.run(
        ["git", "pull"],
        capture_output=True,
        text=True,
        check=True
    )

    print("Git sincronizado correctamente.")

except Exception:

    print(
        "⚠️ [Aviso] No se pudo sincronizar con GitHub "
        "al iniciar. Corriendo en modo local/sin conexión."
    )

def crear_archivo_si_no_existe():
    if not os.path.exists(ARCHIVO):
        with open(ARCHIVO, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["Día de la semana", "Día", "Mes", "Año", "Tiempo total"])


def guardar_tiempo(tiempo_decimal):
    crear_archivo_si_no_existe()

    dia_semana, dia, mes, anio = obtener_fecha()

    filas = []

    with open(ARCHIVO, "r", newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            filas.append(fila)

    encontrado = False

    for i in range(1, len(filas)):
        if (
            filas[i][1] == str(dia)
            and filas[i][2] == mes
            and filas[i][3] == str(anio)
        ):
            filas[i][4] = str(round(float(filas[i][4]) + tiempo_decimal, 2))
            encontrado = True
            break

    if not encontrado:
        filas.append([dia_semana, dia, mes, anio, round(tiempo_decimal, 2)])

    with open(ARCHIVO, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerows(filas)


def detener_contador():
    global contador_activo
    global inicio_contador

    if not contador_activo:
        print("No hay ningún contador en ejecución.")
        return

    tiempo_decimal = (time.time() - inicio_contador) / 3600

    guardar_tiempo(tiempo_decimal)

    print(f"Tiempo guardado: {round(tiempo_decimal, 2)} horas")

    contador_activo = False
    inicio_contador = None


def mostrar_historico():
    crear_archivo_si_no_existe()

    total = 0

    print("\n--- HISTÓRICO ---")

    with open(ARCHIVO, "r", newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)

        primera = True

        for fila in lector:
            if primera:
                primera = False
                continue

            print(f"{fila[0]} {fila[1]} de {fila[2]} de {fila[3]} -> {fila[4]} horas")
            total += float(fila[4])

    print(f"\nTiempo total acumulado: {round(total, 2)} horas")


def modificar_registro():
    filas = []

    with open(ARCHIVO, "r", newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            filas.append(fila)

    if len(filas) <= 1:
        print("No hay registros para modificar.")
        return

    print("\n--- REGISTROS ---")

    for i in range(1, len(filas)):
        fila = filas[i]
        print(f"{i}. {fila[0]} {fila[1]} de {fila[2]} de {fila[3]} -> {fila[4]} horas")

    while True:
        opcion = input("Seleccione un registro: ").strip()

        if not opcion.isdigit():
            print("Ingrese un número válido.")
            continue

        opcion = int(opcion)

        if opcion < 1 or opcion >= len(filas):
            print("Registro inexistente.")
            continue

        break

    while True:
        nuevo = input("Nuevo tiempo decimal: ").strip()

        try:
            nuevo = float(nuevo)

            if nuevo < 0:
                print("No puede ser negativo.")
                continue

            break

        except ValueError:
            print("Ingrese un número válido.")

    filas[opcion][4] = str(round(nuevo, 2))

    with open(ARCHIVO, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerows(filas)

    print("Registro actualizado correctamente.")

def ajustar_horas_hoy():

    dia_semana, dia, mes, anio = obtener_fecha()

    filas = []

    with open(ARCHIVO, "r", newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)

        for fila in lector:
            filas.append(fila)

    indice_hoy = None

    for i in range(1, len(filas)):

        if (
            filas[i][1] == str(dia)
            and filas[i][2] == mes
            and filas[i][3] == str(anio)
        ):
            indice_hoy = i
            break

    # Si hoy todavía no existe en el CSV
    if indice_hoy is None:

        print("\nNo existe un registro para hoy.")
        print("Se creará uno nuevo.")

        filas.append([
            dia_semana,
            dia,
            mes,
            anio,
            0
        ])

        indice_hoy = len(filas) - 1

    tiempo_actual = float(filas[indice_hoy][4])

    print(f"\nHoras registradas hoy: {tiempo_actual} hs")

    while True:

        ajuste = input(
            "Ingrese ajuste (+2, -0.5, etc): "
        ).strip()

        try:

            ajuste = float(ajuste)

            nuevo_total = tiempo_actual + ajuste

            if nuevo_total < 0:
                print(
                    "El resultado no puede ser negativo."
                )
                continue

            break

        except ValueError:
            print("Ingrese un número válido.")

    filas[indice_hoy][4] = str(round(nuevo_total, 2))

    with open(ARCHIVO, "w", newline="", encoding="utf-8") as archivo:

        escritor = csv.writer(archivo)

        escritor.writerows(filas)

    print("\nAjuste realizado correctamente.")
    print(f"Anterior: {tiempo_actual} hs")
    print(f"Ajuste: {ajuste:+.2f} hs")
    print(f"Nuevo total: {round(nuevo_total, 2)} hs")

def sincronizar_github():

    try:

        subprocess.run(
            ["git", "add", ARCHIVO],
            check=True,
            capture_output=True,
            text=True
        )

        # Puede fallar si no hay cambios.
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                "Actualización automática de horas"
            ],
            capture_output=True,
            text=True
        )

        subprocess.run(
            ["git", "push"],
            check=True,
            capture_output=True,
            text=True
        )

        print(
            "\n¡Sincronización exitosa con GitHub!"
        )

    except Exception as e:

        print(
            "\n⚠️ Error al sincronizar con GitHub."
        )

        print(str(e))

#-----------------------------------------------------------------------------------------------------

crear_archivo_si_no_existe()

try:
    while True:
        print("1. Iniciar contador")
        print("2. Detener contador")
        print("3. Agregar tiempo manualmente")
        print("4. Ver histórico")
        print("5. Modificar registro")
        print("6. Ajustar horas de hoy")
        print("7. Sincronizar con GitHub (Push)")
        print("8. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if not opcion.isdigit():
            print("Error: Debe ingresar un número válido.")
            continue

        opcion = int(opcion)

        if opcion == 1:
            if contador_activo:
                print("El contador ya está corriendo.")
            else:
                inicio_contador = time.time()
                contador_activo = True
                print("Contador iniciado.")

        elif opcion == 2:
            detener_contador()

        elif opcion == 3:
            while True:
                valor = input("Ingrese horas decimales: ").strip()

                try:
                    valor = float(valor)

                    if valor <= 0:
                        print("Ingrese un valor mayor que cero.")
                        continue

                    guardar_tiempo(valor)
                    print("Tiempo agregado correctamente.")
                    break

                except ValueError:
                    print("Ingrese un número válido.")

        elif opcion == 4:
            mostrar_historico()

        elif opcion == 5:
            modificar_registro()

        elif opcion == 6:
            ajustar_horas_hoy()

        elif opcion == 7:
            sincronizar_github()

        elif opcion == 8:

            if contador_activo:
                detener_contador()

            print("Programa finalizado.")
            break

        else:
            print("Opción inválida.")

except KeyboardInterrupt:
    print("\\nInterrupción detectada.")

    if contador_activo:
        detener_contador()

    print("Datos guardados. Cerrando programa.")
