"""
Copyright (c) 2018-2021 Qualcomm Technologies, Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written permission.
* The origin of this software must not be misrepresented; you must not claim that you wrote the original software.
If you use this software in a product, an acknowledgment is required by displaying the trademark/log as per the details
provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
* Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
* This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.
"""


import os
import magic
from dns_app.common.json_parser import json_parser
from django.db.models import Q
from elasticsearch_dsl import Search, Q
from django.http import JsonResponse
from device_notification_subsystem.celery import app
from device_notification_subsystem.settings import conf
from rest_framework.response import Response
from django_celery_results.models import TaskResult
from .tasks import bulk_sms_file, celery_email, jasmine_sms, bulk_sms_db, bulk_email_db, bulk_email_file
from rest_framework import status
from rest_framework.decorators import api_view
from .paginations import CustomLimitOffsetPagination
from .models import Sms, UniqueMsisdn, UniqueEmail, SmsContent, Email, EmailContent
from rest_framework import viewsets
from .serializers import (SmsSerializer, SmsContentSerializer, EmailSerializer, EmailContentSerializer,
                          UniqueMsisdnSerializer, UniqueEmailSerializer)


class SmsView(viewsets.ModelViewSet):
    queryset = Sms.objects.all()
    serializer_class = SmsSerializer
    pagination_class = CustomLimitOffsetPagination

    # Over-riding create method to perform DB insertion simultaneously in two related models namely
    # Sms & SmsContent

    def create(self, request, *args, **kwargs):

        # API params to get validated using SmsSerializer. SmsContentSerializer is not used because Foreign-Key
        # parameter "sms_id" is not provided in params rather extracted from first DB object.

        serializer1 = SmsSerializer(data=request.data)
        serializer1.is_valid(raise_exception=True)

        data = {
            "sms_to": request.data.get('sms_to').strip(),
            "sms_from": request.data.get('sms_from').strip(),
            "imei": request.data.get('imei'),
            "subsystem": request.data.get('subsystem').strip(),
            "operator": request.data.get('operator'),
            "filename": request.data.get('filename'),
            "sms_content": request.data.get('sms_content').strip()
        }

        if request.data.get('sms_content'):

            if not data['filename']: data['filename'] = ""
            if not data['imei']: data['imei'] = ""
            if not data['operator']: data['operator'] = ""

            # sending SMS by calling jasmine API via celery using default queue
            jasmine_sms.apply_async(args=[data['sms_to'], data['sms_content'], data['sms_from']])

            # writing into database
            sms_obj = Sms.objects.create(imei=data['imei'].strip(), sms_to=data['sms_to'], sms_from=data['sms_from'],
                                         operator=data['operator'], subsystem=data['subsystem'],
                                         filename=data['filename'].strip())

            sms_content_obj = SmsContent(sms_content=data['sms_content'], sms_id=sms_obj.id)
            sms_content_obj.save()

            msg = {'message': "SMS is being sent to the recipient"}
            return Response(data=msg, status=status.HTTP_200_OK)
        else:
            error = {"Error": "SMS Content is missing"}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)


class SmsContentView(viewsets.ModelViewSet):
    queryset = SmsContent.objects.all()
    serializer_class = SmsContentSerializer
    pagination_class = CustomLimitOffsetPagination


class EmailView(viewsets.ModelViewSet):
    queryset = Email.objects.all()
    serializer_class = EmailSerializer
    pagination_class = CustomLimitOffsetPagination

    # Over-riding create method to perform DB insertion simultaneously in two related models namely
    # EEmailContent

    def create(self, request, *args, **kwargs):

        # API params to get validated using SmsSerializer. SmsContentSerializer is not used because Foreign-Key
        # parameter "sms_id" is not provided in params rather extracted from first DB object.

        serializer1 = EmailSerializer(data=request.data)
        serializer1.is_valid(raise_exception=True)

        data = {
            "email_to": request.data.get('email_to').strip(),
            "email_from": request.data.get('email_from').strip(),
            "imei": request.data.get('imei'),
            "subsystem": request.data.get('subsystem').strip(),
            "filename": request.data.get(''),
            "email_subject": request.data.get('email_subject'),
            "email_content": request.data.get('email_content'),
        }

        if data['email_subject'] and data['email_content']:

            if not data['filename']: data['filename'] = ""
            if not data['imei']: data['imei'] = ""

            # sending Email via Celery using default queue
            celery_email.apply_async(args=[data['email_subject'], data['email_content'], data['email_from'],
                                           data['email_to']])

            # writing into database
            email_obj = Email.objects.create(email_to=data['email_to'], email_from=data['email_from'],
                                             imei=data['imei'].strip(), subsystem=data['subsystem'],
                                             filename=data['filename'].strip())

            email_content_obj = EmailContent(email_subject=data['email_subject'].strip(),
                                             email_content=data['email_content'].strip(),
                                             email_id=email_obj.id)
            email_content_obj.save()

            msg = {'message': "Email is being sent to the recipient"}
            return Response(data=msg, status=status.HTTP_200_OK)
        else:
            error = {"Error": "Email Subject or Content is missing"}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)


class EmailContentView(viewsets.ModelViewSet):
    queryset = EmailContent.objects.all()
    serializer_class = EmailContentSerializer
    pagination_class = CustomLimitOffsetPagination


class UniqueMsisdnView(viewsets.ModelViewSet):
    queryset = UniqueMsisdn.objects.all()
    serializer_class = UniqueMsisdnSerializer
    pagination_class = CustomLimitOffsetPagination


class UniqueEmailView(viewsets.ModelViewSet):
    queryset = UniqueEmail.objects.all()
    serializer_class = UniqueEmailSerializer
    pagination_class = CustomLimitOffsetPagination


@api_view(['POST'])
def email_campaign(request):
    try:
        file = request.data.get('file')
        content = request.data.get('email_content')
        subject = request.data.get('email_subject')
        subsystem = request.data.get('subsystem')
        sender_email = request.data.get('email_from')
        mode = request.data.get('mode')

        if subsystem not in conf['subsystems']:
            error = {"Error": "Subsystem name is not correct"}
            return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif sender_email not in conf['dns_sender_email']:
            error = {"Error": 'Sender Email {} is not configured'.format(sender_email)}
            return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif mode not in conf['campaign_modes']:
            error = {"Error": "Campaign Mode ""{}"" is not configured".format(mode)}
            return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif content in [None, ""] or subject in [None, ""]:
            error = {"Error": "Email subject or content can not be empty"}
            return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        subject = subject.strip()
        content = content.strip()

        if mode == "DB":
            bulk_email_db.apply_async(args=[subject, content, subsystem, sender_email])  # calling celery task
            msg = {'message': "Email-Campaign is being run in the background"}
            return JsonResponse(data=msg, status=status.HTTP_200_OK)
        elif mode == "File":
            if file:
                filetype = magic.from_file(file, mime=True)  # checking File type
                if filetype == 'text/plain' or filetype == 'application/csv':
                    bulk_email_file.apply_async(args=[file, subject, content, subsystem, sender_email])  # calling celery task
                    msg = {'message': "File is being processed in the background"}
                    return JsonResponse(data=msg, status=status.HTTP_200_OK)
                else:
                    error = {"Error": "System only accepts csv/txt files"}
                    return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            else:
                error = {"Error": "File name is missing"}
                return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    except FileNotFoundError:
        error = {"Error": "No such file or directory exists"}
        return Response(data=error, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def sms_campaign(request):
    try:
        file = request.data.get('file')
        content = request.data.get('sms_content')
        operator = request.data.get('operator')
        subsystem = request.data.get('subsystem')
        sender_no = request.data.get('sms_from')
        mode = request.data.get('mode')
        sms_rate = request.data.get('sms_rate')

        if operator not in conf['mnos']:
            error = {"Error": "Operator name is not correct"}
            return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif subsystem not in conf['subsystems']:
            error = {"Error": "Subsystem name is not correct"}
            return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif sender_no not in conf['dns_sender_no']:
            error = {"Error": 'Sender Number {} is not configured'.format(sender_no)}
            return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif mode not in conf['campaign_modes']:
            error = {"Error": "Campaign Mode ""{}"" is not configured".format(mode)}
            return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif content in [None, ""]:
            error = {"Error": "SMS content can not be empty"}
            return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif not isinstance(sms_rate, int) or int(sms_rate) > conf['sms_batch_size']:
            error = {"Error": "SMS Rate is not within the configured limits"}
            return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if mode == "File":
            if file and file_allowed(os.path.basename(file)):
                filetype = magic.from_file(file, mime=True)   # checking File type
                if filetype == 'text/plain' or filetype == 'application/csv':
                    bulk_sms_file.apply_async(args=[file, content, operator, subsystem, sender_no, sms_rate])   # calling celery task
                    msg = {'message': "File is being processed in the background"}
                    return JsonResponse(data=msg, status=status.HTTP_200_OK)
                else:
                    error = {"Error": "System only accepts csv/txt files"}
                    return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            else:
                error = {"Error": "File is either missing or having forbidden extension"}
                return Response(data=error, status=status.HTTP_400_BAD_REQUEST)
        elif mode == "DB":
            bulk_sms_db.apply_async(args=[content, operator, subsystem, sender_no, sms_rate])  # calling celery task
            msg = {'message': "SMS-Campaign is being run in the background"}
            return JsonResponse(data=msg, status=status.HTTP_200_OK)

    except FileNotFoundError:
        error = {"Error": "No such file or directory exists"}
        return Response(data=error, status=status.HTTP_404_NOT_FOUND)


def file_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in conf['allowed_extensions']


def dns(request):
    msg = {"message": "Welcome to DNS"}
    return JsonResponse(msg)


def workers_detail(request):
    tmp_json = worker_status()
    result = json_parser(tmp_json)
    if result.status_code == 200:
        return result
    else:
        return result


# noinspection PyBroadException
def worker_status():
    try:
        i = app.control.inspect()
        availability = i.ping()
        active_tasks = i.active()
        reserved_tasks = i.reserved()
        active_queues = i.active_queues()
        result = {
            'availability': availability,
            'active_tasks': active_tasks,
            'reserved_tasks': reserved_tasks,
            'active_queues': active_queues
        }
        return result
    except Exception:
        error = {"Error": "No Celery-Worker is found"}
        return Response(data=error, status=status.HTTP_404_NOT_FOUND)


# noinspection PyUnboundLocalVariable,PyBroadException,PyUnusedLocal
@api_view(['GET'])
def search_sms(request):
    """ Function for searching SMS related fields.
        Here we are using dns_sms_content index instead of dns_sms. This will get the job done in single request.
    """
    try:
        search_params = []
        offset = request.GET.get('offset')
        limit = request.query_params.get('limit')
        sms_to = request.GET.get('sms_to')
        sms_from = request.query_params.get('sms_from')
        imei = request.GET.get('imei')
        subsystem = request.query_params.get('subsystem')
        operator = request.GET.get('operator')
        filename = request.query_params.get('filename')
        sms_content = request.GET.get('sms_content')
        start_date = request.GET.get('start_date')
        end_date = request.query_params.get('end_date')
        campaign_id = request.GET.get('campaign_id')

        if offset is not None and limit is not None and offset.isnumeric() and limit.isnumeric():
            offset = int(offset.strip())
            limit = int(limit.strip())
            s = Search(index='dns_sms_content')
            if sms_to:
                q1 = Q("match_phrase", sms__sms_to=sms_to.strip())
                search_params.append(q1)
            if sms_from:
                q2 = Q("match", sms__sms_from=sms_from.strip())
                search_params.append(q2)
            if imei:
                q3 = Q("match_phrase", sms__imei=imei.strip())  # match_phrase strictly matches provided str with doc field
                search_params.append(q3)
            if subsystem:
                q4 = Q("match_phrase", sms__subsystem=subsystem.strip())
                search_params.append(q4)
            if operator:
                q5 = Q("match_phrase", sms__operator=operator.strip())
                search_params.append(q5)
            if filename:
                q6 = Q("match", sms__filename=filename.strip())
                search_params.append(q6)
            if sms_content:
                q7 = Q("match", sms_content=sms_content.strip())
                search_params.append(q7)
            if campaign_id:
                q8 = Q("match", sms__campaign_id=campaign_id.strip())
                search_params.append(q8)
            if start_date and end_date:
                if start_date > end_date:
                    error = {"Error": "wrong date ranges"}
                    return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                q9 = Q(
                    {
                        "range": {
                            "sms.sms_delivered": {
                                "gte": start_date.strip(),
                                "lte": end_date.strip()
                            }
                        }
                    }
                )

                search_params.append(q9)

            s.query = Q('bool', must=search_params)
            response = s.execute()  # execute method allow to access any key from the response dictionary via attribute access.
            count = response.hits.total.value

            # s.query = q1 & q2  another way of ANDing two queries
            # s = SmsContentDocument.search().query("match", sms__sms_to="923329837713")
            # result = s.to_dict()

            t_limit = offset + limit
            result, data = [], {}

            for hit in s[offset:t_limit]:  # Pagination happens here
                res = hit.to_dict()
                data = res['sms']
                data['sms_content'] = res['sms_content']
                result.append(data)

            msg = {"limit": int(limit), "offset": int(offset), "count": count, "Result": result}
            return JsonResponse(msg, status=status.HTTP_200_OK)

        else:
            error = {"Error": "wrong limit or offset"}
            return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    except Exception as e:
        error = {"Error": "Search failed"}
        return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


# noinspection PyBroadException,PyUnusedLocal
@api_view()
def search_email(request):
    """ Function for searching Email related fields.
        Here we are using dns_email_content index instead of dns_email. This will get the job done in single request.
    """
    try:
        search_params = []
        offset = request.GET.get('offset')
        limit = request.query_params.get('limit')
        email_to = request.GET.get('email_to')
        email_from = request.query_params.get('email_from')
        imei = request.GET.get('imei')
        subsystem = request.query_params.get('subsystem')
        filename = request.query_params.get('filename')
        email_subject = request.GET.get('email_subject')
        email_content = request.query_params.get('email_content')
        start_date = request.GET.get('start_date')
        end_date = request.query_params.get('end_date')
        campaign_id = request.GET.get('campaign_id')

        if offset is not None and limit is not None and offset.isnumeric() and limit.isnumeric():
            offset = int(offset.strip())
            limit = int(limit.strip())
            s = Search(index='dns_email_content')
            if email_to:
                q1 = Q("match_phrase", email__email_to=email_to.strip())
                search_params.append(q1)
            if email_from:
                q2 = Q("match", email__email_from=email_from.strip())
                search_params.append(q2)
            if imei:
                q3 = Q("match_phrase", email__imei=imei.strip())
                search_params.append(q3)
            if subsystem:
                q4 = Q("match_phrase", email__subsystem=subsystem.strip())
                search_params.append(q4)
            if filename:
                q5 = Q("match", email__filename=filename.strip())
                search_params.append(q5)
            if email_subject:
                q6 = Q("match_phrase", email_subject=email_subject.strip())
                search_params.append(q6)
            if email_content:
                q7 = Q("match_phrase", email_content=email_content.strip())
                search_params.append(q7)
            if campaign_id:
                q8 = Q("match", email__campaign_id=campaign_id.strip())
                search_params.append(q8)
            if start_date and end_date:
                if start_date > end_date:
                    error = {"Error": "wrong date ranges"}
                    return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                q9 = Q(
                    {
                        "range": {
                            "email.email_delivered": {
                                "gte": start_date.strip(),
                                "lte": end_date.strip()
                            }
                        }
                    }
                )

                search_params.append(q9)

            s.query = Q('bool', must=search_params)

            response = s.execute()  # execute method allow to access any key from the response dictionary via attribute access.

            count = response.hits.total.value

            t_limit = offset + limit
            result, data = [], {}

            for hit in s[offset:t_limit]:  # Pagination happens here
                res = hit.to_dict()
                data = res['email']
                data['email_subject'] = res['email_subject']
                data['email_content'] = res['email_content']
                result.append(data)

            msg = {"limit": int(limit), "offset": int(offset), "count": count, "Result": result}
            return JsonResponse(msg, status=status.HTTP_200_OK)

        else:
            error = {"Error": "wrong limit or offset"}
            return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    except Exception as e:
        error = {"Error": "Search failed"}
        return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


def completed_campaigns(request):
    cmp = {}
    campaign = {"campaigns": []}

    offset = request.GET.get('offset')
    limit = request.GET.get('limit')
    if offset is not None and limit is not None and offset.isnumeric() and limit.isnumeric():
        offset = int(offset.strip())
        limit = int(limit.strip())

    # res = TaskResult.objects.filter(Q(task_name='dns_app.tasks.bulk_sms_file') | Q(task_name='dns_app.tasks.bulk_email_file')).order_by('-date_done')
        count = (TaskResult.objects.filter(task_name='dns_app.tasks.bulk_sms_file') |
               TaskResult.objects.filter(task_name='dns_app.tasks.bulk_email_file')).count()
        campaign['count'] = count
        res = (TaskResult.objects.filter(task_name='dns_app.tasks.bulk_sms_file') |
               TaskResult.objects.filter(task_name='dns_app.tasks.bulk_email_file')).order_by('-date_done')[offset:offset+limit]
        for r in res:
            cmp['campaign_name'] = r.task_name.rsplit('.', 1)[1]
            cmp['campaign_id'] = r.task_id
            cmp['campaign_status'] = r.status
            cmp['campaign_started'] = r.date_created
            cmp['campaign_completed'] = r.date_done
            cmp['campaign_result'] = r.result

            campaign['campaigns'].append(dict(cmp))

        return JsonResponse(campaign, content_type='application/json')
    else:
        error = {"Error": "wrong limit or offset"}
        return Response(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


def mnos(request):
    mno = {"mnos": conf['mnos']}
    return JsonResponse(mno, content_type='application/json', status=status.HTTP_200_OK)


# noinspection PyBroadException
def dashboard_counters(request):
    try:
        t_sms = Sms.objects.all().count()
        t_emails = Email.objects.all().count()
        u_msisdns = UniqueMsisdn.objects.all().count()
        u_emails = UniqueEmail.objects.all().count()
        count = (TaskResult.objects.filter(task_name='dns_app.tasks.bulk_sms_file') |
                 TaskResult.objects.filter(task_name='dns_app.tasks.bulk_email_file')).count()

        counters = {"Total SMS": t_sms, "Total Emails": t_emails, "Unique MSISDNs": u_msisdns,
                    "Unique Email-IDs": u_emails, "Total Campaigns": count}

        return JsonResponse(counters, content_type='application/json', status=status.HTTP_200_OK)

    except Exception:
        error = {"Error": "Error occurred while fetching counters"}
        return JsonResponse(data=error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
