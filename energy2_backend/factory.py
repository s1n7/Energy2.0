from datetime import date


def simulate_input(start_date, producers):
    current_hour = 0
    current_datetime = date.now()

# @api_view(['GET'])
# def populate_view(request):
#     if request.method == 'GET':
#         while True:
#             sensor = Sensor.objects.create(eui_id=123, device_id=123)
#             Producer.objects.create(name="Test", sensor=sensor)
#             print('created')
#             time.sleep(15)
#
#         return Response({"message": "Got some data!", "data": request.data})
#
#     # Messpunkt(Measuring) = (kWh, time)
#     # gegeben: Startzeit, Intervall n für 1/n, TimeArray
#     # TimeArray[24]: Für jede Stunde ein Sonnenfaktor(0=keine Sonne 1=normale Sonne 2=sehr Sonnig)