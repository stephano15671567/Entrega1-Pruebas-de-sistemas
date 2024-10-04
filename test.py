import unittest
import grpc
from distance_unary_pb2 import SourceDest, Position
from distance_unary_pb2_grpc import DistanceServiceStub

class TestDistanceService(unittest.TestCase):

    # Configura la conexión al servidor gRPC
    def setUp(self):
        self.canal = grpc.insecure_channel("localhost:50051")
        self.stub = DistanceServiceStub(self.canal)

    # Cierra la conexión después de cada prueba
    def tearDown(self):
        self.canal.close()

    # 1- Prueba una distancia válida entre dos puntos en kilómetros (success path)
    def test_distancia_valida_km(self):
        solicitud = SourceDest(
            source=Position(latitude=0, longitude=0),
            destination=Position(latitude=10, longitude=10),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(solicitud)
        # Delta estricto para forzar el fallo si no coincide exactamente
        self.assertAlmostEqual(respuesta.distance, 1568, delta=1)
        self.assertEqual(respuesta.unit, "km")

    # 2- Prueba una distancia válida entre dos puntos en millas náuticas (success path)
    def test_distancia_valida_nm(self):
        solicitud = SourceDest(
            source=Position(latitude=0, longitude=0),
            destination=Position(latitude=10, longitude=10),
            unit="nm"
        )
        respuesta = self.stub.geodesic_distance(solicitud)
        # Delta estricto para forzar el fallo si no coincide exactamente
        self.assertAlmostEqual(respuesta.distance, 847, delta=1)
        self.assertEqual(respuesta.unit, "nm")

    # 3- Prueba con una latitud inválida por encima del rango permitido (expected exception)
    def test_latitud_invalida_superior(self):
        solicitud = SourceDest(
            source=Position(latitude=91, longitude=0),
            destination=Position(latitude=10, longitude=10),
            unit="km"
        )
        # Verificamos que el servicio debería lanzar una excepción ValueError
        with self.assertRaises(ValueError):  # Esto debería fallar si no se lanza la excepción
            self.stub.geodesic_distance(solicitud)

    # 4- Prueba con una longitud inválida por debajo del rango permitido (expected exception)
    def test_longitud_invalida_inferior(self):
        solicitud = SourceDest(
            source=Position(latitude=0, longitude=-181),
            destination=Position(latitude=10, longitude=10),
            unit="km"
        )
        # Verificamos que el servicio debería lanzar una excepción ValueError
        with self.assertRaises(ValueError):  # Esto debería fallar si no se lanza la excepción
            self.stub.geodesic_distance(solicitud)

    # 5- Prueba con una longitud inválida por encima del rango permitido (expected exception)
    def test_longitud_invalida_superior(self):
        solicitud = SourceDest(
            source=Position(latitude=0, longitude=181),
            destination=Position(latitude=10, longitude=10),
            unit="km"
        )
        # Verificamos que el servicio debería lanzar una excepción ValueError
        with self.assertRaises(ValueError):  # Esto debería fallar si no se lanza la excepción
            self.stub.geodesic_distance(solicitud)

    # 6- Prueba sin especificar una unidad, debería devolver kilómetros por defecto (success path)
    def test_sin_unidad(self):
        solicitud = SourceDest(
            source=Position(latitude=0, longitude=0),
            destination=Position(latitude=10, longitude=10),
            unit=""
        )
        respuesta = self.stub.geodesic_distance(solicitud)
        # Delta estricto para que falle si el valor no es exacto
        self.assertAlmostEqual(respuesta.distance, 1568, delta=1)
        self.assertEqual(respuesta.unit, "km")

    # 7- Prueba con una latitud cerca del límite inferior (valores frontera)
    def test_latitud_casi_minima(self):
        solicitud = SourceDest(
            source=Position(latitude=-89.999, longitude=0),
            destination=Position(latitude=10, longitude=10),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(solicitud)
        self.assertGreaterEqual(respuesta.distance, 0)

    # 8- Prueba con la latitud y longitud mínima permitida (valores frontera)
    def test_latitud_longitud_minima(self):
        solicitud = SourceDest(
            source=Position(latitude=-90, longitude=-180),
            destination=Position(latitude=-90, longitude=-180),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(solicitud)
        self.assertEqual(respuesta.distance, 0.0)

    # 9- Prueba con valores flotantes pequeños e inusuales (casos límites)
    def test_valores_flotantes_inusuales(self):
        solicitud = SourceDest(
            source=Position(latitude=0.000001, longitude=-179.999999),
            destination=Position(latitude=0.000002, longitude=-179.999998),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(solicitud)
        self.assertGreaterEqual(respuesta.distance, 0)

    # 10- Prueba cuando los puntos de origen y destino son los mismos (success path)
    def test_mismo_origen_y_destino(self):
        solicitud = SourceDest(
            source=Position(latitude=0, longitude=0),
            destination=Position(latitude=0, longitude=0),
            unit="km"
        )
        respuesta = self.stub.geodesic_distance(solicitud)
        self.assertEqual(respuesta.distance, 0.0)
        self.assertEqual(respuesta.unit, "km")


if __name__ == "__main__":
    unittest.main()
