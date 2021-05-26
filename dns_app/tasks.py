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
import json
import time
import string
import requests
import pandas as pd
from math import trunc
from time import strftime
from random import choice
from celery import shared_task
from django.core.mail import send_mail
from device_notification_subsystem.settings import conf
from .models import Sms, SmsContent, Email, EmailContent, UniqueEmail, UniqueMsisdn


@shared_task()
def celery_email(subject, content, sender, recipient):
    recipients = [recipient]
    send_mail(subject, content, sender, recipients, fail_silently=False)
    return "Email has been sent"


@shared_task()
def jasmine_sms(msisdn, content, sender_no):
    url = conf['jasmine_single_sms_url']
    sms_body = {
        "to": msisdn,
        "from": sender_no,
        # "coding": 0,
        "content": content
    }
    headers = {'content-type': 'application/json', 'Authorization': conf['Jasmine_Authorization']}
    response = requests.post(url=url, data=json.dumps(sms_body), headers=headers)
    if response:
        if response.status_code == 200:
            return "SMS sent to {m} : {c}".format(m=msisdn, c=content)
        else:
            return "SMS delivery to {m} is failed".format(m=msisdn)


@shared_task
def bulk_email_db(subject, content, subsystem, sender_email):

    t1 = time.time()
    qry = UniqueEmail.objects.order_by('email').values_list('email', flat=True).distinct()
    campaign_id = "Email_DB_" + strftime("%Y-%m-%d_%H-%M-%S")
    for q in qry:
        print(f"sending email to: {q}")
        celery_email.apply_async(args=[subject, content, sender_email, q], queue='email_que')  # calling celery task

        write_email_db(q, sender_email, subsystem, subject, content, campaign_id)

    t2 = time.time()

    return "Email campaign completed in: {time} secs".format(time=(t2 - t1))


@shared_task
def bulk_sms_db(content, operator, subsystem, sender_no, sms_rate):

    t1 = time.time()
    qry = UniqueMsisdn.objects.order_by('msisdn').values_list('msisdn', flat=True).distinct()

    start = 0
    total_msisdns = len(qry)
    sms_batch_size = sms_rate
    total_chunks = (total_msisdns / sms_batch_size)

    if total_chunks.is_integer(): total_chunks = trunc(total_chunks)
    else: total_chunks = trunc(total_chunks) + 1

    print("total chunks = ", total_chunks)
    end = sms_batch_size

    for chunk in range(0, total_chunks):
        if chunk != total_chunks - 1:
            msisdn_list = qry[start:end]
            start = end
            end = end + sms_batch_size
        else:
            msisdn_list = qry[start:]

        print("processing chunk-", chunk + 1)
        # res = send_sms_batch(msisdn_list, content)
        send_sms_batch(msisdn_list, content)

    print("DB insertion started ")

    campaign_id = "SMS_DB_" + strftime("%Y-%m-%d_%H-%M-%S")

    # result = [write_sms_db(q, sender_no, operator, subsystem, content, campaign_id) for q in qry]
    [write_sms_db(q, sender_no, operator, subsystem, content, campaign_id) for q in qry]

    t2 = time.time()

    return "SMS campaign completed in: {time} sec".format(time=(t2 - t1))


# noinspection PyUnboundLocalVariable,PyUnusedLocal
@shared_task
def bulk_email_file(file, subject, content, subsystem, sender_email):
    """Function to create celery task of processing bulk file for sending Email campaigns """

    t1 = time.time()

    # extracting file path & file name
    file_path, file_name = os.path.split(file)

    try:
        # read the file into DataFrame
        df_csv = pd.read_csv(file, usecols=range(2), dtype={"imei": str, "imsi": str, "email": str},
                             chunksize=conf['df_big_chunksize'])

    except Exception as e:
        if e:
            error = {"Error": "File content is not Correct"}
            return json.dumps(error)

    df = pd.concat(df_csv)

    # removing white spaces from Column 'email'
    df['email'] = df['email'].str.strip()

    # removing Email-IDs with wrong format
    df = df[(df.email.astype(str).str.match(conf['validation_regex']['email']))]

    rows, cols = df.shape
    print(rows, cols)
    start = 0

    # generating random string for file-name
    all_char = string.ascii_letters + string.digits
    rand_str = "".join(choice(all_char) for x in range(8))

    if rows >= 10:
        chunk_size = trunc(rows / 10)
        end = chunk_size
        email_files, all_files = [], []

        for i in range(1, 11):
            print(start, end)
            f_all = "Email_" + rand_str + "_chunk_" + str(i) + ".csv"

            file_all = os.path.join(file_path, f_all)
            print(file_all)

            all_files.append(file_all)

            if i != 10:
                df[start:end].to_csv(file_all, index=False)
                start = end
                end = end + chunk_size
            else:
                df[start:].to_csv(file_all, index=False)
    else:
        return "File must contain more than 10 Email-IDs"

    for i in range(1, 11):
        print("Processing File-", i)
        all_file = all_files[i - 1]
        que = 'que' + str(i)
        process_email_file.apply_async(args=[all_file, subject, content, subsystem, file_name, sender_email],
                                       queue=que)

    t2 = time.time()

    return "File chunking completed in: {time} sec".format(time=(t2 - t1))


# noinspection PyUnboundLocalVariable,PyUnusedLocal
@shared_task
def bulk_sms_file(file, content, operator, subsystem, sender_no, sms_rate):
    """Function to create celery task of processing bulk file for sending SMS campaign """

    t1 = time.time()

    # extracting file path & file name
    file_path, file_name = os.path.split(file)

    try:
        # read the file into DataFrame
        df_csv = pd.read_csv(file, usecols=range(5), dtype={"imei": str, "imsi": str, "msisdn": str, "block_date": str,
                                                            "reasons": str}, chunksize=conf['df_big_chunksize'])
    except Exception as e:
        if e:
            error = {"Error": "File content is not Correct"}
            return json.dumps(error)

    df = pd.concat(df_csv)

    # removing white spaces from Column 'msisdn'
    df['msisdn'] = df['msisdn'].str.strip()

    # removing MSISDN with wrong format
    df = df[(df.msisdn.astype(str).str.match(conf['validation_regex']['msisdn']))]

    # Copying "MSISDN" column to new DataFrame
    df_new = pd.DataFrame()
    df_new['msisdn'] = df['msisdn']

    rows, cols = df_new.shape
    print(rows, cols)
    start = 0

    # generating random string for file-name
    all_char = string.ascii_letters + string.digits
    rand_str = "".join(choice(all_char) for x in range(8))

    if rows >= 10:
        chunk_size = trunc(rows / 10)
        end = chunk_size
        msisdn_files, all_files = [], []

        for i in range(1, 11):

            print(start, end)

            f_msisdn = "MSISDN_only_" + rand_str + "_chunk_" + str(i) + ".csv"
            f_all = "File_all_" + rand_str + "_chunk_" + str(i) + ".csv"

            file_msisdn = os.path.join(file_path, f_msisdn)
            file_all = os.path.join(file_path, f_all)
            print(file_msisdn)

            msisdn_files.append(file_msisdn)
            all_files.append(file_all)

            if i != 10:
                df_new[start:end].to_csv(file_msisdn, index=False)
                df[start:end].to_csv(file_all, index=False)
                start = end
                end = end + chunk_size
            else:
                df_new[start:].to_csv(file_msisdn, index=False)
                df[start:].to_csv(file_all, index=False)
    else:
        return "File must contain more than 10 MSISDNs"

    for i in range(1, 11):
        print("Processing File-", i)
        msisdn_file = msisdn_files[i-1]
        all_file = all_files[i-1]
        que = 'que' + str(i)
        process_sms_file.apply_async(args=[msisdn_file, all_file, content, operator, subsystem, file_name,
                                           sender_no, sms_rate], queue=que)
    t2 = time.time()

    return "File chunking completed in: {time} sec".format(time=(t2 - t1))


@shared_task
def process_email_file(file_all, subject, content, subsystem, file_name, sender_email):

    t1 = time.time()

    df_t2 = pd.read_csv(file_all, chunksize=conf['df_small_chunksize'])
    df_all = pd.concat(df_t2)

    campaign_id = "Email_File_" + strftime("%Y-%m-%d_%H-%M-%S")

    for row in df_all.itertuples(index=False):
        print(f"Sending Email to {row[1]}")
        celery_email(subject, content, sender_email, row[1])
        write_email_db(row[1], sender_email, subsystem, subject, content, campaign_id, file_name, row[0])

    t2 = time.time()

    return "File processing is completed in {time} secs".format(time=(t2 - t1))


@shared_task
def process_sms_file(file_msisdn, file_all, content, operator, subsystem, file_name, sender_no, sms_rate):

    start = 0
    t1 = time.time()
    df_t = pd.read_csv(file_msisdn, chunksize=conf['df_small_chunksize'])
    df_f = pd.concat(df_t)

    df_t2 = pd.read_csv(file_all, chunksize=conf['df_small_chunksize'])
    df_all = pd.concat(df_t2)

    total_msisdns, cols = df_f.shape
    print(df_f.shape)
    sms_batch_size = sms_rate
    total_chunks = (total_msisdns / sms_batch_size)
    if total_chunks.is_integer(): total_chunks = trunc(total_chunks)
    else: total_chunks = trunc(total_chunks) + 1

    print("total chunks = ", total_chunks)
    end = sms_batch_size

    for chunk in range(0, total_chunks):
        if chunk != total_chunks-1:
            msisdn_list = df_f[start:end].stack().to_list()
            start = end
            end = end + sms_batch_size
        else:
            msisdn_list = df_f[start:].stack().to_list()

        print("processing chunk-", chunk+1)
        send_sms_batch(msisdn_list, content)
        time.sleep(1)

    print("DB insertion started ")

    df_all['sms_from'] = sender_no
    df_all['operator'] = operator
    df_all['subsystem'] = subsystem
    df_all['file_name'] = file_name
    df_all['sms_content'] = content

    campaign_id = "SMS_File_" + strftime("%Y-%m-%d_%H-%M-%S")

    # result = [write_sms_db(row[2], row[5], row[6], row[7], row[9], campaign_id, row[8], row[0]) for row in
    #           df_all.itertuples(index=False)]
    [write_sms_db(row[2], row[5], row[6], row[7], row[9], campaign_id, row[8], row[0]) for row in df_all.itertuples(index=False)]

    # ---------------------------------------------------------------------------------------------------------------
    # df_all.to_csv(file_all, index=False, header=False)
    # con = pg.connect("dbname = 'dns_db' user = 'postgres' password = 'postgres' host = 'localhost'  ")
    # cur = con.cursor()
    # f = open(file_all)
    # cur.copy_from(f, 'dns_app_sms', sep=",", columns=['imei', 'imsi', 'sms_to', 'imei_block_date', 'imei_block_reason',
    #                                                   'sms_from', 'operator', 'subsystem_id', 'filename'])
    # con.commit()
    #
    # cur.close()
    # con.close()
    # f.close()

    # ---------------------------------------------------------------------------------------------------------------
    # objs = (Sms(sms_to=msisdn, sms_from=sms_from, imei=imei, imsi=imsi, imei_block_date=block_date, imei_block_reason=reasons,
    #             filename=file_name, operator=operator) for msisdn in df_all['msisdn'])
    # while True:
    #     batch = list(islice(objs, batch_size))
    #     if not batch:
    #         break
    #     Sms.objects.bulk_create(batch, batch_size)
    # ---------------------------------------------------------------------------------------------------------------

    t2 = time.time()

    return "File chunk is completed in {time} secs".format(time=(t2 - t1))


def write_sms_db(sms_to, sms_from, operator, subsystem, content, campaign_id="", filename="", imei=""):

    print("writing {} in to the DB".format(sms_to))

    sms_obj = Sms(imei=imei, sms_to=sms_to, sms_from=sms_from, operator=operator, subsystem=subsystem,
                  filename=filename, campaign_id=campaign_id)
    sms_obj.save()
    sms_content_obj = SmsContent(sms_content=content, sms_id=sms_obj.id)
    sms_content_obj.save()


def write_email_db(email_to, email_from, subsystem, email_subject, email_content, campaign_id="", filename="", imei=""):

    email_obj = Email(email_to=email_to, email_from=email_from, imei=imei, subsystem=subsystem, filename=filename,
                      campaign_id=campaign_id)
    email_obj.save()
    email_content_obj = EmailContent(email_subject=email_subject, email_content=email_content, email_id=email_obj.id)
    email_content_obj.save()


def send_sms_batch(msisdn_list, sms_content=""):

    url = conf['jasmine_bulk_sms_url']

    sms_batch = {
            "messages": [
                {
                    "to": msisdn_list,
          "content": sms_content
        }
      ]
    }
    headers = {'content-type': 'application/json', 'Authorization': conf['Jasmine_Authorization']}
    response = requests.post(url=url, data=json.dumps(sms_batch), headers=headers)
    if response:
        if response.status_code == 200:
            result = json.loads(response.text)
            print(f'SMS delivered to {result["data"]["messageCount"]} MSISDNs. Batch-ID is {result["data"]["batchId"]}')
        else:
            print(f'SMS batch delivery is failed')


@shared_task
def add(a, b):
    time.sleep(12)
    print(f'Sum of two numbers is {a+b}')
    return a+b


@shared_task
def multiply(c, d):
    time.sleep(12)
    print(f'Product of two numbers is {c*d}')
    return c*d
