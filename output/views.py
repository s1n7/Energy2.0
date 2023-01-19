import decimal
from datetime import datetime, timedelta

from base.data.models import Production, Consumption
from base.data.serializers import ProductionSerializer, ConsumptionSerializer
from base.sensors.models import Producer, Consumer
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response


# Create your views here.
@api_view(['GET', ])
@permission_classes([permissions.IsAuthenticated])
def output_view(request):
    """
Endpoint to get data for data display, charts etc.

* if user.is_admin:
    * if producer_id is specified:
        * return all productions of producer & consumptions of its consumers
    - else:
        - return productions and consumptions of all producers and their consumers
- if not user.is_admin or (user.is_admin and consumer_id is specified):
    - return all consumptions of consumer

    """
    st = datetime.now()
    user = request.user
    query_params = request.query_params
    start_date = query_params.get('start_date')
    end_date = query_params.get('end_date')
    # if no time is specified -> last 30days
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()

    producer_id = query_params.get('producer_id')
    consumer_id = query_params.get('consumer_id')
    # non-admins can only access their own consumption data
    if not user.is_staff:
        consumer_id = user.consumer.id
    # if producer_id is set the user has to be an admin
    if producer_id is not None:
        if not user.is_staff:
            raise PermissionDenied()
        # get_productions in the timeframe -> sum production and used
        # for all consumers do the same (maybe only the prices)
        producer = get_object_or_404(Producer, pk=producer_id)
        data = get_productions_and_aggregations(producer, start_date, end_date, request)
        print(datetime.now() - st)
        return Response(data, status=200)
    elif consumer_id:
        consumer = get_object_or_404(Consumer, pk=consumer_id)
        data = get_consumptions_and_aggregations(consumer, start_date, end_date, request)
        print(datetime.now() - st)
        return Response(data)
    # if no consumer_id is set and no production_id
    # return all data of all producers
    else:
        producers = {}
        producers_total_revenue = 0
        producers_total_production = 0
        producers_total_used = 0
        producers_total_consumption = 0
        producers_total_saved = 0
        for producer in Producer.objects.all():
            producers[producer.name] = get_productions_and_aggregations(producer, start_date, end_date, request)
            producers_total_revenue += producers[producer.name]['consumers_total_revenue']
            producers_total_production += producers[producer.name]['total_production']
            producers_total_used += producers[producer.name]['total_used']
            producers_total_consumption += producers[producer.name]['consumers_total_consumption']
            producers_total_saved += producers[producer.name]['consumers_total_saved']
        data = {'producers_total_production': producers_total_production,
                'producers_total_used': producers_total_used,
                'producers_total_revenue': producers_total_revenue,
                'producers_total_consumption': producers_total_consumption,
                'producers_total_saved': producers_total_saved,
                'producers': producers}
        print(datetime.now() - st)
        return Response(data)


def get_productions_and_aggregations(producer, start_date, end_date, request):
    """
    Get all productions of producer in given timeframe and calculates aggregations @return
    :param producer:
    :param start_date:
    :param end_date:
    :param request:
    :return: {productions, total_production, total_used, self_usage_percentage,
    consumers: {consumer.name: {consumptions_and_aggregations}}}
    """
    productions = Production.objects.filter(producer__id=producer.id, time__gte=start_date, time__lte=end_date)
    if len(productions) == 0:
        raise NotFound()
    if len(productions) > 1:
        # total_production = difference of first and last meter_reading
        total_production = productions.last().production_meter_reading - productions.first().production_meter_reading
        # total_used = difference total_production & total_grid_feed_in
        total_used = total_production - (productions.last().grid_meter_reading - productions.first().grid_meter_reading)
    else:
        total_production = productions.first().production_meter_reading
        total_used = total_production - productions.first().grid_meter_reading
    try:
        self_usage_percentage = round(total_used / total_production * 100, 1)
    except decimal.DivisionByZero:
        self_usage_percentage = None
    serialized_productions = ProductionSerializer(productions, many=True, context={'request': request}).data

    consumers = {}
    for consumer in producer.consumer_set.all():
        consumptions = get_consumptions_and_aggregations(consumer, start_date, end_date, request)
        consumers[consumer.name] = consumptions
    # TODO: add consumers_total_revenue and consumers_total_consumption
    consumers_total_revenue = 0
    consumers_total_consumption = 0
    consumers_total_saved = 0
    for consumer in consumers.values():
        consumers_total_revenue += consumer['total_price']
        consumers_total_consumption += consumer['total_consumption']
        consumers_total_saved += consumer['total_saved']
    return {'total_production': total_production,
            'total_used': total_used,
            'self_usage_percentage': self_usage_percentage,
            'consumers_total_revenue': consumers_total_revenue,
            'consumers_total_consumption': consumers_total_consumption,
            'consumers_total_saved': consumers_total_saved,
            'productions': serialized_productions,
            'consumers': consumers}


def get_consumptions_and_aggregations(consumer, start_date, end_date, request):
    consumptions = Consumption.objects.filter(consumer__id=consumer.id, time__gte=start_date, time__lte=end_date)
    total_consumption = consumptions.last().meter_reading - consumptions.first().meter_reading
    total_self_consumption, total_price, total_reduced_price, total_saved = \
        consumptions.aggregate(Sum('self_consumption'), Sum('price'), Sum('reduced_price'), Sum('saved')).values()
    total_grid_consumption = total_consumption - total_self_consumption
    total_grid_price = total_price - total_reduced_price
    serialized_consumptions = ConsumptionSerializer(consumptions, many=True, context={'request': request}).data
    return {
        'id': consumer.id,
        'consumptions': serialized_consumptions,
        'total_consumption': total_consumption,
        'total_self_consumption': total_self_consumption,
        'total_grid_consumption': total_grid_consumption,
        'total_price': total_price,
        'total_reduced_price': total_reduced_price,
        'total_grid_price': total_grid_price,
        'total_saved': total_saved
    }
