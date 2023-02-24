from decimal import Decimal
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
    - elif producer_id and consumer_id are None:
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
        data = get_producer_output(producer, start_date, end_date, request)
        print(datetime.now() - st)
        return Response(data, status=200)
    elif consumer_id:
        consumer = get_object_or_404(Consumer, pk=consumer_id)
        data = get_consumer_output(consumer, start_date, end_date, request)
        data.update(get_producer_output(consumer.producer, start_date, end_date, request, True))
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
        # loop over all producers and sum their values
        producer_set = Producer.objects.all()
        if len(producer_set) == 0:
            raise NotFound()
        for producer in producer_set:
            # get all data for producer but dont aggregate all consumptions to one data set
            producers[producer.name] = get_producer_output(producer, start_date, end_date, request,
                                                           no_aggregation=True)
            producers_total_revenue += producers[producer.name]['consumers_total_revenue']
            producers_total_production += producers[producer.name]['total_production']
            producers_total_used += producers[producer.name]['total_used']
            producers_total_consumption += producers[producer.name]['consumers_total_consumption']
            producers_total_saved += producers[producer.name]['consumers_total_saved']

        data = {
            'producers_total_production': producers_total_production,
            'producers_total_used': producers_total_used,
            'producers_total_revenue': producers_total_revenue,
            'producers_total_consumption': producers_total_consumption,
            'producers_total_saved': producers_total_saved,
            'producers': producers
        }
        print(datetime.now() - st)
        return Response(data)


def get_producer_output(producer, start_date, end_date, request, only_productions=False, no_aggregation=False):
    """
    Get all productions of producer in given timeframe and calculates aggregations 
    @return
    :param no_aggregation:
    :param only_productions:
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
    serialized_productions = ProductionSerializer(productions, many=True, context={'request': request}).data
    data = {'productions': serialized_productions}
    if not only_productions:
        if len(productions) > 1:
            # total_production = difference of first and last meter_reading
            total_production = productions.last().production_meter_reading - \
                               productions.first().production_meter_reading
            # total_used = difference total_production & total_grid_feed_in
            total_used = total_production - (productions.last().grid_meter_reading -
                                             productions.first().grid_meter_reading)
        else:
            # if only one is in timeframe -> difference wont work
            total_production = productions.first().produced
            total_used = productions.first().used
        aggregated_consumer_data = aggregate_consumer_outputs(producer.consumer_set.all(), start_date, end_date, request,
                                                              no_aggregation)
        data.update(aggregated_consumer_data)
        data.update({
            'total_production': total_production,
            'total_used': total_used
        })
    return data


def get_consumer_output(consumer, start_date, end_date, request):
    consumptions = Consumption.objects.filter(consumer__id=consumer.id, time__gte=start_date, time__lte=end_date)
    if len(consumptions) == 0:
        raise NotFound()
    if len(consumptions) > 1:
        total_consumption = consumptions.last().meter_reading - consumptions.first().meter_reading
    else:
        total_consumption = consumptions.first().consumption
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


def aggregate_consumer_outputs(consumer_set, start_date, end_date, request, no_aggregation=False):
    consumers = {}
    for consumer in consumer_set:
        consumptions = get_consumer_output(consumer, start_date, end_date, request)
        consumers[consumer.name] = consumptions
        # revenue, consumption, saved over all consumers of producer
    consumers_total_revenue = 0
    consumers_total_consumption = 0
    consumers_total_saved = 0
    for consumer in consumers.values():
        consumers_total_revenue += consumer['total_price']
        consumers_total_consumption += consumer['total_consumption']
        consumers_total_saved += consumer['total_saved']
    data = {
        'consumers_total_revenue': consumers_total_revenue,
        'consumers_total_consumption': consumers_total_consumption,
        'consumers_total_saved': consumers_total_saved,
        'consumers': consumers,
    }

    if not no_aggregation:
        # aggregate all consumptions to one summed dataset
        consumptions = []
        for i in range(0, len(list(consumers.values())[0]['consumptions'])):
            consumption = 0
            self_consumption = 0
            grid_consumption = 0
            time = list(consumers.values())[0]['consumptions'][i]['time']
            for consumer in consumers.values():
                consumption += Decimal(consumer['consumptions'][i]['consumption'])
                self_consumption += Decimal(consumer['consumptions'][i]['self_consumption'])
                grid_consumption += Decimal(consumer['consumptions'][i]['grid_consumption'])
            consumptions.append({
                'time': time,
                'consumption': consumption,
                'self_consumption': self_consumption,
                'grid_consumption': grid_consumption
            })
        data.update({'consumptions': consumptions})
    return data
